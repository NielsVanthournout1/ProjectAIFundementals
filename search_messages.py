import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry  # Import DateEntry for the date picker
import pandas as pd
import requests

# API URL
api_url = 'https://www.chatforumaiprogramming.be/api.php'

# Function to fetch messages from the API and convert them into a DataFrame
def fetch_messages():
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            # Convert the messages to a DataFrame
            messages = response.json().get('messages', [])
            df = pd.DataFrame(messages)
            df['dateTime'] = pd.to_datetime(df['dateTime'])  # Convert dateTime to datetime
            return df
    except Exception as e:
        print(f"Error fetching messages: {e}")
    return pd.DataFrame()  # Return an empty DataFrame if there's an error

# Function to search messages by user, date, or word
def search_messages():
    user = user_entry.get()
    selected_date = date_picker.get_date()
    word = word_entry.get()

    # Fetch all messages into a pandas DataFrame
    df = fetch_messages()

    if not df.empty:
        # Filter by user (exact match)
        if user:
            df = df[df['user'].str.lower() == user.lower()]  # Exact match (case-insensitive)
        
        # Filter by date
        if selected_date:
            # Filter by the selected date
            df = df[df['dateTime'].dt.date == selected_date]
        
        # Filter by word in the message
        if word:
            # Filter by word in the message content
            df = df[df['message'].str.contains(word, case=False, na=False)]  # Case-insensitive search
        
        # Display results
        for widget in results_frame.winfo_children():
            widget.destroy()  # Clear previous results
        
        if not df.empty:
            for _, row in df.iterrows():
                tk.Label(results_frame, text=f"User: {row['user']}").pack(anchor='w', pady=2)
                tk.Label(results_frame, text=f"Message: {row['message']}").pack(anchor='w', pady=2)
                tk.Label(results_frame, text=f"Date: {row['dateTime']}").pack(anchor='w', pady=2)
                ttk.Separator(results_frame, orient='horizontal').pack(fill='x', pady=5)
        else:
            tk.Label(results_frame, text="No messages found.").pack()
    else:
        messagebox.showerror("Error", "Failed to fetch messages or no messages available.")

# Toegevoegde variabele om de huidige pagina bij te houden
current_page = 0
messages_per_page = 3  # Aantal berichten per pagina

# Functie om berichten te tonen op basis van de huidige pagina
def display_paginated_messages():
    global current_page
    messages = fetch_messages()

    for widget in messages_canvas_frame.winfo_children():
        widget.destroy()

    if messages:
        start_index = current_page * messages_per_page
        end_index = start_index + messages_per_page
        paginated_messages = messages[start_index:end_index]

        for message in reversed(paginated_messages):  # Reversed zodat nieuwste onderaan staat
            tk.Label(messages_canvas_frame, text=f"User: {message['user']}").pack(anchor='w', pady=2)
            tk.Label(messages_canvas_frame, text=f"Message: {message['message']}").pack(anchor='w', pady=2)
            tk.Label(messages_canvas_frame, text=f"Date: {message['dateTime']}").pack(anchor='w', pady=2)
            ttk.Separator(messages_canvas_frame, orient='horizontal').pack(fill='x', pady=5)

        # Als er geen berichten meer zijn om weer te geven
        if not paginated_messages:
            tk.Label(messages_canvas_frame, text="No more messages to display.").pack()

    else:
        tk.Label(messages_canvas_frame, text="No messages found.").pack()

    update_navigation_buttons(messages)

# Functie om de navigatieknoppen te updaten
def update_navigation_buttons(messages):
    prev_button.config(state=tk.NORMAL if current_page > 0 else tk.DISABLED)
    next_button.config(state=tk.NORMAL if (current_page + 1) * messages_per_page < len(messages) else tk.DISABLED)

# Functie om naar de vorige pagina te gaan
def show_previous_page():
    global current_page
    if current_page > 0:
        current_page -= 1
        display_paginated_messages()

# Functie om naar de volgende pagina te gaan
def show_next_page():
    global current_page
    messages = fetch_messages()
    if (current_page + 1) * messages_per_page < len(messages):
        current_page += 1
        display_paginated_messages()
# Create the search window
def create_search_window():
    search_window = tk.Toplevel()
    search_window.title("Search Messages")
    search_window.geometry("500x400")
    
    # User input field
    tk.Label(search_window, text="Enter User Name:").pack(pady=5)
    global user_entry
    user_entry = tk.Entry(search_window)
    user_entry.pack(pady=5)
    
    # Date picker for date selection
    tk.Label(search_window, text="Select Date:").pack(pady=5)
    global date_picker
    date_picker = DateEntry(search_window, width=12, background='darkblue', foreground='white', borderwidth=2)
    date_picker.pack(pady=5)
    
    # Word input field
    tk.Label(search_window, text="Enter Word to Search:").pack(pady=5)
    global word_entry
    word_entry = tk.Entry(search_window)
    word_entry.pack(pady=5)
    
    # Search button
    search_button = tk.Button(search_window, text="Search", command=search_messages)
    search_button.pack(pady=10)
    
    # Frame for scrollable area to display results
    global results_frame
    results_frame = tk.Frame(search_window)
    
    # Add a Canvas widget for scrolling
    results_canvas = tk.Canvas(results_frame)
    results_scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=results_canvas.yview)
    results_canvas.configure(yscrollcommand=results_scrollbar.set)

    results_canvas.pack(side='left', fill='both', expand=True)
    results_scrollbar.pack(side='right', fill='y')
    
    # Create a frame inside the canvas to hold the message results
    results_canvas_frame = tk.Frame(results_canvas)
    results_canvas.create_window((0, 0), window=results_canvas_frame, anchor='nw')

    # Update the canvas scroll region when content changes
    def update_scroll_region(event):
        results_canvas.configure(scrollregion=results_canvas.bbox("all"))

    results_canvas_frame.bind("<Configure>", update_scroll_region)

    # Pack the results_frame after adding the canvas
    results_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Function to trigger the search window from the main window
def open_search_window():
    create_search_window()
