<template>
  <div class="payments-container">
    <!-- Header -->
    <div class="header-section">
      <h2 class="page-title">Monthly Payment Management</h2>
      <p class="page-subtitle">Track and manage student fee payments</p>
    </div>

    <!-- Controls Section -->
    <div class="controls-section">
      <div class="month-controls">
        <div class="month-selector">
          <label for="month-input">Select Month</label>
          <input 
            id="month-input"
            type="month" 
            v-model="selectedMonth" 
            class="month-input"
          />
        </div>
        
        <button @click="generatePayments" :disabled="loading" class="generate-btn">
          <span v-if="loading" class="btn-icon spinner">⏳</span>
          <!-- <span v-else class="btn-icon">➕</span> -->
          <span class="btn-text">{{ loading ? 'Generating...' : 'Generate Records' }}</span>
        </button>

        <router-link to="/reminders" class="reminder-link">
          <button class="reminder-btn">
            <span class="btn-icon">🔔</span>
            <span class="btn-text">Send Reminders</span>
          </button>
        </router-link>
      </div>

      <!-- Filters -->
      <div class="filters">
        <div class="search-wrapper">
          <span class="search-icon">🔍</span>
          <input 
            type="text" 
            v-model="searchTerm" 
            placeholder="Search by name or seat number..." 
            class="search-input"
          />
        </div>
        
        <select v-model="statusFilter" class="status-filter">
          <option value="">All Payments</option>
          <option value="paid">✅ Paid Only</option>
          <option value="unpaid">❌ Unpaid Only</option>
        </select>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="summary-cards">
      <div class="summary-card paid">
        <div class="card-icon">✅</div>
        <div class="card-content">
          <div class="card-number">{{ paidCount }}</div>
          <div class="card-label">Paid</div>
        </div>
      </div>
      
      <div class="summary-card unpaid">
        <div class="card-icon">❌</div>
        <div class="card-content">
          <div class="card-number">{{ unpaidCount }}</div>
          <div class="card-label">Unpaid</div>
        </div>
      </div>
      
      <div class="summary-card total">
        <div class="card-icon">💰</div>
        <div class="card-content">
          <div class="card-number">₹{{ totalAmount }}</div>
          <div class="card-label">Total</div>
        </div>
      </div>

      <div class="summary-card collected">
        <div class="card-icon">💳</div>
        <div class="card-content">
          <div class="card-number">₹{{ collectedAmount }}</div>
          <div class="card-label">Collected</div>
        </div>
      </div>
    </div>

    <!-- Desktop Table View -->
    <div v-if="filteredPayments.length > 0" class="table-container desktop-view">
      <table class="payments-table">
        <thead>
          <tr>
            <th>Student Details</th>
            <th>Seat</th>
            <th>Amount</th>
            <th>Joining Date</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="payment in filteredPayments" :key="payment.id" class="payment-row">
            <td class="student-info">
              <router-link :to="`/students/${payment.student.id}`" class="student-link">
                <div class="student-avatar">
                  {{ payment.student.name.charAt(0).toUpperCase() }}
                </div>
                <div class="student-details">
                  <span class="student-name">{{ payment.student.name }}</span>
                </div>
              </router-link>
            </td>
            
            <td class="seat-cell">
              <span class="seat-badge" v-if="payment.student.seat?.seat_number">
                {{ payment.student.seat.seat_number }}
              </span>
              <span class="no-seat" v-else>—</span>
            </td>
            
            <td class="amount-cell">
              <span class="amount">₹{{ formatAmount(payment.amount) }}</span>
            </td>
            
            <td class="date-cell">
              <span class="date">{{ formatDate(payment.student.date_of_joining) }}</span>
            </td>
            
            <td class="status-cell">
              <span class="status-badge" :class="{ paid: payment.paid, unpaid: !payment.paid }">
                <span class="status-icon">{{ payment.paid ? '✅' : '❌' }}</span>
                <span class="status-text">{{ payment.paid ? 'Paid' : 'Unpaid' }}</span>
              </span>
            </td>
            
            <td class="actions-cell">
              <div class="action-buttons">
                <button 
                  @click="togglePaid(payment)" 
                  class="action-btn toggle-btn"
                  :class="{ paid: payment.paid, unpaid: !payment.paid }"
                >
                  <!-- <span class="btn-icon">{{ payment.paid ? '↩️' : '✅' }}</span> -->
                  <span class="btn-text">{{ payment.paid ? 'Mark Unpaid' : 'Mark Paid' }}</span>
                </button>
                
                <button @click="deletePayment(payment)" class="action-btn delete-btn">
                  <!-- <span class="btn-icon">🗑️</span> -->
                  <span class="btn-text">Delete</span>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Mobile Card View -->
    <div class="mobile-view">
      <div 
        v-for="payment in filteredPayments" 
        :key="payment.id" 
        class="payment-card"
      >
        <div class="card-header">
          <router-link :to="`/students/${payment.student.id}`" class="student-link">
            <div class="student-avatar mobile">
              {{ payment.student.name.charAt(0).toUpperCase() }}
            </div>
            <div class="student-info-mobile">
              <h3 class="student-name-mobile">{{ payment.student.name }}</h3>
              <p class="student-details-mobile">
                Seat: {{ payment.student.seat?.seat_number || 'Not assigned' }}
              </p>
            </div>
          </router-link>
          
          <div class="status-badge mobile" :class="{ paid: payment.paid, unpaid: !payment.paid }">
            <span class="status-icon">{{ payment.paid ? '✅' : '❌' }}</span>
            <span class="status-text">{{ payment.paid ? 'Paid' : 'Unpaid' }}</span>
          </div>
        </div>

        <div class="card-body">
          <div class="payment-details">
            <div class="detail-row">
              <span class="detail-label">Amount:</span>
              <span class="detail-value amount">₹{{ formatAmount(payment.amount) }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Joining Date:</span>
              <span class="detail-value">{{ formatDate(payment.student.date_of_joining) }}</span>
            </div>
          </div>
        </div>

        <div class="card-footer">
          <div class="action-buttons mobile">
            <button 
              @click="togglePaid(payment)" 
              class="action-btn toggle-btn mobile"
              :class="{ paid: payment.paid, unpaid: !payment.paid }"
            >
              <!-- <span class="btn-icon">{{ payment.paid ? '↩️' : '✅' }}</span> -->
              <span class="btn-text">{{ payment.paid ? 'Mark Unpaid' : 'Mark Paid' }}</span>
            </button>
            <button @click="deletePayment(payment)" class="action-btn delete-btn mobile">
              <!-- <span class="btn-icon">🗑️</span> -->
              <span class="btn-text">Delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredPayments.length === 0 && !loading" class="empty-state">
      <div class="empty-icon">💳</div>
      <h3>No Payment Records Found</h3>
      <p v-if="searchTerm || statusFilter">Try adjusting your search criteria or filters.</p>
      <p v-else>Click "Generate Records" to create payment records for this month.</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner">⏳</div>
      <p>Loading payment records...</p>
    </div>

    <!-- Confirmation Modal -->
    <ConfirmationModal
      :show="showConfirmationModal"
      title="Payment Confirmed! 🎉"
      :message="`Send confirmation message to ${selectedPayment?.student?.name.toUpperCase()}?`"
      @whatsapp="sendWhatsAppConfirmation"
      @sms="sendSMSConfirmation"
      @cancel="closeModal"
    />
  </div>
</template>

<script>
import API from '../api';
import { useToast } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';
import ConfirmationModal from './ConfirmationModal.vue';

export default {
  components: {
    ConfirmationModal
  },

  setup() {
    const toast = useToast();
    
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
        closeButton: "button",
        icon: true,
        rtl: false,
        style: {
          backgroundColor: '#667eea',
          color: '#fff',
          borderRadius: '12px'
        },       
        ...options
      });
    };
    
    const showError = (message) => {
      toast.error(message, {
        style: {
          backgroundColor: '#dc2626',
          color: '#fff',
          borderRadius: '12px'
        }
      });
    };
    
    return {
      showSuccess,
      showError
    };
  },

  data() {
    const today = new Date();
    const defaultMonth = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
    return {
      selectedMonth: defaultMonth,
      payments: [],
      searchTerm: '',
      statusFilter: '',
      showConfirmationModal: false,
      selectedPayment: null,
      loading: false
    };
  },

  computed: {
    filteredPayments() {
      return this.payments.filter(payment => {
        const search = this.searchTerm.trim().toLowerCase();
        const matchesName = payment.student.name.toLowerCase().includes(search);
        const seatNum = payment.student.seat?.seat_number ? String(payment.student.seat.seat_number) : '';
        const matchesSeat = seatNum.includes(search);

        const matchesStatus =
          this.statusFilter === '' ||
          (this.statusFilter === 'paid' && payment.paid) ||
          (this.statusFilter === 'unpaid' && !payment.paid);

        return (matchesName || matchesSeat) && matchesStatus;
      });
    },

    paidCount() {
      return this.filteredPayments.filter(p => p.paid).length;
    },

    unpaidCount() {
      return this.filteredPayments.filter(p => !p.paid).length;
    },

    totalAmount() {
      return this.filteredPayments.reduce((sum, p) => sum + p.amount, 0).toLocaleString('en-IN');
    },

    collectedAmount() {
      return this.filteredPayments.filter(p => p.paid).reduce((sum, p) => sum + p.amount, 0).toLocaleString('en-IN');
    }
  },

  mounted() {
    this.fetchPayments();
  },

  watch: {
    selectedMonth: {
      handler: 'fetchPayments',
      immediate: false
    }
  },

  methods: {
    async fetchPayments() {
      this.loading = true;
      try {
        const res = await API.get(`/monthly-payments/${this.selectedMonth}`);
        this.payments = res.data;
      } catch (err) {
        this.showError('Error fetching monthly payments');
      } finally {
        this.loading = false;
      }
    },

    async togglePaid(payment) {
      try {
        const res = await API.put(`/monthly-payments/toggle/${payment.id}`);
        payment.paid = res.data.paid;
        
        if (payment.paid) {
          this.showSuccess('✅ Payment marked as paid!');
          this.showConfirmationModal = true;
          this.selectedPayment = payment;
        } else {
          this.showSuccess('↩️ Payment marked as unpaid');
        }
      } catch (err) {
        this.showError('❌ Failed to toggle status');
      }
    },

    sendWhatsAppConfirmation() {
      this.sendPaymentConfirmation(this.selectedPayment);
      this.closeModal();
    },

    sendSMSConfirmation() {
      this.sendSMS(this.selectedPayment);
      this.closeModal();
    },

    closeModal() {
      this.showConfirmationModal = false;
      this.selectedPayment = null;
    },

    sendPaymentConfirmation(payment) {
      const libraryName = localStorage.getItem('library_name') || "Your Library";
      const monthDate = new Date(this.selectedMonth + '-01');
      const monthName = monthDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
      
      const msg = `Dear ${payment.student.name},\n` +
                  `We have received your library fee of ₹${payment.amount} for ${monthName}.\n` +
                  `Your payment has been successfully recorded.\n\n` +
                  `Thanks,\n${libraryName}`;
      
      const phone = "91" + payment.student.contact.replace(/^0+/, "");
      const url = `https://wa.me/${phone}?text=${encodeURIComponent(msg)}`;
      window.open(url, "_blank");
      this.showSuccess('📱 WhatsApp confirmation sent!');
    },

    sendSMS(payment) {
      const libraryName = localStorage.getItem('library_name') || "Your Library";
      const monthDate = new Date(this.selectedMonth + '-01');
      const monthName = monthDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
      
      const msg = `Dear ${payment.student.name},\n` +
                  `We have received your library fee of ₹${payment.amount} for ${monthName}.\n` +
                  `Your payment has been successfully recorded.\n\n` +
                  `Thanks,\n${libraryName}`;
      
      const phone = payment.student.contact.replace(/^(\+91|91)/, "");
      const url = `sms:${phone}?body=${encodeURIComponent(msg)}`;
      window.open(url, "_blank");
      this.showSuccess('💬 SMS confirmation sent!');
    },

    async deletePayment(payment) {
      if (!confirm('⚠️ Are you sure you want to delete this payment record?')) return;
      
      try {
        await API.delete(`/monthly-payments/${payment.id}`);
        this.payments = this.payments.filter(p => p.id !== payment.id);
        this.showSuccess('✅ Payment record deleted successfully');
      } catch (err) {
        this.showError('❌ Error deleting payment');
      }
    },

    async generatePayments() {
      this.loading = true;
      try {
        const monthDate = new Date(this.selectedMonth + '-01');
        const monthName = monthDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
        await API.post(`/generate-monthly-payments/${this.selectedMonth}`);
        this.showSuccess(`✅ Payment records generated for ${monthName}`);
        this.fetchPayments();
      } catch (err) {
        this.showError('❌ Error generating payment records');
      } finally {
        this.loading = false;
      }
    },

    formatDate(dateString) {
      const date = new Date(dateString);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = String(date.getFullYear()).slice(-2);
      return `${day}-${month}-${year}`;
    },

    formatAmount(amount) {
      return amount.toLocaleString('en-IN');
    }
  }
};
</script>

