<template>
  <div class="image-wrapper">
    <figure class="report-image" v-if="title">
      <img :src="url" :alt="url" :title="title" />
      <figcaption>Figure: {{ title }}</figcaption>
    </figure>
    <img v-if="!title" class="report-image" :src="url" :alt="url" />
  </div>
</template>

<script>
  export default {
    props: ['rootUrl', 'data'],

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
        return this.rootUrl + this.data['path'];
      }
    },

    data() {
      return {};
    }
  }
</script>

<style lang="scss" scoped>
  @import './settings.scss';

  .image-wrapper {
    display: inline;
  }

  // apply to both situations
  .report-image {
    display: block;
    max-width: 100%;
    border: 1px solid $figure-border-color;
    border-radius: $block-border-radius;
    padding: $figure-border-padding;
    margin: 1em auto;
  }

  // apply only if the image is wrapped in figure
  .report-image {
    img {
      padding: 0;
      margin: 0;
      width: 100%;
    }
    figcaption {
      width: 100%;
      text-align: center;
    }
  }
</style>
