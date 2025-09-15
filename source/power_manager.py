import customtkinter as ctk
import subprocess
import threading
import time
import platform
from tkinter import messagebox

# -------------------- MAIN WINDOW --------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Power Utility")
root.geometry("340x220")
root.resizable(False, False)

# -------------------- COLORS & FONTS --------------------
BG_COLOR = "#0A0A0A"  # Dark background for neon contrast
TEXT_COLOR = "#FFFFFF"  # Pure white for maximum visibility
NEON_YELLOW = "#FFFF00"  # Neon yellow for timer labels and countdown
NEON_MAGENTA = "#FF00FF"  # Neon magenta for shutdown/cancelled states
NEON_PINK = "#FF2E63"  # Neon pink for shutdown
NEON_GREEN = "#00FF9F"  # Neon green for timer
NEON_BLUE = "#00D1FF"  # Neon blue for sleep
NEON_ORANGE = "#FF9500"  # Neon orange for restart
NEON_PURPLE = "#D600FF"  # Neon purple for hibernate

BTN_COLORS = {
    "Shutdown": NEON_PINK,
    "Restart": NEON_ORANGE,
    "Hibernate": NEON_PURPLE,
    "Sleep": NEON_BLUE,
    "Timer": NEON_GREEN
}

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_BUTTON = ("Segoe UI", 12, "bold")
FONT_LABEL = ("Segoe UI", 12, "bold")
FONT_COUNTDOWN = ("Segoe UI", 18, "bold")

# -------------------- GLOBALS --------------------
timer_running = False
timer_thread = None

# -------------------- COMMAND EXECUTION --------------------
def run_command(command, confirm=False):
    if confirm:
        if not messagebox.askyesno("Confirm", "Proceed with action?", parent=root):
            return
    try:
        subprocess.run(command, check=True, shell=True, stderr=subprocess.PIPE, text=True)
        root.destroy()
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed: {e.stderr}\nRun as administrator.", parent=root)

# -------------------- ACTIONS --------------------
def shutdown_now():
    cmd = "shutdown /s /t 0" if platform.system() == "Windows" else "sudo shutdown -h now"
    run_command(cmd, confirm=True)

def restart_now():
    cmd = "shutdown /r /t 0" if platform.system() == "Windows" else "sudo shutdown -r now"
    run_command(cmd, confirm=True)

def hibernate_now():
    cmd = "shutdown /h" if platform.system() == "Windows" else "sudo systemctl hibernate"
    run_command(cmd, confirm=True)

def sleep_now():
    cmd = "rundll32.exe powrprof.dll,SetSuspendState 0,1,0" if platform.system() == "Windows" else "systemctl suspend"
    run_command(cmd, confirm=True)

def direct_shutdown():
    cmd = "shutdown /s /t 0" if platform.system() == "Windows" else "sudo shutdown -h now"
    run_command(cmd, confirm=False)

# -------------------- TIMER LOGIC --------------------
def start_countdown(total_seconds):
    global timer_running
    timer_running = True
    cancel_btn.configure(state="normal")
    start_timer_btn.configure(state="disabled")
    toggle_timer_btn.configure(state="disabled")

    while total_seconds > 0 and timer_running:
        mins, secs = divmod(total_seconds, 60)
        hours = mins // 60
        mins = mins % 60
        countdown_label.configure(text=f"{hours:02d}:{mins:02d}:{secs:02d}", text_color=NEON_YELLOW)
        root.update()
        time.sleep(1)
        total_seconds -= 1

    if timer_running:
        countdown_label.configure(text="Shutting down...", text_color=NEON_MAGENTA)
        direct_shutdown()
    else:
        countdown_label.configure(text="Timer Cancelled", text_color=NEON_MAGENTA)

    cancel_btn.configure(state="disabled")
    start_timer_btn.configure(state="normal")
    toggle_timer_btn.configure(state="normal")
    hour_input.delete(0, "end")
    min_input.delete(0, "end")
    sec_input.delete(0, "end")

def set_timer_shutdown():
    global timer_thread
    try:
        h = int(hour_input.get() or 0)
        m = int(min_input.get() or 0)
        s = int(sec_input.get() or 0)
        if h < 0 or m < 0 or s < 0:
            raise ValueError("Negative values are not allowed")
        total_seconds = h * 3600 + m * 60 + s
        if total_seconds <= 0:
            raise ValueError("Enter a valid time")
        if timer_thread and timer_thread.is_alive():
            messagebox.showwarning("Warning", "Timer is already running.", parent=root)
            return
        timer_thread = threading.Thread(target=start_countdown, args=(total_seconds,), daemon=True)
        timer_thread.start()
    except ValueError as e:
        messagebox.showerror("Invalid Input", str(e), parent=root)

def cancel_timer():
    global timer_running
    timer_running = False

def toggle_timer_panel():
    if timer_panel.winfo_ismapped():
        timer_panel.grid_remove()
        root.geometry("340x220")
        toggle_timer_btn.configure(text="Timer")
    else:
        timer_panel.grid()
        root.geometry("340x340")
        toggle_timer_btn.configure(text="Hide Timer")

# -------------------- UI --------------------
root.configure(fg_color=BG_COLOR)
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)

