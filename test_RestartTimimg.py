import datetime
import os
import sys
import time
import subprocess

def restart_program():
    # Paths to the two files you want to execute
    file1 = 'test_DemoFirstFile.py'
    file2 = 'test_DemoSecondFile.py'

    # Executing the first file
    print("Executing the first file...")
    process = subprocess.Popen([sys.executable, file1])

    # Wait for 30 seconds or until process finishes
    try:
        process.wait(timeout=30)
    except subprocess.TimeoutExpired:
        print("First file did not finish in 30 seconds. Terminating it...")
        process.terminate()
        try:
            process.wait(timeout=5)  # Wait for 5 seconds for clean termination
        except subprocess.TimeoutExpired:
            process.kill()  # Forcefully kill if it doesn't terminate cleanly

    # Executing the second file
    print("Executing the Main file...")
    # subprocess.run([sys.executable, file2])

    # Restart the current script
    python = sys.executable
    os.execl(python, python, *sys.argv)

def get_remaining_time(target, current):
    """Calculate the remaining time until the target time."""
    target_datetime = datetime.datetime.combine(datetime.date.today(), target)
    current_datetime = datetime.datetime.combine(datetime.date.today(), current)

    # Adjust for the next day if the target time is already passed for today
    if current_datetime > target_datetime:
        target_datetime += datetime.timedelta(days=1)

    return target_datetime - current_datetime

# Define the target time: 8:00 PM
target_time = datetime.time(16,55, 0)  # 20:00 or 8:00 PM

while True:
    # Get the current time
    now = datetime.datetime.now().time()
    print(f"[+] Remaining Time : {get_remaining_time(target_time,now)}")
    if now.hour == target_time.hour and now.minute == target_time.minute:
        print("Restarting program at 8:00 PM...")
        restart_program()

    # Sleep for a short duration to prevent high CPU usage
    time.sleep(1)  # Sleep for 30 seconds
