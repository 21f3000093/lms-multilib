<template>
  <main class="about-page" ref="pageRoot">
    <div class="mesh-layer" aria-hidden="true"></div>

    <Transition name="sticky-cta">
      <div v-if="showStickyCta" class="sticky-cta-bar">
        <div class="sticky-cta-copy">
          <p class="sticky-cta-kicker">Smart Library App</p>
          <strong>Run students, seats, billing, and reminders from one workspace.</strong>
        </div>
        <div class="sticky-cta-actions">
          <router-link class="btn btn-solid magnetic" to="/signup" @mousemove="onMagneticMove" @mouseleave="onMagneticLeave">
            Start Free
          </router-link>
          <router-link class="btn btn-ghost magnetic" to="/pricing-plans" @mousemove="onMagneticMove" @mouseleave="onMagneticLeave">
            View Pricing
          </router-link>
        </div>
      </div>
    </Transition>

    <section ref="heroSection" class="hero section-shell">
      <div class="hero-copy reveal" data-stagger="0">
        <p class="kicker">Run your library from one calmer workspace</p>
        <h1>
          The <span class="gradient-text">digital operating system</span>
          for modern study centers
        </h1>
        <p class="hero-subtitle">
          Smart Library App helps library owners and admins register students, assign seats, collect fees, send reminders,
          and monitor daily operations without juggling notebooks, spreadsheets, and manual follow-ups.
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

    </section>

    <section class="comparison section-shell">
      <header class="section-header reveal" data-stagger="0">
        <h2>The Transition: From Manual to Digital</h2>
        <p>See how Smart Library App replaces scattered, time-heavy admin work with one connected operating workflow.</p>
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
    </section>

    <section class="features section-shell">
      <header class="section-header reveal" data-stagger="0">
        <h2>Everything your team needs to run the library without manual chaos</h2>
        <p>From admissions to reminders to collections, every workflow is designed to keep operations visible, faster, and easier to trust.</p>
      </header>

      <div class="bento-grid">
        <article
          v-for="feature in features"
          :key="feature.title"
          class="bento-card reveal"
          :class="feature.span"
          :data-stagger="feature.stagger"
        >
          <div class="icon-wrap">
            <component :is="feature.icon" class="feature-icon" aria-hidden="true" />
          </div>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
        </article>
      </div>
    </section>

    <section class="showcase section-shell">
      <header class="section-header reveal" data-stagger="0">
        <h2>See the product across the workflows your team uses every day</h2>
        <p>Switch between core pages below. Replace the placeholder screenshot sources with real product captures whenever you’re ready.</p>
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
            <div class="showcase-copy">
              <p class="showcase-kicker">{{ activeShowcase.label }}</p>
              <h3>{{ activeShowcase.title }}</h3>
              <p>{{ activeShowcase.description }}</p>
            </div>
            <div class="showcase-frame">
              <img :src="activeShowcase.src" :alt="activeShowcase.alt" class="showcase-image" />
            </div>
          </article>
        </Transition>
      </div>
    </section>

    <section class="workflow section-shell">
      <header class="section-header reveal" data-stagger="0">
        <h2>How the workflow comes together</h2>
        <p>Get started quickly and keep the whole library team aligned in four simple steps.</p>
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

    <section class="stats section-shell reveal" data-stagger="0">
      <article v-for="item in stats" :key="item.label" class="stat-card reveal" :data-stagger="item.stagger">
        <p class="stat-value">{{ item.value }}</p>
        <p class="stat-label">{{ item.label }}</p>
      </article>
    </section>

    <section class="testimonials section-shell">
      <header class="section-header reveal" data-stagger="0">
        <h2>What library teams say after switching</h2>
        <p>These placeholder testimonials show the kind of proof and trust layer the landing page is designed to support.</p>
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
        <p>Start at ₹9 per seat per month, reduce your monthly equivalent with longer billing cycles, and unlock bonus months on eligible first purchases.</p>
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
        <p>Use this accordion to answer the objections and product questions visitors usually have before signing up.</p>
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
        <h2>Launch one workspace for students, seats, collections, reminders, and growth.</h2>
        <p>
          Replace fragmented admin work with one secure system your team can use every day.
        </p>

        <div class="cta-actions">
          <router-link class="btn btn-solid magnetic" to="/signup" @mousemove="onMagneticMove" @mouseleave="onMagneticLeave">
            Create Library Account
          </router-link>
          <router-link class="btn btn-ghost magnetic" to="/pricing-plans" @mousemove="onMagneticMove" @mouseleave="onMagneticLeave">
            View Pricing
          </router-link>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import {
  ArrowRight,
  Armchair,
  BadgeCheck,
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
const heroSection = ref(null)
const showStickyCta = ref(false)
const activeShowcaseKey = ref('dashboard')
const openFaqIndex = ref(0)

let revealObserver = null
let heroObserver = null

const createPlaceholderImage = (title, subtitle) => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1400 900" role="img" aria-label="${title}">
      <defs>
        <linearGradient id="bg" x1="0%" x2="100%" y1="0%" y2="100%">
          <stop offset="0%" stop-color="#0f172a" />
          <stop offset="50%" stop-color="#0b1220" />
          <stop offset="100%" stop-color="#111827" />
        </linearGradient>
        <linearGradient id="accent" x1="0%" x2="100%" y1="0%" y2="0%">
          <stop offset="0%" stop-color="#0ea5e9" />
          <stop offset="100%" stop-color="#2563eb" />
        </linearGradient>
      </defs>
      <rect width="1400" height="900" rx="32" fill="url(#bg)" />
      <rect x="44" y="44" width="1312" height="812" rx="28" fill="rgba(15, 23, 42, 0.82)" stroke="rgba(148, 163, 184, 0.18)" />
      <rect x="82" y="86" width="280" height="728" rx="24" fill="rgba(15, 23, 42, 0.95)" stroke="rgba(148, 163, 184, 0.12)" />
      <rect x="398" y="86" width="916" height="96" rx="24" fill="rgba(255,255,255,0.06)" />
      <rect x="430" y="118" width="300" height="18" rx="9" fill="url(#accent)" />
      <rect x="430" y="148" width="220" height="12" rx="6" fill="rgba(226,232,240,0.32)" />
      <rect x="398" y="214" width="284" height="150" rx="24" fill="rgba(255,255,255,0.05)" />
      <rect x="714" y="214" width="284" height="150" rx="24" fill="rgba(255,255,255,0.05)" />
      <rect x="1030" y="214" width="284" height="150" rx="24" fill="rgba(255,255,255,0.05)" />
      <rect x="398" y="398" width="450" height="380" rx="26" fill="rgba(255,255,255,0.05)" />
      <rect x="880" y="398" width="434" height="380" rx="26" fill="rgba(14,165,233,0.10)" stroke="rgba(37,99,235,0.30)" />
      <rect x="438" y="438" width="180" height="14" rx="7" fill="rgba(226,232,240,0.82)" />
      <rect x="438" y="470" width="250" height="12" rx="6" fill="rgba(148,163,184,0.48)" />
      <rect x="438" y="530" width="370" height="18" rx="9" fill="rgba(255,255,255,0.08)" />
      <rect x="438" y="566" width="330" height="18" rx="9" fill="rgba(255,255,255,0.08)" />
      <rect x="438" y="602" width="280" height="18" rx="9" fill="rgba(255,255,255,0.08)" />
      <rect x="920" y="438" width="210" height="14" rx="7" fill="rgba(226,232,240,0.82)" />
      <rect x="920" y="470" width="320" height="12" rx="6" fill="rgba(148,163,184,0.48)" />
      <rect x="920" y="530" width="334" height="18" rx="9" fill="rgba(255,255,255,0.08)" />
      <rect x="920" y="566" width="284" height="18" rx="9" fill="rgba(255,255,255,0.08)" />
      <rect x="920" y="602" width="248" height="18" rx="9" fill="rgba(255,255,255,0.08)" />
      <text x="700" y="835" fill="#e2e8f0" font-size="42" font-family="Inter, Arial, sans-serif" text-anchor="middle" font-weight="700">${title}</text>
      <text x="700" y="870" fill="#94a3b8" font-size="24" font-family="Inter, Arial, sans-serif" text-anchor="middle">${subtitle}</text>
    </svg>
  `

  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`
}

