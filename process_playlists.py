import ijson
import json
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Step 1: Define Top Jazz Musicians
top_jazz_musicians = {
    "Stan Getz",
    "Count Basie",
    "Ella Fitzgerald",
    "Billie Holiday",
    "Chet Baker",
    "Miles Davis",
}

# Define words to exclude
exclude_words = {"christmas", "xmas", "holiday"}

# Helper function to check if the playlist or track should be excluded
def should_exclude(name):
    name_lower = name.lower()
    return any(word in name_lower for word in exclude_words)

# Helper function to process and filter a chunk
def process_chunk(chunk):
    filtered_playlists = []

    for playlist in chunk:
        # Exclude playlists based on the name
        if should_exclude(playlist['name']):
            logging.info(f'Excluded playlist: {playlist["name"]}')
            continue
        
        # Check if any of the tracks should be excluded
        exclude_playlist = False
        for track in playlist['tracks']:
            if should_exclude(track['track_name']):
                exclude_playlist = True
                logging.info(f'Excluded track: {track["track_name"]} in playlist: {playlist["name"]}')
                break

        if exclude_playlist:
            continue

        # Check if any track is by the top jazz musicians
        contains_top_jazz = any(track['artist_name'] in top_jazz_musicians for track in playlist['tracks'])
        if contains_top_jazz:
            filtered_playlists.append(playlist)
            logging.info(f'Included playlist: {playlist["name"]}')

    return filtered_playlists

# Step 2: Iterate through JSON slice files
slice_dir = 'C:/Users/miliBUB/OneDrive/Skrivebord/masters_thesis_spotify/json_slices_master_dataset'  # Directory containing the JSON slice files

# Verify if the directory exists
if not os.path.exists(slice_dir):
    logging.error(f'Directory not found: {slice_dir}')
    raise FileNotFoundError(f'Directory not found: {slice_dir}')

num_slices = 1000  # Number of slices; adjust this as needed
slice_files = [f'mpd.slice.{i}-{i+999}.json' for i in range(0, num_slices * 1000, 1000)]
chunk_size = 1000
chunk_count = 0

logging.info('Starting to process slice files.')

for slice_file in slice_files:
    slice_path = os.path.join(slice_dir, slice_file)
    
    # Verify if the slice file exists
    if not os.path.exists(slice_path):
        logging.warning(f'Slice file not found: {slice_path}')
        continue

    chunk = []

    with open(slice_path, 'r') as file:
        for playlist in ijson.items(file, 'playlists.item'):
            chunk.append(playlist)
            if len(chunk) >= chunk_size:
                # Process the chunk
                filtered_playlists = process_chunk(chunk)
                # Save intermediate result
                with open(f'filtered_playlists_{chunk_count}.json', 'w') as outfile:
                    json.dump({"playlists": filtered_playlists}, outfile, indent=4)
                logging.info(f'Saved filtered playlists chunk: {chunk_count}')
                chunk = []
                chunk_count += 1

# Process any remaining items in the last chunk
if chunk:
    filtered_playlists = process_chunk(chunk)
    with open(f'filtered_playlists_{chunk_count}.json', 'w') as outfile:
        json.dump({"playlists": filtered_playlists}, outfile, indent=4)
    logging.info(f'Saved filtered playlists chunk: {chunk_count}')
    chunk = []
    chunk_count += 1

# Step 3: Combine Intermediate Results into a Final Dataset
final_playlists = []

logging.info('Combining intermediate results into final dataset.')

for i in range(chunk_count):
    with open(f'filtered_playlists_{i}.json', 'r') as infile:
        data = json.load(infile)
        final_playlists.extend(data['playlists'])
        logging.info(f'Loaded filtered playlists chunk: {i}')

with open('final_filtered_playlists.json', 'w') as final_file:
    json.dump({"playlists": final_playlists}, final_file, indent=4)

logging.info('Final filtered playlists saved.')
