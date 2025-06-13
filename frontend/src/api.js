//frontend/src/api.js

import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,  // 🔒 Send secure HttpOnly cookie with every request
});

export default API;