const heroPoints = [
  { icon: BadgeCheck, label: 'Google sign-in onboarding', stagger: 2 },
  { icon: MessageSquare, label: 'WhatsApp reminder workflows', stagger: 3 },
  { icon: ReceiptText, label: 'Receipt-ready payment records', stagger: 4 },
]

const stats = [
  { value: '50+', label: 'libraries already operating digitally', stagger: 1 },
  { value: '9k+', label: 'student records managed on platform', stagger: 2 },
  { value: '35%', label: 'faster admin follow-ups for daily ops', stagger: 3 },
  { value: '1', label: 'connected workspace for seats, fees, and reminders', stagger: 4 },
]

const testimonials = [
  {
    name: 'Aarav Jain',
    library: 'Green Valley Library',
    quote: 'We cut manual follow-up time dramatically because seats, collections, and reminders now live in one place.',
    stagger: 1,
  },
  {
    name: 'Neha Sharma',
    library: 'Scholars Study Hub',
    quote: 'The dashboard gives our team clarity every morning. We no longer guess which seats are free or which fees are pending.',
    stagger: 2,
  },
  {
    name: 'Rohit Verma',
    library: 'Focus Point Reading Room',
    quote: 'Receipts and payment history are much easier to manage now. Parents and students get answers faster, and our staff does too.',
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
    title: 'See every seat and shift live',
    description: 'Know exactly which seats are occupied across shifts before assigning or moving students.',
    span: 'span-2-rows',
    stagger: 1,
  },
  {
    icon: Users,
    title: 'Register and place students without spreadsheet confusion',
    description: 'Capture student details, assign seats, and keep profiles updated from one admissions flow.',
    span: 'span-2-cols',
    stagger: 2,
  },
  {
    icon: CreditCard,
    title: 'Keep fees, receipts, and payment history organized',
    description: 'Track monthly billing, mark payments, and share receipts without scattered manual records.',
    span: '',
    stagger: 3,
  },
  {
    icon: MessageSquare,
    title: 'Follow up instantly instead of manually chasing dues',
    description: 'Run reminder workflows through WhatsApp and keep fee follow-ups fast and consistent.',
    span: '',
    stagger: 4,
  },
  {
    icon: BarChart3,
    title: 'Monitor occupancy, collections, and growth at a glance',
    description: 'Use dashboards and trends to make better day-to-day decisions without waiting on reports.',
    span: 'span-2-cols',
    stagger: 5,
  },
  {
    icon: ShieldCheck,
    title: 'Keep library data safe and secure',
    description: 'Store student, payment, and seat records in one protected system instead of risking errors across scattered manual tools.',
    span: '',
    stagger: 6,
  },
]

