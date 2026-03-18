<template>
  <div class="layout-wrapper">
    <aside v-if="isLoggedIn" class="sidebar desktop-only">
      <router-link :to="homeRoute" class="brand-link" @click="closeMenu">
        <span class="brand-icon-wrap">
          <BookOpen class="brand-icon" aria-hidden="true" />
        </span>
        <span class="brand-text-wrap">
          <span class="brand-title">Smart Library</span>
          <span class="brand-subtitle">{{ library_name || 'Workspace' }}</span>
        </span>
      </router-link>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in sidebarItems"
          :key="item.key"
          :to="item.to"
          class="sidebar-link"
          :class="{ 'is-active': isNavItemActive(item) }"
        >
          <component :is="item.icon" class="nav-icon" aria-hidden="true" />
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="item.unread && unreadCount > 0" class="nav-badge">{{ unreadBadge }}</span>
        </router-link>
      </nav>
    </aside>

    <nav class="topbar" :class="{ 'with-sidebar': isLoggedIn }">
      <div class="topbar-content">
        <button class="menu-btn mobile-only" type="button" @click="toggleMenu" :aria-label="menuOpen ? 'Close menu' : 'Open menu'">
          <X v-if="menuOpen" class="menu-icon" aria-hidden="true" />
          <Menu v-else class="menu-icon" aria-hidden="true" />
        </button>
        <div v-if="isLoggedIn" class="desktop-only"> </div>

        <router-link :to="homeRoute" class="topbar-brand" @click="closeMenu">
          <BookOpen class="topbar-brand-icon" aria-hidden="true" />
          <span>Smart Library App</span>
        </router-link>

        <div class="topbar-actions" v-if="!isLoggedIn">
          <router-link to="/pricing-plans" class="public-link desktop-only">Pricing</router-link>
          <router-link to="/about" class="public-link desktop-only">About</router-link>
          <router-link to="/signup" class="public-link desktop-only">Signup</router-link>
          <button type="button" class="theme-toggle public-link desktop-only" @click="handleThemeToggle(false)">
            <Sun v-if="themeState.current === 'dark'" class="theme-toggle-icon" aria-hidden="true" />
            <Moon v-else class="theme-toggle-icon" aria-hidden="true" />
            <!-- <span>{{ nextThemeLabel }}</span> -->
          </button>
          <router-link to="/login" class="public-link public-link-primary desktop-only">Login</router-link>
        </div>

        <div v-if="isLoggedIn" class="topbar-actions">
          <button
            v-if="role === 'admin'"
            type="button"
            class="notification-btn"
            @click="openNotifications"
            aria-label="Notifications"
          >
            <Bell class="notification-icon" aria-hidden="true" />
            <span v-if="unreadCount > 0" class="notification-badge">{{ unreadBadge }}</span>
          </button>

          <div class="user-menu" @click.stop>
            <button type="button" class="user-btn" @click="toggleDropdown">
              <img src="../assets/profile/account.png" alt="User avatar" class="user-avatar" loading="lazy" />
            </button>

            <div class="dropdown" :class="{ show: dropdownOpen }" @click.stop>
              <div class="dropdown-head">
                <img src="../assets/profile/account.png" alt="User avatar" class="dropdown-avatar" loading="lazy" />
                <div>
                  <p class="dropdown-title">{{ library_name || 'Smart Library' }}</p>
                  <p class="dropdown-subtitle">{{ username }}</p>
                </div>
              </div>

              <button type="button" class="dropdown-item" @click="goChangePassword">
                <KeyRound class="dropdown-icon" aria-hidden="true" />
                <span>Change Password</span>
              </button>
              <button v-if="role === 'admin'" type="button" class="dropdown-item" @click="goBilling">
                <CircleDollarSign class="dropdown-icon" aria-hidden="true" />
                <span>Billing Center</span>
              </button>
              <button type="button" class="dropdown-item" @click="goPricing">
                <CircleDollarSign class="dropdown-icon" aria-hidden="true" />
                <span>Pricing & Plans</span>
              </button>
              <button type="button" class="dropdown-item" @click="openNotifications">
                <Bell class="dropdown-icon" aria-hidden="true" />
                <span>Notifications</span>
                <span v-if="role === 'admin' && unreadCount > 0" class="dropdown-badge">{{ unreadBadge }}</span>
              </button>
              <button type="button" class="dropdown-item" @click="goAbout">
                <Info class="dropdown-icon" aria-hidden="true" />
                <span>About</span>
              </button>
              <button type="button" class="dropdown-item" @click="handleThemeToggle()">
                <Sun v-if="themeState.current === 'dark'" class="dropdown-icon" aria-hidden="true" />
                <Moon v-else class="dropdown-icon" aria-hidden="true" />
                <span>{{ nextThemeLabel }}</span>
              </button>

              <div class="dropdown-divider"></div>

              <button type="button" class="dropdown-item danger" @click="logout">
                <LogOut class="dropdown-icon" aria-hidden="true" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="mobile-panel" :class="{ show: menuOpen }" v-if="isLoggedIn">
        <router-link
          v-for="item in mobileItems"
          :key="item.key"
          :to="item.to"
          class="mobile-link"
          :class="{ 'is-active': isNavItemActive(item) }"
          @click="closeMenu"
        >
          <component :is="item.icon" class="nav-icon" aria-hidden="true" />
          <span class="mobile-label">{{ item.label }}</span>
          <span v-if="item.unread && unreadCount > 0" class="mobile-badge">{{ unreadBadge }}</span>
        </router-link>
      </div>

      <div class="mobile-panel" :class="{ show: menuOpen }" v-else>
        <router-link
          v-for="item in publicMobileItems"
          :key="item.key"
          :to="item.to"
          class="mobile-link"
          :class="{ 'is-active': isNavItemActive(item) }"
          @click="closeMenu"
        >
          <component :is="item.icon" class="nav-icon" aria-hidden="true" />
          <span class="mobile-label">{{ item.label }}</span>
        </router-link>
        <button type="button" class="mobile-link mobile-theme-toggle" @click="handleThemeToggle(true)">
          <Sun v-if="themeState.current === 'dark'" class="nav-icon" aria-hidden="true" />
          <Moon v-else class="nav-icon" aria-hidden="true" />
          <span class="mobile-label">{{ nextThemeLabel }}</span>
        </button>
      </div>
    </nav>

    <nav v-if="isLoggedIn && role === 'admin'" class="bottom-nav mobile-only">
      <router-link
        v-for="item in bottomItems"
        :key="item.key"
        :to="item.to"
        class="bottom-link"
        :class="{ 'is-active': isNavItemActive(item) }"
        :aria-label="item.label"
      >
        <component :is="item.icon" class="bottom-icon" aria-hidden="true" />
      </router-link>
    </nav>
  </div>
