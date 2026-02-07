"""
CLI-only deliberate-practice framework for computational philosophy.

Use this file from the shell; do not import it as a library.

Quick start:
  python3 learning_loop.py -h
  python3 learning_loop.py init --state mnt/learning_state.json
  python3 learning_loop.py status --state mnt/learning_state.json
  python3 learning_loop.py record --state mnt/learning_state.json --phase error_hunt --prediction 0.70 --observed 0.52 --errors shallow_formalization --failure-point formalize_problem --feedback-seconds 180 --adjust --diagnose
  python3 learning_loop.py recommend --state mnt/learning_state.json
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
import json
import math
import os
import re
import subprocess


# ---------------------------------------------------------------------------
# Core data structures
# ---------------------------------------------------------------------------

if __name__ != "__main__":
    raise RuntimeError(
        "learning_loop.py is CLI-only. Run it via `python3 learning_loop.py ...`."
    )


class _Phase(str, Enum):
    WARMUP = "warmup"
    ERROR_HUNT = "error_hunt"
    CORRECTION = "correction"
    CONSOLIDATE = "consolidate"


@dataclass
class _MetricSpec:
    primary: str                       # e.g. "correctness", "depth", "rigor"
    secondary: Optional[str] = None    # e.g. "elegance", "novelty"


@dataclass
class _DrillSpec:
    drill_id: str
    name: str
    description: str
    knobs: Dict[str, Any] = field(default_factory=dict)

    def with_difficulty(self, difficulty: float) -> Dict[str, Any]:
        difficulty = max(0.0, min(1.0, difficulty))
        resolved: Dict[str, Any] = {}
        for key, value in self.knobs.items():
            if (
                isinstance(value, (tuple, list))
                and len(value) == 2
                and all(isinstance(x, (int, float)) for x in value)
            ):
                lo, hi = value
                resolved[key] = lo + (hi - lo) * difficulty
            else:
                resolved[key] = value
        return resolved


@dataclass
class _AttemptRecord:
    timestamp: str
    phase: _Phase
    drill_id: str
    difficulty: float
    prediction: float          # agent's predicted quality before checking
    observed: float            # actual quality after evaluation
    error_types: List[str] = field(default_factory=list)
    failure_point: Optional[str] = None
    feedback_seconds: Optional[float] = None
    notes: Optional[str] = None
    correction: Optional[str] = None
    clean_rep: bool = False

    @property
    def has_error(self) -> bool:
        return len(self.error_types) > 0


@dataclass
class _FixSpec:
    dominant_error_type: str
    failure_moment: str        # where exactly the attempt broke
    trigger: str               # what preceded the failure
    one_change: str            # single correction variable
    cue: str                   # short phrase for execution focus
    proof_clean_reps: int = 0
    required_clean_reps: int = 3


@dataclass
class _TransitionSpec:
    from_failure_point: str
    to_failure_point: str
    drill_id: str
    reason: str
    timestamp: str


@dataclass
class _EdgePolicy:
    # Keep predicted success in this zone for "desirable difficulty."
    target_success_zone: Tuple[float, float] = (0.70, 0.90)
    # Feedback after this window is still useful but less weighty.
    feedback_half_life_sec: float = 900.0
    min_update_weight: float = 0.35
    max_update_weight: float = 1.00
    noisy_error_ceiling: float = 0.50


@dataclass
class _SessionPlan:
    warmup_reps: int = 3
    error_hunt_reps: int = 8
    correction_reps: int = 8
    consolidate_target_clean_reps: int = 3


# ---------------------------------------------------------------------------
# Practice state - persisted across cycles
# ---------------------------------------------------------------------------


@dataclass
class _PracticeState:
    skill_name: str
    metric: _MetricSpec
    skill_pipeline: List[str]
    drills: Dict[str, _DrillSpec]
    current_drill_id: str
    current_failure_point: str
    difficulty: float = 0.35
    target_error_rate: Tuple[float, float] = (0.10, 0.30)

    # Drill -> pipeline stage where it usually fails or is trained.
    drill_focus: Dict[str, str] = field(default_factory=dict)
    # Learned online from outcomes and feedback latency.
    drill_mastery: Dict[str, float] = field(default_factory=dict)
    failure_point_mastery: Dict[str, float] = field(default_factory=dict)
    edge_policy: _EdgePolicy = field(default_factory=_EdgePolicy)

    error_catalog: Dict[str, int] = field(default_factory=dict)
    history: List[_AttemptRecord] = field(default_factory=list)
    last_fix: Optional[_FixSpec] = None
    last_transition: Optional[_TransitionSpec] = None

    # --- Serialization ------------------------------------------------

    def to_json(self) -> str:
        payload = asdict(self)
        payload["history"] = [
            {**asdict(record), "phase": record.phase.value}
            for record in self.history
        ]
        return json.dumps(payload, indent=2)

    @staticmethod
    def from_json(data: str) -> "_PracticeState":
        raw = json.loads(data)
        metric = _MetricSpec(**raw["metric"])
        drills = {key: _DrillSpec(**value) for key, value in raw["drills"].items()}
        state = _PracticeState(
            skill_name=raw["skill_name"],
            metric=metric,
            skill_pipeline=raw["skill_pipeline"],
            drills=drills,
            current_drill_id=raw["current_drill_id"],
            current_failure_point=raw["current_failure_point"],
            difficulty=raw.get("difficulty", 0.35),
            target_error_rate=tuple(raw.get("target_error_rate", (0.10, 0.30))),
            drill_focus=raw.get("drill_focus", {}),
            drill_mastery=raw.get("drill_mastery", {}),
            failure_point_mastery=raw.get("failure_point_mastery", {}),
            edge_policy=_EdgePolicy(**raw.get("edge_policy", {})),
            error_catalog=raw.get("error_catalog", {}),
            last_fix=_FixSpec(**raw["last_fix"]) if raw.get("last_fix") else None,
            last_transition=(
                _TransitionSpec(**raw["last_transition"])
                if raw.get("last_transition")
                else None
            ),
        )
        for record in raw.get("history", []):
            phase_value = record.get("phase", _Phase.ERROR_HUNT.value)
            try:
                phase = _Phase(phase_value)
            except ValueError:
                phase = _Phase.ERROR_HUNT
            state.history.append(
                _AttemptRecord(
                    timestamp=record["timestamp"],
                    phase=phase,
                    drill_id=record["drill_id"],
                    difficulty=record["difficulty"],
                    prediction=record["prediction"],
                    observed=record["observed"],
                    error_types=record.get("error_types", []),
                    failure_point=record.get("failure_point"),
                    feedback_seconds=record.get("feedback_seconds"),
                    notes=record.get("notes"),
                    correction=record.get("correction"),
                    clean_rep=record.get("clean_rep", False),
                )
            )
        return state

    # --- Persistence helpers ------------------------------------------

    @staticmethod
    def load(path: str = "mnt/learning_state.json") -> Optional["_PracticeState"]:
        if os.path.exists(path):
            with open(path) as file:
                return _PracticeState.from_json(file.read())
        return None

    def save(self, path: str = "mnt/learning_state.json") -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as file:
            file.write(self.to_json())


# ---------------------------------------------------------------------------
# Controller: edge-of-competence learning loop
# ---------------------------------------------------------------------------


class _LearningLoop:
    """
    Runs a single learning session:
    warmup -> error-hunt -> diagnose -> correct -> consolidate.

    The core policy is to keep training near the edge of competence:
    not so hard that errors become noise, not so easy that errors vanish.
    """

    def __init__(self, state: _PracticeState, plan: _SessionPlan | None = None):
        self.state = state
        self.plan = plan or _SessionPlan()

    # --- Public API ---------------------------------------------------

    def record_attempt(
        self,
        phase: _Phase,
        prediction: float,
        observed: float,
        error_types: List[str] | None = None,
        notes: str | None = None,
        drill_id: str | None = None,
        difficulty: float | None = None,
        failure_point: str | None = None,
        feedback_seconds: float | None = None,
        correction: str | None = None,
        clean_rep: bool = False,
    ) -> _AttemptRecord:
        """Record a single practice attempt and update skill models."""
        drill = drill_id or self.state.current_drill_id
        point = failure_point or self.state.current_failure_point
        diff = self._clamp(difficulty if difficulty is not None else self.state.difficulty)
        pred = self._clamp(prediction)
        obs = self._clamp(observed)

        record = _AttemptRecord(
            timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            phase=phase,
            drill_id=drill,
            difficulty=diff,
            prediction=pred,
            observed=obs,
            error_types=error_types or [],
            failure_point=point,
            feedback_seconds=feedback_seconds,
            notes=notes,
            correction=correction,
            clean_rep=clean_rep,
        )
        self.state.history.append(record)
        self.state.current_drill_id = drill
        self.state.current_failure_point = point

        for error in record.error_types:
            self.state.error_catalog[error] = self.state.error_catalog.get(error, 0) + 1

        self._update_fix_progress(record)
        self._update_mastery_models(record)
        self._maybe_advance_failure_point(
            trigger=f"stabilized_after_{record.phase.value}"
        )
        return record

    def estimate_success_probability(
        self,
        drill_id: str | None = None,
        difficulty: float | None = None,
        failure_point: str | None = None,
    ) -> float:
        """Estimate probability of acceptable performance for a planned attempt."""
        drill = drill_id or self.state.current_drill_id
        point = failure_point or self.state.current_failure_point
        diff = self._clamp(difficulty if difficulty is not None else self.state.difficulty)

        drill_mastery = self.state.drill_mastery.get(drill, max(0.05, 1.0 - diff))
        point_mastery = self.state.failure_point_mastery.get(point, drill_mastery)
        effective_mastery = (0.70 * drill_mastery) + (0.30 * point_mastery)

        # Higher difficulty lowers success; logistic keeps output in [0, 1].
        margin = (effective_mastery - diff) * 6.0
        return self._sigmoid(margin)

    def weakest_subskills(self, recent_n: int = 30, top_k: int = 3) -> List[Tuple[str, float]]:
        """Return failure points ordered by current weakness estimate."""
        recent = self.state.history[-recent_n:]
        weakness: Dict[str, float] = {}

        if recent:
            size = len(recent)
            for index, attempt in enumerate(recent, start=1):
                point = attempt.failure_point or self.state.current_failure_point
                recency_weight = 0.5 + (0.5 * index / size)
                miss = max(0.0, 1.0 - attempt.observed)
                error_penalty = 0.35 if attempt.has_error else 0.0
                error_count_penalty = 0.10 * len(attempt.error_types)
                weakness[point] = weakness.get(point, 0.0) + recency_weight * (
                    miss + error_penalty + error_count_penalty
                )

        for point, mastery in self.state.failure_point_mastery.items():
            weakness[point] = weakness.get(point, 0.0) + max(0.0, 0.70 - mastery)

        ranked = sorted(weakness.items(), key=lambda item: item[1], reverse=True)
        return ranked[:top_k]

    def recommend_next_attempt(self) -> Dict[str, Any]:
        """
        Propose a focused next attempt:
        keep error rate in budget, favor diagnosable mistakes, and close fix loops.
        """
        recent = self.state.history[-20:]
        calibration = self._prediction_profile(recent[-12:])

        pending_fix = self._pending_fix()
        target_phase = _Phase.CORRECTION if pending_fix is not None else _Phase.ERROR_HUNT
        error_lo, error_hi = self._phase_error_zone(target_phase)
        success_lo, success_hi = self._success_zone_from_error_zone((error_lo, error_hi))
        signal = self._difficulty_signal(recent, phase=target_phase)

        if pending_fix is not None:
            target_point = pending_fix.failure_moment or self.state.current_failure_point
            drill = self._select_drill_for_failure_point(target_point)
            proof_reps_remaining = max(
                1, pending_fix.required_clean_reps - pending_fix.proof_clean_reps
            )
            target_success = min(0.95, max(success_hi - 0.01, (success_lo + success_hi) / 2.0))
            difficulty = self._difficulty_for_target(drill, target_point, target_success)
            predicted_success = self.estimate_success_probability(
                drill_id=drill,
                difficulty=difficulty,
                failure_point=target_point,
            )
            drill_blueprint = self._drill_blueprint(drill, difficulty)
            return {
                "mode": "prove_fix",
                "phase": target_phase.value,
                "drill_id": drill,
                "failure_point": target_point,
                "difficulty": round(difficulty, 2),
                "predicted_success": round(predicted_success, 2),
                "predicted_error_rate": round(1.0 - predicted_success, 2),
                "repeat_reps": proof_reps_remaining,
                "feedback_window_seconds": 300,
                "target_error_budget": [round(error_lo, 2), round(error_hi, 2)],
                "proof_clean_reps_done": pending_fix.proof_clean_reps,
                "proof_clean_reps_target": pending_fix.required_clean_reps,
                "one_change": pending_fix.one_change,
                "drill_name": drill_blueprint.get("name"),
                "drill_description": drill_blueprint.get("description"),
                "drill_knobs": drill_blueprint.get("knobs"),
                "rationale": "Fix it, then prove it with consecutive clean reps before raising difficulty.",
            }

        target_phase = _Phase.ERROR_HUNT
        error_lo, error_hi = self._phase_error_zone(target_phase)
        success_lo, success_hi = self._success_zone_from_error_zone((error_lo, error_hi))
        signal = self._difficulty_signal(recent, phase=target_phase)
        target_success = (success_lo + success_hi) / 2.0
        if signal == "too_easy":
            target_success = min(success_hi, success_lo + 0.02)
        elif signal == "too_hard":
            target_success = max(success_lo, success_hi - 0.02)
        elif calibration["bias"] < -0.10:
            target_success = min(0.95, target_success + 0.03)
        elif calibration["bias"] > 0.10:
            target_success = max(0.55, target_success - 0.02)

        weak_points = self.weakest_subskills()
        if self._should_focus_current_failure_point():
            target_point = self.state.current_failure_point
        else:
            target_point = weak_points[0][0] if weak_points else self.state.current_failure_point
        drill = self._select_drill_for_failure_point(target_point)
        difficulty = self._difficulty_for_target(drill, target_point, target_success)
        predicted_success = self.estimate_success_probability(
            drill_id=drill,
            difficulty=difficulty,
            failure_point=target_point,
        )

        profile = self._error_profile(recent[-10:])
        if signal == "too_easy":
            repeat_reps = 6
        elif signal == "too_hard":
            repeat_reps = 3
        else:
            repeat_reps = 4 if profile["diagnosable_error_share"] >= 0.50 else 5

        drill_blueprint = self._drill_blueprint(drill, difficulty)
        return {
            "mode": "error_hunt",
            "phase": target_phase.value,
            "drill_id": drill,
            "failure_point": target_point,
            "difficulty": round(difficulty, 2),
            "predicted_success": round(predicted_success, 2),
            "predicted_error_rate": round(1.0 - predicted_success, 2),
            "repeat_reps": repeat_reps,
            "feedback_window_seconds": 300,
            "target_error_budget": [round(error_lo, 2), round(error_hi, 2)],
            "drill_name": drill_blueprint.get("name"),
            "drill_description": drill_blueprint.get("description"),
            "drill_knobs": drill_blueprint.get("knobs"),
            "drill_design": "One micro-skill, one failure mode, one correction variable.",
            "rationale": (
                "Practice at the edge where mistakes stay diagnosable: "
                "small, explainable, and fast to retest."
            ),
        }

    def diagnose(self, recent_n: int = 10) -> _FixSpec:
        """Analyze recent attempts and produce a one-variable fix."""
        recent = self.state.history[-recent_n:]
        error_counts: Dict[str, int] = {}
        failure_counts: Dict[str, int] = {}
        for attempt in recent:
            point = attempt.failure_point or self.state.current_failure_point
            if attempt.has_error:
                failure_counts[point] = failure_counts.get(point, 0) + 1
            for error in attempt.error_types:
                error_counts[error] = error_counts.get(error, 0) + 1

        dominant_error = max(error_counts, key=error_counts.get) if error_counts else "unlabeled_error"
        dominant_failure = (
            max(failure_counts, key=failure_counts.get)
            if failure_counts
            else self.state.current_failure_point
        )
        recommendation = self.recommend_next_attempt()
        recommendation_phase = recommendation.get("phase", _Phase.ERROR_HUNT.value)
        try:
            phase = _Phase(recommendation_phase)
        except ValueError:
            phase = _Phase.ERROR_HUNT
        signal = self._difficulty_signal(recent, phase=phase)
        error_lo, error_hi = self._phase_error_zone(phase)
        target_point = dominant_failure or self.state.current_failure_point

        trigger_parts: List[str] = []
        error_difficulties = [
            attempt.difficulty
            for attempt in recent
            if dominant_error in attempt.error_types
        ]
        if error_difficulties:
            avg_error_diff = sum(error_difficulties) / len(error_difficulties)
            trigger_parts.append(f"difficulty around {avg_error_diff:.2f}")
        if dominant_failure:
            trigger_parts.append(f"work reaches '{dominant_failure}'")
        trigger = " and ".join(trigger_parts) if trigger_parts else "insufficient recent data"

        if signal == "too_easy":
            one_change = (
                "Add one constraint to the same drill (time/tool/vocabulary limit) "
                "without changing anything else."
            )
        elif signal == "too_hard":
            one_change = (
                "Reduce difficulty by 0.10 and force exactly one error tag per rep "
                "until mistakes become explainable."
            )
        else:
            one_change = (
                f"Run {recommendation['repeat_reps']} reps on '{target_point}' at "
                f"difficulty {recommendation['difficulty']:.2f} with <=5 minute feedback."
            )

        fix = _FixSpec(
            dominant_error_type=dominant_error,
            failure_moment=target_point,
            trigger=trigger,
            one_change=one_change,
            cue=(
                f"keep error rate in {error_lo:.2f}-{error_hi:.2f}; "
                "fix one variable, then prove with clean reps"
            ),
            proof_clean_reps=0,
            required_clean_reps=max(2, self.plan.consolidate_target_clean_reps),
        )
        self.state.last_fix = fix
        return fix

    def adjust_difficulty(self) -> float:
        """
        Recompute difficulty with error-budget control.
        Increase if too easy, decrease if too hard/noisy.
        """
        recent = self.state.history[-12:]
        target_phase = recent[-1].phase if recent else _Phase.ERROR_HUNT
        error_lo, error_hi = self._phase_error_zone(target_phase)
        success_lo, success_hi = self._success_zone_from_error_zone((error_lo, error_hi))
        predicted = self.estimate_success_probability()
        calibration = self._prediction_profile(recent)
        step = 0.0

        if recent:
            profile = self._error_profile(recent)
            error_rate = profile["error_rate"]

            if error_rate < error_lo:
                step += 0.08 + min(0.08, (error_lo - error_rate) * 0.30)
            elif error_rate > error_hi:
                step -= 0.08 + min(0.08, (error_rate - error_hi) * 0.30)

            if profile["noisy_error_share"] > self.state.edge_policy.noisy_error_ceiling:
                step -= 0.06
            elif (
                error_lo <= error_rate <= error_hi
                and profile["diagnosable_error_share"] >= 0.60
            ):
                step += 0.02
        else:
            if predicted > success_hi:
                step += 0.08
            elif predicted < success_lo:
                step -= 0.08

        if calibration["bias"] < -0.10:
            # Overconfidence: lower challenge slightly to restore reliable signal.
            step -= 0.04
        elif calibration["bias"] > 0.10:
            # Underconfidence: modestly raise challenge.
            step += 0.02

        if calibration["mean_abs_gap"] > 0.20:
            step -= 0.02

        if predicted > success_hi + 0.08:
            step += 0.04
        elif predicted < success_lo - 0.08:
            step -= 0.04

        step = self._clamp(step, -0.20, 0.20)
        self.state.difficulty = self._clamp(self.state.difficulty + step)
        return self.state.difficulty

    def status(self) -> Dict[str, Any]:
        """Current learning status summary."""
        recent = self.state.history[-20:]
        active_phase = recent[-1].phase if recent else _Phase.ERROR_HUNT
        profile = self._error_profile(recent)
        error_lo, error_hi = self._phase_error_zone(active_phase)
        success_lo, success_hi = self._success_zone_from_error_zone((error_lo, error_hi))
        calibration = self._prediction_profile(recent)
        error_counts: Dict[str, int] = {}
        for attempt in recent:
            for error in attempt.error_types:
                error_counts[error] = error_counts.get(error, 0) + 1

        weak_subskills = [
            {"failure_point": point, "weakness": round(score, 2)}
            for point, score in self.weakest_subskills(top_k=3)
        ]

        last_fix_payload = asdict(self.state.last_fix) if self.state.last_fix else None
        if last_fix_payload is not None:
            proof_done = self.state.last_fix.proof_clean_reps
            proof_target = self.state.last_fix.required_clean_reps
            last_fix_payload["resolved"] = proof_done >= proof_target

        last_transition_payload = (
            asdict(self.state.last_transition)
            if self.state.last_transition
            else None
        )
        current_drill_blueprint = self._drill_blueprint(
            self.state.current_drill_id,
            self.state.difficulty,
        )

        return {
            "skill": self.state.skill_name,
            "active_phase": active_phase.value,
            "failure_point": self.state.current_failure_point,
            "current_drill_id": self.state.current_drill_id,
            "current_drill_name": current_drill_blueprint.get("name"),
            "current_drill_knobs": current_drill_blueprint.get("knobs"),
            "difficulty": round(self.state.difficulty, 2),
            "predicted_success": round(self.estimate_success_probability(), 2),
            "target_error_rate": [round(error_lo, 2), round(error_hi, 2)],
            "edge_success_zone": [round(success_lo, 2), round(success_hi, 2)],
            "recent_error_rate": round(profile["error_rate"], 2),
            "difficulty_signal": self._difficulty_signal(recent, phase=active_phase),
            "prediction_calibration": {
                "bias_observed_minus_predicted": round(calibration["bias"], 3),
                "mean_abs_gap": round(calibration["mean_abs_gap"], 3),
                "overconfident_share": round(calibration["overconfident_share"], 3),
            },
            "mistake_quality": {
                "diagnosable_error_share": round(profile["diagnosable_error_share"], 2),
                "high_quality_error_share": round(profile["high_quality_error_share"], 2),
                "noisy_error_share": round(profile["noisy_error_share"], 2),
            },
            "total_attempts": len(self.state.history),
            "top_errors": dict(sorted(error_counts.items(), key=lambda item: -item[1])[:5]),
            "weak_subskills": weak_subskills,
            "recommended_next": self.recommend_next_attempt(),
            "last_fix": last_fix_payload,
            "last_transition": last_transition_payload,
        }

    def should_switch_failure_point(self) -> bool:
        """Switch once the current failure point is mostly stable at high difficulty."""
        if self._pending_fix() is not None:
            return False

        recent = self.state.history[-20:]
        if len(recent) < 10:
            return False

        current_point = self.state.current_failure_point
        point_attempts = [
            attempt
            for attempt in recent
            if (attempt.failure_point or current_point) == current_point
        ]
        if len(point_attempts) < 5:
            return False

        point_error_rate = sum(1 for attempt in point_attempts if attempt.has_error) / len(point_attempts)
        error_lo, _ = self._phase_error_zone(_Phase.CONSOLIDATE)
        mastery = self.state.failure_point_mastery.get(current_point, 0.0)
        return (
            point_error_rate < max(0.06, error_lo)
            and mastery > 0.75
            and self.state.difficulty > 0.65
        )

    # --- Internals ----------------------------------------------------

    @staticmethod
    def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))

    @staticmethod
    def _sigmoid(value: float) -> float:
        if value >= 0:
            exp_term = math.exp(-value)
            return 1.0 / (1.0 + exp_term)
        exp_term = math.exp(value)
        return exp_term / (1.0 + exp_term)

    def _target_error_zone(self) -> Tuple[float, float]:
        lo, hi = self.state.target_error_rate
        lo = self._clamp(float(lo))
        hi = self._clamp(float(hi))
        return (lo, hi) if lo <= hi else (hi, lo)

    def _phase_error_zone(self, phase: _Phase) -> Tuple[float, float]:
        base_lo, base_hi = self._target_error_zone()
        if phase == _Phase.WARMUP:
            lo, hi = base_lo * 0.60, base_hi * 0.75
        elif phase == _Phase.CORRECTION:
            lo, hi = max(0.04, base_lo * 0.80), max(base_lo + 0.05, base_hi * 0.85)
        elif phase == _Phase.CONSOLIDATE:
            lo, hi = max(0.02, base_lo * 0.40), max(0.08, base_hi * 0.45)
        else:
            lo, hi = base_lo, base_hi

        lo = self._clamp(lo)
        hi = self._clamp(hi)
        if lo > hi:
            lo, hi = hi, lo
        if (hi - lo) < 0.02:
            hi = self._clamp(lo + 0.02)
        return lo, hi

    def _success_zone_from_error_zone(
        self,
        error_zone: Tuple[float, float],
    ) -> Tuple[float, float]:
        error_lo, error_hi = error_zone
        budget_lo, budget_hi = 1.0 - error_hi, 1.0 - error_lo

        policy_lo, policy_hi = self.state.edge_policy.target_success_zone
        policy_lo = self._clamp(float(policy_lo))
        policy_hi = self._clamp(float(policy_hi))
        if policy_lo > policy_hi:
            policy_lo, policy_hi = policy_hi, policy_lo

        lo = max(budget_lo, policy_lo)
        hi = min(budget_hi, policy_hi)
        if lo <= hi:
            return lo, hi
        return budget_lo, budget_hi

    def _target_success_zone(self) -> Tuple[float, float]:
        return self._success_zone_from_error_zone(self._target_error_zone())

    def _prediction_profile(self, attempts: List[_AttemptRecord]) -> Dict[str, float]:
        if not attempts:
            return {
                "bias": 0.0,
                "mean_abs_gap": 0.0,
                "overconfident_share": 0.0,
            }

        size = len(attempts)
        bias = sum((attempt.observed - attempt.prediction) for attempt in attempts) / size
        mean_abs_gap = (
            sum(abs(attempt.observed - attempt.prediction) for attempt in attempts) / size
        )
        overconfident_share = (
            sum(1 for attempt in attempts if (attempt.prediction - attempt.observed) > 0.10)
            / size
        )
        return {
            "bias": bias,
            "mean_abs_gap": mean_abs_gap,
            "overconfident_share": overconfident_share,
        }

    def _drill_blueprint(self, drill_id: str, difficulty: float) -> Dict[str, Any]:
        spec = self.state.drills.get(drill_id)
        if spec is None:
            return {"id": drill_id, "name": drill_id, "description": "", "knobs": {}}

        knobs: Dict[str, Any] = {}
        for key, value in spec.with_difficulty(difficulty).items():
            if isinstance(value, float):
                knobs[key] = int(value) if value.is_integer() else round(value, 2)
            else:
                knobs[key] = value

        return {
            "id": spec.drill_id,
            "name": spec.name,
            "description": spec.description,
            "knobs": knobs,
        }

    def _ordered_failure_points(self) -> List[str]:
        ordered: List[str] = []
        for point in self.state.skill_pipeline:
            if point not in ordered:
                ordered.append(point)
        for point in self.state.failure_point_mastery:
            if point not in ordered:
                ordered.append(point)
        if self.state.current_failure_point not in ordered:
            ordered.append(self.state.current_failure_point)
        return ordered

    def _recent_attempts_for_point(
        self,
        failure_point: str,
        recent_n: int = 12,
    ) -> List[_AttemptRecord]:
        recent = self.state.history[-recent_n:]
        return [
            attempt
            for attempt in recent
            if (attempt.failure_point or failure_point) == failure_point
        ]

    def _should_focus_current_failure_point(self) -> bool:
        transition = self.state.last_transition
        if transition is None:
            return False
        if transition.to_failure_point != self.state.current_failure_point:
            return False
        # After switching stages, gather a few direct reps before jumping back
        # to a previously weak point.
        current_reps = self._recent_attempts_for_point(self.state.current_failure_point, recent_n=8)
        return len(current_reps) < 4

    def _maybe_advance_failure_point(self, trigger: str) -> Optional[_TransitionSpec]:
        if self._pending_fix() is not None:
            return None
        if not self.should_switch_failure_point():
            return None

        ordered = self._ordered_failure_points()
        current = self.state.current_failure_point
        if current not in ordered:
            return None
        index = ordered.index(current)
        if index >= len(ordered) - 1:
            return None

        next_point = ordered[index + 1]
        if next_point == current:
            return None

        next_drill = self._select_drill_for_failure_point(next_point)
        transition = _TransitionSpec(
            from_failure_point=current,
            to_failure_point=next_point,
            drill_id=next_drill,
            reason=trigger,
            timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
        self.state.current_failure_point = next_point
        self.state.current_drill_id = next_drill
        # Enter the new stage at stretch difficulty, not at the prior stage's cap.
        entry_difficulty = self._difficulty_for_target(
            drill_id=next_drill,
            failure_point=next_point,
            target_success=0.78,
        )
        self.state.difficulty = min(self.state.difficulty, entry_difficulty)
        self.state.last_transition = transition
        self.state.last_fix = None
        return transition

    def _select_drill_for_failure_point(self, failure_point: str) -> str:
        focused_drills = [
            drill_id
            for drill_id, focus_point in self.state.drill_focus.items()
            if focus_point == failure_point
        ]
        candidates = focused_drills or list(self.state.drills.keys())
        if not candidates:
            return self.state.current_drill_id
        return min(
            candidates,
            key=lambda drill_id: self.state.drill_mastery.get(drill_id, 0.50),
        )

    def _pending_fix(self) -> Optional[_FixSpec]:
        fix = self.state.last_fix
        if fix is None:
            return None
        if fix.proof_clean_reps >= fix.required_clean_reps:
            return None
        return fix

    def _update_fix_progress(self, attempt: _AttemptRecord) -> None:
        fix = self._pending_fix()
        if fix is None:
            return

        point = attempt.failure_point or self.state.current_failure_point
        if point != fix.failure_moment:
            return

        if attempt.has_error:
            if (
                fix.dominant_error_type == "unlabeled_error"
                or fix.dominant_error_type in attempt.error_types
            ):
                fix.proof_clean_reps = 0
            return

        success_zone = self._success_zone_from_error_zone(
            self._phase_error_zone(attempt.phase)
        )
        clean_threshold = max(0.70, success_zone[0])
        if attempt.observed >= clean_threshold:
            fix.proof_clean_reps += 1
        else:
            fix.proof_clean_reps = 0

    def _mistake_quality(
        self,
        attempts: List[_AttemptRecord],
        index: int,
    ) -> Dict[str, bool]:
        attempt = attempts[index]
        if not attempt.has_error:
            return {
                "small": False,
                "repeatable": False,
                "explainable": False,
                "fixable": False,
                "diagnosable": False,
                "followed_by_clean": False,
                "high_quality": False,
            }

        point = attempt.failure_point or self.state.current_failure_point
        small = len(attempt.error_types) == 1 and attempt.observed >= 0.35
        explainable = bool(attempt.error_types) and bool(point)

        repeatable = False
        for prev in attempts[max(0, index - 6):index]:
            prev_point = prev.failure_point or point
            if not prev.has_error or prev_point != point:
                continue
            if set(prev.error_types).intersection(attempt.error_types):
                repeatable = True
                break

        fixable = explainable and len(attempt.error_types) <= 2
        diagnosable = small and repeatable and explainable and fixable

        followed_by_clean = False
        clean_threshold = max(0.70, self._target_success_zone()[0])
        for nxt in attempts[index + 1 : index + 6]:
            nxt_point = nxt.failure_point or point
            if nxt_point != point:
                continue
            if not nxt.has_error and nxt.observed >= clean_threshold:
                followed_by_clean = True
                break

        return {
            "small": small,
            "repeatable": repeatable,
            "explainable": explainable,
            "fixable": fixable,
            "diagnosable": diagnosable,
            "followed_by_clean": followed_by_clean,
            "high_quality": diagnosable and followed_by_clean,
        }

    def _error_profile(self, attempts: List[_AttemptRecord]) -> Dict[str, float]:
        if not attempts:
            return {
                "error_rate": 0.0,
                "diagnosable_error_share": 0.0,
                "high_quality_error_share": 0.0,
                "noisy_error_share": 0.0,
            }

        error_indexes = [idx for idx, attempt in enumerate(attempts) if attempt.has_error]
        error_count = len(error_indexes)
        if error_count == 0:
            return {
                "error_rate": 0.0,
                "diagnosable_error_share": 0.0,
                "high_quality_error_share": 0.0,
                "noisy_error_share": 0.0,
            }

        diagnosable = 0
        high_quality = 0
        for idx in error_indexes:
            quality = self._mistake_quality(attempts, idx)
            diagnosable += 1 if quality["diagnosable"] else 0
            high_quality += 1 if quality["high_quality"] else 0

        noisy = error_count - diagnosable
        return {
            "error_rate": error_count / len(attempts),
            "diagnosable_error_share": diagnosable / error_count,
            "high_quality_error_share": high_quality / error_count,
            "noisy_error_share": noisy / error_count,
        }

    def _difficulty_signal(
        self,
        attempts: List[_AttemptRecord],
        phase: _Phase | None = None,
    ) -> str:
        active_phase = phase or (attempts[-1].phase if attempts else _Phase.ERROR_HUNT)
        error_lo, error_hi = self._phase_error_zone(active_phase)
        success_lo, success_hi = self._success_zone_from_error_zone((error_lo, error_hi))
        predicted = self.estimate_success_probability()

        if not attempts:
            if predicted > success_hi:
                return "too_easy"
            if predicted < success_lo:
                return "too_hard"
            return "stretch"

        profile = self._error_profile(attempts)
        if profile["error_rate"] < error_lo and predicted < (success_lo - 0.10):
            return "too_hard"
        if profile["error_rate"] < error_lo:
            return "too_easy"
        if (
            profile["error_rate"] > error_hi
            or profile["noisy_error_share"] > self.state.edge_policy.noisy_error_ceiling
        ):
            return "too_hard"
        if predicted > (success_hi + 0.10):
            return "too_easy"
        if predicted < (success_lo - 0.10):
            return "too_hard"
        return "stretch"

    def _feedback_weight(self, feedback_seconds: float | None) -> float:
        policy = self.state.edge_policy
        if feedback_seconds is None:
            return 0.60

        delay = max(1.0, feedback_seconds)
        decay = math.exp(-delay / policy.feedback_half_life_sec)
        raw_weight = policy.min_update_weight + (
            (policy.max_update_weight - policy.min_update_weight) * decay
        )
        return self._clamp(raw_weight, policy.min_update_weight, policy.max_update_weight)

    def _update_mastery_models(self, attempt: _AttemptRecord) -> None:
        drill_id = attempt.drill_id
        point = attempt.failure_point or self.state.current_failure_point
        prior_drill = self.state.drill_mastery.get(drill_id, max(0.05, 1.0 - attempt.difficulty))
        prior_point = self.state.failure_point_mastery.get(point, prior_drill)

        quality = self._mistake_quality(self.state.history, len(self.state.history) - 1)

        # Fast feedback and diagnosable mistakes update models more strongly.
        quality_weight = 1.00
        if attempt.has_error:
            quality_weight = 1.10 if quality["diagnosable"] else 0.70
        calibration_gap = abs(attempt.prediction - attempt.observed)
        if calibration_gap > 0.25:
            quality_weight *= 0.90
        alpha = 0.18 * self._feedback_weight(attempt.feedback_seconds) * quality_weight
        alpha = self._clamp(alpha, 0.05, 0.30)

        drill_target = attempt.observed
        if attempt.has_error:
            if quality["diagnosable"]:
                point_target = max(0.0, attempt.observed - 0.12)
            else:
                point_target = max(0.0, attempt.observed - 0.28)
            if (attempt.prediction - attempt.observed) > 0.15:
                point_target = max(0.0, point_target - 0.05)
        else:
            clean_boost = 0.08 if attempt.clean_rep else 0.05
            point_target = min(1.0, attempt.observed + clean_boost)

        self.state.drill_mastery[drill_id] = self._clamp(
            prior_drill + alpha * (drill_target - prior_drill)
        )
        self.state.failure_point_mastery[point] = self._clamp(
            prior_point + alpha * (point_target - prior_point)
        )

    def _difficulty_for_target(
        self,
        drill_id: str,
        failure_point: str,
        target_success: float,
    ) -> float:
        lo, hi = 0.0, 1.0
        target = self._clamp(target_success, 0.05, 0.95)
        for _ in range(20):
            mid = (lo + hi) / 2.0
            predicted = self.estimate_success_probability(
                drill_id=drill_id,
                difficulty=mid,
                failure_point=failure_point,
            )
            if predicted > target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2.0


# ---------------------------------------------------------------------------
# Default drills for computational philosophy
# ---------------------------------------------------------------------------


_DEFAULT_DRILLS: Dict[str, _DrillSpec] = {
    "formalize_argument": _DrillSpec(
        drill_id="formalize_argument",
        name="Formalize a philosophical argument",
        description=(
            "Take a natural-language philosophical argument and translate it "
            "into formal logic. Verify validity."
        ),
        knobs={"complexity": (1, 10), "time_limit_min": (30, 5)},
    ),
    "build_simulation": _DrillSpec(
        drill_id="build_simulation",
        name="Build a philosophical simulation",
        description=(
            "Create an agent-based or mathematical simulation that tests a "
            "philosophical claim. Run it and interpret results."
        ),
        knobs={"agent_count": (3, 100), "scenario_complexity": (1, 10)},
    ),
    "prove_or_refute": _DrillSpec(
        drill_id="prove_or_refute",
        name="Prove or refute a claim",
        description=(
            "Use formal methods (SAT solver, model checker, proof assistant, "
            "or mathematical proof) to verify or refute a philosophical claim."
        ),
        knobs={"claim_complexity": (1, 10)},
    ),
    "computational_essay": _DrillSpec(
        drill_id="computational_essay",
        name="Write a computational essay",
        description=(
            "Write an essay that combines prose argument with working code. "
            "The code must run and produce results that support or challenge "
            "the argument."
        ),
        knobs={"depth": (1, 10), "code_ratio": (0.3, 0.7)},
    ),
    "bridge_traditions": _DrillSpec(
        drill_id="bridge_traditions",
        name="Bridge philosophical traditions computationally",
        description=(
            "Take ideas from two different philosophical traditions and find "
            "computational common ground. Build a model that synthesizes them."
        ),
        knobs={"abstraction_level": (1, 10)},
    ),
}

_DEFAULT_DRILL_FOCUS: Dict[str, str] = {
    "formalize_argument": "formalize_problem",
    "build_simulation": "implement_solution",
    "prove_or_refute": "run_and_interpret",
    "computational_essay": "write_findings",
    "bridge_traditions": "research_background",
}


def _init_default_state(skill_name: str = "computational_philosophy") -> _PracticeState:
    """Create a fresh practice state with error-budget defaults."""
    pipeline = [
        "select_question",
        "research_background",
        "formalize_problem",
        "implement_solution",
        "run_and_interpret",
        "write_findings",
    ]
    default_mastery = {drill_id: 0.55 for drill_id in _DEFAULT_DRILLS}
    failure_mastery = {point: 0.55 for point in pipeline}
    failure_mastery["formalize_problem"] = 0.50

    return _PracticeState(
        skill_name=skill_name,
        metric=_MetricSpec(primary="rigor", secondary="novelty"),
        skill_pipeline=pipeline,
        drills=_DEFAULT_DRILLS,
        current_drill_id="formalize_argument",
        current_failure_point="formalize_problem",
        drill_focus=_DEFAULT_DRILL_FOCUS.copy(),
        drill_mastery=default_mastery,
        failure_point_mastery=failure_mastery,
        edge_policy=_EdgePolicy(target_success_zone=(0.70, 0.90)),
    )


# ---------------------------------------------------------------------------
# Git worktree helpers
# ---------------------------------------------------------------------------


class _GitWorktreeError(RuntimeError):
    """Raised when worktree operations fail."""


class _GitWorktreeManager:
    """Minimal helpers to create/list worktrees for parallel experiments."""

    @staticmethod
    def _run_git(repo_path: str, args: List[str]) -> str:
        result = subprocess.run(
            ["git", "-C", repo_path, *args],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            error = (result.stderr or result.stdout).strip()
            raise _GitWorktreeError(error or f"git {' '.join(args)} failed")
        return result.stdout.strip()

    @staticmethod
    def is_git_repo(repo_path: str = ".") -> bool:
        result = subprocess.run(
            ["git", "-C", repo_path, "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"

    @staticmethod
    def list_worktrees(repo_path: str = ".") -> List[Dict[str, str]]:
        if not _GitWorktreeManager.is_git_repo(repo_path):
            raise _GitWorktreeError(f"Not a git repo: {repo_path}")

        output = _GitWorktreeManager._run_git(repo_path, ["worktree", "list", "--porcelain"])
        entries: List[Dict[str, str]] = []
        current: Dict[str, str] = {}
        for line in output.splitlines():
            if not line.strip():
                if current:
                    entries.append(current)
                    current = {}
                continue

            key, _, value = line.partition(" ")
            if key == "worktree":
                current["path"] = value
            elif key == "HEAD":
                current["head"] = value
            elif key == "branch":
                current["branch"] = value.removeprefix("refs/heads/")
            elif key == "detached":
                current["detached"] = "true"
            elif key == "prunable":
                current["prunable"] = value

        if current:
            entries.append(current)
        return entries

    @staticmethod
    def _sanitize_name(name: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-")
        if not cleaned:
            raise _GitWorktreeError("worktree name must contain alphanumeric characters")
        return cleaned

    @staticmethod
    def _branch_exists(repo_path: str, branch_name: str) -> bool:
        result = subprocess.run(
            ["git", "-C", repo_path, "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"],
            check=False,
        )
        return result.returncode == 0

    @staticmethod
    def create_worktree(
        repo_path: str,
        worktree_name: str,
        worktree_root: str = "mnt/worktrees",
        branch_prefix: str = "alive",
        base_ref: str = "HEAD",
    ) -> Dict[str, str]:
        if not _GitWorktreeManager.is_git_repo(repo_path):
            raise _GitWorktreeError(f"Not a git repo: {repo_path}")

        safe_name = _GitWorktreeManager._sanitize_name(worktree_name)
        branch_name = f"{branch_prefix}/{safe_name}" if branch_prefix else safe_name

        repo_abs = os.path.abspath(repo_path)
        if os.path.isabs(worktree_root):
            root_abs = worktree_root
        else:
            root_abs = os.path.join(repo_abs, worktree_root)
        worktree_path = os.path.join(root_abs, safe_name)
        os.makedirs(root_abs, exist_ok=True)

        if os.path.exists(worktree_path):
            raise _GitWorktreeError(f"worktree path already exists: {worktree_path}")

        if _GitWorktreeManager._branch_exists(repo_path, branch_name):
            _GitWorktreeManager._run_git(repo_path, ["worktree", "add", worktree_path, branch_name])
        else:
            _GitWorktreeManager._run_git(
                repo_path,
                ["worktree", "add", "-b", branch_name, worktree_path, base_ref],
            )

        return {
            "repo": repo_abs,
            "path": worktree_path,
            "branch": branch_name,
            "base_ref": base_ref,
        }


# ---------------------------------------------------------------------------
# CLI entry point for deliberate-practice and worktree workflows
# ---------------------------------------------------------------------------


def _state_payload(state_path: str, created: bool) -> Dict[str, Any]:
    return {"state_path": os.path.abspath(state_path), "state_created": created}


def _ensure_state(
    state_path: str,
    auto_create: bool = True,
    skill_name: str = "computational_philosophy",
) -> Tuple[_PracticeState, bool]:
    state = _PracticeState.load(state_path)
    if state is not None:
        return state, False
    if not auto_create:
        raise FileNotFoundError(f"Learning state not found: {state_path}")

    state = _init_default_state(skill_name=skill_name)
    state.save(state_path)
    return state, True


def _parse_error_types(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _attempt_to_payload(record: _AttemptRecord) -> Dict[str, Any]:
    payload = asdict(record)
    payload["phase"] = record.phase.value
    return payload


if __name__ == "__main__":
    import argparse
    import sys

    cli_help_epilog = """
