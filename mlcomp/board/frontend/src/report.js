// Initialize the Vue and its plugins
import Vue from 'vue';
import MuseUI from 'muse-ui';
Vue.use(MuseUI);

// Initialize the App
import Report from './report/Report.vue';

// The Vue main application
new Vue({
  el: '#app',
  render(h) {
    return h(Report);
  }
});