</template>

<script>
import API from '../api'
import { unsubscribeCurrentBrowserPush } from '../utils/pushNotifications'
import { initTheme, themeState, toggleTheme } from '../utils/theme'
import {
  Armchair,
  Banknote,
  Bell,
  BookOpen,
  CircleDollarSign,
  Grid3X3,
  Info,
  KeyRound,
  LayoutDashboard,
  LogIn,
  LogOut,
  Menu,
  Moon,
  ReceiptText,
  Shield,
  SlidersHorizontal,
  Sun,
  UserCircle2,
  UserPlus,
  Users,
  X,
} from 'lucide-vue-next'

export default {
  components: {
    Armchair,
    Banknote,
    Bell,
    BookOpen,
    CircleDollarSign,
    Grid3X3,
    Info,
    KeyRound,
    LayoutDashboard,
    LogIn,
    LogOut,
    Menu,
    Moon,
    ReceiptText,
    Shield,
    SlidersHorizontal,
    Sun,
    UserCircle2,
    UserPlus,
    Users,
    X,
  },
  data() {
    return {
      isLoggedIn: false,
      menuOpen: false,
      dropdownOpen: false,
      username: localStorage.getItem('username'),
      library_name: localStorage.getItem('library_name') || 'Smart Library',
      role: localStorage.getItem('role') || '',
      themeState,
      unreadCount: 0,
      unreadPollIntervalId: null,
    }
  },
  computed: {
    homeRoute() {
      if (!this.isLoggedIn) {
        return '/login'
      }
      return this.role === 'superadmin' ? '/superadmin' : '/dashboard'
    },
    unreadBadge() {
      return this.unreadCount > 99 ? '99+' : String(this.unreadCount)
    },
    nextThemeLabel() {
      return this.themeState.current === 'dark' ? 'Light theme' : 'Dark theme'
    },
    adminItems() {
      return [
        { key: 'dashboard', to: '/dashboard', label: 'Dashboard', icon: 'LayoutDashboard' },
        { key: 'register', to: '/register', label: 'Register', icon: 'UserPlus' },
        { key: 'students', to: '/students', label: 'Student List', icon: 'Users' },
        { key: 'monthly-payments', to: '/monthly-payments', label: 'Monthly Fees', icon: 'Banknote' },
        { key: 'fee-reminders', to: '/reminders', label: 'Fee Reminders', icon: 'Bell' },
        { key: 'seat-map', to: '/seat-map', label: 'Seat Map', icon: 'Grid3X3' },
        { key: 'monthly-expenses', to: '/monthly-expenses', label: 'Expenses', icon: 'ReceiptText' },
        { key: 'billing', to: '/billing', label: 'Billing Center', icon: 'CircleDollarSign' },
        // { key: 'notifications', to: '/notifications', label: 'Notifications', icon: 'Bell', unread: true },
      ]
    },
    superAdminItems() {
      return [
        { key: 'superadmin-dashboard', to: '/superadmin', label: 'Dashboard', icon: 'Shield' },
        { key: 'superadmin-signup-queue', to: '/superadmin/signup-requests', label: 'Signup Review', icon: 'UserCircle2' },
        { key: 'superadmin-subscriptions', to: '/superadmin/subscriptions', label: 'Subscriptions', icon: 'CircleDollarSign' },
        { key: 'superadmin-plan-catalog', to: '/superadmin/plan-catalog', label: 'Plan Catalog', icon: 'SlidersHorizontal' },
        { key: 'superadmin-notifications', to: '/superadmin/notifications', label: 'Notifications', icon: 'Bell' },
      ]
    },
    sidebarItems() {
      return this.role === 'superadmin' ? this.superAdminItems : this.adminItems
    },
    mobileItems() {
      return this.sidebarItems
    },
    publicMobileItems() {
      return [
        { key: 'public-signup', to: '/signup', label: 'Signup', icon: 'UserPlus' },
        { key: 'public-login', to: '/login', label: 'Login', icon: 'LogIn' },
        { key: 'public-pricing', to: '/pricing-plans', label: 'Plans & Pricing', icon: 'CircleDollarSign' },
        { key: 'public-about', to: '/about', label: 'About', icon: 'Info' },
      ]
    },
    bottomItems() {
      return [
        { key: 'dashboard', to: '/dashboard', label: 'Dashboard', icon: 'LayoutDashboard' },
        { key: 'register', to: '/register', label: 'Register', icon: 'UserPlus' },
        { key: 'students', to: '/students', label: 'Student List', icon: 'Users' },
        { key: 'monthly-payments', to: '/monthly-payments', label: 'Monthly Fees', icon: 'Banknote' },
        { key: 'fee-reminders', to: '/reminders', label: 'Fee Reminders', icon: 'Bell' },
        { key: 'seat-map', to: '/seat-map', label: 'Seat Map', icon: 'Armchair' },
      ]
    },
  },
  mounted() {
    initTheme()
    this.checkLoginStatus()
    this.fetchUnreadCount()
    document.addEventListener('click', this.handleDocumentClick)
    window.addEventListener('notifications:unread-count-updated', this.syncUnreadCount)
    this.unreadPollIntervalId = window.setInterval(() => {
      this.fetchUnreadCount()
    }, 60000)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleDocumentClick)
    window.removeEventListener('notifications:unread-count-updated', this.syncUnreadCount)
    if (this.unreadPollIntervalId) {
      clearInterval(this.unreadPollIntervalId)
      this.unreadPollIntervalId = null
    }
  },
  methods: {
    closeMenu() {
      this.menuOpen = false
    },
    toggleMenu() {
      this.menuOpen = !this.menuOpen
      this.dropdownOpen = false
    },
    toggleDropdown() {
      this.dropdownOpen = !this.dropdownOpen
      this.menuOpen = false
    },
    handleThemeToggle(closeMenu = true) {
      toggleTheme()
      if (closeMenu) {
        this.dropdownOpen = false
        this.menuOpen = false
      }
    },
    handleDocumentClick(event) {
      if (!this.$el.contains(event.target)) {
        this.dropdownOpen = false
        this.menuOpen = false
      }
    },
    syncUnreadCount(event) {
      this.unreadCount = Number(event.detail?.count || 0)
    },
    async fetchUnreadCount() {
      if (!this.isLoggedIn || this.role !== 'admin') {
        this.unreadCount = 0
        return
      }

      try {
        const res = await API.get('/notifications/inbox/unread-count')
        this.unreadCount = Number(res.data?.unread_count || 0)
      } catch (err) {
        this.unreadCount = 0
      }
    },
    checkLoginStatus() {
      this.isLoggedIn = !!localStorage.getItem('role')
      this.library_name = localStorage.getItem('library_name') || 'Smart Library'
      this.role = localStorage.getItem('role') || ''
      this.username = localStorage.getItem('username')
      if (this.role !== 'admin') {
        this.unreadCount = 0
      }
    },
    isNavItemActive(item) {
      const currentPath = this.$route.path

      if (item.key === 'students') {
        return currentPath === '/students' || currentPath.startsWith('/students/')
      }

      if (item.key === 'monthly-payments') {
        return currentPath === '/monthly-payments' || currentPath.startsWith('/receipts/')
      }

      if (item.key === 'superadmin-dashboard') {
        return (
          currentPath.startsWith('/superadmin') &&
          !currentPath.startsWith('/superadmin/notifications') &&
          !currentPath.startsWith('/superadmin/signup-requests') &&
          !currentPath.startsWith('/superadmin/subscriptions') &&
          !currentPath.startsWith('/superadmin/plan-catalog')
        )
      }

      if (item.key === 'superadmin-signup-queue') {
        return currentPath === '/superadmin/signup-requests'
      }

      if (item.key === 'superadmin-subscriptions') {
        return currentPath === '/superadmin/subscriptions'
      }

      if (item.key === 'superadmin-plan-catalog') {
        return currentPath === '/superadmin/plan-catalog'
      }

      if (item.key === 'superadmin-notifications') {
        return currentPath === '/superadmin/notifications'
      }

      return currentPath === item.to
    },
    goChangePassword() {
      this.dropdownOpen = false
      this.$router.push('/change-password')
    },
    goPricing() {
      this.dropdownOpen = false
      this.$router.push('/pricing-plans')
    },
    goBilling() {
      this.dropdownOpen = false
      this.$router.push('/billing')
    },
    goAbout() {
      this.dropdownOpen = false
      this.$router.push('/about')
    },
    openNotifications() {
      this.dropdownOpen = false
      if (this.role === 'superadmin') {
        this.$router.push('/superadmin/notifications')
        return
      }
      if (this.role === 'admin') {
        this.$router.push('/notifications')
      }
    },
    async logout() {
      try {
        if (confirm('Are you sure you want to log out?')) {
          await unsubscribeCurrentBrowserPush()
          await API.post('/auth/logout')

          localStorage.removeItem('role')
          localStorage.removeItem('username')
          localStorage.removeItem('library_id')
          localStorage.removeItem('library_name')

          this.isLoggedIn = false
          this.menuOpen = false
          this.dropdownOpen = false
          this.library_name = 'Smart Library'
          this.username = ''
          this.unreadCount = 0

          this.$router.push('/login')
        }
      } catch (err) {
        alert('Logout failed. Try again.')
      }
    },
  },
  watch: {
    $route() {
      this.checkLoginStatus()
      this.fetchUnreadCount()
      this.closeMenu()
      this.dropdownOpen = false
    },
  },
}
</script>

