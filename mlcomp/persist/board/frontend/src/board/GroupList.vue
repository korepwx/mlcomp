<template>
  <div>
    <mu-list>
      <mu-list-item v-for="group in groups" toggleNested titleClass="group-title"
                    :title="'/' + group.path" :value="group" :data="group" :key="group.path"
                    :open="false">
        <mu-icon slot="left" value="folder" />
        <div class="group-summary">
          <div class="counts">
            <span style="color: #3f51b5" class="active-count"
                  v-if="group.active_count">{{ group.active_count }} running</span>
            <span style="color: #009688" class="success-count"
                  v-if="group.success_count">{{ group.success_count }} success</span>
            <span style="color: #f44336" class="error-count"
                  v-if="group.error_count">{{ group.error_count }} error</span>
          </div>
          <time-label style="color: #9e9e9e" class="update-time" :timestamp="group.update_time"></time-label>
          <div class="clear"></div>
        </div>

        <!-- Here start the storage list -->
        <mu-list-item slot="nested" v-for="storage in group.items"
                      :title="storage.name" :value="storage" :data="storage" :key="storage.name">
          <mu-icon slot="left" value="assignment"/>
        </mu-list-item>
      </mu-list-item>
    </mu-list>
  </div>
</template>

<script>
  import TimeLabel from './TimeLabel.vue';

  export default {
    components: {
      'time-label': TimeLabel
    },

    props: {
      groups: {
        type: Array,
        default: []
      }
    },

    data() {
      return {};
    }
  }
</script>

<style lang="sass">
  .group-title {
    font-weight: bold;
    font-size: 20px;
  }

  .group-summary {
    padding-top: 8px;

    div.counts {
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
    }
    div.update-time {
      float: right;
    }
    div.clear {
      clear: both;
    }
  }
</style>