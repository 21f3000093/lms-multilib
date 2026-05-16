<template>
  <main class="privacy-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <!-- Top nav bar -->
    <nav class="top-nav" aria-label="Site navigation">
      <div class="top-nav-inner">
        <div class="top-nav-brand">
          <BookOpen class="brand-icon" aria-hidden="true" />
          <span>Smart Library App</span>
        </div>
        <div class="top-nav-links">
          <router-link class="nav-link" to="/">Home</router-link>
          <router-link class="nav-link" to="/pricing-plans">Pricing</router-link>
          <router-link class="btn btn-solid" to="/login">Go to App</router-link>
        </div>
      </div>
    </nav>

    <!-- Hero -->
    <section class="section-shell hero">
      <div class="hero-meta">
        <span class="kicker">Legal</span>
        <span class="kicker-divider" aria-hidden="true">·</span>
        <span class="last-updated">Last Updated: May 9, 2026</span>
      </div>
      <h1>Privacy Policy</h1>
      <p class="hero-subtitle">
        This Privacy Policy explains how Smart Library App collects, uses, secures, and processes
        information when you use our multi-library management platform.
      </p>
    </section>

    <!-- Two-column layout: sidebar ToC + content -->
    <div class="section-shell content-layout">

      <!-- Sticky sidebar table of contents -->
      <aside class="toc-sidebar" aria-label="Table of contents">
        <p class="toc-heading">On this page</p>
        <nav>
          <ol class="toc-list">
            <li v-for="section in sections" :key="section.id">
              <a
                :href="`#${section.id}`"
                class="toc-link"
                :class="{ 'is-active': activeSection === section.id }"
                @click.prevent="scrollToSection(section.id)"
              >
                <span class="toc-num">{{ section.num }}</span>
                <span>{{ section.title }}</span>
              </a>
            </li>
          </ol>
        </nav>

        <div class="toc-contact-box">
          <ShieldCheck class="toc-contact-icon" aria-hidden="true" />
          <p>Questions about this policy?</p>
          <a href="mailto:support@smartlibraryapp.in" class="toc-contact-link">
            support@smartlibraryapp.in
          </a>
        </div>
      </aside>

      <!-- Policy content -->
      <article class="policy-content" aria-label="Smart Library App privacy policy">

        <section
          v-for="section in sections"
          :key="section.id"
          :id="section.id"
          class="policy-section"
          :aria-labelledby="`${section.id}-heading`"
        >
          <div class="section-num-badge">{{ section.num }}</div>
          <h2 :id="`${section.id}-heading`">{{ section.title }}</h2>

          <div class="section-body" v-html="section.body"></div>
        </section>

        <!-- Contact footer inside content -->
        <section id="contact" class="policy-section contact-section" aria-labelledby="contact-heading">
          <div class="section-num-badge">{{ sections.length + 1 }}</div>
          <h2 id="contact-heading">Contact Information</h2>
          <p>For privacy-related questions or requests, reach out to us directly:</p>
          <div class="contact-grid">
            <a href="mailto:support@smartlibraryapp.in" class="contact-card">
              <Mail class="contact-card-icon" aria-hidden="true" />
              <div>
                <strong>Email</strong>
                <span>support@smartlibraryapp.in</span>
              </div>
            </a>
            <div class="contact-card">
              <Globe class="contact-card-icon" aria-hidden="true" />
              <div>
                <strong>Platform</strong>
                <span>smartlibraryapp.in</span>
              </div>
            </div>
            <div class="contact-card">
              <Server class="contact-card-icon" aria-hidden="true" />
              <div>
                <strong>API</strong>
                <span>api.smartlibraryapp.in</span>
              </div>
            </div>
          </div>
        </section>

      </article>
    </div>

    <!-- Footer -->
    <footer class="page-footer">
      <div class="section-shell footer-inner">
        <p>© {{ currentYear }} Smart Library App. All rights reserved.</p>
        <div class="footer-links">
          <router-link to="/">Home</router-link>
          <router-link to="/pricing-plans">Pricing</router-link>
          <router-link to="/login">Login</router-link>
        </div>
      </div>
    </footer>

    <!-- Mobile ToC toggle -->
    <button
      type="button"
      class="mobile-toc-btn"
      :class="{ 'is-open': mobileTocOpen }"
      @click="mobileTocOpen = !mobileTocOpen"
      aria-label="Toggle table of contents"
    >
      <List class="mobile-toc-icon" aria-hidden="true" />
      <span>Contents</span>
      <ChevronUp class="mobile-toc-chevron" :class="{ 'is-open': mobileTocOpen }" aria-hidden="true" />
    </button>

    <!-- Mobile ToC drawer -->
    <Transition name="mobile-toc">
      <div v-if="mobileTocOpen" class="mobile-toc-drawer" role="dialog" aria-label="Table of contents">
        <p class="toc-heading">On this page</p>
        <ol class="toc-list">
          <li v-for="section in sections" :key="section.id">
            <a
              :href="`#${section.id}`"
              class="toc-link"
              :class="{ 'is-active': activeSection === section.id }"
              @click.prevent="scrollToSection(section.id); mobileTocOpen = false"
            >
              <span class="toc-num">{{ section.num }}</span>
              <span>{{ section.title }}</span>
            </a>
          </li>
          <li>
            <a
              href="#contact"
              class="toc-link"
              @click.prevent="scrollToSection('contact'); mobileTocOpen = false"
            >
              <span class="toc-num">{{ sections.length + 1 }}</span>
              <span>Contact Information</span>
            </a>
          </li>
        </ol>
      </div>
    </Transition>
  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { BookOpen, ChevronUp, Globe, List, Mail, Server, ShieldCheck } from 'lucide-vue-next'

