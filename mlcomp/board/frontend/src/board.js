// Initialize the Vue and its plugins
import Vue from 'vue';
import MuseUI from 'muse-ui';
Vue.use(MuseUI);

// Initialize the App
import Board from './board/Board.vue';

// The Vue main application
new Vue({
  el: '#app',
  render(h) {
    return h(Board);
  }
});
