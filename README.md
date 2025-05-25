# KPOP Song Recommender

## Overview
The KPOP Song Recommender is an AI-powered web application that recommends KPOP songs based on the user's current mood. Users can input their mood through a manual selection or text input, and the application will provide a curated list of KPOP songs that align with their emotional state.

## Features
- Mood input via manual selection or text description.
- Sentiment analysis and mood classification using NLP models.
- Curated database of KPOP songs tagged with mood labels.
- Engaging and mobile-friendly user interface.

## Tech Stack
- **Frontend:** Vue.js
- **Backend:** Python (Flask or FastAPI)
- **Database:** JSON file for song storage
- **NLP Models:** Hugging Face Transformers for mood detection

### Project Structure
```
kpop-song-recommender
├── backend
│   ├── app.py
│   ├── models
│   │   └── mood_detection.py
│   └── requirements.txt
├── frontend
│   ├── public
│   │   └── index.html
│   ├── src
│   │   ├── assets
│   │   │   ├── main.css
│   │   │   ├── output.css
│   │   ├── components
│   │   │   ├── Header.vue
│   │   │   ├── MoodInput.vue
│   │   │   └── SongList.vue
│   │   ├── views
│   │   │   ├── Home.vue
│   │   │   └── About.vue
│   │   ├── App.vue
│   │   ├── config.js
│   │   ├── main.js
│   │   └── router.js
│   └── package.json
├── README.md
└── .gitignore
```

## Setup Instructions

### Backend
1. Navigate to the `backend` directory.
2. Install the required Python packages listed in `requirements.txt`.
3. Run the backend server using Flask or FastAPI.

### Frontend
1. Navigate to the `frontend` directory.
2. Install the necessary npm packages using `npm install`.
3. Start the Vue application with `npm run serve`.

## Usage
1. Open the web application in your browser.
2. Input your mood using the provided options or text input.
3. View the recommended KPOP songs based on your mood.

## Future Enhancements
- Implement facial expression or voice-based mood detection.
- Add user profiles and mood tracking history.
- Enable playlist generation and export to Spotify.
- Provide trending KPOP recommendations by mood.
- Support multiple languages (Korean/English).

## License
This project is licensed under the MIT License. Please see the LICENSE file for more details.