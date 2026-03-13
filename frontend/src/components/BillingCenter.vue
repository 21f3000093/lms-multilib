<template>
  <main class="billing-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="section-shell hero">
      <div>
        <p class="kicker">Billing</p>
        <h1>
          Subscription
          <span class="gradient-text">Control Center</span>
        </h1>
        <p class="hero-subtitle">
          Choose a plan, complete payment securely, and keep your library access active.
        </p>
      </div>
      <button type="button" class="btn btn-ghost" :disabled="isPageLoading" @click="refreshAll">
        {{ isPageLoading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </section>

    <section class="section-shell status-grid">
      <article class="glass-card status-card">
        <header>
          <p class="label">Current Status</p>
          <span class="status-pill" :class="statusClass">{{ statusLabel }}</span>
        </header>

        <div class="status-details">
          <p>
            <span>Current Plan</span>
            <strong>{{ currentPlanName }}</strong>
          </p>
          <p>
            <span>Billing Basis</span>
            <strong>{{ seatsBilled > 0 ? `${seatsBilled} seats` : '—' }}</strong>
          </p>
          <p>
            <span>Valid Until</span>
            <strong>{{ formatDate(subscription?.valid_until) }}</strong>
          </p>
          <p>
            <span>Current Period</span>
            <strong>{{ currentPeriodText }}</strong>
          </p>
        </div>
      </article>

      <article class="glass-card info-card">
        <header>
          <p class="label">How Billing Works</p>
        </header>
        <ul>
          <li>Charges are calculated from your configured seat capacity: <strong>{{ seatsBilled > 0 ? seatsBilled : '—' }} seats</strong>.</li>
          <li>Next paid period starts from <strong>{{ expectedStartDateLabel }}</strong>.</li>
          <li v-if="isFirstPaidSubscription">First paid subscription bonus is eligible and applied where plan bonus months exist.</li>
          <li v-else>First paid subscription bonus is already consumed; renewals include base billing months only.</li>
          <li>After payment capture, your subscription period extends immediately.</li>
        </ul>
      </article>
    </section>

    <section class="section-shell" v-if="messageText">
      <div class="message-banner" :class="messageTypeClass">
        <CheckCircle2 v-if="messageType === 'success'" class="message-icon" aria-hidden="true" />
        <AlertTriangle v-else class="message-icon" aria-hidden="true" />
        <span class="message-text">{{ messageText }}</span>
        <button
          v-if="showRetryVerifyButton"
          type="button"
          class="btn btn-ghost btn-mini"
          :disabled="verifyLoading || isAnyCheckoutBusy"
          @click="retryLastVerification"
        >
          <LoaderCircle v-if="verifyLoading" class="btn-spin" aria-hidden="true" />
          <span>{{ verifyLoading ? 'Retrying...' : 'Retry Verify' }}</span>
        </button>
      </div>
    </section>

    <section class="section-shell plans-shell glass-card">
      <header class="plans-header">
        <h2>Available Plans</h2>
        <p>Select a plan and proceed with secure Razorpay checkout.</p>
      </header>

      <div v-if="isPageLoading" class="state-text">Loading plans...</div>
      <div v-else-if="pageError" class="state-text error">{{ pageError }}</div>
      <div v-else-if="!plans.length" class="state-text">No active plans available right now.</div>

      <div v-else class="plans-grid">
        <article
          v-for="plan in plans"
          :key="plan.code"
          class="plan-card"
          :class="{ current: isCurrentPlan(plan) }"
        >
          <div class="plan-head">
            <div>
              <h3>{{ plan.name }}</h3>
              <p>{{ plan.description || 'Subscription plan' }}</p>
            </div>
            <span v-if="isCurrentPlan(plan)" class="current-pill">Current</span>
          </div>

          <div class="plan-price">
            <p class="price-value">₹{{ formatPaise(plan.price_per_seat_paise) }}</p>
            <p class="price-note">per seat / month (base rate)</p>
            <p class="pay-now">Pay now: ₹{{ formatPaise(payableNowPaise(plan)) }}</p>
          </div>

          <div class="plan-metrics">
            <p>
              <span>Billing cycle</span>
              <strong>{{ plan.billing_months }} month{{ plan.billing_months > 1 ? 's' : '' }}</strong>
            </p>
            <p>
              <span>Seats billed</span>
              <strong>{{ seatsForPlan(plan) }}</strong>
            </p>
            <p>
              <span>Bonus applied now</span>
              <strong>{{ bonusMonthsApplied(plan) }}</strong>
            </p>
            <p>
              <span>Coverage months</span>
              <strong>{{ coverageMonths(plan) }}</strong>
            </p>
            <p>
              <span>Effective monthly total</span>
              <strong>₹{{ formatPaise(effectiveMonthlyTotalPaise(plan)) }}</strong>
            </p>
            <p>
              <span>Effective per seat / month</span>
              <strong>₹{{ formatPaise(effectiveMonthlyPerSeatPaise(plan)) }}</strong>
            </p>
            <p>
              <span>Estimated period</span>
              <strong>{{ periodWindowText(plan) }}</strong>
            </p>
          </div>

          <button
            type="button"
            class="btn btn-solid full"
            :disabled="isAnyCheckoutBusy || verifyLoading"
            @click="startCheckout(plan)"
          >
            <LoaderCircle
              v-if="checkoutLoadingCode === plan.code || verifyLoading"
              class="btn-spin"
              aria-hidden="true"
            />
            <span>
              {{ checkoutLoadingCode === plan.code ? 'Creating order...' : verifyLoading ? 'Verifying payment...' : checkoutLabel(plan) }}
            </span>
          </button>
        </article>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { AlertTriangle, CheckCircle2, LoaderCircle } from 'lucide-vue-next'
import API from '../api'

const plans = ref([])
const subscription = ref(null)
const quoteContext = ref({
  seats_billed: 0,
  is_first_paid_subscription: false,
  expected_start_date: null,
})
const isPageLoading = ref(true)
const pageError = ref('')

const checkoutLoadingCode = ref('')
const verifyLoading = ref(false)
const messageText = ref('')
const messageType = ref('success')
const lastVerificationPayload = ref(null)

const isAnyCheckoutBusy = computed(() => Boolean(checkoutLoadingCode.value))

const statusLabel = computed(() => {
  const status = String(subscription.value?.status || 'inactive').toLowerCase()
  if (status === 'active') return 'Active'
  if (status === 'trialing') return 'Trialing'
  if (status === 'grace') return 'Grace'
  if (status === 'past_due') return 'Past Due'
  if (status === 'expired') return 'Expired'
  return 'Inactive'
})

const statusClass = computed(() => {
  const status = String(subscription.value?.status || 'inactive').toLowerCase()
  if (status === 'active') return 'status-active'
  if (status === 'trialing') return 'status-trial'
  if (status === 'grace') return 'status-grace'
  if (status === 'past_due') return 'status-risk'
  if (status === 'expired') return 'status-expired'
  return 'status-inactive'
})

const currentPlanName = computed(() => {
  return (
    subscription.value?.plan_config?.name ||
    subscription.value?.plan ||
    'Not subscribed'
  )
})

const currentPeriodText = computed(() => {
  const start = formatDate(subscription.value?.current_period_start)
  const end = formatDate(subscription.value?.current_period_end)
  if (start === '—' || end === '—') return '—'
  return `${start} to ${end}`
})

const seatsBilled = computed(() => Number(quoteContext.value?.seats_billed || 0))

const isFirstPaidSubscription = computed(() => Boolean(quoteContext.value?.is_first_paid_subscription))

const expectedStartDateLabel = computed(() => formatDate(quoteContext.value?.expected_start_date))

const messageTypeClass = computed(() => {
  return messageType.value === 'success' ? 'message-success' : 'message-error'
})

const showRetryVerifyButton = computed(() => {
  return messageType.value === 'error' && Boolean(lastVerificationPayload.value)
})

function formatDate(value) {
  if (!value) return '—'
  const dt = new Date(value)
  if (Number.isNaN(dt.getTime())) return '—'
  return dt.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  })
}