# Title
title_label = ctk.CTkLabel(root, text="🔌 Power Utility", font=FONT_TITLE, text_color=TEXT_COLOR)
title_label.grid(row=0, column=0, pady=6)

# Buttons frame
btn_frame = ctk.CTkFrame(root, fg_color=BG_COLOR, corner_radius=6)
btn_frame.grid(row=1, column=0, padx=6, pady=2, sticky="ew")
btn_frame.grid_columnconfigure((0, 1), weight=1)

btn_shutdown = ctk.CTkButton(btn_frame, text="Shutdown", font=FONT_BUTTON, command=shutdown_now,
                             fg_color=BTN_COLORS["Shutdown"], hover_color="#E61E50", height=30, text_color=TEXT_COLOR)
btn_restart = ctk.CTkButton(btn_frame, text="Restart", font=FONT_BUTTON, command=restart_now,
                            fg_color=BTN_COLORS["Restart"], hover_color="#E68600", height=30, text_color=TEXT_COLOR)
btn_hibernate = ctk.CTkButton(btn_frame, text="Hibernate", font=FONT_BUTTON, command=hibernate_now,
                              fg_color=BTN_COLORS["Hibernate"], hover_color="#BF00E6", height=30, text_color=TEXT_COLOR)
btn_sleep = ctk.CTkButton(btn_frame, text="Sleep", font=FONT_BUTTON, command=sleep_now,
                          fg_color=BTN_COLORS["Sleep"], hover_color="#00B8E6", height=30, text_color=TEXT_COLOR)
toggle_timer_btn = ctk.CTkButton(btn_frame, text="Timer", font=FONT_BUTTON, command=toggle_timer_panel,
                                 fg_color=BTN_COLORS["Timer"], hover_color="#00E68A", height=30, text_color=TEXT_COLOR)

btn_shutdown.grid(row=0, column=0, padx=3, pady=2, sticky="ew")
btn_restart.grid(row=0, column=1, padx=3, pady=2, sticky="ew")
btn_hibernate.grid(row=1, column=0, padx=3, pady=2, sticky="ew")
btn_sleep.grid(row=1, column=1, padx=3, pady=2, sticky="ew")
toggle_timer_btn.grid(row=2, column=0, columnspan=2, padx=3, pady=2, sticky="ew")

# Timer Panel
timer_panel = ctk.CTkFrame(root, fg_color=BG_COLOR, corner_radius=6)
timer_panel.grid(row=2, column=0, padx=6, pady=2, sticky="ew")
timer_panel.grid_columnconfigure((0, 1, 2), weight=1)
timer_panel.grid_remove()

# Timer inputs
ctk.CTkLabel(timer_panel, text="Hours", font=FONT_LABEL, text_color=NEON_YELLOW).grid(row=0, column=0, padx=3, pady=2)
ctk.CTkLabel(timer_panel, text="Minutes", font=FONT_LABEL, text_color=NEON_YELLOW).grid(row=0, column=1, padx=3, pady=2)
ctk.CTkLabel(timer_panel, text="Seconds", font=FONT_LABEL, text_color=NEON_YELLOW).grid(row=0, column=2, padx=3, pady=2)

hour_input = ctk.CTkEntry(timer_panel, width=30, justify="center", fg_color="#2A2A2A", 
                          text_color=TEXT_COLOR, font=FONT_LABEL, border_width=0)
hour_input.grid(row=1, column=0, padx=3, pady=2)
min_input = ctk.CTkEntry(timer_panel, width=30, justify="center", fg_color="#2A2A2A", 
                         text_color=TEXT_COLOR, font=FONT_LABEL, border_width=0)
min_input.grid(row=1, column=1, padx=3, pady=2)
sec_input = ctk.CTkEntry(timer_panel, width=30, justify="center", fg_color="#2A2A2A", 
                         text_color=TEXT_COLOR, font=FONT_LABEL, border_width=0)
sec_input.grid(row=1, column=2, padx=3, pady=2)

# Timer buttons
start_timer_btn = ctk.CTkButton(timer_panel, text="Start", font=FONT_BUTTON, command=set_timer_shutdown,
                                fg_color=BTN_COLORS["Timer"], hover_color="#00E68A", height=30, width=75, text_color=TEXT_COLOR)
cancel_btn = ctk.CTkButton(timer_panel, text="Cancel", font=FONT_BUTTON, command=cancel_timer,
                           fg_color=BTN_COLORS["Shutdown"], hover_color="#E61E50", height=30, width=75, text_color=TEXT_COLOR, state="disabled")
ctk.CTkButton(timer_panel, text="Close", font=FONT_BUTTON, command=toggle_timer_panel,
              fg_color="#2A2A2A", hover_color="#404040", height=30, width=75, text_color=TEXT_COLOR).grid(row=2, column=2, padx=3, pady=2)

start_timer_btn.grid(row=2, column=0, padx=3, pady=2)
cancel_btn.grid(row=2, column=1, padx=3, pady=2)

# Countdown Label
countdown_label = ctk.CTkLabel(timer_panel, text="00:00:00", font=FONT_COUNTDOWN, text_color=NEON_YELLOW)
countdown_label.grid(row=3, column=0, columnspan=3, pady=4)

root.mainloop()
