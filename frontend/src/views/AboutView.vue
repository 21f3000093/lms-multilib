<template>
  <main class="about-page" ref="pageRoot">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="hero section-shell">
      <div class="hero-copy reveal" data-stagger="0">
        <p class="kicker">Smart Library App</p>
        <h1>Run your library from one dashboard</h1>
        <p class="hero-subtitle">
          Manage admissions, seats, fees, receipts, and WhatsApp reminders without notebooks or spreadsheets.
        </p>

        <div class="hero-actions">
          <router-link
            class="btn btn-solid magnetic"
            to="/signup"
            @mousemove="onMagneticMove"
            @mouseleave="onMagneticLeave"
          >
            Start Free
          </router-link>
          <router-link
            class="btn btn-ghost magnetic"
            to="/pricing-plans"
            @mousemove="onMagneticMove"
            @mouseleave="onMagneticLeave"
          >
            View Pricing
          </router-link>
        </div>

        <div class="hero-points">
          <div v-for="item in heroPoints" :key="item.label" class="point-chip reveal" :data-stagger="item.stagger">
            <component :is="item.icon" class="point-icon" aria-hidden="true" />
            {{ item.label }}
          </div>
        </div>
      </div>

      <div class="hero-visual reveal" data-stagger="1">
        <div class="hero-device-stage">
          <img
            :src="heroScreenshot"
            alt="Smart Library dashboard showing occupancy, collections, and library performance"
            class="hero-image"
          />
        </div>
        <div class="hero-float-card hero-float-card-top">
          <span class="float-value">Live</span>
          <span class="float-label">seat visibility</span>
        </div>
        <div class="hero-float-card hero-float-card-bottom">
          <span class="float-value">₹</span>
          <span class="float-label">fees and receipts</span>
        </div>
      </div>
    </section>

    <section class="stats section-shell reveal" data-stagger="0">
      <article v-for="item in stats" :key="item.label" class="stat-card reveal" :data-stagger="item.stagger">
        <p class="stat-value">{{ item.value }}</p>
        <p class="stat-label">{{ item.label }}</p>
      </article>
    </section>

    <section class="showcase section-shell">
      <header class="section-header reveal" data-stagger="0">
        <h2>See Smart Library in action</h2>
        <p>Switch through the core workflows your team uses every day.</p>
      </header>

      <div class="showcase-shell glass-card reveal" data-stagger="1">
        <div class="showcase-tabs" role="tablist" aria-label="App screenshot switcher">
          <button
            v-for="tab in showcaseTabs"
            :key="tab.key"
            type="button"
            class="showcase-tab"
            :class="{ 'is-active': activeShowcaseKey === tab.key }"
            :aria-selected="activeShowcaseKey === tab.key"
            @click="activeShowcaseKey = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>

        <Transition name="showcase-fade" mode="out-in">
          <article :key="activeShowcase.key" class="showcase-stage">
            <div class="showcase-frame">
              <img :src="activeShowcase.src" :alt="activeShowcase.alt" class="showcase-image" />
            </div>
            <div class="showcase-copy">
              <p class="showcase-kicker">{{ activeShowcase.label }}</p>
              <h3>{{ activeShowcase.title }}</h3>
              <p>{{ activeShowcase.description }}</p>
            </div>
          </article>
        </Transition>
      </div>
    </section>

    <section class="comparison section-shell">
      <header class="section-header reveal" data-stagger="0">
        <h2>Manual work vs Smart Library</h2>
        <p>Replace scattered records with one visible workflow for seats, students, fees, and reminders.</p>
      </header>

      <div class="comparison-grid">
        <article class="glass-card comparison-card comparison-card-old reveal" data-stagger="1">
          <p class="comparison-kicker">The Old Way</p>
          <ul class="comparison-list">
            <li v-for="item in oldWayPoints" :key="item" class="comparison-item">
              <CircleX class="comparison-icon comparison-icon-old" aria-hidden="true" />
              <span>{{ item }}</span>
            </li>
          </ul>
        </article>

        <div class="comparison-divider reveal" data-stagger="2" aria-hidden="true">
          <span class="comparison-divider-line"></span>
          <div class="comparison-divider-badge">
            <ArrowRight class="comparison-divider-icon" aria-hidden="true" />
          </div>
          <span class="comparison-divider-line"></span>
        </div>

        <article class="glass-card comparison-card comparison-card-smart reveal" data-stagger="3">
          <p class="comparison-kicker comparison-kicker-smart">The Smart Way</p>
          <ul class="comparison-list">
            <li v-for="item in smartWayPoints" :key="item" class="comparison-item">
              <CheckCircle2 class="comparison-icon comparison-icon-smart" aria-hidden="true" />
              <span>{{ item }}</span>
            </li>
          </ul>
        </article>
      </div>

      <div class="feature-strip">
        <article
          v-for="feature in features"
          :key="feature.title"
          class="feature-pill-card reveal"
          :data-stagger="feature.stagger"
        >
          <component :is="feature.icon" class="feature-pill-icon" aria-hidden="true" />
          <div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </article>
      </div>
    </section>

    <section class="workflow section-shell">
      <header class="section-header reveal" data-stagger="0">
        <h2>Start fast, then run daily work from one place</h2>
        <p>Four steps from setup to daily operations.</p>
      </header>

      <div class="workflow-grid">
        <article v-for="step in workflowSteps" :key="step.title" class="glass-card workflow-card reveal" :data-stagger="step.stagger">
          <div class="workflow-step">{{ step.step }}</div>
          <component :is="step.icon" class="workflow-icon" aria-hidden="true" />
          <h3>{{ step.title }}</h3>
          <p>{{ step.description }}</p>
        </article>
      </div>
    </section>

    <section class="testimonials section-shell">
      <header class="section-header reveal" data-stagger="0">
        <h2>What library teams say after switching</h2>
        <p>Less paperwork, clearer operations, faster follow-ups.</p>
      </header>

      <div class="testimonial-grid">
        <article v-for="item in testimonials" :key="item.name" class="glass-card testimonial-card reveal" :data-stagger="item.stagger">
          <div class="testimonial-stars" aria-label="5 star rating">
            <Star v-for="star in 5" :key="star" class="testimonial-star" aria-hidden="true" />
          </div>
          <p class="testimonial-quote">“{{ item.quote }}”</p>
          <div class="testimonial-meta">
            <strong>{{ item.name }}</strong>
            <span>{{ item.library }}</span>
          </div>
        </article>
      </div>
    </section>

    <section class="pricing-teaser section-shell">
      <header class="section-header reveal" data-stagger="0">
        <h2>Flexible pricing that scales with your seat count</h2>
        <p>Start at ₹9 per seat per month with lower effective costs on longer plans.</p>
      </header>

      <div class="pricing-teaser-grid">
        <article v-for="item in pricingHighlights" :key="item.title" class="glass-card teaser-card reveal" :data-stagger="item.stagger">
          <component :is="item.icon" class="teaser-icon" aria-hidden="true" />
          <p class="teaser-kicker">{{ item.kicker }}</p>
          <h3>{{ item.title }}</h3>
          <p>{{ item.description }}</p>
        </article>
      </div>

      <div class="pricing-teaser-bar glass-card reveal" data-stagger="4">
        <div>
          <p class="pricing-teaser-eyebrow">Included in every plan</p>
          <h3>No setup fee. Full feature access. Predictable seat-based billing.</h3>
        </div>
        <router-link class="btn btn-solid magnetic" to="/pricing-plans" @mousemove="onMagneticMove" @mouseleave="onMagneticLeave">
          Explore Full Pricing
        </router-link>
      </div>
    </section>

    <section class="faq section-shell">
      <header class="section-header reveal" data-stagger="0">
        <h2>Frequently asked questions</h2>
        <p>The basics before you create your library account.</p>
      </header>

      <div class="faq-list">
        <article v-for="(item, index) in faqs" :key="item.question" class="glass-card faq-card reveal" :data-stagger="index + 1">
          <button
            type="button"
            class="faq-trigger"
            :aria-expanded="openFaqIndex === index"
            @click="toggleFaq(index)"
          >
            <span>{{ item.question }}</span>
            <ChevronDown class="faq-icon" :class="{ 'is-open': openFaqIndex === index }" aria-hidden="true" />
          </button>
          <Transition name="faq-collapse">
            <div v-if="openFaqIndex === index" class="faq-answer">
              <p>{{ item.answer }}</p>
            </div>
          </Transition>
        </article>
      </div>
    </section>

    <section class="cta section-shell reveal" data-stagger="1">
      <div class="cta-card">
        <p class="cta-kicker">Ready to digitize your library operations?</p>
        <h2>Ready to make your library truly smart?</h2>
        <p>Run your study center from your phone or laptop without manual registers.</p>

        <div class="cta-actions">
          <router-link class="btn btn-solid magnetic" to="/signup" @mousemove="onMagneticMove" @mouseleave="onMagneticLeave">
            Create Library Account
          </router-link>
          <!-- <router-link class="btn btn-ghost magnetic" to="/pricing-plans" @mousemove="onMagneticMove" @mouseleave="onMagneticLeave">
            View Pricing
          </router-link> -->
        </div>
      </div>
    </section>

    <footer class="about-footer section-shell reveal" data-stagger="2">
      <p class="about-footer-copy">© {{ currentYear }} Smart Library App</p>
      <nav class="about-footer-links" aria-label="About page footer links">
        <router-link to="/about">About</router-link>
        <router-link to="/pricing-plans">Pricing</router-link>
        <router-link to="/privacy-policy">Privacy Policy</router-link>
        <router-link to="/login">Login</router-link>
      </nav>
    </footer>
  </main>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import {
  ArrowRight,
  Armchair,
  BarChart3,
  Bell,
  CheckCircle2,
  ChevronDown,
  CircleDollarSign,
  CircleX,
  CreditCard,
  Gift,
  LayoutDashboard,
  MessageSquare,
  ReceiptText,
  ShieldCheck,
  Sparkles,
  Star,
  UserPlus,
  Users,
} from 'lucide-vue-next'