function formatPaise(paise) {
  const amount = Number(paise || 0) / 100
  return amount.toLocaleString('en-IN', {
    minimumFractionDigits: amount % 1 === 0 ? 0 : 2,
    maximumFractionDigits: 2,
  })
}

function isCurrentPlan(plan) {
  return Number(subscription.value?.plan_id || 0) === Number(plan.id)
}

function checkoutLabel(plan) {
  if (isCurrentPlan(plan) && String(subscription.value?.status || '').toLowerCase() === 'active') {
    return 'Renew / Extend'
  }
  return 'Choose Plan'
}

function extractError(error, fallback) {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string' && detail.trim()) return detail
  if (typeof detail === 'object' && detail?.message) return detail.message
  if (typeof error?.message === 'string' && error.message.trim()) return error.message
  return fallback
}

function getErrorDetailText(error) {
  const detail = error?.response?.data?.detail
  return typeof detail === 'string' ? detail : ''
}

function isRetryableVerifyError(error) {
  const status = Number(error?.response?.status || 0)
  const detailText = getErrorDetailText(error)
  if (status === 409 && detailText.includes('authorized but not captured')) return true
  if (status === 502 && detailText.includes('Unable to confirm payment capture')) return true
  return false
}

function mapVerifyPaymentError(error) {
  const status = Number(error?.response?.status || 0)
  const detailText = getErrorDetailText(error)

  if (status === 409 && detailText.includes('authorized but not captured')) {
    return 'Payment is authorized but capture is still in progress. Please wait a few seconds and try again.'
  }

  if (status === 502 && detailText.includes('Unable to confirm payment capture')) {
    return 'Could not confirm payment capture from gateway yet. Please wait a few seconds and retry.'
  }

  return extractError(error, 'Payment verification failed')
}

