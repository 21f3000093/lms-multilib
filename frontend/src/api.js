import axios from 'axios';

const API = axios.create({
  baseURL: 'https://librarymanagementsystem-production-6a76.up.railway.app',
  withCredentials: true,  // 🔒 Send secure HttpOnly cookie with every request
});

export default API;
