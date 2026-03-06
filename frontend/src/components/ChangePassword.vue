<template>
  <main class="change-password-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="form-shell glass-card">
      <header class="form-header">
        <p class="kicker">Security Settings</p>
        <h1>
          Change
          <span class="gradient-text">Password</span>
        </h1>
        <p class="subtitle">Update your account credentials and keep access secure.</p>
      </header>

      <form @submit.prevent="changePassword" class="password-form" novalidate>
        <div class="form-group">
          <label for="currentPassword" class="field-label">Current Password</label>
          <div class="input-wrap" :class="{ error: errors.current_password }">
            <input
              :type="showCurrentPassword ? 'text' : 'password'"
              id="currentPassword"
              v-model="form.current_password"
              class="field-input"
              placeholder="Enter your current password"
              required
            />
            <button
              type="button"
              class="password-toggle"
              @click="showCurrentPassword = !showCurrentPassword"
            >
              {{ showCurrentPassword ? 'Hide' : 'Show' }}
            </button>
          </div>
          <p v-if="errors.current_password" class="error-message">{{ errors.current_password }}</p>
        </div>

        <div class="form-group">
          <label for="newPassword" class="field-label">New Password</label>
          <div class="input-wrap" :class="{ error: errors.new_password }">
            <input
              :type="showNewPassword ? 'text' : 'password'"
              id="newPassword"
              v-model="form.new_password"
              class="field-input"
              placeholder="Enter your new password"
              required
            />
            <button
              type="button"
              class="password-toggle"
              @click="showNewPassword = !showNewPassword"
            >
              {{ showNewPassword ? 'Hide' : 'Show' }}
            </button>
          </div>
          <p v-if="errors.new_password" class="error-message">{{ errors.new_password }}</p>
        </div>

        <div class="form-group">
          <label for="confirmPassword" class="field-label">Confirm New Password</label>
          <div class="input-wrap" :class="{ error: errors.confirm_password }">
            <input
              :type="showConfirmPassword ? 'text' : 'password'"
              id="confirmPassword"
              v-model="form.confirm_password"
              class="field-input"
              placeholder="Confirm your new password"
              required
            />
            <button
              type="button"
              class="password-toggle"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              {{ showConfirmPassword ? 'Hide' : 'Show' }}
            </button>
          </div>
          <p v-if="errors.confirm_password" class="error-message">{{ errors.confirm_password }}</p>
        </div>

        <div class="form-actions">
          <button
            type="button"
            class="btn btn-ghost"
            @click="resetForm"
            :disabled="loading"
          >
            Cancel
          </button>

          <button
            type="submit"
            class="btn btn-solid"
            :disabled="loading"
          >
            {{ loading ? 'Changing Password...' : 'Change Password' }}
          </button>
        </div>
      </form>

      <div v-if="successMessage" class="alert success-alert">
        <p class="alert-title">Success</p>
        <p class="alert-message">{{ successMessage }}</p>
      </div>

      <div v-if="errorMessage" class="alert error-alert">
        <p class="alert-title">Error</p>
        <p class="alert-message">{{ errorMessage }}</p>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, reactive } from 'vue'
import API from '../api'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'

const toast = useToast()

const form = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
})

const errors = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
})

const loading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const showSuccess = (message) => {
  toast.success(message, {
    position: 'top',
    timeout: 3000,
    style: {
      backgroundColor: '#0ea5e9',
      color: '#fff',
      borderRadius: '10px',
    },
  })
}

const showError = (message) => {
  toast.error(message, {
    style: {
      backgroundColor: '#ef4444',
      color: '#fff',
      borderRadius: '10px',
    },
  })
}

const validateForm = () => {
  Object.keys(errors).forEach((key) => {
    errors[key] = ''
  })

  let isValid = true

  if (!form.current_password) {
    errors.current_password = 'Current password is required'
    isValid = false
  }

  if (!form.new_password) {
    errors.new_password = 'New password is required'
    isValid = false
  } else if (form.new_password.length < 6) {
    errors.new_password = 'Password must be at least 6 characters long'
    isValid = false
  }

  if (!form.confirm_password) {
    errors.confirm_password = 'Please confirm your new password'
    isValid = false
  } else if (form.new_password !== form.confirm_password) {
    errors.confirm_password = 'Passwords do not match'
    isValid = false
  }

  if (form.current_password && form.new_password && form.current_password === form.new_password) {
    errors.new_password = 'New password must be different from current password'
    isValid = false
  }

  return isValid
}

