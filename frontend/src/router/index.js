// frontend/src/router/index.js


import { createRouter, createWebHistory } from 'vue-router'
// import HomeView from '../views/HomeView.vue'
import AdminDashboard from '@/components/AdminDashboard.vue'
import StudentForm from '@/components/StudentForm.vue'
import StudentList from '@/components/StudentList.vue'
import MonthlyPayments from '@/components/MonthlyPayments.vue'
import StudentDetail from '@/components/StudentDetail.vue'
import AdminLogin from '@/views/AdminLogin.vue'
import SeatMap from '@/components/SeatMap.vue'
import SuperAdminDashboard from '@/views/SuperAdminDashboard.vue'
import LibraryStudentList from '@/components/LibraryStudentList.vue'
import WhatsAppReminders from '@/components/WhatsAppReminders.vue';





const routes = [
  { path: '/login', name: 'AdminLogin', component: AdminLogin },
  { path: '/', redirect: '/dashboard',meta: { requiresAuth: true } },
  
  { path: '/dashboard', name: 'AdminDashboard', component: AdminDashboard , meta: { requiresAuth: true } },

  { path: '/register', name: 'Register', component: StudentForm , meta: { requiresAuth: true }},
  { path: '/students', name: 'StudentList', component: StudentList , meta: { requiresAuth: true }},
  { path: '/monthly-payments',name: 'MonthlyPayments', component: MonthlyPayments , meta: { requiresAuth: true } },
  { path: '/students/:id', name: 'StudentDetail', component: StudentDetail , meta: { requiresAuth: true } },
  { path: '/seat-map', name: 'SeatMap', component: SeatMap , meta: { requiresAuth: true }},
  { path: '/superadmin', name: 'SuperAdminDashboard', component: SuperAdminDashboard, meta: { requiresAuth: true } },
  {
    path: '/superadmin/library/:library_id/students',
    name: 'LibraryStudentList',
    component: LibraryStudentList,
    meta: { requiresAuth: true }
  },
  {
    path: '/reminders',
    name: 'WhatsAppReminders',
    component: WhatsAppReminders,
    meta: { requiresAuth: true }
  },

]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// // Route guard
// router.beforeEach((to, from, next) => {
//   const isLoggedIn = !!localStorage.getItem('admin');
//   if (to.meta.requiresAuth && !isLoggedIn) {
//     next('/login');
//   } else {
//     next();
//   }
// });

router.beforeEach((to, from, next) => {
  const role = localStorage.getItem('role'); // set this after login (e.g. 'admin' or 'superadmin')

  if (to.path === '/superadmin' && role !== 'superadmin') {
    return next('/dashboard'); // block access if not superadmin
  }

  if (to.meta.requiresAuth && !role) {
    return next('/login'); // not logged in
  }

  next();
});


export default router
