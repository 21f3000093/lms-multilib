<template>
  <div id="app" class="app-background">
    <div
      class="app-content"
      :class="{
        'no-sidebar': !isLoggedIn || !shouldShowNav,
        'has-bottom-nav': isLoggedIn && role === 'admin' && shouldShowNav,
        'no-topbar': !shouldShowNav
      }"
    >
      <NavBar v-if="shouldShowNav" class="navbar" />
      <router-view />
    </div>
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue';
import { initTheme } from './utils/theme'

export default {
  components: { NavBar },
  computed: {
    shouldShowNav() {
      return !this.$route.meta?.hideNav
    }
  },
  data() {
    return {
      isLoggedIn: false,
      role: ''
    }
  },
  mounted() {
    initTheme()
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
  background: var(--theme-page-bg);
}

.app-background {
  --global-bg: var(--theme-page-bg);
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
  background: var(--theme-mesh-background);
  filter: saturate(112%);
  animation: app-mesh-drift 18s ease-in-out infinite alternate;
}

.app-content {
  position: relative;
  z-index: 1;
  margin-left: var(--sidebar-width);
  transition: margin-left 0.3s ease;
  padding-top: calc(var(--topbar-height));
}

.app-content.no-sidebar {
  margin-left: 0;
  padding-top: calc(var(--topbar-height));
}

.app-content.no-topbar {
  padding-top: 0;
}

#app {
  font-family: Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: var(--theme-text-primary);
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

  .app-content.no-topbar {
    padding-top: 0 !important;
  }
}

@media (max-width: 767px) {
  .app-content.has-bottom-nav {
    /* padding-bottom: calc(82px + env(safe-area-inset-bottom)); */
    padding-bottom: 0;

  }
}
</style>
