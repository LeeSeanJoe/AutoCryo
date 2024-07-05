import tkinter as tk
import serial
import requests
import time

# Set up the serial connection (replace 'COM3' with the correct port)
try:
    ser = serial.Serial('COM3', 19200, timeout=1)  # Adjust COM3 port as necessary
except serial.SerialException as e:
    print(f"Failed to connect to serial port: {e}")
    ser = None

def read_pressure():
    try:
        ser.write(b'PR?')  # Command to read pressure
        pressure = ser.readline().decode('ascii').strip()
        return pressure
    except (serial.SerialException, AttributeError) as e:
        print(f"Error reading pressure: {e}")
        return "Error"

def set_pressure_setpoint(setpoint):
    try:
        command = f'SP {setpoint}\n'  # Setpoint command
        ser.write(command.encode('ascii'))
        response = ser.readline().decode('ascii').strip()
        return response
    except (serial.SerialException, AttributeError) as e:
        print(f"Error setting pressure setpoint: {e}")
        return "Error"

def send_to_arduino(url):
    try:
        requests.get(url)
    except requests.RequestException as e:
        print(f"Failed to send data to Arduino: {e}")

def update_settings():
    global desired_setpoint, reading_interval
    desired_setpoint = float(setpoint_var.get())
    reading_interval = int(reading_interval_var.get())
    warning_limit = int(warning_limit_var.get())
    shutdown_limit = int(shutdown_limit_var.get())

    # Set pressure setpoint
    set_response = set_pressure_setpoint(desired_setpoint)
    print(f"Setpoint Response: {set_response}")

    # Send warning and shutdown limits to Arduino
    send_to_arduino(f"http://<arduino_ip>/setWarning?value={warning_limit}")
    send_to_arduino(f"http://<arduino_ip>/setShutdown?value={shutdown_limit}")
    
    read_pressure_loop()  # Start the pressure reading loop

def read_pressure_loop():
    pressure_value = read_pressure()
    print(f"Pressure: {pressure_value} psi")
    current_pressure_var.set(f"{pressure_value} psi")
    
    # Send pressure value to Arduino
    send_to_arduino(f"http://<arduino_ip>/pressure?value={pressure_value}")

    root.after(reading_interval * 1000, read_pressure_loop)  # Schedule the next reading

# Initial default values
desired_setpoint = 50.0  # Default setpoint
reading_interval = 3600  # Default reading interval (1 hour in seconds)
default_warning_limit = 350
default_shutdown_limit = 300

# Tkinter GUI
root = tk.Tk()
root.title("Digital Gauge Control")

# Variables for setpoint, reading interval, and limits
setpoint_var = tk.DoubleVar(value=desired_setpoint)
reading_interval_var = tk.IntVar(value=reading_interval)
warning_limit_var = tk.IntVar(value=default_warning_limit)
shutdown_limit_var = tk.IntVar(value=default_shutdown_limit)
current_pressure_var = tk.StringVar(value="N/A")

# Create UI components
tk.Label(root, text="Desired Setpoint:").grid(row=0, column=0, sticky="e")
tk.Entry(root, textvariable=setpoint_var).grid(row=0, column=1)

tk.Label(root, text="Reading Interval (s):").grid(row=1, column=0, sticky="e")
tk.Entry(root, textvariable=reading_interval_var).grid(row=1, column=1)

tk.Label(root, text="Warning Limit:").grid(row=2, column=0, sticky="e")
tk.Entry(root, textvariable=warning_limit_var).grid(row=2, column=1)

tk.Label(root, text="Shutdown Limit:").grid(row=3, column=0, sticky="e")
tk.Entry(root, textvariable=shutdown_limit_var).grid(row=3, column=1)

tk.Label(root, text="Current Pressure:").grid(row=4, column=0, sticky="e")
tk.Label(root, textvariable=current_pressure_var).grid(row=4, column=1)

tk.Button(root, text="Update Settings", command=update_settings).grid(row=5, column=0, columnspan=2)

# Start reading pressure if the serial connection was successful
if ser:
    read_pressure_loop()

# Start the Tkinter event loop
root.mainloop()
