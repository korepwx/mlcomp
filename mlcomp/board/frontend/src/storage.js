// Initialize the Vue and its plugins
import Vue from 'vue';
import VueRouter from 'vue-router';
import MuseUI from 'muse-ui';
Vue.use(VueRouter);
Vue.use(MuseUI);

// Initialize the App
import Storage from './storage/Storage.vue';
import StorageBrowse from './storage/StorageBrowse.vue';
import StorageInfo from './storage/StorageInfo.vue';
import StorageReport from './storage/StorageReport.vue';
import StorageLog from './storage/StorageLog.vue';

// The vue routes and router
const routes = [
  { path: '/', component: StorageInfo },
  { path: '/report/:name', component: StorageReport },
  { path: '/browse/*', component: StorageBrowse },
  { path: '/console/', component: StorageLog },
];
const router = new VueRouter({
  routes,
  base: window.root_url,
  mode: 'history',
});

// The Vue main application
new Vue({
  el: '#app',
  router,
  render(h) {
    return h(Storage);
  }
});
