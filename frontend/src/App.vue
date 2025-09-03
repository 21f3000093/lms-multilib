<template>
  <div id="app" class="app-background">
    <!-- Gradient background -->
    <div class="gradient-bg"></div>

    <!-- App content above background -->
    <div class="app-content" :class="{ 'no-sidebar': !isLoggedIn }">
      <NavBar class="navbar"  />
      <router-view />
    </div>
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue';

export default {
  components: { NavBar },
  data() {
    return {
      isLoggedIn: false
    }
  },
  mounted() {
    this.checkLoginStatus()
  },
  methods: {
    checkLoginStatus() {
      this.isLoggedIn = !!localStorage.getItem('role')
    }
  },
  watch: {
    '$route'() {
      this.checkLoginStatus()
    }
  }
};
</script>

<style>
body, html, #app {
  margin: 0;
  padding: 0;
  padding-top: 0vh;
}

/* Main wrapper styling */
.app-background {
  position: relative;
  min-height: 100vh;
  width: 100%;
  overflow: hidden;
  padding-top: 5rem;
}

/* Background gradient */
.gradient-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  /* background: radial-gradient(125% 125% at 50% 90%, #fff 40%, #6366f1 100%); */
  /* background: linear-gradient(90deg, #7e00d0 0%, #007bff 100%); */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  

}

/* Content on top of the gradient */
.app-content {
  position: relative;
  z-index: 10;
  margin-left: 260px; /* Same as sidebar width */
  transition: margin-left 0.3s ease;
  padding-top: 10px; /* Account for navbar height */
}

/* When user is not logged in or no sidebar */
.app-content.no-sidebar {
  margin-left: 0;
  padding-top: 10px; /* Keep navbar spacing */
}

/* Existing styles */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}



/* Mobile responsive */
@media (max-width: 1080px) {
  .app-content {
    margin-left: 0 !important;
    padding-top: 0px; /* More space for mobile navbar */
  }
}
</style>
