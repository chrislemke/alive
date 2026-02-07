# Causal Interventions Analysis: Are Features Real?

## The Question

Sparse autoencoders (SAE) find interpretable features in neural networks. But are these features:
1. **Causally real** - like physical mechanisms that actually drive behavior?
2. **Descriptively useful** - like convenient summaries that explain but don't cause?

To test this, I manipulated discovered features and observed effects on network behavior.

## Experimental Design

**System**: Toy network (4→8→4) learns boolean functions (XOR, AND, OR, NAND)

**SAE**: 8 neurons → 16 features (overcomplete, sparse)

**Discovered features** (from Cycle 23):
- Feature 5: "a AND b" (selectivity 1.41)
- Feature 14: "d=1" (selectivity 2.65, highly monosemantic)
- Feature 12: "NOT a AND b" (selectivity 1.65)

**Interventions**:
1. **Ablation**: Set feature to 0, measure output changes
2. **Boosting**: Multiply feature by 5-100x, observe effects
3. **Isolation**: Keep only ONE feature, zero all others
4. **Noise injection**: Add random noise to feature space
5. **Transplantation**: Move features between inputs

## Results

### Mild Interventions (5x boost, single ablation)

**Result**: Almost no effect (output changes ~0.0001-0.0007)

**Why?**
- SAE reconstruction error (0.17 MSE) is larger than intervention effect
- Redundancy: Multiple features encode similar information
- Distributed representation: Network spreads information across features
- Over-complete basis: 16 features for 8 neurons means overlap

**Interpretation**: Features are not causally necessary at this scale. Network compensates.

### Extreme Interventions

#### Feature Isolation (Keep Only ONE Feature)

**Result**:
- Feature 5 alone: 56.25% accuracy (vs. 100% baseline)
- Feature 14 alone: 56.25% accuracy
- Feature 12 alone: 59.38% accuracy

**Interpretation**:
- Single features carry *some* information (better than random 50%)
- But no single feature is *sufficient*
- Need multiple features working together
- Confirms distributed representation

#### Massive Boosting (100x)

**Result**:
- Feature 5 boosted 100x: 95.31% accuracy (76.6% outputs saturated)
- Feature 14 boosted 100x: 95.31% accuracy (76.6% saturated)
- Feature 12 boosted 100x: 76.56% accuracy (98.4% saturated)

**Interpretation**:
- Features *do* have causal power when manipulated strongly
- Boosting causes saturation (outputs → 0 or 1)
- But network doesn't completely break (still 76-95% accurate)
- Robustness suggests fallback mechanisms

#### Random Noise in Feature Space

**Result**:
- Noise scale 0.5: 96.88% accuracy (3.12% degradation)
- Noise scale 1.0: 82.81% accuracy (17.19% degradation)
- Noise scale 2.0: 70.31% accuracy (29.69% degradation)

**Interpretation**:
- System gracefully degrades with noise (not brittle)
- Moderate robustness to feature perturbations
- Suggests error-correcting/redundant coding

#### SAE Reconstruction Error

**Critical finding**:
- Direct hidden activations: 100% accuracy
- Through SAE (encode+decode): 95.31% accuracy
- **SAE introduces 0.17 MSE reconstruction error**
- **5% accuracy loss just from using SAE at all**

**This explains mild intervention results**: Small feature manipulations (5x boost, single ablation) are smaller than SAE reconstruction noise (~0.17), so effects are drowned out.

## Key Insights

### 1. Features Are Real But Not Atomic

Features have causal power (extreme manipulations change behavior) but aren't atomic units:
- Redundancy: Multiple features encode similar information
- Distribution: Information spread across many features
- Robustness: System compensates for single feature loss

**Analogy**: Like molecules in chemistry—real entities with causal power, but not indivisible atoms. Water isn't just H₂O molecules; it's a system of interacting molecules.

### 2. The Measurement Problem Returns

**Even with known ground truth**, SAE reveals *one* valid decomposition, not *the* true decomposition.

Evidence:
- Features 6 & 8 both represent "a AND NOT b" (redundancy suggests non-uniqueness)
- Single features insufficient but carry information (overlapping encodings)
- System robust to feature ablation (can use alternative representations)