const currentYear = computed(() => new Date().getFullYear())
const activeSection = ref('')
const mobileTocOpen = ref(false)

const sections = [
  {
    id: 'information-collect',
    num: '01',
    title: 'Information We Collect',
    body: `
      <p>We collect information required to operate library workflows, including:</p>
      <ul>
        <li>Admin account details such as name, mobile number, email, and role.</li>
        <li>Library profile data such as library name, address, seat capacity, and operating settings.</li>
        <li>Student data such as name, contact number, seat preferences, attendance, and fee history.</li>
        <li>Operational analytics such as occupancy, collections, reminders sent, and activity usage.</li>
        <li>Technical metadata such as browser/device info, app version, and diagnostic logs.</li>
      </ul>
    `,
  },
  {
    id: 'use-information',
    num: '02',
    title: 'How We Use Information',
    body: `
      <p>We use your data to:</p>
      <ul>
        <li>Provide and maintain student management, seat allocation, fee tracking, and attendance features.</li>
        <li>Enable reminders, payment workflows, receipts, and dashboard analytics.</li>
        <li>Improve platform reliability, fraud prevention, and product performance.</li>
        <li>Provide support, troubleshooting, and service communications.</li>
      </ul>
      <p class="callout">We do not sell personal data.</p>
    `,
  },
  {
    id: 'auth-security',
    num: '03',
    title: 'Authentication and Account Security',
    body: `
      <p>Access to Smart Library App is role-based. Admin authentication uses secure session and token controls. Credentials and authorization checks are used to protect restricted features and data boundaries across libraries.</p>
    `,
  },
  {
    id: 'payment-data',
    num: '04',
    title: 'Payment and Fee Data',
    body: `
      <p>We process billing and fee records to support subscription plans, collections, and receipts. Payment events and references are stored for reconciliation and audit history. Sensitive payment details are handled via trusted payment integrations and are not sold or repurposed by us.</p>
    `,
  },
  {
    id: 'whatsapp-usage',
    num: '05',
    title: 'WhatsApp Reminder Usage',
    body: `
      <p>Smart Library App can send reminder messages on behalf of authorized library admins. Message content is generated from configured student and fee records. Admins are responsible for ensuring they have appropriate communication consent from their students.</p>
    `,
  },
  {
    id: 'cookies-storage',
    num: '06',
    title: 'Cookies and Local Storage',
    body: `
      <p>We use browser storage and similar technologies for session continuity, authentication state, preferences, and performance. This helps keep users signed in securely and improves app responsiveness.</p>
    `,
  },
  {
    id: 'pwa-caching',
    num: '07',
    title: 'PWA and Offline Data Caching',
    body: `
      <p>Smart Library App operates as a Progressive Web App and Android Trusted Web Activity. For PWA functionality, service workers may cache limited offline assets such as static files and app shell resources to improve load speed and resilience.</p>
    `,
  },
  {
    id: 'data-security',
    num: '08',
    title: 'Data Security',
    body: `
      <p>We use industry-standard safeguards including HTTPS encryption in transit between clients and servers. We apply access controls and monitoring practices designed to reduce unauthorized access, disclosure, or misuse.</p>
    `,
  },
  {
    id: 'third-party',
    num: '09',
    title: 'Third-Party Services',
    body: `
      <p>We may rely on third-party services for hosting, notifications, analytics, and payment processing. These providers process data under their own terms and applicable laws, and only to the extent required for service delivery.</p>
    `,
  },
  {
    id: 'child-privacy',
    num: '10',
    title: "Children's Privacy",
    body: `
      <p>Smart Library App is designed for use by library owners and administrators. It is not intended for direct use by children. Library admins are responsible for lawful data handling within their institution context.</p>
    `,
  },
  {
    id: 'user-rights',
    num: '11',
    title: 'User Rights',
    body: `
      <p>Subject to applicable law, users may request to:</p>
      <ul>
        <li>Access or correct account information.</li>
        <li>Request deletion of eligible records.</li>
        <li>Raise concerns related to privacy or security practices.</li>
      </ul>
    `,
  },
  {
    id: 'policy-changes',
    num: '12',
    title: 'Changes to This Policy',
    body: `
      <p>We may update this policy from time to time to reflect legal, technical, or product changes. Updated versions will be posted at this page with a revised "Last Updated" date.</p>
    `,
  },
]

