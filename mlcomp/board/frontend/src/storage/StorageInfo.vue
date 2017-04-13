<template>
  <div>
    <mu-table :showCheckbox="false">
      <mu-tbody>
        <mu-tr>
          <mu-td class="label">Name</mu-td>
          <mu-td>{{ storage.name }}</mu-td>
        </mu-tr>
        <mu-tr>
          <mu-td class="label">Status</mu-td>
          <mu-td v-if="storage.is_active">Running</mu-td>
          <mu-td v-if="!storage.is_active && !storage.has_error">Finished</mu-td>
          <mu-td v-if="!storage.is_active && storage.has_error">Error</mu-td>
        </mu-tr>
        <mu-tr v-if="storage.tags && storage.tags.length">
          <mu-td class="label">Tags</mu-td>
          <mu-td class="tag-container">
            <mu-chip class="tag" v-for="tag in storage.tags" :key="tag">{{ tag }}</mu-chip>
          </mu-td>
        </mu-tr>
        <mu-tr v-if="storage.description">
          <mu-td class="label">Description</mu-td>
          <mu-td>{{ storage.description }}</mu-td>
        </mu-tr>
        <mu-tr v-if="storage.create_time">
          <mu-td class="label">Create Time</mu-td>
          <mu-td><time-label :timestamp="storage.create_time"></time-label></mu-td>
        </mu-tr>
        <mu-tr v-if="storage.update_time">
          <mu-td v-if="storage.is_active" class="label">Update Time</mu-td>
          <mu-td v-if="!storage.is_active" class="label">Finish Time</mu-td>
          <mu-td><time-label :timestamp="storage.update_time"></time-label></mu-td>
        </mu-tr>
        <mu-tr v-if="storage.running_status && storage.running_status.hostname">
          <mu-td class="label">Host Name</mu-td>
          <mu-td>{{ storage.running_status.hostname }}</mu-td>
        </mu-tr>
        <mu-tr v-if="storage.running_status && storage.running_status.pid">
          <mu-td class="label">PID</mu-td>
          <mu-td>{{ storage.running_status.pid }}</mu-td>
        </mu-tr>
      </mu-tbody>
    </mu-table>
  </div>
</template>

<script>
  import TimeLabel from '../comp/TimeLabel.vue';
  import { Storage } from '../lib/api.js';

  export default {
    props: [
      'storageInfo',
      'rootUrl',
    ],

    components: {
      TimeLabel
    },

    data() {
      return {};
    },

    computed: {
      storage() {
        if (this.storageInfo) {
          const name = this.storageInfo['name'];
          let path = this.rootUrl;
          if (path.startsWith('/s/')) {
            path = path.substr(3);
          }
          if (path === name + '/') {
            path = '';
          } else if (path.endsWith('/' + name + '/')) {
            path = path.substr(0, path.length - 2 - name.length);
          }
          return new Storage(path, name, this.storageInfo);
        }
      }
    }
  }
</script>

<style lang="scss" scoped>
  td.label {
    font-weight: bold;
  }
  .tag-container {
    .tag {
      margin-right: 8px;
    }
    .tag:last-child {
      margin-right: 0;
    }
  }
</style>
