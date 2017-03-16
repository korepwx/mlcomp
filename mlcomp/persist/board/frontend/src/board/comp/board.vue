<template>
  <div id="board" class="content">
    <!-- the storage modal -->
    <bs-modal v-show="showGroupModal">
      Some content displayed in the modal.

      <button type="button" class="btn btn-secondary" v-on:click="this.selectedGroup = null" data-dismiss="modal">Close</button>
    </bs-modal>
    
    <!-- the main list group -->
    <ul class="list-group">
      <a href="#" class="list-group-item list-group-item-action flex-column align-items-start"
         v-for="group in storageGroups" @click="selectedGroup = group">
        <div class="d-flex w-100 justify-content-between">
          <h5 class="mb-1">/{{ group.path }}</h5>
          <div>
            <span class="badge badge-default badge-pill align-top"
                  v-if="group.active_count">{{ group.active_count }}</span>
          </div>
        </div>
        <div class="d-flex w-100 justify-content-between">
          <div class="mb-1 group-summary">
            <small class="text-primary align-bottom"
                   v-if="group.active_count">{{ group.active_count }} running</small>
            <small class="text-success align-bottom"
                   v-if="group.success_count">{{ group.success_count }} success</small>
            <small class="text-error align-bottom"
                   v-if="group.error_count">{{ group.error_count }} error</small>
          </div>
          <div>
            <small class="align-bottom text-muted">{{ formatTime(group.update_time) }}</small>
          </div>
        </div>
      </a>
    </ul>
  </div>
</template>
<script>
  import { mapState } from 'vuex';
  import { formatTime } from '../lib/datetime.js';
  import store from '../lib/store.js';
  import ModalComponent from './modal.vue';

  /**
   * Filter the storage groups by query and status.
   */
  function filterGroups({ status, query }) {
    const groups = store.state.storageGroups;

    // if no status filter and no query filter, directly return the groups.
    if (!status && !query) {
      return groups;
    }

    // build the status filter
    const matchStatus = (function() {
      if (status == 'active') {
        return function (g) {
          return g.is_active;
        };
      } else if (status == 'completed') {
        return function (g) {
          return !g.is_active;
        };
      } else {
        return function (g) {
          return true;
        };
      }
    })();

    // build the query filter
    const matchQuery = function(g) {
      return true;
    };

    // now filter the result
    return groups.filter(function(g) {
      return matchStatus(g) && matchQuery(g);
    });
  }

  export default {
    data() {
      return {
        selectedGroup: null
      }
    },

    components: {
      'bs-modal': ModalComponent
    },

    computed: mapState({
      storageGroups() {
        return filterGroups(this.$route.path.substr(1));
      },

      showGroupModal() {
        return !!this.selectedGroup;
      }
    }),

    methods: {
      formatTime
    }
  }
</script>

<style lang="sass" scoped>
  div.group-summary {
    small:after {
      content: ', ';
    }
    small:last-child:after {
      content: '';
    }
  }
</style>