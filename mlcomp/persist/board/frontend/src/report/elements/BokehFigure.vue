<template>
  <figure class="bokeh-figure">
    <div class="figure" v-html="html"></div>
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

      html() {
        return this.data['html'];
      }
    },

    data() {
      return {};
    },

    mounted() {
      const s = document.createElement("script");
      s.type = "text/javascript";
      s.src = this.data.js.path;
      s.async = true;
      this.$el.appendChild(s);
    }
  }
</script>

<style lang="scss" scoped>
  .bokeh-figure {
    .figure {
      width: 100%;
    }
    figcaption {
      width: 100%;
      text-align: center;
    }

    width: 100%;
    max-width: 600px;
    display: block;
  }
</style>
