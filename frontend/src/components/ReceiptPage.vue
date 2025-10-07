<template>
  <div class="receipt-page">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner">⏳</div>
      <p>Loading receipt...</p>
    </div>

    <!-- Main Content -->
    <template v-else-if="payment">
      <!-- Print/Download Controls -->
      <div class="controls no-print">
        <button @click="printReceipt" class="action-btn print-btn">
          <!-- <span class="btn-icon">🖨️</span> -->
          <span class="btn-text">Print Receipt</span>
        </button>
        <button @click="downloadPDF" class="action-btn download-btn">
          <!-- <span class="btn-icon">📥</span> -->
          <span class="btn-text">Download PDF</span>
        </button>
        <router-link to="/monthly-payments" class="back-btn">
          <!-- <span class="btn-icon">←</span> -->
          <span class="btn-text">Back to Payments</span>
        </router-link>
      </div>

      <!-- Receipt Content - Optimized for PDF -->
      <div id="receipt-content" class="receipt-wrapper">
        <div class="receipt-container">
          <!-- Header with Border -->
          <div class="receipt-header">
            <div class="company-info">
              <h1 class="company-name">{{ libraryName }}</h1>
              <p class="company-address" v-if="libraryAddress">{{ libraryAddress }}</p>
              <p class="company-contact" v-if="libraryContact">📞 {{ libraryContact }}</p>
            </div>
            <div class="receipt-title-box">
              <h2 class="receipt-title">PAYMENT RECEIPT</h2>
            </div>
          </div>

          <!-- Receipt Info Section -->
          <div class="receipt-info-section">
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
          </div>

          <!-- Student Details Section -->
          <div class="section-box">
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
          </div>

          <!-- Payment Details Table -->
          <div class="section-box">
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
          </div>

          <!-- Payment Status Badge -->
          <div class="status-section">
            <div class="status-badge" :class="payment.paid ? 'paid-badge' : 'unpaid-badge'">
              <span class="status-icon">{{ payment.paid ? '✓' : '×' }}</span>
              <span class="status-text">{{ payment.paid ? 'PAID' : 'UNPAID' }}</span>
            </div>
          </div>

          <!-- Footer -->
          <div class="receipt-footer">
            <div class="thank-you-message">
              <p>Thank you for your payment!</p>
              <!-- <p class="footer-note">This is a computer-generated receipt and does not require a physical signature.</p> -->
            </div>
            <div class="signature-section">
              <div class="signature-line">
                <span>_____________________</span>
                <p class="signature-label">Authorized Signature</p>
              </div>
            </div>
          </div>

          <!-- Watermark -->
          <!-- <div class="receipt-watermark" v-if="payment.paid">PAID</div> -->
        </div>
      </div>
    </template>

    <!-- Error State -->
    <div v-else class="empty-state">
      <div class="empty-icon">❌</div>
      <h3>Receipt Not Found</h3>
      <p>Unable to load the payment receipt.</p>
      <router-link to="/monthly-payments" class="back-btn">
        <!-- <span class="btn-icon">←</span> -->
        <span class="btn-text">Back to Payments</span>
      </router-link>
    </div>
  </div>
</template>

<script>
import API from '../api';
import { useToast } from 'vue-toast-notification';
import html2pdf from 'html2pdf.js';

