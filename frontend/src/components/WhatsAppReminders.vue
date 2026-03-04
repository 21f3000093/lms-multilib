<template>
  <main class="reminders-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="section-shell hero">
      <div>
        <p class="kicker">Communication Desk</p>
        <h1>
          Fee
          <span class="gradient-text">Reminders</span>
        </h1>
        <p class="hero-subtitle">Review unpaid students for the selected month and send reminders through WhatsApp or SMS.</p>
      </div>
    </section>

    <section class="section-shell controls-card glass-card">
      <div class="control-grid">
        <label class="field-wrap" for="month-input">
          <span class="field-label">Select Month</span>
          <input
            id="month-input"
            type="month"
            v-model="selectedMonth"
            class="field-input month-input"
          />
        </label>

        <button @click="$router.back()" class="btn btn-ghost" type="button">Back</button>
        <button @click="fetchReminders" :disabled="loading" class="btn btn-solid" type="button">
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </section>

    <section v-if="pendingList.length > 0" class="section-shell summary-grid">
      <article class="glass-card stat-card">
        <p class="stat-label">Pending Students</p>
        <p class="stat-value">{{ pendingList.length }}</p>
      </article>
      <article class="glass-card stat-card">
        <p class="stat-label">Total Pending</p>
        <p class="stat-value">₹{{ totalPendingAmount }}</p>
      </article>
    </section>

    <section v-if="loading" class="section-shell glass-card loading-card">
      <div class="loader"></div>
      <p>Loading pending reminders...</p>
    </section>

    <section v-else-if="pendingList.length > 0" class="section-shell glass-card table-card desktop-view">
      <div class="table-wrap">
        <table class="reminders-table">
          <thead>
            <tr>
              <th>Student</th>
              <th>Phone</th>
              <th>Amount</th>
              <th>Month</th>
              <th>Due Date</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in pendingList" :key="student.phone">
              <td>
                <router-link :to="`/students/${student.student_id}`" class="student-link">
                  <span class="avatar">{{ student.student_name.charAt(0).toUpperCase() }}</span>
                  <span class="student-name">{{ student.student_name }}</span>
                </router-link>
              </td>
              <td class="mono">{{ student.phone }}</td>
              <td class="amount">₹{{ formatAmount(student.amount) }}</td>
              <td>{{ formatMonth(student.month) }}</td>
              <td>
                <span class="due-pill" :class="{ overdue: isOverdue(student.due_date) }">
                  {{ formatDate(student.due_date) }}
                </span>
              </td>
              <td>
                <button @click="openReminderModal(student)" class="action-btn action-success" type="button">
                  Send Reminder
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-else class="section-shell glass-card empty-state">
      <h3>No Pending Reminders</h3>
      <p>All students have paid their fees on time for {{ formatMonth(selectedMonth) }}.</p>
    </section>

    <section v-if="!loading && pendingList.length > 0" class="section-shell mobile-view">
      <article
        v-for="student in pendingList"
        :key="student.phone"
        class="glass-card reminder-card"
      >
        <header class="card-head">
          <router-link :to="`/students/${student.student_id}`" class="student-link">
            <span class="avatar">{{ student.student_name.charAt(0).toUpperCase() }}</span>
            <div>
              <p class="student-name">{{ student.student_name }}</p>
              <p class="mono muted">{{ student.phone }}</p>
            </div>
          </router-link>
          <span class="due-pill" :class="{ overdue: isOverdue(student.due_date) }">
            {{ formatDate(student.due_date) }}
          </span>
        </header>

        <div class="detail-grid">
          <div class="detail-row">
            <span class="muted">Amount</span>
            <span class="amount">₹{{ formatAmount(student.amount) }}</span>
          </div>
          <div class="detail-row">
            <span class="muted">Month</span>
            <span>{{ formatMonth(student.month) }}</span>
          </div>
        </div>

        <button @click="openReminderModal(student)" class="action-btn action-success mobile-action" type="button">
          Send Reminder
        </button>
      </article>
    </section>

    <ConfirmationModal
      :show="showReminderModal"
      title="Send Fee Reminder"
      :message="`Send payment reminder to ${selectedStudent?.student_name?.toUpperCase()}?`"
      @whatsapp="sendReminderWhatsApp"
      @sms="sendReminderSMS"
      @cancel="closeReminderModal"
    />
  </main>
</template>

<script>
import API from '../api'
import ConfirmationModal from './ConfirmationModal.vue'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'

