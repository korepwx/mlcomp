<template>
  <mu-dialog :open="!!group" :title="group ? '/' + group.path : ''" scrollable @close="handleClose">
    <mu-list class="group-detail" v-if="group" @itemClick="handleSelectStorage">
      <mu-list-item v-for="storage in group.items" titleClass="storage-title"
                    :title="storage.name" :value="storage" :data="storage" :key="storage.name">
        <!-- storage status as left icon -->
        <mu-icon v-if="storage.is_active" value="update" slot="left"/>
        <mu-icon v-if="!storage.is_active && !storage.has_error" value="done" slot="left"/>
        <mu-icon v-if="!storage.is_active && storage.has_error" value="error_outline" slot="left"/>

        <!-- storage describe -->
        <span slot="describe">
          <time-label class="info" :timestamp="storage.update_time"></time-label>
        </span>
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

<style>
  .group-detail {
    .storage-title {
      font-weight: bold;
    }
  }
</style>