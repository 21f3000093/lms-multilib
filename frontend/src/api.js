//frontend/src/api.js

import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,  // 🔒 Send secure HttpOnly cookie with every request
});


// API.interceptors.response.use(
//   response => response,
//   error => {
//     if (error.response && (error.response.status === 401 || error.response.status === 422)) {
//       localStorage.removeItem('admin');
//       localStorage.removeItem('is_admin_logged_in');
//       localStorage.removeItem('role');
//       window.location.href = '/login';
//     }
//     return Promise.reject(error);
//   }
// );
API.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data?.detail;

      if (status === 403) {
        alert('❌ Your account is blocked. Please contact the Owner for more details.');
      } 
      else if (status === 401) {
        if (detail === 'invalid_credentials') {
          alert('❌ Invalid username or password.');
        } else if (detail === 'token_expired_or_invalid') {
          alert('🔐 Your session has expired. Please log in again.');
        } else {
          alert('🔒 Unauthorized access.');
        }
      }

      if ([401, 403, 422].includes(status)) {
        localStorage.removeItem('admin');
        localStorage.removeItem('is_admin_logged_in');
        localStorage.removeItem('role');
        localStorage.removeItem('username');
        localStorage.removeItem('library_id');
        localStorage.removeItem('library_name');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);



export default API;
