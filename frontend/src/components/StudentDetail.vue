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
          <button class="action-btn action-primary add-payments-btn" type="button" @click="openBulkPaymentModal">
            Add Payments
          </button>
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
                        :disabled="isPaymentToggling(payment.id)"
                        type="button"
                      >
                        <span v-if="isPaymentToggling(payment.id)" class="btn-spinner" aria-hidden="true"></span>
                        {{ isPaymentToggling(payment.id) ? 'Updating...' : (payment.paid ? 'Mark Unpaid' : 'Mark Paid') }}
                      </button>
                      <button
                        v-if="payment.paid"
                        @click="viewReceipt(payment.id)"
                        class="action-btn action-receipt"
                        :disabled="isPaymentToggling(payment.id)"
                        type="button"
                      >
                        Receipt
                      </button>
                      <button
                        @click="deletePayment(payment.id)"
                        class="action-btn action-danger"
                        :disabled="isPaymentToggling(payment.id)"
                        type="button"
                      >
                        Delete
                      </button>
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
                :disabled="isPaymentToggling(payment.id)"
                type="button"
              >
                <span v-if="isPaymentToggling(payment.id)" class="btn-spinner" aria-hidden="true"></span>
                {{ isPaymentToggling(payment.id) ? 'Updating...' : (payment.paid ? 'Mark Unpaid' : 'Mark Paid') }}
              </button>
              <button
                v-if="payment.paid"
                @click="viewReceipt(payment.id)"
                class="action-btn action-receipt"
                :disabled="isPaymentToggling(payment.id)"
                type="button"
              >
                Receipt
              </button>
              <button
                @click="deletePayment(payment.id)"
                class="action-btn action-danger"
                :disabled="isPaymentToggling(payment.id)"
                type="button"
              >
                Delete
              </button>
            </div>
          </article>
        </div>

        <section v-if="payments.length === 0" class="glass-card empty-state">
          <h3>No Payment Records</h3>
          <p>No payment history found for this student.</p>
        </section>
      </section>

      <div v-if="showBulkPaymentModal" class="modal-overlay" @click.self="closeBulkPaymentModal">
        <div class="modal-content glass-card">
          <header class="modal-head">
            <h3>Add Advance Payments</h3>
            <button class="modal-close" type="button" @click="closeBulkPaymentModal" aria-label="Close modal">×</button>
          </header>

          <form class="bulk-form" @submit.prevent="submitBulkPayments">
            <label class="field-wrap">
              <span class="field-label">Month Selection Mode</span>
              <select v-model="bulkPaymentForm.monthMode" class="field-input">
                <option value="range">Start Month + Number of Months</option>
                <option value="custom">Select Specific Months</option>
              </select>
            </label>

            <template v-if="bulkPaymentForm.monthMode === 'range'">
              <label class="field-wrap">
                <span class="field-label">Start Month</span>
                <input v-model="bulkPaymentForm.startMonth" type="month" class="field-input" required />
              </label>

              <label class="field-wrap">
                <span class="field-label">Number of Months</span>
                <input
                  v-model.number="bulkPaymentForm.numberOfMonths"
                  type="number"
                  min="1"
                  max="24"
                  class="field-input"
                  required
                />
              </label>
            </template>

            <template v-else>
              <label class="field-wrap">
                <span class="field-label">Specific Months (comma separated)</span>
                <input
                  v-model="bulkPaymentForm.customMonthsText"
                  type="text"
                  class="field-input"
                  placeholder="2026-04, 2026-05, 2026-07"
                  required
                />
              </label>
            </template>

            <label class="field-wrap">
              <span class="field-label">Total Fees Paid (optional)</span>
              <input
                v-model.number="bulkPaymentForm.totalAmountPaid"
                type="number"
                min="1"
                class="field-input"
                placeholder="Leave empty to use student monthly fee"
              />
            </label>

            <label class="checkbox-wrap">
              <input v-model="bulkPaymentForm.markAsPaid" type="checkbox" />
              <span>Mark generated records as paid now</span>
            </label>

            <div class="preview-box" v-if="previewMonths.length">
              <p class="preview-title">Preview</p>
              <p class="preview-text">Months: {{ previewMonths.join(', ') }}</p>
              <p class="preview-text">
                Amount per month:
                <span v-if="bulkPaymentForm.totalAmountPaid">₹{{ formatAmount(previewPerMonthAmount) }}</span>
                <span v-else>Student monthly fee (₹{{ formatAmount(student?.custom_fees || student?.total_fee || 0) }})</span>
              </p>
            </div>

            <div class="modal-actions">
              <button type="button" class="action-btn action-ghost" @click="closeBulkPaymentModal">Cancel</button>
              <button type="submit" class="action-btn action-primary" :disabled="submittingBulk">
                {{ submittingBulk ? 'Saving...' : 'Create Payments' }}
              </button>
            </div>
          </form>
        </div>
      </div>
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
    const today = new Date()
    const defaultMonth = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`
    return {
      student: null,
      payments: [],
      loading: false,
      showBulkPaymentModal: false,
      submittingBulk: false,
      togglingPaymentIds: {},
      bulkPaymentForm: {
        monthMode: 'range',
        startMonth: defaultMonth,
        numberOfMonths: 1,
        customMonthsText: '',
        totalAmountPaid: null,
        markAsPaid: true,
      },
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

    previewMonths() {
      return this.getMonthsForSubmission(false)
    },

    previewPerMonthAmount() {
      if (!this.bulkPaymentForm.totalAmountPaid || !this.previewMonths.length) return 0
      return Math.floor(this.bulkPaymentForm.totalAmountPaid / this.previewMonths.length)
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
      if (this.isPaymentToggling(payment.id)) return
      this.togglingPaymentIds[payment.id] = true
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
      } finally {
        delete this.togglingPaymentIds[payment.id]
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

    viewReceipt(paymentId) {
      this.$router.push(`/receipts/${paymentId}`)
    },

    openBulkPaymentModal() {
      this.showBulkPaymentModal = true
    },

    closeBulkPaymentModal() {
      this.showBulkPaymentModal = false
      this.submittingBulk = false
    },

    parseCustomMonths() {
      return (this.bulkPaymentForm.customMonthsText || '')
        .split(',')
        .map((value) => value.trim())
        .filter((value) => value.length > 0)
    },

    buildRangeMonths() {
      const startMonth = this.bulkPaymentForm.startMonth
      const count = Number(this.bulkPaymentForm.numberOfMonths || 0)
      if (!startMonth || count < 1 || count > 24) return []

      const [startYear, startMonthNum] = startMonth.split('-').map(Number)
      if (!startYear || !startMonthNum) return []

      const months = []
      let year = startYear
      let month = startMonthNum

      for (let i = 0; i < count; i += 1) {
        months.push(`${year}-${String(month).padStart(2, '0')}`)
        month += 1
        if (month > 12) {
          month = 1
          year += 1
        }
      }
      return months
    },

    getMonthsForSubmission(throwOnInvalid = true) {
      const months = this.bulkPaymentForm.monthMode === 'custom'
        ? this.parseCustomMonths()
        : this.buildRangeMonths()

      const uniqueMonths = [...new Set(months)].sort()
      const monthPattern = /^\d{4}-\d{2}$/
      const hasInvalid = uniqueMonths.some((value) => !monthPattern.test(value))

      if (throwOnInvalid && hasInvalid) {
        throw new Error('Months must be in YYYY-MM format')
      }
      if (throwOnInvalid && (!uniqueMonths.length || uniqueMonths.length > 24)) {
        throw new Error('Select between 1 and 24 months')
      }

      return hasInvalid ? [] : uniqueMonths
    },

    async submitBulkPayments() {
      if (!this.student?.id) return

      let selectedMonths = []
      try {
        selectedMonths = this.getMonthsForSubmission(true)
      } catch (error) {
        this.showError(error.message || 'Invalid month selection')
        return
      }

      const payload = {
        start_month: this.bulkPaymentForm.startMonth || selectedMonths[0],
        number_of_months: Number(this.bulkPaymentForm.numberOfMonths || selectedMonths.length || 1),
        mark_as_paid: !!this.bulkPaymentForm.markAsPaid,
        total_amount_paid: this.bulkPaymentForm.totalAmountPaid ? Number(this.bulkPaymentForm.totalAmountPaid) : null,
        selected_months: this.bulkPaymentForm.monthMode === 'custom' ? selectedMonths : null,
      }

      this.submittingBulk = true
      try {
        const res = await API.post(`/students/${this.student.id}/payments/bulk`, payload)
        await this.fetchPayments(this.student.id)
        const { created = 0, updated = 0, skipped = 0 } = res.data || {}
        this.showSuccess(`Payments updated. Created: ${created}, Updated: ${updated}, Skipped: ${skipped}`)
        this.closeBulkPaymentModal()
      } catch (err) {
        this.showError(err.response?.data?.detail || 'Failed to create bulk payments')
      } finally {
        this.submittingBulk = false
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

    isPaymentToggling(paymentId) {
      return !!this.togglingPaymentIds[paymentId]
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
  padding: 2rem 1rem 2.8rem 3rem;
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
  justify-content: center;
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
  justify-content: center;
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
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
  text-align: left;
}

.payments-table tbody tr:hover {
  background: rgba(148, 163, 184, 0.07);
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  /* justify-content: space-between; */
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
  width: auto;
  min-width: 110px;
}

.action-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-spinner {
  width: 12px;
  height: 12px;
  margin-right: 0.35rem;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
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
  background: rgba(59, 130, 246, 0.18);
  color: #bfdbfe;
  border-color: rgba(59, 130, 246, 0.36);
}

.action-primary {
  background: linear-gradient(90deg, #0ea5e9, #3b82f6);
  color: #fff;
  border-color: rgba(59, 130, 246, 0.32);
}

.action-ghost {
  background: rgba(148, 163, 184, 0.18);
  color: #e2e8f0;
  border-color: rgba(148, 163, 184, 0.34);
}

.add-payments-btn {
  min-width: 130px;
}

.mobile-view {
  display: none;
  margin-top: 0.85rem;
  gap: 0.55rem;
}

.payment-card {
  border-radius: 14px;
  padding: 0.7rem;
  overflow: auto;
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

.mobile-actions .action-btn {
  width: 30%;
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

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(2, 8, 23, 0.72);
  display: grid;
  place-items: center;
  padding: 1rem 2rem;
}

.modal-content {
  width: min(560px, 100%);
  border-radius: 16px;
  padding: 0.9rem;
  text-align: left;
}

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.8rem;
}

.modal-head h3 {
  margin: 0;
}

.modal-close {
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.6);
  color: #e2e8f0;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  cursor: pointer;
}

.bulk-form {
  display: grid;
  gap: 0.65rem;
}

.field-wrap {
  display: grid;
  gap: 0.33rem;
  width: webkit-fit-content;
  margin-right: 1rem;
}

.field-label {
  font-size: 0.78rem;
  color: #cbd5e1;
}

.field-input {
  width: 100%;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  background: rgba(15, 23, 42, 0.62);
  color: #e2e8f0;
  padding: 0.55rem 0.65rem;
  outline: none;
}

.field-input:focus {
  border-color: rgba(56, 189, 248, 0.7);
}

.checkbox-wrap {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #cbd5e1;
  font-size: 0.85rem;
}

.preview-box {
  border: 1px solid rgba(56, 189, 248, 0.3);
  background: rgba(56, 189, 248, 0.08);
  border-radius: 10px;
  padding: 0.55rem 0.65rem;
}

.preview-title {
  margin: 0 0 0.25rem;
  font-size: 0.8rem;
  color: #bae6fd;
  font-weight: 700;
}

.preview-text {
  margin: 0.2rem 0 0;
  font-size: 0.8rem;
}

.modal-actions {
  margin-top: 0.45rem;
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 0.5rem;
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
  .student-detail-page {
    padding: 2rem 1rem 5rem 1rem;
  }

  .desktop-view {
    display: none;
  }

  .mobile-view {
    display: grid;
  }
}

@media (max-width: 767px) {
  .student-detail-page {
    padding: 2rem 1rem 5rem 1rem;
  }

  .section-shell {
    width: min(1240px, calc(100% - 1rem));
  }

  
  .summary-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .info-grid{
    grid-template-columns: 2fr 1fr;
  }

  .actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  justify-content: space-between;
  flex-flow: row;
  overflow: auto;
}
}
</style>
