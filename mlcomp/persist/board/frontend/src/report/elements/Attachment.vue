<template>
  <div class="report-attachment" :class="{ 'attach-inline': link_only, 'attach-block': !link_only }">
    <span v-if="!link_only">Download the attachment: </span>
    <a :href="url" :title="title">{{ title || url }}</a>
  </div>
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
  .attach-inline {
    display: inline;
  }
  .attach-block {
    display: block;
  }
</style>
