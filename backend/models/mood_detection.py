from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
import spacy
import numpy as np
from collections import Counter

class MoodDetector:
    def __init__(self):
        # Download necessary NLTK data
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')
            
        # Load SpaCy for NLP processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # If model is not installed, download it
            try:
                spacy.cli.download("en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
            except:
                self.nlp = None
                print("SpaCy model could not be loaded. Using fallback options.")
        
        # Sentiment analyzer
        self.sia = SentimentIntensityAnalyzer()
        
        # Zero-shot classifier for more complex mood detection
        self.zero_shot = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        
        # Emotion classifier
        try:
            model_name = "j-hartmann/emotion-english-distilroberta-base"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.emotion_classifier = pipeline("text-classification", model=model_name, tokenizer=self.tokenizer)
        except:
            self.emotion_classifier = None
            print("Emotion classifier could not be loaded. Using fallback options.")
        
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
    
    def _extract_emotion_keywords(self, text):
        """Extract emotion keywords from text using various NLP techniques"""
        keywords = []
        
        # Use SpaCy to extract adjectives and adverbs that might indicate mood
        if self.nlp:
            doc = self.nlp(text)
            for token in doc:
                if token.pos_ in ['ADJ', 'ADV'] and not token.is_stop and len(token.text) > 2:
                    # Check if the word is semantically related to an emotion
                    for mood, related_words in self.mood_clusters.items():
                        for word in related_words:
                            similarity = self.nlp(token.text).similarity(self.nlp(word))
                            if similarity > 0.5:  # If words are semantically similar
                                keywords.append(token.text)
                                break
        
        # Use the emotion classifier if available
        if self.emotion_classifier:
            try:
                emotion_result = self.emotion_classifier(text)[0]
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
        result = self.zero_shot(text, candidate_labels=candidate_moods)
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

# Example usage
if __name__ == "__main__":
    detector = MoodDetector()
    user_input = "I'm feeling really energetic and ready to dance all night!"
    primary_mood, keywords = detector.detect_mood(user_input)
    print(f"Primary mood: {primary_mood}")
    print(f"Mood keywords: {keywords}")