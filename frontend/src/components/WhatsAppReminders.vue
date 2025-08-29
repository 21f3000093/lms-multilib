<template>
  <div class="reminders-container">
    <!-- Header -->
    <div class="header-section">
      <h2 class="page-title">Pending Fee Reminders</h2>
      <p class="page-subtitle">Send payment reminders to students with pending fees</p>
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
        
        <button @click="$router.back()" class="control-btn back-btn">
          <!-- <span class="btn-icon">←</span> -->
          <span class="btn-text">Back</span>
        </button>
        
        <button @click="fetchReminders" :disabled="loading" class="control-btn refresh-btn">
          <span v-if="loading" class="btn-icon spinner">⏳</span>
          <!-- <span v-else class="btn-icon">🔄</span> -->
          <span class="btn-text">{{ loading ? 'Loading...' : 'Refresh' }}</span>
        </button>
      </div>
    </div>

    <!-- Summary Card -->
    <div class="summary-card" v-if="pendingList.length > 0">
      <div class="summary-content">
        <div class="summary-icon">⚠️</div>
        <div class="summary-info">
          <div class="summary-number">{{ pendingList.length }}</div>
          <div class="summary-label">Students with pending fees</div>
        </div>
        <div class="summary-amount">
          <div class="amount-number">₹{{ totalPendingAmount }}</div>
          <div class="amount-label">Total Pending</div>
        </div>
      </div>
    </div>

    <!-- Desktop Table View -->
    <div v-if="pendingList.length > 0" class="table-container desktop-view">
      <table class="reminders-table">
        <thead>
          <tr>
            <th>Student Details</th>
            <th>Phone</th>
            <th>Amount</th>
            <th>Month</th>
            <th>Due Date</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="student in pendingList" :key="student.phone" class="reminder-row">
            <td class="student-info">
              <router-link :to="`/students/${student.student_id}`" class="student-link">
                <div class="student-avatar">
                  {{ student.student_name.charAt(0).toUpperCase() }}
                </div>
                <div class="student-details">
                  <span class="student-name">{{ student.student_name }}</span>
                </div>
              </router-link>
            </td>
            
            <td class="phone-cell">
              <span class="phone-number">{{ student.phone }}</span>
            </td>
            
            <td class="amount-cell">
              <span class="amount">₹{{ formatAmount(student.amount) }}</span>
            </td>
            
            <td class="month-cell">
              <span class="month">{{ formatMonth(student.month) }}</span>
            </td>
            
            <td class="date-cell">
              <span class="due-date" :class="{ overdue: isOverdue(student.due_date) }">
                {{ formatDate(student.due_date) }}
              </span>
            </td>
            
            <td class="action-cell">
              <button @click="openReminderModal(student)" class="action-btn reminder-btn">
                <span class="btn-icon">💬</span>
                <span class="btn-text">Send Reminder</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Mobile Card View -->
    <div class="mobile-view">
      <div 
        v-for="student in pendingList" 
        :key="student.phone" 
        class="reminder-card"
      >
        <div class="card-header">
          <router-link :to="`/students/${student.student_id}`" class="student-link">
            <div class="student-avatar mobile">
              {{ student.student_name.charAt(0).toUpperCase() }}
            </div>
            <div class="student-info-mobile">
              <h3 class="student-name-mobile">{{ student.student_name }}</h3>
              <p class="student-details-mobile">
                📞 {{ student.phone }} | ₹{{ formatAmount(student.amount) }}
              </p>
            </div>
          </router-link>
          
          <div class="due-badge" :class="{ overdue: isOverdue(student.due_date) }">
            <span class="due-icon">{{ isOverdue(student.due_date) ? '⚠️' : '📅' }}</span>
            <span class="due-text">{{ formatDate(student.due_date) }}</span>
          </div>
        </div>

        <div class="card-body">
          <div class="month-info">
            <span class="month-label">For Month:</span>
            <span class="month-value">{{ formatMonth(student.month) }}</span>
          </div>
        </div>

        <div class="card-footer">
          <button @click="openReminderModal(student)" class="action-btn reminder-btn mobile">
            <span class="btn-icon">💬</span>
            <span class="btn-text">Send Reminder</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="pendingList.length === 0 && !loading" class="empty-state">
      <div class="empty-icon">✅</div>
      <h3>No Pending Reminders</h3>
      <p>All students have paid their fees on time for {{ formatMonth(selectedMonth) }}!</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner">⏳</div>
      <p>Loading pending reminders...</p>
    </div>

    <!-- Fee Reminder Modal -->
    <ConfirmationModal
      :show="showReminderModal"
      title="Send Fee Reminder 💰"
      :message="`Send payment reminder to ${selectedStudent?.student_name?.toUpperCase()}?`"
      @whatsapp="sendReminderWhatsApp"
      @sms="sendReminderSMS"
      @cancel="closeReminderModal" 
    />
  </div>
</template>

