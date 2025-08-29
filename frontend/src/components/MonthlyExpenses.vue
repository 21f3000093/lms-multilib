<template>
  <div class="expenses-container">
    <!-- Header -->
    <div class="header-section">
      <h2 class="page-title">Monthly Expenses</h2>
      <p class="page-subtitle">Track and manage your library expenses</p>
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
        
        <button @click="openExpenseModal" :disabled="loading" class="control-btn add-btn">
          <!-- <span class="btn-icon">➕</span> -->
          <span class="btn-text">Add Expense</span>
        </button>
      </div>
    </div>

    <!-- Summary Card -->
    <div class="summary-card" v-if="expenses.length > 0">
      <div class="summary-content">
        <div class="summary-icon">📊</div>
        <div class="summary-info">
          <div class="summary-number">{{ expenses.length }}</div>
          <div class="summary-label">Total Expenses</div>
        </div>
        <div class="summary-amount">
          <div class="amount-number">₹{{ formatAmount(totalExpenses) }}</div>
          <div class="amount-label">Total Spent</div>
        </div>
      </div>
    </div>

    <!-- Desktop Table View -->
    <div v-if="expenses.length > 0" class="table-container desktop-view">
      <table class="expenses-table">
        <thead>
          <tr>
            <th>Expense Details</th>
            <th>Amount</th>
            <th>Date</th>
            <th>Category</th>
            <th>Description</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="expense in expenses" :key="expense.id" class="expense-row">
            <td class="expense-info">
              <div class="expense-details">
                <span class="expense-name">{{ expense.name }}</span>
              </div>
            </td>
            
            <td class="amount-cell">
              <span class="amount">₹{{ formatAmount(expense.amount) }}</span>
            </td>
            
            <td class="date-cell">
              <span class="date">{{ formatDate(expense.date) }}</span>
            </td>
            
            <td class="category-cell">
              <span class="category-badge" v-if="expense.category">
                {{ expense.category }}
              </span>
              <span class="no-category" v-else>—</span>
            </td>
            
            <td class="description-cell">
              <span class="description" :title="expense.description">
                {{ expense.description || '—' }}
              </span>
            </td>
            
            <td class="actions-cell">
              <button @click="deleteExpense(expense)" class="action-btn delete-btn">
                <!-- <span class="btn-icon">🗑️</span> -->
                <span class="btn-text">Delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Mobile Card View -->
    <div class="mobile-view">
      <div 
        v-for="expense in expenses" 
        :key="expense.id" 
        class="expense-card"
      >
        <div class="card-header">
          <div class="expense-info-mobile">
            <h3 class="expense-name-mobile">{{ expense.name }}</h3>
            <p class="expense-details-mobile">
              {{ formatDate(expense.date) }} | {{ expense.category || 'Uncategorized' }}
            </p>
          </div>
          
          <div class="amount-badge">
            ₹{{ formatAmount(expense.amount) }}
          </div>
        </div>

        <div class="card-body" v-if="expense.description">
          <div class="description-section">
            <span class="description-label">Description:</span>
            <span class="description-value">{{ expense.description }}</span>
          </div>
        </div>

        <div class="card-footer">
          <button @click="deleteExpense(expense)" class="action-btn delete-btn mobile">
            <!-- <span class="btn-icon">🗑️</span> -->
            <span class="btn-text">Delete</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="expenses.length === 0 && !loading" class="empty-state">
      <div class="empty-icon">📊</div>
      <h3>No Expenses Found</h3>
      <p>No expenses recorded for {{ formatMonth(selectedMonth) }} yet.</p>
      <button @click="openExpenseModal" class="empty-action-btn">
        <!-- <span class="btn-icon">➕</span> -->
        <span class="btn-text">Add First Expense</span>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner">⏳</div>
      <p>Loading expenses...</p>
    </div>

    <!-- Add Expense Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Add New Expense</h3>
          <button class="modal-close" @click="closeModal">✕</button>
        </div>
        
        <form @submit.prevent="addExpense" class="expense-form">
          <div class="form-group">
            <label for="expense-name">Expense Name</label>
            <input 
              id="expense-name"
              v-model="expenseForm.name" 
              type="text" 
              placeholder="Enter expense name" 
              required 
              class="form-input"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="expense-amount">Amount (₹)</label>
              <input 
                id="expense-amount"
                v-model.number="expenseForm.amount" 
                type="number" 
                placeholder="Enter amount" 
                required 
                min="1" 
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label for="expense-date">Date</label>
              <input 
                id="expense-date"
                v-model="expenseForm.date" 
                type="date" 
                required 
                class="form-input"
              />
            </div>
          </div>

          <div class="form-group">
            <label for="expense-category">Category</label>
            <select id="expense-category" v-model="expenseForm.category" class="form-select">
              <option value="">Select Category (optional)</option>
              <option value="Utilities">🔌 Utilities</option>
              <option value="Maintenance">🔧 Maintenance</option>
              <option value="Supplies">📦 Supplies</option>
              <option value="Repair">🛠️ Repair</option>
              <option value="Rent">🏢 Rent</option>
              <option value="Internet">🌐 Internet</option>
              <option value="Other">📝 Other</option>
            </select>
          </div>

          <div class="form-group">
            <label for="expense-description">Description</label>
            <textarea 
              id="expense-description"
              v-model="expenseForm.description" 
              placeholder="Enter description (optional)" 
              rows="3"
              class="form-textarea"
            ></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn-cancel">
              <!-- <span class="btn-icon">❌</span> -->
              <span class="btn-text">Cancel</span>
            </button>
            <button type="submit" :disabled="loading" class="btn-submit">
              <span v-if="loading" class="btn-icon spinner">⏳</span>
              <!-- <span v-else class="btn-icon">➕</span> -->
              <span class="btn-text">{{ loading ? 'Adding...' : 'Add Expense' }}</span>
            </button>
          </div>
        </form>
      </div>
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
      expenses: [],
      showModal: false,
      loading: false,
      expenseForm: {
        name: '',
        date: new Date().toISOString().slice(0, 10),
        amount: '',
        description: '',
        category: '',
      }
    }
  },

  computed: {
    totalExpenses() {
      return this.expenses.reduce((total, exp) => total + (exp.amount || 0), 0);
    }
  },

  mounted() {
    this.fetchExpenses();
  },

  watch: {
    selectedMonth: 'fetchExpenses'
  },

  methods: {
    async fetchExpenses() {
      this.loading = true;
      try {
        const res = await API.get(`/monthly-expenses/${this.selectedMonth}`);
        this.expenses = res.data;
        // if (this.expenses.length > 0) {
        //   this.showSuccess(`📊 Loaded ${this.expenses.length} expenses`);
        // }
      } catch (err) {
        this.showError('❌ Error fetching monthly expenses');
      } finally {
        this.loading = false;
      }
    },

    openExpenseModal() {
      this.showModal = true;
      this.expenseForm = {
        name: '',
        date: new Date().toISOString().slice(0, 10),
        amount: '',
        description: '',
        category: '',
      }
    },

    closeModal() {
      this.showModal = false;
    },

    async addExpense() {
      if (!this.expenseForm.name.trim() || !this.expenseForm.amount || !this.expenseForm.date) {
        this.showError("⚠️ Please fill all required fields");
        return;
      }

      this.loading = true;
      try {
        await API.post('/monthly-expenses/', this.expenseForm);
        this.showSuccess('✅ Expense added successfully!');
        this.closeModal();
        this.fetchExpenses();
      } catch (err) {
        this.showError('❌ Error adding expense');
      } finally {
        this.loading = false;
      }
    },

    async deleteExpense(expense) {
      if (!confirm(`⚠️ Are you sure you want to delete "${expense.name}"?`)) return;
      
      try {
        await API.delete(`/monthly-expenses/${expense.id}`);
        this.showSuccess('✅ Expense deleted successfully');
        this.fetchExpenses();
      } catch (err) {
        this.showError('❌ Error deleting expense');
      }
    },
    
    formatDate(dateStr) {
      const d = new Date(dateStr);
      const day = String(d.getDate()).padStart(2, '0');
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const year = String(d.getFullYear()).slice(-2);
      return `${day}-${month}-${year}`;
    },

    formatAmount(amount) {
      return amount.toLocaleString('en-IN');
    },

    formatMonth(monthString) {
      if (monthString && monthString.includes('-')) {
        const [year, month] = monthString.split('-');
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        return `${monthNames[parseInt(month) - 1]} ${year}`;
      }
      return monthString;
    }
  }
}
</script>

