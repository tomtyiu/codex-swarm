#!/usr/bin/env python3
# version 1.0
# Author: Thomas Yiu
# Code type: Python
# This is codex swarm, AI agent that will control different codex independtly.  This is alpha code from me. Use AI to code
#!/usr/bin/env python3
"""
Interactive tool for spawning Codex workers for a set of tasks.
"""

import os
import sys
import shutil
import subprocess
import concurrent.futures
import argparse
from pathlib import Path

# ANSI colors
PURPLE = "\033[95m"
RESET = "\033[0m"

# Directory containing template subfolders under .swarm
SWARM_DIR = Path(__file__).parent / ".swarm"


def enable_windows_ansi_colors() -> None:
    """Enable ANSI escape sequence processing on Windows."""
    if os.name == "nt":
        try:
            import ctypes

            handle = ctypes.windll.kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint()
            if ctypes.windll.kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                ctypes.windll.kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass


def list_templates() -> None:
    """Print available templates in the .swarm directory."""
    if not SWARM_DIR.is_dir():
        print("No .swarm directory found.")
        return
    print("Available templates:")
    for sub in sorted(SWARM_DIR.iterdir()):
        if sub.is_dir():
            print(f"  {sub.name}")


def prompt_task_description() -> str:
    """Prompt the user for a task description or choose a template."""
    while True:
        entry = input(f"{PURPLE}Description (or /template): {RESET}").strip()
        if not entry:
            return ""
        if entry.startswith("/template"):
            parts = entry.split(maxsplit=1)
            if len(parts) == 1:
                list_templates()
                choice = input(f"{PURPLE}Select template: {RESET}").strip()
            else:
                choice = parts[1].strip()
            template_file = SWARM_DIR / choice / "PROMPT.txt"
            try:
                return template_file.read_text()
            except Exception as e:
                print(f"Error loading template '{choice}': {e}")
                continue
        return entry


def prompt_tasks() -> dict[str, str]:
    """Prompt the user to enter multiple named tasks."""
    tasks: dict[str, str] = {}
    print("Welcome to the Codex Swarm Task Manager!")
    print("You can enter multiple tasks with names and descriptions.")
    print("Type '/template' to select a template for the task description.")
    print("Press Enter without typing anything to finish entering tasks.")
    while True:
        
        print("\n" + "=" * 40)
        name = input(f"{PURPLE}Task name (empty to finish): {RESET}").strip()
        if not name:
            break
        description = prompt_task_description()
        if not description:
            print("Empty description, skipping task.")
            continue
        tasks[name] = description
    return tasks


def start_task_process(name: str, description: str) -> str:
    """Launch a new terminal window running `npx codex` with the given description."""
    if os.name == "nt":
        # Use start to keep the window open after execution
        cmd = f'start cmd /k "npx codex "{description}""'
        subprocess.Popen(cmd, shell=True, env=os.environ)
    else:
        # Try common terminals
        for term in ("gnome-terminal", "konsole", "x-terminal-emulator", "xterm"):
            if shutil.which(term):
                subprocess.Popen([term, "-e", f"npx codex {description}"])
                break
        else:
            print(f"No supported terminal found for task: {name}")
    return name


def run_tasks(tasks: dict[str, str], max_workers: int) -> dict[str, str]:
    """Submit tasks to a ThreadPoolExecutor and collect their results."""
    results: dict[str, str] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(start_task_process, n, d): n for n, d in tasks.items()}
        for fut in concurrent.futures.as_completed(future_map):
            name = future_map[fut]
            try:
                fut.result()
                results[name] = "started"
            except Exception as e:
                results[name] = f"failed: {e}"
    return results


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Launch Codex swarm tasks")
    parser.add_argument(
        "-j", "--max-workers", type=int, default=4,
        help="number of parallel tasks to run"
    )
    return parser.parse_args()


def main() -> None:
    enable_windows_ansi_colors()
    args = parse_args()
    tasks = prompt_tasks()
    if not tasks:
        print("No tasks to run. Exiting.")
        return
    results = run_tasks(tasks, args.max_workers)
    print("\nTask results:")
    for name, status in results.items():
        print(f"  {name}: {status}")


if __name__ == "__main__":
    main()

