import requests
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pandas as pd
import serial
import json
import os
from search_messages import open_search_window
from message_fetcher import MessageFetcher

# API URL to fetch and post messages
api_url = 'https://www.chatforumaiprogramming.be/api.php'  # Replace with your actual domain

# Initialize the serial connection as None (disabled by default)
ser = None

# File to store the last message details
last_message_file = 'last_message.json'

# Track if notifications are enabled
notifications_enabled = False

# Track if auto-refresh is enabled
auto_refresh_enabled = True

# Main class for fetching messages, inheriting from MessageFetcher
class MessageFetcherMain(MessageFetcher):
    def __init__(self, api_url):
        self.api_url = api_url

    def fetch_messages(self):
        # Fetches messages from the API
        try:
            response = requests.get(self.api_url)
            if response.status_code == 200:
                response_data = response.json()
                return response_data.get('messages', [])
        except Exception as e:
            print(f"Error fetching messages: {e}")
        return []

# Function to display messages in the Tkinter canvas
def display_messages(messages_canvas_frame, notifications_enabled, ser):
    if auto_refresh_enabled:  # Refresh messages only if auto-refresh is enabled
        messages = fetch_messages()

        # Clear the existing messages from the canvas
        for widget in messages_canvas_frame.winfo_children():
            widget.destroy()

        # Display messages if any are found
        if messages:
            most_recent_message = messages[0]
            stored_last_message = load_last_message(last_message_file)

            # Save and notify if the message is new
            if stored_last_message is None or stored_last_message.get('dateTime') != most_recent_message['dateTime']:
                save_last_message(most_recent_message, last_message_file)

                if notifications_enabled and ser and ser.is_open:
                    ser.write(b'new_message\n')  # Send notification to micro:bit

            # Display the messages in reverse order (newest at the bottom)
            for message in reversed(messages):
                tk.Label(messages_canvas_frame, text=f"User: {message['user']}").pack(anchor='w', pady=2)
                tk.Label(messages_canvas_frame, text=f"Message: {message['message']}").pack(anchor='w', pady=2)
                tk.Label(messages_canvas_frame, text=f"Date: {message['dateTime']}").pack(anchor='w', pady=2)
                ttk.Separator(messages_canvas_frame, orient='horizontal').pack(fill='x', pady=5)

        else:
            tk.Label(messages_canvas_frame, text="No messages found.").pack()

        # Schedule the next refresh every second (1000 ms)
        root.after(1000, display_messages, messages_canvas_frame, notifications_enabled, ser)  # Refresh every second

# Function to save the most recent message to a file
def save_last_message(message, last_message_file):
    try:
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
def load_last_message(last_message_file):
    if os.path.exists(last_message_file):
        try:
            with open(last_message_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading last message: {e}")
    return None

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

# Function to send a new message to the API
def send_message():
    user, message = user_entry.get(), message_entry.get()
    if user and message:
        data = {'user': user, 'message': message, 'dateTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        try:
            response = requests.post(api_url, json=data)
            if response.status_code == 200:
                # No auto-refresh after sending the message
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

# Function to toggle notifications and the micro:bit connection
def toggle_notifications():
    global notifications_enabled, ser

    if notifications_enabled:
        notifications_enabled = False
        if ser:
            ser.close()  # Close the micro:bit connection
            ser = None
        notifications_button.config(text="Notifications Off")
        print("Notifications disabled.")
    else:
        try:
            ser = serial.Serial('COM4', 115200, timeout=1)  # Open serial connection
            notifications_enabled = True
            notifications_button.config(text="Notifications On")
            print("Notifications enabled, Micro:bit system connected.")
        except serial.SerialException:
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
        display_messages(messages_canvas_frame, notifications_enabled, ser)  # Start refreshing
    else:
        auto_refresh_button.config(text="Enable Auto-Refresh")
        print("Auto-refresh disabled.")

# Create the main window
root = tk.Tk()
root.title("Messages from API")
root.geometry("500x600")

# Set minimum window size
root.minsize(600, 150)

# Frame for buttons (top of the window)
buttons_frame = tk.Frame(root)
buttons_frame.pack(side='top', fill='x', pady=10)

# Buttons for analyzing, notifications, and auto-refresh
auto_refresh_button = tk.Button(buttons_frame, text="Disable Auto-Refresh", command=toggle_auto_refresh)
auto_refresh_button.pack(side='left', padx=5)

notifications_button = tk.Button(buttons_frame, text="Notifications Off", command=toggle_notifications)
notifications_button.pack(side='left', padx=5)

# Search messages button
search_button = tk.Button(buttons_frame, text="Search Messages", command=open_search_window)
search_button.pack(side='left', padx=10)

# Frame for displaying messages with scrollbar
messages_frame = tk.Frame(root)
messages_frame.pack(fill='both', expand=True, padx=10, pady=10)

messages_canvas = tk.Canvas(messages_frame)
messages_scrollbar = ttk.Scrollbar(messages_frame, orient='vertical', command=messages_canvas.yview)
messages_canvas.configure(yscrollcommand=messages_scrollbar.set)

messages_canvas.pack(side='left', fill='both', expand=True)
messages_scrollbar.pack(side='right', fill='y')

# Frame inside the canvas for message labels
messages_canvas_frame = tk.Frame(messages_canvas)
messages_canvas.create_window((0, 0), window=messages_canvas_frame, anchor='nw')

# Update the scroll region when content changes
def update_scroll_region(event):
    messages_canvas.configure(scrollregion=messages_canvas.bbox("all"))

messages_canvas_frame.bind("<Configure>", update_scroll_region)

# Input frame for the user and message fields
input_frame = tk.Frame(root)
input_frame.pack(side='bottom', fill='x', padx=10, pady=10)

tk.Label(input_frame, text="Your Name:").pack(side='left', padx=5)
user_entry = tk.Entry(input_frame, width=15)
user_entry.pack(side='left', padx=5)

tk.Label(input_frame, text="Your Message:").pack(side='left', padx=5)
message_entry = tk.Entry(input_frame, width=30)
message_entry.pack(side='left', fill='x', expand=True, padx=5)

# Send message button
send_button = tk.Button(input_frame, text="Send Message", command=send_message)
send_button.pack(side='right', padx=5)

# Initialize the MessageFetcher instance
message_fetcher = MessageFetcherMain(api_url)

# Start displaying messages
display_messages(messages_canvas_frame, notifications_enabled, ser)

# Start the main event loop
root.mainloop()
