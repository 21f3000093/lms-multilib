<template>
  <main class="privacy-page">
    <div class="mesh-layer" aria-hidden="true"></div>

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
      <div class="hero-nav">
        <router-link class="btn btn-ghost" to="/">← Back to Home</router-link>
        <router-link class="btn btn-ghost" to="/login">Go to Login</router-link>
      </div>
    </section>

    <!-- Two-column layout -->
    <div class="section-shell content-layout">

      <!-- Sticky sidebar ToC -->
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
            <li>
              <a
                href="#contact"
                class="toc-link"
                :class="{ 'is-active': activeSection === 'contact' }"
                @click.prevent="scrollToSection('contact')"
              >
                <span class="toc-num">{{ sections.length + 1 }}</span>
                <span>Contact Information</span>
              </a>
            </li>
          </ol>
        </nav>

        <div class="toc-contact-box">
          <ShieldCheck class="toc-contact-icon" aria-hidden="true" />
          <p>Privacy questions?</p>
          <a href="mailto:support@smartlibraryapp.in" class="toc-contact-link">
            support@smartlibraryapp.in
          </a>
        </div>
      </aside>

      <!-- Policy content -->
      <article class="policy-content" aria-label="Privacy policy content">

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

        <!-- Contact -->
        <section id="contact" class="policy-section" aria-labelledby="contact-heading">
          <div class="section-num-badge">{{ sections.length + 1 }}</div>
          <h2 id="contact-heading">Contact Information</h2>
          <p class="section-intro">For privacy-related questions or requests, reach out to us directly:</p>
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
          <router-link to="/about">About</router-link>
        </div>
      </div>
    </footer>

    <!-- Mobile floating ToC button -->
    <button
      type="button"
      class="mobile-toc-btn"
      @click="mobileTocOpen = !mobileTocOpen"
      :aria-expanded="mobileTocOpen"
      aria-label="Toggle table of contents"
    >
      <List class="mobile-toc-icon" aria-hidden="true" />
      <span>Contents</span>
      <ChevronDown
        class="mobile-toc-chevron"
        :class="{ 'is-open': mobileTocOpen }"
        aria-hidden="true"
      />
    </button>

    <!-- Mobile ToC drawer -->
    <Transition name="mobile-toc">
      <div v-if="mobileTocOpen" class="mobile-toc-drawer">
        <div class="mobile-toc-header">
          <p class="toc-heading">On this page</p>
          <button
            type="button"
            class="mobile-toc-close"
            @click="mobileTocOpen = false"
            aria-label="Close table of contents"
          >
            <X class="close-icon" aria-hidden="true" />
          </button>
        </div>
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
              :class="{ 'is-active': activeSection === 'contact' }"
              @click.prevent="scrollToSection('contact'); mobileTocOpen = false"
            >
              <span class="toc-num">{{ sections.length + 1 }}</span>
              <span>Contact Information</span>
            </a>
          </li>
        </ol>
      </div>
    </Transition>

    <!-- Backdrop -->
    <Transition name="backdrop">
      <div
        v-if="mobileTocOpen"
        class="mobile-toc-backdrop"
        @click="mobileTocOpen = false"
        aria-hidden="true"
      ></div>
    </Transition>

  </main>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { ChevronDown, Globe, List, Mail, Server, ShieldCheck, X } from 'lucide-vue-next'

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
      <div class="callout">We do not sell personal data.</div>
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
  const offset = 72
  const top = el.getBoundingClientRect().top + window.scrollY - offset
  window.scrollTo({ top, behavior: 'smooth' })
}

let scrollObserver = null

onMounted(() => {
  const targets = document.querySelectorAll('.policy-section')
  scrollObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) activeSection.value = entry.target.id
      })
    },
    { rootMargin: '-15% 0px -65% 0px', threshold: 0 }
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
  width: min(1160px, calc(100% - 3rem));
  margin: 0 auto;
}

/* ── Hero ── */
.hero {
  padding: 2.5rem 0 2rem;
  display: grid;
  gap: 0.85rem;
  text-align: left;
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.kicker {
  display: inline-flex;
  padding: 0.28rem 0.65rem;
  border-radius: 999px;
  border: 1px solid var(--theme-border);
  font-size: 0.72rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--theme-text-soft);
  background: var(--theme-surface-soft);
  font-weight: 700;
}

.kicker-divider {
  color: var(--theme-text-muted);
}

.last-updated {
  color: var(--theme-text-muted);
  font-size: 0.82rem;
  font-weight: 500;
}

.hero h1 {
  margin: 0;
  font-size: clamp(2rem, 5vw, 3.2rem);
  line-height: 1.04;
  letter-spacing: -0.03em;
  color: var(--theme-text-strong, var(--text-primary));
  text-align: left;
}

.hero-subtitle {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.7;
  max-width: 64ch;
  font-size: 0.97rem;
  text-align: left;
}

.hero-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin-top: 0.3rem;
}

