import json
import requests
import time
import os
# Define the file paths
input_json_path = r'C:\\Users\\miliBUB\\OneDrive\\Skrivebord\\masters_thesis_spotify\\filtered_playlist.json'  # Update with your actual file path
output_json_path = r'C:\\Users\\miliBUB\\OneDrive\\Skrivebord\\masters_thesis_spotify\\enriched_playlist.json'  # Use raw string to avoid unicode escape error
token_file_path = 'access_token.json'

# Function to read access token from file
def read_access_token(token_file_path):
    with open(token_file_path, 'r') as file:
        return json.load(file)['access_token']

# Function to get audio features from Spotify API



def get_audio_features(access_token, track_ids, output_file='audio_features.json'):
    base_url = 'https://api.spotify.com/v1/audio-features'
    max_ids_per_request = 80
    audio_features = []
    headers = {'Authorization': f'Bearer {access_token}'}

    # Check if output file exists and load progress
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            audio_features = json.load(f)
        fetched_track_ids = {feature['id'] for feature in audio_features if feature}
        remaining_track_ids = [track_id for track_id in track_ids if track_id not in fetched_track_ids]
    else:
        remaining_track_ids = track_ids

    for i in range(0, len(remaining_track_ids), max_ids_per_request):
        batch_ids = remaining_track_ids[i:i + max_ids_per_request]
        ids_param = ','.join(batch_ids)
        
        while True:
            response = requests.get(f'{base_url}?ids={ids_param}', headers=headers)

            if response.status_code == 200:
                audio_features.extend(response.json()['audio_features'])
                print(f'Successfully fetched audio features for batch {i // max_ids_per_request + 1}')
                
                # Save progress to file
                with open(output_file, 'w') as f:
                    json.dump(audio_features, f)
                
                time.sleep(2)  # Sleep for 2 seconds after each successful request
                break
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 1))  # Get the retry-after value from headers, default to 1 second if not available
                print(f'Rate limit exceeded, sleeping for {retry_after} seconds')
                time.sleep(retry_after)
            else:
                print(f'Error fetching audio features: {response.status_code} {response.text}')
                break

    return audio_features

# Example usage
# access_token = 'your_spotify_access_token'
# track_ids = ['track_id_1', 'track_id_2', ...]  # List of up to 80 track IDs
# features = get_audio_features(access_token, track_ids)



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
