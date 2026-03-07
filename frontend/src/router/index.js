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
import ChangePassword from '@/components/ChangePassword.vue'
import MonthlyExpenses from '@/components/MonthlyExpenses.vue'
import PricingPlans from '@/components/PricingPlans.vue'
import AboutView from '@/views/AboutView.vue'
import ReceiptPage from '@/components/ReceiptPage.vue'
import NotificationCenter from '@/components/NotificationCenter.vue'
import SuperadminNotifications from '@/components/SuperadminNotifications.vue'





const routes = [
  { path: '/login', name: 'AdminLogin', component: AdminLogin, meta: { guestOnly: true } },
  { path: '/', redirect: '/dashboard',meta: { requiresAuth: true } },

  { path: '/about', name: 'AboutView', component: AboutView },
  
  { path: '/dashboard', name: 'AdminDashboard', component: AdminDashboard , meta: { requiresAuth: true } },

  { path: '/register', name: 'Register', component: StudentForm , meta: { requiresAuth: true }},
  { path: '/students', name: 'StudentList', component: StudentList , meta: { requiresAuth: true }},
  { path: '/monthly-payments',name: 'MonthlyPayments', component: MonthlyPayments , meta: { requiresAuth: true } },
  { path: '/monthly-expenses',name: 'MonthlyExpenses', component: MonthlyExpenses , meta: { requiresAuth: true } },
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
  {
    path: '/notifications',
    name: 'NotificationCenter',
    component: NotificationCenter,
    meta: { requiresAuth: true }
  },
  {
    path: '/superadmin/notifications',
    name: 'SuperadminNotifications',
    component: SuperadminNotifications,
    meta: { requiresAuth: true }
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: ChangePassword,
    meta: { requiresAuth: true } // If you have auth guards
  },
  {
    path: '/pricing-plans',
    name: 'PricingPlans',
    component: PricingPlans,
    meta: { requiresAuth: false } // If you have auth guards
  },
  {
    path: '/public-receipts/:token',
    name: 'PublicReceiptPage',
    component: ReceiptPage,
    meta: { requiresAuth: false }
  },
  {
    path: '/receipts/:paymentId',
    name: 'ReceiptPage',
    component: ReceiptPage,
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0, left: 0 }
  }
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

const getHomeRouteByRole = (role) => (role === 'superadmin' ? '/superadmin' : '/dashboard');

router.beforeEach((to, from, next) => {
  const role = localStorage.getItem('role'); // set this after login (e.g. 'admin' or 'superadmin')

  if (to.meta.guestOnly && role) {
    return next(getHomeRouteByRole(role));
  }

  if (to.meta.requiresAuth && !role) {
    return next('/login'); // not logged in
  }

  // Superadmin should not stay on admin-only authenticated pages.
  if (
    role === 'superadmin' &&
    to.meta.requiresAuth &&
    !to.path.startsWith('/superadmin') &&
    to.path !== '/change-password'
  ) {
    return next('/superadmin');
  }

  if (to.path.startsWith('/superadmin') && role !== 'superadmin') {
    return next('/dashboard'); // block access if not superadmin
  }

  next();
});


export default router
