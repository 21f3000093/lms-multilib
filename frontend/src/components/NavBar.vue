<template>
  <nav class="navbar">
    <div class="navbar-top">
      <router-link v-if="!isLoggedIn || role === 'admin'" to="/dashboard" style="text-decoration: none; background-color: unset;"><div class="logo">{{ this.library_name }}</div></router-link>
      <router-link  v-if="isLoggedIn && role === 'superadmin'" to="/superadmin" style="text-decoration: none; background-color: unset;"><div class="logo">{{ this.library_name }}</div></router-link>
      <!-- <div class="logo">📚 LMS Admin</div> -->
      <button class="hamburger" @click="toggleMenu">☰</button>
    </div>

    <div class="nav-links" :class="{ open: menuOpen }">
      <router-link v-if="isLoggedIn && role === 'admin'" to="/dashboard" @click="closeMenu">📊 Dashboard</router-link>
      <router-link v-if="isLoggedIn && role === 'admin'" to="/register" @click="closeMenu">➕ Register</router-link>
      <router-link v-if="isLoggedIn && role === 'admin'" to="/students" @click="closeMenu">📋 Student List</router-link>
      <router-link v-if="isLoggedIn && role === 'admin'" to="/monthly-payments" @click="closeMenu">💰 Monthly Fees</router-link>
      <router-link v-if="isLoggedIn && role === 'admin'" to="/seat-map" @click="closeMenu">🪑 Seat Map</router-link>
      <button v-if="isLoggedIn" class="logout-btn mobile-logout" @click="logout">🚪 Logout</button>
    </div>

    <!-- Desktop logout only -->
    <!-- <button v-if="isLoggedIn" class="logout-btn desktop-logout" @click="logout">🚪 Logout</button> -->

    <button v-if="isLoggedIn" @click="logout" class="custom-logout-btn desktop-logout">
      <div class="custom-logout-inner">
        <svg class="logout-icon" viewBox="0 0 512 512" fill="white">
          <path
            d="M377.9 105.9L500.7 228.7c7.2 7.2 11.3 17.1 11.3 27.3s-4.1 20.1-11.3 27.3L377.9 406.1c-6.4 6.4-15 9.9-24 9.9c-18.7 0-33.9-15.2-33.9-33.9l0-62.1-128 0c-17.7 0-32-14.3-32-32l0-64c0-17.7 14.3-32 32-32l128 0 0-62.1c0-18.7 15.2-33.9 33.9-33.9c9 0 17.6 3.6 24 9.9zM160 96L96 96c-17.7 0-32 14.3-32 32l0 256c0 17.7 14.3 32 32 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-64 0c-53 0-96-43-96-96L0 128C0 75 43 32 96 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32z"
          ></path>
        </svg>
        <span class="logout-text">Logout</span>
      </div>
    </button>


  </nav>
</template>

<script>
import API from '../api'

export default {
  data() {
    return {
      isLoggedIn: false,
      menuOpen: false,
      username: localStorage.getItem('username'),
      library_name: localStorage.getItem('library_name')?.toUpperCase() || 'Library Management System',
      role: localStorage.getItem('role') ?? '',      

    }
  },
  mounted() {
    this.checkLoginStatus()
  },
  methods: {
    closeMenu() {
      this.menuOpen = false
    },
    toggleMenu() {
      this.menuOpen = !this.menuOpen
    },
    checkLoginStatus() {
      // ✅ use role instead of unused is_admin_logged_in
      this.isLoggedIn = !!localStorage.getItem('role')
      this.library_name = localStorage.getItem('library_name')?.toUpperCase() || 'Library Management System'
      this.role = localStorage.getItem('role')?? ''
    },
    async logout() {
      try {
        if (confirm('Are you sure you want to log out?')) {
          await API.post('/auth/logout')
        }

        // ✅ Clear relevant localStorage keys only
        localStorage.removeItem('role')
        localStorage.removeItem('username')
        localStorage.removeItem('library_id')
        localStorage.removeItem('library_name')


        this.isLoggedIn = false
        this.menuOpen = false
        this.library_name = 'Library Management System'
        this.$router.push('/login')
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
.navbar {
  display: flex;
  background-color: #8082e3;
  padding: 12px 24px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Top bar */
.navbar-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  color: white;
  font-size: 1.2rem;
  font-weight: bold;
}

/* Hamburger Icon */
.hamburger {
  background: none;
  color: white;
  font-size: 1.5rem;
  border: none;
  cursor: pointer;
  display: none;
}

/* Nav links */
.nav-links {
  
  display: flex;
  gap: 16px;
  margin-top: 12px;
  align-items: center;
  margin-left: auto;
}

.nav-links a {
  color: #f5f6fa;
  text-decoration: none;
  font-weight: bold;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-links a:hover {
  background-color: #40739e;
}

/* Logout buttons */
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

.router-link-exact-active {
  background-color: #44bd32;
  color: white;
}

/* Desktop view */
.desktop-logout {
  margin-left: auto;
  display: block;
  align-self: center;
}

.mobile-logout {
  display: none;
}

.custom-logout-btn {
  display: flex;
  align-items: center;
  justify-content: start;
  width: 44px;
  height: 44px;
  background-color: #e84118;
  border-radius: 50%;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  position: relative;
  border: none;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.custom-logout-btn:hover {
  width: 130px;
  border-radius: 8px;
}

.custom-logout-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  transition: all 0.3s ease;
  padding-left: 0;
}

.custom-logout-btn:hover .custom-logout-inner {
  justify-content: flex-start;
  padding-left: 14px;
}

.logout-icon {
  width: 18px;
  height: 18px;
  transition: transform 0.3s;
}

.logout-text {
  position: absolute;
  right: 18px;
  transform: translateX(100%);
  opacity: 0;
  color: white;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s ease;
}

.custom-logout-btn:hover .logout-text {
  transform: translateX(0);
  opacity: 1;
}


/* Mobile responsive */
@media (max-width: 1080px) {
  .navbar {
    flex-direction: column;
    align-items: stretch;
  }

  .hamburger {
    display: block;
  }

  .nav-links {
    flex-direction: column;
    align-items: center;
    gap: 12px;
    display: none;
    width: 100%;
    margin-top: 12px;
  }

  .nav-links.open {
    display: flex;
  }

  .nav-links a {
    width: 80%;
    text-align: center;
  }

  .mobile-logout {
    display: block;
    width: 80%;
    text-align: center;
    margin-top: 10px;
  }

  .desktop-logout {
    display: none;
  }
}

</style>