import tkinter as tk
from tkinter import messagebox
import pyvisa

# Initialize the VISA resource manager
rm = pyvisa.ResourceManager()

# Open a connection to the Lakeshore device (adjust the resource string as needed)
try:
    lakeshore = rm.open_resource('ASRL1::INSTR')  # Replace 'ASRL1::INSTR' with your COM port
except pyvisa.errors.VisaIOError as e:
    messagebox.showerror("Connection Error", f"Failed to connect to device: {e}")
    lakeshore = None

# Function to read temperature
def read_temperature():
    if lakeshore is not None:
        try:
            temperature = lakeshore.query('KRDG? A')  # 'A' for sensor channel A
            return float(temperature)
        except (ValueError, pyvisa.errors.VisaIOError) as e:
            messagebox.showerror("Read Error", f"Error reading temperature: {e}")
            return None

# Function to update temperature display
def update_temperature():
    temp = read_temperature()
    if temp is not None:
        current_temp_var.set(f"{temp:.2f} K")
    root.after(update_interval_var.get() * 1000, update_temperature)  # Update at specified interval

# Function to update the interval
def update_interval():
    interval = update_interval_var.get()
    print(f"Update interval set to {interval} seconds")
    root.after_cancel(update_temperature_handle)  # Cancel the previous after call
    update_temperature()  # Start with the new interval

# Tkinter GUI
root = tk.Tk()
root.title("Lakeshore Temperature Display")

current_temp_var = tk.StringVar(value="N/A")
default_interval = 3600  # Default update interval (1 hour in seconds)
update_interval_var = tk.IntVar(value=default_interval)

# Create UI components
tk.Label(root, text="Current Temperature:").grid(row=0, column=0, sticky="e")
tk.Label(root, textvariable=current_temp_var).grid(row=0, column=1)

tk.Label(root, text="Update Interval (s):").grid(row=1, column=0, sticky="e")
tk.Entry(root, textvariable=update_interval_var).grid(row=1, column=1)

tk.Button(root, text="Update Interval", command=update_interval).grid(row=2, column=0, columnspan=2)

# Start updating temperature
update_temperature_handle = root.after(update_interval_var.get() * 1000, update_temperature)

# Start Tkinter event loop
root.mainloop()

# Close the connection when the application is closed
if lakeshore is not None:
    lakeshore.close()
