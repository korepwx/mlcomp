<template>
  <div class="main-wrapper">
    <mu-table :showCheckbox="false">
      <mu-tbody>
        <mu-tr>
          <mu-td class="label">Name</mu-td>
          <mu-td>{{ storage.name }}</mu-td>
        </mu-tr>
        <mu-tr>
          <mu-td class="label">Status</mu-td>
          <mu-td v-if="storage.is_active" class="text-active">Running</mu-td>
          <mu-td v-if="!storage.is_active && !storage.has_error" class="text-success">Finished</mu-td>
          <mu-td v-if="!storage.is_active && storage.has_error" class="text-error">Error</mu-td>
        </mu-tr>
        <mu-tr>
          <mu-td class="label">Tags</mu-td>
          <mu-td>
            <editable-tags :tags="storage.tags" @change="onTagsChange"></editable-tags>
          </mu-td>
        </mu-tr>
        <mu-tr>
          <mu-td class="label">Description</mu-td>
          <mu-td><editable-text :value="storage.description" @change="onDescriptionChange"></editable-text></mu-td>
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
  import EditableText from '../comp/EditableText.vue';
  import EditableTags from '../comp/EditableTags.vue';
  import { Storage } from '../lib/api.js';

  export default {
    props: [
      'storageInfo',
      'rootUrl',
    ],

    components: {
      TimeLabel,
      EditableText,
      EditableTags,
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
    },

    methods: {
      onDescriptionChange(val) {
        this.$emit('infoChanged', {'description': val});
      },
      onTagsChange(tags) {
        this.$emit('infoChanged', {'tags': tags});
      }
    }
  }
</script>

<style lang="scss" scoped>
  .main-wrapper {
    height: 100%;
    overflow: auto;
  }
  td.label {
    font-weight: bold;
    width: 120px;
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
