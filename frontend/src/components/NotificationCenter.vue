<template>
  <section class="notifications-page">
    <header class="page-header">
      <div>
        <h1>Notification Center</h1>
        <p>Messages from superadmin about billing, offers, and updates.</p>
      </div>
      <div class="header-actions">
        <button class="secondary-btn" @click="refreshAll" :disabled="loading">
          Refresh
        </button>
        <button
          class="primary-btn"
          @click="markAllAsRead"
          :disabled="markingAll || unreadCount === 0"
        >
          Mark all read
        </button>
      </div>
    </header>

    <div class="filters">
      <button
        class="filter-btn"
        :class="{ active: !unreadOnly }"
        @click="setUnreadOnly(false)"
      >
        All
      </button>
      <button
        class="filter-btn"
        :class="{ active: unreadOnly }"
        @click="setUnreadOnly(true)"
      >
        Unread ({{ unreadCount }})
      </button>
    </div>

    <div v-if="loading" class="state-card">Loading notifications...</div>
    <div v-else-if="notifications.length === 0" class="state-card">
      No notifications found.
    </div>

    <div v-else class="notification-list">
      <article
        v-for="item in notifications"
        :key="item.recipient_id"
        class="notification-card"
        :class="{ unread: !item.is_read }"
      >
        <div class="card-top">
          <span class="category-pill" :class="`category-${item.category}`">
            {{ item.category }}
          </span>
          <span class="time-text">{{ formatDateTime(item.created_at) }}</span>
        </div>

        <h3>{{ item.title }}</h3>
        <p>{{ item.message }}</p>

        <div class="card-footer">
          <span class="sender-text">
            From: {{ item.sender_username || 'Superadmin' }}
          </span>
          <button
            v-if="!item.is_read"
            class="mark-btn"
            @click="markOneRead(item)"
          >
            Mark read
          </button>
          <span v-else class="read-tag">Read</span>
        </div>
      </article>
    </div>
  </section>
</template>

<script>
import API from '../api'

export default {
  name: 'NotificationCenter',
  data() {
    return {
      notifications: [],
      unreadOnly: false,
      unreadCount: 0,
      loading: false,
      markingAll: false,
    }
  },
  mounted() {
    this.refreshAll()
  },
  methods: {
    emitUnreadCount() {
      window.dispatchEvent(
        new CustomEvent('notifications:unread-count-updated', {
          detail: { count: this.unreadCount },
        })
      )
    },

    async refreshAll() {
      this.loading = true
      try {
        await Promise.all([this.loadUnreadCount(), this.loadNotifications()])
      } finally {
        this.loading = false
      }
    },

    async loadUnreadCount() {
      const res = await API.get('/notifications/inbox/unread-count')
      this.unreadCount = res.data.unread_count || 0
      this.emitUnreadCount()
    },

    async loadNotifications() {
      const res = await API.get('/notifications/inbox', {
        params: {
          unread_only: this.unreadOnly,
          limit: 150,
        },
      })
      this.notifications = res.data
    },

    async setUnreadOnly(value) {
      if (this.unreadOnly === value) {
        return
      }
      this.unreadOnly = value
      this.loading = true
      try {
        await this.loadNotifications()
      } finally {
        this.loading = false
      }
    },

    async markOneRead(item) {
      if (item.is_read) {
        return
      }

      await API.patch(`/notifications/inbox/${item.notification_id}/read`)
      item.is_read = true
      item.read_at = new Date().toISOString()
      this.unreadCount = Math.max(0, this.unreadCount - 1)
      this.emitUnreadCount()

      if (this.unreadOnly) {
        this.notifications = this.notifications.filter(
          (notification) => notification.recipient_id !== item.recipient_id
        )
      }
    },

    async markAllAsRead() {
      if (!this.unreadCount) {
        return
      }

      this.markingAll = true
      try {
        await API.patch('/notifications/inbox/read-all')
        this.unreadCount = 0
        this.emitUnreadCount()

        if (this.unreadOnly) {
          this.notifications = []
        } else {
          const now = new Date().toISOString()
          this.notifications = this.notifications.map((notification) => ({
            ...notification,
            is_read: true,
            read_at: notification.read_at || now,
          }))
        }
      } finally {
        this.markingAll = false
      }
    },

    formatDateTime(value) {
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
    },
  },
}
</script>

<style scoped>
.notifications-page {
  max-width: 90%;
  margin: 5rem auto;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.85);
  border-radius: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.page-header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #1f2937;
}

.page-header p {
  margin: 0.35rem 0 0;
  color: #4b5563;
}

.header-actions {
  display: flex;
  gap: 0.6rem;
}

.primary-btn,
.secondary-btn,
.filter-btn,
.mark-btn {
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.primary-btn,
.secondary-btn {
  padding: 0.55rem 0.9rem;
}

.primary-btn {
  background: #5b21b6;
  color: #fff;
}

.primary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.secondary-btn {
  background: #e5e7eb;
  color: #111827;
}

.filters {
  display: flex;
  gap: 0.7rem;
  margin: 1rem 0 1.25rem;
}

.filter-btn {
  padding: 0.45rem 0.85rem;
  background: #f3f4f6;
  color: #374151;
}

.filter-btn.active {
  background: #ddd6fe;
  color: #5b21b6;
}

.state-card {
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  padding: 1.1rem;
  color: #475569;
  background: #fff;
}

.notification-list {
  display: grid;
  gap: 0.9rem;
}

.notification-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1rem;
}

.notification-card.unread {
  border-color: #a78bfa;
  box-shadow: 0 0 0 1px rgba(91, 33, 182, 0.2);
}

.card-top {
  display: flex;
  justify-content: space-between;
  gap: 0.8rem;
  align-items: center;
}

.category-pill {
  text-transform: capitalize;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.5rem;
  border-radius: 999px;
  color: #111827;
  background: #e5e7eb;
}

.category-subscription {
  background: #fee2e2;
  color: #991b1b;
}

.category-offer {
  background: #dcfce7;
  color: #166534;
}

.category-general {
  background: #e0e7ff;
  color: #3730a3;
}

.time-text {
  font-size: 0.78rem;
  color: #6b7280;
}

.notification-card h3 {
  margin: 0.7rem 0 0.5rem;
  font-size: 1.02rem;
  color: #1f2937;
}

.notification-card p {
  margin: 0;
  color: #374151;
  line-height: 1.4;
  text-align: left;
}

.card-footer {
  margin-top: 0.85rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}

.sender-text {
  font-size: 0.82rem;
  color: #6b7280;
}

.mark-btn {
  padding: 0.4rem 0.7rem;
  background: #f59e0b;
  color: #111827;
}

.read-tag {
  font-size: 0.8rem;
  color: #059669;
  font-weight: 700;
}

@media (max-width: 767px) {
  .notifications-page {
    margin: 5rem auto;
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
  }

  .primary-btn,
  .secondary-btn {
    flex: 1;
  }
}
</style>
