<!-- frontend/src/views/AdminLogin.vue -->

<template>
  <div class="login-container">
    <h2>Admin Login</h2>
    <form @submit.prevent="login">
      <input v-model="username" placeholder="Username" required @blur="onUsernameBlur" />

      <div class="password-wrapper">
        <input
          :type="showPassword ? 'text' : 'password'"
          v-model="password"
          placeholder="Password"
          required
          @blur="onPasswordBlur"
        />
        <button type="button" class="toggle-btn" @click="togglePassword">
          {{ showPassword ? '🙈 Hide' : '👁 Show' }}
        </button>
      </div>

      <button type="submit" :disabled="loading">
        {{ loading ? 'Please wait...' : 'Login' }}
      </button>

      <p v-if="error">{{ error }}</p>
    </form>
  </div>
</template>


<script>
import API from '../api';
export default {
  data() {
    return {
      username: '',
      password: '',
      error: '',
      showPassword: false,
      loading: false,
    };
  },
  methods: {
    togglePassword() {
      this.showPassword = !this.showPassword;
    },
    async login() {

      this.error = '';
      this.onUsernameBlur();
      this.onPasswordBlur();
      
      if (!this.username || !this.password) {
        this.error = 'Please enter username and password';
        return;
      }

      this.loading = true;
      try {
        const res = await API.post('/auth/login', {
          username: this.username,
          password: this.password
        });
        // localStorage.setItem('token', res.data.token);
        localStorage.setItem('role', res.data.role); // response from backend
        localStorage.setItem('username', res.data.username);
        localStorage.setItem('library_id', res.data.library_id ?? ''); 
        localStorage.setItem('library_name', res.data.library?.name || '');        

        if (res.data.role === 'superadmin') {
          this.$router.push('/superadmin');
        } else {
          this.$router.push('/dashboard');
        }

      } catch (err) {
        if (err.response) {
          this.error = err.response.data.detail || 'Login failed';
        } else {
          this.error = 'Network error. Please try again.';
        }
      } finally {
        this.loading = false;
      }
    },

    onUsernameBlur() {
      this.username = this.username.trim().replace(/\s+/g, ' ');
    },
    onPasswordBlur() {
      this.password = this.password.trim();
    },
    
    
  }
};
</script>

<style scoped>

.login-container {
  max-width: 400px;
  margin: 20vh auto;
  padding: 2rem;
  background-color: #f9f9f900;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  font-family: "Segoe UI", sans-serif;
  text-align: center;
}

h2 {
  margin-bottom: 1.5rem;
  color: #333;
}

form {
  display: flex;
  flex-direction: column;
}

input {
  padding: 12px;
  margin: 10px 0;
  border-radius: 8px;
  border: 1px solid #ccc;
  font-size: 1rem;
  width: 95%;
}

.password-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.toggle-btn {
  background: none;
  border: none;
  color: #007bff;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0;
}

button[type="submit"] {
  padding: 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 1rem;
}

p {
  color: red;
  margin-top: 10px;
  font-size: 0.95rem;
}

@media (max-width: 480px) {
  .login-container {
    margin: 8vh 1rem;
    padding: 1.5rem;
    max-width: 95%;
    margin-top: 30vh;

  }

  h2 {
    font-size: 1.5rem;
  }

  .toggle-btn {
    font-size: 0.8rem;
  }
}
</style>
