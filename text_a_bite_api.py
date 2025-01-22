import time
from datetime import datetime

import requests
from dateutil.parser import isoparse

from gemini import get_nutrition

# Dictionary to store the latest timestamp for each user
latest_timestamps = {}


def send_subscribe_message(user_id):
    """Send a subscription welcome message."""
    message = "Welcome! Text 'Text-a-Bite qty measure food' to get nutritional value."
    send_an_sms(message, user_id)


def send_an_sms(text, user_id):
    """Send an SMS to the specified user."""
    url = "http://hackathons.masterschool.com:3030/sms/send"
    headers = {"Content-Type": "application/json"}
    payload = {
        "phoneNumber": user_id,
        "message": text,
        "sender": ""
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"Message sent successfully to {user_id}")
        else:
            print(f"Failed to send message to {user_id}. Status code: {response.status_code}")
        return response
    except Exception as e:
        print(f"An error occurred while sending message to {user_id}: {e}")
        return None


def fetch_data():
    """Fetch new messages and process them."""
    global latest_timestamps
    url = "http://hackathons.masterschool.com:3030/team/getMessages/Text-a-Bite"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()

            # Log the raw response for debugging
            #print("API Response:", data)

            # Dictionary to store new messages
            new_messages = {}

            for user_id, messages in data.items():
                # Get the latest timestamp for this user
                last_timestamp = latest_timestamps.get(user_id, None)
                print("last_timestamp", last_timestamp)
                if last_timestamp:
                    try:
                        last_timestamp = isoparse(last_timestamp)
                    except ValueError as e:
                        print(f"Error parsing last timestamp for user {user_id}: {e}")
                        last_timestamp = None  # If parsing fails, reset to None

                # Filter messages for this user based on the timestamp
                if last_timestamp is not None:
                    new_messages[user_id] = [
                        msg for msg in messages
                        if isoparse(msg["receivedAt"]) > last_timestamp
                    ]
                else:
                    # Initialize last_timestamp with the most recent message's receivedAt
                    if messages:
                        latest_message = max(messages, key=lambda x: isoparse(x["receivedAt"]))
                        last_timestamp = isoparse(latest_message["receivedAt"])
                        latest_timestamps[user_id] = last_timestamp.isoformat()
                        new_messages[user_id] = []

                # Update the latest timestamp for this user if new messages exist
                if new_messages[user_id]:
                    latest_timestamps[user_id] = max(
                        isoparse(msg["receivedAt"]) for msg in new_messages[user_id]
                    ).isoformat()
            print("med", new_messages)
            # Process new messages
            for user_id, messages in new_messages.items():
                for message in messages:
                    text = message['text']
                    if "SUBSCRIBE" in text.upper():
                        send_subscribe_message(user_id)
                    elif "Text-a-Bite" in text:
                        cleaned_text = text.replace("Text-a-Bite", "").strip()
                        nutrition_value = get_nutrition(cleaned_text)
                        print(f"Preparing to send message to {user_id} with data: {messages}")
                        send_an_sms(nutrition_value, user_id)
                        print(f"Message sent successfully to {user_id}")

        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error during data fetch: {e}")


def main():
    """Main loop to fetch and process messages periodically."""
    while True:
        fetch_data()
        time.sleep(10)


if __name__ == "__main__":
    main()
