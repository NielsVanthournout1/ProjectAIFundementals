import requests
import json
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import pandas as pd
import serial
import time

# API URL
api_url = 'https://www.chatforumaiprogramming.be/api.php'  # Replace with your actual domain


# Set up serial communication with the micro:bit (adjust COM port as needed)
ser = serial.Serial('COM4', 115200)  # Replace 'COM3' with your micro:bit's COM port

# Function to fetch messages from the API
def fetch_messages():
    response = requests.get(api_url)
    if response.status_code == 200:
        response_data = response.json()
        if response_data['status'] == 'success':
            return response_data['messages']
        else:
            return []  # Return an empty list if no messages are found
    else:
        print(f"Failed to connect to API. Status Code: {response.status_code}")
        return []

# Function to display messages in the GUI and notify the micro:bit of new messages
def display_messages():
    messages = fetch_messages()
    for widget in messages_frame.winfo_children():
        widget.destroy()  # Clear the current messages in the frame

    if messages:
        for message in messages:
            user_label = tk.Label(messages_frame, text=f"User: {message['user']}")
            user_label.pack(anchor='w', pady=2)
            message_label = tk.Label(messages_frame, text=f"Message: {message['message']}")
            message_label.pack(anchor='w', pady=2)
            date_label = tk.Label(messages_frame, text=f"Date: {message['dateTime']}")
            date_label.pack(anchor='w', pady=2)
            separator = ttk.Separator(messages_frame, orient='horizontal')
            separator.pack(fill='x', pady=5)
        
        # Send a notification signal to the micro:bit
        ser.write(b'new_message\n')
    else:
        no_message_label = tk.Label(messages_frame, text="No messages found.")
        no_message_label.pack()

# Function to send a new message to the API
def send_message():
    user = user_entry.get()  # Get the user input
    message = message_entry.get()  # Get the message input
    
    if user and message:  # Check if both fields are filled
        # Get the current time in a readable format
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Prepare the data to be sent to the API
        data = {'user': user, 'message': message, 'dateTime': current_time}
        
        # Send the message to the API
        response = requests.post(api_url, json=data)
        
        if response.status_code == 200:
            response_data = response.json()
            print('Response from API:', response_data)
            display_messages()  # Refresh the message list after sending the new message
        else:
            print(f"Failed to connect to API. Status Code: {response.status_code}")
    else:
        print("Please enter both a user name and a message.")

# Function to analyze the messages using pandas (e.g., count messages per user)
def analyze_messages():
    messages = fetch_messages()
    if messages:
        df = pd.DataFrame(messages)
        df['dateTime'] = pd.to_datetime(df['dateTime'])  # Convert dateTime to pandas datetime object
        print("Messages per User:")
        print(df['user'].value_counts())  # Count messages per user
        print("\nMessages per Time:")
        print(df['dateTime'].dt.date.value_counts())  # Count messages per date
    else:
        print("No messages to analyze.")

# Create the main window
root = tk.Tk()
root.title("Messages from API")
root.geometry("400x500")

# Frame for the input fields and send button
input_frame = tk.Frame(root)
input_frame.pack(fill='x', padx=10, pady=10)

# Label and Entry for the user name
user_label = tk.Label(input_frame, text="Your Name:")
user_label.pack(side='left', padx=5)
user_entry = tk.Entry(input_frame)
user_entry.pack(side='left', fill='x', expand=True, padx=5)

# Label and Entry for the message
message_label = tk.Label(input_frame, text="Your Message:")
message_label.pack(side='left', padx=5)
message_entry = tk.Entry(input_frame)
message_entry.pack(side='left', fill='x', expand=True, padx=5)

# Button to send the message
send_button = tk.Button(input_frame, text="Send Message", command=send_message)
send_button.pack(side='left', padx=5)

# Button to refresh the messages
refresh_button = tk.Button(root, text="Refresh Messages", command=display_messages)
refresh_button.pack(pady=10)

# Button to analyze messages
analyze_button = tk.Button(root, text="Analyze Messages", command=analyze_messages)
analyze_button.pack(pady=10)

# Frame to hold the messages
messages_frame = tk.Frame(root)
messages_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Fetch and display the initial messages
display_messages()

# Start the main event loop
root.mainloop()