"""CLI để chạy 1 cuộc debate từ command line.

Examples:
    # Dùng claim mặc định
    python experiments/run_demo.py

    # Tự nhập claim
    python experiments/run_demo.py --claim "Vitamin C prevents the common cold."

    # Tăng số round
    python experiments/run_demo.py --claim "..." --rounds 3

    # Đổi model (phải có sẵn trong Ollama)
    python experiments/run_demo.py --model llama3.2:3b

    # Lưu kết quả ra JSON
    python experiments/run_demo.py --claim "..." --output result.json
"""
import argparse
import json
from dataclasses import asdict
from pathlib import Path

from scidebate import Debate
from scidebate.llms import OllamaLLM


DEFAULT_CLAIM = "Drinking 8 glasses of water per day is essential for human health."


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run a Multi-Agent Debate on a scientific claim.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--claim",
        type=str,
        default=DEFAULT_CLAIM,
        help="Scientific claim to debate",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="qwen2.5:3b",
        help="Ollama model name",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=2,
        help="Number of debate rounds",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="LLM sampling temperature",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=300,
        help="Max tokens per turn",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional: path to save result as JSON",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress live turn-by-turn logs (only show final verdict)",
    )
    return parser.parse_args()


def result_to_dict(result) -> dict:
    """Convert DebateResult sang dict để dump JSON."""
    return {
        "claim": result.claim,
        "num_rounds": result.num_rounds,
        "verdict": {
            "verdict": result.verdict.verdict,
            "confidence": result.verdict.confidence,
            "justification": result.verdict.justification,
        } if result.verdict else None,
        "transcript": [
            {"round": t.round_num, "speaker": t.speaker, "content": t.content}
            for t in result.transcript
        ],
    }


def main():
    args = parse_args()

    # Init LLM
    llm = OllamaLLM(
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    # Init debate
    debate = Debate(
        llm=llm,
        max_rounds=args.rounds,
        verbose=not args.quiet,
    )

    # Run
    result = debate.run(args.claim)

    # Final summary (always show)
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(result.summary())

    # Save to JSON if requested
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_to_dict(result), f, indent=2, ensure_ascii=False)
        print(f"\nResult saved to: {output_path}")


if __name__ == "__main__":
    main()