<script>
import API from '../api';
import ConfirmationModal from './ConfirmationModal.vue';
import { useToast } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';

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
      pendingList: [],
      showReminderModal: false,
      selectedStudent: null,
      loading: false
    };
  },

  computed: {
    totalPendingAmount() {
      return this.pendingList.reduce((sum, student) => sum + student.amount, 0).toLocaleString('en-IN');
    }
  },
  
  methods: {
    async fetchReminders() {
      this.loading = true;
      try {
        const res = await API.get(`/reminders/pending-fees/${this.selectedMonth}`);
        this.pendingList = res.data;
        // if (this.pendingList.length > 0) {
        //   this.showSuccess(`📋 Found ${this.pendingList.length} pending reminders`);
        // }
      } catch (err) {
        this.showError("❌ Failed to fetch reminders: " + (err.response?.data?.detail || err.message));
      } finally {
        this.loading = false;
      }
    },

    openReminderModal(student) {
      this.selectedStudent = student;
      this.showReminderModal = true;
    },

    closeReminderModal() {
      this.showReminderModal = false;
      this.selectedStudent = null;
    },

    sendReminderWhatsApp() {
      const message = this.generateReminderMessage();
      const phone = "91" + this.selectedStudent.phone.replace(/^0+/, "");
      const url = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
      window.open(url, "_blank");
      this.closeReminderModal();
      this.showSuccess('📱 WhatsApp reminder sent!');
    },

    sendReminderSMS() {
      const message = this.generateReminderMessage();
      const phone = this.selectedStudent.phone.replace(/^(\+91|91)/, "");
      const url = `sms:${phone}?body=${encodeURIComponent(message)}`;
      window.open(url, "_blank");
      this.closeReminderModal();
      this.showSuccess('💬 SMS reminder sent!');
    },

    generateReminderMessage() {
      const libraryName = localStorage.getItem('library_name') || "Your Library";
      const monthDate = new Date(this.selectedStudent.month + '-01');
      const monthName = monthDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
      
      return `Dear ${this.selectedStudent.student_name},\n` +
             `Your library fee of Rs.${this.selectedStudent.amount} for ${monthName} was due on ${this.selectedStudent.due_date}.\n` +
             `Please pay it as soon as possible to avoid disruption.\n\n` +
             `Thanks,\n${libraryName}`;
    },

    formatAmount(amount) {
      return amount.toLocaleString('en-IN');
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = String(date.getFullYear()).slice(-2);
      return `${day}-${month}-${year}`;
    },

    formatMonth(monthString) {
      if (monthString && monthString.includes('-')) {
        const [year, month] = monthString.split('-');
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        return `${monthNames[parseInt(month) - 1]} ${year}`;
      }
      return monthString;
    },

    isOverdue(dueDateString) {
      if (!dueDateString) return false;
      const dueDate = new Date(dueDateString);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      return dueDate < today;
    }
  },

  created() {
    this.fetchReminders();
  },

  watch: {
    selectedMonth: {
      handler: 'fetchReminders',
      immediate: false
    }
  }
};
</script>

<style scoped>
.reminders-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  padding-top: 3rem;
}

