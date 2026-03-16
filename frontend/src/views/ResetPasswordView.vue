<template>
  <main class="auth-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="auth-shell glass-card">
      <header class="auth-head">
        <p class="kicker">Account Recovery</p>
        <h1>{{ isLinkMode ? 'Create a new password' : 'Confirm your OTP reset' }}</h1>
        <p>
          {{
            isLinkMode
              ? 'This secure reset link lets you set a fresh password for your admin account.'
              : 'Enter the OTP sent to your verified email, then choose a new password.'
          }}
        </p>
      </header>

      <form class="auth-form" @submit.prevent="submitReset">
        <label v-if="!isLinkMode" class="input-label" for="email">Verified Email</label>
        <div v-if="!isLinkMode" class="input-wrap" :class="{ error: error && !email }">
          <Mail class="input-icon" aria-hidden="true" />
          <input
            id="email"
            v-model="email"
            type="email"
            autocomplete="email"
            placeholder="Enter your verified email"
            required
            @blur="normalizeEmail"
          />
        </div>

        <label v-if="!isLinkMode" class="input-label" for="otp">OTP Code</label>
        <div v-if="!isLinkMode" class="input-wrap" :class="{ error: error && !otp }">
          <ShieldCheck class="input-icon" aria-hidden="true" />
          <input
            id="otp"
            v-model="otp"
            type="text"
            inputmode="numeric"
            maxlength="6"
            placeholder="Enter the 6-digit code"
            required
            @blur="normalizeOtp"
          />
        </div>

        <label class="input-label" for="new-password">New Password</label>
        <div class="input-wrap" :class="{ error: error && !newPassword }">
          <Lock class="input-icon" aria-hidden="true" />
          <input
            id="new-password"
            :type="showPassword ? 'text' : 'password'"
            v-model="newPassword"
            autocomplete="new-password"
            placeholder="Create a new password"
            required
            @blur="normalizePassword"
          />
          <button
            type="button"
            class="toggle-btn"
            :aria-label="showPassword ? 'Hide password' : 'Show password'"
            @click="showPassword = !showPassword"
          >
            <EyeOff v-if="showPassword" class="toggle-icon" aria-hidden="true" />
            <Eye v-else class="toggle-icon" aria-hidden="true" />
          </button>
        </div>

        <label class="input-label" for="confirm-password">Confirm Password</label>
        <div class="input-wrap" :class="{ error: error && !confirmPassword }">
          <Lock class="input-icon" aria-hidden="true" />
          <input
            id="confirm-password"
            :type="showConfirmPassword ? 'text' : 'password'"
            v-model="confirmPassword"
            autocomplete="new-password"
            placeholder="Confirm your new password"
            required
            @blur="normalizeConfirmPassword"
          />
          <button
            type="button"
            class="toggle-btn"
            :aria-label="showConfirmPassword ? 'Hide password' : 'Show password'"
            @click="showConfirmPassword = !showConfirmPassword"
          >
            <EyeOff v-if="showConfirmPassword" class="toggle-icon" aria-hidden="true" />
            <Eye v-else class="toggle-icon" aria-hidden="true" />
          </button>
        </div>

        <TurnstileWidget
          v-if="requiresCaptcha && turnstileConfig.enabled"
          :site-key="turnstileConfig.site_key"
          :reset-key="captchaResetKey"
          @verified="onCaptchaVerified"
          @expired="onCaptchaExpired"
        />

        <button type="submit" class="primary-btn" :disabled="loading">
          <LoaderCircle v-if="loading" class="spinner" aria-hidden="true" />
          <span>{{ loading ? 'Updating...' : 'Reset Password' }}</span>
        </button>

        <p v-if="successMessage" class="banner success">
          <BadgeCheck class="banner-icon" aria-hidden="true" />
          <span>{{ successMessage }}</span>
        </p>
        <p v-if="error" class="banner error">
          <AlertTriangle class="banner-icon" aria-hidden="true" />
          <span>{{ error }}</span>
        </p>
      </form>

      <div class="footer-links">
        <router-link to="/login">Back to login</router-link>
        <span>•</span>
        <router-link to="/forgot-password">Request another reset</router-link>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  AlertTriangle,
  BadgeCheck,
  Eye,
  EyeOff,
  LoaderCircle,
  Lock,
  Mail,
  ShieldCheck,
} from 'lucide-vue-next'
import API from '../api'
import TurnstileWidget from '../components/TurnstileWidget.vue'

const route = useRoute()
const router = useRouter()

const email = ref(String(route.query.email || ''))
const otp = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const successMessage = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const requiresCaptcha = ref(false)
const captchaToken = ref('')
const captchaResetKey = ref(0)
const turnstileConfig = ref({ enabled: false, site_key: null })

const linkToken = computed(() => String(route.query.token || ''))
const isLinkMode = computed(() => Boolean(linkToken.value))

