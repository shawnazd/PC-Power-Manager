import customtkinter as ctk
import subprocess
import threading
import time
import platform
from tkinter import messagebox

# -------------------- MAIN WINDOW SETUP --------------------
ctk.set_appearance_mode("dark")  # Dark mode
ctk.set_default_color_theme("green")  # Accent color theme

root = ctk.CTk()
root.title("⚡ System Power Utility")
root.geometry("600x480")
root.resizable(False, False)

# -------------------- COLORS --------------------
ACCENT_COLOR = "#00FFC6"
DANGER_COLOR = "#FF5C5C"

# -------------------- COMMAND EXECUTION --------------------
def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True, stderr=subprocess.PIPE, text=True)
        messagebox.showinfo("✅ Success", "Command executed successfully.")
        root.destroy()
    except subprocess.CalledProcessError as e:
        messagebox.showerror("❌ Error", f"Failed: {e.stderr}\nRun as administrator or check permissions.")

# -------------------- ACTIONS --------------------
def shutdown_now():
    if messagebox.askyesno("⚠ Confirm", "Shut down now?"):
        run_command("shutdown /s /t 0" if platform.system() == "Windows" else "sudo shutdown -h now")

def restart_now():
    if messagebox.askyesno("⚠ Confirm", "Restart now?"):
        run_command("shutdown /r /t 0" if platform.system() == "Windows" else "sudo shutdown -r now")

def hibernate_now():
    if messagebox.askyesno("⚠ Confirm", "Hibernate now?"):
        run_command("shutdown /h" if platform.system() == "Windows" else "sudo systemctl hibernate")

def sleep_now():
    if messagebox.askyesno("⚠ Confirm", "Sleep now?"):
        run_command("rundll32.exe powrprof.dll,SetSuspendState 0,1,0" if platform.system() == "Windows" else "systemctl suspend")

# -------------------- TIMER LOGIC --------------------
timer_running = False
timer_thread = None

def start_countdown(seconds):
    global timer_running
    timer_running = True
    cancel_btn.configure(state="normal")
    set_btn.configure(state="disabled")

    for i in range(seconds, 0, -1):
        if not timer_running:
            break
        h, rem = divmod(i, 3600)
        m, s = divmod(rem, 60)
        timer_label.configure(text=f"⏳ {h:02d}:{m:02d}:{s:02d}", text_color=ACCENT_COLOR)
        root.update()
        time.sleep(1)

    if timer_running:
        timer_label.configure(text="🔻 Shutting down...", text_color=DANGER_COLOR)
        shutdown_now()
    else:
        timer_label.configure(text="❌ Timer Cancelled", text_color=DANGER_COLOR)

    cancel_btn.configure(state="disabled")
    set_btn.configure(state="normal")

def custom_shutdown():
    global timer_thread, timer_running
    if timer_thread and timer_thread.is_alive():
        timer_running = False
        timer_thread.join()

    try:
        h = int(hours_input.get())
        m = int(minutes_input.get())
        s = int(seconds_input.get())
        total_seconds = h * 3600 + m * 60 + s
        if total_seconds <= 0:
            raise ValueError
        timer_thread = threading.Thread(target=start_countdown, args=(total_seconds,), daemon=True)
        timer_thread.start()
        messagebox.showinfo("⏱ Timer Set", f"Shutdown in {total_seconds} seconds.")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers for time.")

def cancel_shutdown():
    global timer_running
    if timer_running:
        timer_running = False
        messagebox.showinfo("Cancelled", "Shutdown timer has been cancelled.")

# -------------------- UI LAYOUT --------------------
title_label = ctk.CTkLabel(root, text="⚡ System Power Utility", font=("Segoe UI", 28, "bold"), text_color=ACCENT_COLOR)
title_label.pack(pady=20)

# --- Immediate Actions ---
frame_quick = ctk.CTkFrame(root, corner_radius=15)
frame_quick.pack(padx=20, pady=10, fill="x")

ctk.CTkLabel(frame_quick, text="Quick Actions", font=("Segoe UI", 16, "bold")).pack(pady=10)

btn_shutdown = ctk.CTkButton(frame_quick, text="🔻 Shut Down", command=shutdown_now)
btn_restart = ctk.CTkButton(frame_quick, text="🔄 Restart", command=restart_now)
btn_hibernate = ctk.CTkButton(frame_quick, text="💾 Hibernate", command=hibernate_now)
btn_sleep = ctk.CTkButton(frame_quick, text="😴 Sleep", command=sleep_now)

btn_shutdown.pack(side="left", expand=True, fill="x", padx=10, pady=8)
btn_restart.pack(side="left", expand=True, fill="x", padx=10, pady=8)
btn_hibernate.pack(side="left", expand=True, fill="x", padx=10, pady=8)
btn_sleep.pack(side="left", expand=True, fill="x", padx=10, pady=8)

# --- Custom Timer ---
frame_timer = ctk.CTkFrame(root, corner_radius=15)
frame_timer.pack(padx=20, pady=10, fill="x")

ctk.CTkLabel(frame_timer, text="Custom Timed Shutdown", font=("Segoe UI", 16, "bold")).pack(pady=10)

input_frame = ctk.CTkFrame(frame_timer, fg_color="transparent")
input_frame.pack(pady=10)

hours_input = ctk.CTkEntry(input_frame, placeholder_text="Hours", width=60, justify="center")
minutes_input = ctk.CTkEntry(input_frame, placeholder_text="Minutes", width=60, justify="center")
seconds_input = ctk.CTkEntry(input_frame, placeholder_text="Seconds", width=60, justify="center")

hours_input.grid(row=0, column=0, padx=5)
minutes_input.grid(row=0, column=1, padx=5)
seconds_input.grid(row=0, column=2, padx=5)

set_btn = ctk.CTkButton(frame_timer, text="✅ Set Timer", command=custom_shutdown)
cancel_btn = ctk.CTkButton(frame_timer, text="❌ Cancel Timer", command=cancel_shutdown, state="disabled")

set_btn.pack(side="left", expand=True, padx=10, pady=8)
cancel_btn.pack(side="left", expand=True, padx=10, pady=8)

timer_label = ctk.CTkLabel(frame_timer, text="", font=("Segoe UI", 20, "bold"))
timer_label.pack(pady=10)

root.mainloop()
