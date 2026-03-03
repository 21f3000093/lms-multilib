<template>
  <div id="app" class="app-background">
    <div
      class="app-content"
      :class="{ 'no-sidebar': !isLoggedIn, 'has-bottom-nav': isLoggedIn && role === 'admin' }"
    >
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
      isLoggedIn: false,
      role: ''
    }
  },
  mounted() {
    this.checkLoginStatus()
  },
  methods: {
    checkLoginStatus() {
      this.isLoggedIn = !!localStorage.getItem('role')
      this.role = localStorage.getItem('role') || ''
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
  background: #0f172a;
}

.app-background {
  --global-bg: #0f172a;
  --sidebar-width: 260px;
  --topbar-height: 68px;

  position: relative;
  min-height: 100vh;
  width: 100%;
  overflow-x: hidden;
  background: var(--global-bg);
}

.app-background::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background:
    radial-gradient(48rem 26rem at 8% 14%, rgba(34, 211, 238, 0.14), transparent 70%),
    radial-gradient(44rem 26rem at 90% 8%, rgba(59, 130, 246, 0.14), transparent 68%),
    radial-gradient(40rem 24rem at 66% 88%, rgba(14, 165, 233, 0.10), transparent 70%),
    linear-gradient(180deg, #0f172a 0%, #0b1222 100%);
  filter: saturate(112%);
  animation: app-mesh-drift 18s ease-in-out infinite alternate;
}

.app-content {
  position: relative;
  z-index: 1;
  margin-left: var(--sidebar-width);
  transition: margin-left 0.3s ease;
  padding-top: calc(var(--topbar-height) + 6px);
}

.app-content.no-sidebar {
  margin-left: 0;
  padding-top: calc(var(--topbar-height) + 6px);
}

#app {
  font-family: Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #e2e8f0;
}

@keyframes app-mesh-drift {
  0% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  100% {
    transform: translate3d(-1.5%, 1.2%, 0) scale(1.04);
  }
}

@media print {
  nav,
  .navbar,
  header,
  .nav,
  .no-print {
    display: none !important;
  }
}



@media (max-width: 1080px) {
  .app-content {
    margin-left: 0 !important;
    padding-top: var(--topbar-height);
  }
}

@media (max-width: 767px) {
  .app-content.has-bottom-nav {
    /* padding-bottom: calc(82px + env(safe-area-inset-bottom)); */
    padding-bottom: 0;

  }
}
</style>
