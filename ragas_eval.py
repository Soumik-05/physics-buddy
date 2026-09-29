"""
ragas_eval.py — RAGAS Baseline Evaluation for PhysicsBuddy
Part 6 of the capstone process.
Computes: faithfulness, answer_relevancy, context_precision

If RAGAS is not installed, falls back to manual LLM-based faithfulness scoring.
Run: python ragas_eval.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.graph import build_graph, ask

# ── 5 Gold-standard QA pairs with ground truth from KB ───────────────────────
RAGAS_DATASET = [
    {
        "question": "What is Newton's Second Law of Motion?",
        "ground_truth": (
            "Newton's Second Law states that Force equals mass times acceleration (F = ma). "
            "A larger force produces greater acceleration, and a heavier object requires more force "
            "to achieve the same acceleration."
        )
    },
    {
        "question": "What are the four equations of kinematics?",
        "ground_truth": (
            "The four equations are: v = u + at; s = ut + ½at²; v² = u² + 2as; s = (u + v)/2 × t. "
            "These apply only for constant acceleration."
        )
    },
    {
        "question": "What is escape velocity on Earth?",
        "ground_truth": (
            "Escape velocity is the minimum speed needed for an object to escape Earth's gravity. "
            "v_e = √(2gR) ≈ 11.2 km/s."
        )
    },
    {
        "question": "State Faraday's Law of Electromagnetic Induction.",
        "ground_truth": (
            "Faraday's Law states that EMF = -dΦ/dt, where Φ is the magnetic flux. "
            "The induced EMF opposes the change in flux (Lenz's Law)."
        )
    },
    {
        "question": "What is the energy of a photon?",
        "ground_truth": (
            "The energy of a photon is E = hf = hc/λ, where h = 6.626×10⁻³⁴ J·s is Planck's constant, "
            "f is frequency, c is speed of light, and λ is wavelength."
        )
    }
]


def run_ragas_evaluation(app):
    print("\n" + "="*65)
    print("PhysicsBuddy — RAGAS Baseline Evaluation")
    print("="*65)

    # Collect agent outputs
    eval_data = []
    for i, item in enumerate(RAGAS_DATASET):
        print(f"\n[{i+1}/5] Running: {item['question'][:60]}...")
        result = ask(app, item["question"], thread_id=f"ragas_{i}")
        eval_data.append({
            "question": item["question"],
            "answer": result.get("answer", ""),
            "contexts": [result.get("retrieved", "")],
            "ground_truth": item["ground_truth"],
            "faithfulness_score": result.get("faithfulness", 0.0)
        })
        print(f"  Faithfulness (agent): {result.get('faithfulness', 0.0):.2f}")

    # Try RAGAS
    try:
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy, context_precision
        from datasets import Dataset

        ragas_input = {
            "question": [d["question"] for d in eval_data],
            "answer": [d["answer"] for d in eval_data],
            "contexts": [d["contexts"] for d in eval_data],
            "ground_truth": [d["ground_truth"] for d in eval_data],
        }
        dataset = Dataset.from_dict(ragas_input)
        scores = evaluate(dataset, metrics=[faithfulness, answer_relevancy, context_precision])

        print("\n" + "="*65)
        print("RAGAS Scores (Baseline):")
        print(f"  Faithfulness:        {scores['faithfulness']:.3f}")
        print(f"  Answer Relevancy:    {scores['answer_relevancy']:.3f}")
        print(f"  Context Precision:   {scores['context_precision']:.3f}")
        print("="*65)
        return scores

    except ImportError:
        # Manual fallback
        print("\n[RAGAS not installed — using manual LLM faithfulness scoring]")
        avg_faith = sum(d["faithfulness_score"] for d in eval_data) / len(eval_data)
        print(f"\nManual Faithfulness (average): {avg_faith:.3f}")
        print("Install RAGAS for full metrics: pip install ragas")
        return {"faithfulness": avg_faith, "answer_relevancy": "N/A", "context_precision": "N/A"}


if __name__ == "__main__":
    app, _, _, _ = build_graph()
    run_ragas_evaluation(app)
