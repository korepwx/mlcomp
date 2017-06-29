<template>
  <div id="Storage" class="page-wrapper">
    <!-- the navigation bar -->
    <mu-appbar :title="getStorageTitle()" class="appbar">
      <mu-icon-button v-if="rootUrl !== '/'" icon="arrow_back" slot="left" href="/"></mu-icon-button>
      <mu-flat-button v-if="bottomNavValue === '/report/'" :label="selectedReport" slot="right" @click="toggleSelectReport"></mu-flat-button>

      <mu-icon-button icon="refresh" @click="handleReload" slot="right" title="Reload"></mu-icon-button>
      <mu-icon-menu icon="more_vert" slot="right" tooltip="Actions"
                    :anchorOrigin="{horizontal: 'right', vertical: 'bottom'}"
                    :targetOrigin="{horizontal: 'right', vertical: 'top'}">
        <mu-menu-item leftIcon="get_app" :href="rootUrl + 'archive.zip'" target="_blank" title="Download"></mu-menu-item>
        <mu-divider></mu-divider>
        <mu-menu-item leftIcon="delete" @click="handleOpenDialog" title="Delete"></mu-menu-item>
      </mu-icon-menu>
    </mu-appbar>

    <mu-bottom-sheet :open="selectReportOpen" @close="closeSelectReport">
      <mu-list @itemClick="closeSelectReport" @change="changeSelectReport">
        <mu-sub-header>
          Select a report
        </mu-sub-header>
        <mu-list-item v-for="report in reportNames" :title="report" :key="report" :value="report"></mu-list-item>
      </mu-list>
    </mu-bottom-sheet>

    <!-- the delete confirmation dialog -->
    <mu-dialog :open="deleteConfirm" title="Confirm to Delete" @close="handleCloseDialog">
      <div style="margin-top: 20px">
        Are you sure to delete {{ getStorageTitle(true) }}?
       </div>

      <mu-flat-button primary label="Delete" @click="handleDelete" slot="actions"/>
      <mu-flat-button default label="Cancel" @click="handleCloseDialog" slot="actions"/>
    </mu-dialog>

    <!-- the main content -->
    <div class="storage-wrapper">
      <!-- the loading progress -->
      <delayed-progress-bar :loading="isLoading"></delayed-progress-bar>

      <!-- the loading error message -->
      <div v-if="errorMessage" class="storage-content error">
        Failed to load experiment data: {{ errorMessage }}.
      </div>

      <!-- the main list group -->
      <div v-if="!errorMessage && storageInfo" class="storage-content storage">
        <router-view :storageInfo="storageInfo" :rootUrl="rootUrl" @changeBrowsePath="changeBrowsePath"
                     @infoChanged="storageInfoChanged"></router-view>
      </div>
    </div> <!-- div.main-wrapper -->

    <!-- the bottom navigation -->
    <mu-paper class="bottom-nav">
      <mu-bottom-nav :value="bottomNavValue">
        <mu-bottom-nav-item value="/" to="/" title="Home" icon="home" exact></mu-bottom-nav-item>
        <mu-bottom-nav-item value="/report/" :to="'/report/' + selectedReport + '/'" title="Report" icon="assignment"></mu-bottom-nav-item>
        <mu-bottom-nav-item value="/console/" to="/console/" title="Console" icon="access_time"></mu-bottom-nav-item>
        <mu-bottom-nav-item value="/browse/" :to="'/browse/' + browsePath" title="Files" icon="library_books" exact></mu-bottom-nav-item>
      </mu-bottom-nav>
    </mu-paper>
  </div> <!-- div.page-wrapper -->
</template>

<script>
  import $ from 'jquery';
  import naturalSort from 'javascript-natural-sort';
  import { getJSON, postGetJSON } from '../lib/utils.js';
  import { eventBus } from '../lib/eventBus.js';
  import DelayedProgressBar from '../comp/DelayedProgressBar.vue';

  naturalSort.insensitive = true;

  export default {
    components: {
      DelayedProgressBar
    },

    data() {
      return {
        isLoading: false,
        storageInfo: null,
        errorMessage: null,
        selectedReport: 'default',
        selectReportOpen: false,
        browsePath: '',
        deleteConfirm: false,
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
        const ret = this.storageInfo && this.storageInfo['reports'];
        return ret && ret.sort(naturalSort);
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
      getStorageTitle(lower=false) {
        const expTitle = lower ? 'experiment' : 'Experiment';
        if (this.storageInfo)
          return `${expTitle} “${this.storageInfo.name}”`;
        else
          return expTitle;
      },

      loadStorageInfoSuccess (data) {
        if (data['__type__'] !== 'StorageInfo') {
          this.storageInfo = null;
          this.errorMessage = 'This URL seems not to be an experiment storage';
          console.log(`storage info: ${data}.`);
        } else {
          window.document.title = `${data['name']} - ML Board`;
          this.storageInfo = data;
          this.errorMessage = null;
          console.log(`loaded storage info ${this.rootUrl}.`);
        }
        this.isLoading = false;
      },

      loadStorageInfoError (e) {
        this.storageInfo = null;
        this.errorMessage = e;
        console.log(`error when loading storage info: ${e}`);
        this.isLoading = false;
      },

      loadStorageInfo() {
        const self = this;
        this.isLoading = true;

        // start to load the data
        getJSON({
          url: self.rootUrl + 'info',
          cache: false,
          success: (data) => self.loadStorageInfoSuccess(data),
          error: (e) => self.loadStorageInfoError(e)
        });
      }, // loadStorageInfo

      updateStorageInfo(payload) {
        const self = this;
        this.isLoading = true;

        // start to load the data
        postGetJSON({
          url: self.rootUrl + 'info',
          payload: payload,
          cache: false,
          success: (data) => self.loadStorageInfoSuccess(data),
          error: (e) => self.loadStorageInfoError(e)
        });
      }, // updateStorageInfo

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
        if (!autoReload || this.storageInfo.is_active) {
          eventBus.$emit('handleReload', autoReload);
          this.loadStorageInfo();
        }
      },

      handleOpenDialog() {
        this.deleteConfirm = true;
      },

      handleCloseDialog() {
        this.deleteConfirm = false;
      },

      handleDelete() {
        const self = this;
        this.isLoading = true;
        this.deleteConfirm = false;

        // start to load the data
        postGetJSON({
          url: self.rootUrl + 'delete',
          payload: {},
          cache: false,
          success: (data) => {
            if (data['error'] !== 0) {
              self.storageInfo = null;
              self.errorMessage = data;
              console.log(`error when deleting storage: ${data}`);
              self.isLoading = false;
            } else {
              window.location.href = '/';
            }
          },
          error: (e) => {
            self.storageInfo = null;
            self.errorMessage = e;
            console.log(`error when deleting storage: ${e}`);
            self.isLoading = false;
          }
        });
      },

      storageInfoChanged(payload) {
        this.updateStorageInfo(payload);
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
