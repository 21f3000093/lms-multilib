<template>
  <div class="layout-wrapper">
    <!-- Desktop Sidebar -->
    <aside v-if="isLoggedIn" class="sidebar desktop-only">
      <div class="sidebar-header ">
        <router-link v-if="!isLoggedIn || role === 'admin'" to="/dashboard" class="sidebar-logo" style="background-color: transparent;">
          {{ this.library_name }}
        </router-link>
        <router-link v-if="isLoggedIn && role === 'superadmin'" to="/superadmin" class="sidebar-logo" style="background-color: transparent;">
          {{ this.library_name }}
        </router-link>
      </div>
      
      <nav class="sidebar-nav">
        <router-link v-if="isLoggedIn && role === 'admin'" to="/dashboard" class="sidebar-link">
          <span class="sidebar-icon">📊</span>
          <span class="sidebar-text">Dashboard</span>
        </router-link>
        <router-link v-if="isLoggedIn && role === 'admin'" to="/register" class="sidebar-link">
          <span class="sidebar-icon">➕</span>
          <span class="sidebar-text">Register</span>
        </router-link>
        <router-link v-if="isLoggedIn && role === 'admin'" to="/students" class="sidebar-link">
          <span class="sidebar-icon">📋</span>
          <span class="sidebar-text">Student List</span>
        </router-link>
        <router-link v-if="isLoggedIn && role === 'admin'" to="/monthly-payments" class="sidebar-link">
          <span class="sidebar-icon">💰</span>
          <span class="sidebar-text">Monthly Fees</span>
        </router-link>
        <router-link v-if="isLoggedIn && role === 'admin'" to="/seat-map" class="sidebar-link">
          <span class="sidebar-icon">🪑</span>
          <span class="sidebar-text">Seat Map</span>
        </router-link>
        <router-link v-if="isLoggedIn && role === 'admin'" to="/monthly-expenses" class="sidebar-link">
          <span class="sidebar-icon">💰</span>
          <span class="sidebar-text">Expenses</span>
        </router-link>
      </nav>
    </aside>

    <!-- Top Navbar -->
    <nav class="navbar" :class="{ 'with-sidebar': isLoggedIn }">
      <div class="navbar-top">

        <!-- <button v-if="isLoggedIn" class="hamburger mobile-only" @click="toggleMenu">☰</button> -->
        <button v-if="isLoggedIn" class="hamburger mobile-only" :class="{ 'menu-open': menuOpen }" @click="toggleMenu"> {{ menuOpen ? '⛌' : '☰' }} </button>
        
        <!-- Add this NEW desktop logo for when not logged in -->
        <router-link v-if="!isLoggedIn" to="/login" 
                    style="text-decoration: none; background-color: unset;" 
                    class="desktop-logo-when-not-logged-in desktop-only">
          <!-- <div class="logo ">{{ this.library_name }}</div> -->
           <div class="logo">Smart Library App</div>
        </router-link>
        <!-- Mobile logo (hidden on desktop when logged in) -->
        <router-link v-if="!isLoggedIn || role === 'admin'" to="/dashboard" 
                     style="text-decoration: none; background-color: unset; margin: auto; " 
                     class="mobile-logo" @click="closeMenu">
          <div class="logo">Smart Library App</div>
          <!-- <div class="logo">{{ this.library_name }}</div> -->
        </router-link>
        <router-link v-if="isLoggedIn && role === 'superadmin'" to="/superadmin" 
                     style="text-decoration: none; background-color: unset;" 
                     class="mobile-logo">
          <!-- <div class="logo">{{ this.library_name }}</div> -->
           <div class="logo">Smart Library App</div>
        </router-link> 
        
        
        
        <!-- Desktop User Dropdown -->
        <div v-if="isLoggedIn" class="user-dropdown " @click.stop="toggleDropdown">
          <div class="user-avatar">
            <img src="../assets/profile/account.png" alt="User Avatar" />
          </div>
          <!-- <span class="username">{{ username || 'User' }}</span>
          <svg class="dropdown-arrow" :class="{ 'rotated': dropdownOpen }" viewBox="0 0 24 24" fill="currentColor">
            <path d="M7 10l5 5 5-5z"/>
          </svg> -->
          
          <!-- Dropdown Menu -->
          <div class="dropdown-menu" :class="{ 'show': dropdownOpen }" @click.stop>
            <div class="dropdown-header">
              <img src="../assets/profile/account.png" alt="User Avatar" />
              <div class="user-info">
                <div class="user-name">{{ library_name || 'User' }}</div>
                <div class="user-email">{{ username }}</div>
              </div>
            </div>
            
            <div class="dropdown-divider"></div>
            
            <a href="#" class="dropdown-item" @click.prevent="viewProfile">
              <svg class="dropdown-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
              View Profile
            </a>
            
            <a href="#" class="dropdown-item" @click.prevent="ChangePassword">
              <svg class="dropdown-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.82,11.69,4.82,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z"/>
              </svg>
              Change Password
            </a>
            
            <a href="#" class="dropdown-item" @click.prevent="notifications">
              <svg class="dropdown-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12,22c1.1,0,2-0.9,2-2h-4C10,21.1,10.9,22,12,22z M18,16v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-0.83-0.67-1.5-1.5-1.5 s-1.5,0.67-1.5,1.5v0.68C7.63,5.36,6,7.92,6,11v5l-2,2v1h16v-1L18,16z"/>
              </svg>
              Notifications
            </a>
            
            <a href="#" class="dropdown-item" @click.prevent="helpCenter">
              <svg class="dropdown-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12,2C6.48,2,2,6.48,2,12s4.48,10,10,10s10-4.48,10-10S17.52,2,12,2z M13,19h-2v-2h2V19z M15.07,11.25l-0.9,0.92 C13.45,12.9,13,13.5,13,15h-2v-0.5c0-1.1,0.45-2.1,1.17-2.83l1.24-1.26c0.37-0.36,0.59-0.86,0.59-1.41c0-1.1-0.9-2-2-2 s-2,0.9-2,2H8c0-2.21,1.79-4,4-4s4,1.79,4,4C16,9.89,15.64,10.68,15.07,11.25z"/>
              </svg>
              Help Center
            </a>
            
            <div class="dropdown-divider"></div>
            
            <a href="#" class="dropdown-item logout-item" @click.prevent="logout">
              <svg class="dropdown-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17,7l-1.41,1.41L18.17,11H8v2h10.17l-2.58,2.59L17,17l5-5L17,7z M4,5h8V3H4C2.9,3,2,3.9,2,5v14c0,1.1,0.9,2,2,2h8v-2H4V5z"/>
              </svg>
              Logout
            </a>
          </div>
        </div>
        
      </div>

      <!-- Mobile Navigation Links -->
      <div class="nav-links mobile-only" :class="{ open: menuOpen }" v-show="menuOpen">
        <router-link v-if="isLoggedIn && role === 'admin'" to="/dashboard" @click="closeMenu">📊 Dashboard</router-link>
        <router-link v-if="isLoggedIn && role === 'admin'" to="/register" @click="closeMenu">➕ Register</router-link>
        <router-link v-if="isLoggedIn && role === 'admin'" to="/students" @click="closeMenu">📋 Student List</router-link>
        <router-link v-if="isLoggedIn && role === 'admin'" to="/monthly-payments" @click="closeMenu">💰 Monthly Fees</router-link>
        <router-link v-if="isLoggedIn && role === 'admin'" to="/seat-map" @click="closeMenu">🪑 Seat Map</router-link>
        <router-link v-if="isLoggedIn && role === 'admin'" to="/monthly-expenses" @click="closeMenu">💰 Expenses</router-link>
        <!-- <button v-if="isLoggedIn" class="logout-btn mobile-logout" @click="logout">🚪 Logout</button> -->
      </div>
    </nav>
  </div>
