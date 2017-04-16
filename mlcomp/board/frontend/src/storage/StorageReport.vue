<template>
  <div class="storage-report">
    <report :rootUrl="reportUrl" :reportDirName="selectedReport"></report>
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

      reportUrl() {
        return this.rootUrl + 'report/' + this.selectedReport + '/';
      }
    },
  }
</script>

<style lang="scss" scoped>
  .storage-report {
    height: 100%;
  }
</style>