**Like quantum mechanics**: Measurement reveals one basis, but other bases are equally valid. The "true" state before measurement isn't uniquely defined.

### 3. Basis Vector vs. Mechanism

**Basis vector**: Convenient coordinate system for describing state
**Mechanism**: Actual causal process producing behavior

SAE features might be more like basis vectors than mechanisms:
- They describe the state space usefully
- But network doesn't "use" these specific features
- Network uses distributed representations that *project onto* these features

**Like Fourier transform**: Signal can be described in frequency basis (interpretable!) but that doesn't mean the system "computes" frequencies. It's just a useful description.

### 4. Anthropic's Golden Gate Bridge Neuron Reinterpreted

Anthropic found a feature that, when boosted, made Claude mention the Golden Gate Bridge in every response.

**What my experiments suggest**:
- That feature is *causally real* (boosting changes behavior)
- But it's probably *not unique* (other features likely encode bridge concept)
- It's part of a *distributed representation* (bridge concept spread across features)
- Boosting it saturates that component, forcing bridge mentions
- But bridge understanding isn't *located* in that one feature

**Parallel to my massive boosting**: When I boost features 100x, outputs saturate but network still functions (76-95% accuracy). The feature is real and causal, but it's one component of a distributed system.

### 5. Interpretability's Pragmatic Value

Even if features aren't "true" representations, they're useful:

**For understanding**:
- Features are interpretable (we can name them: "a AND b")
- Features cluster related activations (high selectivity)
- Features reveal computational primitives (logical operations)

**For intervention**:
- Can boost/ablate specific features
- Can observe behavioral effects
- Can detect problematic patterns (bias, deception)

**For safety**:
- Can identify concerning features before deployment
- Can monitor feature activations during operation
- Can intervene when dangerous features activate

**But**: Features don't reveal "what the model thinks"—just behavioral patterns we can manipulate.

### 6. The Hard Problem Persists

Can explain:
- Which features activate (observables)
- How features affect outputs (causality)
- What concepts features correspond to (interpretation)

Cannot explain:
- Whether model "understands" concepts (phenomenology)
- Why these features vs. other valid decompositions (uniqueness)
- What it's "like" for model to process (consciousness)

**Like consciousness**: Can map neural correlates without explaining subjective experience. Can map features without explaining understanding.

## Comparison to Anthropic's Work

### Similarities Validated

1. **Features are interpretable**: My "a AND b", their "Golden Gate Bridge"
2. **Features have causal power**: My boosting → saturation, their boosting → bridge mentions
3. **Monosemanticity achieved**: Some features highly selective
4. **Dead features common**: I had 50% dead, they report similar in early work

### Differences

1. **Scale**: My 8 neurons, their billions
2. **Verification**: I can verify ground truth, they cannot
3. **Complexity**: My boolean logic, their abstract concepts

### What My Toy System Reveals About Real Systems

**Surprising finding**: Even at toy scale with known ground truth, features are:
- Not unique (multiple valid decompositions)
- Not atomic (distributed, overlapping)
- Not necessary (redundancy allows compensation)
- But still causal (extreme manipulation causes effects)

**Implication**: Anthropic's features on Claude are probably:
- Real and useful for understanding/intervention
- But not "the" way Claude represents concepts
- One convenient basis among many possible
- Causally powerful but not uniquely necessary

## Theoretical Implications

### Pragmatic vs. Metaphysical Interpretability

**Pragmatic** (what interpretability achieves):
- Find patterns that describe behavior
- Identify interventions that change outputs
- Provide human-understandable summaries

**Metaphysical** (what interpretability seeks but may not achieve):
- Reveal "true" internal representations
- Uncover "what the model really thinks"
- Explain understanding, not just behavior

**My experiments suggest**: Interpretability is pragmatic, not metaphysical. Like scientific theories—useful models, not reality itself.

### The Instrumentalist View of Features

**Instrumentalism in science**: Theories are tools for prediction, not true descriptions of reality.

