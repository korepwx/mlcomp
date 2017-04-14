<template>
  <div class="report-attachment" :class="{ 'attach-inline': link_only, 'attach-block': !link_only }">
    <span v-if="!link_only">Download the attachment: </span>
    <a :href="url" :title="title">{{ title || url }}</a>
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
      },

      link_only() {
        return this.data['link_only'];
      }
    },

    data() {
      return {};
    }
  }
</script>

<style lang="scss" scoped>
  @import './settings.scss';

  .attach-inline {
    display: inline;
  }
  .attach-block {
    display: block;
    padding: 10px;
    border: 1px solid #bdbdbd;
    border-left: 4px solid #bdbdbd;
    border-radius: $block-border-radius;
  }
  .attach-inline, .attach-block {
    a:hover {
      text-decoration: underline;
    }
  }
</style>