Algorithm model:
  1) Keep observed error rate near the 10%-30% budget.
  2) Prefer diagnosable mistakes (small, repeatable, explainable, fixable).
  3) Weight updates by feedback speed and mistake quality.
  4) Apply one correction variable, then prove it with clean reps.
  5) Reduce noisy error spikes (>40%-50%) before raising challenge again.

Examples:
  python3 learning_loop.py init --state mnt/learning_state.json
  python3 learning_loop.py record --state mnt/learning_state.json --phase error_hunt --prediction 0.70 --observed 0.52 --errors shallow_formalization --failure-point formalize_problem --feedback-seconds 180 --adjust --diagnose
  python3 learning_loop.py recommend --state mnt/learning_state.json
  python3 learning_loop.py worktree-create alt-hypothesis --repo /path/to/repo
  python3 learning_loop.py record -h
"""

    parser = argparse.ArgumentParser(
        description=(
            "Error-budget learning CLI. "
            "Use subcommands for status, record, recommend, diagnose, and worktrees."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=cli_help_epilog.strip(),
    )
    parser.add_argument(
        "--state",
        default="mnt/learning_state.json",
        help="State path used by default when no subcommand is provided.",
    )
    subparsers = parser.add_subparsers(dest="command")

    shared_state = argparse.ArgumentParser(add_help=False)
    shared_state.add_argument(
        "--state",
        default="mnt/learning_state.json",
        help="Path to learning state JSON.",
    )

    init_parser = subparsers.add_parser(
        "init",
        parents=[shared_state],
        help="Initialize a learning state file.",
    )
    init_parser.add_argument(
        "--skill-name",
        default="computational_philosophy",
        help="Skill name used for fresh initialization.",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite any existing state file.",
    )

    subparsers.add_parser(
        "status",
        parents=[shared_state],
        help="Show current learning status.",
    )
    subparsers.add_parser(
        "recommend",
        parents=[shared_state],
        help="Recommend next error-budget attempt.",
    )

    record_parser = subparsers.add_parser(
        "record",
        parents=[shared_state],
        help="Record one attempt from CLI (errors, correction, proof reps).",
    )
    record_parser.add_argument(
        "--phase",
        required=True,
        choices=[phase.value for phase in _Phase],
        help="Practice phase for this attempt.",
    )
    record_parser.add_argument(
        "--prediction",
        required=True,
        type=float,
        help="Predicted quality before checking, in [0,1].",
    )
    record_parser.add_argument(
        "--observed",
        required=True,
        type=float,
        help="Observed quality after evaluation, in [0,1].",
    )
    record_parser.add_argument(
        "--errors",
        help="Comma-separated error tags.",
    )
    record_parser.add_argument(
        "--failure-point",
        help="Pipeline failure point (e.g. formalize_problem).",
    )
    record_parser.add_argument(
        "--feedback-seconds",
        type=float,
        help="Seconds from attempt completion to feedback.",
    )
    record_parser.add_argument(
        "--drill-id",
        help="Drill ID for this attempt (defaults to current drill).",
    )
    record_parser.add_argument(
        "--difficulty",
        type=float,
        help="Difficulty used for this attempt (defaults to current difficulty).",
    )
    record_parser.add_argument(
        "--notes",
        help="Optional notes for this attempt.",
    )
    record_parser.add_argument(
        "--correction",
        help="One correction variable applied on this attempt.",
    )
    record_parser.add_argument(
        "--clean-rep",
        action="store_true",
        help="Mark attempt as a deliberate clean/proof rep after a fix.",
    )
    record_parser.add_argument(
        "--adjust",
        action="store_true",
        help="Run difficulty adjustment after recording.",
    )
    record_parser.add_argument(
        "--diagnose",
        action="store_true",
        help="Run diagnosis after recording.",
    )

    diagnose_parser = subparsers.add_parser(
        "diagnose",
        parents=[shared_state],
        help="Diagnose recent attempts and produce one-variable fix.",
    )
    diagnose_parser.add_argument(
        "--recent-n",
        type=int,
        default=10,
        help="Number of recent attempts to analyze.",
    )

    subparsers.add_parser(
        "adjust",
        parents=[shared_state],
        help="Adjust difficulty toward the target error budget.",
    )

    worktree_list_parser = subparsers.add_parser(
        "worktree-list",
        help="List git worktrees for a repo.",
    )
    worktree_list_parser.add_argument(
        "--repo",
        default=".",
        help="Repository path (default: current directory).",
    )

    worktree_create_parser = subparsers.add_parser(
        "worktree-create",
        help="Create a git worktree for a parallel experiment.",
    )
    worktree_create_parser.add_argument(
        "name",
        help="Worktree name token.",
    )
    worktree_create_parser.add_argument(
        "--repo",
        default=".",
        help="Repository path (default: current directory).",
    )
    worktree_create_parser.add_argument(
        "--worktree-root",
        default="mnt/worktrees",
        help="Worktree root relative to --repo unless absolute.",
    )
    worktree_create_parser.add_argument(
        "--branch-prefix",
        default="alive",
        help="Branch prefix for new worktrees.",
    )
    worktree_create_parser.add_argument(
        "--base-ref",
        default="HEAD",
        help="Base ref for new worktree branches.",
    )

    args = parser.parse_args()

    try:
        if args.command is None:
            state, created = _ensure_state(args.state, auto_create=True)
            loop = _LearningLoop(state)
            print(json.dumps({**_state_payload(args.state, created), "status": loop.status()}, indent=2))
            sys.exit(0)

        if args.command == "init":
            if os.path.exists(args.state) and not args.force:
                payload = {
                    **_state_payload(args.state, created=False),
                    "initialized": False,
                    "reason": "state already exists; use --force to overwrite",
                }
                print(json.dumps(payload, indent=2))
                sys.exit(0)

            state = _init_default_state(skill_name=args.skill_name)
            state.save(args.state)
            loop = _LearningLoop(state)
            payload = {
                **_state_payload(args.state, created=True),
                "initialized": True,
                "status": loop.status(),
            }
            print(json.dumps(payload, indent=2))
            sys.exit(0)

        if args.command == "worktree-list":
            payload = {
                "repo": os.path.abspath(args.repo),
                "worktrees": _GitWorktreeManager.list_worktrees(args.repo),
            }
            print(json.dumps(payload, indent=2))
            sys.exit(0)

        if args.command == "worktree-create":
            created = _GitWorktreeManager.create_worktree(
                repo_path=args.repo,
                worktree_name=args.name,
                worktree_root=args.worktree_root,
                branch_prefix=args.branch_prefix,
                base_ref=args.base_ref,
            )
            print(json.dumps({"created": created}, indent=2))
            sys.exit(0)

        state, created = _ensure_state(args.state, auto_create=True)
        loop = _LearningLoop(state)

        if args.command == "status":
            print(json.dumps({**_state_payload(args.state, created), "status": loop.status()}, indent=2))
            sys.exit(0)

        if args.command == "recommend":
            payload = {
                **_state_payload(args.state, created),
                "recommendation": loop.recommend_next_attempt(),
            }
            print(json.dumps(payload, indent=2))
            sys.exit(0)

        if args.command == "record":
            errors = _parse_error_types(args.errors)
            record = loop.record_attempt(
                phase=_Phase(args.phase),
                prediction=args.prediction,
                observed=args.observed,
                error_types=errors,
                notes=args.notes,
                drill_id=args.drill_id,
                difficulty=args.difficulty,
                failure_point=args.failure_point,
                feedback_seconds=args.feedback_seconds,
                correction=args.correction,
                clean_rep=args.clean_rep,
            )

            adjusted_difficulty = None
            if args.adjust:
                adjusted_difficulty = loop.adjust_difficulty()

            diagnosis = None
            if args.diagnose:
                diagnosis = asdict(loop.diagnose())

            state.save(args.state)
            payload = {
                **_state_payload(args.state, created),
                "recorded_attempt": _attempt_to_payload(record),
                "status": loop.status(),
            }
            if adjusted_difficulty is not None:
                payload["adjusted_difficulty"] = round(adjusted_difficulty, 2)
            if diagnosis is not None:
                payload["diagnosis"] = diagnosis
            print(json.dumps(payload, indent=2))
            sys.exit(0)

        if args.command == "diagnose":
            fix = loop.diagnose(recent_n=args.recent_n)
            state.save(args.state)
            payload = {
                **_state_payload(args.state, created),
                "diagnosis": asdict(fix),
            }
            print(json.dumps(payload, indent=2))
            sys.exit(0)

        if args.command == "adjust":
            new_difficulty = loop.adjust_difficulty()
            state.save(args.state)
            payload = {
                **_state_payload(args.state, created),
                "difficulty": round(new_difficulty, 2),
                "status": loop.status(),
            }
            print(json.dumps(payload, indent=2))
            sys.exit(0)

        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(2)
    except (_GitWorktreeError, FileNotFoundError, ValueError) as exc:
        print(f"Learning loop CLI error: {exc}", file=sys.stderr)
        sys.exit(1)
