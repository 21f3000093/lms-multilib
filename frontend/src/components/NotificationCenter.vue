<template>
  <main class="notifications-page" ref="pageRoot">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="hero section-shell reveal" data-stagger="0">
      <div>
        <p class="kicker">Admin Workspace</p>
        <h1>
          Notification
          <span class="gradient-text">Center</span>
        </h1>
        <p class="hero-subtitle">
          Track announcements from superadmin, quickly clear unread items, and stay synced with billing and operational updates.
        </p>
      </div>

      <div class="hero-actions">
        <button class="btn btn-ghost" :disabled="loading" @click="refreshAll">
          <RefreshCw class="btn-icon" :class="{ spinning: loading }" aria-hidden="true" />
          <span>Refresh</span>
        </button>
        <button class="btn btn-solid" :disabled="markingAll || unreadCount === 0" @click="markAllAsRead">
          <CheckCheck class="btn-icon" aria-hidden="true" />
          <span>{{ markingAll ? 'Updating...' : 'Mark all read' }}</span>
        </button>
      </div>
    </section>

    <section class="section-shell reveal" data-stagger="1">
      <div class="toolbar-card">
        <div class="filters">
          <button class="filter-btn" :class="{ active: !unreadOnly }" @click="setUnreadOnly(false)">
            <Inbox class="filter-icon" aria-hidden="true" />
            <span>All</span>
          </button>
          <button class="filter-btn" :class="{ active: unreadOnly }" @click="setUnreadOnly(true)">
            <Bell class="filter-icon" aria-hidden="true" />
            <span>Unread ({{ unreadCount }})</span>
          </button>
        </div>
      </div>

      <div v-if="loading" class="state-card">
        <RefreshCw class="state-icon spinning" aria-hidden="true" />
        <span>Loading notifications...</span>
      </div>

      <div v-else-if="notifications.length === 0" class="state-card">
        <Inbox class="state-icon" aria-hidden="true" />
        <span>No notifications found.</span>
      </div>

      <div v-else class="notification-list">
        <article
          v-for="(item, index) in notifications"
          :key="item.recipient_id"
          class="notification-card reveal"
          :class="{ unread: !item.is_read }"
          :data-stagger="(index % 5) + 1"
        >
          <div class="card-top">
            <span class="category-pill" :class="`category-${item.category}`">
              {{ item.category }}
            </span>
            <span class="time-text">
              <Clock3 class="time-icon" aria-hidden="true" />
              {{ formatDateTime(item.created_at) }}
            </span>
          </div>

          <h3>{{ item.title }}</h3>
          <p>{{ item.message }}</p>

          <div class="card-footer">
            <span class="sender-text">
              <CircleUserRound class="sender-icon" aria-hidden="true" />
              {{ item.sender_username || 'Superadmin' }}
            </span>

            <button v-if="!item.is_read" class="mark-btn" @click="markOneRead(item)">
              <Check class="mark-icon" aria-hidden="true" />
              <span>Mark read</span>
            </button>

            <span v-else class="read-tag">
              <CheckCheck class="mark-icon" aria-hidden="true" />
              <span>Read</span>
            </span>
          </div>
        </article>
      </div>
    </section>
  </main>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import {
  Bell,
  Check,
  CheckCheck,
  CircleUserRound,
  Clock3,
  Inbox,
  RefreshCw,
} from 'lucide-vue-next'
import API from '../api'

const pageRoot = ref(null)
let observer = null

const notifications = ref([])
const unreadOnly = ref(false)
const unreadCount = ref(0)
const loading = ref(false)
const markingAll = ref(false)

const emitUnreadCount = () => {
  window.dispatchEvent(
    new CustomEvent('notifications:unread-count-updated', {
      detail: { count: unreadCount.value },
    })
  )
}

const refreshAll = async () => {
  loading.value = true
  try {
    await Promise.all([loadUnreadCount(), loadNotifications()])
  } finally {
    loading.value = false
  }
}

const loadUnreadCount = async () => {
  const res = await API.get('/notifications/inbox/unread-count')
  unreadCount.value = Number(res.data.unread_count || 0)
  emitUnreadCount()
}

const loadNotifications = async () => {
  const res = await API.get('/notifications/inbox', {
    params: {
      unread_only: unreadOnly.value,
      limit: 150,
    },
  })
  notifications.value = res.data
}

const setUnreadOnly = async (value) => {
  if (unreadOnly.value === value) {
    return
  }

  unreadOnly.value = value
  loading.value = true
  try {
    await loadNotifications()
  } finally {
    loading.value = false
  }
}

const markOneRead = async (item) => {
  if (item.is_read) {
    return
  }

  await API.patch(`/notifications/inbox/${item.notification_id}/read`)
  item.is_read = true
  item.read_at = new Date().toISOString()
  unreadCount.value = Math.max(0, unreadCount.value - 1)
  emitUnreadCount()

  if (unreadOnly.value) {
    notifications.value = notifications.value.filter(
      (notification) => notification.recipient_id !== item.recipient_id
    )
  }
}

