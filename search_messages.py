from message_fetcher import MessageFetcher  # Import MessageFetcher
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry  # Import DateEntry for the date picker
import pandas as pd
import requests

# Derived class to handle searching functionality
class SearchableMessageFetcher(MessageFetcher):
    def __init__(self, api_url):
        super().__init__(api_url)

    def search_messages(self, user, selected_date, word):
        # Fetch all messages into a pandas DataFrame
        df = self.fetch_messages()

        if not df.empty:
            # Filter by user (exact match)
            if user:
                df = df[df['user'].str.lower() == user.lower()]  # Exact match (case-insensitive)

            # Filter by date if selected_date is provided
            if selected_date:
                # Filter by the selected date
                df = df[df['dateTime'].dt.date == selected_date]

            # Filter by word in the message
            if word:
                # Filter by word in the message content
                df = df[df['message'].str.contains(word, case=False, na=False)]  # Case-insensitive search

            return df
        else:
            return pd.DataFrame()  # Return empty DataFrame if no messages are found

# Function to open search window and search messages
def open_search_window():
    def search_messages():
        user = user_entry.get()
        selected_date = date_picker.get_date() if date_var.get() else None  # Only use date if checkbox is selected
        word = word_entry.get()

        # Create an instance of the derived class to handle search
        searchable_message_fetcher = SearchableMessageFetcher('https://www.chatforumaiprogramming.be/api.php')

        # Search messages using the search functionality from the derived class
        df = searchable_message_fetcher.search_messages(user, selected_date, word)

        # Display the search results
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

    search_window = tk.Toplevel()
    search_window.title("Search Messages")
    search_window.geometry("500x400")
    
    # User input field
    tk.Label(search_window, text="Enter User Name:").pack(pady=5)
    global user_entry
    user_entry = tk.Entry(search_window)
    user_entry.pack(pady=5)
    
    # Date picker for date selection
    global date_var
    date_var = tk.BooleanVar(value=True)  # Track if the date filter is enabled

    tk.Label(search_window, text="Select Date (Leave blank to ignore):").pack(pady=5)
    date_checkbox = tk.Checkbutton(search_window, text="Filter by Date", variable=date_var)
    date_checkbox.pack(pady=5)

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