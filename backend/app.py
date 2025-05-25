from flask import Flask, request, jsonify
from models.mood_detection import MoodDetector
from flask_cors import CORS
from dotenv import load_dotenv
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import requests
import threading
import time

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

# Preload the MoodDetector model
mood_detector = MoodDetector()

# Spotify API setup
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    raise ValueError("Spotify client ID and secret must be set in environment variables.")

# Initialize Spotify client
spotify = Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Global variable to store the Spotify token
global_token_info = None

def refresh_spotify_token():
    global global_token_info
    while True:
        global_token_info = spotify.client_credentials_manager.get_access_token()
        if not global_token_info:
            raise ValueError("Failed to obtain Spotify API token.")
        print("Spotify token refreshed.")
        time.sleep(3600)  # Refresh every hour

# Start the token refresh thread
threading.Thread(target=refresh_spotify_token, daemon=True).start()

def remove_duplicates(recommendations):
    unique_songs = []
    seen_ids = set()
    for song in recommendations:
        song_id = song.get('title')
        if song_id and song_id not in seen_ids:
            unique_songs.append(song)
            seen_ids.add(song_id)
    return unique_songs

@app.route('/recommend', methods=['POST'])
def recommend():
    # Extract mood input from the request
    mood_input = request.json.get('mood_input', 'happy')

    # Use enhanced MoodDetector to analyze the mood and extract keywords
    primary_mood, mood_keywords = mood_detector.detect_mood(mood_input)
    
    print(f"Detected primary mood: {primary_mood}")
    print(f"Extracted mood keywords: {mood_keywords}")

    # Build a query using the detected mood keywords
    # Limit to top 3 keywords to keep search focused
    top_keywords = mood_keywords[:3]
    query = f"{' '.join(top_keywords)} kpop"
    
    print(f"Search query: {query}")

    # Use the global token
    access_token = global_token_info['access_token']
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Make the Spotify API call manually and handle pagination using threading
    from concurrent.futures import ThreadPoolExecutor

    def fetch_page(url):
        response = requests.get(url, headers=headers)
        return response.json()

    urls = [f'https://api.spotify.com/v1/search?q={query}&type=track&limit=20&offset={offset}' for offset in range(0, 100, 20)]

    with ThreadPoolExecutor() as executor:
        results_list = list(executor.map(fetch_page, urls))

    songs = []
    artist_ids = []
    track_items = []

    for results in results_list:
        print(f"Spotify API response: {results}")

        for item in results['tracks']['items']:
            track_items.append(item)
            artist_ids.append(item['artists'][0]['id'])  # Collect artist IDs

    # Fetch artist details in parallel using threading
    def fetch_artist_details(artist_id):
        artist_url = f'https://api.spotify.com/v1/artists/{artist_id}'
        artist_response = requests.get(artist_url, headers=headers)
        return artist_response.json()

    unique_artist_ids = list(set(artist_ids))  # Remove duplicate artist IDs
    artist_genre_map = {}

    with ThreadPoolExecutor() as executor:
        artist_details_list = list(executor.map(fetch_artist_details, unique_artist_ids))

    for artist_details in artist_details_list:
        artist_id = artist_details.get('id')
        if artist_id:  # Check if 'id' exists in artist_details
            artist_genre_map[artist_id] = artist_details.get('genres', [])
        else:
            app.logger.warning(f"Missing 'id' in artist details: {artist_details}")

    # Process tracks and filter by KPOP genre
    for item in track_items:
        artist_id = item['artists'][0]['id']
        artist_genres = artist_genre_map.get(artist_id, [])

        print(f"Artist ID: {artist_id}, Genres: {artist_genres}")

        # Check if 'k-pop' is in the artist's genres
        if 'k-pop' in artist_genres:
            songs.append({
                'title': item['name'],
                'artist': ', '.join(artist['name'] for artist in item['artists']),
                'link': item['external_urls']['spotify'],
                'mood': primary_mood  # Include the detected mood
            })

    # If no songs found, try a more generic search
    if not songs:
        print("No songs found with specific mood. Trying more general search.")
        generic_query = "kpop"
        generic_url = f'https://api.spotify.com/v1/search?q={generic_query}&type=track&limit=20'
        response = requests.get(generic_url, headers=headers)
        results = response.json()
        
        for item in results['tracks']['items']:
            artist_id = item['artists'][0]['id']
            artist_url = f'https://api.spotify.com/v1/artists/{artist_id}'
            artist_response = requests.get(artist_url, headers=headers)
            artist_details = artist_response.json()
            artist_genres = artist_details.get('genres', [])
            
            if 'k-pop' in artist_genres:
                songs.append({
                    'title': item['name'],
                    'artist': ', '.join(artist['name'] for artist in item['artists']),
                    'link': item['external_urls']['spotify'],
                    'mood': 'general'  # Generic mood
                })

    unique_songs = remove_duplicates(songs)  # Remove duplicate songs
    return jsonify(unique_songs)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the KPOP Mood AI Recommender API!"})

@app.route('/healthz')
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)