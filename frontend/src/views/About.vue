<template>
  <div class="about">
    <div class="content">
      <h1>About KPOP Mood AI Recommender</h1>
      <p>
        The KPOP Mood AI Recommender is a fun and easy-to-use app that suggests KPOP songs based on how you're feeling.
        Whether you're happy, sad, relaxed, or full of energy, this app will find songs that match your mood.
        Just tell us how you're feeling, and we'll do the rest! The app uses smart technology to understand your emotions and pick the perfect songs for you.
        Discover new music and enjoy a personalized playlist that resonates with your feelings!
      </p>
    </div>
  </div>
</template>

<script>
import Header from '@/components/Header.vue';

export default {
  name: 'About',
  components: {
    Header
  }
};
</script>

<style scoped>
.about {
  text-align: center;
  padding: 20px;
  background: linear-gradient(to bottom, #fad0c4, #ff9a9e);
  color: #333;
}

.dark-mode .about {
  background: linear-gradient(to bottom, #1e1e1e, #343a40);
}

.content {
  max-width: 800px;
  margin: 0 auto;
  text-align: left;
  line-height: 1.6;
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.dark-mode .content {
  background: #2c2c2c;
  color: #f8f9fa;
}

.content h1 {
  text-align: center;
  margin-bottom: 20px;
  color: #ff6f61;
}
</style>