<template>
  <main class="privacy-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="section-shell hero">
      <nav class="hero-nav" aria-label="Privacy policy navigation">
        <router-link class="btn btn-ghost" to="/">Back to Home</router-link>
        <router-link class="btn btn-ghost" to="/login">Go to Login</router-link>
      </nav>

      <p class="kicker">Smart Library App</p>
      <h1>Privacy Policy</h1>
      <p class="hero-subtitle">
        This Privacy Policy explains how Smart Library App collects, uses, secures, and processes information when
        you use our multi-library management platform.
      </p>
      <p class="last-updated">Last Updated: May 9, 2026</p>
    </section>

    <article class="section-shell glass-card policy-card" aria-label="Smart Library App privacy policy">
      <section id="information-collect" class="policy-section" aria-labelledby="information-collect-heading">
        <h2 id="information-collect-heading">Information We Collect</h2>
        <p>We collect information required to operate library workflows, including:</p>
        <ul>
          <li>Admin account details such as name, mobile number, email, and role.</li>
          <li>Library profile data such as library name, address, seat capacity, and operating settings.</li>
          <li>Student data such as name, contact number, seat preferences, attendance, and fee history.</li>
          <li>Operational analytics such as occupancy, collections, reminders sent, and activity usage.</li>
          <li>Technical metadata such as browser/device info, app version, and diagnostic logs.</li>
        </ul>
      </section>

      <section id="use-information" class="policy-section" aria-labelledby="use-information-heading">
        <h2 id="use-information-heading">How We Use Information</h2>
        <p>We use your data to:</p>
        <ul>
          <li>Provide and maintain student management, seat allocation, fee tracking, and attendance features.</li>
          <li>Enable reminders, payment workflows, receipts, and dashboard analytics.</li>
          <li>Improve platform reliability, fraud prevention, and product performance.</li>
          <li>Provide support, troubleshooting, and service communications.</li>
        </ul>
        <p>We do not sell personal data.</p>
      </section>

      <section id="auth-security" class="policy-section" aria-labelledby="auth-security-heading">
        <h2 id="auth-security-heading">Authentication and Account Security</h2>
        <p>
          Access to Smart Library App is role-based. Admin authentication uses secure session and token controls.
          Credentials and authorization checks are used to protect restricted features and data boundaries across
          libraries.
        </p>
      </section>

      <section id="payment-data" class="policy-section" aria-labelledby="payment-data-heading">
        <h2 id="payment-data-heading">Payment and Fee Data</h2>
        <p>
          We process billing and fee records to support subscription plans, collections, and receipts. Payment events
          and references are stored for reconciliation and audit history. Sensitive payment details are handled via
          trusted payment integrations and are not sold or repurposed by us.
        </p>
      </section>

      <section id="whatsapp-usage" class="policy-section" aria-labelledby="whatsapp-usage-heading">
        <h2 id="whatsapp-usage-heading">WhatsApp Reminder Usage</h2>
        <p>
          Smart Library App can send reminder messages on behalf of authorized library admins. Message content is
          generated from configured student and fee records. Admins are responsible for ensuring they have appropriate
          communication consent from their students.
        </p>
      </section>

      <section id="cookies-storage" class="policy-section" aria-labelledby="cookies-storage-heading">
        <h2 id="cookies-storage-heading">Cookies and Local Storage</h2>
        <p>
          We use browser storage and similar technologies for session continuity, authentication state, preferences,
          and performance. This helps keep users signed in securely and improves app responsiveness.
        </p>
      </section>

      <section id="pwa-caching" class="policy-section" aria-labelledby="pwa-caching-heading">
        <h2 id="pwa-caching-heading">PWA and Offline Data Caching</h2>
        <p>
          Smart Library App operates as a Progressive Web App and Android Trusted Web Activity. For PWA functionality,
          service workers may cache limited offline assets such as static files and app shell resources to improve load
          speed and resilience.
        </p>
      </section>

      <section id="data-security" class="policy-section" aria-labelledby="data-security-heading">
        <h2 id="data-security-heading">Data Security</h2>
        <p>
          We use industry-standard safeguards including HTTPS encryption in transit between clients and servers. We
          apply access controls and monitoring practices designed to reduce unauthorized access, disclosure, or misuse.
        </p>
      </section>

      <section id="third-party" class="policy-section" aria-labelledby="third-party-heading">
        <h2 id="third-party-heading">Third-Party Services</h2>
        <p>
          We may rely on third-party services for hosting, notifications, analytics, and payment processing. These
          providers process data under their own terms and applicable laws, and only to the extent required for service
          delivery.
        </p>
      </section>

      <section id="child-privacy" class="policy-section" aria-labelledby="child-privacy-heading">
        <h2 id="child-privacy-heading">Children's Privacy</h2>
        <p>
          Smart Library App is designed for use by library owners and administrators. It is not intended for direct
          use by children. Library admins are responsible for lawful data handling within their institution context.
        </p>
      </section>

      <section id="user-rights" class="policy-section" aria-labelledby="user-rights-heading">
        <h2 id="user-rights-heading">User Rights</h2>
        <p>Subject to applicable law, users may request to:</p>
        <ul>
          <li>Access or correct account information.</li>
          <li>Request deletion of eligible records.</li>
          <li>Raise concerns related to privacy or security practices.</li>
        </ul>
      </section>

      <section id="policy-changes" class="policy-section" aria-labelledby="policy-changes-heading">
        <h2 id="policy-changes-heading">Changes to Privacy Policy</h2>
        <p>
          We may update this policy from time to time to reflect legal, technical, or product changes. Updated
          versions will be posted at this page with a revised "Last Updated" date.
        </p>
      </section>

      <section id="contact" class="policy-section" aria-labelledby="contact-heading">
        <h2 id="contact-heading">Contact Information</h2>
        <p>
          For privacy-related questions, contact us at
          <a href="mailto:support@smartlibraryapp.in">support@smartlibraryapp.in</a>.
        </p>
        <p>
          Platform: <strong>smartlibraryapp.in</strong><br />
          API: <strong>api.smartlibraryapp.in</strong>
        </p>
      </section>
    </article>
  </main>
