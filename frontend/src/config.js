/**
 * Application Configuration
 * This file contains centralized configuration values for the application
 */

// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.VUE_APP_API_URL || 'http://localhost:5000',
  ENDPOINTS: {
    RECOMMEND: '/recommend'
  }
};

// Mood Configuration
export const MOOD_CONFIG = {
  PREDEFINED_MOODS: [
    'Happy 😊',
    'Sad 😢',
    'Chill 😌',
    'Energetic 🔥'
  ],
  DEFAULT_ERROR_MESSAGE: 'Please tell us how you are feeling right now.'
};

// Pagination Configuration
export const PAGINATION_CONFIG = {
  SONGS_PER_PAGE: 10,
  INITIAL_PAGE: 1
};
