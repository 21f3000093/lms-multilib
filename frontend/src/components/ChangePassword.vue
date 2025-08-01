<template>
  <div class="change-password-container">
    <div class="card">
      <div class="card-header">
        <h3>Change Password</h3>
      </div>
      <div class="card-body">
        <form @submit.prevent="changePassword">
          <div class="form-group">
            <label for="currentPassword">Current Password</label>
            <input
              type="password"
              id="currentPassword"
              v-model="form.current_password"
              class="form-control"
              required
              :class="{ 'is-invalid': errors.current_password }"
            />
            <div v-if="errors.current_password" class="invalid-feedback">
              {{ errors.current_password }}
            </div>
          </div>

          <div class="form-group">
            <label for="newPassword">New Password</label>
            <input
              type="password"
              id="newPassword"
              v-model="form.new_password"
              class="form-control"
              required
              :class="{ 'is-invalid': errors.new_password }"
            />
            <div v-if="errors.new_password" class="invalid-feedback">
              {{ errors.new_password }}
            </div>
          </div>

          <div class="form-group">
            <label for="confirmPassword">Confirm New Password</label>
            <input
              type="password"
              id="confirmPassword"
              v-model="form.confirm_password"
              class="form-control"
              required
              :class="{ 'is-invalid': errors.confirm_password }"
            />
            <div v-if="errors.confirm_password" class="invalid-feedback">
              {{ errors.confirm_password }}
            </div>
          </div>

          <div class="form-actions">
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="loading"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ loading ? 'Changing...' : 'Change Password' }}
            </button>
            <button
              type="button"
              class="btn btn-secondary"
              @click="resetForm"
            >
              Cancel
            </button>
          </div>
        </form>

        <!-- Success/Error Messages -->
        <div v-if="successMessage" class="alert alert-success mt-3">
          {{ successMessage }}
        </div>
        <div v-if="errorMessage" class="alert alert-danger mt-3">
          {{ errorMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable */
import { ref, reactive } from 'vue'
import API from '../api';


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
    errors.new_password = 'New password must be at least 6 characters long'
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
  if (form.current_password === form.new_password) {
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
    const response = await API.put('/auth/change-password', form)

    successMessage.value = 'Password changed successfully!'
    resetForm()
    
    // Optional: Auto-hide success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)

  } catch (error) {
    console.error('Change password error:', error)
    
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else {
      errorMessage.value = 'An error occurred while changing password'
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
}
</script>

<style scoped>
.change-password-container {
  max-width: 40vw;
  margin: 30vh auto;
  padding: 0 1rem;
  /* background-color: #ffffff; */
}

.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.159);
  background-color: #ffffffb1;
}

.card-header {
  background-color: #f8f9fa00;
  padding: 1rem;
  border-bottom: 1px solid #ddd;
  border-radius: 8px 8px 0 0;
}

.card-header h3 {
  margin: 0;
  color: #333;
}

.card-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.345);
}

.form-control.is-invalid {
  border-color: #dc3545;
}

.invalid-feedback {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-primary:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #545b62;
}

.alert {
  padding: 0.75rem;
  border-radius: 4px;
  margin-top: 1rem;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

@media (max-width: 768px) {
  .change-password-container {
    max-width: 80vw;
  }
}


</style>
