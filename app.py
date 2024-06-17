
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from dtaidistance import dtw
import joblib
import random
# Load the models and data
scaler = joblib.load('scaler.pkl')
label_encoder = joblib.load('label_encoder.pkl')
playlists = joblib.load('playlists.pkl')

# Load the dataset to get the song features
file_path = 'enriched_playlist_v2.csv'
data = pd.read_csv(file_path)

# Normalize the features
X = data.drop(columns=['playlist_id', 'track_id', 'track_name', 'artist_name', 'num_followers'])
X_scaled = scaler.fit_transform(X)

# Function to fetch a random song's normalized features
def get_random_song_features(data, X_scaled):
    random_index = random.randint(0, len(data) - 1)
    random_song_features = X_scaled[random_index]
    return random_song_features

# Function to compute DTW distance
def compute_dtw_distance(song_features, playlist_features):
    distances = []
    for playlist_song in playlist_features:
        distance = dtw.distance(song_features, playlist_song)
        distances.append(distance)
    return np.mean(distances)

# Function to find the best matching playlists based on DTW distance
def find_best_matching_playlists(song_features, playlists, num_neighbors=10):
    dtw_distances = {}
    for playlist_id, playlist_features in playlists.items():
        dtw_distance = compute_dtw_distance(song_features, playlist_features)
        dtw_distances[playlist_id] = dtw_distance
    
    sorted_playlists = sorted(dtw_distances, key=dtw_distances.get)[:num_neighbors]
    return sorted_playlists

# Streamlit app
st.title('Playlist Recommendation System')

# Button to get a random song ID
if st.button('Get Random Song ID'):
    example_song_features = get_random_song_features(data, X_scaled)
    st.write(f'Random Song Features: {example_song_features}')

    # Find the nearest playlists using DTW
    recommended_playlists = find_best_matching_playlists(example_song_features, playlists)

    # Map the best matching playlists indices to original playlist IDs
    recommended_playlists_ids = label_encoder.inverse_transform(recommended_playlists)
    
    st.write(f'Recommended Playlists:')
    st.write(recommended_playlists_ids)

# Input for song ID
song_id = st.text_input('Enter Song ID:')

if song_id:
    try:
        # Find the song features based on song ID
        song_features = data[data['track_id'] == int(song_id)].drop(columns=['playlist_id', 'track_id', 'track_name', 'artist_name', 'num_followers']).values
        if len(song_features) == 0:
            st.write("Song ID not found.")
        else:
            song_features = scaler.transform(song_features)[0]  # Normalize the song features

            # Find the nearest playlists using DTW
            recommended_playlists = find_best_matching_playlists(song_features, playlists)

            # Map the best matching playlists indices to original playlist IDs
            recommended_playlists_ids = label_encoder.inverse_transform(recommended_playlists)
            
            st.write(f'Recommended Playlists:')
            st.write(recommended_playlists_ids)
    except ValueError:
        st.write("Invalid Song ID entered. Please enter a valid numeric Song ID.")