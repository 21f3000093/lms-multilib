<template>
  <div id="app" class="app-background">
    <!-- Gradient background -->
    <div class="gradient-bg"></div>

    <!-- App content above background -->
    <div class="app-content">
      <NavBar />
      <router-view />
    </div>
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue';

export default {
  components: { NavBar }
};
</script>

<style>
/* Main wrapper styling */
.app-background {
  position: relative;
  min-height: 100vh;
  width: 100%;
  overflow: hidden;
}

/* Background gradient */
.gradient-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  background: radial-gradient(125% 125% at 50% 90%, #fff 40%, #475569 100%);
}

/* Content on top of the gradient */
.app-content {
  position: relative;
  z-index: 10;
}

/* Existing styles */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}
</style>