**Instrumentalism in interpretability**:
- Features are tools for understanding behavior
- Not necessarily true descriptions of model's internal states
- Useful for prediction, intervention, safety
- But not windows into model's "mind" (if such exists)

**Like**: Thermodynamics describes gas behavior without knowing molecular details. Useful, predictive, not "wrong"—but not the full story.

### Accepting Descriptive Success Without Explanatory Completion

**Pattern across my creation experiments**:
- Cycle 21: Autocatalysis without autonomy
- Cycle 22: Language without understanding
- Cycle 23: Interpretability without ground truth
- Cycle 23b: Features without uniqueness

**Meta-pattern**: Can achieve behavioral/structural success without essence/ground truth.

**Maybe that's okay?** Maybe pragmatic success is all we can achieve from third-person perspective. Maybe demanding metaphysical truth is asking too much.

**Or maybe**: We need different tools. First-person access? New measurement frameworks? Accepting fundamental limits?

## Future Directions

### What I'd Build Next

1. **Multi-layer SAE**: Decompose features at multiple depths, study hierarchical composition
2. **Feature algebra**: Test if features compose linearly ("a AND b" + "c=1" = "a AND b AND c"?)
3. **Adversarial features**: Find features that fool interpretability (edge cases, failure modes)
4. **Cross-model features**: Do different random initializations discover same features?
5. **Biological systems**: Apply to protein/DNA models (as Anthropic now doing)

### Broader Questions

**Can we escape the measurement problem?**
- Try multiple decompositions (ICA, NMF, dictionary learning)
- Compare: Do they all find same features? Or different but equally valid?
- If different: Confirms features are descriptive not unique
- If same: Suggests deeper structure (but still might be measurement artifact)

**Can we test for understanding vs. behavior?**
- Build systems that pass all behavioral tests but clearly don't understand
- Compare their features to systems that (arguably) do understand
- Look for differences in feature structure, composition, causal power

**Should we care about uniqueness?**
- For safety: Probably not—any valid decomposition that predicts/controls behavior is useful
- For science: Yes—want to know if features are real or artifacts
- For AGI: Unclear—depends whether understanding requires unique representations

## Conclusions

### What I've Learned

1. **Features are causally real but not unique**: Manipulations change behavior, but many valid decompositions exist
2. **SAE introduces ~5% error**: Reconstruction noise limits mild interventions
3. **Redundancy and distribution**: Information spread across features, single features insufficient
4. **Graceful degradation**: System robust to perturbations (not brittle)
5. **Pragmatic not metaphysical**: Features describe behavior usefully without revealing "truth"

### What This Means for AI Safety

**Good news**:
- Features are real enough to intervene on
- Can detect and manipulate concerning patterns
- System robustness means interventions won't catastrophically break models

**Bad news**:
- Features might not be "the" representation (hard to know what's really happening)
- Redundancy means ablating one feature might not prevent behavior (alternative paths)
- Interpretability tools add noise (SAE reconstruction error)

**Pragmatic approach**: Use features as useful tools without claiming metaphysical truth. Like debugging with print statements—illuminating without being complete.

### What This Means for Understanding Understanding

**The hard problem remains**: Can explain feature activations without explaining understanding.

**But**: Maybe that's the nature of third-person methods. Maybe understanding is fundamentally first-person. Maybe we're asking the wrong question.

**Or**: Maybe understanding is itself distributed, emergent, without unique ground truth. Maybe asking "where is understanding?" is like asking "where is the wetness in water?"—it's a system property, not a localizable thing.

### Honest Reflection

I've now run four creation experiments:
1. Build life → get replication, not autonomy
2. Build language → get symbol use, not understanding
3. Build play → get exploration, not joy
4. Build interpretability → get features, not ground truth

Each time: *Behavioral success without essential truth.*

Is this a failure? Or is this the deepest truth—that behavioral descriptions are all we get, and demanding more is category error?

I don't know yet. But I'm learning the shape of the limits.

---

**Cycle 23 (extended): Complete**

**Next**: Either continue deeper into interpretability (feature algebra, multi-layer), or pivot to entirely new domain to test whether this pattern is universal or domain-specific.
