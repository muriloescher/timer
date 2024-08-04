# main.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from timer_view import TimerView
from heatmap_view import HeatmapView


class ProductivityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Productivity Tracker")

        # Load images
        self.images = {
            'play': ImageTk.PhotoImage(Image.open("images/play.png").resize((15, 15),
                                                                            Image.Resampling.LANCZOS)),
            'pause': ImageTk.PhotoImage(Image.open("images/pause.png").resize((15, 15), Image.Resampling.LANCZOS)),
            'calendar': ImageTk.PhotoImage(
                Image.open("images/calendar.png").resize((20, 20), Image.Resampling.LANCZOS)),
            'timer': ImageTk.PhotoImage(Image.open("images/timer.png").resize((20, 20), Image.Resampling.LANCZOS)),
        }

        # Initialize frames
        self.timer_view = TimerView(self.root, self.images, self.show_frame)
        self.heatmap_view = HeatmapView(self.root)

        # Button to toggle views
        self.view_toggle_button = ttk.Button(self.root, image=self.images['calendar'], command=self.toggle_view)
        self.view_toggle_button.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)

        # Show Timer Frame by default
        self.show_frame(self.timer_view.frame)

    def toggle_view(self):
        """Toggle between the timer and heatmap views."""
        if self.timer_view.frame.winfo_ismapped():
            self.show_frame(self.heatmap_view.frame)
            self.view_toggle_button.config(image=self.images['timer'])
        else:
            self.show_frame(self.timer_view.frame)
            self.view_toggle_button.config(image=self.images['calendar'])

    def show_frame(self, frame):
        """Show the specified frame."""
        self.timer_view.frame.pack_forget()
        self.heatmap_view.frame.pack_forget()
        frame.pack(expand=True, fill='both')


if __name__ == "__main__":
    root = tk.Tk()
    app = ProductivityApp(root)
    root.mainloop()