function scrollToSection(id) {
  const el = document.getElementById(id)
  if (!el) return
  const offset = 80
  const top = el.getBoundingClientRect().top + window.scrollY - offset
  window.scrollTo({ top, behavior: 'smooth' })
}

let scrollObserver = null

onMounted(() => {
  const targets = document.querySelectorAll('.policy-section')

  scrollObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          activeSection.value = entry.target.id
        }
      })
    },
    {
      rootMargin: '-20% 0px -60% 0px',
      threshold: 0,
    }
  )

  targets.forEach((t) => scrollObserver?.observe(t))
})

onBeforeUnmount(() => {
  scrollObserver?.disconnect()
})
</script>

<style scoped>
/* ── Base ── */
.privacy-page {
  --surface: var(--theme-surface);
  --surface-border: var(--theme-surface-border);
  --text-primary: var(--theme-text-primary);
  --text-secondary: var(--theme-text-secondary);

  min-height: 100vh;
  position: relative;
  color: var(--text-primary);
  isolation: isolate;
  overflow-x: hidden;
  font-family: Inter, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}

.mesh-layer {
  position: fixed;
  inset: 0;
  z-index: -1;
  background: var(--theme-mesh-background);
  filter: saturate(115%);
  animation: mesh-drift 18s ease-in-out infinite alternate;
}

.section-shell {
  width: min(1200px, calc(100% - 3rem));
  margin: 0 auto;
}

/* ── Top Nav ── */
.top-nav {
  position: sticky;
  top: 0;
  z-index: 200;
  border-bottom: 1px solid var(--theme-border-soft);
  background: var(--theme-nav-surface-strong, var(--theme-surface));
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.top-nav-inner {
  width: min(1200px, calc(100% - 3rem));
  margin: 0 auto;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.top-nav-brand {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--theme-text-primary);
  text-decoration: none;
}

.brand-icon {
  width: 1.1rem;
  height: 1.1rem;
  color: var(--theme-brand-a);
}

.top-nav-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  color: var(--theme-text-secondary);
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: color 150ms ease;
}

.nav-link:hover {
  color: var(--theme-text-primary);
}

/* ── Buttons ── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 36px;
  padding: 0.45rem 1rem;
  border-radius: 10px;
  border: 1px solid transparent;
  font-weight: 600;
  font-size: 0.88rem;
  text-decoration: none;
  cursor: pointer;
  transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
}

.btn-solid {
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
  color: var(--theme-brand-on);
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.18);
}

.btn-solid:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.26);
}

/* ── Hero ── */
.hero {
  padding: 3rem 0 2rem;
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  margin-bottom: 1rem;
}

.kicker {
  display: inline-flex;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  border: 1px solid var(--theme-border);
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--theme-text-soft);
  background: var(--theme-surface-soft);
  font-weight: 600;
}

.kicker-divider {
  color: var(--theme-text-muted);
  font-size: 0.9rem;
}

.last-updated {
  color: var(--theme-text-muted);
  font-size: 0.84rem;
  font-weight: 500;
}

