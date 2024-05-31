import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Spotify API credentials
CLIENT_ID = '524a50e02ddc42e08a83aafd479b6bea'
CLIENT_SECRET = '214cbe61711f4477b4f433a9c77b22f7'

# Setup Spotify API client
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Load the final filtered playlists
with open('filtered_playlist.json', 'r') as file:
    data = json.load(file)

playlists = data['playlists']

# Function to get audio features for a list of track URIs with rate limiting and exponential backoff
def get_audio_features(track_uris):
    features = []
    for i in range(0, len(track_uris), 100):  # Spotify API allows max 100 track URIs per request
        batch = track_uris[i:i + 100]
        attempt = 0
        while True:
            try:
                features.extend(sp.audio_features(batch))
                break
            except spotipy.exceptions.SpotifyException as e:
                if e.http_status == 429:
                    attempt += 1
                    retry_after = int(e.headers.get('Retry-After', 5))  # Default retry after 5 seconds if not specified
                    logging.error(f'Spotify API rate limit exceeded. Retrying after {retry_after} seconds...')
                    time.sleep(retry_after * attempt)  # Exponential backoff
                else:
                    logging.error(f'Spotify API error: {e}')
                    raise
        time.sleep(0.34)  # Sleep for 0.34 seconds between requests to stay within the limit
    return features

# Enrich playlists with audio features
for playlist in playlists:
    track_uris = [track['track_uri'].split(":")[-1] for track in playlist['tracks']]  # Extract URI IDs for API call
    audio_features = get_audio_features(track_uris)
    
    for track, features in zip(playlist['tracks'], audio_features):
        if features:
            track.update(features)
        else:
            logging.warning(f'No audio features found for track: {track["track_uri"]}')

# Save the enriched playlists
with open('enriched_final_filtered_playlists.json', 'w') as file:
    json.dump({"playlists": playlists}, file, indent=4)

logging.info('Enriched playlists saved.')
