<template>
  <div>
    <div v-if="reportName">
      <!-- The list of available report -->
      <mu-dropDown-menu v-if="reportNames" :value="reportName" @change="handleReportNameChange">
        <mu-menu-item v-for="name in reportNames" :key="name" :value="name" :title="name" />
      </mu-dropDown-menu>

      <!-- The content of selected report -->
      <report :root_url="reportUrl"></report>
    </div>
    <div v-if="!reportName">
      No report has been generated.
    </div>
  </div>
</template>

<script>
  import Report from '../report/Report.vue';

  export default {
    props: ['storage', 'root_url'],

    components: {
      Report
    },

    data() {
      return {
        reportName: 'default',
      };
    },

    computed: {
      reportNames() {
        return this.storage && this.storage.reports;
      },

      reportUrl() {
        return this.root_url + 'report/' + this.reportName + '/';
      }
    },

    methods: {
      handleReportNameChange(val) {
        this.reportName = val;
      }
    }
  }
</script>