<style scoped>
.expenses-container {
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
  font-size: 2.5rem;
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
  max-width: 600px;
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
}

.add-btn {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
}

.add-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.add-btn:disabled {
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
  max-width: 600px;
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
  font-size: 2rem;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(102, 126, 234, 0.1);
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
  color: #6b7280;
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
  color: #6b7280;
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

.expenses-table {
  width: 100%;
  border-collapse: collapse;
}

.expenses-table thead {
  background: linear-gradient(45deg, #667eea, #764ba2);
}

.expenses-table th {
  /* background: linear-gradient(45deg, #667eea, #764ba2); */
  color: white;
  padding: 16px 12px;
  text-align: center          ;
  font-weight: 600;
  font-size: 0.9rem;
  border: none;
}

.expense-row {
  transition: all 0.3s ease;
  animation: slideIn 0.6s ease-out forwards;
  opacity: 0;
}

.expense-row:hover {
  background: #f8faff;
}

.expense-row:nth-child(even) {
  background: rgba(102, 126, 234, 0.02);
}

.expenses-table td {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: middle;
}

.expense-info {
  min-width: 160px;
}

.expense-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.expense-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.9rem;
}

.expense-id {
  font-size: 0.75rem;
  color: #6b7280;
}

.amount {
  font-weight: 700;
  color: #dc2626;
  font-size: 1rem;
}

.date {
  color: #374151;
  font-weight: 500;
  font-size: 0.85rem;
}

.category-badge {
  background: linear-gradient(45deg, #10b981, #059669);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  display: inline-block;
}

.no-category {
  color: #9ca3af;
  font-style: italic;
}

.description {
  color: #374151;
  font-size: 0.85rem;
  max-width: 200px;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

.delete-btn {
  background: linear-gradient(45deg, #dc2626, #b91c1c);
  color: white;
  margin: auto;
}

.delete-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
}

/* Mobile View */
.mobile-view {
  display: none;
  gap: 12px;
  max-width: 600px;
  margin: 0 auto;
}

.expense-card {
  background: rgba(255,255,255,0.95);
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.expense-card:hover {
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

.expense-info-mobile {
  flex: 1;
}

.expense-name-mobile {
  font-size: 1rem;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: #1f2937;
}

.expense-details-mobile {
  margin: 0;
  color: #6b7280;
  font-size: 0.85rem;
}

.amount-badge {
  background: linear-gradient(45deg, #dc2626, #b91c1c);
  color: white;
  padding: 6px 12px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.9rem;
}

.card-body {
  margin-bottom: 10px;
}

.description-section {
  padding: 8px 12px;
  background: #f8faff;
  border-radius: 8px;
}

.description-label {
  font-weight: 600;
  color: #374151;
  font-size: 0.85rem;
  margin-right: 8px;
}

.description-value {
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
  margin-bottom: 20px;
}

.empty-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(255,255,255,0.2);
  color: white;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.empty-action-btn:hover {
  background: rgba(255,255,255,0.3);
  transform: translateY(-2px);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 9999;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 2px solid #f3f4f6;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 700;
  color: #1f2937;
}

.modal-close {
  background: #f3f4f6;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: #e5e7eb;
}

.expense-form {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  outline: none;
  font-size: 16px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  border-color: #667eea;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  padding-top: 20px;
  border-top: 2px solid #f3f4f6;
}

.btn-cancel,
.btn-submit {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-submit {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.expense-row:nth-child(1) { animation-delay: 0.1s; }
.expense-row:nth-child(2) { animation-delay: 0.2s; }
.expense-row:nth-child(3) { animation-delay: 0.3s; }
.expense-row:nth-child(4) { animation-delay: 0.4s; }
.expense-row:nth-child(5) { animation-delay: 0.5s; }

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
  .expenses-container {
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
    flex-direction: row;
    gap: 10px;
  }

  .month-selector {
    width: 100%;
  }
  
  .control-btn {
    width: 40%;
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
  
  .expense-card {
    padding: 10px;
  }
  
  .card-header {
    margin-bottom: 8px;
    padding-bottom: 8px;
  }
  
  .card-footer {
    padding-top: 8px;
  }
  
  .modal-content {
    width: 95%;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .expenses-container {
    padding: 10px;
    padding-top: 3.5rem;
  }

  .card-header {
    flex-direction: row;
    gap: 8px;
    text-align: center;
  }
  
  .expense-info-mobile {
    text-align: left;
    margin-left: 1rem;
  }
  
  .modal-actions {
    flex-direction: column;
  }
  
  .month-controls {
    flex-direction: column;
    gap: 10px;
  }

  .month-selector {
    width: 100%;
  }
  .control-btn {
    width: 100%;
    height: 44px;
    justify-content: center;
    font-size: 16px;
  }
}
</style>