export default {
  setup() {
    const toast = useToast();
    return {
      showSuccess: (message) => toast.success(message, {
        position: 'top',
        timeout: 3000,
        style: {
          backgroundColor: '#10b981',
          color: '#fff',
          borderRadius: '12px'
        }
      }),
      showError: (message) => toast.error(message, {
        position: 'top',
        timeout: 3000,
        style: {
          backgroundColor: '#dc2626',
          color: '#fff',
          borderRadius: '12px'
        }
      })
    };
  },

  data() {
    return {
      payment: null,
      libraryName: '',
      libraryAddress: '',
      libraryContact: '',
      loading: true
    };
  },

  mounted() {
    this.loadLibraryInfo();
    this.fetchPayment();
  },

  methods: {
    loadLibraryInfo() {
      this.libraryName = localStorage.getItem('library_name') || 'Library Name';
      this.libraryAddress = localStorage.getItem('library_address') || '';
      this.libraryContact = localStorage.getItem('library_contact') || '';
    },

    async fetchPayment() {
      this.loading = true;
      try {
        const paymentId = this.$route.params.paymentId;
        const res = await API.get(`/monthly-payments/single/${paymentId}`);
        this.payment = res.data;
      } catch (err) {
        console.error('Error loading receipt:', err);
        this.showError('Error loading receipt');
        setTimeout(() => {
          this.$router.push('/monthly-payments');
        }, 5000);
      } finally {
        this.loading = false;
      }
    },

    printReceipt() {
      window.print();

    },

    async downloadPDF() {
      const element = document.getElementById('receipt-content');
      
      // High-quality PDF options
      const opt = {
        margin: [8, 8, 8, 8],
        filename: `Receipt_${String(this.payment.id).padStart(6, '0')}_${this.payment.month}.pdf`,
        image: { 
          type: 'jpeg', 
          quality: 0.98 
        },
        html2canvas: { 
          scale: 2.5, // Higher scale for better quality
          useCORS: true,
          letterRendering: true,
          logging: false
        },
        jsPDF: { 
          unit: 'mm', 
          format: 'a4', 
          orientation: 'portrait',
          compress: true
        },
        pagebreak: { 
          mode: ['avoid-all', 'css', 'legacy'] 
        }
      };
      
      try {
        this.showSuccess('⏳ Generating PDF...');
        await html2pdf().set(opt).from(element).save();
        this.showSuccess('✅ Receipt downloaded successfully');
      } catch (error) {
        console.error('PDF download error:', error);
        this.showError('❌ Error downloading PDF');
      }
    },

    formatDate(date) {
      const d = new Date(date);
      const day = String(d.getDate()).padStart(2, '0');
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const year = d.getFullYear();
      return `${day}/${month}/${year}`;
    },

    formatMonth(monthStr) {
      const date = new Date(monthStr + '-01');
      return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    },

    formatAmount(amount) {
      return amount.toLocaleString('en-IN');
    }
  }
};
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.receipt-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  background: #f5f5f500;
  padding-top: 6rem;
}

/* Loading and Error States */
.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.loading-spinner {
  font-size: 48px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 24px;
  color: #1f2937;
  margin: 10px 0;
}

.empty-state p {
  color: #6b7280;
  margin-bottom: 30px;
}

/* Controls */
.controls {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn, .back-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.print-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.print-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.download-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.download-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.back-btn {
  background: #e5e7eb;
  color: #374151;
}

.back-btn:hover {
  background: #d1d5db;
}

/* Receipt Wrapper */
.receipt-wrapper {
  background: white;
  padding: 0;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.receipt-container {
  position: relative;
  padding: 30px;
  background: white;
  font-family: 'Arial', 'Helvetica', sans-serif;
  color: #1f2937;
  line-height: 1.5;
}

/* Header */
.receipt-header {
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 3px solid #667eea;
}

.company-info {
  text-align: center;
  margin-bottom: 20px;
}

.company-name {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
  letter-spacing: 0.5px;
}

.company-address {
  font-size: 14px;
  color: #6b7280;
  margin: 4px 0;
}

.company-contact {
  font-size: 14px;
  color: #6b7280;
  margin: 4px 0;
  font-weight: 500;
}

.receipt-title-box {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 12px 24px;
  text-align: center;
  border-radius: 8px;
  margin-top: 16px;
}

.receipt-title {
  font-size: 24px;
  font-weight: 700;
  color: white;
  margin: 0;
  letter-spacing: 2px;
}

/* Receipt Info Section */
.receipt-info-section {
  background: #f9fafb;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  border: 1px solid #e5e7eb;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-label {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
}

.info-value {
  font-size: 15px;
  font-weight: 700;
  color: #1f2937;
}

/* Section Box */
.section-box {
  margin-bottom: 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  background: white;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #667eea;
}

/* Detail Grid */
.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
  min-width: 120px;
}

.detail-value {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  text-align: right;
}

/* Payment Table */
.payment-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 12px;
}

