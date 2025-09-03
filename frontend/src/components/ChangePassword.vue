<template>
  <div class="change-password-page">
    <div class="change-password-container">
      <!-- Header Section -->
      <div class="header-section">
        <h2 class="page-title">Change Password</h2>
        <p class="page-subtitle">Update your account security</p>
      </div>

      <!-- Password Change Form -->
      <div class="form-container">
        <form @submit.prevent="changePassword" class="password-form">
          <div class="form-group">
            <label for="currentPassword" class="form-label">Current Password</label>
            <div class="input-wrapper">
              <input
                :type="showCurrentPassword ? 'text' : 'password'"
                id="currentPassword"
                v-model="form.current_password"
                class="form-input"
                :class="{ 'error': errors.current_password }"
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
            <div v-if="errors.current_password" class="error-message">
              {{ errors.current_password }}
            </div>
          </div>

          <div class="form-group">
            <label for="newPassword" class="form-label">New Password</label>
            <div class="input-wrapper">
              <input
                :type="showNewPassword ? 'text' : 'password'"
                id="newPassword"
                v-model="form.new_password"
                class="form-input"
                :class="{ 'error': errors.new_password }"
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
            <div v-if="errors.new_password" class="error-message">
              {{ errors.new_password }}
            </div>
          </div>

          <div class="form-group">
            <label for="confirmPassword" class="form-label">Confirm New Password</label>
            <div class="input-wrapper">
              <input
                :type="showConfirmPassword ? 'text' : 'password'"
                id="confirmPassword"
                v-model="form.confirm_password"
                class="form-input"
                :class="{ 'error': errors.confirm_password }"
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
            <div v-if="errors.confirm_password" class="error-message">
              {{ errors.confirm_password }}
            </div>
          </div>

          <div class="form-actions">
            <button
              type="button"
              class="btn-cancel"
              @click="resetForm"
              :disabled="loading"
            >
              Cancel
            </button>

            <button
              type="submit"
              class="btn-submit"
              :disabled="loading"
            >
              {{ loading ? 'Changing Password...' : 'Change Password' }}
            </button>
          </div>
        </form>

        <!-- Success Message -->
        <div v-if="successMessage" class="success-alert">
          <div class="alert-content">
            <div class="alert-title">Success</div>
            <div class="alert-message">{{ successMessage }}</div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="error-alert">
          <div class="alert-content">
            <div class="alert-title">Error</div>
            <div class="alert-message">{{ errorMessage }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
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
  confirm_password: ''
})

const errors = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const loading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

// Password visibility toggles
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const showSuccess = (message) => {
  toast.success(message, {
    position: 'top',
    timeout: 3000,
    style: {
      backgroundColor: '#10b981',
      color: '#fff',
      borderRadius: '8px'
    }
  })
}

const showError = (message) => {
  toast.error(message, {
    style: {
      backgroundColor: '#ef4444',
      color: '#fff',
      borderRadius: '8px'
    }
  })
}

const validateForm = () => {
  // Reset errors
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })

  let isValid = true

  // Validate current password
  if (!form.current_password) {
    errors.current_password = 'Current password is required'
    isValid = false
  }

  // Validate new password
  if (!form.new_password) {
    errors.new_password = 'New password is required'
    isValid = false
  } else if (form.new_password.length < 6) {
    errors.new_password = 'Password must be at least 6 characters long'
    isValid = false
  }

  // Validate confirm password
  if (!form.confirm_password) {
    errors.confirm_password = 'Please confirm your new password'
    isValid = false
  } else if (form.new_password !== form.confirm_password) {
    errors.confirm_password = 'Passwords do not match'
    isValid = false
  }

  // Check if new password is different from current
  if (form.current_password && form.new_password && form.current_password === form.new_password) {
    errors.new_password = 'New password must be different from current password'
    isValid = false
  }

  return isValid
}

const changePassword = async () => {
  // Clear previous messages
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
    
    // Auto-hide success message after 3 seconds
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
  
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })
  
  errorMessage.value = ''
  successMessage.value = ''
  
  // Reset password visibility
  showCurrentPassword.value = false
  showNewPassword.value = false
  showConfirmPassword.value = false
}
</script>

<style scoped>
.change-password-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  display: flex;
  align-items: center;
  justify-content: center;
}

.change-password-container {
  width: 100%;
  max-width: 450px;
}

.header-section {
  text-align: center;
  color: white;
  margin-bottom: 32px;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  letter-spacing: -0.025em;
}

.page-subtitle {
  font-size: 0.95rem;
  opacity: 0.9;
  margin: 0;
  font-weight: 400;
}

.form-container {
  background: white;
  border-radius: 12px;
  padding: 32px 28px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
  font-size: 0.875rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.form-input {
  width: 100%;
  padding: 12px 14px;
  padding-right: 70px;
  font-size: 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.2s ease;
  box-sizing: border-box;
  background: white;
}

.form-input:focus {
  border-color: #667eea;
}

.form-input.error {
  border-color: #ef4444;
}

.password-toggle {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #667eea;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.password-toggle:hover {
  background: #f3f4f6;
}

.error-message {
  color: #ef4444;
  font-size: 0.8rem;
  margin-top: 4px;
  font-weight: 500;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.btn-cancel,
.btn-submit {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn-cancel:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-submit {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-cancel:disabled,
.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.success-alert,
.error-alert {
  padding: 14px 16px;
  border-radius: 8px;
  margin-top: 16px;
}

.success-alert {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
}

.error-alert {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.alert-content {
  text-align: center;
}

.alert-title {
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 2px;
}

.alert-message {
  font-size: 0.85rem;
  opacity: 0.9;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .change-password-page {
    padding: 16px;
  }
  
  .change-password-container {
    max-width: 100%;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .form-container {
    padding: 24px 20px;
  }
  
  .form-input {
    padding: 11px 12px;
    padding-right: 65px;
  }
  
  .form-actions {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .change-password-page {
    padding: 12px;
  }
  
  .page-title {
    font-size: 1.3rem;
  }
  
  .form-container {
    padding: 20px 16px;
  }
}
</style>