const showcaseTabs = [
  {
    key: 'dashboard',
    label: 'Dashboard',
    title: 'Collections, occupancy, and action items in one glance',
    description: 'Use your dashboard to see revenue health, occupied seats, pending work, and trend signals before the day gets busy.',
    alt: 'Placeholder dashboard screenshot for Smart Library App',
    src: createPlaceholderImage('Dashboard View', 'Replace with your real dashboard screenshot'),
  },
  {
    key: 'students',
    label: 'Students',
    title: 'Student records that stay organized and searchable',
    description: 'Keep admissions, contact details, seat allocation, and payment history connected to each student profile.',
    alt: 'Placeholder students screenshot for Smart Library App',
    src: createPlaceholderImage('Students View', 'Replace with your real student list screenshot'),
  },
  {
    key: 'seats',
    label: 'Seats',
    title: 'Live seat visibility by shift',
    description: 'Know what is occupied, what is available, and what can be assigned before staff spend time checking manually.',
    alt: 'Placeholder seat map screenshot for Smart Library App',
    src: createPlaceholderImage('Seat Map View', 'Replace with your real seat map screenshot'),
  },
  {
    key: 'payments',
    label: 'Payments',
    title: 'Monthly fee control and receipt-ready records',
    description: 'Track who has paid, who is pending, and what receipts are ready to share without fragmented records.',
    alt: 'Placeholder payments screenshot for Smart Library App',
    src: createPlaceholderImage('Payments View', 'Replace with your real monthly payments screenshot'),
  },
  {
    key: 'reminders',
    label: 'Reminders',
    title: 'Reminder workflows that save follow-up time',
    description: 'Move from manual chase-ups to ready-to-send fee reminders that keep collections moving consistently.',
    alt: 'Placeholder reminders screenshot for Smart Library App',
    src: createPlaceholderImage('Reminders View', 'Replace with your real reminders screenshot'),
  },
]

const activeShowcase = computed(() => showcaseTabs.find((tab) => tab.key === activeShowcaseKey.value) || showcaseTabs[0])

const workflowSteps = [
  {
    step: '01',
    icon: UserPlus,
    title: 'Create your library account',
    description: 'Start your workspace, verify ownership, and get your library ready for daily operations.',
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
    answer: 'The app uses authenticated access, role-based controls, and structured records so library data stays organized and available only to the right users.',
  },
  {
    question: 'Is there a trial period before I commit?',
    answer: 'Yes. The product supports a self-serve signup flow and trial-first onboarding so you can evaluate the workflow before making a longer commitment.',
  },
  {
    question: 'Can this support multi-branch or growing operations?',
    answer: 'Yes. The platform is designed for growing library networks with superadmin oversight, standardized workflows, and pricing that scales with usage.',
  },
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

  heroObserver = new IntersectionObserver(
    (entries) => {
      const [entry] = entries
      showStickyCta.value = !entry.isIntersecting
    },
    {
      threshold: 0.08,
      rootMargin: '0px 0px -12% 0px',
    }
  )

  if (heroSection.value) {
    heroObserver.observe(heroSection.value)
  }
})

