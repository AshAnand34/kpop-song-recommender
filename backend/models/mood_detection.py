from textblob import TextBlob
from collections import Counter

class MoodDetector:
    def __init__(self):
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
        """Extract emotion keywords from text using TextBlob"""
        keywords = []
        blob = TextBlob(text)

        # Extract adjectives and adverbs that might indicate mood
        for word, pos in blob.tags:
            if pos in ['JJ', 'RB']:  # Adjectives and adverbs
                for mood, related_words in self.mood_clusters.items():
                    if word.lower() in related_words:
                        keywords.append(word.lower())
                        break

        # Get sentiment to add general tone keywords
        sentiment = blob.sentiment.polarity
        if sentiment > 0.5:
            keywords.extend(['cheerful', 'upbeat', 'bright', 'positive'])
        elif sentiment < -0.5:
            keywords.extend(['melancholy', 'emotional', 'downbeat'])

        # Return unique keywords
        return list(set(keywords))

    def detect_mood(self, text):
        """Detect mood from text using TextBlob"""
        # Extract additional mood keywords
        extracted_keywords = self._extract_emotion_keywords(text)

        # Combine primary mood's keywords and extracted keywords
        primary_mood_keywords = []
        for mood, related_words in self.mood_clusters.items():
            if any(word in text.lower() for word in related_words):
                primary_mood_keywords.extend(related_words)

        all_keywords = primary_mood_keywords + extracted_keywords

        # Count frequencies and get most frequent keywords
        keyword_counts = Counter(all_keywords)
        top_keywords = [kw for kw, _ in keyword_counts.most_common(5)]

        # Determine primary mood based on the most frequent keywords
        primary_mood = max(self.mood_clusters.keys(), key=lambda mood: sum(kw in self.mood_clusters[mood] for kw in top_keywords))

        # Add primary mood if not already in keywords
        if primary_mood not in top_keywords:
            top_keywords.insert(0, primary_mood)

        # Return both the primary mood and the keywords
        return primary_mood, top_keywords