<style scoped>
.layout-wrapper {
  position: relative;
  color: var(--theme-text-primary);
}

.sidebar {
  width: 260px;
  position: fixed;
  top: 0;
  left: 0;
  height: 100dvh;
  z-index: 1060;
  display: flex;
  flex-direction: column;
  padding: 1rem 0.85rem;
  border-right: 1px solid var(--theme-border);
  background:
    radial-gradient(120% 80% at 20% 0%, rgba(56, 189, 248, 0.12), transparent 45%),
    var(--theme-nav-surface);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 0.72rem;
  text-decoration: none;
  color: var(--theme-text-primary);
  padding: 0.45rem 0.5rem;
  border-radius: 12px;
}

.brand-icon-wrap {
  width: 2.1rem;
  height: 2.1rem;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: var(--theme-surface-soft-strong);
  border: 1px solid var(--theme-border);
}

.brand-icon {
  width: 1.1rem;
  height: 1.1rem;
  color: var(--theme-brand-pill-text);
}

.brand-text-wrap {
  display: grid;
  line-height: 1.05;
}

.brand-title {
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.brand-subtitle {
  font-size: 0.73rem;
  color: var(--theme-text-secondary);
  margin-top: 0.2rem;
  max-width: 172px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-nav {
  margin-top: 1rem;
  display: grid;
  gap: 0.35rem;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 0.62rem;
  text-decoration: none;
  color: var(--theme-text-soft);
  padding: 0.62rem 0.68rem;
  border-radius: 10px;
  border: 1px solid transparent;
  transition: all 180ms ease;
}

.sidebar-link:hover {
  background: var(--theme-surface-soft-strong);
  color: var(--theme-text-strong);
}

.sidebar-link.is-active {
  border-color: var(--theme-brand-border);
  background: var(--theme-brand-soft);
  color: var(--theme-text-strong);
}

.nav-icon {
  width: 1.02rem;
  height: 1.02rem;
  flex: 0 0 auto;
}

.nav-label {
  font-size: 0.9rem;
  font-weight: 600;
}

.nav-badge,
.notification-badge,
.dropdown-badge,
.mobile-badge {
  margin-left: auto;
  min-width: 20px;
  height: 20px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
  font-size: 0.72rem;
  font-weight: 700;
  color: #fff;
  background: #ef4444;
}

.topbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 68px;
  z-index: 1070;
  border-bottom: 1px solid var(--theme-border);
  background: var(--theme-nav-surface);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.topbar.with-sidebar {
  left: 285px;
}

.topbar-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  gap: 0.9rem;
}

.topbar-brand {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--theme-text-primary);
  text-decoration: none;
  font-weight: 700;
  font-size: 0.97rem;
}

