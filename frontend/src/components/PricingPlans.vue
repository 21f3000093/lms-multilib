<template>
  <main class="pricing-page" ref="pageRoot">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="hero section-shell">
      <div class="hero-copy reveal" data-stagger="0">
        <p class="kicker">Plans Built For Growing Libraries</p>
        <h1>
          Predictable pricing for every
          <span class="gradient-text">seat you manage</span>
        </h1>
        <p class="hero-subtitle">
          Start small and scale confidently. Choose a plan that matches your seat capacity and operational goals.
        </p>

        <div class="hero-points">
          <div class="point-chip">
            <ShieldCheck class="point-icon" aria-hidden="true" />
            No setup fee
          </div>
          <div class="point-chip">
            <Sparkles class="point-icon" aria-hidden="true" />
            First-time bonus months
          </div>
          <div class="point-chip">
            <BadgeCheck class="point-icon" aria-hidden="true" />
            Full feature access
          </div>
        </div>
      </div>

      <div class="hero-visual reveal" data-stagger="1">
        <div class="hero-orb floaty">
          <div class="orb-core">
            <IndianRupee class="orb-icon" aria-hidden="true" />
          </div>
        </div>
      </div>
    </section>

    <section class="calculator section-shell reveal" data-stagger="1">
      <div class="calculator-card">
        <header>
          <h2>Seat Cost Calculator</h2>
          <p>Estimate your monthly cost instantly before selecting a plan.</p>
        </header>

        <label for="seat-input">Number of Seats</label>
        <input
          id="seat-input"
          v-model.number="seatCount"
          type="number"
          min="1"
          max="300"
          placeholder="e.g. 100"
          @input="validateInput"
          @blur="validateInput"
        />

        <div class="preset-buttons">
          <button
            v-for="preset in presetSeats"
            :key="preset"
            class="preset-btn"
            :class="{ active: seatCount === preset }"
            @click="seatCount = preset"
          >
            {{ preset }}
          </button>
        </div>

        <div class="calculator-summary">
          <article class="summary-item">
            <p>Estimated monthly</p>
            <strong>₹{{ formatCurrency(baseMonthlyCost) }}</strong>
          </article>
          <article class="summary-item">
            <p>Yearly at monthly rate</p>
            <strong>₹{{ formatCurrency(baseMonthlyCost * 12) }}</strong>
          </article>
          <article class="summary-item">
            <p>Lowest monthly equivalent</p>
            <strong>₹{{ formatCurrency(lowestEquivalentMonthly) }}</strong>
          </article>
        </div>
      </div>
    </section>

    <section class="pricing section-shell">
      <header class="section-header reveal" data-stagger="0">
        <h2>Choose your billing cycle</h2>
        <p>Longer commitments reduce cost per seat and unlock additional free months.</p>
      </header>

      

      <div class="pricing-carousel-wrapper">
        <swiper
          :modules="swiperModules"
          :slides-per-view="'auto'"
          :centered-slides="true"
          :slide-to-clicked-slide="true"
          :space-between="20"
          :initial-slide="initialPlanSlideIndex" 
          :pagination="{ clickable: true }"
          :navigation="true"
          :grab-cursor="true"
          class="pricing-swiper"
          @swiper="onPricingSwiperInit"
          @slideChange="onPricingSwiperChange"
        >
        
          <swiper-slide v-for="(plan, index) in plans" :key="plan.name" class="pricing-slide">
            
            <article
              class="pricing-card"
              :class="{ featured: plan.featured, 'best-value': plan.bestValue, 'is-focused': isPlanFocused(index) }"
              @click="focusPlan(index)"
            >
              <div v-if="plan.badge" class="plan-badge" :class="plan.badgeTone">{{ plan.badge }}</div>

              <div class="card-header">
                <div class="plan-icon-wrap">
                  <component :is="plan.icon" class="plan-icon" aria-hidden="true" />
                </div>
                <h3>{{ plan.name }}</h3>
                <p>{{ plan.description }}</p>
              </div>

              <div class="price-box">
                <div class="price-main">
                  <span class="currency">₹</span>
                  <span class="amount">{{ plan.price.toFixed(2) }}</span>
                  <span class="unit">/seat per month</span>
                </div>
                <p class="billing-note">{{ plan.duration }}</p>

                <div v-if="plan.discount" class="savings-badge">
                  <span>{{ plan.discount }}% OFF</span>
                  <span>Save ₹{{ formatCurrency(calculateSavings(plan)) }}</span>
                </div>
              </div>

              <ul class="feature-list">
                <li v-for="feature in plan.features" :key="feature">
                  <Check class="check-icon" aria-hidden="true" />
                  <span>{{ feature }}</span>
                </li>
              </ul>

              <div class="total-box">
                <div class="total-row">
                  <span>Total billed</span>
                  <strong>₹{{ formatCurrency(calculateTotal(plan)) }}</strong>
                </div>

                <div v-if="plan.extraMonth" class="bonus-row">
                  <Gift class="bonus-icon" aria-hidden="true" />
                  <div>
                    <strong>+{{ plan.extraMonth }} free month{{ plan.extraMonth > 1 ? 's' : '' }}</strong>
                    <p>For first-time purchase</p>
                  </div>
                </div>

                <p class="effective-note">
                  Effective: ₹{{ effectivePerSeat(plan) }}/seat/mo
                  <span>across {{ plan.multiplier + (plan.extraMonth || 0) }} months</span>
                </p>
              </div>
            </article>

          </swiper-slide>
        </swiper>
      </div>

      <div class="pricing-actions reveal" data-stagger="1">
        <router-link class="btn btn-solid" to="/signup">Start Free Trial</router-link>
      </div>

    </section>

    <section class="included section-shell reveal" data-stagger="1">
      <h2>Included in every plan</h2>
      <div class="included-grid">
        <article v-for="item in includedFeatures" :key="item.label" class="included-card reveal" :data-stagger="item.stagger">
          <component :is="item.icon" class="included-icon" aria-hidden="true" />
          <p>{{ item.label }}</p>
        </article>
      </div>
    </section>

    <section class="faq section-shell reveal" data-stagger="1">
      <h2>FAQ</h2>
      <div class="faq-grid">
        <article v-for="item in faqs" :key="item.question" class="faq-card reveal" :data-stagger="item.stagger">
          <h3>{{ item.question }}</h3>
          <p>{{ item.answer }}</p>
        </article>
      </div>
    </section>

    <section class="cta section-shell reveal" data-stagger="1">
      <div class="cta-card">
        <p class="cta-kicker">Need custom enterprise support?</p>
        <h2>Talk to us about a tailored plan for your library network.</h2>
        <p>
          We can help with migration, onboarding, and long-term pricing strategy for multi-branch operations.
        </p>

        <div class="cta-actions">
          <router-link class="btn btn-solid magnetic" to="/signup" @mousemove="onMagneticMove" @mouseleave="onMagneticLeave">
            Create Library Account
          </router-link>
          <a class="btn btn-solid magnetic" href="mailto:shubham.libraryapp@gmail.com" @mousemove="onMagneticMove" @mouseleave="onMagneticLeave">
            Contact Sales
          </a>
          <a class="btn btn-ghost magnetic" href="tel:+919024600138" @mousemove="onMagneticMove" @mouseleave="onMagneticLeave">
            Schedule Call
          </a>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
