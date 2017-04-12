<template>
  <div id="Storage" class="page-wrapper">
    <!-- the navigation bar -->
    <mu-appbar :title="storageInfo ? `Experiment “${storageInfo.name}”` : 'Experiment'" class="appbar">
      <mu-icon-button icon="arrow_back" slot="left" href="/" />
    </mu-appbar>

    <!-- the main content -->
    <div class="storage-wrapper">
      <!-- the loading progress -->
      <mu-linear-progress class="loading-progress" v-if="isLoading"></mu-linear-progress>

      <!-- the loading error message -->
      <div v-if="errorMessage" class="storage-content error">
        Failed to load experiment data: {{ errorMessage }}.
      </div>

      <!-- the main list group -->
      <div v-if="!errorMessage" class="storage-content storage">
        <transition name="md-router" appear>
          <router-view :storage="storageInfo" :root_url="root_url"></router-view>
        </transition>
      </div>
    </div> <!-- div.main-wrapper -->

    <!-- the bottom navigation -->
    <mu-paper class="bottom-nav">
      <mu-bottom-nav :value="$route.path">
        <mu-bottom-nav-item value="/" to="/" title="Home" icon="home" exact/>
        <mu-bottom-nav-item value="/report/" to="/report/" title="Report" icon="assignment"/>
        <mu-bottom-nav-item value="/_logging/" to="/_logging/" title="Log" icon="access_time"/>
      </mu-bottom-nav>
    </mu-paper>
  </div> <!-- div.page-wrapper -->
</template>

<script>
  import { getStorageInfo } from '../lib/api.js';

  export default {
    data() {
      return {
        isLoading: false,
        storageInfo: null,
        errorMessage: null,
      };
    },

    created() {
      this.loadStorageInfo();
    },

    computed: {
      root_url() {
        let url = window.root_url;
        if (!url.endsWith('/')) {
          url += '/';
        }
        return url;
      }
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
        getStorageInfo({
          root_url: self.root_url,
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
              console.log('loaded storage info.');
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
  .storage-wrapper {
    height: 100%;
    padding-top: 64px;
    padding-bottom: 56px;
    overflow-y: hidden;

    .storage-content {
      height: 100%;
      overflow-y: scroll;
    }
  }

  .bottom-nav {
    position: fixed;
    width: 100%;
    bottom: 0;
  }
</style>