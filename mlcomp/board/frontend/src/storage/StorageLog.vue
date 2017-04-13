<template>
  <div>
    <!-- the loading progress -->
    <mu-linear-progress class="loading-progress" v-if="isLoading"></mu-linear-progress>

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

  export default {
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

        // show the loading flag if the resource cannot be retrieved within half a second
        const loadingFlag = [true];
        const showLoadingAfterHalfSecond = setInterval(function() {
          self.isLoading = loadingFlag[0];
          clearInterval(showLoadingAfterHalfSecond);
        }, 500);

        function clearLoadingFlag() {
          loadingFlag[0] = false;
          clearInterval(showLoadingAfterHalfSecond);
          self.isLoading = false;
        }

        // start to load the data
        $.ajax({
          url: self.rootUrl + 'console.log',
          dataType: 'text',
          cache: false,
          success: function (data) {
            self.logs = data;
            self.errorMessage = null;
            clearLoadingFlag();
          },
          error: function (e) {
            self.logs = null;
            self.errorMessage = e.statusText;
            console.log(`error when loading logs: ${e.statusText}`);
            clearLoadingFlag();
          }
        });
      }
    },

    mounted() {
      this.loadLogs();
    },
  }
</script>