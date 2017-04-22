<template>
  <div id="Storage" class="page-wrapper">
    <!-- the navigation bar -->
    <mu-appbar :title="storageInfo ? `Experiment “${storageInfo.name}”` : 'Experiment'" class="appbar">
      <mu-icon-button v-if="rootUrl !== '/'" icon="arrow_back" slot="left" href="/"></mu-icon-button>
      <mu-flat-button v-if="bottomNavValue === '/report/'" :label="selectedReport" slot="right" @click="toggleSelectReport"></mu-flat-button>
      <mu-icon-button icon="refresh" slot="right" @click="handleReload"></mu-icon-button>
    </mu-appbar>

    <mu-bottom-sheet :open="selectReportOpen" @close="closeSelectReport">
      <mu-list @itemClick="closeSelectReport" @change="changeSelectReport">
        <mu-sub-header>
          Select a report
        </mu-sub-header>
        <mu-list-item v-for="report in reportNames" :title="report" :key="report" :value="report"></mu-list-item>
      </mu-list>
    </mu-bottom-sheet>

    <!-- the main content -->
    <div class="storage-wrapper">
      <!-- the loading progress -->
      <mu-linear-progress class="loading-progress" v-if="isLoading"></mu-linear-progress>

      <!-- the loading error message -->
      <div v-if="errorMessage" class="storage-content error">
        Failed to load experiment data: {{ errorMessage }}.
      </div>

      <!-- the main list group -->
      <div v-if="!errorMessage && storageInfo" class="storage-content storage">
        <router-view :storageInfo="storageInfo" :rootUrl="rootUrl" @changeBrowsePath="changeBrowsePath"></router-view>
      </div>
    </div> <!-- div.main-wrapper -->

    <!-- the bottom navigation -->
    <mu-paper class="bottom-nav">
      <mu-bottom-nav :value="bottomNavValue">
        <mu-bottom-nav-item value="/" to="/" title="Home" icon="home" exact></mu-bottom-nav-item>
        <mu-bottom-nav-item value="/report/" :to="'/report/' + selectedReport + '/'" title="Report" icon="assignment"></mu-bottom-nav-item>
        <mu-bottom-nav-item value="/logs/" to="/logs/" title="Log" icon="access_time"></mu-bottom-nav-item>
        <mu-bottom-nav-item value="/browse/" :to="'/browse/' + browsePath" title="Files" icon="library_books" exact></mu-bottom-nav-item>
      </mu-bottom-nav>
    </mu-paper>
  </div> <!-- div.page-wrapper -->
</template>

<script>
  import $ from 'jquery';
  import { getJSON } from '../lib/utils.js';
  import { eventBus } from '../lib/eventBus.js';

  export default {
    data() {
      return {
        isLoading: false,
        storageInfo: null,
        errorMessage: null,
        selectedReport: 'default',
        selectReportOpen: false,
        browsePath: '',
      };
    },

    created() {
      this.loadStorageInfo();
    },

    mounted() {
      // extract the default report name
      let initialReport = 'default';
      const reportMatch = this.$route.path.match(/^\/report\/([^/]+)\/?$/);
      if (reportMatch) {
        initialReport = reportMatch[1];
      }
      this.selectedReport = initialReport;

      // extract the default browse path
      let initialBrowse = '';
      const browseMatch = this.$route.path.match(/^\/browse\/(.*)$/);
      if (browseMatch) {
        initialBrowse = browseMatch[1];
      }
      this.browsePath = initialBrowse;

      // initialize the auto-refresh interval
      this.reloadInterval = setInterval(
        () => this.handleReload({ autoReload: true }),
        60 * 1000
      )
    },

    destroyed() {
      clearInterval(this.reloadInterval);
    },

    computed: {
      rootUrl() {
        let url = window.root_url;
        if (!url.endsWith('/')) {
          url += '/';
        }
        return url;
      },

      reportNames() {
        return this.storageInfo && this.storageInfo['reports'];
      },

      bottomNavValue() {
        let val = this.$route.path;
        if (val.startsWith('/report/')) {
          val = '/report/';
        }
        if (val.startsWith('/browse/')) {
          val = '/browse/';
        }
        return val;
      },
    },

    methods: {
      loadStorageInfo() {
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
        getJSON({
          url: self.rootUrl + 'info',
          success: function (data) {
            if (data['__type__'] !== 'StorageInfo') {
              self.storageInfo = null;
              self.errorMessage = 'This URL seems not to be an experiment storage';
              console.log(`storage info: ${data}.`);
              clearLoadingFlag();
            } else {
              window.document.title = `${data['name']} - ML Board`;
              self.storageInfo = data;
              self.errorMessage = null;
              console.log(`loaded storage info ${self.rootUrl}.`);
              clearLoadingFlag();
            }
          },
          error: function (e) {
            self.storageInfo = null;
            self.errorMessage = e;
            console.log(`error when loading storage info: ${e}`);
            clearLoadingFlag();
          }
        });
      }, // loadStorageInfo

      handleNavChange(val) {
        this.$router.push(val);
      },

      closeSelectReport() {
        this.selectReportOpen = false;
      },

      toggleSelectReport() {
        this.selectReportOpen = !this.selectReportOpen;
      },

      changeSelectReport(val) {
        this.selectedReport = val;
        this.$router.push('/report/' + val + '/');
      },

      changeBrowsePath(val) {
        const path = (val && !val.endsWith('/') ? val + '/' : val);
        this.browsePath = val;
        this.$router.push('/browse/' + path);
      },

      handleReload({ autoReload=false }) {
        if (this.storageInfo.is_active) {
          eventBus.$emit('handleReload', autoReload);
          this.loadStorageInfo();
        }
      }
    },
  }
</script>

<style lang="scss" scoped>
  .page-wrapper {
    height: 100%;
  }

  .appbar {
    position: fixed;
    width: 100%;
    top: 0;
  }

  @media (max-width: 480px) {
    .storage-wrapper {
      padding-top: 56px;
    }
  }
  @media (min-width: 481px) {
    .storage-wrapper {
      padding-top: 64px;
    }
  }
  .storage-wrapper {
    height: 100%;
    padding-bottom: 56px;
    overflow-y: hidden;

    .storage-content {
      height: 100%;
    }
  }

  .bottom-nav {
    position: fixed;
    width: 100%;
    bottom: 0;
  }
</style>
