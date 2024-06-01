from spotipy.oauth2 import SpotifyClientCredentials
import json
import spotipy
import time
import logging

# Define the file paths
input_json_path = r'C:\\Users\\miliBUB\\OneDrive\\Skrivebord\\masters_thesis_spotify\\filtered_playlist.json'  # Update with your actual file path
output_json_path = r'C:\\Users\\miliBUB\\OneDrive\\Skrivebord\\masters_thesis_spotify\\enriched_playlist.json'  # Use raw string to avoid unicode escape error

# Spotify API credentials
client_id = '524a50e02ddc42e08a83aafd479b6bea'  # Replace with your Client ID
client_secret = '214cbe61711f4477b4f433a9c77b22f7'  # Replace with your Client Secret

# Initialize spotipy client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Spotify API allows up to 100 IDs per request, set to 15 as per the requirement
max_ids_per_request = 15
audio_features = []

# Function to handle rate limits and retries
def fetch_audio_features(sp, batch_ids):
    retries = 5
    backoff_time = 2  # Initial backoff time in seconds
    for i in range(retries):
        try:
            features = sp.audio_features(batch_ids)
            return features
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(e.headers.get('Retry-After', backoff_time)) if 'Retry-After' in e.headers else backoff_time
                logger.warning(f"Rate limit exceeded. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)
                backoff_time = max(backoff_time * 2, retry_after)  # Exponential backoff or use Retry-After if greater
            else:
                logger.error(f"Error fetching audio features: {e}")
                raise
    logger.error(f"Max retries reached for batch_ids: {batch_ids}")
    return []

# Make API requests in batches with rate limiting
for i in range(0, len(track_ids), max_ids_per_request):
    batch_ids = track_ids[i:i + max_ids_per_request]
    features = fetch_audio_features(sp, batch_ids)
    audio_features.extend(features)
    
    # Sleep to respect rate limit
    time.sleep(1)  # Ensure we don't exceed the rate limit of 20 requests per second

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

logger.info(f'Enriched data saved to {output_json_path}')
