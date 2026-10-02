import serial
import csv
import os
from datetime import datetime
import time

# Arduino connection
PORT = "COM8"
BAUD_RATE = 9600

# CSV file
CSV_FILE = "real_sensor_data.csv"

# Connect to Arduino
arduino = serial.Serial(PORT, BAUD_RATE, timeout=1)

# Give Arduino time to reset
time.sleep(2)

# Check whether CSV already exists
file_exists = os.path.exists(CSV_FILE)

# Open CSV file in append mode
with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:

    writer = csv.writer(file)

    # Create header if file is new
    if not file_exists:
        writer.writerow([
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

            # Ignore Arduino header
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

            # Current timestamp
            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # Save data to CSV
            writer.writerow([
                timestamp,
                soil_moisture,
                temperature,
                humidity
            ])

            # Make sure data is written immediately
            file.flush()

            print(
                f"{timestamp} | "
                f"Soil: {soil_moisture:.1f}% | "
                f"Temp: {temperature:.1f}°C | "
                f"Humidity: {humidity:.1f}%"
            )

    except KeyboardInterrupt:

        print("\nData collection stopped.")

    finally:

        arduino.close()

        print(f"Data saved to {CSV_FILE}")