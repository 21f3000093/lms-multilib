<template>
  <main class="signup-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="signup-shell">
      <article class="intro-card">
        <p class="kicker">Smart Library App</p>
        <h1>
          Launch your library workspace with an
          <span class="gradient-text">instant free trial</span>
        </h1>
        <p>
          Create your library, set your seat capacity, and start managing students, payments, reminders,
          and billing in one place.
        </p>

        <div class="intro-points">
          <div class="point-chip">
            <ShieldCheck class="point-icon" aria-hidden="true" />
            Secure owner access
          </div>
          <div class="point-chip">
            <Sparkles class="point-icon" aria-hidden="true" />
            Trial starts immediately
          </div>
          <div class="point-chip">
            <CircleDollarSign class="point-icon" aria-hidden="true" />
            Billing ready from day one
          </div>
        </div>
      </article>

      <article class="form-card">
        <header class="form-head">
          <h2>Create your library account</h2>
          <p>Set up your workspace and owner login in one step.</p>
        </header>

        <form class="signup-form" @submit.prevent="signup">
          <section class="form-section">
            <div class="section-label">
              <Building2 class="section-icon" aria-hidden="true" />
              <span>Library Details</span>
            </div>

            <div class="field-grid two-col">
              <div>
                <label class="input-label" for="library-name">Library Name</label>
                <div class="input-wrap" :class="{ error: error && !form.library_name }">
                  <Building2 class="input-icon" aria-hidden="true" />
                  <input id="library-name" v-model="form.library_name" type="text" placeholder="Enter library name" required @blur="normalizeLibraryName" />
                </div>
              </div>

              <div>
                <label class="input-label" for="max-seats">Max Seats</label>
                <div class="input-wrap" :class="{ error: error && !form.max_seats }">
                  <Armchair class="input-icon" aria-hidden="true" />
                  <input id="max-seats" v-model.number="form.max_seats" type="number" min="1" max="200" placeholder="e.g. 50" required />
                </div>
              </div>
            </div>

            <div class="field-grid two-col">
              <div>
                <label class="input-label" for="contact-phone">Contact Phone</label>
                <div class="input-wrap" :class="{ error: error && !form.contact_phone }">
                  <Phone class="input-icon" aria-hidden="true" />
                  <input id="contact-phone" v-model="form.contact_phone" type="text" inputmode="tel" placeholder="Enter phone number" required @blur="normalizePhone" />
                </div>
              </div>

              <div>
                <label class="input-label" for="address">Address <span class="label-hint">Optional</span></label>
                <div class="input-wrap">
                  <MapPin class="input-icon" aria-hidden="true" />
                  <input id="address" v-model="form.address" type="text" placeholder="Library address" @blur="normalizeAddress" />
                </div>
              </div>
            </div>
          </section>

          <section class="form-section">
            <div class="section-label">
              <UserRoundCog class="section-icon" aria-hidden="true" />
              <span>Owner Admin Details</span>
            </div>

            <div class="field-grid two-col">
              <div>
                <label class="input-label" for="admin-username">Username</label>
                <div class="input-wrap" :class="{ error: error && !form.admin_username }">
                  <User class="input-icon" aria-hidden="true" />
                  <input id="admin-username" v-model="form.admin_username" type="text" autocomplete="username" placeholder="Choose a username" required @blur="normalizeUsername" />
                </div>
              </div>

              <div>
                <label class="input-label" for="admin-email">Email</label>
                <div class="input-wrap" :class="{ error: error && !form.admin_email }">
                  <Mail class="input-icon" aria-hidden="true" />
                  <input id="admin-email" v-model="form.admin_email" type="email" autocomplete="email" placeholder="you@example.com" required @blur="normalizeEmail" />
                </div>
              </div>
            </div>

            <div class="field-grid two-col">
              <div>
                <label class="input-label" for="password">Password</label>
                <div class="input-wrap" :class="{ error: error && !form.password }">
                  <Lock class="input-icon" aria-hidden="true" />
                  <input
                    id="password"
                    :type="showPassword ? 'text' : 'password'"
                    v-model="form.password"
                    autocomplete="new-password"
                    placeholder="Create a password"
                    required
                    @blur="normalizePassword"
                  />
                  <button type="button" class="toggle-btn" @click="showPassword = !showPassword" :aria-label="showPassword ? 'Hide password' : 'Show password'">
                    <EyeOff v-if="showPassword" class="toggle-icon" aria-hidden="true" />
                    <Eye v-else class="toggle-icon" aria-hidden="true" />
                  </button>
                </div>
              </div>

              <div>
                <label class="input-label" for="confirm-password">Confirm Password</label>
                <div class="input-wrap" :class="{ error: error && !form.confirm_password }">
                  <Lock class="input-icon" aria-hidden="true" />
                  <input
                    id="confirm-password"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    v-model="form.confirm_password"
                    autocomplete="new-password"
                    placeholder="Confirm your password"
                    required
                    @blur="normalizeConfirmPassword"
                  />
                  <button type="button" class="toggle-btn" @click="showConfirmPassword = !showConfirmPassword" :aria-label="showConfirmPassword ? 'Hide password' : 'Show password'">
                    <EyeOff v-if="showConfirmPassword" class="toggle-icon" aria-hidden="true" />
                    <Eye v-else class="toggle-icon" aria-hidden="true" />
                  </button>
                </div>
              </div>
            </div>
          </section>

          <button type="submit" class="signup-btn" :disabled="loading">
            <LoaderCircle v-if="loading" class="spinner" aria-hidden="true" />
            <span>{{ loading ? 'Creating workspace...' : 'Start Free Trial' }}</span>
            <ArrowRight v-if="!loading" class="btn-arrow" aria-hidden="true" />
          </button>

          <p v-if="error" class="error-banner">
            <AlertCircle class="error-icon" aria-hidden="true" />
            <span>{{ error }}</span>
          </p>
        </form>

        <div class="form-footer-links">
          <router-link to="/login">Already have an account?</router-link>
          <span>•</span>
          <router-link to="/pricing-plans">Pricing</router-link>
          <span>•</span>
          <router-link to="/about">About</router-link>
        </div>
      </article>
    </section>
  </main>
