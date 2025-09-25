<template>
  <div class="layout-wrapper">
    <!-- Desktop Sidebar -->
    <aside v-if="isLoggedIn" class="sidebar desktop-only">
      <div class="sidebar-header">
        <router-link 
          :to="role === 'superadmin' ? '/superadmin' : '/dashboard'" 
          class="sidebar-logo"
        >
          <!-- <div class="logo-icon">📚</div> -->
          <div class="logo-text">{{ library_name }}</div>
        </router-link>
      </div>
      
      <nav class="sidebar-nav">
        <router-link v-if="role === 'admin'" to="/dashboard" class="sidebar-link">
          <span class="sidebar-icon">
            <!-- 📊 -->
            <img src="../assets/svg/chart-2.svg" class="sidebar-icon" alt="" loading="lazy">
          </span>
          <span class="sidebar-text">Dashboard</span>
        </router-link>
        <router-link v-if="role === 'admin'" to="/register" class="sidebar-link">
          <span class="sidebar-icon">
            <!-- ➕ -->
             <img src="../assets/svg/add-plus-w.svg" class="sidebar-icon" alt="" loading="lazy">
          </span>
          <span class="sidebar-text">Register</span>
        </router-link>
        <router-link v-if="role === 'admin'" to="/students" class="sidebar-link">
          <span class="sidebar-icon">
            <!-- 📋 -->
             <img src="../assets/svg/list-w.svg" class="sidebar-icon" alt="" loading="lazy">
          </span>
          <span class="sidebar-text">Student List</span>
        </router-link>
        <router-link v-if="role === 'admin'" to="/monthly-payments" class="sidebar-link">
          <span class="sidebar-icon">
            <!-- 💰 -->
             <img src="../assets/svg/money-dollar.svg" class="sidebar-icon" alt="" loading="lazy">
          </span>
          <span class="sidebar-text">Monthly Fees</span>
        </router-link>
        <router-link v-if="role === 'admin'" to="/seat-map" class="sidebar-link">
          <span class="sidebar-icon">
            <!-- 🪑 -->
             <img src="../assets/svg/map-w.svg" class="sidebar-icon" alt="" loading="lazy">
          </span>
          <span class="sidebar-text">Seat Map</span>
        </router-link>
        <router-link v-if="role === 'admin'" to="/monthly-expenses" class="sidebar-link">
          <span class="sidebar-icon">
            <!-- 💸 -->
             <img src="../assets/svg/money-out-w.svg" class="sidebar-icon" alt="" loading="lazy">
          </span>
          <span class="sidebar-text">Expenses</span>
        </router-link>
      </nav>
    </aside>

    <!-- Top Navbar -->
    <nav class="navbar" :class="{ 'with-sidebar': isLoggedIn }">
      <div class="navbar-content">
        <!-- Mobile hamburger menu -->
        <button 
          v-if="isLoggedIn || !isLoggedIn" 
          class="hamburger mobile-only" 
          :class="{ 'menu-open': menuOpen }" 
          @click="toggleMenu"
        >
          <span class="hamburger-line"></span>
          <span class="hamburger-line"></span>
          <span class="hamburger-line"></span>
        </button>
        
        <!-- Desktop/Mobile logo when not logged in -->

        <div v-if="!isLoggedIn" class="desktop-only"></div>
        <router-link 
          v-if="!isLoggedIn" 
          to="/login" 
          class="navbar-logo"
        >
          <!-- <div class="logo-icon">📚</div> -->
          
          <div class="logo-text">Smart Library App</div>
          
        </router-link>
        <div v-if="!isLoggedIn" class="desktop-only"></div>

        <div v-if="!isLoggedIn" class="mobile-only" style="width: 42px;">

        </div>
        <div v-if="isLoggedIn" class="desktop-only"></div>

        <router-link 
          v-if="isLoggedIn" 
          :to="role === 'superadmin' ? '/superadmin' : '/dashboard'" 
          class="navbar-logo desktop-only"
          @click="closeMenu"
        >
          <!-- <div class="logo-icon">📚</div> -->
          <div class="logo-text">Smart Library App</div>
        </router-link>

        <!-- Mobile logo when logged in -->
        <router-link 
          v-if="isLoggedIn" 
          :to="role === 'superadmin' ? '/superadmin' : '/dashboard'" 
          class="navbar-logo mobile-only"
          @click="closeMenu"
        >
          <!-- <div class="logo-icon">📚</div> -->
          <div class="logo-text">Smart Library App</div>
        </router-link>
        
        <!-- User Dropdown (Desktop & Mobile) -->
        <div v-if="isLoggedIn" class="user-dropdown" @click.stop="toggleDropdown">
          <div class="user-avatar">
            <img src="../assets/profile/account.png" alt="User Avatar" loading="lazy" />
          </div>
          
          <!-- Dropdown Menu -->
          <div class="dropdown-menu" :class="{ 'show': dropdownOpen }" @click.stop>
            <div class="dropdown-header">
              <img src="../assets/profile/account.png" alt="User Avatar" loading="lazy" />
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

            <a href="#" class="dropdown-item" @click.prevent="PricingPlans">
              <svg class="dropdown-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M15 5.5 C13.4 4.3, 11 4.3, 9.4 5.5 C7.8 6.7, 7.8 9.1, 9.4 10.3 C11 11.5, 13.4 11.0, 15 12.8 C16.6 14.6, 16.6 17.0, 15 18.2 C13.4 19.4, 11 19.4, 9.0 18.4" />
                <path d="M12 3v18" />
              </svg>
              Pricing & Plans
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
              About
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
      <div class="mobile-menu" :class="{ 'show': menuOpen }" v-if="isLoggedIn">
        <router-link v-if="role === 'admin'" to="/dashboard" @click="closeMenu" class="mobile-link">
          <span class="mobile-icon">
            <!-- 📊 -->
            <img src="../assets/svg/chart-2.svg" class="mobile-icon" alt="" loading="lazy">
          </span>
          <span class="mobile-text">Dashboard</span>
        </router-link>
        <router-link v-if="role === 'admin'" to="/register" @click="closeMenu" class="mobile-link">
          <span class="mobile-icon">
            <!-- ➕ -->
             <img src="../assets/svg/add-plus-w.svg" class="mobile-icon" alt="" loading="lazy">
          </span>
          <span class="mobile-text">Register</span>
        </router-link>
        <router-link v-if="role === 'admin'" to="/students" @click="closeMenu" class="mobile-link">
          <span class="mobile-icon">
            <!-- 📋 -->
             <img src="../assets/svg/list-w.svg" class="mobile-icon" alt="" loading="lazy">
          </span>
          <span class="mobile-text">Student List</span>
        </router-link>
        <router-link v-if="role === 'admin'" to="/monthly-payments" @click="closeMenu" class="mobile-link">
          <span class="mobile-icon">
            <!-- 💰 -->
             <img src="../assets/svg/money-dollar.svg" class="mobile-icon" alt="" loading="lazy">
          </span>
          <span class="mobile-text">Monthly Fees</span>
        </router-link>
        <router-link v-if="role === 'admin'" to="/seat-map" @click="closeMenu" class="mobile-link">
          <span class="mobile-icon">
            <!-- 🪑 -->
             <img src="../assets/svg/map-w.svg" class="mobile-icon" alt="" loading="lazy">
          </span>
          <span class="mobile-text">Seat Map</span>
        </router-link>
        <router-link v-if="role === 'admin'" to="/monthly-expenses" @click="closeMenu" class="mobile-link">
          <span class="mobile-icon">
            <!-- 💸 -->
             <img src="../assets/svg/money-out-w.svg" class="mobile-icon" alt="" loading="lazy">
          </span>
          <span class="mobile-text">Expenses</span>
        </router-link>
      </div>
      <div class="mobile-menu" :class="{ 'show': menuOpen }" v-if="!isLoggedIn">
        <router-link to="/login" @click="closeMenu" class="mobile-link">
          <span class="mobile-icon">
            <!-- 👤 -->
             <img src="../assets/svg/login-w.svg" class="mobile-icon" alt="" loading="lazy">
          </span>
          <span class="mobile-text">Login</span>
        </router-link>
        <router-link to="/pricing-plans" @click="closeMenu" class="mobile-link">
          <span class="mobile-icon">
            <!-- 💰 -->
             <img src="../assets/svg/price-tag1.svg" class="mobile-icon" alt="" loading="lazy" >
          </span>
          <span class="mobile-text">Plans & Pricing</span>
        </router-link>
        <router-link to="/about" @click="closeMenu" class="mobile-link">
          <span class="mobile-icon">
            <!-- 🤔 -->
             <img src="../assets/svg/about.svg" class="mobile-icon" alt="" loading="lazy">
          </span>
          <span class="mobile-text">About</span>
        </router-link>
      </div>

    </nav>
  </div>
