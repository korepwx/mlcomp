<template>
  <div class="report-container" :class="{'container-inline': inline, 'container-block': !inline}">
    <dispatch v-for="child in children" :key="child['__id__']" :rootUrl="rootUrl" :data="child" :level="level"></dispatch>
  </div>
</template>

<script>
  import Dispatch from './Dispatch.vue';

  export default {
    props: ['rootUrl', 'data', 'level', 'inline'],

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
  .container-inline {
    display: inline;
  }
  .container-block {
    display: block;
    margin: 1em 0;
  }
</style>