</template>

<script setup>
import { reactive, ref } from 'vue'
import {
  AlertCircle,
  Armchair,
  ArrowRight,
  Building2,
  CircleDollarSign,
  Eye,
  EyeOff,
  LoaderCircle,
  Lock,
  Mail,
  MapPin,
  Phone,
  ShieldCheck,
  Sparkles,
  User,
  UserRoundCog,
} from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'
import API from '../api'
import { setupPushForCurrentAdmin } from '../utils/pushNotifications'

const router = useRouter()
const toast = useToast()

const form = reactive({
  library_name: '',
  max_seats: 25,
  contact_phone: '',
  address: '',
  admin_username: '',
  admin_email: '',
  password: '',
  confirm_password: '',
})

const error = ref('')
const loading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const showSuccess = (message) => {
  toast.success(message, {
    position: 'top',
    timeout: 2200,
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

const normalizeLibraryName = () => {
  form.library_name = form.library_name.trim().replace(/\s+/g, ' ')
}

const normalizePhone = () => {
  form.contact_phone = form.contact_phone.trim().replace(/\s+/g, ' ')
}

const normalizeAddress = () => {
  form.address = form.address.trim().replace(/\s+/g, ' ')
}

const normalizeUsername = () => {
  form.admin_username = form.admin_username.trim().replace(/\s+/g, ' ')
}

const normalizeEmail = () => {
  form.admin_email = form.admin_email.trim().toLowerCase()
}

const normalizePassword = () => {
  form.password = form.password.trim()
}

const normalizeConfirmPassword = () => {
  form.confirm_password = form.confirm_password.trim()
}

const normalizeAll = () => {
  normalizeLibraryName()
  normalizePhone()
  normalizeAddress()
  normalizeUsername()
  normalizeEmail()
  normalizePassword()
  normalizeConfirmPassword()
}

const signup = async () => {
  error.value = ''
  normalizeAll()

  if (!form.library_name || !form.contact_phone || !form.admin_username || !form.admin_email || !form.password || !form.confirm_password) {
    error.value = 'Please complete all required fields'
    showError('Please fill in all required fields')
    return
  }

  if (!Number.isInteger(Number(form.max_seats)) || Number(form.max_seats) < 1 || Number(form.max_seats) > 200) {
    error.value = 'Max seats must be between 1 and 200'
    showError('Please enter a valid seat count')
    return
  }

  if (form.password !== form.confirm_password) {
    error.value = 'Passwords do not match'
    showError('Passwords do not match')
    return
  }

  loading.value = true
  try {
    const res = await API.post('/auth/signup', {
      library_name: form.library_name,
      max_seats: Number(form.max_seats),
      contact_phone: form.contact_phone,
      address: form.address || null,
      admin_username: form.admin_username,
      admin_email: form.admin_email,
      password: form.password,
      confirm_password: form.confirm_password,
    })

    localStorage.setItem('role', res.data.role)
    localStorage.setItem('username', res.data.username)
    localStorage.setItem('library_id', res.data.library_id ?? '')
    localStorage.setItem('library_name', res.data.library?.name || '')

    showSuccess('Workspace created successfully')

    await setupPushForCurrentAdmin()
    router.push('/dashboard')
  } catch (err) {
    if (err.response) {
      const detail = err.response.data?.detail
      error.value = typeof detail === 'string' ? detail : 'Signup failed. Please try again.'
    } else {
      error.value = 'Network error. Please check your connection.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.signup-page {
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
  padding: 2rem 1rem 3rem;
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

.signup-shell {
  width: min(1120px, 100%);
  margin: 0 auto;
  display: grid;
  gap: 1.1rem;
}

.intro-card,
.form-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 22px;
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
  font-size: clamp(2rem, 4.8vw, 3.4rem);
  line-height: 1.04;
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
  line-height: 1.65;
}

.intro-points {
  margin-top: 1.1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.point-chip,
.section-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(15, 23, 42, 0.55);
  padding: 0.55rem 0.85rem;
  font-size: 0.9rem;
  color: #dbeafe;
}

.point-icon,
.section-icon {
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

.signup-form {
  margin-top: 1rem;
  display: grid;
  gap: 1rem;
}

.form-section {
  display: grid;
  gap: 0.8rem;
}

.field-grid {
  display: grid;
  gap: 0.8rem;
}

.two-col {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.input-label {
  display: block;
  margin-bottom: 0.38rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #cbd5e1;
}

.label-hint {
  color: var(--text-secondary);
  font-weight: 500;
}

.input-wrap {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  min-height: 3.2rem;
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.14);
  background: rgba(15, 23, 42, 0.62);
  padding: 0 0.95rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.input-wrap:focus-within {
  border-color: rgba(56, 189, 248, 0.7);
  box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.12);
}

.input-wrap.error {
  border-color: rgba(248, 113, 113, 0.75);
}

.input-icon,
.toggle-icon {
  width: 1rem;
  height: 1rem;
  color: #7dd3fc;
  flex-shrink: 0;
}

.input-wrap input {
  width: 100%;
  height: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--text-primary);
  font-size: 0.96rem;
}

.input-wrap input::placeholder {
  color: rgba(148, 163, 184, 0.72);
}

.toggle-btn {
  border: 0;
  background: transparent;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.signup-btn {
  margin-top: 0.2rem;
  min-height: 3.35rem;
  border: 0;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  background: linear-gradient(135deg, var(--brand-a), var(--brand-b));
  color: #06111f;
  font-weight: 800;
  font-size: 1rem;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
  box-shadow: 0 20px 44px rgba(14, 165, 233, 0.22);
}

.signup-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.signup-btn:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

.btn-arrow,
.spinner {
  width: 1rem;
  height: 1rem;
}

.spinner {
  animation: spin 0.9s linear infinite;
}

.error-banner {
  margin: 0;
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  color: #fecaca;
  background: rgba(127, 29, 29, 0.35);
  border: 1px solid rgba(248, 113, 113, 0.25);
  border-radius: 14px;
  padding: 0.85rem 0.95rem;
}

.error-icon {
  width: 1rem;
  height: 1rem;
  margin-top: 0.1rem;
  flex-shrink: 0;
}

.form-footer-links {
  margin-top: 1rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  color: var(--text-secondary);
  font-size: 0.92rem;
}

.form-footer-links a {
  color: #7dd3fc;
  text-decoration: none;
}

.form-footer-links a:hover {
  color: #bae6fd;
}

@keyframes mesh-drift {
  from {
    transform: scale(1) translate3d(0, 0, 0);
  }
  to {
    transform: scale(1.04) translate3d(-1.5%, 1.5%, 0);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 760px) {
  .signup-page {
    padding: 1.25rem 0.9rem 2rem;
  }

  .two-col {
    grid-template-columns: 1fr;
  }

  .intro-card,
  .form-card {
    padding: 1.1rem;
    border-radius: 18px;
  }
}
</style>
