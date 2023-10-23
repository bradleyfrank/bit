#!/usr/bin/env python3

import argparse
import os
import re
import subprocess
from pathlib import Path

import inquirer
#from iterfzf import iterfzf
from colorama import init, Fore


def proc(cmd: str) -> dict:
    out = subprocess.run(cmd.split(), capture_output=True, check=False)
    return {
        "rc": out.returncode,
        "stdout": out.stdout.decode("UTF-8"),
        "stderr": out.stderr.decode("UTF-8"),
    }


def in_git_repo() -> bool:
    return proc("git rev-parse --show-toplevel")["rc"] == 0


def git_toplevel() -> Path:
    return Path(proc("git rev-parse --show-toplevel")["stdout"])


def git_repo_name(worktree_path: Path) -> str:
    result = proc(f"git --work-tree {str(worktree_path).strip()} config --get remote.origin.url")
    return Path(result["stdout"]).stem if result["rc"] == 0 else None


def git_worktree_add(toplevel: Path, worktree_name: str) -> Path:
    branch_path = f"{str(toplevel.parent).strip()}/{worktree_name}"
    worktree_dir = str(toplevel).strip()
    result = proc(f"git --work-tree {worktree_dir} worktree add {branch_path}")
    if result["rc"] != 0:
        raise SystemExit(Fore.RED + result["stderr"])
    return Path(branch_path)


def open_in_tmux(worktree: Path) -> None:
    directory = str(worktree).strip()
    if not os.environ.get("TMUX"):
        print(f"{Fore.MAGENTA}Not in a tmux session: {Fore.RESET}{directory}")
        return
    repo = git_repo_name(worktree) or str(worktree.parts[-2])
    new_window = proc(f"tmux new-window -n {repo} ({worktree.name}) -c {directory} -P")["stdout"]


def branch(flags) -> None:
    if not in_git_repo():
        raise SystemExit(Fore.RED + "Not in a Git repository")
    toplevel = git_toplevel()
    worktree = git_worktree_add(toplevel, flags.name)
    open_in_tmux(worktree)


def pull() -> None:
    pass


def delete(flags) -> None:
    if not in_git_repo():
        raise SystemExit(Fore.RED + "Not in a Git repository")
    git_worktree_list = proc("git worktree list --porcelain")
    if git_worktree_list["rc"] != 0:
        raise SystemExit(Fore.RED + git_worktree_list["stderr"])

    matches = re.compile(r"^worktree\s*(.*)", re.MULTILINE).findall(git_worktree_list["stdout"])
    exclude_branches = f"(main|master|{str(git_toplevel().name).strip()})$"
    options = [branch for branch in matches if re.search(rf"{exclude_branches}", branch) is None]
    if not options:
        raise SystemExit(Fore.RED + "No worktrees available to delete")
    questions = [inquirer.Checkbox("choices", "Delete which worktrees?", options)]
    answers = inquirer.prompt(questions)["choices"]
    if not answers:
        print(f"{Fore.MAGENTA}No worktrees selected")
        return

    for answer in answers:
        git_worktree_remove = proc(f"git worktree remove --force {answer}")
        git_branch_delete = proc(f"git branch --delete --force {answer}")


def clone() -> None:
    pass


init(autoreset=True)  # colorama init

parser = argparse.ArgumentParser(prog="bit")
subparsers = parser.add_subparsers(help="Subcommands")

subparser_branch = subparsers.add_parser("branch", help="Create a new branch")
subparser_branch.add_argument("-n", "--name", help="Name of new branch")
subparser_branch.set_defaults(func=branch)

subparser_pull = subparsers.add_parser("pull", help="Pull a branch from origin")
subparser_pull.add_argument("-n", "--name", help="Name of branch to pull")
subparser_pull.set_defaults(func=pull)

subparser_clone = subparsers.add_parser("clone", help="Clone a repo into a worktree")
subparser_clone.add_argument("-g", "--git", help="URL of Git repo")
subparser_clone.set_defaults(func=clone)

subparser_delete = subparsers.add_parser("delete", help="Delete worktree(s)")
subparser_delete.set_defaults(func=delete)

args = parser.parse_args()
args.func(args)
