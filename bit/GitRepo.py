#!/usr/bin/env python3

from pathlib import Path

class GitRepo():
    def __init__(self, repository: Path) -> None:
        self.in_git_repo = None
        self.common = None
        self.toplevel = None
        self.name = None

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