async function verifyPaymentRequest(verifyPayload) {
  verifyLoading.value = true
  try {
    const verifyRes = await API.post('/billing/verify-payment', verifyPayload)
    subscription.value = verifyRes.data.subscription
    messageType.value = 'success'
    messageText.value = verifyRes.data.message || 'Payment verified successfully'
    lastVerificationPayload.value = null
  } catch (error) {
    messageType.value = 'error'
    messageText.value = mapVerifyPaymentError(error)
    if (!isRetryableVerifyError(error)) {
      lastVerificationPayload.value = null
    }
  } finally {
    verifyLoading.value = false
    checkoutLoadingCode.value = ''
    await loadSubscription().catch(() => {})
  }
}

async function retryLastVerification() {
  if (!lastVerificationPayload.value || verifyLoading.value || isAnyCheckoutBusy.value) return
  await verifyPaymentRequest(lastVerificationPayload.value)
}

async function loadPlans() {
  try {
    const res = await API.get('/billing/plan-quotes')
    const data = res.data || {}
    quoteContext.value = {
      seats_billed: Number(data?.seats_billed || 0),
      is_first_paid_subscription: Boolean(data?.is_first_paid_subscription),
      expected_start_date: data?.expected_start_date || null,
    }
    const quotes = Array.isArray(data?.quotes) ? data.quotes : []
    plans.value = quotes
      .map((quote) => ({
        ...(quote?.plan || {}),
        quote,
      }))
      .filter((plan) => Boolean(plan.code))
    return
  } catch (error) {
    const fallbackRes = await API.get('/billing/plans')
    plans.value = Array.isArray(fallbackRes.data) ? fallbackRes.data : []
    quoteContext.value = {
      seats_billed: Number(subscription.value?.library?.max_seats || 0),
      is_first_paid_subscription: false,
      expected_start_date: null,
    }
  }
}

async function loadSubscription() {
  const res = await API.get('/billing/me')
  subscription.value = res.data || null
}

