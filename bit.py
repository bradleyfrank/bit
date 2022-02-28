#!/usr/bin/env python3

"""Wrapper for managing Git branches and worktrees.
"""

import argparse
import datetime

def dt_now(dtformat: str) -> str:
    """Prints current date and time."""
    now = datetime.datetime.now()
    return now.strftime(dtformat)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Brad's Git wrapper")

    subparsers = parser.add_subparsers(dest="mode")

    create_parser = subparsers.add_parser("create", help="Creates a new branch in a worktree")
    create_parser.add_argument("--name", "-n", help="Branch name", default=dt_now("%Y-%b-%d-%H%M"))

    sailor_parser = subparsers.add_parser("sailors", help="Talk to a sailor")
    sailor_parser.add_argument("name", help="Sailors name")
    sailor_parser.add_argument("--greeting", "-g", help="Greeting", default="Ahoy there")

    args = parser.parse_args()
    if args.func == "sailors":
        greet(args.greeting, args.name)
    elif args.command == "list":
        list_ships()
    else:
        sail()
