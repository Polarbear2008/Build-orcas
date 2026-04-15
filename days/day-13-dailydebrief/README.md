# Day 13 - DailyDebrief

DailyDebrief collects activity from your dev day and asks a local Ollama model to generate a structured 5-line debrief:

1. What you built
2. What broke
3. What you learned
4. What is next
5. One-line summary

## Tech Stack

- `ollama`
- `gitpython`
- `pathlib` (stdlib)
- `rich`

## What It Collects

- **Git sensor:** branch, commits, insertions, deletions
- **Shell sensor:** history commands, top commands, error keywords
- **File sensor:** recently modified files and extension breakdown

This follows the "flight data recorder" pipeline:

`data aggregation -> compression -> summarization`

## Setup

```bash
cd /Users/samandar/Documents/buildcored-orcas/days/day-13-dailydebrief
python3 -m venv .venv
source .venv/bin/activate
pip install ollama gitpython rich
ollama pull qwen2.5:3b
```

Start Ollama in a separate terminal:

```bash
ollama serve
```

## Usage

Default (last 24 hours):

```bash
python daily_debrief.py
```

Last 8 hours:

```bash
python daily_debrief.py --since 8
```

Custom model:

```bash
python daily_debrief.py --model llama3
```

No LLM mode (just collected data):

```bash
python daily_debrief.py --no-llm
```

## Shipped Checklist

- [x] Script collects at least 2 data sources (git + shell + files)
- [x] LLM produces a structured debrief (JSON with 5 required fields)
- [x] Output is readable in terminal via `rich`
- [x] README filled in

## Common Fixes

- **No git repo found:** script attempts a tiny starter repo init when run outside a git tree.
- **Shell history appears empty:** script checks both `~/.zsh_history` and `~/.bash_history` (plus `$HISTFILE`).
