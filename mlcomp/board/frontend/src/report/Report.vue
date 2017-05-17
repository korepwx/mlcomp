<template>
  <!-- the main content -->
  <div class="main-wrapper">
    <!-- the loading progress -->
    <delayed-progress-bar :loading="isLoading"></delayed-progress-bar>

    <!-- the loading error message -->
    <div v-if="errorMessage" class="main-content error">
      Failed to load report: {{ errorMessage }}.
    </div>

    <!-- the main report body -->
    <div v-if="!errorMessage && reportFile" class="main-content report-body">
      <h1 v-if="reportTitle">{{ reportTitle }}</h1>
      <dispatch :rootUrl="rootUrl" :data="reportFile.data" :level="1"></dispatch>
    </div>
  </div> <!-- div.main-wrapper -->
</template>

<script>
  import { getReportObject } from '../lib/report.js';
  import { eventBus } from '../lib/eventBus.js';
  import DelayedProgressBar from '../comp/DelayedProgressBar.vue';
  import Dispatch from './elements/Dispatch.vue';

  export default {
    props: {
      // the root url of the report, must end with '/'.
      rootUrl: {
        type: String,
        default: '/',
      },

      // the directory name of the report
      reportDirName: {
        type: String,
        default: window.report_dir_name || null,
      }
    },

    components: {
      Dispatch,
      DelayedProgressBar,
    },

    data() {
      return {
        isLoading: false,
        errorMessage: null,
        reportFile: null,
      };
    },

    computed: {
      reportTitle() {
        const title = this.reportFile && this.reportFile.data && this.reportFile.data.title;
        if (title)
          return title;
        const reportDirName = this.reportDirName;
        if (reportDirName)
          return `Report “${this.reportDirName}”`;
        return null;
      }
    },

    mounted() {
      this.loadReportObject();
      this.onHandleReload = (autoReload) => {
        if (!autoReload) {
          this.reportFile = null;
          this.loadReportObject();
        }
      };
      eventBus.$on('handleReload', this.onHandleReload);
    },

    destroyed() {
      eventBus.$off('handleReload', this.onHandleReload);
    },

    methods: {
      loadReportObject() {
        const self = this;
        self.isLoading = true;

        // start to load the data
        getReportObject({
          url: self.rootUrl + 'report.json',
          success: function (report) {
            self.reportFile = report;
            self.errorMessage = null;
            console.log(`loaded report ${self.rootUrl}.`);
            self.isLoading = false;
          },
          error: function (e) {
            self.reportFile = null;
            self.errorMessage = e;
            console.log(`error when loading report: ${e}.`);
            self.isLoading = false;
          }
        });
      }
    },

    watch: {
      rootUrl(val) {
        this.reportFile = null;
        this.loadReportObject();
      }
    }
  }
</script>

<style lang="scss" scoped>
  .main-wrapper {
    height: 100%;
    overflow: auto;
  }
  .main-content {
    max-width: 960px;
    margin: auto;
    padding: 5px 10px;
  }
  h1 {
    color: #673ab7;
    font-weight: 400;
  }
</style>
