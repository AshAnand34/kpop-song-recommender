<template>
  <div class="mood-input">
    <h2 class="mood-section-title">Select Your Mood</h2>
    <div class="mood-buttons">
      <button v-for="mood in moods" :key="mood" @click="selectMood(mood)">
        {{ mood }}
      </button>
    </div>
    <br/>
    <h2 class="mood-section-title">Or Describe Your Mood</h2>
    <div class="mood-description">
      <textarea v-model="moodDescription" placeholder="Type your mood here..."></textarea>
      <button class="mood-submit" @click="submitMood">Submit</button>
    </div>
  </div>
</template>

<script>
import { MOOD_CONFIG } from '../config';

export default {
  name: 'MoodInput',
  data() {
    return {
      moods: MOOD_CONFIG.PREDEFINED_MOODS,
      moodDescription: ''
    };
  },
  methods: {
    selectMood(mood) {
      this.$emit('mood-selected', mood);
    },
    submitMood() {
      this.$emit('mood-submitted', this.moodDescription);
    }
  }
};
</script>

<style scoped>
.mood-input {
  text-align: center;
  margin: 20px;
}

.mood-buttons button {
  margin: 5px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}

textarea {
  width: 90%;
  height: 80px;
  margin-top: 10px;
  display: block; /* Ensure textarea is a block element */
  margin-left: auto;
  margin-right: auto;
}

.mood-description button {
  margin-top: 10px; /* Add margin to separate the button from the textarea */
  display: block; /* Ensure button is a block element */
  margin-left: auto;
  margin-right: auto;
}
</style>