</template>

<script>
import API from '../api'
// import ChangePassword from './ChangePassword.vue'

export default {
  data() {
    return {
      isLoggedIn: false,
      menuOpen: false,
      dropdownOpen: false,
      username: localStorage.getItem('username'),
      library_name: localStorage.getItem('library_name')?.toUpperCase() || 'Library Management System',
      role: localStorage.getItem('role') ?? '',
    }
  },
  mounted() {
    this.checkLoginStatus()
    // Close dropdown when clicking outside
    document.addEventListener('click', this.handleDocumentClick)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleDocumentClick)
  },
  methods: {
    closeMenu() {
      this.menuOpen = false
    },
    toggleMenu() {
      this.menuOpen = !this.menuOpen
    },
    toggleDropdown(event) {
      event.stopPropagation()
      this.dropdownOpen = !this.dropdownOpen
    },
    handleDocumentClick(event) {
      // Close dropdown when clicking outside
      if (!this.$el.contains(event.target)) {
        this.dropdownOpen = false
      }
    },
    viewProfile() {
      console.log('View Profile clicked')
      this.dropdownOpen = false
      // Add your profile logic here
    },
    ChangePassword() {
      console.log('Change Password clicked')
      this.dropdownOpen = false
      // Add your settings logic here
      this.$router.push('/change-password')
    },
    notifications() {
      console.log('Notifications clicked')
      this.dropdownOpen = false
      // Add your notifications logic here
    },
    helpCenter() {
      console.log('Help Center clicked')
      this.dropdownOpen = false
      // Add your help center logic here
    },
    checkLoginStatus() {
      this.isLoggedIn = !!localStorage.getItem('role')
      this.library_name = localStorage.getItem('library_name')?.toUpperCase() || 'Library Management System'
      this.role = localStorage.getItem('role') ?? ''
      this.username = localStorage.getItem('username')
    },
    async logout() {
      try {
        if (confirm('Are you sure you want to log out?')) {
          // Only run logout logic if user confirms
          await API.post('/auth/logout')
          
          // Clear localStorage
          localStorage.removeItem('role')
          localStorage.removeItem('username')
          localStorage.removeItem('library_id')
          localStorage.removeItem('library_name')

          // Reset component state
          this.isLoggedIn = false
          this.menuOpen = false
          this.dropdownOpen = false
          this.library_name = 'Library Management System'
          this.username = ''
          
          // Redirect to login
          this.$router.push('/login')
        }
        // If user clicks "Cancel", nothing happens - they stay logged in
      } catch (err) {
        console.error('Logout failed', err)
        alert('Logout failed. Try again.')
      }
    },

  },
  watch: {
    '$route': 'checkLoginStatus'
  }
}
</script>