.payment-table th {
  background: #f3f4f6;
  padding: 12px;
  text-align: left;
  font-size: 14px;
  font-weight: 700;
  color: #374151;
  border: 1px solid #e5e7eb;
}

.payment-table td {
  padding: 12px;
  font-size: 14px;
  color: #1f2937;
  border: 1px solid #e5e7eb;
}

.payment-table .amount-cell {
  text-align: right;
  font-weight: 600;
}

.payment-table tfoot .total-row {
  background: #f9fafb;
}

.payment-table tfoot td {
  font-size: 16px;
  padding: 14px 12px;
}

/* Status Section */
.status-section {
  display: flex;
  justify-content: center;
  margin: 24px 0;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 32px;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
}

.paid-badge {
  background: #d1fae5;
  color: #065f46;
  border: 2px solid #10b981;
}

.unpaid-badge {
  background: #fee2e2;
  color: #991b1b;
  border: 2px solid #ef4444;
}

.status-icon {
  font-size: 20px;
  font-weight: 700;
}

/* Footer */
.receipt-footer {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 2px solid #e5e7eb;
}

.thank-you-message {
  text-align: center;
  margin-bottom: 24px;
}

.thank-you-message p {
  font-size: 15px;
  color: #374151;
  margin: 8px 0;
  font-weight: 600;
}

.footer-note {
  font-size: 12px !important;
  color: #9ca3af !important;
  font-weight: 400 !important;
  font-style: italic;
}

.signature-section {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.signature-line {
  text-align: center;
}

.signature-line span {
  display: block;
  margin-bottom: 8px;
  color: #9ca3af;
}

.signature-label {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
  font-weight: 600;
}

/* Watermark */
.receipt-watermark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-45deg);
  font-size: 120px;
  font-weight: 900;
  color: rgba(16, 185, 129, 0.08);
  pointer-events: none;
  z-index: 0;
  letter-spacing: 10px;
}

.receipt-container > * {
  position: relative;
  z-index: 1;
}

/* Print Styles */
@media print {
  .no-print {
    display: none !important;
  }

  .layout-wrapper,img,.logo-text {
    display: none !important;
    visibility: hidden !important;
}
  
  body {
    background: white;
  }
  
  .receipt-page {
    padding: 0;
    margin: 0;
    background: white;
  }
  
  .receipt-wrapper {
    box-shadow: none;
    border-radius: 0;
  }
  
  .receipt-container {
    padding: 30px;
    page-break-inside: avoid;
  }


  
  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
}

/* Mobile Responsive */
@media (max-width: 768px) {

  .receipt-page {
        padding-top: 6rem;
    }

  .receipt-container {
    padding: 24px;
  }
  
  .company-name {
    font-size: 24px;
  }
  
  .receipt-title {
    font-size: 18px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .controls {
    flex-direction: column;
  }
  
  .action-btn, .back-btn {
    width: 100%;
    justify-content: center;
  }
  
  .payment-table {
    font-size: 13px;
  }
  
  .payment-table th,
  .payment-table td {
    padding: 8px;
  }
  
  .receipt-watermark {
    font-size: 80px;
  }
}

@media (max-width: 480px) {
  .receipt-page {
    padding: 12px;
    padding-top: 6rem;
  }
  
  .receipt-container {
    padding: 20px;
  }
  
  .company-name {
    font-size: 20px;
  }
  
  .receipt-title {
    font-size: 16px;
    letter-spacing: 1px;
  }
  
  .detail-label {
    min-width: 90px;
    font-size: 13px;
  }
  
  .detail-value {
    font-size: 13px;
  }
}
</style>
