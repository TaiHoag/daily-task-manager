# Daily Task Manager

## Features

- **Create Task:** Allows users to create tasks with a name and optional minimum and maximum time limits.
- **Task Timer:** Start, pause, and resume task timers, with real-time updates displayed on the GUI.
- **Task List:** Displays all tasks with their respective timers and statuses on a canvas.
- **Task Checkmarks:** Automatically marks tasks as complete when the minimum time is reached.
- **Task Removal:** Remove tasks from the list.
- **Daily Reset:** Automatically resets all task times at 2 AM daily.
- **Logging:** Logs all significant actions, such as task creation, removal, and time updates, in a `log.txt` file.
- **Database Integration:** Tasks and their associated data are stored in a database, ensuring data persistence.

## Installation

### Prerequisites

Ensure you have Python installed on your system. You can download it from the [official Python website](https://www.python.org/downloads/).

### Clone the Repository

```
git https://github.com/TaiHoag/daily-task-manager.git
cd daily-task-manager
```

### Install Required Packages

You need to install the necessary Python packages. You can do this using `pip`:

```bash
pip install customtkinter
pip install tk
```

### Database Setup

The application uses a SQLite database to store tasks. The `DatabaseHandler` class is responsible for interacting with the database. Make sure the `database.py` file is in the same directory as your main application file.

### Running the Application

Once all the dependencies are installed, you can run the application by executing:

```
python main.py
```

Make sure the `icon.ico` file is present in the same directory as your `main.py` file to set the application icon.

## Usage

### Adding a Task

1. Click the "Add Task" button.
2. In the new window, enter the task name.
3. Optionally, specify the minimum and maximum time (in minutes) for the task. You can also select the "No Timer" option if you don't want to set any time limits.
4. Click "Save Task" to add the task to the list.

### Removing a Task

1. Select the task you want to remove by clicking on its name in the task list.
2. Click the "Remove Task" button to delete the task.

### Starting a Task

1. Click the "▶" button next to the task you want to start.
2. The timer window will appear, showing the elapsed time.
3. Use the "Pause" button to pause the timer or the "Add 1 Min" and "Remove 1 Min" buttons to adjust the time.

### Automatic Daily Reset

- All task times are reset at 2 AM daily. This action is logged in the `log.txt` file.

## Logging

All actions performed in the application, such as task creation, removal, timer updates, and daily resets, are logged in a `log.txt` file located in the application's directory. This file is useful for debugging and tracking usage patterns.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. If you find any bugs or have suggestions for new features, feel free to open an issue.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
