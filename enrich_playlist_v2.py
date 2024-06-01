from spotipy.oauth2 import SpotifyClientCredentials
import json
import spotipy
import time
import sys

# Define the file paths
input_json_path = r'C:\\Users\\miliBUB\\OneDrive\\Skrivebord\\masters_thesis_spotify\\filtered_playlist.json'  
output_json_path = r'C:\\Users\\miliBUB\\OneDrive\\Skrivebord\\masters_thesis_spotify\\enriched_playlist.json'  # Use raw string to avoid unicode escape error

# Spotify API credentials
client_id = '524a50e02ddc42e08a83aafd479b6bea'  # Replace with your Client ID
client_secret = '214cbe61711f4477b4f433a9c77b22f7'  # Replace with your Client Secret

# Initialize spotipy client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

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

# Spotify API allows up to 100 IDs per request, set to 80 to not get 429 error
max_ids_per_request = 80
audio_features = []

# Function to handle rate limits and retries
def fetch_audio_features(sp, batch_ids):
    retries = 5
    for i in range(retries):
        try:
            features = sp.audio_features(batch_ids)
            return features
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:
                print("Rate limit exceeded. Waiting to retry...")
                time.sleep((i + 1) * 2)  # Exponential backoff
            else:
                print(f"Error fetching audio features: {e}")
                raise
    return []

# Make API requests in batches with rate limiting
for i in range(0, len(track_ids), max_ids_per_request):
    batch_ids = track_ids[i:i + max_ids_per_request]
    features = fetch_audio_features(sp, batch_ids)
    audio_features.extend(features)
    
    # Sleep to respect rate limit
    time.sleep(0.6)  # Adjusted to handle around 100 requests per minute

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
