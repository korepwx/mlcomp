<template>
  <div>
    <h2 v-if="level === 1" class="section-title">{{ title }}</h2>
    <h3 v-if="level === 2" class="section-title">{{ title }}</h3>
    <h4 v-if="level === 3" class="section-title">{{ title }}</h4>
    <h5 v-if="level === 4" class="section-title">{{ title }}</h5>
    <h6 v-if="level >= 5" class="section-title">{{ title }}</h6>

    <dispatch v-for="child in children" :key="child['name_scope']" :rootUrl="rootUrl" :data="child" :level="level + 1"></dispatch>
  </div>
</template>

<script>
  import Dispatch from './Dispatch.vue';

  export default {
    props: ['rootUrl', 'data', 'level'],

    components: {
      dispatch: Dispatch
    },

    computed: {
      title() {
        return this.data['title'];
      },

      children() {
        return this.data['children'];
      }
    },

    data() {
      return {};
    }
  }
</script>