const markAllAsRead = async () => {
  if (!unreadCount.value) {
    return
  }

  markingAll.value = true
  try {
    await API.patch('/notifications/inbox/read-all')
    unreadCount.value = 0
    emitUnreadCount()

    if (unreadOnly.value) {
      notifications.value = []
    } else {
      const now = new Date().toISOString()
      notifications.value = notifications.value.map((notification) => ({
        ...notification,
        is_read: true,
        read_at: notification.read_at || now,
      }))
    }
  } finally {
    markingAll.value = false
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
  await refreshAll()

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

.notifications-page {
  --bg: #0f172a;
  --surface: rgba(148, 163, 184, 0.03);
  --surface-border: rgba(255, 255, 255, 0.03);
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --brand-a: #22d3ee;
  --brand-b: #3b82f6;

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
  background:
    radial-gradient(45rem 24rem at 10% 15%, rgba(34, 211, 238, 0.14), transparent 70%),
    radial-gradient(40rem 24rem at 86% 8%, rgba(59, 130, 246, 0.14), transparent 68%),
    radial-gradient(36rem 22rem at 65% 88%, rgba(14, 165, 233, 0.11), transparent 70%),
    linear-gradient(180deg, #0f172a 0%, #0b1222 100%);
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
  border: 1px solid rgba(148, 163, 184, 0.25);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #cbd5e1;
  background: rgba(148, 163, 184, 0.07);
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

.hero-subtitle {
  margin: 0.8rem 0 0;
  color: var(--text-secondary);
  max-width: 65ch;
  line-height: 1.6;
  text-wrap: balance;
}

.hero-actions {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.6rem;
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
  background: linear-gradient(90deg, #0ea5e9, #3b82f6);
  color: #fff;
  box-shadow: 0 14px 28px rgba(59, 130, 246, 0.28);
}

.btn-ghost {
  background: rgba(148, 163, 184, 0.08);
  border-color: rgba(148, 163, 184, 0.32);
  color: #e2e8f0;
}

.btn-icon {
  width: 0.95rem;
  height: 0.95rem;
}

.spinning {
  animation: spin 1s linear infinite;
}

.toolbar-card,
.notification-card,
.state-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.toolbar-card {
  margin-top: 1.2rem;
  border-radius: 16px;
  padding: 0.75rem;
}

.filters {
  display: flex;
  gap: 0.55rem;
  flex-wrap: wrap;
}

.filter-btn {
  border: 1px solid rgba(148, 163, 184, 0.34);
  background: rgba(148, 163, 184, 0.08);
  color: #cbd5e1;
  border-radius: 999px;
  padding: 0.42rem 0.72rem;
  display: inline-flex;
  align-items: center;
  gap: 0.36rem;
  font-weight: 700;
  cursor: pointer;
}

.filter-btn.active {
  background: rgba(14, 165, 233, 0.24);
  border-color: rgba(14, 165, 233, 0.45);
  color: #f8fafc;
}

.filter-icon {
  width: 0.92rem;
  height: 0.92rem;
}

.state-card {
  margin-top: 0.95rem;
  border-radius: 14px;
  padding: 1rem;
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  color: #cbd5e1;
}

.state-icon {
  width: 1rem;
  height: 1rem;
}

.notification-list {
  margin-top: 0.9rem;
  display: grid;
  gap: 0.8rem;
}

.notification-card {
  border-radius: 14px;
  padding: 0.95rem;
}

.notification-card.unread {
  border-color: rgba(14, 165, 233, 0.45);
  box-shadow: 0 0 0 1px rgba(14, 165, 233, 0.18);
}

.card-top {
  display: flex;
  justify-content: space-between;
  gap: 0.7rem;
  align-items: center;
}

.category-pill {
  text-transform: capitalize;
  font-size: 0.74rem;
  font-weight: 700;
  padding: 0.22rem 0.48rem;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.22);
  color: #e2e8f0;
}

.category-subscription {
  background: rgba(239, 68, 68, 0.2);
  color: #fecaca;
}

.category-offer {
  background: rgba(16, 185, 129, 0.2);
  color: #a7f3d0;
}

.category-general {
  background: rgba(59, 130, 246, 0.2);
  color: #bfdbfe;
}

.category-maintenance {
  background: rgba(245, 158, 11, 0.2);
  color: #fde68a;
}

.time-text {
  display: inline-flex;
  align-items: center;
  gap: 0.28rem;
  color: #94a3b8;
  font-size: 0.77rem;
}

.time-icon,
.sender-icon,
.mark-icon {
  width: 0.9rem;
  height: 0.9rem;
}

.notification-card h3 {
  margin: 0.66rem 0 0.42rem;
  color: #f8fafc;
  font-size: 1.02rem;
}

.notification-card p {
  margin: 0;
  color: #cbd5e1;
  line-height: 1.5;
}

.card-footer {
  margin-top: 0.78rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.sender-text {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  color: #94a3b8;
  font-size: 0.8rem;
}

.mark-btn,
.read-tag {
  border-radius: 8px;
  padding: 0.36rem 0.58rem;
  font-size: 0.8rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 0.28rem;
}

.mark-btn {
  border: 1px solid rgba(14, 165, 233, 0.46);
  color: #e0f2fe;
  background: rgba(14, 165, 233, 0.16);
  cursor: pointer;
}

.read-tag {
  border: 1px solid rgba(16, 185, 129, 0.36);
  color: #a7f3d0;
  background: rgba(16, 185, 129, 0.12);
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

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
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

@media (max-width: 900px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-actions {
    width: 100%;
  }

  .btn {
    flex: 1;
  }
}

@media (max-width: 767px) {
  .notifications-page {
    padding-top: 5.4rem;
  }

  .section-shell {
    width: min(1040px, calc(100% - 1rem));
  }

  .card-top,
  .card-footer {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
