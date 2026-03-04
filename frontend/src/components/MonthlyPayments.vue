<template>
  <main class="monthly-payments-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="section-shell hero">
      <div>
        <p class="kicker">Billing Desk</p>
        <h1>
          Monthly
          <span class="gradient-text">Payments</span>
        </h1>
        <p class="hero-subtitle">Track fee status, mark payments, generate records, and issue receipts in one workflow.</p>
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

        <button @click="generatePayments" :disabled="loading" class="btn btn-solid" type="button">
          {{ loading ? 'Generating...' : 'Generate Records' }}
        </button>

        <router-link to="/reminders" class="btn btn-emerald reminder-link">Send Reminders</router-link>
      </div>

      <div class="filter-grid">
        <label class="field-wrap" for="payment-search">
          <span class="field-label">Search</span>
          <input
            id="payment-search"
            type="text"
            v-model="searchTerm"
            placeholder="Search by student or seat"
            class="field-input"
          />
        </label>

        <label class="field-wrap" for="status-filter">
          <span class="field-label">Status</span>
          <select id="status-filter" v-model="statusFilter" class="field-input">
            <option value="">All Payments</option>
            <option value="paid">Paid Only</option>
            <option value="unpaid">Unpaid Only</option>
          </select>
        </label>
      </div>
    </section>

    <section class="section-shell summary-grid">
      <article class="glass-card stat-card">
        <p class="stat-label">Paid</p>
        <p class="stat-value">{{ paidCount }}</p>
      </article>
      <article class="glass-card stat-card">
        <p class="stat-label">Unpaid</p>
        <p class="stat-value">{{ unpaidCount }}</p>
      </article>
      <article class="glass-card stat-card">
        <p class="stat-label">Total Amount</p>
        <p class="stat-value">₹{{ totalAmount }}</p>
      </article>
      <article class="glass-card stat-card">
        <p class="stat-label">Collected</p>
        <p class="stat-value">₹{{ collectedAmount }}</p>
      </article>
    </section>

    <section v-if="loading" class="section-shell glass-card loading-card">
      <div class="loader"></div>
      <p>Loading payment records...</p>
    </section>

    <section v-else-if="filteredPayments.length > 0" class="section-shell glass-card table-card desktop-view">
      <div class="table-wrap">
        <table class="payments-table">
          <thead>
            <tr>
              <th>Student</th>
              <th>Seat</th>
              <th>Amount</th>
              <th>Joining Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="payment in filteredPayments" :key="payment.id">
              <td>
                <router-link :to="`/students/${payment.student.id}`" class="student-link">
                  <span class="avatar">{{ payment.student.name.charAt(0).toUpperCase() }}</span>
                  <span class="student-name">{{ payment.student.name }}</span>
                </router-link>
              </td>
              <td>
                <span v-if="payment.student.seat?.seat_number" class="seat-pill">{{ payment.student.seat.seat_number }}</span>
                <span v-else class="muted">—</span>
              </td>
              <td>
                <span class="amount">₹{{ formatAmount(payment.amount) }}</span>
              </td>
              <td>{{ formatDate(payment.student.date_of_joining) }}</td>
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
                  <button @click="deletePayment(payment)" class="action-btn action-danger" type="button">Delete</button>
                  <button @click="viewReceipt(payment)" class="action-btn action-receipt" :disabled="!payment.paid" type="button">Receipt</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-else class="section-shell glass-card empty-state">
      <h3>No Payment Records Found</h3>
      <p v-if="searchTerm || statusFilter">Try adjusting search or filter values.</p>
      <p v-else>Click "Generate Records" to create payment records for this month.</p>
    </section>

    <section v-if="!loading && filteredPayments.length > 0" class="section-shell mobile-view">
      <article
        v-for="payment in filteredPayments"
        :key="payment.id"
        class="glass-card payment-card"
      >
        <header class="card-head">
          <router-link :to="`/students/${payment.student.id}`" class="student-link">
            <span class="avatar">{{ payment.student.name.charAt(0).toUpperCase() }}</span>
            <div>
              <p class="student-name">{{ payment.student.name }}</p>
              <p class="muted">Seat: {{ payment.student.seat?.seat_number || 'Not assigned' }}</p>
            </div>
          </router-link>
          <span class="status-pill" :class="payment.paid ? 'status-paid' : 'status-unpaid'">
            {{ payment.paid ? 'Paid' : 'Unpaid' }}
          </span>
        </header>

        <div class="detail-grid">
          <div class="detail-row">
            <span class="muted">Amount</span>
            <span class="amount">₹{{ formatAmount(payment.amount) }}</span>
          </div>
          <div class="detail-row">
            <span class="muted">Joining Date</span>
            <span>{{ formatDate(payment.student.date_of_joining) }}</span>
          </div>
        </div>

        <div class="actions mobile-actions">
          <button
            @click="togglePaid(payment)"
            class="action-btn"
            :class="payment.paid ? 'action-warning' : 'action-success'"
            type="button"
          >
            {{ payment.paid ? 'Mark Unpaid' : 'Mark Paid' }}
          </button>
          <button @click="deletePayment(payment)" class="action-btn action-danger" type="button">Delete</button>
          <button @click="viewReceipt(payment)" class="action-btn action-receipt" :disabled="!payment.paid" type="button">Receipt</button>
        </div>
      </article>
    </section>

    <ConfirmationModal
      :show="showConfirmationModal"
      title="Payment Confirmed"
      :message="`Send confirmation message to ${selectedPayment?.student?.name.toUpperCase()}?`"
      @whatsapp="sendWhatsAppConfirmation"
      @sms="sendSMSConfirmation"
      @cancel="closeModal"
    />
  </main>
