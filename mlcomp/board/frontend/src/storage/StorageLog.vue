<template>
  <div class="main-wrapper">
    <!-- the loading progress -->
    <delayed-progress-bar :loading="isLoading"></delayed-progress-bar>

    <!-- the loading error message -->
    <div v-if="errorMessage" class="main-content error">
      Failed to load logs: {{ errorMessage }}.
    </div>

    <!-- the main list group -->
    <div v-if="!errorMessage" class="main-content logs">
      <pre>{{ logs }}</pre>
    </div>
  </div>
</template>

<script>
  import $ from 'jquery';
  import { eventBus } from '../lib/eventBus.js';
  import DelayedProgressBar from '../comp/DelayedProgressBar.vue';

  export default {
    components: {
      DelayedProgressBar
    },

    props: ['rootUrl'],

    data() {
      return {
        isLoading: false,
        errorMessage: null,
        logs: null,
      }
    },

    methods: {
      loadLogs() {
        const self = this;
        self.isLoading = true;

        // start to load the data
        $.ajax({
          url: self.rootUrl + 'console.log',
          dataType: 'text',
          cache: false,
          success: function (data) {
            self.logs = data;
            self.errorMessage = null;
            self.isLoading = false;
          },
          error: function (e) {
            self.logs = null;
            self.errorMessage = e.statusText;
            console.log(`error when loading logs: ${e.statusText}`);
            self.isLoading = false;
          }
        });
      }
    },

    mounted() {
      this.loadLogs();
      this.onHandleReload = (autoReload) => this.loadLogs();
      eventBus.$on('handleReload', this.onHandleReload);
    },

    updated() {
      const elem = this.$el;
      const height = $(elem).children('.main-content').height();
      if (height) {
        elem.scrollTop = height;
      }
    },

    destroyed() {
      eventBus.$off('handleReload', this.onHandleReload);
    },
  }
</script>

<style lang="scss" scoped>
  .main-wrapper {
    height: 100%;
    overflow: auto;
  }
  .main-content {
    padding: 5px 10px;
  }
</style>
