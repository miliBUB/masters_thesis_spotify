import unittest
from unittest.mock import patch, MagicMock
import json
import logging

# Import the main functions from the enrich_playlist_v2 module
from enrich_playlist_v2 import fetch_audio_features, main

class TestEnrichPlaylist(unittest.TestCase):
    def setUp(self):
        # Mock data
        self.mock_input_data = {
            "playlists": [
                {
                    "tracks": [
                        {"track_uri": "spotify:track:12345"},
                        {"track_uri": "spotify:track:67890"}
                    ]
                }
            ]
        }
        self.mock_audio_features = [
            {"id": "12345", "danceability": 0.5},
            {"id": "67890", "danceability": 0.7}
        ]
        self.mock_output_data = {
            "playlists": [
                {
                    "tracks": [
                        {"track_uri": "spotify:track:12345", "audio_features": {"id": "12345", "danceability": 0.5}},
                        {"track_uri": "spotify:track:67890", "audio_features": {"id": "67890", "danceability": 0.7}}
                    ]
                }
            ]
        }

    @patch('enrich_playlist_v2.sp.audio_features')
    @patch('enrich_playlist_v2.time.sleep', return_value=None)  # To speed up tests
    def test_fetch_audio_features(self, mock_sleep, mock_audio_features):
        mock_audio_features.return_value = self.mock_audio_features
        result = fetch_audio_features(MagicMock(), ['12345', '67890'])
        self.assertEqual(result, self.mock_audio_features)

    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data=json.dumps({
        "playlists": [
            {
                "tracks": [
                    {"track_uri": "spotify:track:12345"},
                    {"track_uri": "spotify:track:67890"}
                ]
            }
        ]
    }))
    @patch('json.dump')
    @patch('enrich_playlist_v2.sp.audio_features')
    @patch('enrich_playlist_v2.time.sleep', return_value=None)  # To speed up tests
    def test_main(self, mock_sleep, mock_audio_features, mock_json_dump, mock_open):
        mock_audio_features.return_value = [
            {"id": "12345", "danceability": 0.5},
            {"id": "67890", "danceability": 0.7}
        ]
        
        # Run the main script
        main()
        
        # Check that json.dump was called with the correct enriched data
        mock_json_dump.assert_called_once_with({
            "playlists": [
                {
                    "tracks": [
                        {"track_uri": "spotify:track:12345", "audio_features": {"id": "12345", "danceability": 0.5}},
                        {"track_uri": "spotify:track:67890", "audio_features": {"id": "67890", "danceability": 0.7}}
                    ]
                }
            ]
        }, unittest.mock.ANY, indent=2)

if __name__ == '__main__':
    unittest.main()
