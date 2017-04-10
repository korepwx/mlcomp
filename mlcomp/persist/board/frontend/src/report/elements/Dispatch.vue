<template>
  <div class="report-dispatch">
    <r-section v-if="typeName === 'Section'" :data="data" :level="level"></r-section>

    <span v-if="typeName === 'Text'">{{ data['text'] }}</span>
    <p v-if="typeName === 'ParagraphText'">{{ data['text'] }}</p>
    <div v-if="typeName === 'HTML'" v-html="data['html']"></div>
    <br v-if="typeName === 'LineBreak'" />

    <r-math v-if="typeName === 'InlineMath'" :latex="data['latex']" :inline="true"></r-math>
    <r-math v-if="typeName === 'BlockMath'" :latex="data['latex']" :inline="false"></r-math>

    <r-image v-if="typeName === 'Image'" :data="data"></r-image>
    <r-attachment v-if="typeName === 'Attachment'" :data="data"></r-attachment>

    <r-dynamic-content v-if="typeName === 'DynamicContent'" :data="data"></r-dynamic-content>
    <r-canvas-js v-if="typeName === 'CanvasJS'" :data="data"></r-canvas-js>

    <r-container v-if="!isKnownElement(typeName) && data['children']" :data="data" :level="level"></r-container>
  </div>
</template>

<script>
  const knownElements = [
    'Section',
    'Text', 'ParagraphText', 'HTML', 'LineBreak',
    'InlineMath', 'BlockMath',
    'Image', 'Attachment',
    'DynamicContent', 'CanvasJS',
  ];

  export default {
    props: ['data', 'level'],

    beforeCreate() {
      this.$options.components.RSection = require('./Section.vue');
      this.$options.components.RMath = require('./Math.vue');
      this.$options.components.RImage = require('./Image.vue');
      this.$options.components.RAttachment = require('./Attachment.vue');
      this.$options.components.RDynamicContent = require('./DynamicContent.vue');
      this.$options.components.RCanvasJs = require('./CanvasJS.vue');
      this.$options.components.RContainer = require('./Container.vue');
    },

    data() {
      return {};
    },

    computed: {
      typeName() {
        return this.data['__type__'];
      }
    },

    methods: {
      isKnownElement(typeName) {
        return knownElements.indexOf(typeName) >= 0;
      }
    }
  }
</script>

<style lang="scss" scoped>
  .report-dispatch {
    display: inline;
  }
</style>