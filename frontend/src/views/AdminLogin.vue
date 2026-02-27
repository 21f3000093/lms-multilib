<template>
  <div class="login-page">
    <div class="login-container">
      <!-- App Header -->
      <div class="app-header">
        <h1 class="app-title">Smart Library App</h1>
      </div>

      <!-- Login Form -->
      <div class="login-form-wrapper">
        <div class="login-header">
          <h2 class="login-title">Admin Login</h2>
        </div>

        <form @submit.prevent="login" class="login-form">
          <div class="form-group">
            <input 
              v-model="username" 
              type="text"
              placeholder="Username" 
              required 
              @blur="onUsernameBlur"
              class="form-input"
              :class="{ error: error && !username }"
            />
          </div>

          <div class="form-group">
            <div class="password-wrapper">
              <input
                :type="showPassword ? 'text' : 'password'"
                v-model="password"
                placeholder="Password"
                required
                @blur="onPasswordBlur"
                class="form-input password-input"
                :class="{ error: error && !password }"
              />
              <button 
                type="button" 
                class="toggle-password-btn" 
                @click="togglePassword"
                tabindex="-1"
              >
                {{ showPassword ? 'Hide' : 'Show' }}
              </button>
            </div>
          </div>

          <button 
            type="submit" 
            :disabled="loading" 
            class="login-btn"
            :class="{ loading: loading }"
          >
            <span v-if="loading" class="loading-spinner">⏳</span>
            <span class="btn-text">{{ loading ? 'Logging in...' : 'Login' }}</span>
          </button>

          <div v-if="error" class="error-message">
            <span class="error-icon">⚠️</span>
            <span class="error-text">{{ error }}</span>
          </div>
        </form>
      </div>
    </div>
    <!-- Footer -->
    <div class="footer-section">
      <div class="footer-content">
        <div class="footer-logo">
          <!-- <div class="logo-icon">📚</div> -->
          <span class="logo-text">Smart Library App</span>
        </div>
        <p class="footer-text">
          © 2026 Smart Library App. All rights reserved.
        </p>
        <p class="footer-text">Empowering library networks across the India.</p>
      </div>
    </div>
  </div>
</template>

<script>
import API from '../api';
import { useToast } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';

export default {
  setup() {
    const toast = useToast();
    
    const showSuccess = (message) => {
      toast.success(message, {
        position: 'top',
        timeout: 2000,
        style: {
          backgroundColor: '#667eea',
          color: '#fff',
          borderRadius: '12px'
        }
      });
    };
    
    const showError = (message) => {
      toast.error(message, {
        style: {
          backgroundColor: '#dc2626',
          color: '#fff',
          borderRadius: '12px'
        }
      });
    };
    
    return { showSuccess, showError };
  },

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
        this.error = 'Please enter both username and password';
        this.showError('Please fill in all fields');
        return;
      }

      // ✅ FORCE UNREGISTER OLD SERVICE WORKERS AND CLEAR CACHES

      if ('serviceWorker' in navigator) {
        const registrations = await navigator.serviceWorker.getRegistrations();
        for (let registration of registrations) {
          await registration.unregister();
        }
        
        // Clear all caches
        const cacheNames = await caches.keys();
        await Promise.all(cacheNames.map(name => caches.delete(name)));
      }

      this.loading = true;
      try {
        const res = await API.post('/auth/login', {
          username: this.username,
          password: this.password
        });

        // Store user data
        localStorage.setItem('role', res.data.role);
        localStorage.setItem('username', res.data.username);
        localStorage.setItem('library_id', res.data.library_id ?? ''); 
        localStorage.setItem('library_name', res.data.library?.name || '');

        this.showSuccess('✅ Login successful!');

        // Redirect based on role
        if (res.data.role === 'superadmin') {
          this.$router.push('/superadmin');
        } else {
          this.$router.push('/dashboard');
        }

      } catch (err) {
        if (err.response) {
          this.error = err.response.data.detail || 'Invalid username or password';
          // this.showError(this.error);
        } else {
          this.error = 'Network error. Please check your connection.';
          // this.showError('Connection failed. Please try again.');
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
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  /* justify-content: center; */
  padding: 20px;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  display: flex;
  flex-direction: column;  
  padding-top: 12rem;
}

.login-container {
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.app-header {
  text-align: center;
  margin-bottom: 20px;
}

.app-title {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
  letter-spacing: -0.5px;
}

.login-form-wrapper {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 32px 28px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
}

.login-header {
  text-align: center;
  margin-bottom: 28px;
}

.login-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-input {
  width: 100%;
  padding: 14px 16px;
  font-size: 16px; /* Prevent zoom on iOS */
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  outline: none;
  transition: all 0.3s ease;
  box-sizing: border-box;
  background: white;
}

.form-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input.error {
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}

.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input {
  padding-right: 70px;
}

.toggle-password-btn {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.toggle-password-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #4f46e5;
}

.login-btn {
  width: 100%;
  padding: 14px 20px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 8px;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.login-btn.loading {
  background: linear-gradient(45deg, #9ca3af, #6b7280);
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.btn-text {
  font-weight: 600;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
  border-radius: 8px;
  font-size: 0.9rem;
  border: 1px solid rgba(220, 38, 38, 0.2);
}

.error-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.error-text {
  flex: 1;
  font-weight: 500;
}

/* Footer */
.footer-section {
  padding: 40px 20px;
  background: rgba(0, 0, 0, 0.2);
  color: white;
  width: 100%;
  position: absolute;
  bottom: 0%;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.footer-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
}

.logo-icon {
  font-size: 1.5rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
}

.footer-text {
  font-size: 0.9rem;
  opacity: 0.8;
  margin: 0;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .login-page {
    padding: 16px;
    padding-top: 12rem;
    
  }
  
  .app-title {
    font-size: 1.8rem;
  }
  
  .login-form-wrapper {
    padding: 24px 20px;
  }
  
  .login-title {
    font-size: 1.5rem;
  }
  
  .form-input {
    padding: 12px 14px;
  }
  
  .password-input {
    padding-right: 65px;
  }
  
  .toggle-password-btn {
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .login-container {
    max-width: 100%;
  }

  
  .app-title {
    font-size: 1.6rem;
  }
  
  .login-form-wrapper {
    padding: 20px 16px;
  }
  
  .login-title {
    font-size: 1.3rem;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .login-form-wrapper {
    background: rgba(31, 41, 55, 0.95);
  }
  
  .login-title {
    color: white;
  }
  
  .form-input {
    background: rgba(55, 65, 81, 0.5);
    border-color: rgba(75, 85, 99, 0.5);
    color: white;
  }
  
  .form-input::placeholder {
    color: rgba(156, 163, 175, 0.8);
  }
}
</style>
