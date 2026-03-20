<template>
  <main class="receipt-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section v-if="loading" class="section-shell glass-card loading-card">
      <div class="loader"></div>
      <p>Loading receipt...</p>
    </section>

    <template v-else-if="payment">
      <section class="section-shell controls no-print">
        <!-- <button @click="printReceipt" class="action-btn print-btn" type="button">Print Receipt</button> -->
        <button @click="downloadPDF" class="action-btn download-btn" type="button">Download PDF</button>
        <button
          v-if="!isPublicMode"
          @click="sendReceiptWhatsApp"
          class="action-btn whatsapp-btn"
          type="button"
          :disabled="shareLinkLoading"
        >
          {{ shareLinkLoading ? 'Preparing...' : 'Send on WhatsApp' }}
        </button>
        <!-- <router-link v-if="!isPublicMode" to="/monthly-payments" class="action-btn back-btn">Back to Payments</router-link> -->
      </section>

      <section id="receipt-content" class="section-shell receipt-wrapper">
        <article class="receipt-container">
          <header class="receipt-header">
            <div class="company-info">
              <h1 class="company-name">{{ libraryName }}</h1>
              <p class="company-address" v-if="libraryAddress">{{ libraryAddress }}</p>
              <p class="company-contact" v-if="libraryContact">Contact: {{ libraryContact }}</p>
            </div>
            <div class="receipt-title-box">
              <h2 class="receipt-title">PAYMENT RECEIPT</h2>
            </div>
          </header>

          <section class="receipt-info-section">
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Receipt No:</span>
                <span class="info-value">#{{ String(payment.id).padStart(6, '0') }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Date:</span>
                <span class="info-value">{{ formatDate(new Date()) }}</span>
              </div>
              <div class="info-item full-width">
                <span class="info-label">Payment For:</span>
                <span class="info-value">{{ formatMonth(payment.month) }}</span>
              </div>
              <div class="info-item full-width">
                <span class="info-label">Payment Timestamp:</span>
                <span class="info-value">
                  {{ payment.paid_at ? formatDateTime(payment.paid_at) : (payment.paid ? 'Recorded before timestamp tracking' : 'Pending / Not paid yet') }}
                </span>
              </div>
              <div class="info-item full-width">
                <span class="info-label">Billing Period:</span>
                <span class="info-value">{{ formatBillingPeriod(payment.period_start, payment.period_end, payment.month, payment.student?.date_of_joining) }}</span>
              </div>
              <div class="info-item full-width">
                <span class="info-label">Next Due Date:</span>
                <span class="info-value">{{ resolveNextDueDate(payment) }}</span>
              </div>
            </div>
          </section>

          <section class="section-box">
            <h3 class="section-title">Student Details</h3>
            <div class="detail-grid">
              <div class="detail-row">
                <span class="detail-label">Name:</span>
                <span class="detail-value">{{ payment.student.name }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Contact:</span>
                <span class="detail-value">{{ payment.student.contact }}</span>
              </div>
              <div class="detail-row" v-if="payment.student.seat">
                <span class="detail-label">Seat Number:</span>
                <span class="detail-value">{{ payment.student.seat.seat_number }}</span>
              </div>
            </div>
          </section>

          <section class="section-box">
            <h3 class="section-title">Payment Details</h3>
            <table class="payment-table">
              <thead>
                <tr>
                  <th>Description</th>
                  <th>Amount</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Library Fee - {{ formatMonth(payment.month) }}</td>
                  <td class="amount-cell">₹{{ formatAmount(payment.amount) }}</td>
                </tr>
              </tbody>
              <tfoot>
                <tr class="total-row">
                  <td><strong>Total Amount Paid</strong></td>
                  <td class="amount-cell"><strong>₹{{ formatAmount(payment.amount) }}</strong></td>
                </tr>
              </tfoot>
            </table>
          </section>

          <section class="status-section">
            <div class="status-badge" :class="payment.paid ? 'paid-badge' : 'unpaid-badge'">
              {{ payment.paid ? 'PAID' : 'UNPAID' }}
            </div>
          </section>

          <footer class="receipt-footer">
            <p>Thank you for your payment!</p>
            <div class="signature-line">
              <span>_____________________</span>
              <p>Authorized Signature</p>
            </div>
          </footer>
        </article>
      </section>
    </template>

    <section v-else class="section-shell glass-card empty-state">
      <h3>Receipt Not Found</h3>
      <p>Unable to load the payment receipt.</p>
      <router-link :to="isPublicMode ? '/login' : '/monthly-payments'" class="action-btn back-btn">
        {{ isPublicMode ? 'Go to Login' : 'Back to Payments' }}
      </router-link>
    </section>
  </main>
</template>

<script>
import API from '../api'
import { useToast } from 'vue-toast-notification'
import html2pdf from 'html2pdf.js'

export default {
  setup() {
    const toast = useToast()
    return {
      showSuccess: (message) => toast.success(message, {
        position: 'top',
        timeout: 3000,
        style: {
          backgroundColor: 'var(--theme-panel-solid)',
          color: 'var(--theme-text-strong)',
          border: '1px solid var(--theme-success-border)',
          borderRadius: '12px',
          boxShadow: 'var(--theme-shadow-soft)',
        },
      }),
      showError: (message) => toast.error(message, {
        position: 'top',
        timeout: 3000,
        style: {
          backgroundColor: 'var(--theme-panel-solid)',
          color: 'var(--theme-text-strong)',
          border: '1px solid var(--theme-danger-border)',
          borderRadius: '12px',
          boxShadow: 'var(--theme-shadow-soft)',
        },
      }),
    }
  },

  data() {
    return {
      payment: null,
      libraryName: '',
      libraryAddress: '',
      libraryContact: '',
      loading: true,
      shareLinkLoading: false,
    }
  },

  computed: {
    isPublicMode() {
      return Boolean(this.$route.params.token)
    },
  },

  mounted() {
    this.loadLibraryInfo()
    this.fetchPayment()
  },

  methods: {
    loadLibraryInfo() {
      this.libraryName = localStorage.getItem('library_name') || 'Library Name'
      this.libraryAddress = localStorage.getItem('library_address') || ''
      this.libraryContact = localStorage.getItem('library_contact') || ''
    },

    async fetchPayment() {
      this.loading = true
      try {
        const { paymentId, token } = this.$route.params
        if (token) {
          const res = await API.get(`/public-receipts/${token}`)
          this.payment = res.data?.payment || null
          this.libraryName = res.data?.library_name || this.libraryName
          this.libraryAddress = res.data?.library_address || this.libraryAddress
          this.libraryContact = res.data?.library_contact || this.libraryContact
        } else {
          const res = await API.get(`/monthly-payments/single/${paymentId}`)
          this.payment = res.data
        }
      } catch (err) {
        console.error('Error loading receipt:', err)
        this.showError(this.isPublicMode ? 'Invalid or expired receipt link' : 'Error loading receipt')
        if (!this.isPublicMode) {
          setTimeout(() => {
            this.$router.push('/monthly-payments')
          }, 5000)
        }
      } finally {
        this.loading = false
      }
    },

    normalizeWhatsAppPhone(rawPhone) {
      const digits = String(rawPhone || '').replace(/\D/g, '')
      if (!digits) return ''
      if (digits.length === 10) return `91${digits}`
      if (digits.length === 11 && digits.startsWith('0')) return `91${digits.slice(1)}`
      if (digits.length === 12 && digits.startsWith('91')) return digits
      if (digits.length >= 11 && digits.length <= 15) return digits
      return ''
    },

    buildWhatsAppMessage(shareUrl) {
      const studentName = this.payment?.student?.name || 'Student'
      const month = this.formatMonth(this.payment?.month || '')
      const amount = this.formatAmount(this.payment?.amount || 0)
      const library = this.libraryName || 'Smart Library App'

      return (
        `Hi ${studentName},\n` +
        `Your fee receipt for ${month} is ready.\n` +
        `Amount Paid: Rs.${amount}\n` +
        `Receipt Link: ${shareUrl}\n\n` +
        `Thanks,\n${library}`
      )
    },

    async sendReceiptWhatsApp() {
      if (!this.payment?.id) return

      const phone = this.normalizeWhatsAppPhone(this.payment?.student?.contact)
      if (!phone) {
        this.showError('Student phone number is missing or invalid')
        return
      }

      this.shareLinkLoading = true
      try {
        const res = await API.get(`/monthly-payments/${this.payment.id}/share-link`)
        const token = res.data?.token
        const shareUrl = res.data?.share_url || (token ? `${window.location.origin}/public-receipts/${token}` : '')
        if (!shareUrl) {
          throw new Error('Share URL not returned')
        }

        const message = this.buildWhatsAppMessage(shareUrl)
        const whatsappUrl = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`
        window.open(whatsappUrl, '_blank', 'noopener')
        this.showSuccess('WhatsApp opened with receipt link')
      } catch (err) {
        const apiError = err?.response?.data?.detail
        this.showError(apiError || 'Unable to prepare WhatsApp receipt link')
      } finally {
        this.shareLinkLoading = false
      }
    },

    printReceipt() {
      window.print()
    },

    async downloadPDF() {
      const element = document.getElementById('receipt-content')

      const opt = {
        margin: [8, 8, 8, 8],
        filename: `Receipt_${String(this.payment.id).padStart(6, '0')}_${this.payment.month}.pdf`,
        image: {
          type: 'jpeg',
          quality: 0.98,
        },
        html2canvas: {
          scale: 2.5,
          useCORS: true,
          letterRendering: true,
          logging: false,
        },
        jsPDF: {
          unit: 'mm',
          format: 'a4',
          orientation: 'portrait',
          compress: true,
        },
        pagebreak: {
          mode: ['avoid-all', 'css', 'legacy'],
        },
      }

      try {
        this.showSuccess('Generating PDF...')
        await html2pdf().set(opt).from(element).save()
        this.showSuccess('Receipt downloaded successfully')
      } catch (error) {
        console.error('PDF download error:', error)
        this.showError('Error downloading PDF')
      }
    },

    formatDate(value) {
      if (!value) return 'N/A'

      if (typeof value === 'string') {
        const ymdMatch = value.match(/^(\d{4})-(\d{2})-(\d{2})/)
        if (ymdMatch) {
          return `${ymdMatch[3]}/${ymdMatch[2]}/${ymdMatch[1]}`
        }
      }

      const d = new Date(value)
      if (Number.isNaN(d.getTime())) return 'N/A'
      const day = String(d.getDate()).padStart(2, '0')
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const year = d.getFullYear()
      return `${day}/${month}/${year}`
    },

    formatDateTime(dateTimeValue) {
      if (!dateTimeValue) return 'N/A'
      const d = new Date(dateTimeValue)
      if (Number.isNaN(d.getTime())) return 'N/A'
      const datePart = d.toLocaleDateString('en-GB', { timeZone: 'Asia/Kolkata' })
      const timePart = d.toLocaleTimeString('en-IN', {
        timeZone: 'Asia/Kolkata',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true,
      })
      return `${datePart} ${timePart} IST`
    },

    getDueDayFromJoining(joiningDate) {
      if (!joiningDate) return 1
      if (typeof joiningDate === 'string') {
        const ymdMatch = joiningDate.match(/^(\d{4})-(\d{2})-(\d{2})/)
        if (ymdMatch) {
          return Math.max(1, Math.min(31, Number(ymdMatch[3])))
        }
      }
      const parsed = new Date(joiningDate)
      if (Number.isNaN(parsed.getTime())) return 1
      return Math.max(1, Math.min(31, parsed.getDate()))
    },

    computeDueDateString(year, month, dueDay) {
      const lastDay = new Date(year, month, 0).getDate()
      const day = Math.min(dueDay, lastDay)
      return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    },

    computeNextDueDate(monthStr, joiningDate) {
      if (!monthStr) return null
      const [yearStr, monthStrNum] = monthStr.split('-')
      const year = Number(yearStr)
      const month = Number(monthStrNum)
      if (!year || !month) return null

      const dueDay = this.getDueDayFromJoining(joiningDate)
      const nextMonth = month === 12 ? 1 : month + 1
      const nextYear = month === 12 ? year + 1 : year
      return this.computeDueDateString(nextYear, nextMonth, dueDay)
    },

    formatBillingPeriod(periodStart, periodEnd, monthStr, joiningDate) {
      if (monthStr) {
        const [yearStr, monthStrNum] = monthStr.split('-')
        const year = Number(yearStr)
        const month = Number(monthStrNum)
        if (year && month) {
          const dueDay = this.getDueDayFromJoining(joiningDate)
          const currentDue = this.computeDueDateString(year, month, dueDay)
          const nextDue = this.computeNextDueDate(monthStr, joiningDate)

          if (nextDue) {
            const periodEndDate = new Date(`${nextDue}T00:00:00`)
            periodEndDate.setDate(periodEndDate.getDate() - 1)
            return `${this.formatDate(currentDue)} - ${this.formatDate(periodEndDate)}`
          }
        }
      }

      if (periodStart && periodEnd) {
        return `${this.formatDate(periodStart)} - ${this.formatDate(periodEnd)}`
      }

      return 'N/A'
    },

    resolveNextDueDate(payment) {
      const dueDate = this.computeNextDueDate(payment?.month, payment?.student?.date_of_joining) || payment?.next_due_date
      return dueDate ? this.formatDate(dueDate) : 'N/A'
    },

    formatMonth(monthStr) {
      const date = new Date(monthStr + '-01')
      return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
    },

    formatAmount(amount) {
      return Number(amount || 0).toLocaleString('en-IN')
    },
  },
}
</script>

<style scoped>
.receipt-page {
  position: relative;
  min-height: 100vh;
  padding: 2rem 1rem 2.8rem 3rem;
  color: var(--theme-text-primary);
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
  width: min(980px, calc(100% - 2rem));
  margin: 0 auto;
}

.glass-card {
  border: 1px solid var(--theme-surface-border);
  background: var(--theme-surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.loading-card,
.empty-state {
  border-radius: 16px;
  padding: 1rem;
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

.controls {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-bottom: 0.9rem;
  justify-content: center;
}

.action-btn {
  min-height: 42px;
  border-radius: 12px;
  border: 1px solid transparent;
  padding: 0.5rem 0.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  min-width: 20%;
}

.print-btn {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.35);
  color: #bfdbfe;
}

.download-btn {
  background: linear-gradient(135deg, var(--theme-info-solid), var(--theme-brand-b));
  border-color: transparent;
  color: #f8fafc;
  box-shadow: var(--theme-shadow-elevated);
}

.whatsapp-btn {
  background: linear-gradient(135deg, var(--theme-success-solid), var(--theme-success-solid-alt));
  border-color: transparent;
  color: #f8fafc;
  box-shadow: var(--theme-shadow-elevated);
}

.back-btn {
  background: var(--theme-surface-soft-strong);
  border-color: var(--theme-border-strong);
  color: var(--theme-text-primary);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.receipt-wrapper {
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
}

.receipt-container {
  position: relative;
  padding: 24px;
  background: #fff;
  color: #1f2937;
  font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
}

.receipt-header {
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 3px solid #3b82f6;
}

.company-info {
  text-align: center;
}

.company-name {
  margin: 0;
  font-size: 30px;
  font-weight: 800;
}

.company-address,
.company-contact {
  margin: 4px 0 0;
  font-size: 13px;
  color: #6b7280;
}

.receipt-title-box {
  margin-top: 14px;
  background: linear-gradient(90deg, #0ea5e9, #3b82f6);
  border-radius: 8px;
  padding: 10px 16px;
  text-align: center;
}

.receipt-title {
  margin: 0;
  font-size: 22px;
  letter-spacing: 1.3px;
  color: #fff;
}

.receipt-info-section,
.section-box {
  margin-bottom: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  background: #f9fafb;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  padding: 8px;
  border-radius: 6px;
  background: #fff;
}

.full-width {
  grid-column: 1 / -1;
}

.info-label,
.detail-label {
  font-weight: 700;
  color: #4b5563;
}

.info-value,
.detail-value {
  color: #111827;
  font-weight: 600;
}

.section-title {
  margin: 0 0 10px;
  font-size: 16px;
  font-weight: 700;
  color: #374151;
}

.detail-grid {
  display: grid;
  gap: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 8px;
  border-radius: 6px;
  background: #fff;
}

.payment-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
}

.payment-table th,
.payment-table td {
  border: 1px solid #e5e7eb;
  padding: 10px;
  text-align: left;
}

.payment-table thead th {
  background: #f3f4f6;
}

.amount-cell {
  text-align: right;
  font-weight: 700;
}

.total-row td {
  background: #f9fafb;
}

.status-section {
  display: flex;
  justify-content: center;
  margin: 16px 0;
}

.status-badge {
  padding: 8px 22px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 800;
  letter-spacing: 1px;
}

.paid-badge {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #86efac;
}

.unpaid-badge {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

.receipt-footer {
  margin-top: 16px;
  text-align: center;
  border-top: 1px dashed #d1d5db;
  padding-top: 14px;
}

.signature-line {
  margin-top: 18px;
}

.signature-line p {
  margin: 4px 0 0;
  font-size: 13px;
  color: #6b7280;
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

@media (max-width: 767px) {
  .receipt-page {
    padding: 2rem 1rem 5rem;
  }

  .section-shell {
    width: min(980px, calc(100% - 1rem));
  }

  .controls {
    flex-direction: column;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}

@media print {
  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }

  .no-print,
  .mesh-layer {
    display: none !important;
  }

  .receipt-page {
    background: white !important;
    color: black !important;
    padding: 0 !important;
    min-height: auto !important;
    overflow: visible !important;
  }

  .section-shell {
    width: 100% !important;
    margin: 0 !important;
  }

  .receipt-wrapper {
    box-shadow: none !important;
    border-radius: 0 !important;
  }

  .receipt-container {
    padding: 20px !important;
  }
}
</style>
