import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import './assets/output.css'; // Use the processed Tailwind CSS output

const app = createApp(App);
app.use(router);
app.mount('#app');