</template>

<script setup>
</script>

<style scoped>
.privacy-page {
  --surface: var(--theme-surface);
  --surface-border: var(--theme-surface-border);
  --text-primary: var(--theme-text-primary);
  --text-secondary: var(--theme-text-secondary);
  min-height: 100vh;
  position: relative;
  padding: 2rem 1rem 2.6rem;
  color: var(--text-primary);
  isolation: isolate;
  overflow: hidden;
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
  width: min(980px, calc(100% - 1rem));
  margin: 0 auto;
}

.hero {
  display: grid;
  gap: 0.75rem;
}

.hero-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin-bottom: 0.3rem;
}

.kicker {
  margin: 0;
  display: inline-flex;
  width: fit-content;
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
  border: 1px solid var(--theme-border);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--theme-text-soft);
  background: var(--theme-surface-soft);
}

h1 {
  margin: 0;
  font-size: clamp(2rem, 5vw, 3rem);
  line-height: 1.05;
  letter-spacing: -0.02em;
  color: var(--theme-text-strong);
}

.hero-subtitle {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.65;
  max-width: 68ch;
}

.last-updated {
  margin: 0;
  color: var(--theme-text-muted);
  font-size: 0.9rem;
  font-weight: 600;
}

.glass-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.policy-card {
  margin-top: 1rem;
  border-radius: 18px;
  padding: 1.05rem;
  display: grid;
  gap: 0.7rem;
}

.policy-section {
  border: 1px solid var(--theme-border-soft);
  border-radius: 14px;
  background: var(--theme-panel-soft);
  padding: 0.95rem;
}

.policy-section h2 {
  margin: 0;
  font-size: 1.03rem;
  color: var(--theme-text-strong);
}

.policy-section p {
  margin: 0.62rem 0 0;
  color: var(--theme-text-soft);
  line-height: 1.65;
  font-size: 0.94rem;
}

.policy-section ul {
  margin: 0.62rem 0 0;
  padding-left: 1rem;
  display: grid;
  gap: 0.38rem;
}

.policy-section li {
  color: var(--theme-text-soft);
  line-height: 1.55;
  font-size: 0.93rem;
}

.policy-section strong {
  color: var(--theme-text-strong);
}

.policy-section a {
  color: var(--theme-brand-pill-text);
  font-weight: 600;
}

.policy-section a:hover {
  color: var(--theme-text-info);
}

.btn {
  min-height: 40px;
  border-radius: 12px;
  border: 1px solid transparent;
  padding: 0.5rem 0.8rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  cursor: pointer;
  transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
}

.btn-ghost {
  border-color: var(--theme-border-strong);
  background: var(--theme-panel-soft);
  color: var(--theme-text-primary);
}

.btn-ghost:hover {
  border-color: var(--theme-brand-border);
  box-shadow: var(--theme-shadow-soft);
}

.btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--theme-brand-ring);
}

@keyframes mesh-drift {
  0% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  100% {
    transform: translate3d(-1.5%, 1.2%, 0) scale(1.04);
  }
}

@media (max-width: 767px) {
  .privacy-page {
    padding: 1.35rem 0.7rem 2rem;
  }

  .section-shell {
    width: min(980px, 100%);
  }

  .hero-nav {
    gap: 0.45rem;
  }

  .btn {
    width: 100%;
  }

  .policy-card {
    padding: 0.85rem;
    gap: 0.6rem;
  }

  .policy-section {
    padding: 0.85rem;
  }
}
</style>