/* eslint-disable */
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Pagination, Navigation, EffectCreative } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/pagination'
import 'swiper/css/navigation'
import 'swiper/css/effect-creative'
import {
  BadgeCheck,
  BarChart3,
  Calendar,
  Check,
  CreditCard,
  Crown,
  Gem,
  Gift,
  IndianRupee,
  LifeBuoy,
  MessageSquare,
  Rocket,
  ShieldCheck,
  Sparkles,
  TrendingUp,
  Users,
  Armchair,
} from 'lucide-vue-next'

const pageRoot = ref(null)
let observer = null

const swiperModules = [Pagination, Navigation]
const initialPlanSlideIndex = 2
const pricingSwiper = ref(null)
const activePlanSlideIndex = ref(initialPlanSlideIndex)

const seatCount = ref(100)
const presetSeats = [35, 50, 70, 100, 120]
const baseSeatPrice = 9

const plans = [
  {
    name: 'Monthly Pack',
    description: 'Ideal for testing and flexible monthly billing.',
    price: 9,
    duration: 'Billed every month',
    multiplier: 1,
    extraMonth: 1,
    discount: 0,
    icon: Calendar,
    badge: null,
    badgeTone: '',
    featured: false,
    bestValue: false,
    features: ['Full feature access', 'Email support', 'Flexible seat updates'],
  },
  {
    name: '3-Month Pack',
    description: 'Quarterly billing with immediate savings.',
    price: 8.55,
    duration: 'Billed quarterly',
    multiplier: 3,
    extraMonth: 1,
    discount: 5,
    icon: TrendingUp,
    badge: '5% OFF',
    badgeTone: 'tone-cyan',
    featured: false,
    bestValue: false,
    features: ['Save 5% vs monthly', 'Priority support', 'Faster onboarding'],
  },
  {
    name: '6-Month Pack',
    description: 'Balanced pricing for growing libraries.',
    price: 8.1,
    duration: 'Billed half-yearly',
    multiplier: 6,
    extraMonth: 1,
    discount: 10,
    icon: Rocket,
    badge: 'MOST POPULAR',
    badgeTone: 'tone-blue',
    featured: true,
    bestValue: false,
    features: ['Save 10% vs monthly', 'Dedicated support', 'Growth-ready pricing'],
  },
  {
    name: '12-Month Pack',
    description: 'Best annual value with stronger savings.',
    price: 7.65,
    duration: 'Billed yearly',
    multiplier: 12,
    extraMonth: 2,
    discount: 15,
    icon: Crown,
    badge: 'BEST VALUE',
    badgeTone: 'tone-amber',
    featured: false,
    bestValue: true,
    features: ['Save 15% vs monthly', 'Dedicated support', 'Long-term cost stability'],
  },
  {
    name: '24-Month Pack',
    description: 'Lowest per-seat rate for long-term operators.',
    price: 7.2,
    duration: 'Billed every 24 months',
    multiplier: 24,
    extraMonth: 4,
    discount: 20,
    icon: Gem,
    badge: 'MAX SAVINGS',
    badgeTone: 'tone-emerald',
    featured: false,
    bestValue: false,
    features: ['Save 20% vs monthly', 'Custom support pathway', 'Long-horizon predictability'],
  },
]

