<template>
  <main class="receipt-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section v-if="loading" class="section-shell glass-card loading-card">
      <div class="loader"></div>
      <p>Loading receipt...</p>
    </section>

    <template v-else-if="payment">
      <section class="section-shell controls no-print">
        <button @click="printReceipt" class="action-btn print-btn" type="button">Print Receipt</button>
        <button @click="downloadPDF" class="action-btn download-btn" type="button">Download PDF</button>
        <router-link to="/monthly-payments" class="action-btn back-btn">Back to Payments</router-link>
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
      <router-link to="/monthly-payments" class="action-btn back-btn">Back to Payments</router-link>
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
          backgroundColor: '#10b981',
          color: '#fff',
          borderRadius: '12px',
        },
      }),
      showError: (message) => toast.error(message, {
        position: 'top',
        timeout: 3000,
        style: {
          backgroundColor: '#dc2626',
          color: '#fff',
          borderRadius: '12px',
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
    }
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
        const paymentId = this.$route.params.paymentId
        const res = await API.get(`/monthly-payments/single/${paymentId}`)
        this.payment = res.data
      } catch (err) {
        console.error('Error loading receipt:', err)
        this.showError('Error loading receipt')
        setTimeout(() => {
          this.$router.push('/monthly-payments')
        }, 5000)
      } finally {
        this.loading = false
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

    formatDate(date) {
      const d = new Date(date)
      const day = String(d.getDate()).padStart(2, '0')
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const year = d.getFullYear()
      return `${day}/${month}/${year}`
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
  padding: 6.7rem 0 2.8rem;
  color: #e2e8f0;
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
  width: min(980px, calc(100% - 2rem));
  margin: 0 auto;
}

.glass-card {
  border: 1px solid rgba(255, 255, 255, 0.03);
  background: rgba(148, 163, 184, 0.03);
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
  border: 3px solid rgba(148, 163, 184, 0.4);
  border-top-color: #22d3ee;
  animation: spin 1s linear infinite;
}

.controls {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  margin-bottom: 0.9rem;
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
}

.print-btn {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.35);
  color: #bfdbfe;
}

.download-btn {
  background: rgba(16, 185, 129, 0.2);
  border-color: rgba(16, 185, 129, 0.35);
  color: #a7f3d0;
}

.back-btn {
  background: rgba(148, 163, 184, 0.16);
  border-color: rgba(148, 163, 184, 0.35);
  color: #e2e8f0;
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
    padding-top: 5.4rem;
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
