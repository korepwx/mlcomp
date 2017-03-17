<template>
  <div>
    <group-dialog :group="selectedGroup" @close="handleDialogClose"></group-dialog>

    <mu-list class="group-entry" @itemClick="handleSelectGroup">
      <mu-list-item v-for="group in groups" titleClass="group-title"
                    :title="'/' + group.path" :value="group" :data="group" :key="group.path">
        <mu-icon slot="left" value="folder" />
        <div slot="describe" class="summary">
          <div class="status-left">
            <span class="text-active" v-if="group.active_count">{{ group.active_count }} running</span>
            <span class="text-success" v-if="group.success_count">{{ group.success_count }} success</span>
            <span class="text-error" v-if="group.error_count">{{ group.error_count }} failed</span>
          </div>
          <time-label class="status-right text-info" :timestamp="group.update_time"></time-label>
          <div class="clear"></div>
        </div>
      </mu-list-item>
    </mu-list>
  </div>
</template>

<script>
  import TimeLabel from './TimeLabel.vue';
  import GroupDialog from './GroupDialog.vue';

  export default {
    components: {
      'time-label': TimeLabel,
      'group-dialog': GroupDialog,
    },

    props: {
      groups: {
        type: Array,
        default: []
      }
    },

    data() {
      return {
        selectedGroup: null
      };
    },

    methods: {
      handleSelectGroup(item) {
        const group = item.value;
        this.selectedGroup = group;
      },

      handleDialogClose() {
        this.selectedGroup = null;
      }
    }
  }
</script>

<style lang="sass">
  .group-entry {
    .group-title {
      font-weight: bold;
    }

    .summary {
      .status-left {
        float: left;

        span {
          margin-right: 2px;
        }
        span:after {
          color: #9e9e9e;
          content: ',';
        }
        span:last-child {
          margin-right: 0;
        }
        span:last-child:after {
          content: '';
        }
      }  /* .status */

      .status-right {
        float: right;
      }

      .clear {
        clear: both;
      }
    } /* .summary */
  }
</style>