const pageRoot = ref(null)
const activeShowcaseKey = ref('students')
const openFaqIndex = ref(0)
const currentYear = computed(() => new Date().getFullYear())

let revealObserver = null
const screenshotBase = '/img/screenshots'
const heroScreenshot = `${screenshotBase}/dashboard.png`

const heroPoints = [
  { icon: Armchair, label: 'Live seat map', stagger: 2 },
  { icon: ReceiptText, label: 'Payment receipts', stagger: 3 },
  { icon: MessageSquare, label: 'WhatsApp reminders', stagger: 4 },
]

const stats = [
  { value: '50+', label: 'libraries operating digitally', stagger: 1 },
  { value: '9k+', label: 'student records managed', stagger: 2 },
  { value: '35%', label: 'faster daily follow-ups', stagger: 3 },
  { value: '1', label: 'workspace for seats, fees, and reminders', stagger: 4 },
]

const testimonials = [
  {
    name: 'Lokesh Soni',
    library: 'Soni Library',
    quote: 'Manual follow-ups ka tension hi khatam ho gaya! Ab seats, collections aur reminders sab ek hi jagah mil jaate hain, toh kaafi time bachta hai.',
    stagger: 1,
  },
  {
    name: 'Neha Sharma',
    library: 'Scholars Library',
    quote: 'Har subah dashboard dekh kar sab clear ho jata hai. Ab koi guessing game nahi chalta ki kaunsi seat khali hai ya kiska payment baki hai.',
    stagger: 2,
  },
  {
    name: 'Rohit Gupta',
    library: 'Focus Point Library',
    quote: 'Receipts aur payment history sambhalna ab bahut simple hai. Students ko turant jawab mil jata hai aur staff ka kaam bhi kaafi asaan ho gaya hai.',
    stagger: 3,
  },
]