.header-section {
  text-align: center;
  margin-bottom: 24px;
  color: white;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 8px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.page-subtitle {
  font-size: 1rem;
  opacity: 0.9;
  font-weight: 300;
  margin: 0;
}

.controls-section {
  max-width: 800px;
  margin: 0 auto 20px auto;
  background: rgba(255,255,255,0.95);
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.month-controls {
  display: flex;
  gap: 12px;
  align-items: end;
}

.month-selector {
  flex: 1;
  width: -webkit-fill-available;
}

.month-selector label {
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.month-input {
  width: 100%;
  padding: 12px;
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

.control-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  color: white;
}

.back-btn {
  background: linear-gradient(45deg, #6b7280, #4b5563);
}

.back-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3);
}

.refresh-btn {
  background: linear-gradient(45deg, #667eea, #764ba2);
}

.refresh-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 1rem;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.summary-card {
  max-width: 800px;
  margin: 0 auto 20px auto;
  background: rgba(255,255,255,0.95);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.summary-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.summary-icon {
  font-size: 1.8rem;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(220, 38, 38, 0.1);
  border-radius: 12px;
  flex-shrink: 0;
}

.summary-info {
  flex: 1;
}

.summary-number {
  font-size: 1.8rem;
  font-weight: 800;
  color: #1f2937;
  line-height: 1;
}

.summary-label {
  font-size: 0.9rem;
  color: #363b45;
  margin-top: 4px;
}

.summary-amount {
  text-align: right;
}

.amount-number {
  font-size: 1.5rem;
  font-weight: 800;
  color: #dc2626;
  line-height: 1;
}

.amount-label {
  font-size: 0.85rem;
  color: #363b45;
  margin-top: 4px;
}

.table-container {
  max-width: 1200px;
  margin: 0 auto;
  background: rgba(255,255,255,0.95);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.reminders-table {
  width: 100%;
  border-collapse: collapse;
}

.reminders-table th {
  /* background: linear-gradient(45deg, #667eea, #764ba2); */
  color: white;
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  font-size: 0.9rem;
  border: none;
}

.reminders-table thead{
  background: linear-gradient(45deg, #667eea, #764ba2);
}

.reminder-row {
  transition: all 0.3s ease;
  animation: slideIn 0.6s ease-out forwards;
  opacity: 0;
}

.reminder-row:hover {
  background: #f8faff;
}

.reminder-row:nth-child(even) {
  background: rgba(102, 126, 234, 0.02);
}

.reminders-table td {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: middle;
}

.student-info {
  min-width: 180px;
}

.student-link {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s ease;
}

.student-link:hover {
  transform: translateX(4px);
}

.student-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
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
  font-size: 0.9rem;
}

.student-id {
  font-size: 0.75rem;
  color: #6b7280;
}

.phone-number {
  font-family: 'Monaco', 'Menlo', monospace;
  color: #374151;
  font-weight: 500;
}

.amount {
  font-weight: 700;
  color: #dc2626;
  font-size: 1rem;
}

.month {
  color: #374151;
  font-weight: 500;
  font-size: 0.85rem;
}

.due-date {
  color: #374151;
  font-weight: 500;
  font-size: 0.85rem;
}

.due-date.overdue {
  color: #dc2626;
  font-weight: 700;
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
  min-width: 120px;
  justify-content: center;
}

.reminder-btn {
  background: linear-gradient(45deg, #10b981, #059669);
  color: white;
}

.reminder-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

/* Mobile View */
.mobile-view {
  display: none;
  gap: 12px;
  max-width: 600px;
  margin: 0 auto;
}

.reminder-card {
  background: rgba(255,255,255,0.95);
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.reminder-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f3f4f6;
}

.student-avatar.mobile {
  width: 40px;
  height: 40px;
  font-size: 1.1rem;
}

.student-info-mobile {
  flex: 1;
  margin-left: 10px;
}

.student-name-mobile {
  font-size: 1rem;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: #1f2937;
  text-transform: uppercase;
}

.student-details-mobile {
  margin: 0;
  color: #333;
  font-size: 0.85rem;
}

.due-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
}

.due-badge.overdue {
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
}

.due-icon {
  font-size: 0.9rem;
}

.card-body {
  margin-bottom: 10px;
}

.month-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8faff;
  border-radius: 8px;
}

.month-label {
  font-weight: 600;
  color: #374151;
  font-size: 0.85rem;
}

.month-value {
  font-weight: 500;
  color: #1f2937;
  font-size: 0.85rem;
}

.card-footer {
  padding-top: 10px;
  border-top: 1px solid #f3f4f6;
}

.action-btn.mobile {
  width: 100%;
  font-size: 0.9rem;
  padding: 10px 16px;
}

.empty-state,
.loading-state {
  text-align: center;
  padding: 40px 20px;
  color: white;
}

.empty-icon,
.loading-spinner {
  font-size: 3rem;
  margin-bottom: 16px;
}

.loading-spinner {
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-8px); }
  60% { transform: translateY(-4px); }
}

.empty-state h3 {
  font-size: 1.3rem;
  margin-bottom: 8px;
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

.reminder-row:nth-child(1) { animation-delay: 0.1s; }
.reminder-row:nth-child(2) { animation-delay: 0.2s; }
.reminder-row:nth-child(3) { animation-delay: 0.3s; }
.reminder-row:nth-child(4) { animation-delay: 0.4s; }
.reminder-row:nth-child(5) { animation-delay: 0.5s; }

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
  .reminders-container {
    padding: 12px;
    padding-top: 3.5rem;
  }
  
  .page-title {
    font-size: 1.8rem;
  }
  
  .controls-section {
    padding: 16px;
    margin-bottom: 16px;
  }
  
  .month-controls {
    flex-direction: column;
    gap: 10px;
  }
  
  .control-btn {
    width: 100%;
    height: 44px;
    justify-content: center;
    font-size: 16px;
  }
  
  .summary-card {
    padding: 16px;
    margin-bottom: 16px;
  }
  
  .summary-content {
    flex-direction: row;
    text-align: center;
    gap: 12px;
  }
  
  .summary-amount {
    text-align: center;
  }
  
  .reminder-card {
    padding: 10px;
  }
  
  .card-header {
    margin-bottom: 8px;
    padding-bottom: 8px;
  }
  
  .card-footer {
    padding-top: 8px;
  }
}

@media (max-width: 480px) {
  .reminders-container {
    padding: 10px;
    padding-top: 3.5rem;
  }

  .card-header {
    flex-direction: row;
    gap: 8px;
    text-align: center;
  }
  
  .student-info-mobile {
    margin-left: 0;
    text-align: center;
  }
}
</style>
