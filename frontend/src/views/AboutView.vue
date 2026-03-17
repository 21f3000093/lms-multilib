<template>
  <main class="about-page" ref="pageRoot">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="hero section-shell">
      <div class="hero-copy reveal" data-stagger="0">
        <p class="kicker">Trusted By 100+ Libraries</p>
        <h1>
          The <span class="gradient-text">Operating System</span>
          for modern study centers
        </h1>
        <p class="hero-subtitle">
          Smart Library App helps you to manage students, seats, payments, and operations from one enterprise-grade dashboard.
        </p>

        <div class="hero-actions">
          <a 
            class="btn btn-solid magnetic" 
            href="https://wa.me/919024600138?text=Hi%20Shubham!%20I'd%20like%20to%20book%20a%20demo%20for%20the%20Library%20App." 
            target="_blank" 
            rel="noopener noreferrer"
            @mousemove="onMagneticMove" 
            @mouseleave="onMagneticLeave"
          >
            Book a Demo
          </a>
          <a class="btn btn-ghost magnetic" href="tel:+919024600138" @mousemove="onMagneticMove" @mouseleave="onMagneticLeave">
            Talk to Sales
          </a>
        </div>
      </div>

      <div class="hero-visual reveal" data-stagger="1">
        <div class="hero-orb floaty">
          <div class="orb-core">
            <BookOpen class="orb-icon" aria-hidden="true" />
          </div>
        </div>
      </div>
    </section>

    <section class="stats section-shell reveal" data-stagger="0">
      <article v-for="item in stats" :key="item.label" class="stat-card reveal" :data-stagger="item.stagger">
        <p class="stat-value">{{ item.value }}</p>
        <p class="stat-label">{{ item.label }}</p>
      </article>
    </section>

    <section class="features section-shell">
      <header class="section-header reveal" data-stagger="0">
        <h2>Built for scale, reliability, and predictable operations</h2>
        <p>Everything your admin team needs to run multi-library operations without workflow chaos.</p>
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

    <section class="cta section-shell reveal" data-stagger="1">
      <div class="cta-card">
        <p class="cta-kicker">Ready to scale faster?</p>
        <h2>Launch a unified workflow for your entire library network.</h2>
        <p>
          Replace fragmented processes with one secure platform for admin control, communication, and growth.
        </p>

        <div class="cta-actions">
          <a class="btn btn-solid magnetic" 
            href="https://wa.me/919024600138?text=Hi%20Shubham!%20I'd%20like%20to%20start%20a%20conversation%20about%20the%20Smart%20Library%20app." 
            target="_blank" 
            rel="noopener noreferrer"
            @mousemove="onMagneticMove" 
            @mouseleave="onMagneticLeave"
          >
            Start Conversation
          </a>
          <router-link class="btn btn-ghost magnetic" to="/pricing-plans" @mousemove="onMagneticMove" @mouseleave="onMagneticLeave">
            View Pricing
          </router-link>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import {
  Armchair,
  BarChart3,
  BookOpen,
  CreditCard,
  MessageSquare,
  ShieldCheck,
} from 'lucide-vue-next'

const pageRoot = ref(null)
let observer = null

const stats = [
  { value: '100%', label: 'Platform Uptime', stagger: 1 },
  { value: '9k+', label: 'Students Managed', stagger: 2 },
  { value: '50+', label: 'Libraries Enabled', stagger: 3 },
  { value: '35%', label: 'Faster Admin Ops', stagger: 4 },
]

const features = [
  {
    icon: Armchair,
    title: 'Live Seat Intelligence',
    description: 'Track seat occupancy by shift in real-time with clear utilization visibility.',
    span: 'span-2-rows',
    stagger: 1,
  },
  {
    icon: MessageSquare,
    title: 'Automated Messaging',
    description: 'Send reminders and important notices with template-driven WhatsApp workflows.',
    span: 'span-2-cols',
    stagger: 2,
  },
  {
    icon: CreditCard,
    title: 'Fee Collection Control',
    description: 'Centralize monthly payment tracking, due detection, and receipts.',
    span: '',
    stagger: 3,
  },
  {
    icon: BarChart3,
    title: 'Operator Analytics',
    description: 'Monitor trends, active students, and growth metrics at a glance.',
    span: '',
    stagger: 4,
  },
  {
    icon: ShieldCheck,
    title: 'Role-Based Governance',
    description: 'Separate superadmin and admin responsibilities with safer access boundaries.',
    span: 'span-2-cols',
    stagger: 5,
  },
]

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
      threshold: 0.18,
      rootMargin: '0px 0px -10% 0px',
    }
  )

  targets.forEach((target) => observer?.observe(target))
})