.hero h1 {
  margin: 0 0 0.9rem;
  font-size: clamp(2.2rem, 5vw, 3.4rem);
  line-height: 1.04;
  letter-spacing: -0.03em;
  color: var(--theme-text-strong, var(--text-primary));
}

.hero-subtitle {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
  max-width: 64ch;
  font-size: 1.02rem;
}

/* ── Two-column layout ── */
.content-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 2.5rem;
  align-items: start;
  padding-bottom: 4rem;
}

/* ── Sidebar ToC ── */
.toc-sidebar {
  position: sticky;
  top: 72px;
  max-height: calc(100vh - 88px);
  overflow-y: auto;
  scrollbar-width: none;
  padding-bottom: 1rem;
}

.toc-sidebar::-webkit-scrollbar {
  display: none;
}

.toc-heading {
  margin: 0 0 0.75rem;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--theme-text-muted);
}

.toc-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.15rem;
}

.toc-link {
  display: flex;
  align-items: baseline;
  gap: 0.55rem;
  padding: 0.42rem 0.65rem;
  border-radius: 8px;
  text-decoration: none;
  color: var(--theme-text-secondary);
  font-size: 0.84rem;
  font-weight: 500;
  line-height: 1.4;
  transition: background 140ms ease, color 140ms ease;
  border-left: 2px solid transparent;
}

.toc-link:hover {
  background: var(--theme-surface-soft);
  color: var(--theme-text-primary);
}

.toc-link.is-active {
  background: var(--theme-brand-soft);
  color: var(--theme-brand-pill-text);
  border-left-color: var(--theme-brand-a);
  font-weight: 600;
}

.toc-num {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--theme-text-muted);
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
  min-width: 1.6rem;
}

.toc-link.is-active .toc-num {
  color: var(--theme-brand-pill-text);
}

.toc-contact-box {
  margin-top: 1.5rem;
  padding: 0.85rem;
  border-radius: 12px;
  border: 1px solid var(--theme-brand-border);
  background: var(--theme-brand-soft);
  display: grid;
  gap: 0.35rem;
}

.toc-contact-icon {
  width: 1rem;
  height: 1rem;
  color: var(--theme-brand-pill-text);
}

.toc-contact-box p {
  margin: 0;
  font-size: 0.82rem;
  color: var(--theme-text-soft);
  line-height: 1.4;
}

.toc-contact-link {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--theme-brand-pill-text);
  text-decoration: none;
  word-break: break-all;
}

.toc-contact-link:hover {
  text-decoration: underline;
}

/* ── Policy sections ── */
.policy-content {
  display: grid;
  gap: 0;
  min-width: 0;
}

.policy-section {
  padding: 2rem 0;
  border-bottom: 1px solid var(--theme-border-soft);
  scroll-margin-top: 72px;
}

.policy-section:last-child {
  border-bottom: none;
}

.section-num-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: var(--theme-brand-pill-text);
  background: var(--theme-brand-soft);
  border: 1px solid var(--theme-brand-border);
  border-radius: 6px;
  padding: 0.18rem 0.5rem;
  margin-bottom: 0.75rem;
}

.policy-section h2 {
  margin: 0 0 1rem;
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.015em;
  color: var(--theme-text-strong, var(--text-primary));
  line-height: 1.3;
}

/* Rich text inside v-html */
.section-body :deep(p) {
  margin: 0 0 0.85rem;
  color: var(--theme-text-soft);
  line-height: 1.75;
  font-size: 0.95rem;
}

.section-body :deep(p:last-child) {
  margin-bottom: 0;
}

.section-body :deep(ul) {
  margin: 0 0 0.85rem;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.5rem;
}

.section-body :deep(li) {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  color: var(--theme-text-soft);
  line-height: 1.65;
  font-size: 0.95rem;
  padding-left: 0;
}

.section-body :deep(li)::before {
  content: '';
  display: block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--theme-brand-a);
  margin-top: 0.55rem;
  flex-shrink: 0;
}

.section-body :deep(.callout) {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.85rem;
  padding: 0.65rem 1rem;
  border-radius: 10px;
  border: 1px solid var(--theme-success-border);
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
  font-weight: 600;
  font-size: 0.9rem;
}

/* ── Contact section ── */
.contact-section > p {
  margin: 0 0 1.2rem;
  color: var(--theme-text-soft);
  line-height: 1.7;
  font-size: 0.95rem;
}

