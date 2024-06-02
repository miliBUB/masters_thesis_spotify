import requests
import json

# Spotify API credentials
client_id = '524a50e02ddc42e08a83aafd479b6bea'  # Replace with your Client ID
client_secret = '3d8ae4ecd9f444219575bfafd7daf673'  # Replace with your Client Secret

# Function to get access token
def get_access_token(client_id, client_secret):
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Failed to get access token: {response.status_code} {response.text}")

# Get the access token
access_token = get_access_token(client_id, client_secret)

# Save the access token to a file
token_file_path = 'access_token.json'
with open(token_file_path, 'w') as file:
    json.dump({"access_token": access_token}, file)

print(f'Access token saved to {token_file_path}')
