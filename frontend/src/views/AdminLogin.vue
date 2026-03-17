<template>
  <main class="login-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="login-shell">
      <article class="intro-card">
        <p class="kicker">Smart Library App</p>
        <h1>
          Unified operations for
          <span class="gradient-text">modern libraries</span>
        </h1>
        <p>
          Manage students, seat allocation, payments, reminders, and analytics from a single secure workspace.
        </p>

        <!-- <div class="intro-points">
          <div class="point">
            <ShieldCheck class="point-icon" aria-hidden="true" />
            Role-based access
          </div>
          <div class="point">
            <Sparkles class="point-icon" aria-hidden="true" />
            WhatsApp automation
          </div>
          <div class="point">
            <BarChart3 class="point-icon" aria-hidden="true" />
            Real-time visibility
          </div>
        </div> -->
      </article>

      <article class="form-card">
        <header class="form-head">
          <h2>Admin Login</h2>
          <p>Sign in to continue to your dashboard.</p>
        </header>

        <form class="login-form" @submit.prevent="login">
          <div class="social-block">
            <GoogleAuthButton
              text="continue_with"
              hint="Use the same Google email that is linked to your Smart Library account."
              @credential="handleGoogleCredential"
              @error="handleGoogleError"
            />
          </div>

          <div class="divider" aria-hidden="true">
            <span></span>
            <p>or continue with password</p>
            <span></span>
          </div>

          <label class="input-label" for="identifier">Username or Email</label>
          <div class="input-wrap" :class="{ error: error && !identifier }">
            <User class="input-icon" aria-hidden="true" />
            <input
              id="identifier"
              v-model="identifier"
              type="text"
              placeholder="Enter username or email"
              required
              autocomplete="username"
              @blur="onIdentifierBlur"
            />
          </div>

          <label class="input-label" for="password">Password</label>
          <div class="input-wrap" :class="{ error: error && !password }">
            <Lock class="input-icon" aria-hidden="true" />
            <input
              id="password"
              :type="showPassword ? 'text' : 'password'"
              v-model="password"
              placeholder="Enter password"
              required
              autocomplete="current-password"
              @blur="onPasswordBlur"
            />
            <button type="button" class="toggle-btn" @click="togglePassword" :aria-label="showPassword ? 'Hide password' : 'Show password'">
              <EyeOff v-if="showPassword" class="toggle-icon" aria-hidden="true" />
              <Eye v-else class="toggle-icon" aria-hidden="true" />
            </button>
          </div>

          <div class="helper-row">
            <router-link to="/forgot-password" class="helper-link">Forgot password?</router-link>
          </div>

          <TurnstileWidget
            v-if="requiresCaptcha && turnstileConfig.enabled"
            :site-key="turnstileConfig.site_key"
            :reset-key="captchaResetKey"
            @verified="onCaptchaVerified"
            @expired="onCaptchaExpired"
          />

          <button type="submit" class="login-btn" :disabled="loading">
            <LoaderCircle v-if="loading" class="spinner" aria-hidden="true" />
            <span>{{ loading ? 'Signing in...' : 'Sign in' }}</span>
            <ArrowRight v-if="!loading" class="btn-arrow" aria-hidden="true" />
          </button>

          <p v-if="error" class="error-banner">
            <AlertCircle class="error-icon" aria-hidden="true" />
            <span>{{ error }}</span>
          </p>
        </form>

        <div class="form-footer-links">
          <router-link to="/signup">Start Free Trial</router-link>
          <span>•</span>
          <router-link to="/pricing-plans">Pricing</router-link>
          <span>•</span>
          <router-link to="/about">About</router-link>
        </div>
      </article>
    </section>

    <footer class="page-footer">
      <p>© 2026 Smart Library App. All rights reserved.</p>
    </footer>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import {
  AlertCircle,
  ArrowRight,
  // BarChart3,
  Eye,
  EyeOff,
  LoaderCircle,
  Lock,
  // ShieldCheck,
  // Sparkles, 
  User,
} from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'
import API from '../api'
import { setupPushForCurrentAdmin } from '../utils/pushNotifications'
import { homeRouteForRole, storeAdminSession } from '../utils/authSession'
import GoogleAuthButton from '../components/GoogleAuthButton.vue'
import TurnstileWidget from '../components/TurnstileWidget.vue'

const router = useRouter()
const toast = useToast()

const identifier = ref('')
const password = ref('')
const error = ref('')
const showPassword = ref(false)
const loading = ref(false)
const requiresCaptcha = ref(false)
const captchaToken = ref('')
const captchaResetKey = ref(0)
const turnstileConfig = ref({ enabled: false, site_key: null })

const showSuccess = (message) => {
  toast.success(message, {
    position: 'top',
    timeout: 2000,
    style: {
      backgroundColor: '#0ea5e9',
      color: '#fff',
      borderRadius: '12px',
    },
  })
}

const showError = (message) => {
  toast.error(message, {
    style: {
      backgroundColor: '#dc2626',
      color: '#fff',
      borderRadius: '12px',
    },
  })
}

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const onIdentifierBlur = () => {
  identifier.value = identifier.value.trim().replace(/\s+/g, ' ')
}

