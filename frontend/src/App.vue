<template>
  <div id="app" :class="{ dark: isDarkMode }" class="flex flex-col min-h-screen">
    <Header :isDarkMode="isDarkMode" @update:isDarkMode="toggleDarkMode" />
    <router-view :isDarkMode="isDarkMode" class="flex-grow" />
  </div>
</template>

<script>
import Header from './components/Header.vue';

export default {
  name: 'App',
  components: {
    Header
  },
  data() {
    return {
      isDarkMode: false
    };
  },
  methods: {
    toggleDarkMode(newMode) {
      this.isDarkMode = newMode;
      document.body.classList.toggle('dark-mode', this.isDarkMode);
    }
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

#app.dark {
  background-color: #121212;
  color: #ffffff;
}
</style>