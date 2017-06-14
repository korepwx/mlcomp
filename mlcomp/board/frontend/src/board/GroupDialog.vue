<template>
  <mu-dialog :open="!!group" :title="group ? '/' + group.path : ''" @close="handleClose">
    <mu-list class="group-detail" v-if="group">
      <mu-list-item v-for="storage in group.items" titleClass="storage-title"
                    :value="storage" :data="storage" :key="storage.name"
                    :href="getStorageURL(storage)"
      >
        <!-- storage status as left icon -->
        <mu-icon v-if="storage.is_active" value="update" slot="left"/>
        <mu-icon v-if="!storage.is_active && !storage.has_error" value="done" slot="left"/>
        <mu-icon v-if="!storage.is_active && storage.has_error" value="error_outline" slot="left"/>

        <!-- storage title -->
        <div slot="title" class="storage-title">
          {{ storage.name }}
          <time-label class="update-time text-info" :timestamp="storage.update_time"></time-label>
          <div class="clear"></div>
        </div>

        <!-- storage describe -->
        <div slot="describe" class="summary">
          <div class="description status-left" v-if="storage.description">{{ storage.description }}</div>
          <div class="tags status-right" v-if="storage.tags">
            <span v-for="tag in storage.tags" class="tag">{{ tag }}</span>
          </div>
          <div class="clear"></div>
        </div>
      </mu-list-item>
    </mu-list>

    <mu-flat-button primary label="Close" @click="handleClose" slot="actions"/>
  </mu-dialog>
</template>

<script>
  import TimeLabel from '../comp/TimeLabel.vue';

  export default {
    components: {
      'time-label': TimeLabel
    },

    props: {
      group: {
        default: null
      }
    },

    data() {
      return {};
    },

    methods: {
      handleClose() {
        this.$emit('close');
      },

      getStorageURL(storage) {
        const path = this.group.path ? this.group.path + '/' + storage.name : storage.name;
        return `/s/${path}/`;
      }
    }
  }
</script>

<style lang="scss" scoped>
  .group-detail {
    .storage-title {
      font-weight: bold;
      .update-time {
        float: right;
        font-weight: normal;
        font-size: 11px;
      }
    }

    .summary {
      .status-left {
        float: left;
      }  /* .status */

      .status-right {
        float: right;
      }

      .tags {
        .tag {
          margin-left: 5px;
          background-color: #e0e0e0;
          font-size: 11px;
          border-radius: 2px;
          padding: 1px 3px;
        }

        .tag:first-child {
          margin-left: 0;
        }
      }
    } /* .summary */

    .clear {
      clear: both;
    }
  }
</style>