async function refreshAll() {
  isPageLoading.value = true
  pageError.value = ''
  try {
    await Promise.all([loadPlans(), loadSubscription()])
  } catch (error) {
    pageError.value = extractError(error, 'Failed to load billing data')
  } finally {
    isPageLoading.value = false
  }
}

function createIdempotencyKey() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return `idem_${Date.now()}_${Math.random().toString(16).slice(2)}`
}

function getPlanQuote(plan) {
  return plan?.quote || null
}

function seatsForPlan(plan) {
  const seats = Number(getPlanQuote(plan)?.seats_billed || seatsBilled.value || 0)
  return seats > 0 ? seats : 0
}

function bonusMonthsApplied(plan) {
  return Number(getPlanQuote(plan)?.bonus_months_applied || 0)
}

function coverageMonths(plan) {
  const coverage = Number(getPlanQuote(plan)?.coverage_months || plan?.billing_months || 0)
  return coverage > 0 ? coverage : 0
}

function payableNowPaise(plan) {
  const quoteAmount = Number(getPlanQuote(plan)?.payable_now_paise || 0)
  if (quoteAmount > 0) return quoteAmount

  const seats = Math.max(1, seatsForPlan(plan))
  return seats * Number(plan?.price_per_seat_paise || 0) * Number(plan?.billing_months || 1)
}

function effectiveMonthlyTotalPaise(plan) {
  const coverage = Math.max(1, coverageMonths(plan))
  return payableNowPaise(plan) / coverage
}

function effectiveMonthlyPerSeatPaise(plan) {
  const seats = Math.max(1, seatsForPlan(plan))
  return effectiveMonthlyTotalPaise(plan) / seats
}

function periodWindowText(plan) {
  const quote = getPlanQuote(plan)
  const start = formatDate(quote?.expected_period_start || quoteContext.value?.expected_start_date)
  const end = formatDate(quote?.expected_period_end)

  if (start === '—' && end === '—') return '—'
  if (end === '—') return start
  if (start === '—') return `Ends ${end}`
  return `${start} to ${end}`
}

function ensureRazorpayScript() {
  if (window.Razorpay) {
    return Promise.resolve()
  }

  if (window.__razorpayScriptPromise) {
    return window.__razorpayScriptPromise
  }

  window.__razorpayScriptPromise = new Promise((resolve, reject) => {
    const existing = document.getElementById('razorpay-checkout-script')
    if (existing) {
      existing.addEventListener('load', () => resolve(), { once: true })
      existing.addEventListener(
        'error',
        () => {
          window.__razorpayScriptPromise = null
          reject(new Error('Failed to load Razorpay script'))
        },
        { once: true }
      )
      return
    }

    const script = document.createElement('script')
    script.id = 'razorpay-checkout-script'
    script.src = 'https://checkout.razorpay.com/v1/checkout.js'
    script.async = true
    script.onload = () => resolve()
    script.onerror = () => {
      window.__razorpayScriptPromise = null
      reject(new Error('Failed to load Razorpay script'))
    }
    document.body.appendChild(script)
  })

  return window.__razorpayScriptPromise
}