/* ── Buttons ── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 38px;
  padding: 0.44rem 0.9rem;
  border-radius: 10px;
  border: 1px solid transparent;
  font-weight: 600;
  font-size: 0.86rem;
  text-decoration: none;
  cursor: pointer;
  transition: border-color 150ms ease, background 150ms ease;
  white-space: nowrap;
}

.btn-ghost {
  border-color: var(--theme-border-strong);
  background: var(--theme-panel-soft);
  color: var(--theme-text-primary);
}

.btn-ghost:hover {
  border-color: var(--theme-brand-border);
  background: var(--theme-surface-soft);
}

/* ── Two-column layout ── */
.content-layout {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 2.8rem;
  align-items: start;
  padding-bottom: 4rem;
}

/* ── Sidebar ── */
.toc-sidebar {
  position: sticky;
  top: 68px;
  max-height: calc(100vh - 84px);
  overflow-y: auto;
  scrollbar-width: none;
  padding-bottom: 1rem;
}

.toc-sidebar::-webkit-scrollbar { display: none; }

.toc-heading {
  margin: 0 0 0.6rem;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--theme-text-muted);
}

.toc-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.06rem;
}

.toc-link {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  padding: 0.36rem 0.58rem;
  border-radius: 8px;
  text-decoration: none;
  color: var(--theme-text-secondary);
  font-size: 0.81rem;
  font-weight: 500;
  line-height: 1.4;
  border-left: 2px solid transparent;
  transition: background 130ms ease, color 130ms ease, border-color 130ms ease;
}

.toc-link:hover {
  background: var(--theme-surface-soft);
  color: var(--theme-text-primary);
}

.toc-link.is-active {
  background: var(--theme-brand-soft);
  color: var(--theme-brand-pill-text);
  border-left-color: var(--theme-brand-a);
  font-weight: 700;
}

.toc-num {
  font-size: 0.66rem;
  font-weight: 700;
  color: var(--theme-text-muted);
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
  min-width: 1.45rem;
  letter-spacing: 0.04em;
}

.toc-link.is-active .toc-num {
  color: var(--theme-brand-pill-text);
}

.toc-contact-box {
  margin-top: 1.4rem;
  padding: 0.8rem;
  border-radius: 12px;
  border: 1px solid var(--theme-brand-border);
  background: var(--theme-brand-soft);
  display: grid;
  gap: 0.28rem;
}

.toc-contact-icon {
  width: 0.95rem;
  height: 0.95rem;
  color: var(--theme-brand-pill-text);
}

.toc-contact-box p {
  margin: 0;
  font-size: 0.79rem;
  color: var(--theme-text-soft);
}

.toc-contact-link {
  font-size: 0.79rem;
  font-weight: 600;
  color: var(--theme-brand-pill-text);
  text-decoration: none;
  word-break: break-all;
}

.toc-contact-link:hover { text-decoration: underline; }

/* ── Policy content ── */
.policy-content {
  min-width: 0;
  display: grid;
  gap: 0;
}

.policy-section {
  padding: 1.85rem 0;
  border-bottom: 1px solid var(--theme-border-soft);
  scroll-margin-top: 72px;
  text-align: left;
}

.policy-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.section-num-badge {
  display: inline-flex;
  padding: 0.16rem 0.46rem;
  border-radius: 6px;
  font-size: 0.67rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: var(--theme-brand-pill-text);
  background: var(--theme-brand-soft);
  border: 1px solid var(--theme-brand-border);
  margin-bottom: 0.6rem;
}

.policy-section h2 {
  margin: 0 0 0.95rem;
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -0.015em;
  line-height: 1.3;
  color: var(--theme-text-strong, var(--text-primary));
  text-align: left;
}

/* v-html rich text — must use :deep() */
.section-body :deep(p) {
  margin: 0 0 0.75rem;
  color: var(--theme-text-soft);
  line-height: 1.75;
  font-size: 0.93rem;
  text-align: left;
}

.section-body :deep(p:last-child) { margin-bottom: 0; }

.section-body :deep(ul) {
  margin: 0.2rem 0 0.75rem;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.45rem;
}

.section-body :deep(li) {
  display: flex;
  align-items: flex-start;
  gap: 0.58rem;
  color: var(--theme-text-soft);
  line-height: 1.65;
  font-size: 0.92rem;
  text-align: left;
}

.section-body :deep(li)::before {
  content: '';
  display: block;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--theme-brand-a);
  margin-top: 0.56rem;
  flex-shrink: 0;
}

.section-body :deep(.callout) {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  margin-top: 0.7rem;
  padding: 0.52rem 0.88rem;
  border-radius: 10px;
  border: 1px solid var(--theme-success-border);
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
  font-weight: 700;
  font-size: 0.87rem;
  text-align: left;
}

/* Contact section */
.section-intro {
  margin: 0 0 1rem;
  color: var(--theme-text-soft);
  line-height: 1.7;
  font-size: 0.93rem;
  text-align: left;
}

.contact-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.72rem;
}