<style scoped>
.payments-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  padding-top: 2rem;
}

.header-section {
  text-align: center;
  margin-bottom: 2rem;
  color: white;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding-top: 2rem;
}

.page-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  font-weight: 300;
  margin: 0;
}

.controls-section {
  max-width: 1000px;
  margin: 0 auto 2rem auto;
  background: rgba(255,255,255,0.95);
  padding: 24px;
  border-radius: 20px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.month-controls {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: end;
}

.month-selector {
  flex: 1;
  width:-webkit-fill-available;
}

.month-selector label {
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  font-size: 0.95rem;
}

.month-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  outline: none;
  font-size: 16px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.month-input:focus {
  border-color: #667eea;
}

.generate-btn,
.reminder-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.generate-btn {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.reminder-link {
  text-decoration: none;
}

.reminder-btn {
  background: linear-gradient(45deg, #10b981, #059669);
  color: white;
}

.reminder-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-icon {
  font-size: 1.1rem;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.filters {
  display: flex;
  gap: 16px;
  padding-top: 16px;
  border-top: 2px solid #f3f4f6;
}

.search-wrapper {
  position: relative;
  flex: 1;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.1rem;
  color: #9ca3af;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 40px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  outline: none;
  font-size: 16px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.search-input:focus {
  border-color: #667eea;
}

.status-filter {
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  outline: none;
  font-size: 16px;
  background: white;
  cursor: pointer;
  transition: border-color 0.3s ease;
  min-width: 160px;
}

.status-filter:focus {
  border-color: #667eea;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  max-width: 1000px;
  margin: 0 auto 2rem auto;
}

.summary-card {
  background: rgba(255,255,255,0.95);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

.card-icon {
  font-size: 1.5rem;
  /* width: 50px; */
  /* height: 50px; */
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.summary-card.paid .card-icon {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
}

.summary-card.unpaid .card-icon {
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
}

.summary-card.total .card-icon {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.summary-card.collected .card-icon {
  background: rgba(245, 158, 11, 0.1);
  color: #d97706;
}

.card-content {
  flex: 1;
}

.card-number {
  font-size: 1.3rem;
  font-weight: 800;
  color: #1f2937;
  line-height: 1;
}

.card-label {
  font-size: 0.9rem;
  color: #6b7280;
  margin-top: 4px;
}

.table-container {
  max-width: 1200px;
  margin: 0 auto;
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.payments-table {
  width: 100%;
  border-collapse: collapse;
}

.payments-table th {
  /* background: linear-gradient(45deg, #667eea, #764ba2); */
  color: white;
  padding: 20px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 0.95rem;
  border: none;
}
thead{
    background: linear-gradient(45deg, #667eea, #764ba2);

}

.payment-row {
  transition: all 0.3s ease;
  animation: slideIn 0.6s ease-out forwards;
  opacity: 0;
}

.payment-row:hover {
  background: #f8faff;
  transform: scale(1.01);
}

.payment-row:nth-child(even) {
  background: rgba(102, 126, 234, 0.02);
}

.payments-table td {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: middle;
}

.student-info {
  min-width: 200px;
}

.student-link {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s ease;
}

.student-link:hover {
  transform: translateX(4px);
}

.student-avatar {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.student-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.student-name {
  font-weight: 600;
  color: #1f2937;
  text-transform: uppercase;
  font-size: 0.95rem;
}

.student-id {
  font-size: 0.8rem;
  color: #6b7280;
}

.seat-badge {
  background: linear-gradient(45deg, #10b981, #059669);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  display: inline-block;
}

.no-seat {
  color: #9ca3af;
  font-style: italic;
}

.amount {
  font-weight: 700;
  color: #dc2626;
  font-size: 1.1rem;
  font-family: 'Monaco', 'Menlo', monospace;
}

.date {
  color: #374151;
  font-weight: 500;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  justify-content: center;
}

.status-badge.paid {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-badge.unpaid {
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
  border: 1px solid rgba(220, 38, 38, 0.3);
}

.status-icon {
  font-size: 1rem;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.3s ease;
  min-width: 100px;
  justify-content: center;
}

.toggle-btn.paid {
  background: linear-gradient(45deg, #f59e0b, #d97706);
  color: white;
}

.toggle-btn.unpaid {
  background: linear-gradient(45deg, #10b981, #059669);
  color: white;
}

.delete-btn {
  background: linear-gradient(45deg, #dc2626, #b91c1c);
  color: white;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

/* Mobile View */
.mobile-view {
  display: none;
  gap: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.payment-card {
  background: rgba(255,255,255,0.95);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.payment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f3f4f6;
}

.student-avatar.mobile {
  width: 50px;
  height: 50px;
  font-size: 1.4rem;
}

.student-info-mobile {
  flex: 1;
  margin-left: 12px;
}

.student-name-mobile {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: #1f2937;
  text-transform: uppercase;
}

.student-details-mobile {
  margin: 0;
  color: #2b2c30;
  font-size: 0.9rem;
}

.status-badge.mobile {
  font-size: 0.8rem;
  padding: 6px 10px;
}

.card-body {
  margin-bottom: 16px;
}

.payment-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8faff;
  border-radius: 8px;
}

.detail-label {
  font-weight: 600;
  color: #374151;
}

.detail-value {
  font-weight: 500;
  color: #1f2937;
}

.detail-value.amount {
  color: #dc2626;
  font-weight: 700;
}

.card-footer {
  padding-top: 16px;
  border-top: 2px solid #f3f4f6;
}

.action-buttons.mobile {
  flex-direction: column;
  gap: 8px;
}

.action-btn.mobile {
  width: 100%;
  min-width: unset;
}

.empty-state,
.loading-state {
  text-align: center;
  padding: 4rem 2rem;
  color: white;
}

.empty-icon,
.loading-spinner {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.loading-spinner {
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-10px); }
  60% { transform: translateY(-5px); }
}

.empty-state h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.empty-state p {
  opacity: 0.9;
  line-height: 1.5;
}

/* Animations */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.payment-row:nth-child(1) { animation-delay: 0.1s; }
.payment-row:nth-child(2) { animation-delay: 0.2s; }
.payment-row:nth-child(3) { animation-delay: 0.3s; }
.payment-row:nth-child(4) { animation-delay: 0.4s; }
.payment-row:nth-child(5) { animation-delay: 0.5s; }

/* Responsive Design */
@media (max-width: 1024px) {
  .desktop-view {
    display: none;
  }

  .payments-container {
    padding: 16px;
    padding-top: 1rem;
  }

  .page-title {
    font-size: 2rem;
    padding-top: 3rem;
  }
  
  .mobile-view {
    display: flex;
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .payments-container {
    padding: 16px;
    padding-top: 1rem;
  }
  
  .page-title {
    font-size: 2rem;
    padding-top: 3rem;
  }
  
  .controls-section {
    padding: 20px;
  }
  
  .month-controls {
    flex-direction: column;
    gap: 12px;
  }

  .reminder-link[data-v-1678335a] {
    text-decoration: none;
    width: -webkit-fill-available;
}
  
  .generate-btn,
  .reminder-btn {
    width: 100%;
    justify-content: center;
  }
  
  .filters {
    flex-direction: column;
    gap: 12px;
  }
  
  .search-input,
  .status-filter {
    width: 100%;
  }
  
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .payment-card {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .card-header {
    flex-direction: row;
    gap: 12px;
    text-align: center;
  }
  
  .student-info-mobile {
    margin-left: 0;
    text-align: center;
  }
  
  .detail-row {
    flex-direction: row;
    gap: 4px;
    text-align: center;
  }

  .card-icon {
    /* display: none; */
    font-size: 1.5rem;
    width: fit-content;
  }
}
</style>
