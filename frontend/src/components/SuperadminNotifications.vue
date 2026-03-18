<template>
  <main class="superadmin-notifications" ref="pageRoot">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="hero section-shell reveal" data-stagger="0">
      <div>
        <p class="kicker">Superadmin Workspace</p>
        <h1>
          Broadcast
          <span class="gradient-text">Notifications</span>
        </h1>
        <p class="hero-subtitle">
          Send platform notices for subscription dues, promotional offers, and maintenance updates to one or all libraries.
        </p>
      </div>

      <button class="btn btn-ghost" @click="loadSent" :disabled="loadingSent">
        <RefreshCw class="btn-icon" :class="{ spinning: loadingSent }" aria-hidden="true" />
        <span>Refresh Sent</span>
      </button>
    </section>

    <section class="section-shell reveal" data-stagger="1">
      <article class="compose-card">
        <header class="card-head">
          <h2>Create Notification</h2>
          <p>Compose once and target all libraries or a specific library.</p>
        </header>

        <form class="compose-form" @submit.prevent="sendNotification">
          <label class="field-label" for="notify-title">Title</label>
          <div class="field-wrap">
            <Heading class="field-icon" aria-hidden="true" />
            <input id="notify-title" v-model.trim="form.title" type="text" maxlength="200" placeholder="Title" required />
          </div>

          <label class="field-label" for="notify-message">Message</label>
          <div class="field-wrap textarea-wrap">
            <MessageSquare class="field-icon" aria-hidden="true" />
            <textarea id="notify-message" v-model.trim="form.message" rows="4" placeholder="Write message for admins" required></textarea>
          </div>

          <div class="form-grid">
            <div>
              <label class="field-label" for="notify-category">Category</label>
              <div class="field-wrap">
                <Tag class="field-icon" aria-hidden="true" />
                <select id="notify-category" v-model="form.category" required>
                  <option value="general">General</option>
                  <option value="subscription">Subscription</option>
                  <option value="offer">Offer</option>
                  <option value="maintenance">Maintenance</option>
                </select>
              </div>
            </div>

            <div>
              <label class="field-label" for="notify-target-mode">Target</label>
              <div class="field-wrap">
                <SendHorizonal class="field-icon" aria-hidden="true" />
                <select id="notify-target-mode" v-model="targetMode" @change="onTargetModeChange">
                  <option value="all">All Libraries</option>
                  <option value="library">Specific Library</option>
                </select>
              </div>
            </div>

            <div v-if="targetMode === 'library'">
              <label class="field-label" for="notify-library">Library</label>
              <div class="field-wrap">
                <Library class="field-icon" aria-hidden="true" />
                <select id="notify-library" v-model="selectedLibraryId" required>
                  <option disabled value="">Select library</option>
                  <option v-for="library in libraries" :key="library.id" :value="String(library.id)">
                    {{ library.name }} (ID: {{ library.id }})
                  </option>
                </select>
              </div>
            </div>
          </div>

          <div class="actions">
            <button type="button" class="btn btn-ghost" @click="resetForm">
              <RotateCcw class="btn-icon" aria-hidden="true" />
              <span>Clear</span>
            </button>
            <button type="submit" class="btn btn-solid" :disabled="sending">
              <Send class="btn-icon" aria-hidden="true" />
              <span>{{ sending ? 'Sending...' : 'Send Notification' }}</span>
            </button>
          </div>
        </form>
      </article>

      <article class="sent-card">
        <header class="card-head sent-head">
          <div>
            <h2>Sent Notifications</h2>
            <p>Recent broadcasts and delivery status snapshot.</p>
          </div>
          <span class="count-chip">{{ sentNotifications.length }} records</span>
        </header>

        <div v-if="loadingSent" class="state-card">
          <RefreshCw class="state-icon spinning" aria-hidden="true" />
          <span>Loading sent notifications...</span>
        </div>

        <div v-else-if="sentNotifications.length === 0" class="state-card">
          <Inbox class="state-icon" aria-hidden="true" />
          <span>No notifications sent yet.</span>
        </div>

        <div v-else class="sent-list">
          <article
            v-for="(item, index) in sentNotifications"
            :key="item.id"
            class="sent-item reveal"
            :data-stagger="(index % 5) + 1"
          >
            <div class="sent-top">
              <span class="category-pill" :class="`category-${item.category}`">{{ item.category }}</span>
              <span class="time-text">
                <Clock3 class="time-icon" aria-hidden="true" />
                {{ formatDateTime(item.created_at) }}
              </span>
            </div>

            <h3>{{ item.title }}</h3>
            <p>{{ item.message }}</p>

            <div class="sent-meta">
              <span><Users class="meta-icon" aria-hidden="true" /> Recipients: {{ item.recipient_count }}</span>
              <span><Bell class="meta-icon" aria-hidden="true" /> Unread: {{ item.unread_count }}</span>
              <span v-if="item.target_type === 'library'"><Building2 class="meta-icon" aria-hidden="true" /> Library ID: {{ item.target_library_id }}</span>
              <span v-else><Target class="meta-icon" aria-hidden="true" /> Target: {{ item.target_type }}</span>
            </div>
          </article>
        </div>
      </article>
    </section>
  </main>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import {
  Bell,
  Building2,
  Clock3,
  Heading,
  Inbox,
  Library,
  MessageSquare,
  RefreshCw,
  RotateCcw,
  Send,
  SendHorizonal,
  Tag,
  Target,
  Users,
} from 'lucide-vue-next'
import API from '../api'

