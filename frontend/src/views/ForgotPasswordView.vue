<template>
  <main class="auth-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="auth-shell glass-card">
      <header class="auth-head">
        <p class="kicker">Account Recovery</p>
        <h1>Reset your password</h1>
        <p>Request a reset link by email or ask for a one-time OTP code.</p>
      </header>

      <div class="mode-row">
        <button type="button" class="mode-btn" :class="{ active: mode === 'link' }" @click="mode = 'link'">Email Link</button>
        <button type="button" class="mode-btn" :class="{ active: mode === 'otp' }" @click="mode = 'otp'">Email OTP</button>
      </div>

      <form class="auth-form" @submit.prevent="submitRequest">
        <label class="input-label" for="email">Verified Email</label>
        <div class="input-wrap" :class="{ error: error && !email }">
          <Mail class="input-icon" aria-hidden="true" />
          <input id="email" v-model="email" type="email" placeholder="Enter your verified email" autocomplete="email" required @blur="normalizeEmail" />
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
          <span>{{ loading ? 'Sending...' : (mode === 'link' ? 'Send Reset Link' : 'Send OTP Code') }}</span>
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
        <router-link :to="{ path: '/reset-password', query: { email, mode: 'otp' } }">Have an OTP already?</router-link>
      </div>
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { AlertTriangle, BadgeCheck, LoaderCircle, Mail } from 'lucide-vue-next'
import API from '../api'
import TurnstileWidget from '../components/TurnstileWidget.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')
const mode = ref('link')
const loading = ref(false)
const error = ref('')
const successMessage = ref('')
const requiresCaptcha = ref(false)
const captchaToken = ref('')
const captchaResetKey = ref(0)
const turnstileConfig = ref({ enabled: false, site_key: null })

const normalizeEmail = () => {
  email.value = email.value.trim().toLowerCase()
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

const submitRequest = async () => {
  error.value = ''
  successMessage.value = ''
  normalizeEmail()
  if (!email.value) {
    error.value = 'Please enter your verified email address.'
    return
  }

  loading.value = true
  try {
    const endpoint = mode.value === 'link' ? '/auth/password-reset/request-link' : '/auth/password-reset/request-otp'
    const res = await API.post(endpoint, {
      email: email.value,
      captcha_token: requiresCaptcha.value ? captchaToken.value : null,
    })
    successMessage.value = res.data.message
    requiresCaptcha.value = false
    captchaToken.value = ''
    captchaResetKey.value += 1
    if (mode.value === 'otp') {
      router.push({ path: '/reset-password', query: { email: email.value, mode: 'otp' } })
    }
  } catch (err) {
    applyAuthError(err, 'Unable to start password recovery.')
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

.kicker { margin: 0; color: #7dd3fc; text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.78rem; }
.auth-head h1 { margin: 0.45rem 0; font-size: clamp(1.9rem, 4vw, 2.8rem); }
.auth-head p { margin: 0; color: #94a3b8; }
.mode-row { margin-top: 1rem; display: flex; gap: 0.7rem; }
.mode-btn {
  flex: 1;
  min-height: 42px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(15, 23, 42, 0.6);
  color: #cbd5e1;
  cursor: pointer;
}
.mode-btn.active { border-color: rgba(56, 189, 248, 0.45); color: #e0f2fe; }
.auth-form { margin-top: 1rem; display: grid; gap: 0.9rem; }
.input-label { display: block; font-weight: 600; color: #cbd5e1; }
.input-wrap {
  display: flex; align-items: center; gap: 0.7rem; min-height: 3.2rem;
  border-radius: 16px; border: 1px solid rgba(148, 163, 184, 0.14);
  background: rgba(15, 23, 42, 0.62); padding: 0 0.95rem;
}
.input-wrap.error { border-color: rgba(248, 113, 113, 0.75); }
.input-wrap input { width: 100%; border: 0; outline: 0; background: transparent; color: #e2e8f0; font-size: 0.96rem; }
.primary-btn {
  min-height: 3.15rem; border: 0; border-radius: 16px; cursor: pointer;
  background: linear-gradient(135deg, #22d3ee, #3b82f6); color: #06111f; font-weight: 800;
  display: inline-flex; align-items: center; justify-content: center; gap: 0.55rem;
}
.banner { margin: 0; padding: 0.85rem 0.95rem; border-radius: 14px; display: flex; gap: 0.55rem; }
.banner.success { background: rgba(16, 185, 129, 0.12); color: #d1fae5; }
.banner.error { background: rgba(239, 68, 68, 0.12); color: #fecaca; }
.footer-links { margin-top: 1rem; display: flex; flex-wrap: wrap; gap: 0.55rem; justify-content: center; color: #94a3b8; }
.footer-links a { color: #7dd3fc; text-decoration: none; }
.spinner, .input-icon, .banner-icon { width: 1rem; height: 1rem; }
.spinner { animation: spin 0.9s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
