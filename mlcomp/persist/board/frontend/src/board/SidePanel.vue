<template>
  <mu-drawer :open="open" :docked="docked" @close="handleClose" @hide="handleHide">
    <mu-list @itemClick="docked ? '' : toggle()">
      <mu-list-item title="Menu Item 1"/>
      <mu-list-item title="Menu Item 2"/>
      <mu-list-item title="Menu Item 3"/>
      <mu-list-item @click.native="handleClose" title="Close"/>
    </mu-list>
  </mu-drawer>
</template>

<script>
  import { isDesktop } from '../lib/utils.js';

  export default {
    props: {
      open: {
        type: Boolean,
        default: false
      },
      docked: {
        type: Boolean,
        default: false
      }
    },

    methods: {
      toggle() {
        this.$emit('toggle');
      },

      handleClose() {
        this.$emit('close');
      },

      handleHide() {
        this.$emit('hide');
      }
    },
  };
</script>