const includedFeatures = [
  { icon: Users, label: 'Student Management', stagger: 1 },
  { icon: Armchair, label: 'Seat Allocation', stagger: 2 },
  { icon: CreditCard, label: 'Fee Tracking', stagger: 3 },
  { icon: MessageSquare, label: 'WhatsApp Alerts', stagger: 4 },
  { icon: BarChart3, label: 'Analytics & Reports', stagger: 5 },
  { icon: LifeBuoy, label: 'Support Assistance', stagger: 6 },
]

const faqs = [
  {
    question: 'Can I change plans later?',
    answer: 'Yes. You can upgrade your billing cycle anytime and move to a higher savings tier.',
    stagger: 1,
  },
  {
    question: 'Do you charge any setup fee?',
    answer: 'No setup fee. Our onboarding support helps you configure your account without extra charges.',
    stagger: 2,
  },
  {
    question: 'How are free months applied?',
    answer: 'Bonus months are applied on first-time purchase of eligible long-duration plans.',
    stagger: 3,
  },
]

const baseMonthlyCost = computed(() => seatCount.value * baseSeatPrice)

const lowestEquivalentMonthly = computed(() => {
  const lowestPlan = plans.reduce((best, current) => {
    const bestRate = getEffectivePerSeat(best)
    const currentRate = getEffectivePerSeat(current)
    return currentRate < bestRate ? current : best
  }, plans[0])

  return seatCount.value * getEffectivePerSeat(lowestPlan)
})

