<template>
  <nav class="navbar">
    <div class="navbar-top">
      <router-link v-if="!isLoggedIn || role === 'admin'" to="/dashboard" style="text-decoration: none; background-color: unset;"><div class="logo">📚 {{ this.library_name }}</div></router-link>
      <router-link  v-if="isLoggedIn && role === 'superadmin'" to="/superadmin" style="text-decoration: none; background-color: unset;"><div class="logo">📚 {{ this.library_name }}</div></router-link>
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
    <button v-if="isLoggedIn" class="logout-btn desktop-logout" @click="logout">🚪 Logout</button>
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
  background-color: #273c75;
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