.topbar-brand-icon {
  width: 1.05rem;
  height: 1.05rem;
  color: var(--theme-brand-pill-text);
}

.topbar-actions {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
}

.public-link {
  text-decoration: none;
  color: var(--theme-text-soft);
  font-size: 0.88rem;
  font-weight: 600;
  padding: 0.4rem 0.65rem;
  border-radius: 9px;
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  font-family: inherit;
}

.public-link:hover {
  border-color: var(--theme-border-strong);
  color: var(--theme-text-strong);
}

.public-link-primary {
  border-color: var(--theme-brand-border);
  background: var(--theme-brand-soft-strong);
  color: var(--theme-text-strong);
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.42rem;
}

.theme-toggle-icon {
  width: 0.95rem;
  height: 0.95rem;
}

.menu-btn {
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 10px;
  border: 1px solid var(--theme-border-strong);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--theme-surface-soft);
  color: var(--theme-text-strong);
  cursor: pointer;
}

.menu-icon {
  width: 1.15rem;
  height: 1.15rem;
  pointer-events: none;
}

.notification-btn {
  position: relative;
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 10px;
  border: 1px solid var(--theme-border-strong);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--theme-surface-soft);
  color: var(--theme-text-primary);
  cursor: pointer;
}

.notification-icon {
  width: 1rem;
  height: 1rem;
}

