<template>
  <main class="student-detail-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="section-shell hero">
      <div>
        <p class="kicker">Student Profile</p>
        <h1>
          Student
          <span class="gradient-text">Overview</span>
        </h1>
      </div>
    </section>

    <section v-if="loading" class="section-shell glass-card loading-card">
      <div class="loader"></div>
      <p>Loading student details...</p>
    </section>

    <template v-else>
      <section v-if="student" class="section-shell glass-card profile-card">
        <div class="profile-head">
          <span class="avatar">{{ student.name.charAt(0).toUpperCase() }}</span>
          <div>
            <h2 class="student-name">{{ student.name }}</h2>
            <div class="meta-row">
              <span class="meta-item">Contact: {{ student.contact }}</span>
              <span class="meta-item">Joined: {{ formatDate(student.date_of_joining) }}</span>
              <span class="meta-item">Seat: {{ student.seat?.seat_number || 'Not assigned' }}</span>
              <span class="status-pill" :class="student.status === 'active' ? 'status-active' : 'status-left'">
                {{ student.status }}
              </span>
            </div>
          </div>
        </div>

        <div class="info-grid">
          <div class="info-box">
            <p class="info-label">Enrolled Shifts</p>
            <div class="shift-pills">
              <span v-if="student.shift1" class="shift-pill">Shift 1</span>
              <span v-if="student.shift2" class="shift-pill">Shift 2</span>
              <span v-if="student.shift3" class="shift-pill">Shift 3</span>
              <span v-if="!student.shift1 && !student.shift2 && !student.shift3" class="muted">No shifts selected</span>
            </div>
          </div>
          <div class="info-box">
            <p class="info-label">Monthly Fee</p>
            <p class="fee-amount">₹{{ formatAmount(student.custom_fees || 0) }}</p>
          </div>
        </div>
      </section>

      <section v-if="payments.length > 0" class="section-shell summary-grid">
        <article class="glass-card stat-card">
          <p class="stat-label">Paid</p>
          <p class="stat-value">{{ paidCount }}</p>
        </article>
        <article class="glass-card stat-card">
          <p class="stat-label">Unpaid</p>
          <p class="stat-value">{{ unpaidCount }}</p>
        </article>
        <article class="glass-card stat-card">
          <p class="stat-label">Total</p>
          <p class="stat-value">₹{{ formatAmount(totalAmount) }}</p>
        </article>
      </section>

      <section class="section-shell">
        <header class="payments-head">
          <h3>Monthly Payments</h3>
        </header>

        <div v-if="payments.length > 0" class="glass-card table-card desktop-view">
          <div class="table-wrap">
            <table class="payments-table">
              <thead>
                <tr>
                  <th>Month</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="payment in payments" :key="payment.id">
                  <td>{{ formatMonth(payment.month) }}</td>
                  <td class="amount">₹{{ formatAmount(payment.amount) }}</td>
                  <td>
                    <span class="status-pill" :class="payment.paid ? 'status-paid' : 'status-unpaid'">
                      {{ payment.paid ? 'Paid' : 'Unpaid' }}
                    </span>
                  </td>
                  <td>
                    <div class="actions">
                      <button
                        @click="togglePaid(payment)"
                        class="action-btn"
                        :class="payment.paid ? 'action-warning' : 'action-success'"
                        type="button"
                      >
                        {{ payment.paid ? 'Mark Unpaid' : 'Mark Paid' }}
                      </button>
                      <button @click="deletePayment(payment.id)" class="action-btn action-danger" type="button">Delete</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="payments.length > 0" class="mobile-view">
          <article
            v-for="payment in payments"
            :key="payment.id"
            class="glass-card payment-card"
          >
            <header class="card-head">
              <div>
                <p class="payment-month">{{ formatMonth(payment.month) }}</p>
                <p class="amount">₹{{ formatAmount(payment.amount) }}</p>
              </div>
              <span class="status-pill" :class="payment.paid ? 'status-paid' : 'status-unpaid'">
                {{ payment.paid ? 'Paid' : 'Unpaid' }}
              </span>
            </header>

            <div class="actions mobile-actions">
              <button
                @click="togglePaid(payment)"
                class="action-btn"
                :class="payment.paid ? 'action-warning' : 'action-success'"
                type="button"
              >
                {{ payment.paid ? 'Mark Unpaid' : 'Mark Paid' }}
              </button>
              <button @click="deletePayment(payment.id)" class="action-btn action-danger" type="button">Delete</button>
            </div>
          </article>
        </div>

        <section v-if="payments.length === 0" class="glass-card empty-state">
          <h3>No Payment Records</h3>
          <p>No payment history found for this student.</p>
        </section>
      </section>
    </template>
  </main>
</template>

<script>
import API from '../api'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'

