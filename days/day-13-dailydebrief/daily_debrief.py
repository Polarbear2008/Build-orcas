import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

try:
    import git as gitpython
    HAS_GITPYTHON = True
except ImportError:
    HAS_GITPYTHON = False

try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False


DEFAULT_MODEL = "qwen2.5:3b"
MAX_SHELL_LINES = 1200
MAX_FILE_ROWS = 30
ERROR_KEYWORDS = {
    "error",
    "fatal",
    "traceback",
    "permission denied",
    "command not found",
    "failed",
    "exception",
}

console = Console()


def first_line(text: str) -> str:
    """Return first non-empty line from multi-line text."""
    return text.strip().split("\n")[0] if text.strip() else ""


def strip_markdown_fence(text: str) -> str:
    """Remove markdown code fences if model wraps JSON output."""
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    return re.sub(r"\n?```$", "", text).strip()


def collect_git_data(since_dt: datetime) -> dict:
    """Collect commit activity from the current git repository."""
    data = {
        "found": False,
        "branch": None,
        "commits": [],
        "insertions": 0,
        "deletions": 0,
    }
    if not HAS_GITPYTHON:
        data["error"] = "gitpython not installed"
        return data

    try:
        repo = gitpython.Repo(search_parent_directories=True)
    except gitpython.exc.InvalidGitRepositoryError:
        data["error"] = "no git repo found"
        return data

    data["found"] = True
    data["branch"] = repo.active_branch.name if not repo.head.is_detached else "detached"

    for commit in repo.iter_commits():
        commit_dt = datetime.fromtimestamp(commit.committed_date)
        if commit_dt < since_dt:
            break
        stats = commit.stats.total
        data["commits"].append(
            {
                "hash": commit.hexsha[:7],
                "time": commit_dt.isoformat(timespec="minutes"),
                "message": first_line(commit.message),
                "files": stats["files"],
                "insertions": stats["insertions"],
                "deletions": stats["deletions"],
            }
        )
        data["insertions"] += stats["insertions"]
        data["deletions"] += stats["deletions"]
    return data


def find_history_file() -> Optional[Path]:
    """Find the best available shell history file."""
    candidates = [
        Path.home() / ".zsh_history",
        Path.home() / ".bash_history",
        Path(os.environ.get("HISTFILE", "")),
    ]
    for path in candidates:
        if path.exists() and path.stat().st_size > 0:
            return path
    return None


def parse_history_lines(history_path: Path) -> list[tuple[Optional[int], str]]:
    """Parse shell history into (timestamp, command) entries."""
    out: list[tuple[Optional[int], str]] = []
    try:
        raw_lines = history_path.read_text(errors="ignore").splitlines()
    except Exception:
        return out

    for line in raw_lines[-MAX_SHELL_LINES:]:
        line = line.strip()
        if not line:
            continue
        # zsh extended format: : 1712708642:0;git status
        if line.startswith(": ") and ";" in line:
            prefix, command = line.split(";", 1)
            ts_match = re.match(r"^:\s*(\d+):\d+$", prefix)
            timestamp = int(ts_match.group(1)) if ts_match else None
            out.append((timestamp, command.strip()))
            continue
        if not line.startswith("#"):
            out.append((None, line))
    return out


def collect_shell_data(since_dt: datetime) -> dict:
    """Collect shell command patterns and simple friction signals."""
    data = {
        "found": False,
        "history_file": None,
        "commands": [],
        "total_commands": 0,
        "top_commands": [],
        "error_hits": 0,
    }
    history_path = find_history_file()
    if not history_path:
        data["error"] = "no shell history found"
        return data

    parsed = parse_history_lines(history_path)
    if not parsed:
        data["error"] = "history file unreadable or empty"
        return data

    since_ts = int(since_dt.timestamp())
    commands: list[str] = []
    for ts, command in parsed:
        if ts is None or ts >= since_ts:
            commands.append(command)

    if not commands:
        # fallback for histories without timestamps
        commands = [cmd for _, cmd in parsed[-200:]]

    counter = Counter(commands)
    error_hits = 0
    for command in commands:
        low = command.lower()
        if any(keyword in low for keyword in ERROR_KEYWORDS):
            error_hits += 1

    data["found"] = True
    data["history_file"] = str(history_path)
    data["commands"] = commands[-20:]
    data["total_commands"] = len(commands)
    data["top_commands"] = counter.most_common(8)
    data["error_hits"] = error_hits
    return data


