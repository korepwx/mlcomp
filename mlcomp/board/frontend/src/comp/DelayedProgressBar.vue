<template>
  <mu-linear-progress v-if="isLoading"></mu-linear-progress>
</template>

<script>
  export default {
    props: ['loading'],
    
    data() {
      return {
        isLoading: false
      }
    },
    
    created() {
      this.showInterval = null;
      this.setLoadingFlag(this.loading);
    },

    destroyed() {
      if (this.showInterval) {
        clearInterval(this.showInterval);
        this.showInterval = null;
      }
    },

    methods: {
      setLoadingFlag(val) {
        if (val) {
          if (!this.showInterval) {
            this.showInterval = setInterval(() => {
              this.isLoading = this.loading;
              clearInterval(this.showInterval);
              this.showInterval = null;
            }, 500)
          }
        } else {
          if (this.showInterval) {
            clearInterval(this.showInterval);
            this.showInterval = null;
          }
          this.isLoading = false;
        }
      }
    },
    
    watch: {
      loading(val) {
        this.setLoadingFlag(val);
      }
    },
  }
</script>