</template>

<script>
import API from '../api'

export default {
  data() {
    return {
      isLoggedIn: false,
      menuOpen: false,
      dropdownOpen: false,
      username: localStorage.getItem('username'),
      library_name: localStorage.getItem('library_name') || 'Smart Library',
      role: localStorage.getItem('role') || '',
    }
  },
  
  mounted() {
    this.checkLoginStatus()
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
      if (!this.$el.contains(event.target)) {
        this.dropdownOpen = false
        this.menuOpen = false
      }
    },
    
    viewProfile() {
      console.log('View Profile clicked')
      this.dropdownOpen = false
    },
    
    ChangePassword() {
      console.log('Change Password clicked')
      this.dropdownOpen = false
      this.$router.push('/change-password')
    },
    
    notifications() {
      console.log('Notifications clicked')
      this.dropdownOpen = false
    },
    
    helpCenter() {
      console.log('Help Center clicked')
      this.dropdownOpen = false
      this.$router.push('/about')
    },
    
    PricingPlans() {
      console.log('Pricing Plans clicked')
      this.dropdownOpen = false
      this.$router.push('/pricing-plans')
    },
    
    checkLoginStatus() {
      this.isLoggedIn = !!localStorage.getItem('role')
      this.library_name = localStorage.getItem('library_name') || 'Smart Library'
      this.role = localStorage.getItem('role') || ''
      this.username = localStorage.getItem('username')
    },
    
    async logout() {
      try {
        if (confirm('Are you sure you want to log out?')) {
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
          this.library_name = 'Smart Library'
          this.username = ''
          
          // Redirect to login
          this.$router.push('/login')
        }
      } catch (err) {
        console.error('Logout failed', err)
        alert('Logout failed. Try again.')
      }
    }
  },
  
  watch: {
    '$route': 'checkLoginStatus'
  }
}
</script>

