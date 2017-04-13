<template>
  <div class="report-dispatch">
    <r-section v-if="typeName === 'Section'" :rootUrl="rootUrl" :data="data" :level="level"></r-section>
    <r-table v-if="typeName === 'Table'" :rootUrl="rootUrl" :data="data" :level="level"></r-table>

    <span v-if="typeName === 'Text'">{{ data['text'] }}</span>
    <p v-if="typeName === 'ParagraphText'">{{ data['text'] }}</p>
    <div v-if="typeName === 'HTML'" v-html="data['html']"></div>
    <br v-if="typeName === 'LineBreak'" />

    <r-math v-if="typeName === 'InlineMath'" :rootUrl="rootUrl" :latex="data['latex']" :inline="true"></r-math>
    <r-math v-if="typeName === 'BlockMath'" :rootUrl="rootUrl" :latex="data['latex']" :inline="false"></r-math>

    <r-image v-if="typeName === 'Image'" :rootUrl="rootUrl" :data="data"></r-image>
    <r-attachment v-if="typeName === 'Attachment'" :rootUrl="rootUrl" :data="data"></r-attachment>

    <r-dynamic-content v-if="typeName === 'DynamicContent'" :rootUrl="rootUrl" :data="data"></r-dynamic-content>
    <r-canvas-js v-if="typeName === 'CanvasJS'" :rootUrl="rootUrl" :data="data"></r-canvas-js>

    <r-container v-if="!isKnownElement(typeName) && data['children']" :rootUrl="rootUrl" :data="data" :level="level" :inline="inline">
    </r-container>
  </div>
</template>

<script>
  const knownElements = [
    'Section', 'Table',
    'Text', 'ParagraphText', 'HTML', 'LineBreak',
    'InlineMath', 'BlockMath',
    'Image', 'Attachment',
    'DynamicContent', 'CanvasJS',
  ];

  export default {
    props: ['rootUrl', 'data', 'level', 'inline'],

    beforeCreate() {
      this.$options.components.RSection = require('./Section.vue');
      this.$options.components.RTable = require('./Table.vue');
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