const oldWayPoints = [
  'Manual notebooks & spreadsheets',
  'Scattered fee records',
  'Time-consuming manual reminders',
  'No real-time seat visibility',
]

const smartWayPoints = [
  'Unified digital workspace',
  'Automated billing & receipts',
  'Instant WhatsApp workflows',
  'Live occupancy dashboard',
]

const features = [
  {
    icon: Armchair,
    title: 'Live seats',
    description: 'See occupancy by shift before assigning a student.',
    stagger: 1,
  },
  {
    icon: Users,
    title: 'Student profiles',
    description: 'Keep contact, seat, shift, and payment details connected.',
    stagger: 2,
  },
  {
    icon: CreditCard,
    title: 'Fee records',
    description: 'Track monthly dues, paid status, and receipts in one view.',
    stagger: 3,
  },
  {
    icon: MessageSquare,
    title: 'Reminders',
    description: 'Send ready-to-use WhatsApp follow-ups for pending fees.',
    stagger: 4,
  },
  {
    icon: BarChart3,
    title: 'Dashboard',
    description: 'Watch collections, occupancy, and movement trends quickly.',
    stagger: 5,
  },
  {
    icon: ShieldCheck,
    title: 'Secure access',
    description: 'Keep library operations behind authenticated admin access.',
    stagger: 6,
  },
]

