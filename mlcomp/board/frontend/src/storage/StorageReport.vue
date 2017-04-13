<template>
  <div>
    <div v-if="reportNames">
      <!-- The list of available report -->
      <mu-dropDown-menu v-if="reportNames" :value="selectedReport" @change="handleReportNameChange">
        <mu-menu-item v-for="name in reportNames" :key="name" :value="name" :title="name" />
      </mu-dropDown-menu>

      <!-- The content of selected report -->
      <report :rootUrl="reportUrl"></report>
    </div>
    <div v-if="!reportNames">
      No report has been generated.
    </div>
  </div>
</template>

<script>
  import Report from '../report/Report.vue';

  export default {
    props: ['storageInfo', 'rootUrl'],

    components: {
      Report
    },

    data() {
      return {};
    },

    computed: {
      selectedReport() {
        return this.$route.params.name;
      },

      reportNames() {
        return this.storageInfo && this.storageInfo['reports'];
      },

      reportUrl() {
        return this.rootUrl + 'report/' + this.selectedReport + '/';
      }
    },

    methods: {
      handleReportNameChange(val) {
        this.$emit('selectedReportChanged', val);
      }
    }
  }
</script>