onBeforeUnmount(() => {
  revealObserver?.disconnect()
  revealObserver = null
  heroObserver?.disconnect()
  heroObserver = null
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

.sticky-cta-bar {
  position: fixed;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1200;
  width: min(1080px, calc(100% - 2rem));
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.8rem 1rem;
  border-radius: 18px;
  border: 1px solid var(--theme-border-strong);
  background: var(--theme-nav-surface-strong);
  box-shadow: var(--theme-shadow-elevated);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.sticky-cta-kicker {
  margin: 0;
  color: var(--theme-text-secondary);
  font-size: 0.76rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.sticky-cta-copy strong {
  display: block;
  margin-top: 0.22rem;
  font-size: 0.92rem;
}

.sticky-cta-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.hero {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.4rem;
  align-items: start;
  padding-top: 2rem;
  max-width: 780px;
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
  font-size: clamp(2.4rem, 6vw, 5.1rem);
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

.hero-actions,
.cta-actions {
  margin-top: 1.7rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
}

.hero-points {
  margin-top: 1.15rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
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
.features,
.comparison,
.showcase,
.faq,
.cta {
  margin-top: 3rem;
}

.stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.9rem;
}

.glass-card,
.stat-card,
.bento-card,
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

.bento-grid {
  margin-top: 1.3rem;
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  grid-auto-rows: minmax(150px, auto);
  gap: 0.9rem;
}

.bento-card {
  position: relative;
  overflow: hidden;
  border-radius: 18px;
  padding: 1.15rem;
  grid-column: span 4;
  transition: transform 240ms ease, border-color 240ms ease, box-shadow 240ms ease;
}

.bento-card::before {
  content: '';
  position: absolute;
  inset: -35% auto auto -15%;
  width: 11rem;
  height: 11rem;
  background: radial-gradient(circle, rgba(34, 211, 238, 0.2), transparent 70%);
  opacity: 0;
  transition: opacity 260ms ease;
  pointer-events: none;
}

.bento-card:hover {
  transform: translateY(-4px);
  border-color: var(--theme-brand-border);
  box-shadow: var(--theme-shadow-soft);
}

.bento-card:hover::before {
  opacity: 1;
}

.bento-card h3,
.workflow-card h3,
.teaser-card h3,
.showcase-copy h3,
.faq-trigger {
  margin: 0.65rem 0 0;
  font-size: 1.15rem;
}

.bento-card p {
  margin: 0.55rem 0 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

.icon-wrap {
  width: 2.7rem;
  height: 2.7rem;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: var(--theme-surface-soft-strong);
  border: 1px solid var(--theme-border-soft);
}

.feature-icon,
.workflow-icon,
.teaser-icon {
  width: 1.3rem;
  height: 1.3rem;
  color: var(--theme-text-soft);
  stroke-width: 2.1;
}

.span-2-cols {
  grid-column: span 8;
}

.span-2-rows {
  grid-column: span 4;
  grid-row: span 2;
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
  grid-template-columns: minmax(0, 0.95fr) minmax(0, 1.05fr);
  gap: 1.1rem;
  align-items: center;
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
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid var(--theme-border-soft);
  background: var(--theme-panel-strong);
  box-shadow: var(--theme-shadow-soft);
}

.showcase-image {
  display: block;
  width: 100%;
  height: auto;
  aspect-ratio: 14 / 9;
  object-fit: cover;
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

.sticky-cta-enter-active,
.sticky-cta-leave-active,
.showcase-fade-enter-active,
.showcase-fade-leave-active {
  transition: opacity 220ms ease, transform 220ms ease;
}

.sticky-cta-enter-from,
.sticky-cta-leave-to,
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
  .workflow-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .showcase-stage {
    grid-template-columns: 1fr;
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

  .workflow-grid,
  .stats,
  .testimonial-grid {
    grid-template-columns: 1fr;
  }

  .showcase-tabs {
    flex-direction: column;
  }

  .showcase-tab {
    width: 100%;
    justify-content: flex-start;
  }

  .bento-grid {
    grid-template-columns: 1fr;
    grid-auto-rows: auto;
  }

  .bento-card,
  .span-2-cols,
  .span-2-rows {
    grid-column: span 1;
    grid-row: span 1;
  }

  .cta-card {
    padding: 1.3rem;
  }

  .hero-actions,
  .cta-actions,
  .sticky-cta-actions {
    align-items: stretch;
  }

  .btn {
    width: 100%;
  }
}

@media (max-width: 479px) {
  .sticky-cta-bar {
    display: none;
  }
}
</style>
