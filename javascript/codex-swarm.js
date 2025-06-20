#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');
const inquirer = require('inquirer');
const { Command } = require('commander');
const execAsync = promisify(exec);

const PREDEFINED_TASKS = [
  { name: 'Explain Codebase', value: 'explain this codebase to me' },
  { name: 'Fix Build Errors', value: 'fix any build errors' },
  { name: 'Find Bugs', value: 'are there any bugs in my code' }
];

async function codingTask(taskName, taskDescription) {
  console.log(`Running task: ${taskName} with description: ${taskDescription}`);
  const command = `start cmd /k "codex "${taskDescription}""`;
  try {
    const { stdout } = await execAsync(command, {
      env: { PATH: process.env.PATH }
    });
    return stdout;
  } catch (error) {
    return error.stderr || error.message;
  }
}

async function promptForTask(tasks) {
  const { action } = await inquirer.prompt([
    {
      type: 'list',
      name: 'action',
      message: 'What would you like to do?',
      choices: [
        { name: 'Add Task', value: 'add' },
        { name: 'Delete Task', value: 'delete' },
        { name: 'List Tasks', value: 'list' },
        { name: 'Run Tasks', value: 'run' },
        { name: 'Exit', value: 'exit' }
      ]
    }
  ]);

  if (action === 'add') {
    const { usePredefined } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'usePredefined',
        message: 'Use a predefined prompt?',
        default: false
      }
    ]);
    let taskName, taskDescription;
    if (usePredefined) {
      const { predefined } = await inquirer.prompt([
        {
          type: 'list',
          name: 'predefined',
          message: 'Choose a predefined prompt:',
          choices: PREDEFINED_TASKS
        }
      ]);
      taskName = predefined;
      taskDescription = predefined;
    } else {
      const answers = await inquirer.prompt([
        { type: 'input', name: 'taskName', message: 'Enter task name:' },
        { type: 'input', name: 'taskDescription', message: 'Enter task description:' }
      ]);
      taskName = answers.taskName;
      taskDescription = answers.taskDescription;
    }
    if (taskName && taskDescription) {
      tasks[taskName] = taskDescription;
      console.log(`Task "${taskName}" added.`);
    }
  } else if (action === 'delete') {
    const taskNames = Object.keys(tasks);
    if (taskNames.length === 0) {
      console.log('No tasks to delete.');
    } else {
      const { toDelete } = await inquirer.prompt([
        {
          type: 'list',
          name: 'toDelete',
          message: 'Select a task to delete:',
          choices: taskNames
        }
      ]);
      delete tasks[toDelete];
      console.log(`Task "${toDelete}" deleted.`);
    }
  } else if (action === 'list') {
    if (Object.keys(tasks).length === 0) {
      console.log('No tasks available.');
    } else {
      console.log('Current tasks:');
      for (const [name, desc] of Object.entries(tasks)) {
        console.log(`- ${name}: ${desc}`);
      }
    }
  } else if (action === 'run') {
    return 'run';
  } else if (action === 'exit') {
    return 'exit';
  }
  return null;
}

async function loopTasks(tasks) {
  const responses = {};
  const promises = Object.entries(tasks).map(async ([taskName, taskDescription]) => {
    try {
      const result = await codingTask(taskName, taskDescription);
      responses[taskName] = result;
    } catch (error) {
      responses[taskName] = `Generated an exception: ${error}`;
    }
  });

  await Promise.all(promises);
  return responses;
}

async function main() {
  const program = new Command();
  program.version('1.0.0').description('Codex Swarm Task Runner');

  program
    .command('interactive')
    .description('Start interactive task manager')
    .action(async () => {
      const tasks = {};
      while (true) {
        const result = await promptForTask(tasks);
        if (result === 'run') {
          const responses = await loopTasks(tasks);
          for (const [taskName, response] of Object.entries(responses)) {
            console.log(`Task response for '$N{taskName}': ${response}`);
          }
        } else if (result === 'exit') {
          break;
        }
      }
    });

  program.parse(process.argv);

  if (!process.argv.slice(2).length) {
    program.outputHelp();
  }
}

main();