def collect_file_data(since_dt: datetime) -> dict:
    """Collect recently modified files in the current project directory."""
    data = {"total_modified": 0, "files": [], "by_extension": {}}
    root = Path.cwd()
    since_ts = since_dt.timestamp()
    rows = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(
            part in {".git", "__pycache__", "node_modules", ".venv", "venv"}
            for part in path.parts
        ):
            continue
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if mtime >= since_ts:
            ext = path.suffix or "no_ext"
            rows.append({"path": str(path.relative_to(root)), "mtime": mtime, "ext": ext})
            data["by_extension"][ext] = data["by_extension"].get(ext, 0) + 1

    rows.sort(key=lambda item: item["mtime"], reverse=True)
    data["total_modified"] = len(rows)
    data["files"] = [
        {
            "path": item["path"],
            "mtime": datetime.fromtimestamp(item["mtime"]).strftime("%Y-%m-%d %H:%M"),
            "ext": item["ext"],
        }
        for item in rows[:MAX_FILE_ROWS]
    ]
    return data


def build_context(git_data: dict, shell_data: dict, file_data: dict, since_hours: int) -> str:
    """Build a compact text context to send to the local LLM."""
    lines = [f"Activity window: last {since_hours} hours", ""]
    lines.append("GIT:")
    if git_data["found"]:
        lines.append(
            f"branch={git_data['branch']} commits={len(git_data['commits'])} "
            f"+{git_data['insertions']} -{git_data['deletions']}"
        )
        for commit in git_data["commits"][:6]:
            lines.append(f"- {commit['hash']} {commit['message']} ({commit['time']})")
    else:
        lines.append(f"- {git_data.get('error', 'no data')}")

    lines.append("")
    lines.append("SHELL:")
    if shell_data["found"]:
        lines.append(
            f"total={shell_data['total_commands']} "
            f"error_hits={shell_data['error_hits']} "
            f"history={shell_data['history_file']}"
        )
        if shell_data["top_commands"]:
            top = ", ".join(
                f"{cmd} ({count}x)" for cmd, count in shell_data["top_commands"][:5]
            )
            lines.append(f"- top commands: {top}")
        lines.append(f"- sample: {' | '.join(shell_data['commands'])}")
    else:
        lines.append(f"- {shell_data.get('error', 'no data')}")

    lines.append("")
    lines.append("FILES:")
    lines.append(f"modified={file_data['total_modified']}")
    if file_data["by_extension"]:
        ext_summary = ", ".join(
            f"{ext}:{count}"
            for ext, count in sorted(
                file_data["by_extension"].items(),
                key=lambda kv: kv[1],
                reverse=True,
            )
        )
        lines.append(f"- by extension: {ext_summary}")
    for row in file_data["files"][:10]:
        lines.append(f"- {row['path']} @ {row['mtime']}")

    return "\n".join(lines)


PROMPT_TEMPLATE = """You are a senior software engineer writing an end-of-day debrief.
Use the activity context to produce exactly 5 concise lines.

Return valid JSON only with these keys:
{
  "built": "...",
  "broke": "...",
  "learned": "...",
  "next": "...",
  "oneliner": "..."
}

Rules:
- Be concrete and reference actual files, commands, or commit messages when available.
- If nothing broke, say that explicitly.
- Keep each value to 1 short sentence.

Context:
{context}
"""