async function startCheckout(plan) {
  if (!plan || isAnyCheckoutBusy.value || verifyLoading.value) return

  checkoutLoadingCode.value = plan.code
  messageText.value = ''
  lastVerificationPayload.value = null

  try {
    await ensureRazorpayScript()

    const idempotencyKey = createIdempotencyKey()
    const orderRes = await API.post('/billing/checkout-order', {
      plan_code: plan.code,
      idempotency_key: idempotencyKey,
    })
    const order = orderRes.data
    const expectedAmount = Math.round(payableNowPaise(plan))
    if (expectedAmount > 0 && Number(order.amount_paise || 0) !== expectedAmount) {
      throw new Error('Plan pricing changed on server. Please refresh and try again.')
    }

    if (!window.Razorpay) {
      throw new Error('Razorpay SDK unavailable')
    }

    const razorpay = new window.Razorpay({
      key: order.key_id,
      amount: order.amount_paise,
      currency: order.currency,
      name: 'Smart Library App',
      description: `${plan.name} subscription`,
      order_id: order.order_id,
      prefill: {
        name: localStorage.getItem('username') || '',
      },
      theme: {
        color: '#0ea5e9',
      },
      modal: {
        ondismiss: () => {
          if (!verifyLoading.value) {
            checkoutLoadingCode.value = ''
          }
        },
      },
      handler: async (response) => {
        const verifyPayload = {
          razorpay_order_id: response.razorpay_order_id,
          razorpay_payment_id: response.razorpay_payment_id,
          razorpay_signature: response.razorpay_signature,
        }
        lastVerificationPayload.value = verifyPayload
        await verifyPaymentRequest(verifyPayload)
      },
    })

    razorpay.on('payment.failed', (response) => {
      const reason = response?.error?.description || response?.error?.reason || 'Payment failed'
      messageType.value = 'error'
      messageText.value = reason
      checkoutLoadingCode.value = ''
      verifyLoading.value = false
    })

    razorpay.open()
  } catch (error) {
    messageType.value = 'error'
    messageText.value = extractError(error, 'Unable to start checkout')
    checkoutLoadingCode.value = ''
    verifyLoading.value = false
  }
}

onMounted(async () => {
  await refreshAll()
})
</script>

<style scoped>
.billing-page {
  position: relative;
  min-height: 100vh;
  padding: 2rem 2rem 2.8rem;
  color: #e2e8f0;
  isolation: isolate;
  overflow: hidden;
}

