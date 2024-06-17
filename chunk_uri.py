import json

# Define the file paths
input_json_path = r'C:\\Users\\miliBUB\\OneDrive\\Skrivebord\\masters_thesis_spotify\\filtered_playlist.json'  # Update with your actual file path
output_json_path = r'C:\\Users\\miliBUB\\OneDrive\\Skrivebord\\masters_thesis_spotify\\chunked_uris.json'  # Use raw string to avoid unicode escape error

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

# Chunk track IDs into batches of 15
max_ids_per_request = 15
chunked_track_ids = [track_ids[i:i + max_ids_per_request] for i in range(0, len(track_ids), max_ids_per_request)]

# Save the chunked track IDs to a new JSON file
with open(output_json_path, 'w') as file:
    json.dump(chunked_track_ids, file, indent=2)

print(f'Chunked track IDs saved to {output_json_path}')