const pageRoot = ref(null)
let observer = null

const form = ref({
  title: '',
  message: '',
  category: 'general',
})

const targetMode = ref('all')
const selectedLibraryId = ref('')
const libraries = ref([])
const sentNotifications = ref([])
const sending = ref(false)
const loadingSent = ref(false)

const bootstrap = async () => {
  await Promise.all([loadLibraries(), loadSent()])
}

const loadLibraries = async () => {
  const res = await API.get('/superadmin/libraries')
  libraries.value = res.data
}

const loadSent = async () => {
  loadingSent.value = true
  try {
    const res = await API.get('/notifications/sent', {
      params: { limit: 80 },
    })
    sentNotifications.value = res.data
  } finally {
    loadingSent.value = false
  }
}

const onTargetModeChange = () => {
  if (targetMode.value === 'all') {
    selectedLibraryId.value = ''
  }
}

const resetForm = () => {
  form.value = {
    title: '',
    message: '',
    category: 'general',
  }
  targetMode.value = 'all'
  selectedLibraryId.value = ''
}

const sendNotification = async () => {
  if (!form.value.title || !form.value.message) {
    alert('Title and message are required')
    return
  }

  if (targetMode.value === 'library' && !selectedLibraryId.value) {
    alert('Please select a library')
    return
  }

  const payload = {
    title: form.value.title,
    message: form.value.message,
    category: form.value.category,
    click_url: '/notifications',
  }

  if (targetMode.value === 'library') {
    payload.target_library_id = Number(selectedLibraryId.value)
  }

  sending.value = true
  try {
    await API.post('/notifications/', payload)
    await loadSent()
    resetForm()
    alert('Notification sent successfully')
  } finally {
    sending.value = false
  }
}

