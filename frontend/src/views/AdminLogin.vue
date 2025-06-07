<template>
  <div class="login-container">
    <h2>Admin Login</h2>
    <form @submit.prevent="login">
      <input v-model="username" placeholder="Username" required />

      <div class="password-wrapper">
        <input
          :type="showPassword ? 'text' : 'password'"
          v-model="password"
          placeholder="Password"
          required
        />
        <button type="button" class="toggle-btn" @click="togglePassword">
          {{ showPassword ? '🙈 Hide' : '👁 Show' }}
        </button>
      </div>

      <button type="submit">Login</button>
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
      showPassword: false
    };
  },
  methods: {
    togglePassword() {
      this.showPassword = !this.showPassword;
    },
    async login() {
      try {
        const res = await API.post('/auth/login', {
          username: this.username,
          password: this.password
        });
        localStorage.setItem('admin', JSON.stringify(res.data));
        localStorage.setItem('is_admin_logged_in', 'true');
        this.$router.push('/dashboard');
      } catch (err) {
        this.error = 'Invalid credentials';
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 20vh auto;
  padding: 2rem;
  background-color: #f9f9f9;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
  width: 100%;
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
</style>