</template>

<script>
import API from '../api'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'
import ConfirmationModal from './ConfirmationModal.vue'

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
      payments: [],
      searchTerm: '',
      statusFilter: '',
      showConfirmationModal: false,
      selectedPayment: null,
      loading: false,
    }
  },

  computed: {
    filteredPayments() {
      return this.payments.filter((payment) => {
        const search = this.searchTerm.trim().toLowerCase()
        const matchesName = payment.student.name.toLowerCase().includes(search)
        const seatNum = payment.student.seat?.seat_number ? String(payment.student.seat.seat_number) : ''
        const matchesSeat = seatNum.includes(search)

        const matchesStatus =
          this.statusFilter === '' ||
          (this.statusFilter === 'paid' && payment.paid) ||
          (this.statusFilter === 'unpaid' && !payment.paid)

        return (matchesName || matchesSeat) && matchesStatus
      })
    },

    paidCount() {
      return this.filteredPayments.filter((payment) => payment.paid).length
    },

    unpaidCount() {
      return this.filteredPayments.filter((payment) => !payment.paid).length
    },

    totalAmount() {
      return this.filteredPayments.reduce((sum, payment) => sum + payment.amount, 0).toLocaleString('en-IN')
    },

    collectedAmount() {
      return this.filteredPayments
        .filter((payment) => payment.paid)
        .reduce((sum, payment) => sum + payment.amount, 0)
        .toLocaleString('en-IN')
    },
  },

  mounted() {
    this.fetchPayments()
  },

  watch: {
    selectedMonth: {
      handler: 'fetchPayments',
      immediate: false,
    },
  },

  methods: {
    async fetchPayments() {
      this.loading = true
      try {
        const res = await API.get(`/monthly-payments/${this.selectedMonth}`)
        this.payments = res.data
      } catch (err) {
        this.showError('Error fetching monthly payments')
      } finally {
        this.loading = false
      }
    },

    async togglePaid(payment) {
      try {
        const res = await API.put(`/monthly-payments/toggle/${payment.id}`)
        payment.paid = res.data.paid

        if (payment.paid) {
          this.showSuccess('Payment marked as paid!')
          this.showConfirmationModal = true
          this.selectedPayment = payment
        } else {
          this.showSuccess('Payment marked as unpaid')
        }
      } catch (err) {
        this.showError('Failed to toggle status')
      }
    },

    sendWhatsAppConfirmation() {
      this.sendPaymentConfirmation(this.selectedPayment)
      this.closeModal()
    },

    sendSMSConfirmation() {
      this.sendSMS(this.selectedPayment)
      this.closeModal()
    },

    closeModal() {
      this.showConfirmationModal = false
      this.selectedPayment = null
    },

    sendPaymentConfirmation(payment) {
      const libraryName = localStorage.getItem('library_name') || 'Your Library'
      const monthDate = new Date(this.selectedMonth + '-01')
      const monthName = monthDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })

      const msg =
        `Dear ${payment.student.name},\n` +
        `We have received your library fee of ₹${payment.amount} for ${monthName}.\n` +
        `Your payment has been successfully recorded.\n\n` +
        `Thanks,\n${libraryName}`

      const phone = '91' + payment.student.contact.replace(/^0+/, '')
      const url = `https://wa.me/${phone}?text=${encodeURIComponent(msg)}`
      window.open(url, '_blank')
      this.showSuccess('WhatsApp confirmation sent!')
    },

    sendSMS(payment) {
      const libraryName = localStorage.getItem('library_name') || 'Your Library'
      const monthDate = new Date(this.selectedMonth + '-01')
      const monthName = monthDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })

      const msg =
        `Dear ${payment.student.name},\n` +
        `We have received your library fee of ₹${payment.amount} for ${monthName}.\n` +
        `Your payment has been successfully recorded.\n\n` +
        `Thanks,\n${libraryName}`

      const phone = payment.student.contact.replace(/^(\+91|91)/, '')
      const url = `sms:${phone}?body=${encodeURIComponent(msg)}`
      window.open(url, '_blank')
      this.showSuccess('SMS confirmation sent!')
    },

    async deletePayment(payment) {
      if (!confirm('Are you sure you want to delete this payment record?')) return

      try {
        await API.delete(`/monthly-payments/${payment.id}`)
        this.payments = this.payments.filter((entry) => entry.id !== payment.id)
        this.showSuccess('Payment record deleted successfully')
      } catch (err) {
        this.showError('Error deleting payment')
      }
    },

    async generatePayments() {
      this.loading = true
      try {
        const monthDate = new Date(this.selectedMonth + '-01')
        const monthName = monthDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
        await API.post(`/generate-monthly-payments/${this.selectedMonth}`)
        this.showSuccess(`Payment records generated for ${monthName}`)
        this.fetchPayments()
      } catch (err) {
        this.showError('Error generating payment records')
      } finally {
        this.loading = false
      }
    },

    formatDate(dateString) {
      const date = new Date(dateString)
      const day = String(date.getDate()).padStart(2, '0')
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const year = String(date.getFullYear()).slice(-2)
      return `${day}-${month}-${year}`
    },

    formatAmount(amount) {
      return amount.toLocaleString('en-IN')
    },

    viewReceipt(payment) {
      if (!payment.paid) {
        this.showError('Payment not marked as paid yet')
        return
      }
      this.$router.push(`/receipts/${payment.id}`)
    },
  },
}
</script>

