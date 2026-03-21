//frontend/src/api.js

import axios from 'axios';
import { useToast } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';

// Create a toast instance
const toast = useToast();

// Helper functions for different toast types
const showErrorToast = (message, timeout = 5000) => {
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
      backgroundColor: 'var(--theme-panel-solid)',
      color: 'var(--theme-text-strong)',
      border: '1px solid var(--theme-danger-border)',
      borderRadius: '8px',
      margin: '10px',
      boxShadow: 'var(--theme-shadow-soft)',
    }
  });
};

const showWarningToast = (message, timeout = 3000) => {
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
      backgroundColor: 'var(--theme-panel-solid)',
      color: 'var(--theme-text-strong)',
      border: '1px solid var(--theme-warning-border)',
      borderRadius: '8px',
      margin: '10px',
      boxShadow: 'var(--theme-shadow-soft)',
    }
  });
};

const API = axios.create({
  // baseURL: 'https://lms-multilib-production-1470.up.railway.app',
  baseURL: "https://api.smartlibraryapp.in",
  // baseURL: 'http://localhost:8000',
  withCredentials: true,  // 🔒 Send secure HttpOnly cookie with every request
});




API.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data?.detail;
      const detailCode = typeof detail === 'object' ? detail?.code : undefined;
      const detailMessage =
        typeof detail === 'object'
          ? (detail?.message || '')
          : (typeof detail === 'string' ? detail : '');

      if (status === 402) {
        if (detailCode === 'subscription_expired') {
          showWarningToast(detailMessage || 'Your subscription is inactive or expired. Please renew to continue.', 5000);
          if (window.location.pathname !== '/billing') {
            setTimeout(() => {
              window.location.href = '/billing';
            }, 1200);
          }
        } else {
          showWarningToast(detailMessage || 'Subscription is required to continue.', 5000);
        }
      }

      if (status === 403) {
        showErrorToast('Your account is inactive.Please contact the Admin for more details.', 5000);
      } 
      else if (status === 401) {
        if (detail === 'invalid_credentials') {
          showErrorToast('Invalid username, email, or password.');
        } else if (detail === 'token_expired_or_invalid') {
          showWarningToast('Your session has expired. Please log in again.');
        } else {
          showErrorToast('Unauthorized access.');
        }
      }

      // if ([401, 403, 422].includes(status)) {
      //   localStorage.removeItem('admin');
      //   localStorage.removeItem('is_admin_logged_in');
      //   localStorage.removeItem('role');
      //   localStorage.removeItem('username');
      //   localStorage.removeItem('library_id');
      //   localStorage.removeItem('library_name');
      //   // window.location.href = '/login';
      //   setTimeout(() => {
      //     window.location.href = '/login';
      //   }, 2000);
      // }

      // Only force logout on explicit token error or 403
      if (status === 403 || (status === 401 && detail === 'token_expired_or_invalid')) {
        localStorage.removeItem('role');
        localStorage.removeItem('username');
        localStorage.removeItem('library_id');
        localStorage.removeItem('library_name');

        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      }

    }

    return Promise.reject(error);
  }
);



export default API;
