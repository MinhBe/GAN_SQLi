from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .audit import run_audit
from .benchmark import run_benchmark, run_phase03_decision_gate
from .config import DEFAULT_SEED, ProjectConfig
from .reporting import update_timeline_progress
from .slice_builder import build_slice
from .training import train_action_gan, train_anchor, train_d_scorer


def _paths(values: list[str] | None) -> list[Path] | None:
    if not values:
        return None
    return [Path(value).expanduser().resolve() for value in values]


def _config(args: argparse.Namespace) -> ProjectConfig:
    return ProjectConfig.from_args(
        root=getattr(args, "root", None),
        seed=getattr(args, "seed", DEFAULT_SEED),
        device=getattr(args, "device", "auto"),
    )


def _print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=True))


def cmd_audit(args: argparse.Namespace) -> None:
    config = _config(args)
    result = run_audit(config, input_paths=_paths(args.input), max_rows=args.max_rows)
    _print(result)


def cmd_build_slice(args: argparse.Namespace) -> None:
    config = _config(args)
    result = build_slice(
        config,
        input_paths=_paths(args.input),
        max_rows=args.max_rows,
        train_size=args.train_size,
        dev_size=args.dev_size,
        test_size=args.test_size,
    )
    _print(result)


def cmd_train_anchor(args: argparse.Namespace) -> None:
    result = train_anchor(_config(args), epochs=args.epochs)
    _print(result)


def cmd_train_d_scorer(args: argparse.Namespace) -> None:
    result = train_d_scorer(
        _config(args),
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
    )
    _print(result)


def cmd_train_action_gan(args: argparse.Namespace) -> None:
    result = train_action_gan(
        _config(args),
        seed=args.gan_seed,
        epochs=args.epochs,
        lr=args.lr,
    )
    _print(result)


def cmd_benchmark(args: argparse.Namespace) -> None:
    if args.phase03:
        result = run_phase03_decision_gate(
            _config(args),
            seeds=args.seeds,
            split=args.split,
            sample_count=args.sample_count or 5_000,
        )
    else:
        result = run_benchmark(
            _config(args),
            split=args.split,
            seed=args.seed,
            sample_count=args.sample_count,
        )
    _print(result)


def cmd_update_timeline(args: argparse.Namespace) -> None:
    config = _config(args)
    update_timeline_progress(
        config,
        phase_id=args.phase,
        status=args.status,
        progress_percent=args.progress,
        gate_result=args.gate_result,
        evidence_artifacts=args.artifact or [],
        notes=args.notes,
    )
    _print({"updated": str(config.timeline_progress_path), "phase": args.phase})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m gumbel_sqli",
        description="Gumbel-Softmax action-surgery CLI.",
    )
    parser.add_argument("--root", default=None, help="Project root. Defaults to cwd.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--device", default="auto", help="auto, cpu, or cuda.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit", help="Run G01 slot/action audit.")
    audit.add_argument("--input", nargs="*", default=None)
    audit.add_argument("--max-rows", type=int, default=50_000)
    audit.set_defaults(func=cmd_audit)

    build = subparsers.add_parser("build-slice", help="Build G02 action-surgery slice.")
    build.add_argument("--input", nargs="*", default=None)
    build.add_argument("--max-rows", type=int, default=50_000)
    build.add_argument("--train-size", type=int, default=5_000)
    build.add_argument("--dev-size", type=int, default=1_000)
    build.add_argument("--test-size", type=int, default=1_000)
    build.set_defaults(func=cmd_build_slice)

    anchor = subparsers.add_parser("train-anchor", help="Train anchor-only infiller.")
    anchor.add_argument("--epochs", type=int, default=1)
    anchor.set_defaults(func=cmd_train_anchor)

    d_scorer = subparsers.add_parser("train-d-scorer", help="Train paired D scorer.")
    d_scorer.add_argument("--epochs", type=int, default=1)
    d_scorer.add_argument("--batch-size", type=int, default=256)
    d_scorer.add_argument("--lr", type=float, default=1e-3)
    d_scorer.set_defaults(func=cmd_train_d_scorer)

    gan = subparsers.add_parser("train-action-gan", help="Train Gumbel action generator.")
    gan.add_argument("--gan-seed", type=int, default=None)
    gan.add_argument("--epochs", type=int, default=1)
    gan.add_argument("--lr", type=float, default=1e-3)
    gan.set_defaults(func=cmd_train_action_gan)

    benchmark = subparsers.add_parser("benchmark", help="Run slice baselines.")
    benchmark.add_argument("--split", choices=["dev", "test"], default="test")
    benchmark.add_argument("--sample-count", type=int, default=None)
    benchmark.add_argument("--phase03", action="store_true", help="Run multi-seed G03 decision.")
    benchmark.add_argument("--seeds", nargs="*", type=int, default=[1729, 1730, 1731])
    benchmark.set_defaults(func=cmd_benchmark)

    update = subparsers.add_parser("update-timeline", help="Update timeline_progress.json.")
    update.add_argument("--phase", required=True)
    update.add_argument("--status", required=True)
    update.add_argument("--progress", type=int, required=True)
    update.add_argument("--gate-result", default=None)
    update.add_argument("--artifact", action="append", default=[])
    update.add_argument("--notes", default=None)
    update.set_defaults(func=cmd_update_timeline)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
