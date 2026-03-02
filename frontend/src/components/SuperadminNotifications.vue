<template>
  <section class="superadmin-notifications">
    <header class="page-header">
      <h1>Superadmin Notification Center</h1>
      <p>Send announcements to all library admins or one specific library.</p>
    </header>

    <section class="compose-card">
      <h2>Create Notification</h2>
      <form @submit.prevent="sendNotification" class="compose-form">
        <input
          v-model.trim="form.title"
          type="text"
          maxlength="200"
          placeholder="Title"
          required
        />

        <textarea
          v-model.trim="form.message"
          placeholder="Write message for admins"
          rows="4"
          required
        ></textarea>

        <div class="form-row">
          <select v-model="form.category" required>
            <option value="general">General</option>
            <option value="subscription">Subscription</option>
            <option value="offer">Offer</option>
            <option value="maintenance">Maintenance</option>
          </select>

          <select v-model="targetMode" @change="onTargetModeChange">
            <option value="all">All Libraries</option>
            <option value="library">Specific Library</option>
          </select>

          <select v-if="targetMode === 'library'" v-model="selectedLibraryId" required>
            <option disabled value="">Select library</option>
            <option v-for="library in libraries" :key="library.id" :value="String(library.id)">
              {{ library.name }} (ID: {{ library.id }})
            </option>
          </select>
        </div>

        <div class="actions">
          <button type="button" class="secondary-btn" @click="resetForm">Clear</button>
          <button type="submit" class="primary-btn" :disabled="sending">
            {{ sending ? 'Sending...' : 'Send Notification' }}
          </button>
        </div>
      </form>
    </section>

    <section class="sent-card">
      <div class="sent-header">
        <h2>Sent Notifications</h2>
        <button class="secondary-btn" @click="loadSent" :disabled="loadingSent">
          Refresh
        </button>
      </div>

      <div v-if="loadingSent" class="state-card">Loading sent notifications...</div>
      <div v-else-if="sentNotifications.length === 0" class="state-card">
        No notifications sent yet.
      </div>

      <div v-else class="sent-list">
        <article v-for="item in sentNotifications" :key="item.id" class="sent-item">
          <div class="sent-top">
            <span class="sent-category" :class="`category-${item.category}`">{{ item.category }}</span>
            <span class="sent-time">{{ formatDateTime(item.created_at) }}</span>
          </div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.message }}</p>
          <div class="sent-meta">
            <span>Recipients: {{ item.recipient_count }}</span>
            <span>Unread: {{ item.unread_count }}</span>
            <span v-if="item.target_type === 'library'">Library ID: {{ item.target_library_id }}</span>
            <span v-else>Target: {{ item.target_type }}</span>
          </div>
        </article>
      </div>
    </section>
  </section>
</template>

<script>
import API from '../api'

export default {
  name: 'SuperadminNotifications',
  data() {
    return {
      form: {
        title: '',
        message: '',
        category: 'general',
      },
      targetMode: 'all',
      selectedLibraryId: '',
      libraries: [],
      sentNotifications: [],
      sending: false,
      loadingSent: false,
    }
  },
  mounted() {
    this.bootstrap()
  },
  methods: {
    async bootstrap() {
      await Promise.all([this.loadLibraries(), this.loadSent()])
    },

    async loadLibraries() {
      const res = await API.get('/superadmin/libraries')
      this.libraries = res.data
    },

    async loadSent() {
      this.loadingSent = true
      try {
        const res = await API.get('/notifications/sent', {
          params: { limit: 80 },
        })
        this.sentNotifications = res.data
      } finally {
        this.loadingSent = false
      }
    },

    onTargetModeChange() {
      if (this.targetMode === 'all') {
        this.selectedLibraryId = ''
      }
    },

    resetForm() {
      this.form = {
        title: '',
        message: '',
        category: 'general',
      }
      this.targetMode = 'all'
      this.selectedLibraryId = ''
    },

    async sendNotification() {
      if (!this.form.title || !this.form.message) {
        alert('Title and message are required')
        return
      }

      if (this.targetMode === 'library' && !this.selectedLibraryId) {
        alert('Please select a library')
        return
      }

      const payload = {
        title: this.form.title,
        message: this.form.message,
        category: this.form.category,
      }

      if (this.targetMode === 'library') {
        payload.target_library_id = Number(this.selectedLibraryId)
      }

      this.sending = true
      try {
        await API.post('/notifications/', payload)
        await this.loadSent()
        this.resetForm()
        alert('Notification sent successfully')
      } finally {
        this.sending = false
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
.superadmin-notifications {
  max-width: 90%;
  margin: 5rem auto;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.82);
  border-radius: 16px;
}

.page-header h1 {
  margin: 0;
  color: #1f2937;
}

.page-header p {
  margin: 0.5rem 0 1.2rem;
  color: #4b5563;
}

.compose-card,
.sent-card {
  background: #fff;
  border-radius: 12px;
  padding: 1.2rem;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
}

.sent-card {
  margin-top: 1rem;
}

.compose-card h2,
.sent-card h2 {
  margin: 0 0 0.8rem;
  color: #111827;
}

.compose-form {
  display: grid;
  gap: 0.8rem;
}

.compose-form input,
.compose-form textarea,
.compose-form select {
  border: 1px solid #d1d5db;
  border-radius: 8px;
  padding: 0.65rem 0.75rem;
  font-size: 0.95rem;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.7rem;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.7rem;
}

.primary-btn,
.secondary-btn {
  border: none;
  border-radius: 8px;
  padding: 0.55rem 0.85rem;
  cursor: pointer;
  font-weight: 600;
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

.sent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 0.8rem;
}

.state-card {
  border: 1px dashed #cbd5e1;
  border-radius: 10px;
  padding: 1rem;
  color: #475569;
}

.sent-list {
  display: grid;
  gap: 0.8rem;
}

.sent-item {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 0.85rem;
  text-align: left;
}

.sent-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.6rem;
}

.sent-category {
  text-transform: capitalize;
  border-radius: 999px;
  padding: 0.22rem 0.5rem;
  font-size: 0.74rem;
  font-weight: 700;
  background: #e0e7ff;
  color: #3730a3;
}

.category-subscription {
  background: #fee2e2;
  color: #991b1b;
}

.category-offer {
  background: #dcfce7;
  color: #166534;
}

.sent-time {
  color: #6b7280;
  font-size: 0.8rem;
}

.sent-item h3 {
  margin: 0.55rem 0 0.45rem;
  color: #1f2937;
}

.sent-item p {
  margin: 0;
  color: #374151;
  line-height: 1.4;
}

.sent-meta {
  margin-top: 0.7rem;
  display: flex;
  gap: 0.9rem;
  flex-wrap: wrap;
  color: #475569;
  font-size: 0.82rem;
}

@media (max-width: 900px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 767px) {
  .superadmin-notifications {
    margin: 5rem auto;
    padding: 1rem;
  }

  .actions {
    justify-content: stretch;
  }

  .primary-btn,
  .secondary-btn {
    flex: 1;
  }
}
</style>