const showcaseTabs = [
  {
    key: 'dashboard',
    label: 'Dashboard',
    title: 'Collections and occupancy in one glance',
    description: 'Daily revenue, full seats, pending fees, and trends stay visible.',
    alt: 'Smart Library dashboard with occupancy, collection, and student movement metrics',
    src: `${screenshotBase}/dashboard.png`,
  },
  {
    key: 'students',
    label: 'Students',
    title: 'Searchable student records',
    description: 'Admissions, contact details, seats, and payment history stay connected.',
    alt: 'Smart Library student list with contact, seat, shift, and fee details',
    src: `${screenshotBase}/students.png`,
  },
  {
    key: 'seats',
    label: 'Seats',
    title: 'Live seat visibility by shift',
    description: 'See occupied and available seats before assigning anyone.',
    alt: 'Smart Library seat map showing seat availability by shift',
    src: `${screenshotBase}/seats.png`,
  },
  {
    key: 'payments',
    label: 'Payments',
    title: 'Monthly fees and receipts',
    description: 'Track paid, pending, and receipt-ready records without scattered books.',
    alt: 'Smart Library monthly payment list with paid and pending fee records',
    src: `${screenshotBase}/payments.png`,
  },
  {
    key: 'reminders',
    label: 'Reminders',
    title: 'Ready-to-send reminders',
    description: 'Prepare fee follow-ups fast and keep collections moving.',
    alt: 'Smart Library WhatsApp reminders workflow for pending fee follow-ups',
    src: `${screenshotBase}/reminders.png`,
  },
]

const activeShowcase = computed(() => showcaseTabs.find((tab) => tab.key === activeShowcaseKey.value) || showcaseTabs[0])

const workflowSteps = [
  {
    step: '01',
    icon: UserPlus,
    title: 'Create your library account',
    description: 'Sign up with your email and enter your library details in just 2 minutes.',
    stagger: 1,
  },
  {
    step: '02',
    icon: Armchair,
    title: 'Add students and assign seats',
    description: 'Register students, map them to seats and shifts, and keep admissions structured from day one.',
    stagger: 2,
  },
  {
    step: '03',
    icon: Bell,
    title: 'Track fees and send reminders',
    description: 'Keep billing, receipts, and WhatsApp follow-ups in one organized collection workflow.',
    stagger: 3,
  },
  {
    step: '04',
    icon: LayoutDashboard,
    title: 'Monitor operations from one dashboard',
    description: 'See occupancy, payment health, and key activity signals without switching between tools.',
    stagger: 4,
  },
]

const pricingHighlights = [
  {
    icon: CircleDollarSign,
    kicker: 'Monthly flexibility',
    title: 'Start at ₹9 per seat per month',
    description: 'A simple starting point for libraries that want full feature access without setup costs.',
    stagger: 1,
  },
  {
    icon: Sparkles,
    kicker: 'Smarter scaling',
    title: 'Lower your effective monthly cost on longer plans',
    description: 'Annual and multi-month billing cycles reduce cost per seat as operations become more stable.',
    stagger: 2,
  },
  {
    icon: Gift,
    kicker: 'First-purchase advantage',
    title: 'Unlock bonus months on eligible plans',
    description: 'Grow with predictable billing and extra value when you commit to longer operating cycles.',
    stagger: 3,
  },
]

const faqs = [
  {
    question: 'How is pricing calculated?',
    answer: 'Pricing is seat-based, so your cost scales with the number of seats you manage. Longer billing cycles reduce the effective monthly cost per seat.',
  },
  {
    question: 'Are there seat limits on the platform?',
    answer: 'You can start with a small library and scale up. Plans are designed to grow with your seat capacity rather than force a one-size-fits-all limit.',
  },
  {
    question: 'Does the app support WhatsApp reminders?',
    answer: 'Yes. Smart Library App supports reminder workflows that help admins follow up on pending fees much faster than manual messaging.',
  },
  {
    question: 'How is my library data kept secure?',
    answer: 'Your data is backed up safely on the cloud. Only you can access your student and payment records.',
  },
  {
    question: 'Is there a trial period before I commit?',
    answer: 'Yes! You can create an account and try the app completely free to see how it works for your library before choosing a plan.',
  },
  // {
  //   question: 'Can this support multi-branch or growing operations?',
  //   answer: 'Absolutely. If you own multiple library branches, you can manage all of them from one single main account.',
  // },
]

