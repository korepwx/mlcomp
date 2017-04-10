<template>
  <figure class="report-image">
    <img :src="url" :alt="url" :title="title" />
    <figcaption v-if="title">Figure: {{ title }}</figcaption>
  </figure>
</template>

<script>
  export default {
    props: ['data'],

    computed: {
      title() {
        if (this.data['title'])
          return this.data['title'];
        else if (this.data['name'])
          return this.data['name'];
        else
          return null;
      },

      url() {
        return this.data['path'];
      }
    },

    data() {
      return {};
    }
  }
</script>

<style lang="scss" scoped>
  @import './settings.scss';

  .report-image {
    img {
      width: 100%;
    }
    figcaption {
      width: 100%;
      text-align: center;
    }

    width: 100%;
    max-width: $figure-max-width;
    display: block;
  }
</style>
