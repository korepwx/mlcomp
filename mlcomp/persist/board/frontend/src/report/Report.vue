<template>
  <div id="Report" class="page-wrapper">
    <!-- the main content -->
    <div class="main-wrapper">
      <!-- the loading progress -->
      <mu-linear-progress class="loading-progress" v-if="isLoading"></mu-linear-progress>

      <!-- the loading error message -->
      <div v-if="errorMessage" class="main-content error">
        Failed to load report: {{ errorMessage }}.
      </div>

      <!-- the main list group -->
      <div v-if="!errorMessage" class="main-content report">
        {{ reportObject }}
      </div>
    </div> <!-- div.main-wrapper -->
  </div> <!-- div.page-wrapper -->
</template>

<script>
  import { getReportObject } from '../lib/report.js';

  export default {
    props: {
      // the root url of the report, must end with '/'.
      root_url: {
        type: String,
        default: '/',
      }
    },

    data() {
      return {
        isLoading: false,
        errorMessage: null,
        reportObject: null,
      };
    },

    created() {
      this.loadReportObject();
    },

    methods: {
      loadReportObject() {
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
        getReportObject({
          url: self.root_url + 'report.json',
          success: function (report) {
            self.reportObject = report;
            self.errorMessage = null;
            console.log('loaded report.');
            clearLoadingFlag();
          },
          error: function (e) {
            self.reportObject = null;
            self.errorMessage = e;
            console.log(`error when loading report: ${e}.`);
            clearLoadingFlag();
          }
        });
      }
    }
  }
</script>

<style lang="scss" scoped>

</style>