import json
import requests

# Define the file paths
input_json_path = r'C:\Users\miliBUB\OneDrive\Skrivebord\masters_thesis_spotify\filtered_playlist.json'  # Use raw string to avoid unicode escape error
output_json_path = r'C:\Users\miliBUB\OneDrive\Skrivebord\masters_thesis_spotify\enriched_playlist.json'  # Use raw string to avoid unicode escape error

# Spotify API credentials
client_id = '524a50e02ddc42e08a83aafd479b6bea'  # Replace with your Client ID
client_secret = '214cbe61711f4477b4f433a9c77b22f7'  # Replace with your Client Secret

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

# Read the input JSON file to get track IDs
with open(input_json_path, 'r') as file:
    data = json.load(file)

# Extract track IDs from all playlists
track_ids = []
for playlist in data['playlists']:
    for track in playlist['tracks']:
        track_uri = track['track_uri']
        track_id = track_uri.split(':')[-1]  # Extract the track ID from the URI
        track_ids.append(track_id)

# Spotify API settings
base_url = 'https://api.spotify.com/v1/audio-features'

# Spotify API allows up to 100 IDs per request
max_ids_per_request = 100
audio_features = []

# Make API requests in batches
for i in range(0, len(track_ids), max_ids_per_request):
    batch_ids = track_ids[i:i + max_ids_per_request]
    ids_param = ','.join(batch_ids)
    response = requests.get(
        f'{base_url}?ids={ids_param}',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    if response.status_code == 200:
        audio_features.extend(response.json()['audio_features'])
    else:
        print(f'Error fetching audio features: {response.status_code} {response.text}')

# Create a dictionary of audio features for easy lookup
audio_features_dict = {feature['id']: feature for feature in audio_features if feature}

# Enrich original data with audio features
for playlist in data['playlists']:
    for track in playlist['tracks']:
        track_id = track['track_uri'].split(':')[-1]  # Extract the track ID from the URI
        if track_id in audio_features_dict:
            track['audio_features'] = audio_features_dict[track_id]

# Save the enriched data to a new JSON file
with open(output_json_path, 'w') as file:
    json.dump(data, file, indent=2)

print(f'Enriched data saved to {output_json_path}')
