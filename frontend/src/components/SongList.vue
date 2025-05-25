<template>
  <div class="song-list">
    <h2>Recommended Songs</h2>
    <ul>
      <li v-for="song in songs" :key="song.title">
        <h3>{{ song.title }}</h3>
        <p>Artist: {{ song.artist }}</p>
        <a :href="song.link" target="_blank">Listen</a>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'SongList',
  props: {
    songs: {
      type: Array,
      required: true
    }
  }
};
</script>

<style scoped>
.song-list {
  margin: 20px;
}

.song-list ul {
  list-style-type: none;
  padding: 0;
}

.song-list li {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.dark-mode .song-list li {
  background-color: #1e1e1e;
  color: #ffffff;
  box-shadow: 0 4px 6px rgba(255, 255, 255, 0.1);
}

.song-list a {
  color: #007bff;
  text-decoration: none;
}

.song-list a:hover {
  text-decoration: underline;
}
</style>