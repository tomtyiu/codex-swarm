#!/usr/bin/env python3
import subprocess
import concurrent.futures
import os


if os.name == 'nt':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    
def coding_task(task_name: str, task_description: str) -> str:
    """
    Open a new Command Prompt and run npx codex with the given task description.
    """
    cmd = f'start cmd /k "npx codex "{task_description}""'
    try:
        # Use shell=True to allow 'start' and 'cmd' commands
        subprocess.Popen(cmd, shell=True, env=os.environ)
        return f"Started Command Prompt for task: {task_name}"
    except Exception as e:
        return f"Failed to start Command Prompt: {e}"

def enter_task_input():
    """
    Function to allow the user to input tasks in a loop.
    The loop stops when the user enters an empty input.
    """
    PURPLE = "\033[95m"
    
    RESET = "\033[0m"
    tasks = {}
    swarm_dir = os.path.join(os.path.dirname(__file__), '.swarm')
    while True:
        print("======================================")
        print("Welcome to the Codex Swarm Task Input!")
        print("You can enter tasks to be processed by Codex.")
        print("To finish inputting tasks, just press Enter without typing anything.")
        task_name = input(f"{PURPLE}Enter task name: {RESET}")
        if task_name == "":
            print("Input finished.")
            break
        # Prompt for description, allow /template command
        while True:
            prompt = f"{PURPLE}Enter task description (or /template): {RESET}"
            user_input = input(prompt)
            if user_input.strip() == "":
                print("Input finished.")
                return tasks
            if user_input.strip().startswith('/template'):
                parts = user_input.strip().split(maxsplit=1)
                # list templates if no template specified
                if len(parts) == 1:
                    if os.path.isdir(swarm_dir):
                        print("Available templates:")
                        for name in sorted(os.listdir(swarm_dir)):
                            print(f"  {name}")
                    else:
                        print("No templates directory found.")
                        continue
                    choice = input(f"{PURPLE}Select template name: {RESET}").strip()
                else:
                    choice = parts[1].strip()
                template_path = os.path.join(swarm_dir, choice, 'PROMPT.txt')
                try:
                    with open(template_path, 'r') as f:
                        task_description = f.read()
                    print(f"Using template '{choice}':")
                    print(task_description)
                    break
                except Exception as e:
                    print(f"Error loading template '{choice}': {e}")
                    continue
            else:
                task_description = user_input
                break
        tasks[task_name] = task_description

    return tasks

def loop_tasks(tasks):
    """
    Function to loop through the tasks and execute them simultaneously.
    """
    responses = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_task = {
            executor.submit(coding_task, task_name, task_description): task_name
            for task_name, task_description in tasks.items()
        }
        for future in concurrent.futures.as_completed(future_to_task):
            task_name = future_to_task[future]
            try:
                responses[task_name] = future.result()
            except Exception as exc:
                responses[task_name] = f"Generated an exception: {exc}"
    return responses

# Example usage:
if __name__ == "__main__":
    tasks = enter_task_input()
    responses = loop_tasks(tasks)
    for task_name, response in responses.items():
        print(f"Task response for '{task_name}': {response}")