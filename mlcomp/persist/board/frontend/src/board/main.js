// Initialize Bootstrap
import 'tether';
import 'bootstrap';

// Initialize the Vue and its plugins
import Vue from 'vue';
import VueRouter from 'vue-router';
Vue.use(VueRouter);

// Initialize the App
import Main from './comp/main.vue';
import Board from './comp/board.vue';

// The vue routes and router
const routes = [
  // List of experiments, with different filters applied
  { path: '/', component: Board },
  { path: '/active', component: Board },
  { path: '/completed', component: Board },
];
const router = new VueRouter({
  routes,
  base: '/',
  mode: 'history'
});

// The Vue main application
import store from './lib/store.js';
new Vue({
  el: '#app',
  router,
  store,
  render(h) {
    return h(Main);
  }
});

// Start to fetch the data
store.dispatch('loadStorageGroups');