.notification-badge {
  position: absolute;
  top: -6px;
  right: -8px;
  min-width: 18px;
  height: 18px;
}

.user-menu {
  position: relative;
}

.user-btn {
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 999px;
  border: 1px solid var(--theme-border-strong);
  overflow: hidden;
  cursor: pointer;
  padding: 0;
  background: var(--theme-surface-soft);
}

.user-avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  min-width: 260px;
  border-radius: 14px;
  border: 1px solid var(--theme-border);
  background: var(--theme-panel-solid);
  box-shadow: var(--theme-shadow-soft);
  padding: 0.45rem;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-8px) scale(0.98);
  transition: all 180ms ease;
}

.dropdown.show {
  opacity: 1;
  visibility: visible;
  transform: translateY(0) scale(1);
}

.dropdown-head {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  border-radius: 10px;
  padding: 0.55rem;
  background: var(--theme-surface-soft);
  margin-bottom: 0.3rem;
}

.dropdown-avatar {
  width: 34px;
  height: 34px;
  border-radius: 999px;
}

.dropdown-title {
  margin: 0;
  color: var(--theme-text-primary);
  font-size: 0.84rem;
  font-weight: 700;
}

.dropdown-subtitle {
  margin: 0.2rem 0 0;
  color: var(--theme-text-secondary);
  font-size: 0.75rem;
}

