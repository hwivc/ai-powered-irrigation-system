import serial
import openpyxl
import os
from datetime import datetime
import time

# Arduino connection
PORT = "COM8"
BAUD_RATE = 9600

# Excel file
EXCEL_FILE = "real_sensor_data.xlsx"

# Connect to Arduino
arduino = serial.Serial(PORT, BAUD_RATE, timeout=1)

# Give Arduino time to reset
time.sleep(2)

# Open existing Excel file or create a new one
if os.path.exists(EXCEL_FILE):
    workbook = openpyxl.load_workbook(EXCEL_FILE)
    sheet = workbook.active
else:
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Sensor Data"

    sheet.append([
        "Timestamp",
        "Soil_Moisture",
        "Temperature_C",
        "Humidity"
    ])

print("Connected to Arduino on COM8")
print("Collecting sensor data...")
print("Press Ctrl+C to stop.\n")

try:

    while True:

        line = arduino.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()

        # Ignore empty lines
        if not line:
            continue

        # Ignore the Arduino header
        if line.startswith("Soil_Moisture"):
            continue

        # Ignore invalid readings
        if "," not in line:
            continue

        values = line.split(",")

        if len(values) != 3:
            continue

        try:
            soil_moisture = float(values[0])
            temperature = float(values[1])
            humidity = float(values[2])

        except ValueError:
            continue

        timestamp = datetime.now()

        # Add data to Excel
        sheet.append([
            timestamp,
            soil_moisture,
            temperature,
            humidity
        ])

        # Save the file
        workbook.save(EXCEL_FILE)

        print(
            f"{timestamp} | "
            f"Soil: {soil_moisture:.1f}% | "
            f"Temp: {temperature:.1f}°C | "
            f"Humidity: {humidity:.1f}%"
        )

except KeyboardInterrupt:

    print("\nData collection stopped.")

finally:

    workbook.save(EXCEL_FILE)
    arduino.close()

    print(f"Data saved to {EXCEL_FILE}")