.mesh-layer {
  position: absolute;
  inset: 0;
  z-index: -1;
  background:
    radial-gradient(46rem 24rem at 8% 16%, rgba(34, 211, 238, 0.14), transparent 70%),
    radial-gradient(42rem 24rem at 88% 8%, rgba(59, 130, 246, 0.14), transparent 68%),
    radial-gradient(38rem 22rem at 64% 88%, rgba(14, 165, 233, 0.1), transparent 70%),
    linear-gradient(180deg, #0f172a 0%, #0b1222 100%);
  filter: saturate(115%);
  animation: mesh-drift 18s ease-in-out infinite alternate;
}

.section-shell {
  width: min(1140px, calc(100% - 2rem));
  margin: 0 auto;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
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

.hero h1 {
  margin: 0.9rem 0 0;
  font-size: clamp(1.9rem, 4.4vw, 3rem);
  line-height: 1.05;
  letter-spacing: -0.03em;
}

.gradient-text {
  background: linear-gradient(90deg, #22d3ee, #3b82f6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-subtitle {
  margin: 0.75rem 0 0;
  color: #94a3b8;
  line-height: 1.6;
  max-width: 60ch;
}

.btn {
  border-radius: 12px;
  border: 1px solid transparent;
  padding: 0.62rem 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn:disabled {
  opacity: 0.68;
  cursor: not-allowed;
}

.btn-ghost {
  border-color: rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.5);
  color: #e2e8f0;
}

.btn-ghost:hover:not(:disabled) {
  border-color: rgba(14, 165, 233, 0.6);
  transform: translateY(-1px);
}

.glass-card {
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(148, 163, 184, 0.03);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 18px;
}

.status-grid {
  margin-top: 1.1rem;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.8rem;
}

.status-card,
.info-card {
  padding: 1rem;
}

.label {
  margin: 0;
  color: #94a3b8;
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.status-card header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0.28rem 0.65rem;
  font-size: 0.78rem;
  font-weight: 700;
}

.status-active {
  background: rgba(34, 197, 94, 0.2);
  color: #86efac;
}

.status-trial {
  background: rgba(14, 165, 233, 0.2);
  color: #67e8f9;
}

.status-grace {
  background: rgba(245, 158, 11, 0.18);
  color: #fcd34d;
}

.status-risk,
.status-expired,
.status-inactive {
  background: rgba(248, 113, 113, 0.16);
  color: #fca5a5;
}

.status-details {
  margin-top: 0.9rem;
  display: grid;
  gap: 0.58rem;
}

.status-details p {
  margin: 0;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  color: #cbd5e1;
}

.status-details p span {
  color: #94a3b8;
}

.info-card ul {
  margin: 0.8rem 0 0;
  padding-left: 1rem;
  display: grid;
  gap: 0.45rem;
  color: #cbd5e1;
  line-height: 1.5;
}

.message-banner {
  margin-top: 0.85rem;
  border-radius: 12px;
  padding: 0.72rem 0.95rem;
  display: flex;
  align-items: center;
  gap: 0.55rem;
  border: 1px solid transparent;
}

.message-text {
  flex: 1;
}

.btn-mini {
  padding: 0.42rem 0.7rem;
  font-size: 0.8rem;
  display: inline-flex;
  align-items: center;
  gap: 0.38rem;
}

.message-success {
  background: rgba(22, 163, 74, 0.16);
  border-color: rgba(34, 197, 94, 0.35);
  color: #86efac;
}

.message-error {
  background: rgba(239, 68, 68, 0.16);
  border-color: rgba(248, 113, 113, 0.35);
  color: #fecaca;
}

.message-icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

.plans-shell {
  margin-top: 0.95rem;
  padding: 1rem;
}

.plans-header h2 {
  margin: 0;
  font-size: 1.2rem;
}

.plans-header p {
  margin: 0.35rem 0 0;
  color: #94a3b8;
}

.state-text {
  margin-top: 0.9rem;
  color: #cbd5e1;
}

.state-text.error {
  color: #fca5a5;
}

.plans-grid {
  margin-top: 0.9rem;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.plan-card {
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(15, 23, 42, 0.45);
  padding: 0.95rem;
  display: grid;
  gap: 0.8rem;
}

.plan-card.current {
  border-color: rgba(14, 165, 233, 0.62);
  box-shadow: 0 0 0 1px rgba(14, 165, 233, 0.2) inset;
}

.plan-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.6rem;
}

.plan-head h3 {
  margin: 0;
  font-size: 1.02rem;
}

.plan-head p {
  margin: 0.34rem 0 0;
  color: #94a3b8;
  font-size: 0.9rem;
  line-height: 1.45;
}

.current-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0.22rem 0.55rem;
  font-size: 0.72rem;
  font-weight: 700;
  color: #67e8f9;
  background: rgba(14, 165, 233, 0.22);
}

.plan-price {
  display: grid;
  gap: 0.15rem;
}

.price-value {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.price-note {
  margin: 0;
  color: #94a3b8;
  font-size: 0.85rem;
}

.pay-now {
  margin: 0.2rem 0 0;
  color: #c7f9ff;
  font-size: 0.88rem;
  font-weight: 600;
}

.plan-metrics {
  display: grid;
  gap: 0.42rem;
}

.plan-metrics p {
  margin: 0;
  display: flex;
  justify-content: space-between;
  gap: 0.8rem;
  color: #cbd5e1;
  font-size: 0.9rem;
}

.plan-metrics p span {
  color: #94a3b8;
}

.btn-solid {
  background: linear-gradient(120deg, #06b6d4, #2563eb);
  color: #fff;
}

.btn-solid:hover:not(:disabled) {
  filter: brightness(1.06);
  transform: translateY(-1px);
}

.btn.full {
  width: 100%;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  gap: 0.45rem;
}

.btn-spin {
  width: 1rem;
  height: 1rem;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes mesh-drift {
  0% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  100% {
    transform: translate3d(-1.5%, 1.2%, 0) scale(1.04);
  }
}

@media (max-width: 1080px) {
  .billing-page {
    padding: 1.35rem 1rem 2rem;
  }

  .section-shell {
    width: min(1140px, 100%);
  }

  .plans-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .status-grid {
    grid-template-columns: 1fr;
  }

  .plans-grid {
    grid-template-columns: 1fr;
  }
}
</style>
