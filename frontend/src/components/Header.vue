<template>
  <header class="app-header">
    <h1>KPOP Moodify</h1>
    <button @click="toggleDarkMode" class="dark-mode-toggle">
      {{ isDarkMode ? 'Light Mode' : 'Dark Mode' }}
    </button>
    <nav>
      <router-link to="/">Home</router-link>
      <router-link to="/about">About</router-link>
    </nav>
  </header>
</template>

<script>
export default {
  name: 'Header',
  props: {
    isDarkMode: {
      type: Boolean,
      required: true
    }
  },
  methods: {
    toggleDarkMode() {
      this.$emit('update:isDarkMode', !this.isDarkMode);
    }
  }
};
</script>

<style scoped>
.app-header {
  background-color: #f8f9fa;
  padding: 20px;
  text-align: center;
}

#app.dark > .app-header {
  background-color: #343a40;
  color: white;
}

.dark-mode-toggle {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 15px;
  cursor: pointer;
  border-radius: 5px;
}

.dark-mode-toggle:hover {
  background-color: #0056b3;
}

nav {
  margin-top: 10px;
}

nav a {
  margin: 0 15px;
  text-decoration: none;
  color: #007bff;
}

nav a:hover {
  text-decoration: underline;
}
</style>