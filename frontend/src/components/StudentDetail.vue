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
          backgroundColor: 'var(--theme-panel-solid)',
          color: 'var(--theme-text-strong)',
          border: '1px solid var(--theme-brand-border)',
          borderRadius: '12px',
          boxShadow: 'var(--theme-shadow-soft)',
        },
      })
    }

    const showError = (message) => {
      toast.error(message, {
        style: {
          backgroundColor: 'var(--theme-panel-solid)',
          color: 'var(--theme-text-strong)',
          border: '1px solid var(--theme-danger-border)',
          borderRadius: '12px',
          boxShadow: 'var(--theme-shadow-soft)',
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
      return this.payments.reduce((sum, payment) => sum + Number(payment.amount || 0), 0)
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
  --surface: var(--theme-surface);
  --surface-border: var(--theme-surface-border);
  --text-primary: var(--theme-text-primary);
  --text-secondary: var(--theme-text-secondary);

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
  background: var(--theme-mesh-background);
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
  border: 1px solid var(--theme-border);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--theme-text-soft);
  background: var(--theme-surface-soft);
}

.gradient-text {
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
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
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
  color: var(--theme-brand-on);
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
  border: 1px solid var(--theme-border);
  background: var(--theme-surface-soft-strong);
  color: var(--theme-text-primary);
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
  border: 1px solid var(--theme-border-soft);
  background: var(--theme-panel);
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
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
}

.fee-amount,
.amount {
  margin: 0.35rem 0 0;
  font-weight: 700;
  color: var(--theme-brand-pill-text);
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
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
}

.status-left,
.status-unpaid {
  background: var(--theme-danger-soft);
  color: var(--theme-danger-text);
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
  color: var(--theme-text-soft);
  border-bottom: 1px solid var(--theme-border);
  padding: 0.64rem 0.55rem;
}

.payments-table td {
  padding: 0.64rem 0.55rem;
  border-bottom: 1px solid var(--theme-border-soft);
  color: var(--theme-text-primary);
  font-size: 0.9rem;
  vertical-align: middle;
  text-align: left;
}

.payments-table tbody tr:hover {
  background: var(--theme-surface-soft);
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
  /* min-width: 110px; */
}

.action-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-spinner {
  width: 12px;
  height: 12px;
  margin-right: 0.35rem;
  border: 2px solid var(--theme-surface-border);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.action-success {
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
  border-color: var(--theme-success-border);
}

.action-warning {
  background: var(--theme-warning-soft);
  color: var(--theme-warning-text);
  border-color: var(--theme-warning-border);
}

.action-danger {
  background: var(--theme-danger-soft);
  color: var(--theme-danger-text);
  border-color: var(--theme-danger-border);
}

.action-receipt {
  background: var(--theme-info-soft);
  color: var(--theme-info-text);
  border-color: var(--theme-info-border);
}

.action-primary {
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
  color: var(--theme-brand-on);
  border-color: var(--theme-brand-border);
}

.action-ghost {
  background: var(--theme-surface-soft-heavy);
  color: var(--theme-text-primary);
  border-color: var(--theme-border-strong);
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
  border: 3px solid var(--theme-border-strong);
  border-top-color: var(--theme-brand-a);
  animation: spin 1s linear infinite;
}

.muted {
  color: var(--text-secondary);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: var(--theme-overlay);
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
  border: 1px solid var(--theme-border-strong);
  background: var(--theme-panel);
  color: var(--theme-text-primary);
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
  color: var(--theme-text-soft);
}

.field-input {
  width: 100%;
  border-radius: 10px;
  border: 1px solid var(--theme-input-border);
  background: var(--theme-input-bg);
  color: var(--theme-text-primary);
  padding: 0.55rem 0.65rem;
  outline: none;
}

.field-input:focus {
  border-color: var(--theme-brand-border);
  box-shadow: 0 0 0 3px var(--theme-brand-ring);
}

.checkbox-wrap {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--theme-text-soft);
  font-size: 0.85rem;
}

.preview-box {
  border: 1px solid var(--theme-info-border);
  background: var(--theme-info-soft);
  border-radius: 10px;
  padding: 0.55rem 0.65rem;
}

.preview-title {
  margin: 0 0 0.25rem;
  font-size: 0.8rem;
  color: var(--theme-info-text);
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

  /* .section-shell {
    width: min(1240px, calc(100% - 1rem));
  }  */

  
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