const normalizeEmail = () => {
  email.value = email.value.trim().toLowerCase()
}

const normalizeOtp = () => {
  otp.value = otp.value.trim().replace(/\s+/g, '')
}

const normalizePassword = () => {
  newPassword.value = newPassword.value.trim()
}

const normalizeConfirmPassword = () => {
  confirmPassword.value = confirmPassword.value.trim()
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
    return
  }
  error.value = typeof detail === 'string' ? detail : fallbackMessage
}

const submitReset = async () => {
  error.value = ''
  successMessage.value = ''
  normalizeEmail()
  normalizeOtp()
  normalizePassword()
  normalizeConfirmPassword()

  if (!newPassword.value || !confirmPassword.value) {
    error.value = 'Please enter and confirm your new password.'
    return
  }

  if (!isLinkMode.value && (!email.value || !otp.value)) {
    error.value = 'Please enter your verified email and OTP code.'
    return
  }

  loading.value = true
  try {
    const payload = isLinkMode.value
      ? {
          token: linkToken.value,
          new_password: newPassword.value,
          confirm_password: confirmPassword.value,
        }
      : {
          email: email.value,
          otp: otp.value,
          new_password: newPassword.value,
          confirm_password: confirmPassword.value,
          captcha_token: requiresCaptcha.value ? captchaToken.value : null,
        }

    const endpoint = isLinkMode.value ? '/auth/password-reset/confirm-link' : '/auth/password-reset/confirm-otp'
    const res = await API.post(endpoint, payload)

    successMessage.value = res.data.message || 'Password reset successful. You can now log in.'
    requiresCaptcha.value = false
    captchaToken.value = ''
    captchaResetKey.value += 1

    window.setTimeout(() => {
      router.push('/login')
    }, 1200)
  } catch (err) {
    applyAuthError(err, 'Unable to reset your password.')
  } finally {
    loading.value = false
  }
}

const onCaptchaVerified = (token) => {
  captchaToken.value = token
}

const onCaptchaExpired = () => {
  captchaToken.value = ''
}

watch(
  () => route.query.email,
  (value) => {
    email.value = String(value || '')
  }
)

onMounted(() => {
  loadTurnstileConfig()
})
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  padding: 2rem 1rem 3rem;
  color: #e2e8f0;
}

.mesh-layer {
  position: fixed;
  inset: 0;
  z-index: -1;
  background:
    radial-gradient(45rem 24rem at 10% 15%, rgba(34, 211, 238, 0.14), transparent 70%),
    radial-gradient(40rem 24rem at 86% 8%, rgba(59, 130, 246, 0.14), transparent 68%),
    radial-gradient(36rem 22rem at 65% 88%, rgba(14, 165, 233, 0.11), transparent 70%),
    linear-gradient(180deg, #0f172a 0%, #0b1222 100%);
}

.auth-shell {
  width: min(620px, 100%);
  margin: 0 auto;
  padding: 1.4rem;
}

.glass-card {
  border: 1px solid rgba(255, 255, 255, 0.04);
  background: rgba(148, 163, 184, 0.03);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 22px;
}

.kicker {
  margin: 0;
  color: #7dd3fc;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.78rem;
}

.auth-head h1 {
  margin: 0.45rem 0;
  font-size: clamp(1.9rem, 4vw, 2.8rem);
}

.auth-head p {
  margin: 0;
  color: #94a3b8;
}

.auth-form {
  margin-top: 1rem;
  display: grid;
  gap: 0.9rem;
}

.input-label {
  display: block;
  font-weight: 600;
  color: #cbd5e1;
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
}

.input-wrap.error {
  border-color: rgba(248, 113, 113, 0.75);
}

.input-wrap input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: #e2e8f0;
  font-size: 0.96rem;
}

.toggle-btn {
  border: 0;
  background: transparent;
  color: #94a3b8;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.primary-btn {
  min-height: 3.15rem;
  border: 0;
  border-radius: 16px;
  cursor: pointer;
  background: linear-gradient(135deg, #22d3ee, #3b82f6);
  color: #06111f;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
}

.primary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.banner {
  margin: 0;
  padding: 0.85rem 0.95rem;
  border-radius: 14px;
  display: flex;
  gap: 0.55rem;
}

.banner.success {
  background: rgba(16, 185, 129, 0.12);
  color: #d1fae5;
}

.banner.error {
  background: rgba(239, 68, 68, 0.12);
  color: #fecaca;
}

.footer-links {
  margin-top: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  justify-content: center;
  color: #94a3b8;
}

.footer-links a {
  color: #7dd3fc;
  text-decoration: none;
}

.spinner,
.input-icon,
.banner-icon,
.toggle-icon {
  width: 1rem;
  height: 1rem;
}

.spinner {
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
