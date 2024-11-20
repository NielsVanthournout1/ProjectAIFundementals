import requests
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pandas as pd
import serial

# API URL
api_url = 'https://www.chatforumaiprogramming.be/api.php'  # Replace with your actual domain

# Initialize micro:bit connection and toggle state
ser = None
microbit_enabled = False

def connect_microbit():
    """Attempt to connect to the micro:bit on COM4."""
    global ser
    try:
        ser = serial.Serial('COM4', 115200, timeout=1)  # Update 'COM4' if needed for your system
        print("Connected to micro:bit on COM4")
        return True
    except serial.SerialException:
        ser = None
        print("Failed to connect to micro:bit on COM4. Make sure it's connected.")
        return False

def toggle_microbit():
    """Enable or disable the micro:bit functionality."""
    global microbit_enabled, ser
    microbit_enabled = not microbit_enabled
    if microbit_enabled:
        if connect_microbit():
            messagebox.showinfo("Micro:bit Enabled", "Micro:bit functionality enabled.")
        else:
            messagebox.showerror("Micro:bit Error", "Failed to connect to micro:bit. Functionality disabled.")
            microbit_enabled = False
    else:
        if ser:
            ser.close()
            ser = None
        messagebox.showinfo("Micro:bit Disabled", "Micro:bit functionality disabled.")

# Function to fetch messages from the API
def fetch_messages():
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get('messages', [])
    except Exception as e:
        print(f"Error fetching messages: {e}")
    return []

# Function to display messages in the GUI and notify the micro:bit
def display_messages():
    messages = fetch_messages()
    for widget in messages_frame.winfo_children():
        widget.destroy()

    if messages:
        for message in messages:
            tk.Label(messages_frame, text=f"User: {message['user']}").pack(anchor='w', pady=2)
            tk.Label(messages_frame, text=f"Message: {message['message']}").pack(anchor='w', pady=2)
            tk.Label(messages_frame, text=f"Date: {message['dateTime']}").pack(anchor='w', pady=2)
            ttk.Separator(messages_frame, orient='horizontal').pack(fill='x', pady=5)

        # Send notification to micro:bit if enabled
        if microbit_enabled and ser:
            ser.write(b'new_message\n')
    else:
        tk.Label(messages_frame, text="No messages found.").pack()

# Function to send a new message to the API
def send_message():
    user, message = user_entry.get(), message_entry.get()
    if user and message:
        data = {'user': user, 'message': message, 'dateTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        try:
            response = requests.post(api_url, json=data)
            if response.status_code == 200:
                display_messages()
            else:
                print(f"Failed to send message. Status Code: {response.status_code}")
        except Exception as e:
            print(f"Error sending message: {e}")
    else:
        messagebox.showerror("Error", "Please enter both a name and a message.")

# Function to analyze messages using pandas
def analyze_messages():
    messages = fetch_messages()
    if messages:
        df = pd.DataFrame(messages)
        df['dateTime'] = pd.to_datetime(df['dateTime'])
        print("Messages per User:\n", df['user'].value_counts())
        print("Messages per Date:\n", df['dateTime'].dt.date.value_counts())
    else:
        print("No messages to analyze.")

# Create the main window
root = tk.Tk()
root.title("Messages from API")
root.geometry("400x550")

# Input frame
input_frame = tk.Frame(root)
input_frame.pack(fill='x', padx=10, pady=10)

tk.Label(input_frame, text="Your Name:").pack(side='left', padx=5)
user_entry = tk.Entry(input_frame)
user_entry.pack(side='left', fill='x', expand=True, padx=5)

tk.Label(input_frame, text="Your Message:").pack(side='left', padx=5)
message_entry = tk.Entry(input_frame)
message_entry.pack(side='left', fill='x', expand=True, padx=5)

send_button = tk.Button(input_frame, text="Send Message", command=send_message)
send_button.pack(side='left', padx=5)

# Buttons for refreshing and analyzing messages
refresh_button = tk.Button(root, text="Refresh Messages", command=display_messages)
refresh_button.pack(pady=10)

analyze_button = tk.Button(root, text="Analyze Messages", command=analyze_messages)
analyze_button.pack(pady=10)

# Micro:bit toggle button
toggle_button = tk.Button(root, text="Toggle Micro:bit", command=toggle_microbit)
toggle_button.pack(pady=10)

# Frame for displaying messages
messages_frame = tk.Frame(root)
messages_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Start the main event loop
root.mainloop()