const onPasswordBlur = () => {
  password.value = password.value.trim()
}

const loadTurnstileConfig = async () => {
  try {
    const res = await API.get('/auth/turnstile/config')
    turnstileConfig.value = res.data
  } catch (err) {
    turnstileConfig.value = { enabled: false, site_key: null }
  }
}

const applyAuthError = (err, fallbackMessage) => {
  const detail = err.response?.data?.detail
  if (detail && typeof detail === 'object') {
    error.value = detail.message || fallbackMessage
    if (detail.code === 'captcha_required' || detail.code === 'temporarily_locked') {
      requiresCaptcha.value = true
      captchaResetKey.value += 1
    }
    showError(error.value)
    return
  }

  error.value = typeof detail === 'string' ? detail : fallbackMessage
}

const onCaptchaVerified = (token) => {
  captchaToken.value = token
}

const onCaptchaExpired = () => {
  captchaToken.value = ''
}

const handleAuthSuccess = async (admin, message) => {
  storeAdminSession(admin)
  showSuccess(message)

  if (admin.role === 'admin') {
    await setupPushForCurrentAdmin()
  }

  router.push(homeRouteForRole(admin.role))
}

const persistGoogleOnboarding = (payload) => {
  sessionStorage.setItem('google_signup_onboarding', JSON.stringify(payload))
}

const handleGoogleCredential = async (credential) => {
  error.value = ''
  loading.value = true
  try {
    const res = await API.post('/auth/google/exchange', {
      credential,
      intent: 'login',
      captcha_token: requiresCaptcha.value ? captchaToken.value : null,
    })

    if (res.data?.action === 'logged_in' && res.data?.admin) {
      requiresCaptcha.value = false
      captchaToken.value = ''
      captchaResetKey.value += 1
      await handleAuthSuccess(res.data.admin, 'Signed in with Google')
      return
    }

    if (['signup_required', 'complete_signup'].includes(res.data?.action)) {
      persistGoogleOnboarding(res.data)
      router.push('/signup?google=1')
      return
    }

    error.value = res.data?.message || 'Google sign-in could not be completed.'
    showError(error.value)
  } catch (err) {
    applyAuthError(err, 'Google sign-in could not be completed.')
    showError(error.value || 'Google sign-in could not be completed.')
  } finally {
    loading.value = false
  }
}

const handleGoogleError = () => {
  error.value = 'Google sign-in is temporarily unavailable. Please use password login.'
  showError(error.value)
}

