import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import time
import os
import datetime
import threading
import logging
from database import DatabaseHandler

# Configure logging
logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Task Manager")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Set program icon
        self.root.iconbitmap("icon.ico")

        self.tasks = []
        self.task_times = {}
        self.task_checkmarks = {}
        self.task_elapsed_times = {}
        self.task_widgets = {}
        self.timer_running = False
        self.paused = False
        self.elapsed_time = 0

        # Task Canvas
        self.task_canvas = tk.Canvas(root, background="gray14", width=800, height=600)
        self.task_canvas.pack(pady=10)

        # Buttons Frame
        button_frame = ctk.CTkFrame(root)
        button_frame.pack(pady=10)

        # Add Task Button
        self.add_task_button = ctk.CTkButton(
            button_frame,
            text="Add Task",
            command=self.open_task_window,
            font=("Helvetica", 16),
        )
        self.add_task_button.grid(row=0, column=0, padx=10)

        # Remove Task Button
        self.remove_task_button = ctk.CTkButton(
            button_frame,
            text="Remove Task",
            command=self.remove_task,
            font=("Helvetica", 16),
        )
        self.remove_task_button.grid(row=0, column=1, padx=10)

        # Status Bar
        self.status_bar = ctk.CTkLabel(
            root, text="No task running", anchor="w", font=("Helvetica", 12)
        )
        self.status_bar.pack(fill="x", side="bottom", ipady=2)

        # Selected Task Tracking
        self.selected_task = None

        # Initialize database handler
        self.db = DatabaseHandler()

        # Log initialization
        logging.info("Initialized Task Manager Application")

        # Load tasks from database
        self.load_tasks_from_db()

        # Schedule daily reset
        self.schedule_daily_reset()

    def open_task_window(self):
        self.task_window = ctk.CTkToplevel(self.root)
        self.task_window.title("Create Task")
        self.task_window.grab_set()
        self.task_window.transient(self.root)

        # Task Name Entry
        self.task_name_label = ctk.CTkLabel(
            self.task_window, text="Task Name:", font=("Helvetica", 16)
        )
        self.task_name_label.pack(pady=5)
        self.task_name_entry = ctk.CTkEntry(self.task_window, font=("Helvetica", 16))
        self.task_name_entry.pack(pady=5)

        # Minimum Time Entry
        self.min_time_label = ctk.CTkLabel(
            self.task_window, text="Minimum Time (minutes):", font=("Helvetica", 16)
        )
        self.min_time_label.pack(pady=5)
        self.min_time_entry = ctk.CTkEntry(self.task_window, font=("Helvetica", 16))
        self.min_time_entry.pack(pady=5)

        # Maximum Time Entry
        self.max_time_label = ctk.CTkLabel(
            self.task_window, text="Maximum Time (minutes):", font=("Helvetica", 16)
        )
        self.max_time_label.pack(pady=5)
        self.max_time_entry = ctk.CTkEntry(self.task_window, font=("Helvetica", 16))
        self.max_time_entry.pack(pady=5)

        # No Timer Checkbox
        self.no_timer_var = tk.BooleanVar()
        self.no_timer_checkbox = ctk.CTkCheckBox(
            self.task_window,
            text="No Timer",
            variable=self.no_timer_var,
            font=("Helvetica", 16),
            command=self.toggle_timer_entries,
        )
        self.no_timer_checkbox.pack(pady=10)

        # Save Task Button
        self.save_task_button = ctk.CTkButton(
            self.task_window,
            text="Save Task",
            command=self.save_task,
            font=("Helvetica", 16),
        )
        self.save_task_button.pack(pady=10)

    def toggle_timer_entries(self):
        state = "disabled" if self.no_timer_var.get() else "normal"
        self.min_time_entry.configure(state=state)
        self.max_time_entry.configure(state=state)

    def save_task(self):
        task_name = self.task_name_entry.get()
        if not task_name:
            messagebox.showwarning("Input Error", "Task name cannot be empty.")
            return

        if self.no_timer_var.get():
            min_time = None
            max_time = None
        else:
            try:
                min_time = (
                    int(self.min_time_entry.get()) * 60
                    if self.min_time_entry.get()
                    else None
                )
                max_time = (
                    int(self.max_time_entry.get()) * 60
                    if self.max_time_entry.get()
                    else None
                )
            except ValueError:
                messagebox.showwarning(
                    "Input Error", "Please enter valid numbers for the timer settings."
                )
                return

        self.tasks.append(task_name)
        self.task_times[task_name] = {
            "min": min_time,
            "max": max_time,
            "no_timer": self.no_timer_var.get(),
        }
        self.task_checkmarks[task_name] = False
        self.task_elapsed_times[task_name] = 0

        display_time = self.format_time(0)
        self.add_task_to_canvas(task_name, display_time)

        self.task_window.destroy()

        # Log the task creation
        logging.info(
            f"Task '{task_name}' created with min_time={min_time} and max_time={max_time}."
        )

        # Save task to the database
        self.db.add_task(task_name, min_time, max_time)

    def remove_task(self):
        if not self.selected_task:
            messagebox.showwarning("Remove Task", "Please select a task to remove.")
            return

        task_name = self.selected_task
        task_id = self.get_task_id(task_name)

        if task_id is None:
            messagebox.showerror("Error", "Task ID not found. Cannot remove task.")
            return

        # Remove the task from canvas and internal data structures
        self.task_canvas.delete(self.task_widgets[task_name][0])
        self.task_canvas.delete(self.task_widgets[task_name][1])

        self.tasks.remove(task_name)
        del self.task_times[task_name]
        del self.task_checkmarks[task_name]
        del self.task_elapsed_times[task_name]
        del self.task_widgets[task_name]

        self.selected_task = None
        self.rearrange_canvas()

        # Log the task removal with the correct task ID
        logging.info(f"Removing task '{task_name}' with id={task_id}.")

        # Remove task from the database
        self.db.remove_task(task_id)

    def rearrange_canvas(self):
        """Rearrange the canvas items after removing a task to avoid gaps."""
        for idx, task_name in enumerate(self.tasks):
            y_position = 20 + idx * 30
            play_button, task_text = self.task_widgets[task_name]

            self.task_canvas.coords(play_button, 20, y_position)
            self.task_canvas.coords(task_text, 50, y_position)

    def add_task_to_canvas(self, task_name, display_time):
        y_position = 20 + (len(self.tasks) - 1) * 30
        play_button = self.task_canvas.create_text(
            20,
            y_position,
            text="▶",
            fill="snow",
            font=("Helvetica", 20),
            tags=(task_name, "play"),
        )
        task_text = self.task_canvas.create_text(
            50,
            y_position,
            text=f"{task_name} - {display_time}",
            fill="steelblue",
            anchor="w",
            font=("Helvetica", 16),
            tags=(task_name, "text"),
        )

        self.task_widgets[task_name] = (play_button, task_text)

        self.task_canvas.tag_bind(
            play_button,
            "<Button-1>",
            lambda event, t_name=task_name: self.start_task(t_name),
        )
        self.task_canvas.tag_bind(
            task_text,
            "<Button-1>",
            lambda event, t_name=task_name: self.select_task(t_name),
        )

    def select_task(self, task_name):
        if self.selected_task:
            _, old_task_text = self.task_widgets[self.selected_task]
            self.task_canvas.itemconfig(old_task_text, font=("Helvetica", 16))

        self.selected_task = task_name
        _, task_text = self.task_widgets[task_name]
        self.task_canvas.itemconfig(task_text, font=("Helvetica", 16, "bold"))

    def start_task(self, task_name):
        if self.timer_running:
            messagebox.showwarning(
                "Timer Running",
                "Another task is already running. Please wait until it finishes.",
            )
            return

        self.timer_running = True

        self.paused = False
        self.elapsed_time = self.task_elapsed_times[task_name]

        # Hide main window and open timer window

        self.root.withdraw()
        self.timer_window = ctk.CTkToplevel(self.root)
        self.timer_window.title(f"Timer - {task_name}")
        self.timer_label = ctk.CTkLabel(
            self.timer_window,
            text=self.format_time(self.elapsed_time),
            font=("Helvetica", 24),
        )
        self.root.iconbitmap("icon.ico")
        self.timer_label.pack(pady=20)

        # Pause/Resume Button

        self.pause_button = ctk.CTkButton(
            self.timer_window,
            text="Pause",
            command=self.toggle_pause,
            font=("Helvetica", 16),
        )
        self.pause_button.pack(pady=5)

        # Add/Remove Time Buttons
        time_adjust_frame = ctk.CTkFrame(self.timer_window)
        time_adjust_frame.pack(pady=5)

        self.add_time_button = ctk.CTkButton(
            time_adjust_frame,
            text="Add 1 Min",
            command=self.add_time,
            font=("Helvetica", 16),
        )
        self.add_time_button.grid(row=0, column=0, padx=5)

        self.remove_time_button = ctk.CTkButton(
            time_adjust_frame,
            text="Remove 1 Min",
            command=self.remove_time,
            font=("Helvetica", 16),
        )
        self.remove_time_button.grid(row=0, column=1, padx=5)

        threading.Thread(target=self.run_timer, args=(task_name,)).start()
        self.timer_window.protocol("WM_DELETE_WINDOW", self.on_timer_window_close)

        # Update database on task start/stop
        task_id = self.get_task_id(task_name)
        self.db.update_task(task_id, self.elapsed_time, self.task_checkmarks[task_name])

    def get_task_id(self, task_name):
        # Retrieve task ID from the database based on task name
        tasks = self.db.get_tasks()

        for task in tasks:
            if task[1] == task_name:
                return task[0]
        return None

    def load_tasks_from_db(self):
        tasks = self.db.get_tasks()
        for task in tasks:
            task_id, name, min_time, max_time, elapsed_time, checkmark = task

            # Add task to internal structures
            self.tasks.append(name)
            self.task_times[name] = {"min": min_time, "max": max_time}
            self.task_checkmarks[name] = bool(checkmark)
            self.task_elapsed_times[name] = elapsed_time

            # Format time for display
            display_time = self.format_time(elapsed_time)
            self.add_task_to_canvas(name, display_time)

            # Update task display with current status
            self.update_task_time_in_canvas(name)

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.configure(text="Resume" if self.paused else "Pause")
        self.status_bar.configure(text="Paused" if self.paused else "Running...")

    def add_time(self):
        self.elapsed_time += 60

        self.timer_label.configure(text=self.format_time(self.elapsed_time))

    def remove_time(self):
        if self.elapsed_time >= 60:
            self.elapsed_time -= 60
        else:
            self.elapsed_time = 0
        self.timer_label.configure(text=self.format_time(self.elapsed_time))

    def run_timer(self, task_name):
        timing = self.task_times[task_name]
        min_time = timing.get("min")
        max_time = timing.get("max")

        self.status_bar.configure(text=f"Running: {task_name}")

        while self.timer_running:
            if self.paused:
                time.sleep(1)
                continue

            self.elapsed_time += 1
            self.task_elapsed_times[task_name] = self.elapsed_time
            self.update_task_time_in_canvas(task_name)
            self.timer_label.configure(text=self.format_time(self.elapsed_time))
            time.sleep(1)

            # Update database with the latest elapsed time and checkmark
            task_id = self.get_task_id(task_name)
            self.db.update_task(
                task_id, self.elapsed_time, self.task_checkmarks[task_name]
            )

            # Check for minimum time
            if (
                not self.task_checkmarks[task_name]
                and min_time is not None
                and self.elapsed_time >= min_time
            ):
                self.task_checkmarks[task_name] = True
                self.update_task_time_in_canvas(task_name, status="✔️")

                # Log the update
                logging.info(
                    f"Task '{task_name}' min_time={min_time} reached, set checkmark={self.task_checkmarks[task_name]}."
                )

            # Check for maximum time
            if max_time is not None and self.elapsed_time >= max_time:
                self.timer_running = False
                messagebox.showwarning(
                    "Time's Up", f"Maximum time reached for task: {task_name}!"
                )
                time.sleep(1)
                self.on_timer_window_close()

                # Log the update
                logging.info(f"Task '{task_name}' max_time={max_time} reached.")
                break

    def format_time(self, total_seconds):
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def update_task_time_in_canvas(self, task_name, status=""):
        _, task_text = self.task_widgets[task_name]
        elapsed_time = self.format_time(self.task_elapsed_times[task_name])

        # Display checkmark if the minimum time is met
        checkmark = "✔️" if self.task_checkmarks[task_name] else ""

        # Update display with min/max times
        timing = self.task_times[task_name]
        min_time = f"Min: {timing['min'] // 60} min" if timing["min"] else ""
        max_time = f"Max: {timing['max'] // 60} min" if timing["max"] else ""

        display_text = f"{task_name} - {checkmark} {status} (Total Time: {elapsed_time}) {min_time} {max_time}"
        self.task_canvas.itemconfig(task_text, text=display_text)

    def on_timer_window_close(self):
        self.timer_running = False
        self.timer_window.destroy()
        self.root.deiconify()
        self.status_bar.configure(text="No task running")

    def reset_task_times(self):
        for task_name in self.tasks:
            self.task_elapsed_times[task_name] = 0
            self.update_task_time_in_canvas(task_name)
            # Log the reset
            logging.info(f"Task '{task_name}' time reset at 2 AM.")

    def schedule_daily_reset(self):
        now = datetime.datetime.now()
        reset_time = now.replace(hour=2, minute=0, second=0, microsecond=0)

        # If the time now is after 2 AM, schedule for the next day
        if now >= reset_time:
            reset_time += datetime.timedelta(days=1)

        delay = (reset_time - now).total_seconds()
        threading.Timer(delay, self.perform_daily_reset).start()

    def perform_daily_reset(self):
        self.reset_task_times()
        self.schedule_daily_reset()  # Reschedule for the next day


if __name__ == "__main__":
    root = ctk.CTk()
    app = TaskManagerApp(root)
    root.mainloop()
