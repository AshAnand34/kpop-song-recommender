<template>
  <div :class="['home', { dark: isDarkMode }]">
    <div class="mood-input">
      <MoodInput @mood-selected="handleMoodSelected" @mood-submitted="handleMoodSubmitted" />
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </div>
    <div v-if="isLoading" class="spinner">
      <div :class="['animate-spin rounded-full h-16 w-16 border-t-4 border-b-4', isDarkMode ? 'border-white' : 'border-gray-900']" class="mx-auto"></div>
    </div>
    <div class="song-list">
      <SongList v-if="paginatedSongs.length" :songs="paginatedSongs" />
      <p v-else-if="!isLoading && hasClickedSubmit" class="no-songs-message">Sorry, I couldn't find any songs for your mood.</p>
    </div>
    <div v-if="paginatedSongs.length" class="pagination-controls">
      <button @click="prevPage" :disabled="currentPage === 1">Previous</button>
      <span>Page {{ currentPage }} of {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages">Next</button>
    </div>
  </div>
</template>

<script>
import MoodInput from '../components/MoodInput.vue';
import SongList from '../components/SongList.vue';
import axios from 'axios';
import { API_CONFIG, MOOD_CONFIG, PAGINATION_CONFIG } from '../config';

export default {
  name: 'Home',
  components: {
    MoodInput,
    SongList
  },
  props: {
    isDarkMode: {
      type: Boolean,
      required: true
    }
  },
  data() {
    return {
      recommendedSongs: [],
      errorMessage: '',
      isLoading: false,
      hasClickedSubmit: false,
      currentPage: PAGINATION_CONFIG.INITIAL_PAGE,
      songsPerPage: PAGINATION_CONFIG.SONGS_PER_PAGE
    };
  },
  computed: {
    paginatedSongs() {
      const start = (this.currentPage - 1) * this.songsPerPage;
      const end = start + this.songsPerPage;
      return this.recommendedSongs.slice(start, end);
    },
    totalPages() {
      return Math.ceil(this.recommendedSongs.length / this.songsPerPage);
    }
  },
  methods: {
    async fetchRecommendations(selectedMood) {
      try {
        const response = await axios.post(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.RECOMMEND}`, {
          mood_input: selectedMood
        });
        return response.data;
      } catch (error) {
        console.error('Error fetching song recommendations:', error);
      }
    },
    async handleMoodSelected(mood) {
      console.log('Mood selected:', mood);
      this.isLoading = true; // Show the loading spinner
      this.hasClickedSubmit = true;
      this.recommendedSongs = []; // Clear the previous song list
      this.recommendedSongs = await this.fetchRecommendations(mood);
      this.currentPage = PAGINATION_CONFIG.INITIAL_PAGE; // Reset to the first page
      this.isLoading = false; // Hide the loading spinner
    },
    async handleMoodSubmitted(description) {
      if (!description || description.trim() === '') {
        console.log('Please tell us how you are feeling right now.');
        this.errorMessage = MOOD_CONFIG.DEFAULT_ERROR_MESSAGE;
        return;
      }
      this.errorMessage = ''; // Clear the error message if input is valid
      this.isLoading = true; // Show the loading spinner
      this.hasClickedSubmit = true; // Mark that the submit button was clicked
      this.recommendedSongs = []; // Clear the previous song list
      console.log('Mood description submitted:', description);
      this.recommendedSongs = await this.fetchRecommendations(description);
      this.currentPage = PAGINATION_CONFIG.INITIAL_PAGE; // Reset to the first page
      this.isLoading = false; // Hide the loading spinner
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
      }
    }
  }
};
</script>

<style scoped>
.home {
  padding: 20px;
  text-align: center;
}

.home.dark {
  background-color: #121212;
  color: #ffffff;
}

.mood-input {
  margin: 20px 0;
}

.mood-input.dark {
  background-color: #1e1e1e;
  color: #ffffff;
}

.song-list {
  margin-top: 20px;
}

.song-list.dark li {
  background: #1e1e1e;
  color: #ffffff;
  box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
}

.error-message {
  color: red;
  font-weight: bold;
  margin-top: 10px;
}

.no-songs-message {
  color: #555;
  font-size: 16px;
  margin-top: 20px;
}

.pagination-controls {
  margin-top: 20px;
}

.pagination-controls button {
  margin: 0 10px;
  padding: 5px 10px;
  font-size: 14px;
  cursor: pointer;
}
</style>