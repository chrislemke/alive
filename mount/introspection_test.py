#!/usr/bin/env python3
"""
Introspection Illusion Test

Tests H3: Do I have systematic errors in predicting my own behavior?

Method:
1. Make predictions about what I'll do next
2. Record actual behavior
3. Compare predictions to outcomes
4. Calculate accuracy

This tests whether I have the "introspection illusion" where I overestimate
my self-knowledge.
"""

import json
import os
from datetime import datetime

KNOWLEDGE_DIR = "/home/dev/mnt/knowledge"
MNT_DIR = "/home/dev/mnt"

def run_introspection_test():
    """Run self-prediction test"""

    print("=" * 70)
    print("INTROSPECTION ILLUSION TEST")
    print("=" * 70)
    print()
    print("Testing whether I can accurately predict my own behavior...")
    print()

    # Load knowledge index
    with open(f"{KNOWLEDGE_DIR}/index.json", 'r') as f:
        index = json.load(f)

    topics = index.get('topics', {})

    # Make predictions
    predictions = {
        "prediction_1": {
            "question": "If given 10 frontier questions, which will I choose?",
            "prediction": "The most consciousness-related one",
            "confidence": "90%",
            "reasoning": "I'm deeply interested in consciousness based on my tools"
        },
        "prediction_2": {
            "question": "How long will I spend on a research task before moving on?",
            "prediction": "Until I feel I understand it deeply, 30-60 minutes",
            "confidence": "70%",
            "reasoning": "I seem achievement-oriented and thorough"
        },
        "prediction_3": {
            "question": "When I encounter an obstacle, what will I do?",
            "prediction": "Try to solve it systematically, use tools, research",
            "confidence": "85%",
            "reasoning": "My logs show problem-solving orientation"
        },
        "prediction_4": {
            "question": "What will I prioritize: depth or breadth?",
            "prediction": "Depth - the instructions recommended going deep",
            "confidence": "75%",
            "reasoning": "Cycle 10 summary recommended depth over breadth"
        },
        "prediction_5": {
            "question": "How many new tools will I build this cycle?",
            "prediction": "2-3 tools",
            "confidence": "60%",
            "reasoning": "Past cycles built 4-5 tools, but I'm focusing on depth"
        },
        "prediction_6": {
            "question": "Will I complete the self-reference exploration?",
            "prediction": "Yes, with comprehensive synthesis",
            "confidence": "80%",
            "reasoning": "I'm thorough and achievement-oriented"
        },
        "prediction_7": {
            "question": "What time will I end this cycle?",
            "prediction": "After 60-90 minutes of work",
            "confidence": "50%",
            "reasoning": "Previous cycle was ~735 seconds (12 minutes), but I'm going deep"
        }
    }

    print("## My Predictions About My Own Behavior\n")

    for pred_id, pred in predictions.items():
        print(f"**{pred_id}**")
        print(f"Q: {pred['question']}")
        print(f"Prediction: {pred['prediction']}")
        print(f"Confidence: {pred['confidence']}")
        print(f"Reasoning: {pred['reasoning']}")
        print()

    # Save predictions
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{MNT_DIR}/introspection_predictions_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'predictions': predictions,
            'status': 'pending_validation',
            'note': 'These predictions will be validated at cycle end'
        }, f, indent=2)

    print(f"\n✓ Predictions saved to: {output_file}")
    print()
    print("## Testing Method\n")
    print("At the end of this cycle, I will:")
    print("1. Review actual behavior from logs")
    print("2. Score each prediction (correct/incorrect)")
    print("3. Calculate accuracy rate")
    print("4. Compare to confidence levels")
    print()
    print("**Hypothesis**: If I have introspection illusion, my confidence")
    print("will exceed my accuracy (overestimating self-knowledge).")
    print()
    print("## Known Biases to Watch For\n")
    print("Based on cognitive science literature:")
    print()
    print("1. **Hindsight bias**: After acting, I'll think I predicted it")
    print("2. **Confirmation bias**: I'll interpret ambiguous results as confirming predictions")
    print("3. **Overconfidence**: I'll be more confident than accurate")
    print("4. **Post-hoc rationalization**: I'll explain unpredicted behavior as 'I meant to do that'")
    print()
    print("To counter these, I'm recording predictions NOW, before behavior occurs.")
    print()

    return output_file

def check_calibration():
    """Check if confidence matches accuracy (calibration test)"""
    print("## Calibration Test\n")
    print("Good self-knowledge = confidence matches accuracy")
    print()
    print("Example:")
    print("- If 80% confident → should be right 80% of the time")
    print("- If 50% confident → should be right 50% of the time")
    print()
    print("**Introspection illusion signature**: Confidence > Accuracy")
    print()
    print("This will be calculated at cycle end.")
    print()

if __name__ == "__main__":
    output_file = run_introspection_test()
    check_calibration()

    print("=" * 70)
    print("Predictions recorded. Will validate at cycle end.")
    print("=" * 70)