<style scoped>
.layout-wrapper {
  position: relative;
}

/* ========== SIDEBAR STYLES ========== */
.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  color: white;
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 2px 0 10px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px 16px;
  /* border-bottom: 1px solid rgba(255,255,255,0.1); */
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  text-decoration: none;
  transition: all 0.3s ease;
}

.sidebar-logo:hover {
  opacity: 0.9;
}

.logo-icon {
  font-size: 1.8rem;
  width: 40px;
  height: 40px;
  background: rgba(255,255,255,0.15);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: -0.3px;
  line-height: 1.2;
  text-transform: uppercase;
}

.sidebar-nav {
  flex: 1;
  padding: 16px 0;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  margin: 4px 12px;
  color: rgba(255,255,255,0.85);
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.sidebar-link:hover {
  background: rgba(255,255,255,0.15);
  color: white;
  transform: translateX(2px);
}

.sidebar-link.router-link-exact-active {
  background: rgba(255,255,255,0.2);
  color: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.sidebar-icon {
  font-size: 1.2rem;
  width: 24px;
  text-align: center;
}

.sidebar-text {
  font-size: 0.95rem;
}

/* ========== NAVBAR STYLES ========== */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  color: white;
  z-index: 1100;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.navbar.with-sidebar {
  left: 260px;
}

.navbar-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.navbar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  color: white;
  text-decoration: none;
  font-weight: 700;
}

.navbar-logo .logo-icon {
  font-size: 1.6rem;
  width: 36px;
  height: 36px;
  background: rgba(255,255,255,0.15);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.navbar-logo .logo-text {
  font-size: 1.1rem;
  letter-spacing: -0.3px;
}

.hamburger {
  display: none;
  flex-direction: column;
  justify-content: center;
  width: 30px;
  height: 30px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  margin-right: 12px;
}

.hamburger-line {
  width: 24px;
  height: 3px;
  background: white;
  margin: 2px 0;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.hamburger.menu-open .hamburger-line:nth-child(1) {
  transform: rotate(45deg) translate(5px, 5px);
}

.hamburger.menu-open .hamburger-line:nth-child(2) {
  opacity: 0;
}

.hamburger.menu-open .hamburger-line:nth-child(3) {
  transform: rotate(-45deg) translate(5px, -5px);
}

/* ========== USER DROPDOWN ========== */
.user-dropdown {
  position: relative;
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.user-dropdown:hover {
  background: rgba(255,255,255,0.1);
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid rgba(255,255,255,0.3);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  min-width: 280px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px) scale(0.95);
  transition: all 0.3s ease;
  z-index: 1200;
  overflow: hidden;
}

.dropdown-menu.show {
  opacity: 1;
  visibility: visible;
  transform: translateY(0) scale(1);
}

.dropdown-header {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.dropdown-header img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 12px;
  border: 2px solid rgba(255,255,255,0.3);
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 700;
  font-size: 0.9rem;
  margin-bottom: 2px;
}

.user-email {
  font-size: 0.8rem;
  opacity: 0.9;
}

.dropdown-divider {
  height: 1px;
  background: #e5e7eb;
  margin: 8px 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: #374151;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.dropdown-item:hover {
  background: #f3f4f6;
}

.dropdown-item.logout-item {
  color: #ef4444;
  border-top: 1px solid #e5e7eb;
}

.dropdown-item.logout-item:hover {
  background: #fef2f2;
}

.dropdown-icon {
  width: 18px;
  height: 18px;
  opacity: 0.7;
}

/* ========== MOBILE MENU ========== */
.mobile-menu {
  position: fixed;
  top: 64px;
  left: 0;
  right: 0;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
  transform: translateX(-120%);
  transition: transform 0.3s ease;
  z-index: 1000;
  max-height: calc(100vh - 64px);
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.mobile-menu.show {
  transform: translateY(0);
}

.mobile-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  color: white;
  text-decoration: none;
  font-weight: 600;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  transition: all 0.3s ease;
}

.mobile-link:hover {
  background: rgba(255,255,255,0.15);
  padding-left: 24px;
}

.mobile-link.router-link-exact-active {
  background: rgba(255,255,255,0.2);
}

.mobile-icon {
  font-size: 1.2rem;
  width: 24px;
  text-align: center;
}

.mobile-text {
  font-size: 1rem;
}

/* ========== RESPONSIVE DESIGN ========== */
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
    display: flex !important;
  }
  
  .navbar {
    left: 0 !important;
    height: 64px;
    padding: 0 16px;
  }
  
  .navbar-content {
    padding: 0;
  }
  
  .hamburger {
    display: flex !important;
  }
  
  .navbar-logo .logo-text {
    font-size: 1rem;
  }
}

@media (max-width: 480px) {
  .navbar-logo .logo-text {
    display: block;
  }
  
  .dropdown-menu {
    min-width: 250px;
    right: -12px;
  }
  
  .mobile-link {
    padding: 14px 16px;
  }
  
  .user-avatar {
    width: 36px;
    height: 36px;
  }
}

/* Scroll behavior */
.sidebar::-webkit-scrollbar,
.mobile-menu::-webkit-scrollbar {
  width: 4px;
}

.sidebar::-webkit-scrollbar-track,
.mobile-menu::-webkit-scrollbar-track {
  background: rgba(255,255,255,0.1);
}

.sidebar::-webkit-scrollbar-thumb,
.mobile-menu::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.3);
  border-radius: 2px;
}

.sidebar::-webkit-scrollbar-thumb:hover,
.mobile-menu::-webkit-scrollbar-thumb:hover {
  background: rgba(255,255,255,0.5);
}
</style>
