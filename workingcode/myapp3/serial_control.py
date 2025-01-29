
# from concurrent.futures import ThreadPoolExecutor
# import time
# import serial

# # Initialize serial port
# ser = serial.Serial('COM4', 9600, timeout=1)

# def send_command(command):
#     start_time = time.time()
#     ser.write((command + '\n').encode())
#     response = ser.readline().decode().strip()
#     end_time = time.time()
#     duration = end_time - start_time
#     print(f"Command '{command}' took {duration:.4f} seconds")
#     return response

# def handle_door_opening():
#     """Handles door opening asynchronously."""
#     print("Sending 'open' command to open the door")
#     send_command('open')
#     time.sleep(10)  # Simulate door opening delay
#     print("Sending 'close' command to close the door")
#     send_command('close')

# # Use ThreadPoolExecutor to run door opening in a separate thread
# def open_door_async():
#     with ThreadPoolExecutor() as executor:
#         future = executor.submit(handle_door_opening)
#         # You can add other non-blocking operations here if needed





##############Working
# import time
# import requests
# from concurrent.futures import ThreadPoolExecutor

# # Replace with the ESP32's IP address as printed to the Serial Monitor upon successful Wi-Fi connection
# ESP32_IP = "http://192.168.29.148"  # Replace with your ESP32's IP address

# def send_command(command):
#     """Send command ('open' or 'close') to ESP32 and print the response time."""
#     url = f"{ESP32_IP}/{command}"
#     start_time = time.time()
#     try:
#         response = requests.get(url)
#         end_time = time.time()
#         duration = end_time - start_time
#         print(f"Command '{command}' took {duration:.4f} seconds")
#         return response.text
#     except requests.exceptions.RequestException as e:
#         print(f"Failed to send command '{command}': {e}")
#         return None

# def handle_door_opening():
#     """Handles door opening and closing asynchronously."""
#     print("Sending 'open' command to open the door")
#     send_command('open')
#     time.sleep(6)  # Wait for 10 seconds before closing
#     print("Sending 'close' command to close the door")
#     send_command('close')
# executor = ThreadPoolExecutor()

# def open_door_async():
#     """Open door asynchronously by running door control in a separate thread."""
#     executor.submit(handle_door_opening)


# # Test the open door functionality
# if __name__ == "__main__":
#     open_door_async()





import time
import requests
from concurrent.futures import ThreadPoolExecutor

# Emergency status flags
emergency_active = False
emergency_lock = False
ESP32_IP = "http://192.168.29.148"  # Replace with your ESP32's IP address

def set_emergency_status(status):
    global emergency_active
    emergency_active = status

def send_command(command):
    """Send command ('open' or 'close') to ESP32 and print the response time."""
    url = f"{ESP32_IP}/{command}"
    start_time = time.time()
    try:
        response = requests.get(url, timeout=2)
        end_time = time.time()
        duration = end_time - start_time
        print(f"Command '{command}' took {duration:.4f} seconds")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to send command '{command}': {e}")
        return None

def handle_door_opening():
    """Handles door opening with emergency override capability."""
    global emergency_active
    
    print("Sending 'open' command to open the door")
    send_command('open')
    
    start_time = time.time()
    while True:
        # Check every second
        time.sleep(1)
        elapsed = time.time() - start_time
        
        # Emergency override check
        if emergency_active:
            print("Emergency active - door remains open")
            continue  # Skip closing
        
        # Normal operation timeout
        if elapsed >= 6:
            print("Sending 'close' command to close the door")
            send_command('close')
            break

executor = ThreadPoolExecutor()

def open_door_async():
    """Open door asynchronously by running door control in a separate thread."""
    executor.submit(handle_door_opening)

# Test the open door functionality
if __name__ == "__main__":
    open_door_async()