<style scoped>
.layout-wrapper {
  display: flex;
  min-height: 0vh;
  
}

/* Sidebar Styles */
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #6a11cb 0%, #2575fc 100%);
  color: white;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  overflow-y: auto;
  /* box-shadow: 2px 0 10px rgba(0,0,0,0.1); */
  z-index: 1000;
}

.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.sidebar-logo {
  color: white;
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: bold;
}

.sidebar-nav {
  padding: 20px 0;
}

.sidebar-link {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.94);
  text-decoration: none;
  transition: all 0.3s ease;
  margin: 10px 12px;
  border-radius: 8px;
}

.sidebar-link:hover {
  background-color: rgba(255, 255, 255, 0.141);
  color: white;
}

.sidebar-link.router-link-exact-active {
  background-color: rgba(255, 255, 255, 0.211);
  color: white;
}

.sidebar-icon {
  font-size: 1.1rem;
  margin-right: 12px;
  width: 20px;
}

.sidebar-text {
  font-weight: 700;
  font-size: 1.2rem;
  
}

/* Navbar Styles */
.navbar {
  background: linear-gradient(to right, #6a11cb, #2575fc);
  color: white;
  font-weight: 600;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 11px 24px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  
}

.navbar.with-sidebar {
  left: 260px;
}

.navbar-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  color: white;
  font-size: 1.4rem;
  font-weight: bold;
}

.hamburger {
  background: none;
  color: white;
  font-size: 1.5rem;
  border: none;
  cursor: pointer;
}

.hamburger.menu-open {
  /* border: 2px solid rgba(255, 255, 255, 0.8); */
  border-radius: 10px;
  padding: 3px 6px;
  font-size: 1.8rem;
  font-weight: bold;
  
}


/* User Dropdown */
.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 0px 0px;
  border-radius: 8px;
  transition: background-color 0.3s;
  position: relative;
  margin-left: auto;
  
}

.user-dropdown:hover {
  background-color: rgba(255, 255, 255, 0);
}

.user-avatar img {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  /* margin-right: 8px; */
  
}

.username {
  margin-right: 8px;
  font-weight: 500;
}

.dropdown-arrow {
  width: 16px;
  height: 16px;
  transition: transform 0.3s;
}

.dropdown-arrow.rotated {
  transform: rotate(180deg);
}

/* Dropdown Menu */
.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.15);
  min-width: 280px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.3s ease;
  z-index: 1001;
}

.dropdown-menu.show {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-header {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.dropdown-header img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 12px;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
}

.user-email {
  color: #666;
  font-size: 0.8rem;
  margin-top: 2px;
}

.dropdown-divider {
  height: 1px;
  background-color: #f0f0f0;
  margin: 8px 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: #333;
  text-decoration: none;
  transition: background-color 0.2s;
  cursor: pointer;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
}

.dropdown-item.logout-item {
  color: #e74c3c;
}

.dropdown-item.logout-item:hover {
  background-color: #fdf2f2;
}

.dropdown-icon {
  width: 18px;
  height: 18px;
  margin-right: 12px;
  opacity: 0.7;
}

/* Mobile Navigation */
.nav-links {
  flex-direction: column;
  align-items: center;
  gap: 12px;
  width: 100%;
  margin-top: 12px;
}

.nav-links a {
  color: #f5f6fa;
  text-decoration: none;
  font-weight: bold;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
  width: 80%;
  text-align: center;
}

.nav-links a:hover {
  background-color: #8181ffa8;
}

.router-link-exact-active {
  background-color: #8281ffbd;
  color: white;
}

.logout-btn {
  background-color: #e84118;
  color: white;
  border: none;
  padding: 8px 14px;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: #c23616;
}

.mobile-logout {
  width: 80%;
  text-align: center;
  margin-top: 10px;
}

/* Responsive Classes */
.desktop-only {
  display: block;
}

.mobile-only {
  display: none;
}

.mobile-logo {
  display: none;
}

/* Mobile Responsive */
@media (max-width: 1080px) {
  .sidebar {
    display: none;
  }
  
  .navbar {
    left: 0 !important;
    flex-direction: column;
    align-items: stretch;
    padding: 12px 10px;
    /* padding-bottom: 0%; */
    /* height: 35px; */
    
  }

  /* .navbar.nav-links.open {
    display: flex;
    flex-direction: column;
  } */
  
  .desktop-only {
    display: none !important;
  }
  
  .mobile-only {
    display: flex;
    flex-direction: column;
  }
  
  .mobile-logo {
    display: block;
  }
  
  .hamburger {
    display: block;
  }

  .user-avatar img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    /* margin-right: 8px; */
    
  }

  /* User Dropdown */
.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 0px 0px;
  border-radius: 8px;
  transition: background-color 0.3s;
  position: relative;
  margin-left: 0vh;
  
}
  
}
</style>
