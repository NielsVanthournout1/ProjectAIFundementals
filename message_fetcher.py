import requests
import pandas as pd

class MessageFetcher:
    def __init__(self, api_url):
        self.api_url = api_url

    def fetch_messages(self):
        try:
            response = requests.get(self.api_url)
            if response.status_code == 200:
                # Convert the messages to a DataFrame
                messages = response.json().get('messages', [])
                df = pd.DataFrame(messages)
                df['dateTime'] = pd.to_datetime(df['dateTime'])  # Convert dateTime to datetime
                return df
        except Exception as e:
            print(f"Error fetching messages: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if there's an error