.dropdown-item {
  width: 100%;
  border: none;
  background: transparent;
  color: var(--theme-text-soft);
  border-radius: 10px;
  padding: 0.57rem 0.6rem;
  display: flex;
  align-items: center;
  gap: 0.55rem;
  font-size: 0.86rem;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
}

.dropdown-item:hover {
  background: var(--theme-surface-soft-strong);
  color: var(--theme-text-strong);
}

.dropdown-item.danger {
  color: #fda4af;
}

.dropdown-item.danger:hover {
  background: var(--theme-danger-soft);
  color: var(--theme-danger-text);
}

.dropdown-icon {
  width: 0.95rem;
  height: 0.95rem;
}

.dropdown-divider {
  height: 1px;
  background: var(--theme-border);
  margin: 0.35rem 0;
}

.mobile-panel {
  position: fixed;
  top: 68px;
  left: 0;
  right: 0;
  transform: translateX(-180%);
  transition: transform 220ms ease;
  z-index: 1065;
  border-bottom: 1px solid var(--theme-border);
  background: var(--theme-nav-surface-strong);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.mobile-panel.show {
  transform: translateY(0);
}

.mobile-link {
  display: flex;
  align-items: center;
  gap: 0.58rem;
  text-decoration: none;
  color: var(--theme-text-soft);
  border-bottom: 1px solid var(--theme-border-soft);
  padding: 0.85rem 1rem;
  background: transparent;
  font: inherit;
  width: 100%;
  cursor: pointer;
}

.mobile-link.is-active {
  background: var(--theme-brand-soft);
  color: var(--theme-text-strong);
}

.mobile-label {
  font-size: 0.92rem;
  font-weight: 600;
}

.bottom-nav {
  position: fixed;
  left: 0.8rem;
  right: 0.8rem;
  bottom: calc(0.55rem + env(safe-area-inset-bottom));
  z-index: 1068;
  border-radius: 16px;
  border: 1px solid var(--theme-border);
  background: var(--theme-panel-solid);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  padding: 0.4rem;
  box-shadow: var(--theme-shadow-elevated);
}

.bottom-link {
  height: 2.55rem;
  border-radius: 10px;
  display: grid;
  place-items: center;
  color: var(--theme-text-secondary);
  text-decoration: none;
}

.bottom-link.is-active {
  background: var(--theme-brand-soft-strong);
  color: var(--theme-text-primary);
}

.bottom-icon {
  width: 1.12rem;
  height: 1.12rem;
}

.desktop-only {
  display: block;
}

.mobile-only {
  display: none;
}

@media (max-width: 1080px) {
  .desktop-only {
    display: none !important;
  }

  .mobile-only {
    display: inline-flex !important;
  }

  .bottom-nav.mobile-only {
    display: grid !important;
    margin-bottom: 1rem;
  }

  .topbar {
    left: 0 !important;
  }
}

@media (max-width: 767px) {
  .topbar-content {
    padding: 0 0.8rem;
  }

  .topbar-brand {
    font-size: 0.9rem;
  }
}

.sidebar::-webkit-scrollbar,
.mobile-panel::-webkit-scrollbar {
  width: 4px;
}

.sidebar::-webkit-scrollbar-track,
.mobile-panel::-webkit-scrollbar-track {
  background: var(--theme-surface-soft-strong);
}

.sidebar::-webkit-scrollbar-thumb,
.mobile-panel::-webkit-scrollbar-thumb {
  background: var(--theme-surface-muted);
  border-radius: 999px;
}
</style>
