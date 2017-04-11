<template>
  <div v-html="rendered" :class="{'math-inline': this.inline, 'math-block': !this.inline}"></div>
</template>

<script>
  import katex from 'katex';

  export default {
    props: ['latex', 'inline'],

    computed: {
      rendered() {
        try {
          return katex.renderToString(this.latex, {
            throwOnError: false,
            displayMode: !this.inline,
          });
        } catch (e) {
          console.log(e);
          return this.latex;
        }
      }
    },

    data() {
      return {};
    }
  }
</script>

<style lang="scss" scoped>
  .math-inline {
    display: inline;
  }
  .math-block {
    display: block;
  }
</style>
