import json
import requests
import time

# Define the file paths
input_json_path = r'C:\\Users\\miliBUB\\OneDrive\\Skrivebord\\masters_thesis_spotify\\filtered_playlist.json'  # Update with your actual file path
output_json_path = r'C:\\Users\\miliBUB\\OneDrive\\Skrivebord\\masters_thesis_spotify\\enriched_playlist.json'  # Use raw string to avoid unicode escape error
token_file_path = 'access_token.json'

# Function to read access token from file
def read_access_token(token_file_path):
    with open(token_file_path, 'r') as file:
        return json.load(file)['access_token']

# Function to get audio features from Spotify API
def get_audio_features(access_token, track_ids):
    base_url = 'https://api.spotify.com/v1/audio-features'
    max_ids_per_request = 100
    audio_features = []
    headers = {'Authorization': f'Bearer {access_token}'}

    for i in range(0, len(track_ids), max_ids_per_request):
        batch_ids = track_ids[i:i + max_ids_per_request]
        ids_param = ','.join(batch_ids)
        
        # Add a delay to respect rate limits
        time.sleep(1)
        
        response = requests.get(f'{base_url}?ids={ids_param}', headers=headers)

        if response.status_code == 200:
            audio_features.extend(response.json()['audio_features'])
            print(f'Successfully fetched audio features for batch {i // max_ids_per_request + 1}')
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))  # Get the retry-after value from headers
            print(f'Rate limit exceeded, sleeping for {retry_after} seconds')
            time.sleep(retry_after)
            response = requests.get(f'{base_url}?ids={ids_param}', headers=headers)
            if response.status_code == 200:
                audio_features.extend(response.json()['audio_features'])
                print(f'Successfully fetched audio features for batch {i // max_ids_per_request + 1} after retry')
            else:
                print(f'Error fetching audio features after retry: {response.status_code} {response.text}')
        else:
            print(f'Error fetching audio features: {response.status_code} {response.text}')

    return audio_features

# Main execution
if __name__ == "__main__":
    access_token = read_access_token(token_file_path)

    # Read the input JSON file to get track IDs
    with open(input_json_path, 'r') as file:
        data = json.load(file)

    # Extract track IDs from all playlists
    track_ids = [track['track_uri'].split(':')[-1] for playlist in data['playlists'] for track in playlist['tracks']]

    # Fetch audio features from Spotify API
    audio_features = get_audio_features(access_token, track_ids)

    # Create a dictionary of audio features for easy lookup
    audio_features_dict = {feature['id']: feature for feature in audio_features if feature}

    # Enrich original data with audio features
    for playlist in data['playlists']:
        for track in playlist['tracks']:
            track_id = track['track_uri'].split(':')[-1]
            if track_id in audio_features_dict:
                track['audio_features'] = audio_features_dict[track_id]

    # Save the enriched data to a new JSON file
    with open(output_json_path, 'w') as file:
        json.dump(data, file, indent=2)

    print(f'Enriched data saved to {output_json_path}')
