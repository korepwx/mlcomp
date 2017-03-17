<template>
  <mu-dialog :open="!!group" :title="group ? '/' + group.path : ''" scrollable @close="handleClose">
    <mu-list class="group-detail" v-if="group" @itemClick="handleSelectStorage">
      <mu-list-item v-for="storage in group.items" titleClass="storage-title"
                    :value="storage" :data="storage" :key="storage.name">
        <!-- storage status as left icon -->
        <mu-icon v-if="storage.is_active" value="update" slot="left"/>
        <mu-icon v-if="!storage.is_active && !storage.has_error" value="done" slot="left"/>
        <mu-icon v-if="!storage.is_active && storage.has_error" value="error_outline" slot="left"/>

        <!-- storage title -->
        <div slot="title" class="storage-title">
          {{ storage.name }}
          <div class="tags" v-if="storage.tags">
            <span v-for="tag in storage.tags" class="tag">{{ tag }}</span>
            <div class="clear"></div>
          </div>
        </div>

        <!-- storage describe -->
        <div slot="describe" class="summary">
          <div class="description status-left" v-if="storage.description">{{ storage.description }}</div>
          <time-label class="info status-right" :timestamp="storage.update_time"></time-label>
          <div class="clear"></div>
        </div>
      </mu-list-item>
    </mu-list>

    <mu-flat-button primary label="Close" @click="handleClose" slot="actions"/>
  </mu-dialog>
</template>

<script>
  import TimeLabel from './TimeLabel.vue';

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

      handleSelectStorage(item) {
        const storage = item.value;
        const path = this.group.path ? this.group.path + '/' + storage.name : storage.name;
        this.$router.push({ path: `/s/${path}/` });
      }
    }
  }
</script>

<style lang="sass" scoped>
  .group-detail {
    .storage-title {
      font-weight: bold;
      .tags {
        float: right;

        .tag {
          margin-left: 5px;
          font-size: 11px;
          font-weight: normal;
          background-color: #e0e0e0;
          border-radius: 2px;
          padding: 1px 3px;
        }
        .tag:first-child {
          margin-left: 0;
        }
      }
    }

    .summary {
      .status-left {
        float: left;
      }  /* .status */

      .status-right {
        float: right;
      }
    } /* .summary */

    .clear {
      clear: both;
    }
  }
</style>