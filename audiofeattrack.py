import json
import os

def count_collected_ids(output_file='audio_features.json'):
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            audio_features = json.load(f)
        collected_ids = {feature['id'] for feature in audio_features if feature}
        return len(collected_ids)
    else:
        print(f'File {output_file} does not exist.')
        return 0

# Example usage
output_file = 'audio_features.json'
collected_count = count_collected_ids(output_file)
print(f'Number of unique track IDs collected so far: {collected_count}')
