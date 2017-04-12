<template>
  <div>
    This is the storage info: {{ storage }}
  </div>
</template>

<script>
  export default {
    props: [
      'storage',
    ],

    data() {
      return {};
    }
  }
</script>