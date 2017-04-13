<template>
  <!-- the main content -->
  <div class="main-wrapper">
    <!-- the loading progress -->
    <mu-linear-progress class="loading-progress" v-if="isLoading"></mu-linear-progress>

    <!-- the loading error message -->
    <div v-if="errorMessage" class="main-content error">
      Failed to load report: {{ errorMessage }}.
      <img src='asserts/404.png'/>
    </div>

    <!-- the main report body -->
    <div v-if="!errorMessage && reportFile" class="main-content report-body">
      <h1>{{ reportTitle }}</h1>
      <dispatch :rootUrl="rootUrl" :data="reportFile.data" :level="1"></dispatch>
    </div>
  </div> <!-- div.main-wrapper -->
</template>

<script>
  import { getReportObject } from '../lib/report.js';
  import { eventBus } from '../lib/eventBus.js';
  import Dispatch from './elements/Dispatch.vue';

  export default {
    props: {
      // the root url of the report, must end with '/'.
      rootUrl: {
        type: String,
        default: '/',
      }
    },

    components: {
      dispatch: Dispatch
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
        return title || 'Report';
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
          url: self.rootUrl + 'report.json',
          success: function (report) {
            self.reportFile = report;
            self.errorMessage = null;
            console.log(`loaded report ${self.rootUrl}.`);
            clearLoadingFlag();
          },
          error: function (e) {
            self.reportFile = null;
            self.errorMessage = e;
            console.log(`error when loading report: ${e}.`);
            clearLoadingFlag();
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
    padding: 5px 10px;
    max-width: 960px;
    margin: auto;
  }
</style>