const toggleFaq = (index) => {
  openFaqIndex.value = openFaqIndex.value === index ? -1 : index
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
  const element = event.currentTarget
  element.style.transform = 'translate(0, 0)'
}

onMounted(() => {
  const targets = pageRoot.value?.querySelectorAll('.reveal') || []

  revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return
        }

        const stagger = Number(entry.target.dataset.stagger || 0)
        entry.target.style.transitionDelay = `${Math.min(stagger * 80, 420)}ms`
        entry.target.classList.add('is-visible')
        revealObserver?.unobserve(entry.target)
      })
    },
    {
      threshold: 0.18,
      rootMargin: '0px 0px -10% 0px',
    }
  )

  targets.forEach((target) => revealObserver?.observe(target))
})

onUnmounted(() => {
  revealObserver?.disconnect()
  revealObserver = null
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.about-page {
  --bg: var(--theme-page-bg);
  --surface: var(--theme-surface);
  --surface-border: var(--theme-surface-border);
  --text-primary: var(--theme-text-primary);
  --text-secondary: var(--theme-text-secondary);
  --brand-a: var(--theme-brand-a);
  --brand-b: var(--theme-brand-b);

  position: relative;
  min-height: 100vh;
  padding: 2rem 2rem 4rem;
  color: var(--text-primary);
  background: var(--bg);
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
  grid-template-columns: minmax(0, 0.94fr) minmax(0, 1.06fr);
  gap: clamp(1.35rem, 3.5vw, 2.7rem);
  align-items: center;
  padding-top: 1.7rem;
  text-wrap-style: balance;
}

.hero-copy {
  max-width: 34rem;
  text-align: left;
}

.kicker,
.cta-kicker,
.teaser-kicker,
.pricing-teaser-eyebrow,
.showcase-kicker {
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
  font-size: clamp(2.35rem, 4.35vw, 4.15rem);
  line-height: 1.04;
  letter-spacing: -0.03em;
  text-wrap: balance;
}

.hero-visual {
  position: relative;
  min-width: 0;
}

.hero-device-stage {
  position: relative;
  /* overflow: hidden; */
  min-height: clamp(18rem, 35vw, 29rem);
  /* border: 1px solid var(--theme-border-soft); */
  border-radius: 28px;
  /* background:
    radial-gradient(circle at 64% 42%, var(--theme-brand-soft-strong), transparent 38%),
    radial-gradient(circle at 20% 78%, var(--theme-surface-soft-strong), transparent 36%),
    linear-gradient(145deg, var(--theme-panel), var(--theme-surface-soft));
  box-shadow: var(--theme-shadow-elevated); */
}

.hero-image {
  position: absolute;
  width: min(112%, 42rem);
  max-width: none;
  right: -12%;
  top: 50%;
  transform: translateY(-49%);
  filter: drop-shadow(0 28px 34px rgba(15, 23, 42, 0.18));
}

.hero-float-card {
  position: absolute;
  display: none;
  gap: 0.1rem;
  min-width: 8.8rem;
  padding: 0.78rem 0.9rem;
  border: 1px solid var(--theme-border-soft);
  border-radius: 16px;
  background: var(--theme-nav-surface-strong);
  box-shadow: var(--theme-shadow-soft);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.hero-float-card-top {
  top: 14%;
  right: -0.35rem;
}

.hero-float-card-bottom {
  left: -0.25rem;
  bottom: 13%;
}

.float-value {
  color: var(--theme-text-strong);
  font-size: 1.15rem;
  font-weight: 800;
}

.float-label {
  color: var(--theme-text-secondary);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.hero-subtitle,
.section-header p,
.cta-card p,
.teaser-card p,
.workflow-card p,
.showcase-copy p,
.faq-answer p,
.testimonial-quote {
  margin: 1.1rem 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
  text-wrap: balance;
}

.hero-actions{
  margin-top: 1.7rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  justify-content: flex-start;
}

.cta-actions {
  margin-top: 1.7rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  justify-content: center;
}

.hero-points {
  margin-top: 1.15rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
  justify-content: flex-start;
}

.point-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.65rem 0.9rem;
  border-radius: 999px;
  border: 1px solid var(--theme-border-soft);
  background: var(--theme-panel);
  color: var(--theme-text-soft);
  font-size: 0.88rem;
  font-weight: 600;
}

.point-icon {
  width: 1rem;
  height: 1rem;
  color: var(--theme-brand-pill-text);
}

.stats,
.testimonials,
.workflow,
.pricing-teaser,
.comparison,
.showcase,
.faq,
.cta {
  margin-top: 3rem;
}

.about-footer {
  margin-top: 1.2rem;
  padding: 0.4rem 0 0.6rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
  flex-wrap: wrap;
}

.about-footer-copy {
  margin: 0;
  color: var(--theme-text-muted);
  font-size: 0.86rem;
}

.about-footer-links {
  display: inline-flex;
  align-items: center;
  gap: 0.78rem;
  flex-wrap: wrap;
}

.about-footer-links a {
  color: var(--theme-text-soft);
  text-decoration: none;
  font-size: 0.86rem;
  font-weight: 600;
}

.about-footer-links a:hover {
  color: var(--theme-brand-pill-text);
}

.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.9rem;
}

.glass-card,
.stat-card,
.feature-pill-card,
.cta-card,
.workflow-card,
.teaser-card,
.showcase-shell,
.testimonial-card,
.faq-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.stat-card {
  border-radius: 14px;
  padding: 1rem;
  text-align: left;
}

.stat-value {
  margin: 0;
  font-size: clamp(1.2rem, 2vw, 1.9rem);
  font-weight: 700;
}

.stat-label {
  margin: 0.45rem 0 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.section-header h2,
.cta-card h2 {
  margin: 0;
  font-size: clamp(1.5rem, 3.3vw, 2.4rem);
  letter-spacing: -0.02em;
  text-wrap: balance;
}

.testimonial-grid {
  margin-top: 1.3rem;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.9rem;
}

.testimonial-card {
  border-radius: 18px;
  padding: 1.2rem;
}

.testimonial-stars {
  display: flex;
  gap: 0.28rem;
}

.testimonial-star {
  width: 1rem;
  height: 1rem;
  color: var(--theme-warning-text);
  fill: currentColor;
}

.testimonial-quote {
  margin-top: 0.95rem;
}

.testimonial-meta {
  margin-top: 1rem;
  display: grid;
  gap: 0.2rem;
}

.testimonial-meta strong {
  font-size: 0.95rem;
}

.testimonial-meta span {
  color: var(--theme-text-secondary);
  font-size: 0.86rem;
}

.comparison-grid {
  margin-top: 1.3rem;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  gap: 0.9rem;
  align-items: stretch;
}

.comparison-card {
  position: relative;
  overflow: hidden;
  border-radius: 18px;
  padding: 1.2rem;
  text-align: left;
}

.comparison-card-old {
  border-color: var(--theme-border-strong);
  background:
    linear-gradient(145deg, var(--theme-surface-soft), transparent 58%),
    var(--surface);
  box-shadow: inset 0 1px 0 var(--theme-surface-border);
}

.comparison-card-smart {
  border-color: var(--theme-brand-border);
  background:
    radial-gradient(circle at top right, var(--theme-brand-soft-strong), transparent 46%),
    linear-gradient(145deg, var(--theme-brand-soft), transparent 60%),
    var(--surface);
  box-shadow: var(--theme-shadow-soft);
}

.comparison-kicker {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-secondary);
}

.comparison-kicker-smart {
  color: var(--brand-a);
}

.comparison-list {
  list-style: none;
  margin: 1rem 0 0;
  padding: 0;
  display: grid;
  gap: 0.8rem;
}

.comparison-item {
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
  color: var(--text-primary);
  line-height: 1.55;
}

.comparison-icon {
  width: 1.15rem;
  height: 1.15rem;
  flex: 0 0 auto;
  margin-top: 0.1rem;
  stroke-width: 2.1;
}

.comparison-icon-old {
  color: var(--text-secondary);
}

.comparison-icon-smart {
  color: var(--brand-a);
}

.comparison-divider {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  min-width: 3.25rem;
}

.comparison-divider-line {
  width: 1px;
  flex: 1;
  min-height: 2.75rem;
  background: linear-gradient(180deg, transparent, var(--theme-border-strong), transparent);
}

.comparison-divider-badge {
  width: 2.8rem;
  height: 2.8rem;
  border-radius: 999px;
  display: grid;
  place-items: center;
  border: 1px solid var(--theme-brand-border);
  background:
    radial-gradient(circle at 35% 30%, var(--theme-brand-soft-strong), transparent 60%),
    var(--theme-panel-solid);
  box-shadow: var(--theme-shadow-soft);
}

.comparison-divider-icon {
  width: 1.2rem;
  height: 1.2rem;
  color: var(--brand-a);
  stroke-width: 2.1;
}

.feature-strip {
  margin-top: 1rem;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.9rem;
}

.feature-pill-card {
  display: flex;
  align-items: flex-start;
  gap: 0.78rem;
  border-radius: 18px;
  padding: 1rem;
  text-align: left;
}

.feature-pill-icon {
  width: 1.22rem;
  height: 1.22rem;
  margin-top: 0.2rem;
  color: var(--theme-brand-pill-text);
  flex: 0 0 auto;
}

.feature-pill-card h3,
.workflow-card h3,
.teaser-card h3,
.showcase-copy h3,
.faq-trigger {
  margin: 0.65rem 0 0;
  font-size: 1.15rem;
}

.feature-pill-card h3 {
  margin-top: 0;
}

.feature-pill-card p {
  margin: 0.55rem 0 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.workflow-icon,
.teaser-icon {
  width: 1.3rem;
  height: 1.3rem;
  color: var(--theme-text-soft);
  stroke-width: 2.1;
}

.showcase-shell {
  margin-top: 1.3rem;
  border-radius: 22px;
  padding: 1.1rem;
}

.showcase-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
}

.showcase-tab {
  padding: 0.72rem 1rem;
  border-radius: 999px;
  border: 1px solid var(--theme-border-soft);
  background: var(--theme-surface-soft);
  color: var(--theme-text-primary);
  font-weight: 700;
  cursor: pointer;
  transition: border-color 180ms ease, background 180ms ease, color 180ms ease, transform 180ms ease;
}

.showcase-tab:hover {
  transform: translateY(-1px);
  border-color: var(--theme-brand-border);
}

.showcase-tab.is-active {
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
  color: var(--theme-brand-on);
  border-color: transparent;
  box-shadow: var(--theme-shadow-soft);
}

.showcase-stage {
  margin-top: 1rem;
  display: grid;
  grid-template-columns: minmax(0, 1.34fr) minmax(260px, 0.66fr);
  gap: 1.15rem;
  align-items: center;
}

.showcase-copy {
  /* text-align: left; */
  align-self: start;
}

.showcase-copy h3 {
  margin-top: 0.7rem;
  font-size: clamp(1.25rem, 2.7vw, 1.8rem);
  letter-spacing: -0.02em;
}

.showcase-copy p {
  margin-top: 0.8rem;
}

.showcase-frame {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  /* border: 1px solid var(--theme-border-soft);
  background:
    radial-gradient(circle at 55% 42%, var(--theme-brand-soft-strong), transparent 40%),
    linear-gradient(145deg, var(--theme-panel), var(--theme-surface-soft));
  box-shadow: var(--theme-shadow-soft); */
  aspect-ratio: 16 / 16;
}

.showcase-image {
  position: absolute;
  inset: 0;
  display: block;
  width: 100%;
  height: 100%;
  /* object-fit: cover; */
  object-position: center;
}

.workflow-grid,
.pricing-teaser-grid {
  margin-top: 1.3rem;
  display: grid;
  gap: 0.9rem;
}

.workflow-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.pricing-teaser-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.workflow-card,
.teaser-card {
  border-radius: 18px;
  padding: 1.2rem;
}

.workflow-step {
  width: fit-content;
  min-width: 2.55rem;
  height: 2.55rem;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: var(--theme-brand-soft);
  border: 1px solid var(--theme-brand-border);
  color: var(--theme-brand-pill-text);
  font-weight: 800;
  letter-spacing: 0.04em;
}

.workflow-icon,
.teaser-icon {
  margin-top: 1rem;
}

.workflow-card p,
.teaser-card p {
  margin-top: 0.55rem;
}

.pricing-teaser-bar {
  margin-top: 1rem;
  border-radius: 20px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  box-shadow: var(--theme-shadow-soft);
}

.pricing-teaser-eyebrow {
  margin-bottom: 0.65rem;
}

.pricing-teaser-bar h3 {
  margin: 0;
  font-size: clamp(1.15rem, 2.4vw, 1.5rem);
  letter-spacing: -0.02em;
}

.faq-list {
  margin-top: 1.3rem;
  display: grid;
  gap: 0.85rem;
}

.faq-card {
  border-radius: 18px;
  overflow: hidden;
}

.faq-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.1rem;
  border: 0;
  background: transparent;
  color: var(--theme-text-primary);
  text-align: left;
  cursor: pointer;
}

.faq-icon {
  width: 1.1rem;
  height: 1.1rem;
  color: var(--theme-text-secondary);
  transition: transform 180ms ease;
}

.faq-icon.is-open {
  transform: rotate(180deg);
}

.faq-answer {
  padding: 0 1.1rem 1rem;
}

.faq-answer p {
  margin: 0;
  text-align: left;
}

.cta-card {
  border-radius: 22px;
  padding: 1.8rem;
  box-shadow: var(--theme-shadow-soft);
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

.btn-subtle {
  color: var(--theme-text-soft);
  border-color: transparent;
  background: transparent;
}

.btn-ghost:hover,
.btn-subtle:hover {
  border-color: var(--theme-brand-border);
  background: var(--theme-surface-soft-strong);
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

.showcase-fade-enter-active,
.showcase-fade-leave-active {
  transition: opacity 220ms ease, transform 220ms ease;
}

.showcase-fade-enter-from,
.showcase-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.faq-collapse-enter-active,
.faq-collapse-leave-active {
  overflow: hidden;
  transition: max-height 240ms ease, opacity 220ms ease, transform 220ms ease;
}

.faq-collapse-enter-from,
.faq-collapse-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-4px);
}

.faq-collapse-enter-to,
.faq-collapse-leave-from {
  max-height: 220px;
  opacity: 1;
  transform: translateY(0);
}

@keyframes mesh-drift {
  0% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  100% {
    transform: translate3d(-1.5%, 1.2%, 0) scale(1.04);
  }
}

@media (max-width: 1100px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .hero-copy {
    max-width: 44rem;
    margin: 0 auto;
    text-align: center;
  }

  .hero-actions,
  .hero-points {
    justify-content: center;
  }

  .workflow-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .showcase-stage {
    grid-template-columns: 1fr;
  }

  .showcase-copy {
    max-width: 44rem;
  }
}

@media (max-width: 1024px) {
  .stats,
  .testimonial-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .comparison-grid {
    grid-template-columns: 1fr;
  }

  .comparison-divider {
    flex-direction: row;
    min-width: 0;
  }

  .comparison-divider-line {
    width: 100%;
    height: 1px;
    min-height: 0;
    min-width: 2.5rem;
    background: linear-gradient(90deg, transparent, var(--theme-border-strong), transparent);
  }

  .comparison-divider-icon {
    transform: rotate(90deg);
  }

  .pricing-teaser-grid {
    grid-template-columns: 1fr;
  }

  .feature-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .pricing-teaser-bar {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 767px) {
  .about-page {
    padding: 2rem 1rem 5rem;
  }

  .section-shell {
    width: min(100%, calc(100% - 0.5rem));
  }

  .showcase-shell {
    padding: 1rem;
  }

  .hero {
    max-width: 100%;
    padding-top: 1rem;
  }

  .hero h1 {
    font-size: clamp(2rem, 9vw, 2.75rem);
    line-height: 1.06;
  }

  .kicker {
    max-width: 100%;
    justify-content: center;
    text-align: center;
    white-space: normal;
  }

  .hero-subtitle {
    max-width: 32rem;
    margin-left: auto;
    margin-right: auto;
  }

  .hero-actions {
    flex-direction: column;
    align-items: center;
  }

  .hero-float-card {
    display: none;
  }

  .hero-device-stage {
    min-height: 18rem;
  }

  .hero-image {
    width: min(100%, 31rem);
    right: -0%;
  }

  .workflow-grid,
  .testimonial-grid,
  .feature-strip {
    grid-template-columns: 1fr;
  }
  
  .stats{
    grid-template-columns: 1fr 1fr;
  }

  .showcase-frame {
    aspect-ratio: 4 / 4;
  }

  .showcase-tabs {
    flex-direction: column;
  }

  .showcase-tab {
    width: 100%;
    justify-content: flex-start;
  }

  .cta-card {
    padding: 1.3rem;
  }

  /* .hero-actions,
  .cta-actions {
    align-items: stretch;
  } */

  .btn {
    width: min(100%, 18rem);
  }

  .about-footer {
    justify-content: center;
    text-align: center;
  }

  .about-footer-links {
    justify-content: center;
  }
}

</style>
