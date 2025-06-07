import { createRouter, createWebHistory } from 'vue-router'
// import HomeView from '../views/HomeView.vue'
import AdminDashboard from '@/components/AdminDashboard.vue'
import StudentForm from '@/components/StudentForm.vue'
import StudentList from '@/components/StudentList.vue'
import MonthlyPayments from '@/components/MonthlyPayments.vue'
import StudentDetail from '@/components/StudentDetail.vue'
import AdminLogin from '@/views/AdminLogin.vue'
import SeatMap from '@/components/SeatMap.vue'



const routes = [
  { path: '/login', name: 'AdminLogin', component: AdminLogin },
  { path: '/', redirect: '/dashboard',meta: { requiresAuth: true } },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  { path: '/dashboard', name: 'AdminDashboard', component: AdminDashboard , meta: { requiresAuth: true } },

  { path: '/register', name: 'Register', component: StudentForm , meta: { requiresAuth: true }},
  { path: '/students', name: 'StudentList', component: StudentList , meta: { requiresAuth: true }},
  { path: '/monthly-payments',name: 'MonthlyPayments', component: MonthlyPayments , meta: { requiresAuth: true } },
  { path: '/students/:id', name: 'StudentDetail', component: StudentDetail , meta: { requiresAuth: true } },
  { path: '/seat-map', name: 'SeatMap', component: SeatMap , meta: { requiresAuth: true }},

]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Route guard
router.beforeEach((to, from, next) => {
  const isLoggedIn = !!localStorage.getItem('admin');
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login');
  } else {
    next();
  }
});

export default router
