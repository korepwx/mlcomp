<template>
  <div>
    <div v-if="reportName">
      <report :root_url="report_url"></report>
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
      report_url() {
        let url = this.root_url + 'report/' + this.reportName + '/';
        if (!url.endsWith('/'))
          url += '/';
        return url;
      }
    },
  }
</script>