const formatDateTime = (value) => {
  if (!value) {
    return '-'
  }
  return new Date(value).toLocaleString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(async () => {
  await bootstrap()

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
  observer?.disconnect()
  observer = null
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.superadmin-notifications {
  --bg: var(--theme-page-bg);
  --surface: var(--theme-surface);
  --surface-border: var(--theme-surface-border);
  --text-primary: var(--theme-text-primary);
  --text-secondary: var(--theme-text-secondary);
  --brand-a: var(--theme-brand-a);
  --brand-b: var(--theme-brand-b);

  position: relative;
  min-height: 100vh;
  padding: 6.7rem 0 2.8rem;
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
  width: min(1040px, calc(100% - 2rem));
  margin: 0 auto;
}

.hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1rem;
}

.kicker {
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
  margin: 0.8rem 0 0;
  font-size: clamp(1.9rem, 4.4vw, 3rem);
  line-height: 1.05;
  letter-spacing: -0.03em;
}

.gradient-text {
  background: linear-gradient(90deg, var(--brand-a), var(--brand-b));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-subtitle,
.card-head p,
.sent-item p {
  margin: 0.75rem 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
  text-wrap: balance;
}

.btn {
  min-height: 42px;
  border-radius: 12px;
  border: 1px solid transparent;
  padding: 0.6rem 0.85rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  font-weight: 700;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-solid {
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
  color: var(--theme-brand-on);
  box-shadow: var(--theme-shadow-elevated);
}

.btn-ghost {
  background: var(--theme-surface-soft-strong);
  border-color: var(--theme-border-strong);
  color: var(--theme-text-primary);
}

.btn-icon {
  width: 0.95rem;
  height: 0.95rem;
}

.spinning {
  animation: spin 1s linear infinite;
}

.compose-card,
.sent-card,
.sent-item,
.state-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.compose-card,
.sent-card {
  margin-top: 1.2rem;
  border-radius: 16px;
  padding: 1rem;
}

.sent-card {
  margin-top: 0.85rem;
}

.card-head h2 {
  margin: 0;
  font-size: clamp(1.2rem, 2.8vw, 1.9rem);
}

.compose-form {
  margin-top: 0.7rem;
  display: grid;
  gap: 0.65rem;
}

.field-label {
  color: var(--theme-text-soft);
  font-weight: 600;
  font-size: 0.86rem;
}

.field-wrap {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  border-radius: 12px;
  padding: 0 0.6rem;
  border: 1px solid var(--theme-input-border);
  background: var(--theme-input-bg);
}

.field-wrap:focus-within {
  border-color: var(--theme-brand-border);
  box-shadow: 0 0 0 3px var(--theme-brand-ring);
}

.textarea-wrap {
  align-items: flex-start;
  padding-top: 0.55rem;
}

.field-icon {
  width: 0.95rem;
  height: 0.95rem;
  color: var(--theme-text-muted);
  flex: 0 0 auto;
  margin-top: 0.05rem;
}

.field-wrap input,
.field-wrap textarea,
.field-wrap select {
  width: 100%;
  border: none;
  outline: none;
  background: transparent;
  color: var(--theme-text-strong);
  font-size: 0.95rem;
  padding: 0.78rem 0;
}

.field-wrap select option {
  color: var(--theme-text-strong);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.62rem;
}

.actions {
  margin-top: 0.25rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.58rem;
}

.sent-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.8rem;
}

.count-chip {
  border-radius: 999px;
  padding: 0.32rem 0.56rem;
  border: 1px solid var(--theme-border);
  background: var(--theme-surface-soft-strong);
  color: var(--theme-text-soft);
  font-size: 0.76rem;
  font-weight: 700;
}

.state-card {
  margin-top: 0.85rem;
  border-radius: 12px;
  padding: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: var(--theme-text-soft);
}

.state-icon {
  width: 0.98rem;
  height: 0.98rem;
}

.sent-list {
  margin-top: 0.85rem;
  display: grid;
  gap: 0.72rem;
}

.sent-item {
  border-radius: 12px;
  padding: 0.9rem;
}

.sent-top {
  display: flex;
  justify-content: space-between;
  gap: 0.65rem;
  align-items: center;
}

.category-pill {
  text-transform: capitalize;
  font-size: 0.74rem;
  font-weight: 700;
  padding: 0.22rem 0.48rem;
  border-radius: 999px;
  background: var(--theme-surface-soft-heavy);
  color: var(--theme-text-primary);
}

.category-subscription {
  background: var(--theme-danger-soft);
  color: var(--theme-danger-text);
}

.category-offer {
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
}

.category-general {
  background: var(--theme-info-soft);
  color: var(--theme-info-text);
}

.category-maintenance {
  background: var(--theme-warning-soft);
  color: var(--theme-warning-text);
}

.time-text {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  color: var(--theme-text-secondary);
  font-size: 0.76rem;
}

.time-icon,
.meta-icon {
  width: 0.88rem;
  height: 0.88rem;
}

.sent-item h3 {
  margin: 0.62rem 0 0.4rem;
  color: var(--theme-text-strong);
  font-size: 1rem;
}

.sent-meta {
  margin-top: 0.66rem;
  display: flex;
  gap: 0.7rem;
  flex-wrap: wrap;
}

.sent-meta span {
  display: inline-flex;
  align-items: center;
  gap: 0.28rem;
  font-size: 0.8rem;
  color: var(--theme-text-soft);
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

@keyframes mesh-drift {
  0% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  100% {
    transform: translate3d(-1.5%, 1.2%, 0) scale(1.04);
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 980px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .actions {
    justify-content: stretch;
  }

  .actions .btn {
    flex: 1;
  }
}

@media (max-width: 767px) {
  .superadmin-notifications {
    padding-top: 5.4rem;
  }

  .section-shell {
    width: min(1040px, calc(100% - 1rem));
  }

  .sent-head,
  .sent-top {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