export default {
  setup() {
    const toast = useToast()

    const showSuccess = (message) => {
      toast.success(message, {
        position: 'top',
        timeout: 3000,
        style: {
          backgroundColor: '#0ea5e9',
          color: '#fff',
          borderRadius: '12px',
        },
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

    return { showSuccess, showError }
  },

  data() {
    return {
      student: null,
      payments: [],
      loading: false,
    }
  },

  computed: {
    paidCount() {
      return this.payments.filter((payment) => payment.paid).length
    },

    unpaidCount() {
      return this.payments.filter((payment) => !payment.paid).length
    },

    totalAmount() {
      return this.payments.reduce((sum, payment) => sum + payment.amount, 0)
    },
  },

  async mounted() {
    const id = this.$route.params.id
    this.loading = true
    try {
      await Promise.all([
        this.fetchStudent(id),
        this.fetchPayments(id),
      ])
    } finally {
      this.loading = false
    }
  },

  methods: {
    async fetchStudent(id) {
      try {
        const res = await API.get(`/students/${id}`)
        this.student = res.data
      } catch (err) {
        this.showError('Failed to load student details')
      }
    },

    async fetchPayments(id) {
      try {
        const res = await API.get(`/students/${id}/payments`)
        this.payments = res.data
      } catch (err) {
        this.showError('Failed to load payment history')
      }
    },

    async togglePaid(payment) {
      try {
        const res = await API.put(`/monthly-payments/toggle/${payment.id}`)
        payment.paid = res.data.paid

        if (payment.paid) {
          this.showSuccess('Payment marked as paid!')
        } else {
          this.showSuccess('Payment marked as unpaid')
        }
      } catch (err) {
        this.showError('Failed to update payment status')
      }
    },

    async deletePayment(id) {
      if (!confirm('Are you sure you want to delete this payment record?')) return

      try {
        await API.delete(`/monthly-payments/${id}`)
        this.payments = this.payments.filter((payment) => payment.id !== id)
        this.showSuccess('Payment record deleted successfully')
      } catch (err) {
        this.showError('Failed to delete payment record')
      }
    },

    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      const date = new Date(dateStr)
      const day = String(date.getDate()).padStart(2, '0')
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const year = date.getFullYear()
      return `${day}-${month}-${year}`
    },

    formatMonth(monthStr) {
      if (!monthStr) return 'N/A'
      const [year, month] = monthStr.split('-')
      const date = new Date(parseInt(year), parseInt(month) - 1)
      return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    },

    formatAmount(amount) {
      return Number(amount || 0).toLocaleString('en-IN')
    },
  },
}
</script>

<style scoped>
.student-detail-page {
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

.glass-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.profile-card,
.table-card,
.empty-state,
.loading-card {
  margin-top: 0.9rem;
  border-radius: 16px;
  padding: 0.9rem;
}

.profile-head {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
}

.avatar {
  width: 54px;
  height: 54px;
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
  font-size: 1.15rem;
}

.meta-row {
  margin-top: 0.45rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.meta-item {
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  background: rgba(15, 23, 42, 0.58);
  color: #dbeafe;
  padding: 0.22rem 0.55rem;
  font-size: 0.74rem;
  font-weight: 700;
}

.info-grid {
  margin-top: 0.7rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.55rem;
}

.info-box {
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.24);
  background: rgba(15, 23, 42, 0.45);
  padding: 0.6rem;
}

.info-label {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.shift-pills {
  margin-top: 0.35rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.shift-pill {
  border-radius: 999px;
  padding: 0.2rem 0.5rem;
  font-size: 0.74rem;
  font-weight: 700;
  background: rgba(16, 185, 129, 0.22);
  color: #a7f3d0;
}

.fee-amount,
.amount {
  margin: 0.35rem 0 0;
  font-weight: 700;
  color: #fecaca;
  font-family: Monaco, Menlo, monospace;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.status-active,
.status-paid {
  background: rgba(16, 185, 129, 0.2);
  color: #a7f3d0;
}

.status-left,
.status-unpaid {
  background: rgba(239, 68, 68, 0.2);
  color: #fecaca;
}

.summary-grid {
  margin-top: 0.85rem;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
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

.payments-head {
  margin-top: 0.8rem;
  margin-bottom: 0.3rem;
}

.payments-head h3 {
  margin: 0;
}

.table-wrap {
  overflow-x: auto;
}

.payments-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 760px;
}

.payments-table th {
  text-align: left;
  font-size: 0.82rem;
  font-weight: 700;
  color: #cbd5e1;
  border-bottom: 1px solid rgba(148, 163, 184, 0.26);
  padding: 0.64rem 0.55rem;
}

.payments-table td {
  padding: 0.64rem 0.55rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.16);
  color: #e2e8f0;
  font-size: 0.9rem;
  vertical-align: middle;
}

.payments-table tbody tr:hover {
  background: rgba(148, 163, 184, 0.07);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.action-btn {
  min-height: 32px;
  border-radius: 9px;
  border: 1px solid transparent;
  padding: 0.3rem 0.55rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
}

.action-success {
  background: rgba(16, 185, 129, 0.2);
  color: #a7f3d0;
  border-color: rgba(16, 185, 129, 0.36);
}

.action-warning {
  background: rgba(245, 158, 11, 0.2);
  color: #fde68a;
  border-color: rgba(245, 158, 11, 0.36);
}

.action-danger {
  background: rgba(239, 68, 68, 0.16);
  color: #fecaca;
  border-color: rgba(239, 68, 68, 0.36);
}

.mobile-view {
  display: none;
  margin-top: 0.85rem;
  gap: 0.55rem;
}

.payment-card {
  border-radius: 14px;
  padding: 0.7rem;
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.55rem;
}

.payment-month {
  margin: 0;
  font-weight: 700;
}

.mobile-actions {
  margin-top: 0.55rem;
}

.empty-state,
.loading-card {
  text-align: center;
  display: grid;
  place-items: center;
  gap: 0.35rem;
}

.loader {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 3px solid rgba(148, 163, 184, 0.4);
  border-top-color: #22d3ee;
  animation: spin 1s linear infinite;
}

.muted {
  color: var(--text-secondary);
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

@media (max-width: 920px) {
  .desktop-view {
    display: none;
  }

  .mobile-view {
    display: grid;
  }
}

@media (max-width: 767px) {
  .student-detail-page {
    padding-top: 5.4rem;
  }

  .section-shell {
    width: min(1240px, calc(100% - 1rem));
  }

  .info-grid,
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
