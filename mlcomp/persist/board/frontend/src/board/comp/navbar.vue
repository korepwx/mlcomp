<template>
  <header>
    <nav class="navbar navbar-toggleable-md navbar-inverse bg-inverse">
      <button class="navbar-toggler navbar-toggler-right" type="button" data-toggle="collapse" data-target="#navbarsExampleDefault" aria-controls="navbarsExampleDefault" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <a class="navbar-brand" href="#">ML Board</a>
      <div class="collapse navbar-collapse" id="navbarsExampleDefault">
        <ul class="navbar-nav mr-auto">
          <router-link to="/" tag="li" class="nav-item" active-class="active" exact>
            <a class="nav-link">All</a>
          </router-link>
          <router-link to="/active" tag="li" class="nav-item" active-class="active" exact>
            <a class="nav-link">Active</a>
          </router-link>
          <router-link to="/completed" tag="li" class="nav-item" active-class="active" exact>
            <a class="nav-link">Completed</a>
          </router-link>
        </ul>
        <form class="form-inline w-md-100">
          <input class="form-control w-100" type="text" placeholder="Search experiments">
        </form>
      </div>
    </nav>
  </header>
</template>

<script>
  import { mapState } from 'vuex';

  export default {
    data() {
      return {};
    },

    computed: mapState({
      system: 'system'
    })
  }
</script>