def generate_debrief(model: str, context: str) -> Optional[dict]:
    """Call Ollama and parse strict JSON debrief response."""
    if not HAS_OLLAMA:
        console.print("[red]Ollama Python package is not installed.[/red] Run: pip install ollama")
        return None
    prompt = PROMPT_TEMPLATE.format(context=context)
    try:
        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        content = strip_markdown_fence(response["message"]["content"].strip())
        parsed = json.loads(content)
        needed = {"built", "broke", "learned", "next", "oneliner"}
        if not needed.issubset(parsed.keys()):
            missing = ", ".join(sorted(needed - set(parsed.keys())))
            raise ValueError(f"missing keys: {missing}")
        return parsed
    except Exception as exc:
        console.print(f"[red]Failed to generate debrief:[/red] {exc}")
        return None


def render_debrief(debrief: dict, git_data: dict, shell_data: dict, file_data: dict, since_hours: int, model: str) -> None:
    """Render readable terminal output with rich tables and panels."""
    stats = Table(show_header=True, header_style="bold cyan")
    stats.add_column("Source")
    stats.add_column("Snapshot")
    stats.add_row(
        "Git",
        f"{len(git_data.get('commits', []))} commits on `{git_data.get('branch', 'n/a')}`",
    )
    stats.add_row(
        "Shell",
        f"{shell_data.get('total_commands', 0)} commands, "
        f"{shell_data.get('error_hits', 0)} error hints",
    )
    stats.add_row("Files", f"{file_data.get('total_modified', 0)} modified files")
    stats.add_row("Window", f"Last {since_hours}h")
    stats.add_row("Model", model)

    lines = Table(show_header=False, box=None)
    lines.add_column("Label", style="bold")
    lines.add_column("Debrief")
    lines.add_row("Built", debrief["built"])
    lines.add_row("Broke", debrief["broke"])
    lines.add_row("Learned", debrief["learned"])
    lines.add_row("Next", debrief["next"])
    lines.add_row("One-liner", debrief["oneliner"])

    console.print(Panel.fit("DailyDebrief - Day 13", style="bold green"))
    console.print(stats)
    console.print(Panel(lines, title="5-Line Structured Debrief", border_style="green"))


def maybe_init_test_repo() -> None:
    """Create a tiny local repo when script runs outside any git repository."""
    if not HAS_GITPYTHON:
        return
    try:
        gitpython.Repo(search_parent_directories=True)
        return
    except gitpython.exc.InvalidGitRepositoryError:
        pass

    # Starter fallback: create a tiny local repo if user runs outside git.
    repo = gitpython.Repo.init(Path.cwd())
    readme = Path.cwd() / "README.md"
    if not readme.exists():
        readme.write_text("# DailyDebrief temp repo\n")
    repo.index.add([str(readme)])
    repo.index.commit("chore: initialize temp repo for DailyDebrief")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a 5-line daily engineering debrief from local activity."
    )
    parser.add_argument(
        "--since",
        "-s",
        type=int,
        default=24,
        help="Look back window in hours (default: 24)",
    )
    parser.add_argument(
        "--model",
        "-m",
        default=DEFAULT_MODEL,
        help=f"Ollama model (default: {DEFAULT_MODEL})",
    )
    parser.add_argument("--no-llm", action="store_true", help="Only collect/print data; skip LLM call")
    args = parser.parse_args()

    maybe_init_test_repo()
    since_dt = datetime.now() - timedelta(hours=args.since)

    git_data = collect_git_data(since_dt)
    shell_data = collect_shell_data(since_dt)
    file_data = collect_file_data(since_dt)
    context = build_context(git_data, shell_data, file_data, args.since)

    if args.no_llm:
        console.print_json(json.dumps({"git": git_data, "shell": shell_data, "files": file_data}, indent=2))
        return

    debrief = generate_debrief(args.model, context)
    if not debrief:
        sys.exit(1)
    render_debrief(debrief, git_data, shell_data, file_data, args.since, args.model)


if __name__ == "__main__":
    main()
