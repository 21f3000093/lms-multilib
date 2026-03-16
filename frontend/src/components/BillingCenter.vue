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
            <strong style="text-align: end;">{{ currentPeriodText }}</strong>
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
    
      <div v-else class="pricing-carousel-wrapper">
        <swiper
          :modules="swiperModules"
          :slides-per-view="'auto'"
          :centered-slides="true"
          :space-between="20"
          :initial-slide="1" 
          :pagination="{ clickable: true }"
          :navigation="true"
          :grab-cursor="true"
          class="pricing-swiper"
          @swiper="onBillingSwiperInit"
          @slideChange="onBillingSwiperChange"
        >
          <swiper-slide v-for="(plan, index) in plans" :key="plan.code" class="pricing-slide">
            <article
              class="plan-card"
              :class="{ current: isCurrentPlan(plan), 'is-focused': isPlanFocused(index) }"
              @click="focusPlan(index)"
            >
              <div class="card-glow"></div>

              <div class="plan-head">
                <div>
                  <h3>{{ plan.name }}</h3>
                  <p>{{ plan.description || 'Subscription plan' }}</p>
                </div>
                <div class="head-tags">
                  <span v-if="discountPercent(plan) > 0" class="discount-pill">
                    {{ discountPercent(plan) }}% OFF
                  </span>
                  <span v-if="isCurrentPlan(plan)" class="current-pill">Current</span>
                </div>
              </div>

              <div class="plan-price">
                <p class="price-value">₹{{ formatPaise(plan.price_per_seat_paise) }}</p>
                <p class="price-note">per seat / month (base rate)</p>
                <p class="pay-now">Pay now: ₹{{ formatPaise(payableNowPaise(plan)) }}</p>
                <div v-if="discountPercent(plan) > 0" class="savings-badge">
                  <span>{{ discountPercent(plan) }}% OFF</span>
                  <span>Discount on monthly seat rate</span>
                </div>
              </div>

              <div class="plan-metrics">
                <p>
                  <span>Billing cycle</span>
                  <strong>{{ plan.billing_months }} month{{ plan.billing_months > 1 ? 's' : '' }}</strong>
                </p>
                <p>
                  <span>Discount</span>
                  <strong>{{ discountPercent(plan) }}%</strong>
                </p>
                <p>
                  <span>Seats billed</span>
                  <strong>{{ seatsForPlan(plan) }}</strong>
                </p>
                <p>
                  <span>Bonus applied</span>
                  <strong>{{ bonusMonthsApplied(plan) }}</strong>
                </p>
                <p>
                  <span>Coverage</span>
                  <strong>{{ coverageMonths(plan) }} months</strong>
                </p>
                <p>
                  <span>Effective monthly</span>
                  <strong>₹{{ formatPaise(effectiveMonthlyTotalPaise(plan)) }}</strong>
                </p>
                <p>
                  <span>Effective per seat</span>
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
                @click.stop="startCheckout(plan, index)"
              >
                <LoaderCircle
                  v-if="checkoutLoadingCode === plan.code || verifyLoading"
                  class="btn-spin"
                  aria-hidden="true"
                />
                <span>
                  {{
                    checkoutLoadingCode === plan.code
                      ? 'Creating order...'
                      : verifyLoading
                        ? 'Verifying payment...'
                        : isPlanFocused(index)
                          ? checkoutLabel(plan)
                          : 'Tap to focus'
                  }}
                </span>
              </button>
            </article>
          </swiper-slide>
        </swiper>
      </div>
    </section>

    <section class="section-shell history-shell glass-card">
      <header class="history-header">
        <h2>Recent Transactions</h2>
        <p>Your latest subscription payments and attempts.</p>
      </header>

      <div v-if="transactionsLoading" class="state-text">Loading transactions...</div>
      <div v-else-if="transactionsError" class="state-text error">{{ transactionsError }}</div>
      <div v-else-if="!transactions.length" class="state-text">No subscription transactions yet.</div>

      <template v-else>
        <div class="history-table-wrap">
          <table class="history-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Plan</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Period</th>
                <th>Paid At</th>
                <th>Gateway Ref</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="tx in transactions" :key="tx.id">
                <td>#{{ tx.id }}</td>
                <td>{{ transactionPlanName(tx) }}</td>
                <td>₹{{ formatPaise(tx.amount_paise) }}</td>
                <td>
                  <span class="tx-pill" :class="transactionStatusClass(tx.status)">
                    {{ transactionStatusLabel(tx.status) }}
                  </span>
                </td>
                <td>{{ transactionPeriodText(tx) }}</td>
                <td>{{ formatDateTime(tx.paid_at || tx.created_at) }}</td>
                <td class="gateway-ref">
                  {{ tx.gateway_payment_id || tx.gateway_order_id || '—' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="history-actions" v-if="transactionsHasMore">
          <button
            type="button"
            class="btn btn-ghost btn-mini"
            :disabled="transactionsLoadingMore"
            @click="loadMoreTransactions"
          >
            <LoaderCircle v-if="transactionsLoadingMore" class="btn-spin" aria-hidden="true" />
            <span>{{ transactionsLoadingMore ? 'Loading...' : 'Load More' }}</span>
          </button>
        </div>
      </template>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { AlertTriangle, CheckCircle2, LoaderCircle } from 'lucide-vue-next'
// --- SWIPER IMPORTS ---
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Pagination, Navigation } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/pagination'
import 'swiper/css/navigation'
import API from '../api'

const swiperModules = [Pagination, Navigation]
const initialPlanSlideIndex = 1
const billingSwiper = ref(null)
const activePlanSlideIndex = ref(initialPlanSlideIndex)
const plans = ref([])
const subscription = ref(null)
const quoteContext = ref({
  seats_billed: 0,
  is_first_paid_subscription: false,
  expected_start_date: null,
})
const transactions = ref([])
const transactionLimit = 10
const transactionOffset = ref(0)
const transactionsHasMore = ref(false)
const transactionsLoading = ref(false)
const transactionsLoadingMore = ref(false)
const transactionsError = ref('')
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

const planNameById = computed(() => {
  const map = {}
  for (const plan of plans.value) {
    const planId = Number(plan?.id || 0)
    if (planId > 0 && typeof plan?.name === 'string' && plan.name.trim()) {
      map[planId] = plan.name
    }
  }
  return map
})

function formatDate(value) {
  const dt = parseServerDate(value)
  if (Number.isNaN(dt.getTime())) return '—'
  return dt.toLocaleDateString('en-IN', {
    timeZone: 'Asia/Kolkata',
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  })
}

function formatDateTime(value) {
  const dt = parseServerDate(value)
  if (Number.isNaN(dt.getTime())) return '—'
  return dt.toLocaleString('en-IN', {
    timeZone: 'Asia/Kolkata',
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function parseServerDate(value) {
  if (!value) return new Date(NaN)
  if (value instanceof Date) return value

  const raw = String(value).trim()
  if (!raw) return new Date(NaN)

  // Date-only fields should stay calendar-accurate for India.
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
    return new Date(`${raw}T00:00:00+05:30`)
  }

  // If timezone isn't present, backend timestamps are treated as UTC.
  if (raw.includes('T') && !/(Z|[+-]\d{2}:\d{2})$/.test(raw)) {
    return new Date(`${raw}Z`)
  }

  return new Date(raw)
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

function boundedPlanIndex(index) {
  if (!plans.value.length) return -1
  const normalized = Number(index)
  if (!Number.isFinite(normalized)) return -1
  return Math.min(Math.max(0, normalized), plans.value.length - 1)
}

function syncActivePlanSlide(swiper) {
  const nextIndex = boundedPlanIndex(swiper?.activeIndex ?? 0)
  if (nextIndex >= 0) {
    activePlanSlideIndex.value = nextIndex
  }
}

function onBillingSwiperInit(swiper) {
  billingSwiper.value = swiper
  syncActivePlanSlide(swiper)
}

function onBillingSwiperChange(swiper) {
  syncActivePlanSlide(swiper)
}

function isPlanFocused(index) {
  return boundedPlanIndex(index) === activePlanSlideIndex.value
}

function focusPlan(index) {
  const targetIndex = boundedPlanIndex(index)
  if (targetIndex < 0) return
  if (!billingSwiper.value) {
    activePlanSlideIndex.value = targetIndex
    return
  }
  if (billingSwiper.value.activeIndex === targetIndex) return
  billingSwiper.value.slideTo(targetIndex)
}

function resetPlanFocus() {
  const targetIndex = boundedPlanIndex(initialPlanSlideIndex)
  if (targetIndex < 0) {
    activePlanSlideIndex.value = 0
    return
  }
  activePlanSlideIndex.value = targetIndex
  if (billingSwiper.value) {
    billingSwiper.value.slideTo(targetIndex, 0)
  }
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

function transactionStatusClass(status) {
  const normalized = String(status || '').trim().toLowerCase()
  if (normalized === 'captured') return 'tx-captured'
  if (normalized === 'created' || normalized === 'authorized') return 'tx-pending'
  if (normalized === 'failed') return 'tx-failed'
  if (normalized === 'refunded') return 'tx-refunded'
  return 'tx-default'
}

function transactionStatusLabel(status) {
  const normalized = String(status || '').trim().toLowerCase()
  if (!normalized) return 'Unknown'
  if (normalized === 'captured') return 'Successful'
  if (normalized === 'created') return 'Initiated'
  if (normalized === 'authorized') return 'Authorized'
  if (normalized === 'failed') return 'Failed'
  if (normalized === 'refunded') return 'Refunded'
  return 'Processing'
}

function transactionPlanName(tx) {
  const planId = Number(tx?.plan_id || 0)
  if (planId > 0 && planNameById.value[planId]) return planNameById.value[planId]
  if (planId > 0) return `Plan #${planId}`
  return '—'
}

function transactionPeriodText(tx) {
  const start = formatDate(tx?.period_start)
  const end = formatDate(tx?.period_end)
  if (start === '—' && end === '—') return '—'
  if (end === '—') return start
  if (start === '—') return `Ends ${end}`
  return `${start} to ${end}`
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
    await Promise.all([
      loadSubscription().catch(() => {}),
      loadTransactions().catch(() => {}),
    ])
  }
}

async function retryLastVerification() {
  if (!lastVerificationPayload.value || verifyLoading.value || isAnyCheckoutBusy.value) return
  await verifyPaymentRequest(lastVerificationPayload.value)
}

async function loadTransactions(options = {}) {
  const append = options.append === true
  const targetOffset = append ? transactionOffset.value : 0

  if (append) {
    transactionsLoadingMore.value = true
  } else {
    transactionsLoading.value = true
    transactionsError.value = ''
  }

  try {
    const res = await API.get('/billing/transactions', {
      params: {
        limit: transactionLimit,
        offset: targetOffset,
      },
    })
    const rows = Array.isArray(res.data) ? res.data : []

    if (append) {
      transactions.value = [...transactions.value, ...rows]
    } else {
      transactions.value = rows
    }

    transactionOffset.value = targetOffset + rows.length
    transactionsHasMore.value = rows.length === transactionLimit
  } catch (error) {
    if (append) {
      messageType.value = 'error'
      messageText.value = extractError(error, 'Failed to load more transactions')
    } else {
      transactionsError.value = extractError(error, 'Failed to load transactions')
      transactions.value = []
      transactionOffset.value = 0
      transactionsHasMore.value = false
    }
  } finally {
    if (append) {
      transactionsLoadingMore.value = false
    } else {
      transactionsLoading.value = false
    }
  }
}

async function loadMoreTransactions() {
  if (transactionsLoading.value || transactionsLoadingMore.value || !transactionsHasMore.value) return
  await loadTransactions({ append: true })
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
    resetPlanFocus()
    return
  } catch (error) {
    const fallbackRes = await API.get('/billing/plans')
    plans.value = Array.isArray(fallbackRes.data) ? fallbackRes.data : []
    resetPlanFocus()
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
    await Promise.all([loadPlans(), loadSubscription(), loadTransactions()])
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

function discountPercent(plan) {
  const discount = Number(getPlanQuote(plan)?.plan?.discount_percent || plan?.discount_percent || 0)
  return discount > 0 ? discount : 0
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

async function startCheckout(plan, index) {
  if (!plan || isAnyCheckoutBusy.value || verifyLoading.value) return
  if (!isPlanFocused(index)) {
    focusPlan(index)
    return
  }

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
  padding: 2rem 2rem 5rem;
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
  overflow-x: hidden;
  padding-top: 1rem;
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
  text-align: left;
}

.status-details p strong {
  text-align: end;
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
  /* padding: 1rem; */
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

.history-shell {
  margin-top: 0.95rem;
  /* padding: 1rem; */
}

.history-header h2 {
  margin: 0;
  font-size: 1.2rem;
}

.history-header p {
  margin: 0.35rem 0 0;
  color: #94a3b8;
}

.history-table-wrap {
  margin: 0.9rem;
  overflow-x: auto;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 14px;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 760px;
}

.history-table th,
.history-table td {
  text-align: left;
  padding: 0.62rem 0.72rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.16);
  vertical-align: middle;
}

.history-table thead th {
  color: #94a3b8;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: rgba(15, 23, 42, 0.65);
}

.history-table tbody td {
  color: #dbe7ff;
  font-size: 0.86rem;
}

.history-table tbody tr:last-child td {
  border-bottom: none;
}

.tx-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0.18rem 0.5rem;
  font-size: 0.72rem;
  font-weight: 700;
  border: 1px solid transparent;
}

.tx-captured {
  background: rgba(34, 197, 94, 0.2);
  color: #86efac;
  border-color: rgba(34, 197, 94, 0.35);
}

.tx-pending {
  background: rgba(14, 165, 233, 0.2);
  color: #67e8f9;
  border-color: rgba(14, 165, 233, 0.35);
}

.tx-failed {
  background: rgba(248, 113, 113, 0.16);
  color: #fca5a5;
  border-color: rgba(248, 113, 113, 0.35);
}

.tx-refunded,
.tx-default {
  background: rgba(148, 163, 184, 0.18);
  color: #cbd5e1;
  border-color: rgba(148, 163, 184, 0.3);
}

.gateway-ref {
  font-family: 'Roboto Mono', monospace;
  font-size: 0.8rem;
  color: #bfdbfe;
  word-break: break-all;
}

.history-actions {
  margin-top: 0.8rem;
  display: flex;
  justify-content: center;
}

/* 
.plans-grid {
  margin-top: 0.9rem;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
} */

/* .plan-card {
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
} */

/* --- SWIPER CAROUSEL STYLES --- */
.pricing-carousel-wrapper {
  width: 100vw;
  position: relative;
  left: 50%;
  right: 50%;
  margin-left: -50vw;
  margin-right: -50vw;
  padding: 1rem 0 3rem 0; 
}

.pricing-swiper {
  width: 100%;
  padding-bottom: 3rem !important; 
  overflow: visible; 
}

.pricing-slide {
  width: 320px; 
  height: auto;
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s ease;
  opacity: 0.5;
  transform: scale(0.85) translateY(10px); 
}

.swiper-slide-active {
  opacity: 1;
  transform: scale(1) translateY(0);
  z-index: 10;
}

.pricing-slide .plan-card {
  height: 100%;
  margin: 0; 
}

/* --- UPGRADED PLAN CARD STYLES --- */
.plan-card {
  position: relative;
  overflow: hidden;
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 1.25rem;
  display: grid;
  gap: 1rem;
  cursor: pointer;
  transition: transform 240ms ease, box-shadow 240ms ease, border-color 240ms ease;
}

.plan-card.is-focused {
  cursor: default;
}

.plan-card .card-glow {
  position: absolute;
  inset: -40% auto auto -20%;
  width: 13rem;
  height: 13rem;
  background: radial-gradient(circle, rgba(34, 211, 238, 0.2), transparent 70%);
  opacity: 0;
  transition: opacity 260ms ease;
  pointer-events: none;
  z-index: 0;
}

.plan-card:hover {
  transform: translateY(-4px);
  border-color: rgba(34, 211, 238, 0.32);
  box-shadow: 0 20px 34px rgba(2, 6, 23, 0.42);
}

.plan-card:hover .card-glow {
  opacity: 1;
}

.plan-card > * {
  position: relative;
  z-index: 1;
}

.plan-card.current {
  border-color: rgba(14, 165, 233, 0.62);
  box-shadow: 0 0 0 1px rgba(14, 165, 233, 0.2) inset;
}

/* --- SWIPER PAGINATION & NAVIGATION --- */
:deep(.swiper-pagination-bullet) {
  background: #94a3b8;
  opacity: 0.4;
  width: 8px;
  height: 8px;
  transition: all 0.3s ease;
}

:deep(.swiper-pagination-bullet-active) {
  background: #22d3ee;
  opacity: 1;
  width: 24px; 
  border-radius: 4px;
}

:deep(.swiper-button-next),
:deep(.swiper-button-prev) {
  color: #22d3ee; 
  background: rgba(15, 23, 42, 0.75); 
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 1px solid rgba(148, 163, 184, 0.24);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  transition: all 0.3s ease;
}

:deep(.swiper-button-next:hover),
:deep(.swiper-button-prev:hover) {
  background: rgba(15, 23, 42, 0.95);
  border-color: #22d3ee;
  transform: scale(1.05);
}

:deep(.swiper-button-next svg),
:deep(.swiper-button-prev svg) {
  width: 20%;
  stroke-width: 2.5;
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

.head-tags {
  display: inline-flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.4rem;
}

.discount-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0.22rem 0.55rem;
  font-size: 0.72rem;
  font-weight: 700;
  color: #fef08a;
  background: rgba(234, 179, 8, 0.2);
  border: 1px solid rgba(234, 179, 8, 0.35);
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

.savings-badge {
  margin-top: 0.5rem;
  display: inline-flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.14rem;
  border-radius: 12px;
  padding: 0.4rem 0.55rem;
  border: 1px solid rgba(234, 179, 8, 0.35);
  background: rgba(234, 179, 8, 0.13);
}

.savings-badge span:first-child {
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #fde68a;
}

.savings-badge span:last-child {
  font-size: 0.74rem;
  color: #fef3c7;
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
  text-align: left;
}

.plan-metrics p strong {
  /* color: #67e8f9; */
  text-align: end;
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

@media (min-width: 1080px) {
  :deep(.swiper-button-prev) { left: calc(50% - 380px); }
  :deep(.swiper-button-next) { right: calc(50% - 380px); }
}

@media (min-width: 768px) and (max-width: 1079px) {
  :deep(.swiper-button-prev) { left: 5vw; }
  :deep(.swiper-button-next) { right: 5vw; }
}

@media (max-width: 1080px) {
  .billing-page {
    padding: 1.35rem 1rem 5rem;
  }
  .section-shell {
    /* width: min(1140px, 100%); */
    overflow-x: visible;
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

  :deep(.swiper-button-prev) { left: 1rem; }
  :deep(.swiper-button-next) { right: 1rem; }
}
</style>