.contact-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.8rem;
}

.contact-card {
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
  padding: 0.9rem;
  border-radius: 12px;
  border: 1px solid var(--theme-border-soft);
  background: var(--theme-panel-soft);
  text-decoration: none;
  transition: border-color 160ms ease, background 160ms ease;
}

a.contact-card:hover {
  border-color: var(--theme-brand-border);
  background: var(--theme-brand-soft);
}

.contact-card-icon {
  width: 1.1rem;
  height: 1.1rem;
  color: var(--theme-brand-pill-text);
  margin-top: 0.1rem;
  flex-shrink: 0;
}

.contact-card strong {
  display: block;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--theme-text-primary);
  margin-bottom: 0.2rem;
}

.contact-card span {
  font-size: 0.82rem;
  color: var(--theme-text-secondary);
  word-break: break-all;
}

/* ── Footer ── */
.page-footer {
  border-top: 1px solid var(--theme-border-soft);
  background: var(--theme-surface-soft);
  padding: 1.25rem 0;
}

.footer-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.page-footer p {
  margin: 0;
  font-size: 0.84rem;
  color: var(--theme-text-muted);
}

.footer-links {
  display: flex;
  gap: 1.25rem;
}

.footer-links a {
  font-size: 0.84rem;
  color: var(--theme-text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: color 140ms ease;
}

.footer-links a:hover {
  color: var(--theme-brand-pill-text);
}

/* ── Mobile ToC button ── */
.mobile-toc-btn {
  display: none;
  position: fixed;
  bottom: 5rem;
  right: 1rem;
  z-index: 300;
  align-items: center;
  gap: 0.45rem;
  padding: 0.62rem 0.9rem;
  border-radius: 999px;
  border: 1px solid var(--theme-border-strong);
  background: var(--theme-surface);
  color: var(--theme-text-primary);
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: var(--theme-shadow-elevated);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.mobile-toc-icon {
  width: 1rem;
  height: 1rem;
}

.mobile-toc-chevron {
  width: 0.9rem;
  height: 0.9rem;
  transition: transform 220ms ease;
}

.mobile-toc-chevron.is-open {
  transform: rotate(180deg);
}

/* ── Mobile ToC drawer ── */
.mobile-toc-drawer {
  display: none;
  position: fixed;
  bottom: 9rem;
  right: 1rem;
  z-index: 290;
  width: min(320px, calc(100vw - 2rem));
  max-height: 55vh;
  overflow-y: auto;
  border-radius: 16px;
  border: 1px solid var(--theme-border-strong);
  background: var(--theme-surface);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  padding: 1rem;
  box-shadow: var(--theme-shadow-elevated);
}

/* Transitions */
.mobile-toc-enter-active,
.mobile-toc-leave-active {
  transition: opacity 200ms ease, transform 200ms ease;
}

.mobile-toc-enter-from,
.mobile-toc-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* ── Keyframes ── */
@keyframes mesh-drift {
  0% { transform: translate3d(0, 0, 0) scale(1); }
  100% { transform: translate3d(-1.5%, 1.2%, 0) scale(1.04); }
}

/* ── Responsive ── */
@media (max-width: 1024px) {
  .content-layout {
    grid-template-columns: 200px 1fr;
    gap: 1.8rem;
  }
}

@media (max-width: 767px) {
  .section-shell {
    width: min(100%, calc(100% - 1.5rem));
  }

  .top-nav-inner {
    width: calc(100% - 1.5rem);
  }

  .top-nav-links .nav-link {
    display: none;
  }

  .hero {
    padding: 1.75rem 0 1.25rem;
  }

  .hero h1 {
    font-size: clamp(1.9rem, 8vw, 2.6rem);
  }

  .hero-subtitle {
    font-size: 0.95rem;
  }

  /* Hide sidebar on mobile — use floating button instead */
  .content-layout {
    grid-template-columns: 1fr;
    gap: 0;
  }

  .toc-sidebar {
    display: none;
  }

  .mobile-toc-btn {
    display: flex;
  }

  .mobile-toc-drawer {
    display: block;
  }

  .policy-section {
    padding: 1.5rem 0;
  }

  .policy-section h2 {
    font-size: 1.1rem;
  }

  .contact-grid {
    grid-template-columns: 1fr;
  }

  .footer-inner {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.65rem;
  }

  .page-footer {
    padding-bottom: 6rem;
  }
}
</style>