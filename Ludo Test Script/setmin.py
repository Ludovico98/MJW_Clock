#!/usr/bin/env python3
"""Set the MJW clock minute hand to the requested minute."""

import argparse
import sys

from clock_controller import ClockController


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Move the minute hand to the specified minute.")
    parser.add_argument(
        "minute",
        type=int,
        help="Target minute (0-59)."
    )
    return parser.parse_args()


def validate_input(minute_value: int) -> None:
    if minute_value < 0 or minute_value > 59:
        raise ValueError("Minute must be between 0 and 59 inclusive.")


def main() -> int:
    try:
        args = parse_args()
        validate_input(args.minute)

        print(f"Setting minute hand to {args.minute:02d} minutes")

        with ClockController() as controller:
            controller.set_minute(args.minute)

        print("Minute hand set successfully")
        return 0
    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - allow hardware errors to surface
        print(f"Failed to set minute hand: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