const login = async () => {
  error.value = ''
  onIdentifierBlur()
  onPasswordBlur()

  if (!identifier.value || !password.value) {
    error.value = 'Please enter your username or email and password'
    showError('Please fill in all fields')
    return
  }

  if ('serviceWorker' in navigator) {
    const registrations = await navigator.serviceWorker.getRegistrations()
    for (const registration of registrations) {
      await registration.unregister()
    }

    const cacheNames = await caches.keys()
    await Promise.all(cacheNames.map((name) => caches.delete(name)))
  }

  loading.value = true
  try {
    const res = await API.post('/auth/login', {
      identifier: identifier.value,
      password: password.value,
      captcha_token: requiresCaptcha.value ? captchaToken.value : null,
    })

    requiresCaptcha.value = false
    captchaToken.value = ''
    captchaResetKey.value += 1
    await handleAuthSuccess(res.data, 'Login successful')
  } catch (err) {
    if (err.response) {
      applyAuthError(err, 'Invalid username, email, or password')
    } else {
      error.value = 'Network error. Please check your connection.'
      showError(error.value)
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTurnstileConfig()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.login-page {
  --bg: #0f172a;
  --surface: rgba(148, 163, 184, 0.03);
  --surface-border: rgba(255, 255, 255, 0.03);
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --brand-a: #22d3ee;
  --brand-b: #3b82f6;

  min-height: 100vh;
  position: relative;
  overflow: hidden;
  isolation: isolate;
  font-family: Inter, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  color: var(--text-primary);
  background: var(--bg);
  padding: 2rem 1rem 2rem;
}

.mesh-layer {
  position: absolute;
  inset: 0;
  z-index: -1;
  background:
    radial-gradient(45rem 24rem at 10% 15%, rgba(34, 211, 238, 0.14), transparent 70%),
    radial-gradient(40rem 24rem at 86% 8%, rgba(59, 130, 246, 0.14), transparent 68%),
    radial-gradient(36rem 22rem at 65% 88%, rgba(14, 165, 233, 0.11), transparent 70%),
    linear-gradient(180deg, #0f172a 0%, #0b1222 100%);
  filter: saturate(115%);
  animation: mesh-drift 18s ease-in-out infinite alternate;
}

.login-shell {
  width: min(1080px, 100%);
  margin: 0 auto;
  display: grid;
  /* grid-template-columns: 1fr 1fr; */
  gap: 1.1rem;
}

.intro-card,
.form-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 20px;
  padding: 1.4rem;
}

.kicker {
  margin: 0;
  display: inline-flex;
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #cbd5e1;
  background: rgba(148, 163, 184, 0.07);
}

.intro-card h1 {
  margin: 0.9rem 0 0;
  font-size: clamp(1.9rem, 4.4vw, 3rem);
  line-height: 1.05;
  letter-spacing: -0.03em;
  text-wrap: balance;
}

.gradient-text {
  background: linear-gradient(90deg, var(--brand-a), var(--brand-b));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.intro-card p {
  margin: 1rem 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.intro-points {
  margin-top: 1.2rem;
  display: grid;
  gap: 0.55rem;
}

.point {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: #dbeafe;
  font-weight: 600;
  font-size: 0.9rem;
}

.point-icon {
  width: 1rem;
  height: 1rem;
  color: #67e8f9;
}

.form-head h2 {
  margin: 0;
  font-size: 1.6rem;
}

.form-head p {
  margin: 0.45rem 0 0;
  color: var(--text-secondary);
}

.login-form {
  margin-top: 1rem;
  display: grid;
  gap: 0.7rem;
}

.helper-row {
  display: flex;
  justify-content: flex-end;
}

.social-block {
  margin-top: 0.15rem;
}

.divider {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 0.8rem;
  color: #64748b;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.divider span {
  height: 1px;
  background: rgba(148, 163, 184, 0.2);
}

.divider p {
  margin: 0;
}

.helper-link {
  color: #7dd3fc;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 600;
}

.helper-link:hover {
  color: #bae6fd;
}

.input-label {
  color: #cbd5e1;
  font-weight: 600;
  font-size: 0.88rem;
}

.input-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-radius: 12px;
  padding: 0 0.65rem;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.75);
}

.input-wrap.error {
  border-color: rgba(248, 113, 113, 0.78);
}

.input-wrap:focus-within {
  border-color: rgba(34, 211, 238, 0.7);
  box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.15);
}

.input-icon {
  width: 0.98rem;
  height: 0.98rem;
  color: #94a3b8;
  flex: 0 0 auto;
}

.input-wrap input {
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  color: #f8fafc;
  font-size: 0.98rem;
  min-height: 46px;
}

.input-wrap input::placeholder {
  color: #64748b;
}

.input-wrap input:-webkit-autofill,
.input-wrap input:-webkit-autofill:hover,
.input-wrap input:-webkit-autofill:focus,
.input-wrap input:-webkit-autofill:active {
  -webkit-text-fill-color: #f8fafc;
  caret-color: #f8fafc;
  -webkit-box-shadow: 0 0 0 1000px rgba(15, 23, 42, 0.75) inset;
  box-shadow: 0 0 0 1000px rgba(15, 23, 42, 0.75) inset;
  transition: background-color 9999s ease-out 0s;
}

.input-wrap input:-moz-autofill {
  color: #f8fafc;
  caret-color: #f8fafc;
  box-shadow: 0 0 0 1000px rgba(15, 23, 42, 0.75) inset;
}

.toggle-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  background: rgba(148, 163, 184, 0.08);
  color: #e2e8f0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.toggle-icon {
  width: 0.95rem;
  height: 0.95rem;
}

.login-btn {
  margin-top: 0.55rem;
  min-height: 46px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(90deg, #0ea5e9, #3b82f6);
  color: #fff;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  cursor: pointer;
  transition: transform 180ms ease, box-shadow 180ms ease, opacity 180ms ease;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 14px 28px rgba(59, 130, 246, 0.28);
}

.login-btn:disabled {
  opacity: 0.75;
  cursor: not-allowed;
}

.spinner {
  width: 1rem;
  height: 1rem;
  animation: spin 1s linear infinite;
}

.btn-arrow {
  width: 0.95rem;
  height: 0.95rem;
}

.error-banner {
  margin: 0.3rem 0 0;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: #fecaca;
  font-size: 0.88rem;
  font-weight: 600;
  padding: 0.55rem 0.65rem;
  border-radius: 10px;
  border: 1px solid rgba(248, 113, 113, 0.45);
  background: rgba(239, 68, 68, 0.12);
}

.error-icon {
  width: 0.95rem;
  height: 0.95rem;
  flex: 0 0 auto;
}

.form-footer-links {
  margin-top: 0.95rem;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: #64748b;
}

.form-footer-links a {
  color: #cbd5e1;
  text-decoration: none;
  font-size: 0.88rem;
  font-weight: 600;
}

.form-footer-links a:hover {
  color: #67e8f9;
}

.page-footer {
  width: min(1080px, 100%);
  margin: 1.2rem auto 0;
  text-align: center;
  color: #64748b;
  font-size: 0.84rem;
}

@keyframes mesh-drift {
  0% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  100% {
    transform: translate3d(-1.5%, 1.2%, 0) scale(1.04);
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 960px) {
  .login-shell {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 767px) {
  .login-page {
    padding-top: 2rem;
    padding-bottom: 1.5rem;
  }

  .intro-card,
  .form-card {
    padding: 1.1rem;
  }

  .intro-card h1 {
    font-size: clamp(1.7rem, 8vw, 2.3rem);
  }
}
</style>
