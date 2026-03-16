<template>
  <main class="status-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="status-shell glass-card">
      <header class="status-head">
        <p class="kicker">Signup Status</p>
        <h1>Track your library onboarding</h1>
        <p v-if="statusData">Status for <strong>{{ statusData.library_name }}</strong></p>
      </header>

      <div class="steps-grid">
        <article class="step-card" :class="stepClass(1)">
          <MailCheck class="step-icon" aria-hidden="true" />
          <span>Email Verify</span>
        </article>
        <article class="step-card" :class="stepClass(2)">
          <ShieldCheck class="step-icon" aria-hidden="true" />
          <span>Approval Queue</span>
        </article>
        <article class="step-card" :class="stepClass(3)">
          <BadgeCheck class="step-icon" aria-hidden="true" />
          <span>Workspace Ready</span>
        </article>
      </div>

      <div v-if="loading" class="state-card centered">
        <LoaderCircle class="spinner" aria-hidden="true" />
        <p>Loading signup status...</p>
      </div>

      <div v-else-if="statusData" class="content-grid">
        <article class="state-card status-overview">
          <div class="status-line">
            <span class="status-pill" :class="`status-${statusData.status}`">{{ humanStatus }}</span>
            <span class="meta-text">Requested by {{ statusData.admin_username }}</span>
          </div>

          <h2>{{ headline }}</h2>
          <p class="lead-copy">{{ description }}</p>

          <p v-if="successMessage" class="banner success">
            <BadgeCheck class="banner-icon" aria-hidden="true" />
            <span>{{ successMessage }}</span>
          </p>
          <p v-if="error" class="banner error">
            <AlertTriangle class="banner-icon" aria-hidden="true" />
            <span>{{ error }}</span>
          </p>

          <div class="actions-row">
            <button
              v-if="canResend"
              type="button"
              class="btn btn-solid"
              :disabled="actionLoading"
              @click="resendVerification"
            >
              <LoaderCircle v-if="actionLoading" class="spinner small" aria-hidden="true" />
              <span>{{ actionLoading ? 'Sending...' : 'Resend Verification' }}</span>
            </button>

            <router-link v-if="canLogin" to="/login" class="btn btn-solid">Go to Login</router-link>
            <button v-if="canResubmit" type="button" class="btn btn-solid" @click="goToResubmit">Edit and Resubmit</button>
            <router-link v-if="showBackToSignup" to="/signup" class="btn btn-ghost">Back to Signup</router-link>
          </div>

          <TurnstileWidget
            v-if="requiresCaptcha && turnstileConfig.enabled"
            :site-key="turnstileConfig.site_key"
            :reset-key="captchaResetKey"
            @verified="onCaptchaVerified"
            @expired="onCaptchaExpired"
          />
        </article>

        <article class="state-card detail-card">
          <h3>Request Details</h3>
          <dl class="detail-grid">
            <div>
              <dt>Library</dt>
              <dd>{{ statusData.library_name }}</dd>
            </div>
            <div>
              <dt>Email</dt>
              <dd>{{ statusData.admin_email }}</dd>
            </div>
            <div>
              <dt>Phone</dt>
              <dd>{{ statusData.contact_phone }}</dd>
            </div>
            <div>
              <dt>Username</dt>
              <dd>{{ statusData.admin_username }}</dd>
            </div>
            <div v-if="statusData.address">
              <dt>Address</dt>
              <dd>{{ statusData.address }}</dd>
            </div>
            <div>
              <dt>Seats</dt>
              <dd>{{ statusData.max_seats }}</dd>
            </div>
            <div>
              <dt>Submitted</dt>
              <dd>{{ formatDateTime(statusData.submitted_at) }}</dd>
            </div>
            <div v-if="statusData.verified_at">
              <dt>Verified</dt>
              <dd>{{ formatDateTime(statusData.verified_at) }}</dd>
            </div>
            <div v-if="statusData.approved_at">
              <dt>Approved</dt>
              <dd>{{ formatDateTime(statusData.approved_at) }}</dd>
            </div>
            <div v-if="statusData.rejected_at">
              <dt>Rejected</dt>
              <dd>{{ formatDateTime(statusData.rejected_at) }}</dd>
            </div>
          </dl>

          <div v-if="statusData.rejection_reason" class="rejection-box">
            <h4>Rejection Reason</h4>
            <p>{{ statusData.rejection_reason }}</p>
          </div>
        </article>
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
  LoaderCircle,
  MailCheck,
  ShieldCheck,
} from 'lucide-vue-next'
import API from '../api'
import TurnstileWidget from '../components/TurnstileWidget.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const actionLoading = ref(false)
const error = ref('')
const successMessage = ref('')
const statusData = ref(null)
const requiresCaptcha = ref(false)
const captchaToken = ref('')
const captchaResetKey = ref(0)
const turnstileConfig = ref({ enabled: false, site_key: null })
const handledVerifyToken = ref('')