export default {
  components: {
    ConfirmationModal,
  },

  setup() {
    const toast = useToast()

    const showSuccess = (message, options = {}) => {
      toast.success(message, {
        position: 'top',
        timeout: 3000,
        closeOnClick: true,
        pauseOnFocusLoss: true,
        pauseOnHover: true,
        draggable: true,
        draggablePercent: 0.6,
        showCloseButtonOnHover: false,
        hideProgressBar: true,
        closeButton: 'button',
        icon: true,
        rtl: false,
        style: {
          backgroundColor: '#0ea5e9',
          color: '#fff',
          borderRadius: '12px',
        },
        ...options,
      })
    }

    const showError = (message) => {
      toast.error(message, {
        style: {
          backgroundColor: '#dc2626',
          color: '#fff',
          borderRadius: '12px',
        },
      })
    }

    return {
      showSuccess,
      showError,
    }
  },

  data() {
    const today = new Date()
    const defaultMonth = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`
    return {
      selectedMonth: defaultMonth,
      pendingList: [],
      showReminderModal: false,
      selectedStudent: null,
      loading: false,
    }
  },

  computed: {
    totalPendingAmount() {
      return this.pendingList.reduce((sum, student) => sum + student.amount, 0).toLocaleString('en-IN')
    },
  },

  methods: {
    async fetchReminders() {
      this.loading = true
      try {
        const res = await API.get(`/reminders/pending-fees/${this.selectedMonth}`)
        this.pendingList = res.data
      } catch (err) {
        this.showError('Failed to fetch reminders: ' + (err.response?.data?.detail || err.message))
      } finally {
        this.loading = false
      }
    },

    openReminderModal(student) {
      this.selectedStudent = student
      this.showReminderModal = true
    },

    closeReminderModal() {
      this.showReminderModal = false
      this.selectedStudent = null
    },

    sendReminderWhatsApp() {
      const message = this.generateReminderMessage()
      const phone = '91' + this.selectedStudent.phone.replace(/^0+/, '')
      const url = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`
      window.open(url, '_blank')
      this.closeReminderModal()
      this.showSuccess('WhatsApp reminder sent!')
    },

    sendReminderSMS() {
      const message = this.generateReminderMessage()
      const phone = this.selectedStudent.phone.replace(/^(\+91|91)/, '')
      const url = `sms:${phone}?body=${encodeURIComponent(message)}`
      window.open(url, '_blank')
      this.closeReminderModal()
      this.showSuccess('SMS reminder sent!')
    },

    generateReminderMessage() {
      const libraryName = localStorage.getItem('library_name') || 'Your Library'
      const monthDate = new Date(this.selectedStudent.month + '-01')
      const monthName = monthDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })

      return (
        `Dear ${this.selectedStudent.student_name},\n` +
        `Your library fee of Rs.${this.selectedStudent.amount} for ${monthName} was due on ${this.selectedStudent.due_date}.\n` +
        `Please pay it as soon as possible to avoid disruption.\n\n` +
        `Thanks,\n${libraryName}`
      )
    },

    formatAmount(amount) {
      return amount.toLocaleString('en-IN')
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      const day = String(date.getDate()).padStart(2, '0')
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const year = String(date.getFullYear()).slice(-2)
      return `${day}-${month}-${year}`
    },

    formatMonth(monthString) {
      if (monthString && monthString.includes('-')) {
        const [year, month] = monthString.split('-')
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return `${monthNames[parseInt(month) - 1]} ${year}`
      }
      return monthString
    },

    isOverdue(dueDateString) {
      if (!dueDateString) return false
      const dueDate = new Date(dueDateString)
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      return dueDate < today
    },
  },

  created() {
    this.fetchReminders()
  },

  watch: {
    selectedMonth: {
      handler: 'fetchReminders',
      immediate: false,
    },
  },
}
</script>

<style scoped>
.reminders-page {
  --surface: rgba(148, 163, 184, 0.03);
  --surface-border: rgba(255, 255, 255, 0.03);
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;

  position: relative;
  min-height: 100vh;
  padding: 6.7rem 0 2.8rem;
  color: var(--text-primary);
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
  width: min(1240px, calc(100% - 2rem));
  margin: 0 auto;
}

.hero h1 {
  margin: 0.9rem 0 0;
  font-size: clamp(1.9rem, 4.4vw, 3rem);
  line-height: 1.05;
  letter-spacing: -0.03em;
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

.gradient-text {
  background: linear-gradient(90deg, #22d3ee, #3b82f6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-subtitle {
  margin: 0.75rem 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 62ch;
}

.glass-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.controls-card,
.table-card,
.loading-card,
.empty-state {
  margin-top: 0.9rem;
  border-radius: 16px;
  padding: 0.9rem;
}

.control-grid {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 0.6rem;
  align-items: end;
}

.field-wrap {
  display: grid;
  gap: 0.35rem;
}

.field-label {
  color: #cbd5e1;
  font-size: 0.8rem;
  font-weight: 600;
}

.field-input {
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.72);
  color: #f8fafc;
  min-height: 42px;
  padding: 0.5rem 0.7rem;
  outline: none;
}

.field-input:focus {
  border-color: rgba(34, 211, 238, 0.62);
  box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.16);
}

