<template>
  <div>
    <report :rootUrl="reportUrl"></report>
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