const currentStatus = computed(() => statusData.value?.status || '')
const humanStatus = computed(() => {
  const map = {
    pending_email_verification: 'Email Verification Pending',
    pending_approval: 'Pending Approval',
    approved: 'Approved',
    rejected: 'Rejected',
    expired: 'Expired',
  }
  return map[currentStatus.value] || 'Pending'
})

const headline = computed(() => {
  switch (currentStatus.value) {
    case 'pending_email_verification':
      return 'Verify your email to continue'
    case 'pending_approval':
      return 'Your signup is waiting for review'
    case 'approved':
      return 'Your workspace is ready'
    case 'rejected':
      return 'Your signup needs changes'
    case 'expired':
      return 'This verification request expired'
    default:
      return 'Checking signup status'
  }
})

const description = computed(() => {
  switch (currentStatus.value) {
    case 'pending_email_verification':
      return 'Open the verification email we sent and confirm your email address. You can resend it from here if needed.'
    case 'pending_approval':
      return 'Your email is verified. The request is now visible in the superadmin approval queue.'
    case 'approved':
      return 'The library and admin account have been created. You can now log in and start using the app.'
    case 'rejected':
      return 'Please review the rejection reason below and resubmit the request using the secure link from your email.'
    case 'expired':
      return 'The earlier verification window has expired. You can request a fresh verification email from this page.'
    default:
      return ''
  }
})

const canResend = computed(() => ['pending_email_verification', 'expired'].includes(currentStatus.value))
const canLogin = computed(() => currentStatus.value === 'approved')
const canResubmit = computed(() => currentStatus.value === 'rejected' && Boolean(route.query.resubmit_token))
const showBackToSignup = computed(() => !canLogin.value && !canResubmit.value)

const stepClass = (step) => {
  if (currentStatus.value === 'approved') {
    return 'is-complete'
  }
  if (currentStatus.value === 'pending_approval') {
    return step <= 2 ? 'is-complete' : 'is-pending'
  }
  if (currentStatus.value === 'pending_email_verification' || currentStatus.value === 'expired') {
    return step === 1 ? 'is-active' : 'is-pending'
  }
  if (currentStatus.value === 'rejected') {
    return step <= 2 ? 'is-complete is-rejected' : 'is-pending'
  }
  return 'is-pending'
}

const formatDateTime = (value) => {
  if (!value) return '—'
  return new Intl.DateTimeFormat('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'Asia/Kolkata',
  }).format(new Date(value))
}

const loadTurnstileConfig = async () => {
  try {
    const res = await API.get('/auth/turnstile/config')
    turnstileConfig.value = res.data
  } catch (err) {
    turnstileConfig.value = { enabled: false, site_key: null }
  }
}

