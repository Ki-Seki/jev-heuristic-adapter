"""Use `python -m evals plan` to inspect the matrix without network access."""

import argparse
import json
import math
from pathlib import Path

from .data import plan, prepare


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("plan", help="Print the fixed evaluation matrix; no network")
    for name in ("prepare", "run"):
        command = commands.add_parser(name)
        command.add_argument("--output", type=Path, required=True)
        if name == "run":
            command.add_argument("--budget-usd", type=float, required=True)
            command.add_argument("--workers", type=int, default=6)
    args = parser.parse_args(argv)
    if args.command == "plan":
        print(json.dumps(plan(), indent=2))
    elif args.command == "prepare":
        prepare(args.output)
    elif args.command == "run":
        from .run import run

        if (
            not math.isfinite(args.budget_usd)
            or args.budget_usd <= 0
            or args.workers <= 0
        ):
            parser.error("budget and workers must be positive")
        run(args.output, args.budget_usd, args.workers)


if __name__ == "__main__":
    main()
