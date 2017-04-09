<template>
  <div id="Board" class="page-wrapper">
    <!-- the navigation bar -->
    <mu-appbar title="ML Board" class="appbar" :class="{'side-panel-hided': !sidePanelOpen}">
      <mu-icon-button icon="menu" slot="left" @click="toggleSidePanel" />
      <mu-icon-button icon="refresh" slot="right" @click="loadStorageGroups" />
    </mu-appbar>

    <!-- the config panel at the left -->
    <side-panel class="side-panel" :open="sidePanelOpen" :docked="sidePanelDocked"
                :statusFilter="statusFilter" :queryString="queryString"
                @close="closeSidePanel" @toggle="toggleSidePanel"
                @changeStatusFilter="changeStatusFilter"
                @changeQueryString="changeQueryString">
    </side-panel>

    <!-- the main content -->
    <div class="main-wrapper" :class="{'side-panel-hided': !sidePanelOpen}">
      <!-- the loading progress -->
      <mu-linear-progress class="loading-progress" v-if="isLoading"></mu-linear-progress>

      <!-- the loading error message -->
      <div v-if="errorMessage" class="main-content error">
        Failed to load experiments: {{ errorMessage }}.
      </div>

      <!-- the main list group -->
      <group-list v-if="!errorMessage" class="main-content groups"
                  :groups="filteredGroups"></group-list>
    </div> <!-- div.main-wrapper -->
  </div> <!-- div.page-wrapper -->
</template>
<script>
  import { APIClient, ALL_STATUS } from '../lib/api.js';
  import { GroupFilter } from '../lib/query.js';
  import { isDesktop } from '../lib/utils.js';
  import persist from '../lib/persist.js';
  import SidePanel from './SidePanel.vue';
  import GroupList from './GroupList.vue';

  // The component definition.
  export default {
    components: {
      'side-panel': SidePanel,
      'group-list': GroupList,
    },

    data() {
      return {
        sidePanelOpen: isDesktop() && persist.boardConfig.sidePanelOpen,
        sidePanelDocked: isDesktop(),
        desktop: isDesktop(),
        isLoading: false,
        errorMessage: null,
        storageGroups: null,
        statusFilter: persist.boardConfig.statusFilter,
        queryString: persist.boardConfig.queryString,
      }
    },

    created() {
      this.loadStorageGroups();
    },

    mounted() {
      this.checkDesktop();
      this.handleResize = () => {
        this.checkDesktop()
      };
      window.addEventListener('resize', this.handleResize);
      this.reloadInterval = setInterval(
        () => this.loadStorageGroups(),
        5 * 60 * 1000
      );
    },

    destroyed() {
      window.removeEventListener('resize', this.handleResize);
      clearInterval(this.reloadInterval);
    },

    computed: {
      groupFilter() {
        return new GroupFilter(this.storageGroups);
      },

      filteredGroups() {
        return this.groupFilter.getFiltered({
          status: this.statusFilter,
          query: this.queryString
        });
      }
    },

    methods: {
      checkDesktop() {
        const desktop = isDesktop();
        this.sidePanelDocked = desktop;
        if (desktop === this.desktop) return;
        if (!desktop && this.desktop && this.sidePanelOpen) {
          this.sidePanelOpen = false
        }
        if (desktop && !this.desktop && !this.sidePanelOpen) {
          this.sidePanelOpen = persist.boardConfig.sidePanelOpen;
        }
        this.desktop = desktop
      },

      toggleSidePanel() {
        this.sidePanelOpen = !this.sidePanelOpen;
      },

      closeSidePanel() {
        this.sidePanelOpen = false;
      },

      loadStorageGroups() {
        const self = this;
        const apiClient = new APIClient('/_api');

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
        apiClient.getStorageGroups({
          success: function (groups) {
            self.storageGroups = groups;
            self.errorMessage = null;
            console.log('loaded storage groups.');
            clearLoadingFlag();
          },
          error: function (e) {
            self.storageGroups = null;
            self.errorMessage = e;
            console.log(`error when loading storage groups: ${e}.`);
            clearLoadingFlag();
          }
        });
      },

      changeStatusFilter(config) {
        for (const key of Object.keys(config)) {
          const value = config[key];
          if (value) {
            if (!this.statusFilter.includes(key)) {
              this.statusFilter.push(key);
            }
          } else {
            if (this.statusFilter.includes(key)) {
              this.statusFilter = this.statusFilter.filter(x => x != key);
            }
          }
        }
        persist.boardConfig.statusFilter = this.statusFilter;
      }, // changeStatusFilter

      changeQueryString(value) {
        this.queryString = value;
        persist.boardConfig.queryString = this.queryString;
      }, // changeQueryString
    }, // methods

    watch: {
      sidePanelOpen(value) {
        if (this.sidePanelDocked) {
          persist.boardConfig.sidePanelOpen = value;
        }
      }
    }, // watch

    beforeRouteEnter (to, from, next) {
      window.document.title = "Dashboard - ML Board";
      next();
    },
  }
</script>

<style lang="scss" scoped>
  $easeOut: cubic-bezier(0.23, 1, 0.32, 1);

  .appbar {
    position: fixed;
    left: 256px;
    right: 0;
    top: 0;
    width: auto;
    transition: all .45s $easeOut;
  }

  .main-wrapper {
    padding-top: 64px;
    padding-left: 256px;
    transition: all .45s $easeOut;
  }

  .side-panel-hided.main-wrapper {
    padding-left: 0;
  }
  .side-panel-hided.appbar {
    left: 0;
  }

  .main-content {
    padding: 48px 72px;
  }

  @media (max-width: 480px) {
    .main-wrapper {
      padding-top: 56px;
    }
  }
  @media (max-width: 993px) {
    .appbar {
      left: 0;
    }
    .main-wrapper {
      padding-left: 0;
    }
    .main-content {
      padding: 24px 36px;
    }
  }
</style>