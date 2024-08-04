# timer_view.py

import json
import os
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk

from plyer import notification

from timer_states import TimerState


class TimerView:
    def __init__(self, parent, images, update_callback):
        self.parent = parent
        self.images = images
        self.update_callback = update_callback

        # Variables
        self.focus_time = tk.IntVar(value=25)
        self.break_time = tk.IntVar(value=5)
        self.time_remaining = tk.StringVar()
        self.activity_label = tk.StringVar(value="Study")
        self.notified = False
        self.in_focus_mode = True  # Boolean to track if in focus mode
        self.start_time = None
        self.end_time = None
        self.elapsed_time = self.focus_time.get() * 60
        self.data_file = "productivity_data.json"
        self.state = TimerState.START

        # Initialize the frame
        self.frame = ttk.Frame(self.parent)
        self.create_timer_view()

    def create_timer_view(self):
        """Create the timer view with timer display and controls."""
        time_display = ttk.Label(self.frame, textvariable=self.time_remaining, font=("Helvetica", 48))
        time_display.pack(pady=20)

        controls_frame = ttk.Frame(self.frame)
        controls_frame.pack(pady=20)

        ttk.Label(controls_frame, text="Focus Time (min):").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(controls_frame, textvariable=self.focus_time).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(controls_frame, text="Break Time (min):").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(controls_frame, textvariable=self.break_time).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(controls_frame, text="Activity Label:").grid(row=2, column=0, padx=5, pady=5)
        ttk.Entry(controls_frame, textvariable=self.activity_label).grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(controls_frame, text="Start", command=self.start_timer).grid(row=3, column=0, padx=5, pady=5)
        self.pause_button = ttk.Button(controls_frame, text="Pause", command=self.pause_timer,
                                       image=self.images['pause'], compound=tk.LEFT)
        self.pause_button.grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(controls_frame, text="Reset", command=self.reset_timer).grid(row=3, column=2, padx=5, pady=5)

        self.toggle_button = ttk.Button(controls_frame, text="Switch to Break", command=self.toggle_timer)
        self.toggle_button.grid(row=4, column=0, padx=5, pady=5)

        self.update_time_display()

    def update_time_display(self):
        """Update the timer display with the current remaining time."""
        minutes, seconds = divmod(abs(self.elapsed_time), 60)
        sign = "-" if self.elapsed_time < 0 else ""
        self.time_remaining.set(f"{sign}{minutes:02}:{seconds:02}")

    """Update the timer countdown."""
    def update_timer(self):
        if self.state == TimerState.RUNNING:
            now = datetime.now()
            self.elapsed_time = int((self.end_time - now).total_seconds())

            if self.elapsed_time <= 0 and not self.notified:
                self.notify_time_up()

            self.update_time_display()
            self.parent.after(1000, self.update_timer)

    def start_timer(self):
        if self.state == TimerState.START:
            self.state = TimerState.RUNNING
            self.start_time = datetime.now()
            self.end_time = self.start_time + timedelta(
                minutes=self.focus_time.get() if self.in_focus_mode else self.break_time.get())
            self.update_timer()

    """Pause or resume the timer."""
    def pause_timer(self):
        if self.state == TimerState.RUNNING:
            self.state = TimerState.PAUSED
            self.pause_button.config(text="Resume", image=self.images['play'])
            self.elapsed_time = int((self.end_time - datetime.now()).total_seconds())
        elif self.state == TimerState.PAUSED:
            self.state = TimerState.RUNNING
            self.start_time = datetime.now()
            self.end_time = self.start_time + timedelta(seconds=self.elapsed_time)
            self.pause_button.config(text="Pause", image=self.images['pause'])
            self.update_timer()

    """Reset the timer."""
    def reset_timer(self):
        if self.state != TimerState.START:
            self.save_session()

        self.state = TimerState.START
        self.notified = False
        self.pause_button.config(text="Pause", image=self.images['pause'])
        self.elapsed_time = self.focus_time.get() * 60 if self.in_focus_mode else self.break_time.get() * 60
        self.update_time_display()

    """Notify the user when the timer is up."""
    def notify_time_up(self):
        notification.notify(
            title='Productivity Tracker',
            message='Focus time is up!',
            timeout=10
        )
        self.notified = True

    """Toggle between focus and break modes."""
    def toggle_timer(self):
        if self.state == TimerState.RUNNING:
            self.save_session()
        self.state = TimerState.START
        self.pause_button.config(text="Pause", image=self.images['pause'])

        self.in_focus_mode = not self.in_focus_mode

        if self.in_focus_mode:
            self.toggle_button.config(text="Switch to Break")
            self.elapsed_time = self.focus_time.get() * 60
        else:
            self.toggle_button.config(text="Switch to Focus")
            self.elapsed_time = self.break_time.get() * 60

        self.update_time_display()

    def save_session(self):
        if not self.in_focus_mode or self.start_time is None:
            return  # Do not save break sessions

        duration_minutes = (self.focus_time.get() * 60 - self.elapsed_time) // 60
        if duration_minutes == 0:
            return

        session_data = {
            "activity_label": self.activity_label.get(),
            "focus_duration": duration_minutes,
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
                session["focus_duration"] += duration_minutes
                break
        else:
            data[date_str].append(session_data)

        with open(self.data_file, 'w') as file:
            json.dump(data, file, indent=1)
