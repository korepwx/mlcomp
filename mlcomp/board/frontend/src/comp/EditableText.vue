<template>
  <div class="editable-text" @click="onClick">
    <span v-if="!editing">
      {{ value }}
      <span v-if="!value" class="placeholder">(click here to edit)</span>
    </span>
    <mu-text-field v-if="editing" :value="value" @change="onValueChange" @blur="onBlur" fullWidth />
  </div>
</template>

<script>
  import $ from 'jquery';
  import Vue from 'vue';

  export default {
    props: ['value'],

    data() {
      return {
        editing: false
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
        this.$emit('change', val);
        this.editing = false;
      },

      onBlur() {
        this.editing = false;
      }
    }
  }
</script>

<style lang="scss" scoped>
  .editable-text {
    display: block;
    width: 100%;
    .placeholder {
      color: #aaa;
    }
  }
</style>