.contact-card {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  padding: 0.85rem;
  border-radius: 12px;
  border: 1px solid var(--theme-border-soft);
  background: var(--theme-panel-soft);
  text-decoration: none;
  transition: border-color 150ms ease, background 150ms ease;
}

a.contact-card:hover {
  border-color: var(--theme-brand-border);
  background: var(--theme-brand-soft);
}

.contact-card-icon {
  width: 1rem;
  height: 1rem;
  color: var(--theme-brand-pill-text);
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.contact-card strong {
  display: block;
  font-size: 0.79rem;
  font-weight: 700;
  color: var(--theme-text-primary);
  margin-bottom: 0.18rem;
}

.contact-card span {
  font-size: 0.79rem;
  color: var(--theme-text-secondary);
  word-break: break-all;
  line-height: 1.4;
}

/* ── Footer ── */
.page-footer {
  border-top: 1px solid var(--theme-border-soft);
  background: var(--theme-surface-soft);
  padding: 1.1rem 0;
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
  font-size: 0.81rem;
  color: var(--theme-text-muted);
}

.footer-links {
  display: flex;
  gap: 1.2rem;
}

.footer-links a {
  font-size: 0.81rem;
  color: var(--theme-text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: color 130ms ease;
}

.footer-links a:hover { color: var(--theme-brand-pill-text); }

/* ── Mobile floating ToC button ── */
.mobile-toc-btn {
  display: none;
  position: fixed;
  bottom: 5.5rem;
  right: 1rem;
  z-index: 400;
  align-items: center;
  gap: 0.4rem;
  padding: 0.55rem 0.88rem;
  border-radius: 999px;
  border: 1px solid var(--theme-border-strong);
  background: var(--theme-surface);
  color: var(--theme-text-primary);
  font-size: 0.82rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.mobile-toc-icon {
  width: 0.95rem;
  height: 0.95rem;
}

.mobile-toc-chevron {
  width: 0.85rem;
  height: 0.85rem;
  transition: transform 200ms ease;
}

.mobile-toc-chevron.is-open { transform: rotate(180deg); }

/* ── Mobile ToC drawer ── */
.mobile-toc-drawer {
  display: none;
  position: fixed;
  bottom: 9.5rem;
  right: 1rem;
  z-index: 390;
  width: min(300px, calc(100vw - 2rem));
  max-height: 52vh;
  overflow-y: auto;
  border-radius: 16px;
  border: 1px solid var(--theme-border-strong);
  background: var(--theme-surface);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  padding: 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.22);
}

.mobile-toc-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.mobile-toc-close {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 6px;
  border: 1px solid var(--theme-border-soft);
  background: var(--theme-surface-soft);
  color: var(--theme-text-secondary);
  display: grid;
  place-items: center;
  cursor: pointer;
}

.close-icon {
  width: 0.82rem;
  height: 0.82rem;
}

.mobile-toc-backdrop {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 380;
  background: rgba(0, 0, 0, 0.26);
  backdrop-filter: blur(2px);
}

/* ── Transitions ── */
.mobile-toc-enter-active,
.mobile-toc-leave-active {
  transition: opacity 180ms ease, transform 180ms ease;
}

.mobile-toc-enter-from,
.mobile-toc-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.97);
}

.backdrop-enter-active,
.backdrop-leave-active { transition: opacity 180ms ease; }

.backdrop-enter-from,
.backdrop-leave-to { opacity: 0; }

/* ── Keyframes ── */
@keyframes mesh-drift {
  0%   { transform: translate3d(0, 0, 0) scale(1); }
  100% { transform: translate3d(-1.5%, 1.2%, 0) scale(1.04); }
}

/* ── Responsive ── */
@media (max-width: 1024px) {
  .content-layout {
    grid-template-columns: 192px 1fr;
    gap: 2rem;
  }
}

@media (max-width: 767px) {
  .section-shell {
    width: calc(100% - 1.5rem);
  }

  .hero {
    padding: 1.5rem 0 1.2rem;
  }

  .hero h1 {
    font-size: clamp(1.8rem, 7vw, 2.4rem);
  }

  .hero-subtitle {
    font-size: 0.9rem;
  }

  .hero-nav .btn {
    flex: 1;
  }

  /* Single column on mobile — sidebar hidden */
  .content-layout {
    grid-template-columns: 1fr;
    gap: 0;
    padding-bottom: 2rem;
  }

  .toc-sidebar {
    display: none;
  }

  /* Show floating button + drawer */
  .mobile-toc-btn {
    display: flex;
  }

  .mobile-toc-drawer {
    display: block;
  }

  .mobile-toc-backdrop {
    display: block;
  }

  .policy-section {
    padding: 1.35rem 0;
    scroll-margin-top: 60px;
  }

  .policy-section h2 {
    font-size: 1.04rem;
  }

  .contact-grid {
    grid-template-columns: 1fr;
    gap: 0.6rem;
  }

  .footer-inner {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.6rem;
  }

  .page-footer {
    /* clear bottom nav */
    padding-bottom: 5.5rem;
  }
}
</style>