function validateInput() {
  const numeric = Number(seatCount.value)
  if (Number.isNaN(numeric)) {
    seatCount.value = 1
    return
  }

  if (numeric < 1) {
    seatCount.value = 1
    return
  }

  if (numeric > 300) {
    seatCount.value = 300
  }
}

function calculateTotal(plan) {
  return seatCount.value * plan.price * plan.multiplier
}

function calculateSavings(plan) {
  const monthlyTotal = seatCount.value * baseSeatPrice * plan.multiplier
  return monthlyTotal - calculateTotal(plan)
}

function getEffectivePerSeat(plan) {
  const months = plan.multiplier + (plan.extraMonth || 0)
  return (plan.price * plan.multiplier) / months
}

function effectivePerSeat(plan) {
  return getEffectivePerSeat(plan).toFixed(2)
}

function formatCurrency(value) {
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(Math.round(value))
}

function boundedPlanIndex(index) {
  if (!plans.length) return -1
  const normalized = Number(index)
  if (!Number.isFinite(normalized)) return -1
  return Math.min(Math.max(0, normalized), plans.length - 1)
}

function getPricingSwiper() {
  const swiper = pricingSwiper.value
  if (!swiper || swiper.destroyed || !swiper.el?.isConnected) {
    pricingSwiper.value = null
    return null
  }
  return swiper
}

function syncActivePlanSlide(swiper) {
  const nextIndex = boundedPlanIndex(swiper?.activeIndex ?? initialPlanSlideIndex)
  if (nextIndex >= 0) {
    activePlanSlideIndex.value = nextIndex
  }
}

function onPricingSwiperInit(swiper) {
  pricingSwiper.value = swiper?.destroyed ? null : swiper
  syncActivePlanSlide(swiper)
}

function onPricingSwiperChange(swiper) {
  syncActivePlanSlide(swiper)
}

function isPlanFocused(index) {
  return boundedPlanIndex(index) === activePlanSlideIndex.value
}

function focusPlan(index) {
  const targetIndex = boundedPlanIndex(index)
  if (targetIndex < 0) return
  const swiper = getPricingSwiper()
  if (!swiper) {
    activePlanSlideIndex.value = targetIndex
    return
  }
  if (swiper.activeIndex === targetIndex) return
  swiper.slideTo(targetIndex)
}

const onMagneticMove = (event) => {
  const element = event.currentTarget
  const bounds = element.getBoundingClientRect()
  const x = event.clientX - bounds.left
  const y = event.clientY - bounds.top
  const centerX = bounds.width / 2
  const centerY = bounds.height / 2
  const dx = (x - centerX) * 0.08
  const dy = (y - centerY) * 0.12

  element.style.setProperty('--mx', `${x}px`)
  element.style.setProperty('--my', `${y}px`)
  element.style.transform = `translate(${dx}px, ${dy}px)`
}

const onMagneticLeave = (event) => {
  event.currentTarget.style.transform = 'translate(0, 0)'
}

onMounted(() => {
  const targets = pageRoot.value?.querySelectorAll('.reveal') || []

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return
        }

        const stagger = Number(entry.target.dataset.stagger || 0)
        entry.target.style.transitionDelay = `${Math.min(stagger * 80, 420)}ms`
        entry.target.classList.add('is-visible')
        observer?.unobserve(entry.target)
      })
    },
    {
      threshold: 0.16,
      rootMargin: '0px 0px -10% 0px',
    }
  )

  targets.forEach((target) => observer?.observe(target))
})

