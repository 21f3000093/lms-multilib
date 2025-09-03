<template>
  <div class="student-profile-container">
    <!-- Header -->
    <!-- <button @click="$router.back()" class="back-btn">
      <span class="btn-icon">←</span>
      <span class="btn-text">Back</span>
    </button> -->
    <div class="header-section">
      <h2 class="page-title">Student Profile</h2>
    </div>

    <!-- Student Profile Card -->
    <div class="profile-card" v-if="student">
      <div class="profile-header">
        <div class="student-avatar">
          {{ student.name.charAt(0).toUpperCase() }}
        </div>
        <div class="student-info">
          <h3 class="student-name">{{ student.name }}</h3>
          <div class="student-details">
            <div class="detail-item">
              <!-- <span class="detail-icon">📞</span> -->
              <span class="detail-label">Contact:</span>
              <span class="detail-value">{{ student.contact }}</span>
            </div>
            <div class="detail-item">
              <!-- <span class="detail-icon">📅</span> -->
              <span class="detail-label">Joined:</span>
              <span class="detail-value">{{ formatDate(student.date_of_joining) }}</span>
            </div>
            <div class="detail-item">
              <!-- <span class="detail-icon">🪑</span> -->
              <span class="detail-label">Seat:</span>
              <span class="detail-value">{{ student.seat?.seat_number || 'Not assigned' }}</span>
            </div>
            <div class="detail-item">
              <!-- <span class="detail-icon">⭐</span> -->
              <span class="detail-label">Status:</span>
              <span class="status-badge" :class="student.status">
                {{ student.status }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Shifts Info -->
      <div class="shifts-section">
        <h4 class="shifts-title">Enrolled Shifts</h4>
        <div class="shifts-list">
          <div class="shift-item" v-if="student.shift1">
            <span class="shift-icon">🌅</span>
            <span class="shift-name">Morning</span>
          </div>
          <div class="shift-item" v-if="student.shift2">
            <span class="shift-icon">☀️</span>
            <span class="shift-name">Afternoon</span>
          </div>
          <div class="shift-item" v-if="student.shift3">
            <span class="shift-icon">🌙</span>
            <span class="shift-name">Evening</span>
          </div>
        </div>
      </div>

      <!-- Monthly Fee Info -->
      <div class="fee-section">
        <div class="fee-info">
          <span class="fee-label">Monthly Fee:</span>
          <span class="fee-amount">₹{{ formatAmount(student.custom_fees || 0) }}</span>
        </div>
      </div>
    </div>

    <!-- Payment Summary -->
    <div class="summary-cards" v-if="payments.length > 0">
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
    </div>

    <!-- Monthly Payments Section -->
    <div class="payments-section">
      <h3 class="section-title">Monthly Payments</h3>

      <!-- Desktop Table View -->
      <div v-if="payments.length > 0" class="table-container desktop-view">
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
            <tr v-for="payment in payments" :key="payment.id" class="payment-row">
              <td class="month-cell">
                <span class="month">{{ formatMonth(payment.month) }}</span>
              </td>
              
              <td class="amount-cell">
                <span class="amount">₹{{ formatAmount(payment.amount) }}</span>
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
                    <span class="btn-icon">{{ payment.paid ? '↩️' : '✅' }}</span>
                    <span class="btn-text">{{ payment.paid ? 'Mark Unpaid' : 'Mark Paid' }}</span>
                  </button>
                  
                  <button @click="deletePayment(payment.id)" class="action-btn delete-btn">
                    <span class="btn-icon">🗑️</span>
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
          v-for="payment in payments" 
          :key="payment.id" 
          class="payment-card"
        >
          <div class="card-header">
            <div class="payment-info">
              <h4 class="payment-month">{{ formatMonth(payment.month) }}</h4>
              <p class="payment-amount">₹{{ formatAmount(payment.amount) }}</p>
            </div>
            
            <div class="status-badge mobile" :class="{ paid: payment.paid, unpaid: !payment.paid }">
              <span class="status-icon">{{ payment.paid ? '✅' : '❌' }}</span>
              <span class="status-text">{{ payment.paid ? 'Paid' : 'Unpaid' }}</span>
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
              <button @click="deletePayment(payment.id)" class="action-btn delete-btn mobile">
                <!-- <span class="btn-icon">🗑️</span> -->
                <span class="btn-text">Delete</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="payments.length === 0 && !loading" class="empty-state">
        <div class="empty-icon">💳</div>
        <h3>No Payment Records</h3>
        <p>No payment history found for this student.</p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner">⏳</div>
      <p>Loading student details...</p>
    </div>
  </div>
</template>

<script>
import API from '../api';
import { useToast } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';

export default {
  setup() {
    const toast = useToast();
    
    const showSuccess = (message) => {
      toast.success(message, {
        position: 'top',
        timeout: 3000,
        style: {
          backgroundColor: '#667eea',
          color: '#fff',
          borderRadius: '12px'
        }
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
    
    return { showSuccess, showError };
  },

  data() {
    return {
      student: null,
      payments: [],
      loading: false
    };
  },

  computed: {
    paidCount() {
      return this.payments.filter(p => p.paid).length;
    },

    unpaidCount() {
      return this.payments.filter(p => !p.paid).length;
    },

    totalAmount() {
      return this.payments.reduce((sum, p) => sum + p.amount, 0);
    }
  },

  async mounted() {
    const id = this.$route.params.id;
    this.loading = true;
    try {
      await Promise.all([
        this.fetchStudent(id),
        this.fetchPayments(id)
      ]);
    } finally {
      this.loading = false;
    }
  },

  methods: {
    async fetchStudent(id) {
      try {
        const res = await API.get(`/students/${id}`);
        this.student = res.data;
      } catch (err) {
        this.showError('❌ Failed to load student details');
      }
    },

    async fetchPayments(id) {
      try {
        const res = await API.get(`/students/${id}/payments`);
        this.payments = res.data;
      } catch (err) {
        this.showError('❌ Failed to load payment history');
      }
    },

    async togglePaid(payment) {
      try {
        const res = await API.put(`/monthly-payments/toggle/${payment.id}`);
        payment.paid = res.data.paid;
        
        if (payment.paid) {
          this.showSuccess('✅ Payment marked as paid!');
        } else {
          this.showSuccess('↩️ Payment marked as unpaid');
        }
      } catch (err) {
        this.showError('❌ Failed to update payment status');
      }
    },

    async deletePayment(id) {
      if (!confirm('⚠️ Are you sure you want to delete this payment record?')) return;
      
      try {
        await API.delete(`/monthly-payments/${id}`);
        this.payments = this.payments.filter(p => p.id !== id);
        this.showSuccess('✅ Payment record deleted successfully');
      } catch (err) {
        this.showError('❌ Failed to delete payment record');
      }
    },

    formatDate(dateStr) {
      if (!dateStr) return 'N/A';
      const date = new Date(dateStr);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      return `${day}-${month}-${year}`;
    },

    formatMonth(monthStr) {
      if (!monthStr) return 'N/A';
      const [year, month] = monthStr.split('-');
      const date = new Date(parseInt(year), parseInt(month) - 1);
      return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    },

    formatAmount(amount) {
      return amount.toLocaleString('en-IN');
    }
  }
};
</script>

<style scoped>
.student-profile-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  padding-top: 80px;
}

.header-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  justify-content: center;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: rgba(255,255,255,0.2);
  color: white;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
}

.back-btn:hover {
  background: rgba(255,255,255,0.3);
  transform: translateY(-1px);
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.profile-card {
  max-width: 800px;
  margin: 0 auto 24px auto;
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.student-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 2rem;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.student-info {
  flex: 1;
}

.student-name {
  font-size: 1.8rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 12px 0;
  text-transform: uppercase;
}

.student-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f8faff;
  border-radius: 8px;
}

.detail-icon {
  font-size: 1rem;
  width: 20px;
}

.detail-label {
  font-weight: 600;
  color: #6b7280;
  font-size: 0.9rem;
}

.detail-value {
  color: #1f2937;
  font-weight: 500;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.85rem;
  text-transform: uppercase;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-badge.left {
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
  border: 1px solid rgba(220, 38, 38, 0.3);
}

.shifts-section {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8faff;
  border-radius: 12px;
}

.shifts-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #374151;
  margin: 0 0 12px 0;
}

.shifts-list {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;

}

.shift-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
  color: #667eea;
  font-weight: 600;
  font-size: 0.9rem;
}

.fee-section {
  padding: 16px;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.fee-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.fee-label {
  font-weight: 600;
  color: #374151;
  font-size: 1.1rem;
}

.fee-amount {
  font-weight: 800;
  color: #059669;
  font-size: 1.3rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  max-width: 800px;
  margin: 0 auto 24px auto;
}

.summary-card {
  background: rgba(255,255,255,0.95);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.card-icon {
  font-size: 1.3rem;
  width: 35px;
  height: 35px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  flex-shrink: 0;
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
  font-size: 0.8rem;
  color: #6b7280;
  margin-top: 2px;
}

.payments-section {
  max-width: 1000px;
  margin: 0 auto;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin: 0 0 16px 0;
  text-align: center;
}

.table-container {
  background: rgba(255,255,255,0.95);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.payments-table {
  width: 100%;
  border-collapse: collapse;
}

.payments-table th {
  /* background: linear-gradient(45deg, #667eea, #764ba2); */
  color: white;
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  font-size: 0.9rem;
  border: none;
}

.payments-table thead{
  background: linear-gradient(45deg, #667eea, #764ba2);
}

.payment-row {
  transition: all 0.3s ease;
  animation: slideIn 0.6s ease-out forwards;
  opacity: 0;
}

.payment-row:hover {
  background: #f8faff;
}

.payment-row:nth-child(even) {
  background: rgba(102, 126, 234, 0.02);
}

.payments-table td {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: middle;
}

.month {
  font-weight: 600;
  color: #374151;
}

.amount {
  font-weight: 700;
  color: #dc2626;
  font-size: 1rem;
}

.status-badge.paid {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.3);
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  width: fit-content;
}

.status-badge.unpaid {
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
  border: 1px solid rgba(220, 38, 38, 0.3);
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  width: fit-content;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 600;
  transition: all 0.3s ease;
  min-width: 80px;
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
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

/* Mobile View */
.mobile-view {
  display: none;
  gap: 12px;
}

.payment-card {
  background: rgba(255,255,255,0.95);
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f3f4f6;
}

.payment-info h4 {
  margin: 0 0 4px 0;
  font-size: 1rem;
  font-weight: 700;
  color: #1f2937;
}

.payment-info p {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
  color: #dc2626;
}

.status-badge.mobile {
  font-size: 0.75rem;
  padding: 4px 8px;
}

.card-footer {
  padding-top: 10px;
  border-top: 1px solid #f3f4f6;
}

.action-buttons.mobile {
  display: flex;
  gap: 8px;
}

.action-btn.mobile {
  flex: 1;
  font-size: 0.85rem;
  padding: 8px 12px;
}

.empty-state,
.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: white;
}

.empty-icon,
.loading-spinner {
  font-size: 4rem;
  margin-bottom: 20px;
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
  margin-bottom: 10px;
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
    transform: translateY(15px);
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
  
  .mobile-view {
    display: flex;
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .student-profile-container {
    padding: 12px;
    padding-top: 5rem;
  }
  
  .header-section {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
  .student-avatar {
    width: 70px;
    height: 70px;
  }
  
  .page-title {
    font-size: 1.8rem;
  }
  
  .profile-card {
    padding: 16px;
    margin-bottom: 16px;
  }
  
  .profile-header {
    flex-direction: row;
    text-align: center;
    gap: 6px;
    overflow-x: auto;
  }
  
  .student-details {
    /* grid-template-columns: 1fr; */
    display: grid
;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0px;
  }
  
  .shifts-list {
    justify-content: center;
  }
  
  .summary-cards {
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    width: 100%;
  }
  
  .payment-card {
    padding: 10px;
  }

  .detail-item {
    flex-direction: row;
    justify-content: space-between;

  }
}

@media (max-width: 480px) {
  .student-profile-container {
    padding: 10px;
    padding-top: 5rem;
  }

  /* .summary-cards {
    grid-template-columns: 1fr;
  } */
  
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    width: 100%;
  }

  .card-header {
    flex-direction: row;
    gap: 8px;
    text-align: center;
    justify-content: space-evenly;
  }
  
  .action-buttons.mobile {
    flex-direction: row;
  }
}
</style>
