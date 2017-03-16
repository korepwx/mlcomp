<template>
  <div class="page-content">
    <!-- The navigation bar -->
    <navbar></navbar>

    <!-- The main content -->
    <div class="content-wrapper">
      <div v-if="isLoading">
        Loading, please wait ...
      </div>
      <div v-if="errorMessage">
        Error: {{ errorMessage }}
      </div>
      <transition v-if="!isLoading && !errorMessage" name="md-router" appear>
        <router-view></router-view>
      </transition>
    </div>
  </div>
</template>

<script>
  import { mapState } from 'vuex';
  import Navbar from "./navbar.vue";

  export default {
    components: {
      Navbar
    },

    data () {
      return {};
    },

    computed: mapState({
      isLoading: 'isLoading',
      errorMessage: 'errorMessage',
    })
  }
</script>