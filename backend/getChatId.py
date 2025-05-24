import requests
import datetime

TENANT_ID = "C"
CLIENT_ID = "B"
CLIENT_SECRET = "A"


def get_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def get_chats(access_token):
    url = "https://graph.microsoft.com/v1.0/users/d6dc15f6-47e2-4786-a1d6-7b88d7bcf9dd/chats"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["value"]


def get_messages(access_token, chat_id):
    url = f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def main():
    token = get_token()
    resp = get_messages(token, "19:c85ccb7c68164f918361586431268deb@thread.v2")
    messages = resp.get("value", [])
    # filter for only today messages
    today = datetime.datetime.now().date()

    fetch_more = datetime.datetime.fromisoformat(messages[0]["createdDateTime"]).date() < today

    messages = [
        message for message in messages
        if datetime.datetime.fromisoformat(message["createdDateTime"]).date() == today
    ]

    if fetch_more:
        print("Fetching more messages...")
        next_link = resp.get("@odata.nextLink")
        while fetch_more:
            response = requests.get(next_link, headers={"Authorization": f"Bearer {token}"})
            response.raise_for_status()
            next_messages = response.json().get("value", [])
            fetch_more = datetime.datetime.fromisoformat(next_messages[0]["createdDateTime"]).date() < today
            messages.extend([
                message for message in next_messages
                if datetime.datetime.fromisoformat(message["createdDateTime"]).date() == today
            ])
            next_link = response.json().get("@odata.nextLink")


    return messages


if __name__ == "__main__":
    main()