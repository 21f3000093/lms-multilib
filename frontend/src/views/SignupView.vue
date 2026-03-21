<template>
  <main class="signup-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="signup-shell">
      <article class="intro-card">
        <p class="kicker">Smart Library App</p>
        <h1>
          {{ heroLead }}
          <span class="gradient-text">{{ heroAccent }}</span>
        </h1>
        <p>{{ heroDescription }}</p>

        <div class="intro-points">
          <div class="point-chip">
            <ShieldCheck class="point-icon" aria-hidden="true" />
            Email verification first
          </div>
          <div class="point-chip">
            <Sparkles class="point-icon" aria-hidden="true" />
            Risk-based instant activation
          </div>
          <div class="point-chip">
            <CircleDollarSign class="point-icon" aria-hidden="true" />
            Trial starts on activation
          </div>
          <div class="point-chip">
            <Mail class="point-icon" aria-hidden="true" />
            Google signup available
          </div>
        </div>
      </article>

      <article class="form-card">
        <header class="form-head">
          <h2>{{ formHeading }}</h2>
          <p>{{ formSubheading }}</p>
        </header>

        <div v-if="!isResubmitMode && !isGoogleOnboarding" class="google-entry">
          <GoogleAuthButton
            text="continue_with"
            hint="Use Google to skip password creation and email verification."
            @credential="handleGoogleCredential"
            @error="handleGoogleError"
          />
          <div class="divider" aria-hidden="true">
            <span></span>
            <p>or continue with email</p>
            <span></span>
          </div>
        </div>

        <p v-if="isGoogleOnboarding" class="info-banner">
          <ShieldCheck class="info-icon" aria-hidden="true" />
          <span>
            <strong>Google account verified.</strong> Add your library details to finish creating the workspace.
          </span>
        </p>

        <p v-if="resubmitReason" class="info-banner">
          <AlertTriangle class="info-icon" aria-hidden="true" />
          <span><strong>Rejection reason:</strong> {{ resubmitReason }}</span>
        </p>

        <form class="signup-form" @submit.prevent="submitForm">
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
                <div class="input-wrap" :class="{ error: error && !form.admin_email, readonly: isGoogleSignupLike }">
                  <Mail class="input-icon" aria-hidden="true" />
                  <input
                    id="admin-email"
                    v-model="form.admin_email"
                    type="email"
                    autocomplete="email"
                    placeholder="you@example.com"
                    :readonly="isGoogleSignupLike"
                    :disabled="isGoogleSignupLike"
                    required
                    @blur="normalizeEmail"
                  />
                </div>
              </div>
            </div>

            <div v-if="showPasswordFields" class="field-grid two-col">
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

          <TurnstileWidget
            v-if="requiresCaptcha && turnstileConfig.enabled"
            :site-key="turnstileConfig.site_key"
            :reset-key="captchaResetKey"
            @verified="onCaptchaVerified"
            @expired="onCaptchaExpired"
          />

          <button type="submit" class="signup-btn" :disabled="loading">
            <LoaderCircle v-if="loading" class="spinner" aria-hidden="true" />
            <span>{{ loading ? (isResubmitMode ? 'Resubmitting...' : 'Submitting...') : (isResubmitMode ? 'Resubmit Request' : 'Submit Signup Request') }}</span>
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
          <router-link to="/forgot-password">Forgot Password</router-link>
          <span>•</span>
          <router-link to="/pricing-plans">Pricing</router-link>
        </div>
      </article>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import {
  AlertCircle,
  AlertTriangle,
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
import { useRouter, useRoute } from 'vue-router'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'
import API from '../api'
import GoogleAuthButton from '../components/GoogleAuthButton.vue'
import TurnstileWidget from '../components/TurnstileWidget.vue'
import { homeRouteForRole, storeAdminSession } from '../utils/authSession'

const router = useRouter()
const route = useRoute()
const toast = useToast()
const GOOGLE_ONBOARDING_KEY = 'google_signup_onboarding'

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

const loading = ref(false)
const error = ref('')
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const resubmitReason = ref('')
const signupMethod = ref('password')
const requiresCaptcha = ref(false)
const captchaToken = ref('')
const captchaResetKey = ref(0)
const turnstileConfig = ref({ enabled: false, site_key: null })
const googleOnboarding = ref(null)

const isResubmitMode = computed(() => Boolean(route.query.resubmit_token && route.query.public_id))
const isGoogleOnboarding = computed(() => Boolean(googleOnboarding.value?.onboarding_token))
const isGoogleSignupLike = computed(() => isGoogleOnboarding.value || signupMethod.value === 'google')
const showPasswordFields = computed(() => signupMethod.value === 'password' && !isGoogleOnboarding.value)

const heroLead = computed(() => {
  if (isGoogleOnboarding.value) return 'Finish your'
  if (isResubmitMode.value) return 'Update your request and'
  return 'Launch your library workspace with'
})

const heroAccent = computed(() => {
  if (isGoogleOnboarding.value) return 'Google signup'
  if (isResubmitMode.value) return 'resubmit for activation'
  return 'low-friction signup'
})

const heroDescription = computed(() => {
  if (isGoogleOnboarding.value) {
    return 'Your Google email is already verified. Add the remaining library details and we will activate safe signups instantly.'
  }
  if (isResubmitMode.value) {
    return 'Make the requested changes and send the signup back through verification so we can activate it cleanly.'
  }
  return 'Choose email signup or continue with Google. Safe signups activate immediately after verification, and only risky ones go to manual review.'
})

const formHeading = computed(() => {
  if (isGoogleOnboarding.value) return 'Complete your Google signup'
  if (isResubmitMode.value) return 'Resubmit signup request'
  return 'Create your library workspace'
})

const formSubheading = computed(() => {
  if (isGoogleOnboarding.value) return 'We already verified your Google account. Only the workspace details are left.'
  if (isResubmitMode.value) return 'Review the rejected request and send the updated version.'
  return 'Submit your library details and owner account to start the verification and activation flow.'
})

const showError = (message) => {
  toast.error(message, {
    style: {
      backgroundColor: 'var(--theme-panel-solid)',
      color: 'var(--theme-text-strong)',
      border: '1px solid var(--theme-danger-border)',
      borderRadius: '12px',
      boxShadow: 'var(--theme-shadow-soft)',
    },
  })
}

const showSuccess = (message) => {
  toast.success(message, {
    style: {
      backgroundColor: 'var(--theme-panel-solid)',
      color: 'var(--theme-text-strong)',
      border: '1px solid var(--theme-brand-border)',
      borderRadius: '12px',
      boxShadow: 'var(--theme-shadow-soft)',
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
  if (isGoogleSignupLike.value) {
    form.admin_email = (form.admin_email || '').trim().toLowerCase()
    return
  }
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
  if (showPasswordFields.value) {
    normalizePassword()
    normalizeConfirmPassword()
  }
}

const loadTurnstileConfig = async () => {
  try {
    const res = await API.get('/auth/turnstile/config')
    turnstileConfig.value = res.data
  } catch (err) {
    turnstileConfig.value = { enabled: false, site_key: null }
  }
}

const loadResubmitContext = async () => {
  if (!isResubmitMode.value) {
    return
  }
  try {
    const res = await API.get(`/auth/signup-requests/${route.query.public_id}`)
    if (res.data.status !== 'rejected') {
      error.value = 'This resubmit link is no longer available.'
      return
    }
    signupMethod.value = res.data.signup_method || 'password'
    form.library_name = res.data.library_name || ''
    form.max_seats = res.data.max_seats || 25
    form.contact_phone = res.data.contact_phone || ''
    form.address = res.data.address || ''
    form.admin_username = res.data.admin_username || ''
    form.admin_email = res.data.admin_email || ''
    resubmitReason.value = res.data.rejection_reason || ''
  } catch (err) {
    error.value = err.response?.data?.detail || 'Unable to load the rejected signup request.'
  }
}

const persistGoogleOnboarding = (payload) => {
  sessionStorage.setItem(GOOGLE_ONBOARDING_KEY, JSON.stringify(payload))
  googleOnboarding.value = payload
  signupMethod.value = 'google'
  form.admin_email = payload.prefill_email || ''
  if (!form.admin_username) {
    form.admin_username = payload.suggested_username || ''
  }
}

const loadGoogleOnboarding = () => {
  if (!route.query.google) {
    return
  }
  const raw = sessionStorage.getItem(GOOGLE_ONBOARDING_KEY)
  if (!raw) {
    return
  }
  try {
    const payload = JSON.parse(raw)
    if (payload?.onboarding_token) {
      persistGoogleOnboarding(payload)
    }
  } catch (err) {
    sessionStorage.removeItem(GOOGLE_ONBOARDING_KEY)
  }
}

const clearGoogleOnboarding = () => {
  googleOnboarding.value = null
  sessionStorage.removeItem(GOOGLE_ONBOARDING_KEY)
  if (!isResubmitMode.value) {
    signupMethod.value = 'password'
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

const completeAuthenticatedSignup = async (admin, message) => {
  storeAdminSession(admin)
  clearGoogleOnboarding()
  showSuccess(message)
  router.push(homeRouteForRole(admin.role))
}

const handleGoogleCredential = async (credential) => {
  error.value = ''
  loading.value = true
  try {
    const res = await API.post('/auth/google/exchange', {
      credential,
      intent: 'signup',
      captcha_token: requiresCaptcha.value ? captchaToken.value : null,
    })

    if (res.data?.action === 'logged_in' && res.data?.admin) {
      await completeAuthenticatedSignup(res.data.admin, 'Signed in with Google')
      return
    }

    if (['signup_required', 'complete_signup'].includes(res.data?.action)) {
      persistGoogleOnboarding(res.data)
      showSuccess('Google verified. Complete the remaining workspace details.')
      return
    }

    error.value = res.data?.message || 'Google signup could not be started.'
    showError(error.value)
  } catch (err) {
    applyAuthError(err, 'Google signup could not be started.')
    showError(error.value || 'Google signup could not be started.')
  } finally {
    loading.value = false
  }
}

const handleGoogleError = () => {
  error.value = 'Google signup is temporarily unavailable. Please use email signup.'
  showError(error.value)
}

const submitForm = async () => {
  error.value = ''
  normalizeAll()

  if (!form.library_name || !form.contact_phone || !form.admin_username || !form.admin_email) {
    error.value = 'Please complete all required fields'
    showError('Please fill in all required fields')
    return
  }
  if (showPasswordFields.value && (!form.password || !form.confirm_password)) {
    error.value = 'Please complete all required fields'
    showError('Please fill in all required fields')
    return
  }
  if (!Number.isInteger(Number(form.max_seats)) || Number(form.max_seats) < 1 || Number(form.max_seats) > 200) {
    error.value = 'Max seats must be between 1 and 200'
    showError('Please enter a valid seat count')
    return
  }
  if (showPasswordFields.value && form.password !== form.confirm_password) {
    error.value = 'Passwords do not match'
    showError('Passwords do not match')
    return
  }

  loading.value = true
  try {
    let res
    if (isGoogleOnboarding.value) {
      res = await API.post('/auth/google/complete-signup', {
        onboarding_token: googleOnboarding.value.onboarding_token,
        library_name: form.library_name,
        max_seats: Number(form.max_seats),
        contact_phone: form.contact_phone,
        address: form.address || null,
        admin_username: form.admin_username,
        captcha_token: requiresCaptcha.value ? captchaToken.value : null,
      })
    } else {
      const payload = {
        library_name: form.library_name,
        max_seats: Number(form.max_seats),
        contact_phone: form.contact_phone,
        address: form.address || null,
        admin_username: form.admin_username,
        admin_email: form.admin_email,
        password: form.password,
        confirm_password: form.confirm_password,
        captcha_token: requiresCaptcha.value ? captchaToken.value : null,
      }

      res = isResubmitMode.value
        ? await API.post('/auth/signup/resubmit', { ...payload, token: route.query.resubmit_token })
        : await API.post('/auth/signup', payload)
    }

    requiresCaptcha.value = false
    captchaToken.value = ''
    captchaResetKey.value += 1
    if (res.data?.action === 'logged_in' && res.data?.admin) {
      await completeAuthenticatedSignup(res.data.admin, res.data.message || 'Workspace created successfully')
      return
    }
    clearGoogleOnboarding()
    await router.push(`/signup/status/${res.data.public_id}`)
  } catch (err) {
    applyAuthError(
      err,
      isGoogleOnboarding.value
        ? 'Unable to complete Google signup.'
        : (isResubmitMode.value ? 'Unable to resubmit signup request.' : 'Unable to submit signup request.'),
    )
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

onMounted(async () => {
  loadGoogleOnboarding()
  await Promise.all([loadTurnstileConfig(), loadResubmitContext()])
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.signup-page {
  --bg: var(--theme-page-bg);
  --surface: var(--theme-surface);
  --surface-border: var(--theme-surface-border);
  --text-primary: var(--theme-text-primary);
  --text-secondary: var(--theme-text-secondary);
  --brand-a: var(--theme-brand-a);
  --brand-b: var(--theme-brand-b);
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
  background: var(--theme-mesh-background);
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
  border: 1px solid var(--theme-border);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--theme-text-soft);
  background: var(--theme-surface-soft);
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

.intro-card p,
.form-head p,
.label-hint,
.form-footer-links {
  color: var(--text-secondary);
}

.google-entry {
  display: grid;
  gap: 0.9rem;
  margin-bottom: 1rem;
}

.divider {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 0.8rem;
  color: var(--theme-text-muted);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.divider span {
  height: 1px;
  background: var(--theme-border-soft);
}

.divider p {
  margin: 0;
}

.intro-points,
.signup-form,
.form-section {
  display: grid;
  gap: 0.8rem;
}

.intro-points {
  margin-top: 1.1rem;
  display: flex;
  flex-wrap: wrap;
}

.point-chip,
.section-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  border-radius: 999px;
  border: 1px solid var(--theme-border-soft);
  background: var(--theme-panel);
  padding: 0.55rem 0.85rem;
  font-size: 0.9rem;
  color: var(--theme-text-info);
}

.point-icon,
.section-icon,
.input-icon,
.toggle-icon,
.info-icon,
.error-icon,
.spinner,
.btn-arrow {
  width: 1rem;
  height: 1rem;
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
  color: var(--theme-text-soft);
}

.input-wrap {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  min-height: 3.2rem;
  border-radius: 16px;
  border: 1px solid var(--theme-border-soft);
  background: var(--theme-input-bg-soft);
  padding: 0 0.95rem;
}

.input-wrap:focus-within {
  border-color: var(--theme-brand-border);
  box-shadow: 0 0 0 4px var(--theme-brand-ring);
}

.input-wrap.error {
  border-color: var(--theme-danger-border);
}

.input-wrap.readonly {
  opacity: 0.9;
  border-style: dashed;
}

.input-wrap input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--text-primary);
  font-size: 0.96rem;
}

.toggle-btn,
.signup-btn {
  cursor: pointer;
}

.toggle-btn {
  border: 0;
  background: transparent;
  padding: 0;
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
  color: var(--theme-brand-on);
  font-weight: 800;
  font-size: 1rem;
}

.signup-btn:disabled {
  opacity: 0.72;
  cursor: not-allowed;
}

.info-banner,
.error-banner {
  margin: 1rem 0 0;
  display: flex;
  gap: 0.6rem;
  align-items: flex-start;
  padding: 0.85rem 0.95rem;
  border-radius: 14px;
}

.info-banner {
  background: var(--theme-warning-soft);
  color: var(--theme-warning-text);
}

.error-banner {
  color: var(--theme-danger-text);
  background: var(--theme-danger-soft);
  border: 1px solid var(--theme-danger-border);
}

.form-footer-links {
  margin-top: 1rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  font-size: 0.92rem;
}

.form-footer-links a {
  color: var(--theme-brand-pill-text);
  text-decoration: none;
}

.spinner {
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 760px) {
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
