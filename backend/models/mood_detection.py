from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import spacy
import numpy as np
from collections import Counter
from spacy.cli import download

class MoodDetector:
    def __init__(self):
        # Download necessary NLTK data
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')

        # Lazy load SpaCy model
        self.nlp = None

        # Sentiment analyzer
        self.sia = SentimentIntensityAnalyzer()

        # Lazy load the zero-shot classifier
        self.zero_shot = None

        # Lazy load the emotion classifier
        self.emotion_classifier = None

        # Base moods and their related keywords
        self.mood_clusters = {
            'happy': ['cheerful', 'joyful', 'elated', 'upbeat', 'dance', 'bright', 'positive'],
            'sad': ['melancholy', 'gloomy', 'tearful', 'ballad', 'emotional', 'downbeat', 'slow'],
            'angry': ['frustrated', 'irritated', 'intense', 'powerful', 'aggressive', 'fierce'],
            'relaxed': ['calm', 'peaceful', 'chill', 'mellow', 'soft', 'acoustic'],
            'excited': ['enthusiastic', 'eager', 'thrilled', 'energetic', 'party', 'high-energy', 'fun'],
            'tired': ['exhausted', 'weary', 'soothing', 'slow', 'quiet', 'gentle'],
            'anxious': ['worried', 'nervous', 'uneasy', 'hopeful', 'reassuring', 'uplifting'],
            'confident': ['bold', 'strong', 'empowering', 'determined', 'affirmative']
        }

    def _load_spacy_model(self):
        if not self.nlp:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")

    def _extract_emotion_keywords(self, text):
        """Extract emotion keywords from text using various NLP techniques"""
        keywords = []

        # Use SpaCy to extract adjectives and adverbs that might indicate mood
        self._load_spacy_model()
        if self.nlp:
            doc = self.nlp(text)
            for token in doc:
                if token.pos_ in ['ADJ', 'ADV'] and not token.is_stop and len(token.text) > 2:
                    # Check if the word is semantically related to an emotion
                    for mood, related_words in self.mood_clusters.items():
                        if any(word in token.text for word in related_words):
                            keywords.append(token.text)
                            break

        # Use the emotion classifier if available
        emotion_classifier = self.get_emotion_classifier()
        if emotion_classifier:
            try:
                emotion_result = emotion_classifier(text)[0]
                emotion_label = emotion_result['label']
                # Map emotion label to appropriate keywords
                if emotion_label == 'joy':
                    keywords.extend(['happy', 'cheerful', 'upbeat'])
                elif emotion_label == 'sadness':
                    keywords.extend(['sad', 'melancholy', 'emotional'])
                elif emotion_label == 'anger':
                    keywords.extend(['angry', 'intense', 'powerful'])
                elif emotion_label == 'fear':
                    keywords.extend(['anxious', 'reassuring'])
                elif emotion_label == 'surprise':
                    keywords.extend(['excited', 'energetic'])
                # Add more emotion mappings as needed
            except Exception as e:
                print(f"Error with emotion classifier: {e}")

        # Get sentiment to add general tone keywords
        sentiment = self.sia.polarity_scores(text)
        if sentiment['compound'] > 0.5:
            keywords.extend(['cheerful', 'upbeat', 'bright', 'positive'])
        elif sentiment['compound'] < -0.5:
            keywords.extend(['melancholy', 'emotional', 'downbeat'])

        # Return unique keywords
        return list(set(keywords))

    def detect_mood(self, text):
        """
        Detect mood from text using various NLP approaches,
        returning both a primary mood category and relevant mood keywords
        """
        # First, try standard classification to get a primary mood
        candidate_moods = list(self.mood_clusters.keys())
        result = self.get_zero_shot_classifier()(text, candidate_labels=candidate_moods)
        primary_mood = result['labels'][0]  # The mood with highest confidence
        confidence = result['scores'][0]

        # Extract additional mood keywords
        extracted_keywords = self._extract_emotion_keywords(text)

        # Combine primary mood's keywords and extracted keywords
        primary_mood_keywords = self.mood_clusters.get(primary_mood, [])
        all_keywords = primary_mood_keywords + extracted_keywords

        # Count frequencies and get most frequent keywords
        keyword_counts = Counter(all_keywords)
        top_keywords = [kw for kw, _ in keyword_counts.most_common(5)]

        # Add primary mood if not already in keywords
        if primary_mood not in top_keywords:
            top_keywords.insert(0, primary_mood)

        # Return both the primary mood and the keywords
        return primary_mood, top_keywords

    # Lazy load zero-shot classifier when needed
    def get_zero_shot_classifier(self):
        if self.zero_shot is None:
            self.zero_shot = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1")
        return self.zero_shot

    # Lazy load emotion classifier when needed
    def get_emotion_classifier(self):
        if self.emotion_classifier is None:
            model_name = "bhadresh-savani/distilbert-base-uncased-emotion"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.emotion_classifier = pipeline("text-classification", model=model_name, tokenizer=self.tokenizer)
        return self.emotion_classifier
