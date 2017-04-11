<template>
  <mu-drawer :open="open" :docked="docked" @close="handleClose" @hide="handleHide">
    <!-- Keyword query -->
    <mu-sub-header>Keyword Filter</mu-sub-header>
    <div class="option-box">
      <mu-text-field hintText="Type to filter experiments" v-model="query" fullWidth></mu-text-field>
    </div>

    <!-- Status filter -->
    <mu-sub-header>Status Filter</mu-sub-header>
    <div class="option-box">
      <div><mu-checkbox name="group" nativeValue="active" v-model="activeStatus" label="Active" class="demo-checkbox"></mu-checkbox></div>
      <div><mu-checkbox name="group" nativeValue="success" v-model="successStatus" label="Completed" class="demo-checkbox"></mu-checkbox></div>
      <div><mu-checkbox name="group" nativeValue="error" v-model="errorStatus" label="Failed" class="demo-checkbox"></mu-checkbox></div>
    </div>
  </mu-drawer>
</template>

<script>
  import { ALL_STATUS } from '../lib/api.js';
  import { isDesktop } from '../lib/utils.js';

  function statusFilterProperty(status) {
    return {
      get() { return this.statusFilter.includes(status); },
      set(value) { this.$emit('changeStatusFilter', {[status]: value}); }
    };
  }

  export default {
    props: {
      open: {
        type: Boolean,
        default: false
      },
      docked: {
        type: Boolean,
        default: false
      },
      queryString: {
        type: String,
        default: ''
      },
      statusFilter: {
        type: Array,
        default: () => ALL_STATUS
      }
    },

    computed: {
      activeStatus: statusFilterProperty('active'),
      successStatus: statusFilterProperty('success'),
      errorStatus: statusFilterProperty('error'),
      query: {
        get() { return this.queryString; },
        set(value) { this.$emit('changeQueryString', value); }
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

<style lang="scss" scoped>
  .option-box {
    margin-top: 8px;
    padding-left: 16px;
    padding-right: 40px;
    font-size: 16px;
  }
</style>