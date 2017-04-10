<template>
  <div class="report-container">
    <dispatch v-for="child in children" :key="child['__id__']" :data="child" :level="level"></dispatch>
  </div>
</template>

<script>
  import Dispatch from './Dispatch.vue';

  export default {
    props: ['data', 'level'],

    components: {
      dispatch: Dispatch
    },

    computed: {
      children() {
        return this.data['children'];
      }
    },

    data() {
      return {};
    }
  }
</script>

<style lang="scss" scoped>
  .report-container {
    margin: 1em 0;
  }
</style>