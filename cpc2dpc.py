import tkinter as tk
from tkinter import ttk, messagebox
import pyvisa
import time
from simple_pid import PID

# Initialize VISA resource manager with pyvisa-py backend
rm = pyvisa.ResourceManager('@py')

# Connect to the DPC (replace 'ASRL3::INSTR' with the correct address)
try:
    dpc = rm.open_resource('COM3')
except Exception as e:
    messagebox.showerror("Connection Error", f"Failed to connect to device: {e}")

# Function to read current pressure
def read_current_pressure():
    try:
        pressure = float(dpc.query('PR?'))  # Command to read current pressure
        return pressure
    except (ValueError, pyvisa.errors.VisaIOError) as e:
        messagebox.showerror("Read Error", f"Failed to read pressure: {e}")
        return None  # Handle potential conversion errors

# Function to set pressure setpoint
def set_pressure_setpoint(setpoint):
    try:
        command = f'SP {setpoint}\n'  # Setpoint command
        dpc.write(command)
    except pyvisa.errors.VisaIOError as e:
        messagebox.showerror("Write Error", f"Failed to set pressure setpoint: {e}")

# PID Controller
default_kp = 1.0
default_ki = 0.1
default_kd = 0.05
default_setpoint = 50.0
default_reading_interval = 3600  # Default pressure reading frequency (1 hour in seconds)

pid = PID(default_kp, default_ki, default_kd, setpoint=default_setpoint)
pid.output_limits = (0, 100)  # Limits for the setpoint adjustment, adjust as necessary

# Tkinter GUI
root = tk.Tk()
root.title("PID Controller Settings")

# Variables for PID parameters, setpoint, and reading frequency
kp_var = tk.DoubleVar(value=default_kp)
ki_var = tk.DoubleVar(value=default_ki)
kd_var = tk.DoubleVar(value=default_kd)
setpoint_var = tk.DoubleVar(value=default_setpoint)
reading_interval_var = tk.IntVar(value=default_reading_interval)
current_pressure_var = tk.StringVar(value="N/A")

# Function to update PID parameters and reading frequency
def update_settings():
    kp = kp_var.get()
    ki = ki_var.get()
    kd = kd_var.get()
    setpoint = setpoint_var.get()
    reading_interval = reading_interval_var.get()
    pid.tunings = (kp, ki, kd)
    pid.setpoint = setpoint
    print(f"Updated PID values: Kp={kp}, Ki={ki}, Kd={kd}, Setpoint={setpoint}")
    root.after_cancel(read_pressure_handle)  # Cancel the previous after call
    read_pressure()  # Start with the new interval

# Function to read pressure and update GUI
def read_pressure():
    global read_pressure_handle
    current_pressure = read_current_pressure()
    if current_pressure is not None:
        current_pressure_var.set(f"{current_pressure:.2f} psi")
        # Calculate new setpoint using PID
        new_setpoint = pid(current_pressure)
        set_pressure_setpoint(new_setpoint)
        print(f"Current Pressure: {current_pressure} psi, New Setpoint: {new_setpoint}")
    read_pressure_handle = root.after(reading_interval_var.get() * 1000, read_pressure)  # Read pressure at specified interval

# Create UI components
tk.Label(root, text="Kp:").grid(row=0, column=0, sticky="e")
tk.Entry(root, textvariable=kp_var).grid(row=0, column=1)

tk.Label(root, text="Ki:").grid(row=1, column=0, sticky="e")
tk.Entry(root, textvariable=ki_var).grid(row=1, column=1)

tk.Label(root, text="Kd:").grid(row=2, column=0, sticky="e")
tk.Entry(root, textvariable=kd_var).grid(row=2, column=1)

tk.Label(root, text="Setpoint:").grid(row=3, column=0, sticky="e")
tk.Entry(root, textvariable=setpoint_var).grid(row=3, column=1)

tk.Label(root, text="Reading Interval (s):").grid(row=4, column=0, sticky="e")
tk.Entry(root, textvariable=reading_interval_var).grid(row=4, column=1)

tk.Label(root, text="Current Pressure:").grid(row=5, column=0, sticky="e")
tk.Label(root, textvariable=current_pressure_var).grid(row=5, column=1)

tk.Button(root, text="Update Settings", command=update_settings).grid(row=6, column=0, columnspan=2)

# Start reading pressure
read_pressure_handle = root.after(reading_interval_var.get() * 1000, read_pressure)

# Start Tkinter event loop
root.mainloop()