const loadStatus = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await API.get(`/auth/signup-requests/${route.params.publicId}`)
    statusData.value = res.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Unable to load signup status.'
  } finally {
    loading.value = false
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

const tryVerify = async () => {
  const verifyToken = route.query.verify_token
  if (!verifyToken || handledVerifyToken.value === verifyToken) {
    return
  }

  handledVerifyToken.value = String(verifyToken)
  actionLoading.value = true
  error.value = ''
  try {
    const res = await API.post('/auth/signup/verify-email', { token: verifyToken })
    successMessage.value = res.data.message
    await router.replace({ path: route.path, query: { ...route.query, verify_token: undefined } })
    await loadStatus()
  } catch (err) {
    applyAuthError(err, 'Unable to verify email.')
  } finally {
    actionLoading.value = false
  }
}

const resendVerification = async () => {
  actionLoading.value = true
  error.value = ''
  successMessage.value = ''
  try {
    const res = await API.post('/auth/signup/resend-verification', {
      public_id: route.params.publicId,
      captcha_token: requiresCaptcha.value ? captchaToken.value : null,
    })
    successMessage.value = res.data.message
    requiresCaptcha.value = false
    captchaToken.value = ''
    captchaResetKey.value += 1
    await loadStatus()
  } catch (err) {
    applyAuthError(err, 'Unable to resend verification email.')
  } finally {
    actionLoading.value = false
  }
}

const goToResubmit = () => {
  router.push({
    path: '/signup',
    query: {
      public_id: route.params.publicId,
      resubmit_token: route.query.resubmit_token,
    },
  })
}

const onCaptchaVerified = (token) => {
  captchaToken.value = token
}

const onCaptchaExpired = () => {
  captchaToken.value = ''
}

onMounted(async () => {
  await Promise.all([loadTurnstileConfig(), loadStatus()])
  await tryVerify()
})

watch(() => route.query.verify_token, () => {
  tryVerify()
})
</script>

<style scoped>
.status-page {
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

.status-shell {
  width: min(1080px, 100%);
  margin: 0 auto;
  padding: 1.4rem;
}

.glass-card,
.state-card,
.step-card {
  border: 1px solid rgba(255, 255, 255, 0.04);
  background: rgba(148, 163, 184, 0.03);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 20px;
}

.kicker {
  margin: 0;
  color: #7dd3fc;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.78rem;
}

.status-head h1 {
  margin: 0.5rem 0;
  font-size: clamp(1.9rem, 4vw, 3rem);
}

.status-head p {
  margin: 0;
  color: #94a3b8;
}

.steps-grid,
.content-grid {
  display: grid;
  gap: 1rem;
}

.steps-grid {
  margin-top: 1.2rem;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.step-card {
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 0.7rem;
  color: #94a3b8;
}

.step-card.is-complete {
  border-color: rgba(45, 212, 191, 0.35);
  color: #d1fae5;
}

.step-card.is-active {
  border-color: rgba(56, 189, 248, 0.4);
  color: #e0f2fe;
}

.step-card.is-rejected {
  border-color: rgba(248, 113, 113, 0.35);
}

.step-icon,
.banner-icon,
.spinner {
  width: 1rem;
  height: 1rem;
}

.spinner {
  animation: spin 0.9s linear infinite;
}

.content-grid {
  margin-top: 1rem;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
}

.state-card {
  padding: 1.2rem;
}

.centered {
  margin-top: 1rem;
  display: grid;
  justify-items: center;
  gap: 0.75rem;
}

.status-line,
.actions-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}

.status-pill {
  padding: 0.45rem 0.8rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 700;
}

.status-pending_email_verification,
.status-expired {
  background: rgba(59, 130, 246, 0.15);
  color: #bfdbfe;
}

.status-pending_approval {
  background: rgba(245, 158, 11, 0.15);
  color: #fde68a;
}

.status-approved {
  background: rgba(16, 185, 129, 0.15);
  color: #bbf7d0;
}

.status-rejected {
  background: rgba(239, 68, 68, 0.15);
  color: #fecaca;
}

.meta-text,
.lead-copy,
.detail-grid dt,
.rejection-box p {
  color: #94a3b8;
}

.status-overview h2,
.detail-card h3,
.rejection-box h4 {
  margin: 0.9rem 0 0.4rem;
}

.banner {
  margin-top: 1rem;
  padding: 0.85rem 1rem;
  border-radius: 14px;
  display: flex;
  gap: 0.6rem;
  align-items: center;
}

.banner.success {
  background: rgba(16, 185, 129, 0.12);
  color: #d1fae5;
}

.banner.error {
  background: rgba(239, 68, 68, 0.12);
  color: #fecaca;
}

.actions-row {
  margin-top: 1.2rem;
}

.btn {
  min-height: 44px;
  padding: 0.72rem 1rem;
  border-radius: 14px;
  border: 1px solid transparent;
  text-decoration: none;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.55rem;
  cursor: pointer;
}

.btn-solid {
  background: linear-gradient(135deg, #22d3ee, #3b82f6);
  color: #06111f;
}

.btn-ghost {
  background: rgba(15, 23, 42, 0.65);
  color: #e2e8f0;
  border-color: rgba(148, 163, 184, 0.18);
}

.detail-grid {
  display: grid;
  gap: 0.8rem;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.detail-grid dd {
  margin: 0.3rem 0 0;
  color: #f8fafc;
}

.rejection-box {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(148, 163, 184, 0.12);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 900px) {
  .content-grid,
  .steps-grid,
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
