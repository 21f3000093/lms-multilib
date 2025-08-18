//frontend/src/api.js

import axios from 'axios';
import { useToast } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';

// Create a toast instance
const toast = useToast();

// Helper functions for different toast types
const showErrorToast = (message, timeout = 4000) => {
  toast.error(message, {
    position: 'top',
    timeout,
    closeOnClick: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    showCloseButtonOnHover: false,
    hideProgressBar: false,
    closeButton: "button",
    icon: true,
    rtl: false,
    style: {
      backgroundColor: '#dc3545',
      color: '#fff',
      borderRadius: '8px'
    }
  });
};

const showWarningToast = (message, timeout = 4000) => {
  toast.warning(message, {
    position: 'top',
    timeout,
    closeOnClick: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    showCloseButtonOnHover: false,
    hideProgressBar: false,
    closeButton: "button",
    icon: true,
    rtl: false,
    style: {
      backgroundColor: '#ffc107',
      color: '#212529',
      borderRadius: '8px'
    }
  });
};

const API = axios.create({
  baseURL: 'https://lms-multilib-production.up.railway.app',
  // baseURL: 'http://localhost:8000',
  withCredentials: true,  // 🔒 Send secure HttpOnly cookie with every request
});




API.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data?.detail;

      if (status === 403) {
        showErrorToast('❌ Your account is inactive.Please contact the Admin for more details.', 5000);
      } 
      else if (status === 401) {
        if (detail === 'invalid_credentials') {
          showErrorToast('❌ Invalid username or password.');
        } else if (detail === 'token_expired_or_invalid') {
          showWarningToast('🔐 Your session has expired. Please log in again.');
        } else {
          showErrorToast('🔒 Unauthorized access.');
        }
      }

      if ([401, 403, 422].includes(status)) {
        localStorage.removeItem('admin');
        localStorage.removeItem('is_admin_logged_in');
        localStorage.removeItem('role');
        localStorage.removeItem('username');
        localStorage.removeItem('library_id');
        localStorage.removeItem('library_name');
        // window.location.href = '/login';
        setTimeout(() => {
          window.location.href = '/login';
        }, 1500);
      }
    }

    return Promise.reject(error);
  }
);



export default API;
