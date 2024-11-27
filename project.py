import requests
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pandas as pd
import serial
import json
import os
from search_messages import open_search_window  # Import the function

# API URL
api_url = 'https://www.chatforumaiprogramming.be/api.php'  # Replace with your actual domain

# Set the serial port to COM4 (start with None to disable by default)
ser = None

# File to store the last message
last_message_file = 'last_message.json'

# To track if notifications are enabled
notifications_enabled = False

# To track if auto-refresh should happen
auto_refresh_enabled = True

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
    if auto_refresh_enabled:
        messages = fetch_messages()
        for widget in messages_canvas_frame.winfo_children():
            widget.destroy()

        if messages:
            most_recent_message = messages[0]  # Get the most recent message (last in list)
            stored_last_message = load_last_message()
            
            # Check if the most recent message is different from the stored one
            if stored_last_message is None or stored_last_message.get('dateTime') != most_recent_message['dateTime']:
                save_last_message(most_recent_message)  # Save the new most recent message

                # Only notify if the notifications are enabled
                if notifications_enabled and ser:
                    ser.write(b'new_message\n')  # Notify the micro:bit with a new message

            # Display all messages in reverse order (bottom to top)
            for message in reversed(messages):  # Reversed so the most recent is at the bottom
                tk.Label(messages_canvas_frame, text=f"User: {message['user']}").pack(anchor='w', pady=2)
                tk.Label(messages_canvas_frame, text=f"Message: {message['message']}").pack(anchor='w', pady=2)
                tk.Label(messages_canvas_frame, text=f"Date: {message['dateTime']}").pack(anchor='w', pady=2)
                ttk.Separator(messages_canvas_frame, orient='horizontal').pack(fill='x', pady=5)

        else:
            tk.Label(messages_canvas_frame, text="No messages found.").pack()

    # Schedule the next refresh every second (if auto-refresh is enabled)
    if auto_refresh_enabled:
        root.after(1000, display_messages)  # Schedule the next refresh

# Function to save the most recent message to a file
def save_last_message(message):
    try:
        # Save user, message, and dateTime
        last_message = {
            'user': message['user'], 
            'message': message['message'],
            'dateTime': message['dateTime']
        }
        with open(last_message_file, 'w') as f:
            json.dump(last_message, f)
    except Exception as e:
        print(f"Error saving last message: {e}")

# Function to load the last message from the file
def load_last_message():
    if os.path.exists(last_message_file):
        try:
            with open(last_message_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading last message: {e}")
    return None

# Function to send a new message to the API
def send_message():
    user, message = user_entry.get(), message_entry.get()
    if user and message:
        data = {'user': user, 'message': message, 'dateTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        try:
            response = requests.post(api_url, json=data)
            if response.status_code == 200:
                # Do not refresh automatically after sending a message
                pass
            else:
                print(f"Failed to send message. Status Code: {response.status_code}")
        except Exception as e:
            print(f"Error sending message: {e}")
    else:
        messagebox.showerror("Error", "Please enter both a name and a message.")

    messages = fetch_messages()
    if messages:
        df = pd.DataFrame(messages)
        df['dateTime'] = pd.to_datetime(df['dateTime'])
        print("Messages per User:\n", df['user'].value_counts())
        print("Messages per Date:\n", df['dateTime'].dt.date.value_counts())
    else:
        print("No messages to analyze.")

# Function to toggle notifications (and the micro:bit connection)
def toggle_notifications():
    global notifications_enabled, ser

    if notifications_enabled:
        # Turn off notifications and disable micro:bit
        notifications_enabled = False
        if ser:
            ser.close()
            ser = None
        notifications_button.config(text="Notifications Off")
        print("Notifications disabled.")
    else:
        # Try to turn on notifications and enable micro:bit
        try:
            ser = serial.Serial('COM4', 115200, timeout=1)
            notifications_enabled = True  # Enable notifications only if connection succeeds
            notifications_button.config(text="Notifications On")
            print("Notifications enabled, Micro:bit system connected.")
        except serial.SerialException:
            # If connection fails, do not enable notifications
            ser = None
            messagebox.showerror("Error", "Failed to connect to Micro:bit.")
            print("Failed to connect to Micro:bit.")

# Function to toggle auto-refresh behavior
def toggle_auto_refresh():
    global auto_refresh_enabled
    auto_refresh_enabled = not auto_refresh_enabled
    if auto_refresh_enabled:
        auto_refresh_button.config(text="Disable Auto-Refresh")
        print("Auto-refresh enabled.")
        display_messages()  # Start refreshing again if enabled
    else:
        auto_refresh_button.config(text="Enable Auto-Refresh")
        print("Auto-refresh disabled.")

# Create the main window
root = tk.Tk()
root.title("Messages from API")
root.geometry("500x600")

# Set minimum size to ensure buttons and fields are visible
root.minsize(600, 150)  # Minimum width: 400, Minimum height: 150

# Frame for buttons on top
buttons_frame = tk.Frame(root)
buttons_frame.pack(side='top', fill='x', pady=10)

# Buttons for analyzing, notifications, and auto-refresh
auto_refresh_button = tk.Button(buttons_frame, text="Disable Auto-Refresh", command=toggle_auto_refresh)
auto_refresh_button.pack(side='left', padx=5)

notifications_button = tk.Button(buttons_frame, text="Notifications Off", command=toggle_notifications)
notifications_button.pack(side='left', padx=5)

search_button = tk.Button(buttons_frame, text="Search Messages", command=open_search_window)
search_button.pack(side='right', padx=5)

# Frame for messages with scrollbar
messages_frame = tk.Frame(root)
messages_frame.pack(fill='both', expand=True, padx=10, pady=10)

messages_canvas = tk.Canvas(messages_frame)
messages_scrollbar = ttk.Scrollbar(messages_frame, orient='vertical', command=messages_canvas.yview)
messages_canvas.configure(yscrollcommand=messages_scrollbar.set)

messages_canvas.pack(side='left', fill='both', expand=True)
messages_scrollbar.pack(side='right', fill='y')

# Frame inside the canvas for messages
messages_canvas_frame = tk.Frame(messages_canvas)
messages_canvas.create_window((0, 0), window=messages_canvas_frame, anchor='nw')

# Update the canvas scroll region when content changes
def update_scroll_region(event):
    messages_canvas.configure(scrollregion=messages_canvas.bbox("all"))

messages_canvas_frame.bind("<Configure>", update_scroll_region)

# Input frame (User, Message and Send button) at the bottom
input_frame = tk.Frame(root)
input_frame.pack(side='bottom', fill='x', padx=10, pady=10)

# User and Message input fields
tk.Label(input_frame, text="Your Name:").pack(side='left', padx=5)

# Set a fixed width for the username input field
user_entry = tk.Entry(input_frame, width=15)  # Adjusted width for the name entry
user_entry.pack(side='left', padx=5)

tk.Label(input_frame, text="Your Message:").pack(side='left', padx=5)

# Message input field should be as small as possible but flexible
message_entry = tk.Entry(input_frame, width=30)  # Minimum width for the message input
message_entry.pack(side='left', fill='x', expand=True, padx=5)

# Send Message button should always be visible
send_button = tk.Button(input_frame, text="Send Message", command=send_message)
send_button.pack(side='right', padx=5)

# Start the initial call to display messages
display_messages()

# Start the main event loop
root.mainloop()