onBeforeUnmount(() => {
  observer?.disconnect()
  observer = null
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.about-page {
  --bg: #0f172a;
  --surface: rgba(148, 163, 184, 0.03);
  --surface-border: rgba(255, 255, 255, 0.03);
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --brand-a: #22d3ee;
  --brand-b: #3b82f6;

  position: relative;
  min-height: 100vh;
  padding: 2rem 2rem 4rem;
  color: var(--text-primary);
  background: var(--bg);
  font-family: Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  overflow: hidden;
  isolation: isolate;
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

.section-shell {
  width: min(1140px, calc(100% - 2rem));
  margin: 0 auto;
}

.hero {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 2.5rem;
  align-items: center;
  padding-top: 2rem;
}

.kicker,
.cta-kicker {
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
  font-size: clamp(2.4rem, 6vw, 5.2rem);
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
.cta-card p {
  margin: 1.1rem 0 0;
  /* max-width: 62ch; */
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
  justify-content: center;
}

.hero-visual {
  display: flex;
  justify-content: center;
}

.hero-orb {
  /* width: min(360px, 84vw); */
  aspect-ratio: 1;
  border-radius: 28px;
  /* border: 1px solid var(--surface-border); */
  /* background:
    linear-gradient(145deg, rgba(148, 163, 184, 0.14), rgba(148, 163, 184, 0.02)),
    rgba(148, 163, 184, 0.02); */
  backdrop-filter: blur(12px);
  display: grid;
  place-items: center;
  /* box-shadow: 0 26px 60px rgba(2, 6, 23, 0.45); */
}

.orb-core {
  width: 12rem;
  height: 12rem;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: radial-gradient(circle at 28% 22%, rgba(34, 211, 238, 0.5), rgba(30, 41, 59, 0.08));
  box-shadow:
    inset 0 0 30px rgba(226, 232, 240, 0.16),
    0 20px 40px rgba(34, 211, 238, 0.18);
}

.orb-icon {
  width: 3.4rem;
  height: 3.4rem;
  color: #e2e8f0;
  stroke-width: 1.8;
}

.stats {
  margin-top: 2rem;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.9rem;
}

.stat-card,
.bento-card,
.cta-card {
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

.features {
  margin-top: 3rem;
}

.section-header h2,
.cta-card h2 {
  margin: 0;
  font-size: clamp(1.5rem, 3.3vw, 2.4rem);
  letter-spacing: -0.02em;
  text-wrap: balance;
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
  border-color: rgba(34, 211, 238, 0.28);
  box-shadow: 0 20px 34px rgba(2, 6, 23, 0.42);
}

.bento-card:hover::before {
  opacity: 1;
}

.bento-card h3 {
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
  background: rgba(148, 163, 184, 0.14);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.feature-icon {
  width: 1.3rem;
  height: 1.3rem;
  color: #cbd5e1;
  stroke-width: 2.1;
}

.span-2-cols {
  grid-column: span 8;
}

.span-2-rows {
  grid-column: span 4;
  grid-row: span 2;
}

.cta {
  margin-top: 3rem;
  margin-bottom: 0.5rem;
}

.cta-card {
  border-radius: 22px;
  padding: 1.8rem;
  box-shadow: 0 20px 60px rgba(2, 6, 23, 0.45);
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
  background: linear-gradient(90deg, #0ea5e9, #3b82f6);
  color: #f8fafc;
  box-shadow: 0 14px 28px rgba(59, 130, 246, 0.28);
}

.btn-ghost {
  color: #e2e8f0;
  border-color: rgba(148, 163, 184, 0.4);
  background: rgba(148, 163, 184, 0.04);
}

.btn-ghost:hover {
  border-color: rgba(34, 211, 238, 0.42);
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

@media (max-width: 1024px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .hero-visual {
    order: -1;
  }

  .stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .about-page {
    padding: 2rem 1rem 5rem;
  }

  .orb-core {
    width: 9rem;
    height: 9rem;
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

  .stats {
    grid-template-columns: 1fr;
  }

  .cta-card {
    padding: 1.3rem;
  }
}
</style>
