<template>
  <div class="main-wrapper">
    <!-- the loading progress -->
    <mu-linear-progress class="loading-progress" v-if="isLoading"></mu-linear-progress>

    <!-- the loading error message -->
    <div v-if="errorMessage" class="main-content error">
      Failed to load files at "{{ browsePath }}": {{ errorMessage }}.
    </div>

    <!-- the main list group -->
    <div v-if="!errorMessage" class="main-content browse">
      <mu-list v-if="entities" @change="handleClickEntity">
        <mu-list-item v-if="!isRootPath" :value="{'name': '..', 'is_dir': true}" title="..">
          <mu-icon slot="left" value="folder" />
        </mu-list-item>
        <mu-list-item v-for="e in entities" :key="e.name" :value="e" :title="e.name"
                      :href="!e.is_dir ? rootUrl + 'files/' + getEntityPath(e) : null"
                      :target="!e.is_dir ? '_blank' : null">
          <mu-icon slot="left" :value="e.is_dir ? 'folder' : 'insert_drive_file'" />
        </mu-list-item>
      </mu-list>
    </div>
  </div>
</template>

<script>
  import { getJSON } from '../lib/utils.js';
  import { eventBus } from '../lib/eventBus.js';

  export default {
    props: [
      'storageInfo',
      'rootUrl',
    ],

    data() {
      return {
        isLoading: false,
        errorMessage: null,
        entities: null,
      };
    },

    computed: {
      browsePath() {
        return this.$route.params['0'];
      },

      isRootPath() {
        return !this.browsePath.replace('/', '');
      }
    },

    methods: {
      loadEntities() {
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
        self.entities = null;
        getJSON({
          url: self.rootUrl + 'files/' + self.browsePath + '?stat=1',
          cache: false,
          success: function (data) {
            if (!Array.isArray(data)) {
              self.entities = null;
              self.errorMessage = `not a directory`;
            } else {
              data.sort(function (a, b) {
                if (a.is_dir && !b.is_dir)
                  return -1;
                if (!a.is_dir && b.is_dir)
                  return 1;
                return a.name < b.name ? -1 : (a.name > b.name ? 1 : 0);
              });
              self.entities = data;
              self.errorMessage = null;
              console.log(`navigated to "${self.browsePath}".`);
            }
            clearLoadingFlag();
          },
          error: function (e) {
            self.entities = null;
            self.errorMessage = e;
            console.log(`error when loading entities: ${e}`);
            clearLoadingFlag();
          }
        })
      },

      getEntityPath(e) {
        let path = (
          (this.browsePath && !this.browsePath.endsWith('/')) ?
            this.browsePath + '/' : this.browsePath
        );
        if (e.name === '..') {
          const idx = path.lastIndexOf('/', path.length - 2);
          if (idx >= 0) {
            path = path.substr(0, idx);
          } else {
            path = '';
          }
        } else {
          path += e.name;
        }
        return path;
      },

      handleClickEntity(e) {
        if (e.is_dir) {
          this.$emit('changeBrowsePath', this.getEntityPath(e));
        } else {
          // files should be controlled by "href" instead of by action
        }
      },
    },

    mounted() {
      this.loadEntities();
      this.onHandleReload = (autoReload) => {
        if (!autoReload) this.loadEntities();
      };
      eventBus.$on('handleReload', this.onHandleReload);
    },

    destroyed() {
      eventBus.$off('handleReload', this.onHandleReload);
    },

    watch: {
      browsePath() {
        this.loadEntities();
      }
    }
  }
</script>

<style lang="scss" scoped>
  .main-wrapper {
    height: 100%;
    overflow: auto;
  }
</style>