const changePassword = async () => {
  successMessage.value = ''
  errorMessage.value = ''

  if (!validateForm()) {
    return
  }

  loading.value = true

  try {
    await API.put('/auth/change-password', form)

    successMessage.value = 'Password has been changed successfully'
    showSuccess('Password changed successfully')

    resetForm()

    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    console.error('Change password error:', error)

    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
      showError(error.response.data.detail)
    } else {
      errorMessage.value = 'Failed to change password. Please try again.'
      showError('Failed to change password. Please try again.')
    }
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.current_password = ''
  form.new_password = ''
  form.confirm_password = ''

  Object.keys(errors).forEach((key) => {
    errors[key] = ''
  })

  errorMessage.value = ''
  successMessage.value = ''

  showCurrentPassword.value = false
  showNewPassword.value = false
  showConfirmPassword.value = false
}
</script>

<style scoped>
.change-password-page {
  --surface: rgba(148, 163, 184, 0.03);
  --surface-border: rgba(255, 255, 255, 0.03);
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;

  position: relative;
  min-height: 100vh;
  color: var(--text-primary);
  padding: 0rem 1rem 2.4rem;
  overflow: hidden;
  isolation: isolate;
  display: grid;
  place-items: center;
}

.mesh-layer {
  position: absolute;
  inset: 0;
  z-index: -1;
  background:
    radial-gradient(45rem 24rem at 10% 15%, rgba(34, 211, 238, 0.14), transparent 70%),
    radial-gradient(40rem 24rem at 86% 8%, rgba(59, 130, 246, 0.14), transparent 68%),
    radial-gradient(36rem 22rem at 65% 88%, rgba(14, 165, 233, 0.11), transparent 70%),
    linear-gradient(180deg, #0f172a 0%, #0b1222 100%);
  filter: saturate(115%);
  animation: mesh-drift 18s ease-in-out infinite alternate;
}

.glass-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.form-shell {
  width: min(520px, 100%);
  border-radius: 18px;
  padding: 1rem;
}

.kicker {
  margin: 0;
  display: inline-flex;
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #cbd5e1;
  background: rgba(148, 163, 184, 0.07);
}

.form-header h1 {
  margin: 0.82rem 0 0;
  font-size: clamp(1.5rem, 3.8vw, 2.3rem);
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.gradient-text {
  background: linear-gradient(90deg, #22d3ee, #3b82f6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.subtitle {
  margin: 0.7rem 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.password-form {
  margin-top: 0.95rem;
  display: grid;
  gap: 0.6rem;
}

.form-group {
  display: grid;
  gap: 0.32rem;
}

.field-label {
  color: #cbd5e1;
  font-size: 0.8rem;
  font-weight: 600;
}

.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.72);
}

.input-wrap:focus-within {
  border-color: rgba(34, 211, 238, 0.62);
  box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.16);
}

.input-wrap.error {
  border-color: rgba(239, 68, 68, 0.6);
}

.field-input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: #f8fafc;
  font-size: 0.95rem;
  padding: 0.72rem 3.2rem 0.72rem 0.75rem;
  min-height: 44px;
  box-sizing: border-box;
}

.password-toggle {
  position: absolute;
  right: 0.46rem;
  background: rgba(148, 163, 184, 0.12);
  border: 1px solid rgba(148, 163, 184, 0.28);
  color: #cbd5e1;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.45rem;
  cursor: pointer;
}

.error-message {
  margin: 0;
  color: #fca5a5;
  font-size: 0.78rem;
}

.form-actions {
  margin-top: 0.35rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.55rem;
}

.btn {
  min-height: 44px;
  border-radius: 12px;
  border: 1px solid transparent;
  padding: 0.56rem 0.8rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  font-weight: 700;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-solid {
  background: linear-gradient(90deg, #0ea5e9, #3b82f6);
  color: #fff;
  box-shadow: 0 14px 28px rgba(59, 130, 246, 0.28);
}

.btn-ghost {
  background: rgba(148, 163, 184, 0.08);
  border-color: rgba(148, 163, 184, 0.32);
  color: #e2e8f0;
}

.alert {
  margin-top: 0.55rem;
  border-radius: 12px;
  padding: 0.65rem;
  text-align: center;
}

.success-alert {
  border: 1px solid rgba(16, 185, 129, 0.35);
  background: rgba(16, 185, 129, 0.14);
  color: #a7f3d0;
}

.error-alert {
  border: 1px solid rgba(239, 68, 68, 0.35);
  background: rgba(239, 68, 68, 0.14);
  color: #fecaca;
}

.alert-title,
.alert-message {
  margin: 0;
}

.alert-title {
  font-weight: 700;
  font-size: 0.85rem;
}

.alert-message {
  margin-top: 0.12rem;
  font-size: 0.8rem;
}

@keyframes mesh-drift {
  0% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  100% {
    transform: translate3d(-1.5%, 1.2%, 0) scale(1.04);
  }
}

@media (max-width: 767px) {
  .change-password-page {
    padding: 0rem 2rem;
  }

  .form-shell {
    padding: 0.8rem;
  }

  .form-actions {
    grid-template-columns: 1fr;
  }

  .field-input {
    font-size: 16px;
  }
}
</style>