.month-input {
  color-scheme: dark;
}

.month-input::-webkit-calendar-picker-indicator {
  filter: invert(1) brightness(1.35) saturate(0.25);
  opacity: 0.95;
}

.btn {
  min-height: 42px;
  border-radius: 12px;
  border: 1px solid transparent;
  padding: 0.5rem 0.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-solid {
  background: linear-gradient(90deg, #0ea5e9, #3b82f6);
  box-shadow: 0 14px 28px rgba(59, 130, 246, 0.28);
  color: #fff;
}

.btn-ghost {
  background: rgba(148, 163, 184, 0.08);
  border-color: rgba(148, 163, 184, 0.32);
  color: #e2e8f0;
}

.summary-grid {
  margin-top: 0.85rem;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.6rem;
}

.stat-card {
  border-radius: 14px;
  padding: 0.75rem;
}

.stat-label {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.stat-value {
  margin: 0.32rem 0 0;
  font-size: 1.3rem;
  font-weight: 800;
}

.table-wrap {
  overflow-x: auto;
}

.reminders-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 920px;
}

.reminders-table th {
  text-align: left;
  font-size: 0.82rem;
  font-weight: 700;
  color: #cbd5e1;
  border-bottom: 1px solid rgba(148, 163, 184, 0.26);
  padding: 0.64rem 0.55rem;
}

.reminders-table td {
  padding: 0.64rem 0.55rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.16);
  color: #e2e8f0;
  font-size: 0.9rem;
  vertical-align: middle;
}

.reminders-table tbody tr:hover {
  background: rgba(148, 163, 184, 0.07);
}

.student-link {
  display: inline-flex;
  align-items: center;
  gap: 0.52rem;
  color: inherit;
  text-decoration: none;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: inline-grid;
  place-items: center;
  font-weight: 800;
  background: linear-gradient(90deg, #0ea5e9, #3b82f6);
  color: #fff;
  flex-shrink: 0;
}

.student-name {
  margin: 0;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.85rem;
}

.mono {
  font-family: Monaco, Menlo, monospace;
}

.muted {
  color: var(--text-secondary);
  margin: 0;
}

.amount {
  font-weight: 700;
  color: #fecaca;
  font-family: Monaco, Menlo, monospace;
}

.due-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.22rem 0.58rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  background: rgba(16, 185, 129, 0.2);
  color: #a7f3d0;
}

.due-pill.overdue {
  background: rgba(239, 68, 68, 0.2);
  color: #fecaca;
}

.action-btn {
  min-height: 34px;
  border-radius: 10px;
  border: 1px solid transparent;
  padding: 0.35rem 0.6rem;
  font-size: 0.78rem;
  font-weight: 700;
  cursor: pointer;
}

.action-success {
  background: rgba(16, 185, 129, 0.2);
  color: #a7f3d0;
  border-color: rgba(16, 185, 129, 0.36);
}

.loading-card,
.empty-state {
  display: grid;
  place-items: center;
  gap: 0.35rem;
  text-align: center;
}

.loader {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 3px solid rgba(148, 163, 184, 0.4);
  border-top-color: #22d3ee;
  animation: spin 1s linear infinite;
}

.mobile-view {
  display: none;
  margin-top: 0.85rem;
  gap: 0.55rem;
}

.reminder-card {
  border-radius: 14px;
  padding: 0.7rem;
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
}

.detail-grid {
  margin-top: 0.55rem;
  display: grid;
  gap: 0.45rem;
}

.detail-row {
  border-radius: 10px;
  background: rgba(148, 163, 184, 0.12);
  padding: 0.45rem 0.55rem;
  display: flex;
  justify-content: space-between;
  gap: 0.55rem;
}

.mobile-action {
  width: 100%;
  margin-top: 0.55rem;
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
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1100px) {
  .control-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 920px) {
  .desktop-view {
    display: none;
  }

  .mobile-view {
    display: grid;
  }
}

@media (max-width: 767px) {
  .reminders-page {
    padding-top: 5.4rem;
  }

  .section-shell {
    width: min(1240px, calc(100% - 1rem));
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
