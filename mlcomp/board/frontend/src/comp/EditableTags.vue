<template>
  <div class="editable-tags" @click="onClick">
    <div v-if="!editing" class="tag-container">
      <mu-chip class="tag" v-for="tag in tags" :key="tag">{{ tag }}</mu-chip>
      <span v-if="!tags || !tags.length" class="placeholder">(click here to edit)</span>
    </div>
    <mu-text-field v-if="editing" :value="tagValue" @change="onValueChange" @blur="onBlur" fullWidth />
  </div>
</template>

<script>
  import $ from 'jquery';
  import Vue from 'vue';

  export default {
    props: ['tags'],

    data() {
      return {
        editing: false
      }
    },

    computed: {
      tagValue() {
        return (this.tags || []).map(s => s.trim()).filter(s => !!s).join(', ');
      }
    },

    methods: {
      onClick() {
        this.editing = true;
        Vue.nextTick(() => {
          $(this.$el).find('input').focus();
        });
      },

      onValueChange(e, val) {
        this.$emit('change', val.split(',').map(s => s.trim()).filter(s => !!s));
        this.editing = false;
      },

      onBlur() {
        this.editing = false;
      }
    }
  }
</script>

<style lang="scss" scoped>
  .editable-tags {
    display: block;
    width: 100%;
    .tag-container {
      display: inline-block;
      .placeholder {
        color: #aaa;
      }
      .tag {
        margin-right: 8px;
      }
      .tag:last-child {
        margin-right: 0;
      }
    }
  }
</style>