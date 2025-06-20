# Codex Swarm

Codex Swarm is an experimental toolkit for launching multiple [OpenAI Codex](https://platform.openai.com/docs) sessions at once.  Both Python and Node.js implementations are provided and each script opens a new command prompt per task so several Codex instances can run concurrently.

## Features

* **Interactive task input** – Both versions prompt you for task names and descriptions.  The JavaScript tool also offers predefined prompts such as "Explain Codebase" and "Find Bugs"【F:javascript/codex-swarm.js†L13-L17】.
* **Concurrent execution** – Tasks are executed simultaneously.  The Python version uses a thread pool to run `npx codex` in parallel【F:python/codex-swarm.py†L85-L101】.
* **Template support** – The Python tool can load templates from a `.swarm` directory when you type `/template` during input【F:python/codex-swarm.py†L47-L77】.
* **Cross‑platform (Windows focus)** – On Windows, each task spawns a separate Command Prompt window using `start cmd /k`【F:python/codex-swarm.py†L16-L24】【F:javascript/codex-swarm.js†L19-L27】.

## Repository Layout

```
.
├── javascript
│   └── codex-swarm.js   # Node.js CLI
├── python
│   └── codex-swarm.py   # Python CLI
└── LICENSE              # MIT license
```

## Requirements

* Python 3.8 or newer for the `python` script.
* Node.js for the `javascript` script with the `inquirer` and `commander` packages installed (e.g. `npm install inquirer commander`).
* Access to `npx codex` in your system PATH.

## Usage

### Python

```bash
python python/codex-swarm.py
```
You will be prompted for a task name and description. Enter `/template` to list available prompt templates from `python/.swarm`.
Terminal type can be use with this python swarm
* gnome-terminal: The default terminal for GNOME desktop environments (e.g., Ubuntu).
* konsole: The default terminal for KDE desktop environments.
* x-terminal-emulator: A generic terminal emulator symlink on Debian-based systems (often points to gnome-terminal, xterm, etc.).
* xterm: A basic, widely available X11 terminal emulator.
* cmd: Windows command Prompt

### Node.js

```bash
node javascript/codex-swarm.js interactive
```
Choose **Add Task** to create tasks or select predefined prompts. When you choose **Run Tasks**, each task spawns a Codex process.

## Example Session

```
Enter task name: BugFix
Enter task description: fix any build errors
```
Multiple command windows will open and execute the given instructions in Codex.

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.
