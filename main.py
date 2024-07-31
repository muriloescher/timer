import tkinter as tk
from tkinter import ttk
import time
from datetime import datetime, timedelta
import json
import os
from plyer import notification


class ProductivityApp:
    def __init__(self, root):
        self.data = None
        self.root = root
        self.root.title("Productivity Tracker")

        # Variables
        self.focus_time = tk.IntVar(value=25)
        self.break_time = tk.IntVar(value=5)
        self.time_remaining = tk.StringVar()
        self.activity_label = tk.StringVar(value="Study")
        self.timer_running = False
        self.notified = False
        self.start_time = None
        self.end_time = None
        self.elapsed_time = self.focus_time.get() * 60
        self.data_file = "productivity_data.json"

        # Timer Display
        self.time_display = ttk.Label(root, textvariable=self.time_remaining, font=("Helvetica", 48))
        self.time_display.pack(pady=20)

        # Controls
        controls_frame = ttk.Frame(root)
        controls_frame.pack(pady=20)

        ttk.Label(controls_frame, text="Focus Time (min):").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(controls_frame, textvariable=self.focus_time).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(controls_frame, text="Break Time (min):").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(controls_frame, textvariable=self.break_time).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(controls_frame, text="Activity Label:").grid(row=2, column=0, padx=5, pady=5)
        ttk.Entry(controls_frame, textvariable=self.activity_label).grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(controls_frame, text="Start", command=self.start_timer).grid(row=3, column=0, padx=5, pady=5)
        self.pause_button = ttk.Button(controls_frame, text="Pause", command=self.pause_timer)
        self.pause_button.grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(controls_frame, text="Reset", command=self.reset_timer).grid(row=3, column=2, padx=5, pady=5)

        self.toggle_button = ttk.Button(controls_frame, text="Switch to Break", command=self.toggle_timer)
        self.toggle_button.grid(row=4, column=0, padx=5, pady=5)

        # Load Data
        self.load_data()

        # Initial Display
        self.update_time_display()

    def update_time_display(self):
        minutes, seconds = divmod(abs(self.elapsed_time), 60)
        sign = "-" if self.elapsed_time < 0 else ""
        self.time_remaining.set(f"{sign}{minutes:02}:{seconds:02}")

    def update_timer(self):
        if self.timer_running:
            now = datetime.now()
            previous_elapsed_time = self.elapsed_time
            self.elapsed_time = int((self.end_time - now).total_seconds())
            if previous_elapsed_time > 0 >= self.elapsed_time:
                self.notify_time_up()
            self.update_time_display()
            self.root.after(1000, self.update_timer)

    def start_timer(self):
        if not self.timer_running:
            self.start_time = datetime.now()
            self.end_time = self.start_time + timedelta(minutes=self.focus_time.get() if
            self.toggle_button['text'] == "Switch to Break" else self.break_time.get())
            self.timer_running = True
            self.notified = False
            self.update_timer()

    def pause_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.pause_button.config(text="Resume")
            elapsed_time = datetime.now() - self.start_time
            self.elapsed_time = int(elapsed_time.total_seconds())
        else:
            self.timer_running = True
            self.start_time = datetime.now() - timedelta(seconds=self.elapsed_time)
            self.end_time = datetime.now() + timedelta(seconds=(self.focus_time.get() * 60) -
                                                               self.elapsed_time)
            self.pause_button.config(text="Pause")
            self.update_timer()

    def reset_timer(self):
        if self.toggle_button['text'] == "Switch to Focus":
            self.notified = False
            self.timer_running = False
            self.pause_button.config(text="Pause")
            self.elapsed_time = self.break_time.get() * 60
            self.update_time_display()
            return
        if self.timer_running:
            elapsed_time = datetime.now() - self.start_time
        else:
            elapsed_time = timedelta(seconds=self.elapsed_time)

        self.elapsed_time = int(elapsed_time.total_seconds())
        self.save_session(end=False)

        self.notified = False
        self.timer_running = False
        self.elapsed_time = self.focus_time.get() * 60
        self.pause_button.config(text="Pause")
        self.update_time_display()

    def notify_time_up(self):
        if not hasattr(self, 'notified') or not self.notified:
            notification.notify(
                title='Productivity Tracker',
                message='Focus time is up!',
                timeout=10
            )
            self.notified = True

    def toggle_timer(self):
        if self.timer_running:
            return
        if self.toggle_button['text'] == "Switch to Break":
            self.toggle_button.config(text="Switch to Focus")
            self.reset_timer()
            self.elapsed_time = self.break_time.get() * 60
        else:
            self.toggle_button.config(text="Switch to Break")
            self.reset_timer()
            self.elapsed_time = self.focus_time.get() * 60
        self.update_time_display()

    def save_session(self, end):
        if self.toggle_button['text'] == "Switch to Focus":
            return
        if end:
            duration_seconds = self.focus_time.get() * 60
        else:
            elapsed_time = (datetime.now() - self.start_time).total_seconds()
            duration_seconds = elapsed_time + 0 if elapsed_time > 0 else self.focus_time.get()

        duration_minutes = int(duration_seconds // 60)

        # Adjust duration if the time is negative
        if self.elapsed_time < 0:
            negative_minutes = int(abs(self.elapsed_time) // 60 + 1)
            duration_minutes += negative_minutes

        if duration_minutes == 0:
            return

        session_data = {
            "activity_label": self.activity_label.get(),
            "focus_duration": duration_minutes,
            # "break_duration": self.break_time.get()
        }
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as file:
                data = json.load(file)
        else:
            data = {}
        date_str = datetime.now().strftime("%d.%m.%Y")
        if date_str not in data:
            data[date_str] = []

        for session in data[date_str]:
            if session["activity_label"] == self.activity_label.get():
                session["focus_duration"] += self.focus_time.get()
                # session["break_duration"] += self.break_time.get()
                break
        else:
            data[date_str].append(session_data)

        with open(self.data_file, 'w') as file:
            json.dump(data, file)

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as file:
                self.data = json.load(file)
        else:
            self.data = {}


if __name__ == "__main__":
    root = tk.Tk()
    app = ProductivityApp(root)
    root.mainloop()
