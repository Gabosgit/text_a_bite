import time
import requests
from gemini import get_nutrition

#url = "http://hackathons.masterschool.com:3030/team/getMessages/Text-a-Bite"
#headers = {"Content-Type": "application/json"}

# Dictionary to store the latest timestamp for each user
latest_timestamps = {}
def send_subscribe_message(text,user_id):
    message ="""Welcome ! Text 'Text-a-Bite qty measure food' to get nutritional value."
    """
    url =  "http://hackathons.masterschool.com:3030/sms/send"
    headers = {"Content-Type": "application/json"}
    payload = {
        "phoneNumber": user_id,
        "message": message,
    }
    try:
        response = requests.post(url,json=payload,headers=headers)
        if response.status_code == 200:
            print("Message sent successfully!")
            #print("Response:", response.json())
        else:
            print(f"Failed to send message. Status code: {response.status_code}")
            #print("Response:", response.text)
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_an_sms(text,user_id):
    print("user_id::",user_id)
    print("text::",text)
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
            print("Message sent successfully!")
            print("Response:", response.json())
        else:
            print(f"Failed to send message. Status code: {response.status_code}")
            print("Response:", response.text)
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def fetch_data():
    global latest_timestamps  # Access the global dictionary
    url = "http://hackathons.masterschool.com:3030/team/getMessages/Text-a-Bite"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()  # Parse the JSON response

            # Dictionary to store new messages
            new_messages = {}

            for user_id, messages in data.items():
                # Get the latest timestamp for this user
                last_timestamp = latest_timestamps.get(user_id, None)

                # Filter messages for this user based on the timestamp
                new_messages[user_id] = [
                    msg for msg in messages
                    if last_timestamp is None or msg["receivedAt"] > last_timestamp
                ]

                # Update the latest timestamp for this user if new messages exist
                if new_messages[user_id]:
                    latest_timestamps[user_id] = max(
                        msg["receivedAt"] for msg in new_messages[user_id]
                    )
            text = ""
            # Display the new messages
            for user_id, messages in new_messages.items():
                if messages:
                    #print(f"New messages for user {user_id}:")
                    for message in messages:
                        text = message['text']
                        #print(f"  {message['text']} received at {message['receivedAt']}")
                        if "SUBSCRIBE" in text:
                            send_subscribe_message(text,user_id)
                        # Safely split the message text
                        if "Text-a-Bite" in text:
                            split_text = text.split()
                            if len(split_text) > 1 :
                               quantity = split_text[1]
                               measure = split_text[2]
                               food = split_text[3]

                               # Use the second word as the query
                               #print(f"Fetching nutrition information for: {query}")
                               nutrition_value = get_nutrition(quantity, measure, food)
                               send_an_sms(nutrition_value,user_id)
                            else:
                               print("")
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error during request: {e}")

def main():
    while True:
        fetch_data()
        time.sleep(10)

if __name__ == "__main__":
    main()
