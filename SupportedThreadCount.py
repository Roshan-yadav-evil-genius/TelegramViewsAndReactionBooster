import threading
import time



# def print_live_thread_count():
#     live_thread_count = threading.active_count()
#     print(f"Number of live threads: {live_thread_count}")

# Call the function to print the live thread count
# print_live_thread_count()

def worker():
    data = bytearray(1024 * 1024)
    while True:
        # Simulate some work on the allocated memory
        time.sleep(1)

thread_list = []
try:
    while True:
        thread = threading.Thread(target=worker)
        thread_list.append(thread)
        thread.start()
        print(f"Thread {thread.ident} started.")

except Exception as e:
    print(f"Error: {e}")

finally:
    print(f"Total no of live thread :{len(thread_list)}")

510