// Initialize the Vue and its plugins
import Vue from 'vue';
import VueRouter from 'vue-router';
import MuseUI from 'muse-ui';
Vue.use(VueRouter);
Vue.use(MuseUI);

// Initialize the App
import Main from './App.vue';
import Board from './board/Board.vue';

// The vue routes and router
const routes = [
  // List of experiments, with different filters applied
  { path: '/', component: Board },
];
const router = new VueRouter({
  routes,
  base: '/',
  mode: 'history'
});

// The Vue main application
new Vue({
  el: '#app',
  router,
  render(h) {
    return h(Main);
  }
});