onBeforeUnmount(() => {
  pricingSwiper.value = null
  observer?.disconnect()
  observer = null
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.pricing-page {
  --bg: var(--theme-page-bg);
  --surface: var(--theme-surface);
  --surface-border: var(--theme-surface-border);
  --text-primary: var(--theme-text-primary);
  --text-secondary: var(--theme-text-secondary);
  --brand-a: var(--theme-brand-a);
  --brand-b: var(--theme-brand-b);

  position: relative;
  min-height: 100vh;
  padding: 2rem 1rem 4.5rem 3rem;
  background: var(--bg);
  color: var(--text-primary);
  font-family: Inter, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  overflow: hidden;
  isolation: isolate;
}

.mesh-layer {
  position: absolute;
  inset: 0;
  z-index: -1;
  background: var(--theme-mesh-background);
  filter: saturate(115%);
  animation: mesh-drift 18s ease-in-out infinite alternate;
}

.section-shell {
  width: min(1140px, calc(100% - 2rem));
  margin: 0 auto;
}

.hero {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 2.4rem;
  align-items: center;
}

.kicker,
.cta-kicker {
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

.hero h1 {
  margin: 0.9rem 0 0;
  font-size: clamp(2.25rem, 5.8vw, 4.6rem);
  line-height: 1.02;
  letter-spacing: -0.03em;
  text-wrap: balance;
}

.gradient-text {
  background: linear-gradient(90deg, var(--brand-a), var(--brand-b));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-subtitle,
.section-header p,
.calculator-card p,
.cta-card p,
.faq-card p {
  margin: 1.05rem 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
  text-wrap: balance;
}

.hero-points {
  margin-top: 1.4rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.point-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border-radius: 999px;
  border: 1px solid var(--theme-border);
  padding: 0.42rem 0.7rem;
  font-size: 0.86rem;
  color: var(--theme-text-info);
  background: var(--theme-surface-soft);
}

.point-icon {
  width: 0.95rem;
  height: 0.95rem;
}

.hero-visual {
  display: flex;
  justify-content: center;
}

.hero-orb {
  aspect-ratio: 1;
  border-radius: 28px;
  /* border: 1px solid var(--surface-border); */
  backdrop-filter: blur(12px);
  display: grid;
  place-items: center;
}

.orb-core {
  width: 9rem;
  height: 9rem;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: radial-gradient(circle at 30% 30%, rgba(34, 211, 238, 0.52), rgba(30, 41, 59, 0.09));
  box-shadow:
    inset 0 0 30px rgba(226, 232, 240, 0.16),
    0 20px 40px rgba(34, 211, 238, 0.18);
}

.orb-icon {
  width: 3.4rem;
  height: 3.4rem;
  color: var(--theme-text-strong);
  stroke-width: 1.8;
}

.calculator {
  margin-top: 1.9rem;
}

.calculator-card,
.pricing-card,
.included-card,
.faq-card,
.cta-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.calculator-card {
  border-radius: 20px;
  padding: 1.25rem;
}

.calculator-card h2,
.section-header h2,
.included h2,
.faq h2,
.cta h2 {
  margin: 0;
  font-size: clamp(1.4rem, 3vw, 2.2rem);
  letter-spacing: -0.02em;
  text-wrap: balance;
}

.calculator-card label {
  display: inline-block;
  margin-top: 1rem;
  font-weight: 600;
  color: var(--theme-text-info);
}

.calculator-card input {
  width: 95%;
  margin-top: 0.45rem;
  padding: 0.82rem 0.85rem;
  border-radius: 12px;
  border: 1px solid var(--theme-input-border);
  background: var(--theme-input-bg);
  color: var(--theme-text-strong);
  font-size: 1rem;
  outline: none;
}

.calculator-card input:focus {
  border-color: var(--theme-brand-border);
  box-shadow: 0 0 0 3px var(--theme-brand-ring);
}

.preset-buttons {
  margin-top: 0.75rem;
  display: flex;
  gap: 0.45rem;
  flex-wrap: wrap;
}

.preset-btn {
  border: 1px solid var(--theme-border-strong);
  background: var(--theme-surface-soft);
  color: var(--theme-text-primary);
  border-radius: 999px;
  padding: 0.35rem 0.7rem;
  font-weight: 600;
  cursor: pointer;
}

.preset-btn.active,
.preset-btn:hover {
  border-color: var(--theme-brand-border);
  background: var(--theme-brand-soft-strong);
}

.calculator-summary {
  margin-top: 1rem;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.65rem;
}

.summary-item {
  border-radius: 12px;
  border: 1px solid var(--theme-border);
  background: var(--theme-panel-strong);
  padding: 0.7rem;
}

.summary-item p {
  margin: 0;
  font-size: 0.82rem;
  color: var(--theme-text-secondary);
}

.summary-item strong {
  display: block;
  margin-top: 0.4rem;
  font-size: 1.02rem;
}

.pricing {
  margin-top: 2.6rem;
}

.section-header {
  margin-bottom: 1.1rem;
}

.pricing-actions {
  margin-top: 0.8rem;
  display: flex;
  justify-content: center;
}

/* --- SWIPER CAROUSEL STYLES --- */
.pricing-carousel-wrapper {
  /* This lets the carousel bleed to the edges of the screen on mobile for a native feel */
  width: 100vw;
  position: relative;
  left: 50%;
  right: 50%;
  margin-left: -50vw;
  margin-right: -50vw;
  padding: 1rem 0 3rem 0; /* Extra bottom padding for pagination dots */
}

.pricing-swiper {
  width: 100%;
  padding-bottom: 3rem !important; /* Forces room for the pagination dots */
  overflow: visible; /* Lets shadows render outside the container */
}

.pricing-slide {
  width: 320px; /* Fixed width for the cards */
  height: auto;
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s ease;
  
  /* Dim and shrink the cards that are NOT in the center */
  opacity: 0.5;
  transform: scale(0.85) translateY(10px); 
}

/* The card that is currently centered */
.swiper-slide-active {
  opacity: 1;
  transform: scale(1) translateY(0);
  z-index: 10;
}

/* Ensure the article inside takes full height */
.pricing-slide .pricing-card {
  height: 100%;
  margin: 0; /* Reset margins */
}

/* --- CUSTOMIZE SWIPER PAGINATION DOTS --- */
:deep(.swiper-pagination-bullet) {
  background: var(--text-secondary);
  opacity: 0.4;
  width: 8px;
  height: 8px;
  transition: all 0.3s ease;
}

:deep(.swiper-pagination-bullet-active) {
  background: var(--brand-a);
  opacity: 1;
  width: 24px; /* Makes the active dot look like a pill/dash */
  border-radius: 4px;
}

/* Base Pricing Card Styles (Cleaned up for Swiper) */
.pricing-card {
  position: relative;
  overflow: hidden;
  border-radius: 18px;
  padding: 1.1rem;
  cursor: pointer;
  transition: transform 240ms ease, box-shadow 240ms ease, border-color 240ms ease;
  background: var(--surface);
  border: 1px solid var(--surface-border);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.pricing-card.is-focused {
  cursor: default;
}

.pricing-card::before {
  content: '';
  position: absolute;
  inset: -40% auto auto -20%;
  width: 13rem;
  height: 13rem;
  background: radial-gradient(circle, rgba(34, 211, 238, 0.2), transparent 70%);
  opacity: 0;
  transition: opacity 260ms ease;
  pointer-events: none;
}

.pricing-card:hover {
  transform: translateY(-4px);
  border-color: var(--theme-brand-border);
  box-shadow: var(--theme-shadow-soft);
}

.pricing-card:hover::before {
  opacity: 1;
}

.pricing-card.featured {
  border-color: var(--theme-brand-border);
}

.pricing-card.best-value {
  border-color: rgba(245, 158, 11, 0.48);
}

.plan-badge {
  position: absolute;
  right: 12px;
  top: 12px;
  border-radius: 999px;
  padding: 0.27rem 0.58rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #f8fafc;
  background: linear-gradient(90deg, #0ea5e9, #2563eb);
}

.tone-cyan {
  background: linear-gradient(90deg, #06b6d4, #0ea5e9);
}

.tone-blue {
  background: linear-gradient(90deg, #2563eb, #3b82f6);
}

.tone-amber {
  background: linear-gradient(90deg, #f59e0b, #d97706);
}

.tone-emerald {
  background: linear-gradient(90deg, #10b981, #059669);
}

.card-header h3 {
  margin: 0.7rem 0 0;
  font-size: 1.2rem;
}

.card-header p {
  margin: 0.5rem 0 0;
  color: var(--text-secondary);
}

.plan-icon-wrap {
  width: 2.7rem;
  height: 2.7rem;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: var(--theme-surface-soft-strong);
  border: 1px solid var(--theme-border);
}

.plan-icon {
  width: 1.3rem;
  height: 1.3rem;
  color: var(--theme-text-soft);
}

.price-box {
  margin-top: 0.95rem;
  padding-top: 0.85rem;
  border-top: 1px solid var(--theme-border-soft);
}

.price-main {
  display: flex;
  align-items: baseline;
  gap: 0.3rem;
  justify-content: center;
}

.currency {
  font-size: 1.2rem;
  color: var(--theme-text-soft);
}

.amount {
  font-size: clamp(1.8rem, 3.2vw, 2.5rem);
  font-weight: 800;
}

.unit,
.billing-note {
  color: var(--theme-text-secondary);
}

.billing-note {
  margin: 0.35rem 0 0;
  font-size: 0.88rem;
}

.savings-badge {
  margin-top: 0.55rem;
  display: flex;
  justify-content: space-between;
  gap: 0.7rem;
  border-radius: 8px;
  background: var(--theme-success-soft);
  border: 1px solid var(--theme-success-border);
  color: var(--theme-success-text);
  padding: 0.45rem 0.6rem;
  font-size: 0.84rem;
  font-weight: 700;
}

.feature-list {
  margin: 0.95rem 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.6rem;
}

.feature-list li {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
  color: var(--theme-text-soft);
  font-size: 0.9rem;
}

.check-icon {
  width: 1rem;
  height: 1rem;
  color: var(--theme-success-text);
  flex: 0 0 auto;
  margin-top: 0.15rem;
}

.total-box {
  margin-top: 1rem;
  border-radius: 12px;
  border: 1px solid var(--theme-border);
  background: var(--theme-panel-strong);
  padding: 0.75rem;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.6rem;
}

.total-row strong {
  font-size: 1.08rem;
}

.bonus-row {
  margin-top: 0.6rem;
  border-radius: 10px;
  padding: 0.58rem;
  background: var(--theme-info-soft);
  border: 1px solid var(--theme-info-border);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.bonus-row strong {
  display: block;
  font-size: 0.9rem;
}

.bonus-row p {
  margin: 0.2rem 0 0;
  font-size: 0.78rem;
  color: var(--theme-info-text);
}

.bonus-icon {
  width: 1rem;
  height: 1rem;
  color: var(--theme-info-text);
  flex: 0 0 auto;
}

.effective-note {
  margin: 0.65rem 0 0;
  font-size: 0.82rem;
  color: var(--theme-info-text);
}

.effective-note span {
  display: block;
  color: var(--theme-text-secondary);
  margin-top: 0.2rem;
}

.included,
.faq,
.cta {
  margin-top: 2.8rem;
}

.included-grid,
.faq-grid {
  margin-top: 1.1rem;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.8rem;
}

.included-card,
.faq-card {
  border-radius: 14px;
  padding: 0.9rem;
}

.included-card {
  display: flex;
  align-items: center;
  gap: 0.55rem;
}

.included-card p {
  margin: 0;
  color: var(--theme-text-info);
  font-size: 0.92rem;
}

.included-icon {
  width: 1.1rem;
  height: 1.1rem;
  color: var(--theme-brand-pill-text);
}

.faq-card h3 {
  margin: 0;
  font-size: 1rem;
  color: var(--theme-text-strong);
}

.faq-card p {
  margin: 0.5rem 0 0;
  font-size: 0.92rem;
}

.cta-card {
  border-radius: 22px;
  padding: 1.6rem;
  box-shadow: var(--theme-shadow-soft);
}

.cta-actions {
  margin-top: 1.4rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
}

.btn {
  --mx: 50%;
  --my: 50%;

  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.75rem 1.15rem;
  border-radius: 12px;
  text-decoration: none;
  border: 1px solid transparent;
  font-weight: 600;
  letter-spacing: 0.01em;
  transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease, background 180ms ease;
  will-change: transform;
}

.btn::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: radial-gradient(circle at var(--mx) var(--my), rgba(255, 255, 255, 0.2), transparent 55%);
  opacity: 0;
  transition: opacity 180ms ease;
  pointer-events: none;
}

.btn:hover::after {
  opacity: 1;
}

.btn-solid {
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
  color: var(--theme-brand-on);
  box-shadow: 0 14px 28px rgba(59, 130, 246, 0.2);
}

.btn-ghost {
  color: var(--theme-text-primary);
  border-color: var(--theme-border-strong);
  background: var(--theme-surface-soft);
}

.btn-ghost:hover {
  border-color: var(--theme-brand-border);
}

.reveal {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 620ms cubic-bezier(0.16, 1, 0.3, 1), transform 620ms cubic-bezier(0.16, 1, 0.3, 1);
}

.reveal.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.floaty {
  animation: float 6s ease-in-out infinite;
}


/* --- CUSTOMIZE SWIPER NAVIGATION ARROWS --- */
:deep(.swiper-button-next),
:deep(.swiper-button-prev) {
  color: var(--brand-a); /* Uses your cyan gradient color */
  background: var(--theme-input-bg); /* Matches your card background */
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 1px solid var(--theme-border);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  transition: all 0.3s ease;

  svg{
    width : 20% ;
    stroke-width : 2.5;
  }
}

:deep(.swiper-button-next:hover),
:deep(.swiper-button-prev:hover) {
  background: var(--theme-panel-solid);
  border-color: var(--brand-a);
  transform: scale(1.05);
}

/* Make the actual arrow icon smaller and bolder */
:deep(.swiper-button-next::after),
:deep(.swiper-button-prev::after) {
  font-size: 1.2rem;
  font-weight: 800;
}



@keyframes mesh-drift {
  0% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  100% {
    transform: translate3d(-1.5%, 1.2%, 0) scale(1.04);
  }
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-14px);
  }
}

@media (min-width: 1080px) {
  :deep(.swiper-button-prev) {
    /* 320px is your card width. This safely anchors the arrow outside it */
    left: calc(50% - 380px); 
  }
  
  :deep(.swiper-button-next) {
    right: calc(50% - 380px);
  }
}

/* For mid-sized screens (tablets/small laptops), just give them safe padding */
@media (min-width: 768px) and (max-width: 1079px) {
  :deep(.swiper-button-prev) {
    left: 4vw;
  }
  :deep(.swiper-button-next) {
    right: 4vw;
  }
}

@media (max-width: 1200px) {
  .included-grid,
  .faq-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 1080px) {
  .pricing-page {
    padding: 2rem 1rem 4.5rem 1rem;
  }

  .hero {
    grid-template-columns: 1fr;
  }

  .hero-visual {
    order: -1;
  }

  .calculator-summary {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 767px) {
  .included-grid,
  .faq-grid {
    grid-template-columns: 1fr;
  }

  .cta-card,
  .calculator-card {
    padding: 1.2rem;
  }

  .calculator-card input {
    width: 90%;
  }

}
</style>