<style scoped>
.monthly-payments-page {
  --surface: rgba(148, 163, 184, 0.03);
  --surface-border: rgba(255, 255, 255, 0.03);
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;

  position: relative;
  min-height: 100vh;
  padding: 2rem 2rem 2.8rem;
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
  /* max-width: 62ch; */
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

.control-grid,
.filter-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.6rem;
  align-items: end;
}

.filter-grid {
  grid-template-columns: 1fr 1fr;
  margin-top: 0.6rem;
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
  /* min-height: 42px; */
  padding: 0.5rem 0.7rem;
  outline: none;
}

.field-input:focus {
  border-color: rgba(34, 211, 238, 0.62);
  box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.16);
}

.field-input option {
  color: #0f172a;
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
  /* padding: 0.5rem 0.75rem; */
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  color: #fff;
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-solid {
  background: linear-gradient(90deg, #0ea5e9, #3b82f6);
  box-shadow: 0 14px 28px rgba(59, 130, 246, 0.28);
}

.btn-emerald {
  background: linear-gradient(90deg, #22c55e, #16a34a);
}

.summary-grid {
  margin-top: 0.85rem;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
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

.payments-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 980px;
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
  text-align: left;
}

.payments-table tbody tr:hover {
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

.seat-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 52px;
  padding: 0.28rem 0.55rem;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 700;
  background: rgba(16, 185, 129, 0.2);
  color: #a7f3d0;
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

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.status-paid {
  background: rgba(16, 185, 129, 0.2);
  color: #a7f3d0;
}

.status-unpaid {
  background: rgba(239, 68, 68, 0.2);
  color: #fecaca;
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
  padding: 0.3rem 0.5rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: #fff;
  cursor: pointer;
}

.action-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
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

.action-receipt {
  background: rgba(59, 130, 246, 0.2);
  color: #bfdbfe;
  border-color: rgba(59, 130, 246, 0.36);
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

.payment-card {
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

.mobile-actions {
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
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

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
  .monthly-payments-page {
    padding-top: 2rem;
    padding-bottom: 5rem;
    padding-inline: 1rem;
  }

  .section-shell {
    width: min(1240px, calc(100% - 1rem));
  }

  .filter-grid{
    grid-template-columns: 1fr;
  }
  
  .summary-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
