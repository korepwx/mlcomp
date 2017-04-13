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
  .image-wrapper {
    display: inline;
  }

  // apply to both situations
  .report-image {
    display: block;
    width: 100%;
    border: 1px solid #ccc;
    border-radius: 2px;
    padding: 2px;
    margin: 1em 0;
  }

  // apply only if the image is wrapped in figure
  .report-image {
    img {
      width: 100%;
      margin: 0;
      padding: 0;
    }
    figcaption {
      width: 100%;
      text-align: center;
    }
  }
</style>
