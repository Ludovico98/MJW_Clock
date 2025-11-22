#!/usr/bin/env python3
"""Set the MJW clock hour hand to the requested position."""

import argparse
import sys

from clock_controller import ClockController


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Move the hour hand to the specified time.")
    parser.add_argument(
        "hour",
        type=int,
        help="Target hour (0-23). Values >= 12 map to afternoon positions."
    )
    parser.add_argument(
        "--minute",
        type=int,
        default=0,
        help="Minute offset (0-59) to align the hour hand fractionally."
    )
    return parser.parse_args()


def validate_inputs(hour_value: int, minute_value: int) -> None:
    if hour_value < 0 or hour_value > 23:
        raise ValueError("Hour must be between 0 and 23 inclusive.")
    if minute_value < 0 or minute_value > 59:
        raise ValueError("Minute offset must be between 0 and 59 inclusive.")


def hour_to_index(hour_value: int) -> int:
    return hour_value % 12


def format_display(hour_index: int, minute_value: int) -> str:
    display_hour = hour_index if hour_index != 0 else 12
    return f"{display_hour:02d}:{minute_value:02d}"


def main() -> int:
    try:
        args = parse_args()
        validate_inputs(args.hour, args.minute)

        hour_index = hour_to_index(args.hour)
        display_time = format_display(hour_index, args.minute)
        print(f"Setting hour hand to {display_time}")

        with ClockController() as controller:
            controller.set_hour(hour_index, args.minute)

        print("Hour hand set successfully")
        return 0
    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 - propagate GPIO errors to stderr
        print(f"Failed to set hour hand: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
