from flask import Flask, request, jsonify
from models.mood_detection import MoodDetector
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import threading
import time
import logging
from time import sleep
import nltk
import base64

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://kpop-moodify.netlify.app", "http://localhost:3000"], "methods": ["GET", "POST", "OPTIONS"]}}, supports_credentials=True)

# Load environment variables
load_dotenv()

# Initialize MoodDetector lazily
mood_detector = None

def get_mood_detector():
    global mood_detector
    if not mood_detector:
        mood_detector = MoodDetector()
    return mood_detector

# Spotify API setup
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    raise ValueError("Spotify client ID and secret must be set in environment variables.")

# Function to get Spotify access token
def get_spotify_access_token():
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    if not client_id or not client_secret:
        raise ValueError("Spotify client ID and secret must be set in environment variables.")

    # Encode client_id and client_secret in Base64
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_header}"
    }
    data = {"grant_type": "client_credentials"}

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()["access_token"]

# Refresh Spotify token manually
def refresh_spotify_token():
    global global_token_info
    while True:
        try:
            global_token_info = {"access_token": get_spotify_access_token()}
            logger.info("Spotify token refreshed.")
        except Exception as e:
            logger.error(f"Failed to refresh Spotify token: {e}")
        time.sleep(3600)  # Refresh every hour

# Start the token refresh thread
threading.Thread(target=refresh_spotify_token, daemon=True).start()

def remove_duplicates(recommendations):
    unique_songs = []
    seen_ids = set()  # Use a set for faster lookups
    for song in recommendations:
        song_id = song.get('title')
        if song_id and song_id not in seen_ids:
            unique_songs.append(song)
            seen_ids.add(song_id)
    return unique_songs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reduce the number of concurrent threads for Spotify API calls
MAX_THREADS = 5  # Limit the number of threads to reduce memory usage

def fetch_with_retries(url, headers, retries=3, backoff_factor=1):
    """Fetch a URL with retries and exponential backoff."""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL {url}: {e}")
            if attempt < retries - 1:
                sleep_time = backoff_factor * (2 ** attempt)
                logger.info(f"Retrying in {sleep_time} seconds...")
                sleep(sleep_time)
            else:
                logger.error(f"Failed to fetch URL {url} after {retries} attempts.")
                return None

# Define fetch_page to use fetch_with_retries
def fetch_page(url, headers):
    return fetch_with_retries(url, headers)

# Define fetch_artist_details to use fetch_with_retries
def fetch_artist_details(artist_id, headers):
    artist_url = f'https://api.spotify.com/v1/artists/{artist_id}'
    return fetch_with_retries(artist_url, headers)

@app.route('/recommend', methods=['POST'])
def recommend():
    # Extract mood input from the request
    mood_input = request.json.get('mood_input', 'happy')

    # Use enhanced MoodDetector to analyze the mood and extract keywords
    mood_detector_instance = get_mood_detector()
    primary_mood, mood_keywords = mood_detector_instance.detect_mood(mood_input)

    logger.info(f"Detected primary mood: {primary_mood}")
    logger.info(f"Extracted mood keywords: {mood_keywords}")

    # Ensure mood_keywords is defined and used correctly
    if not mood_keywords:
        mood_keywords = [primary_mood]

    # Build a query using the detected mood keywords
    # Limit to top 3 keywords to keep search focused
    top_keywords = mood_keywords[:3]
    query = f"{' '.join(top_keywords)} kpop"

    logger.info(f"Search query: {query}")

    # Use the global token
    access_token = global_token_info['access_token']
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Make the Spotify API call manually and handle pagination using threading
    from concurrent.futures import ThreadPoolExecutor

    urls = [f'https://api.spotify.com/v1/search?q={query}&type=track&limit=20&offset={offset}' for offset in range(0, 100, 20)]

    # Use ThreadPoolExecutor with a limited number of threads
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        results_list = list(executor.map(lambda url: fetch_page(url, headers), urls))

    songs = []
    # Use a set for artist IDs to ensure uniqueness
    artist_ids = set()
    track_items = []

    for results in results_list:
        if results is None:
            logger.warning("Skipping a failed Spotify API response.")
            continue
        logger.info(f"Spotify API response: {results}")

        for item in results.get('tracks', {}).get('items', []):
            track_items.append(item)
            artist_ids.add(item['artists'][0]['id'])  # Add to set for uniqueness

    # Convert artist_ids back to a list for further processing
    unique_artist_ids = list(artist_ids)

    # Fetch artist details in parallel with limited threads
    artist_genre_map = {}

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        artist_details_list = list(executor.map(lambda artist_id: fetch_artist_details(artist_id, headers), unique_artist_ids))

    for artist_details in artist_details_list:
        if artist_details is None:
            logger.warning("Skipping a failed artist details response.")
            continue
        artist_id = artist_details.get('id')
        if artist_id:  # Check if 'id' exists in artist_details
            artist_genre_map[artist_id] = artist_details.get('genres', [])
        else:
            logger.warning(f"Missing 'id' in artist details: {artist_details}")

    # Process tracks and filter by KPOP genre
    for item in track_items:
        artist_id = item['artists'][0]['id']
        artist_genres = artist_genre_map.get(artist_id, [])

        logger.info(f"Artist ID: {artist_id}, Genres: {artist_genres}")

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
        logger.info("No songs found with specific mood. Trying more general search.")
        generic_query = "kpop"
        generic_url = f'https://api.spotify.com/v1/search?q={generic_query}&type=track&limit=20'
        results = fetch_with_retries(generic_url, headers)
        if results:
            for item in results.get('tracks', {}).get('items', []):
                artist_id = item['artists'][0]['id']
                artist_url = f'https://api.spotify.com/v1/artists/{artist_id}'
                artist_details = fetch_with_retries(artist_url, headers)
                if artist_details:
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
    # Ensure required NLTK data is downloaded during startup
    nltk_data_packages = ["punkt", "averaged_perceptron_tagger", "wordnet"]
    for package in nltk_data_packages:
        try:
            nltk.download(package)
        except Exception as e:
            print(f"Error downloading NLTK package {package}: {e}")
    
    # Start the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)