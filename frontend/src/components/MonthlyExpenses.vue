<template>
  <main class="monthly-expenses-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="section-shell hero">
      <div>
        <p class="kicker">Expense Tracking</p>
        <h1>
          Monthly
          <span class="gradient-text">Expenses</span>
        </h1>
        <p class="hero-subtitle">Track recurring costs, log new expenses, and monitor total monthly spend in one view.</p>
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

        <button @click="openExpenseModal" :disabled="loading" class="btn btn-solid" type="button">
          Add Expense
        </button>
      </div>
    </section>

    <section v-if="expenses.length > 0" class="section-shell summary-grid">
      <article class="glass-card stat-card">
        <p class="stat-label">Total Expenses</p>
        <p class="stat-value">{{ expenses.length }}</p>
      </article>
      <article class="glass-card stat-card">
        <p class="stat-label">Total Spent</p>
        <p class="stat-value">₹{{ formatAmount(totalExpenses) }}</p>
      </article>
    </section>

    <section v-if="loading" class="section-shell glass-card loading-card">
      <div class="loader"></div>
      <p>Loading expenses...</p>
    </section>

    <section v-else-if="expenses.length > 0" class="section-shell glass-card table-card desktop-view">
      <div class="table-wrap">
        <table class="expenses-table">
          <thead>
            <tr>
              <th>Expense</th>
              <th>Amount</th>
              <th>Date</th>
              <th>Category</th>
              <th>Description</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="expense in expenses" :key="expense.id">
              <td>
                <span class="expense-name">{{ expense.name }}</span>
              </td>
              <td>
                <span class="amount">₹{{ formatAmount(expense.amount) }}</span>
              </td>
              <td>{{ formatDate(expense.date) }}</td>
              <td>
                <span v-if="expense.category" class="category-pill">{{ expense.category }}</span>
                <span v-else class="muted">—</span>
              </td>
              <td>
                <span class="description" :title="expense.description">{{ expense.description || '—' }}</span>
              </td>
              <td>
                <button @click="deleteExpense(expense)" class="action-btn action-danger" type="button">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-else class="section-shell glass-card empty-state">
      <img src="../assets/svg/money-out-w.svg" class="empty-icon" alt="No expenses" />
      <h3>No Expenses Found</h3>
      <p>No expenses recorded for {{ formatMonth(selectedMonth) }} yet.</p>
      <button @click="openExpenseModal" class="btn btn-ghost" type="button">Add First Expense</button>
    </section>

    <section v-if="!loading && expenses.length > 0" class="section-shell mobile-view">
      <article
        v-for="expense in expenses"
        :key="expense.id"
        class="glass-card expense-card"
      >
        <header class="card-head">
          <div>
            <p class="expense-name">{{ expense.name }}</p>
            <p class="muted">{{ formatDate(expense.date) }} | {{ expense.category || 'Uncategorized' }}</p>
          </div>
          <span class="amount-badge">₹{{ formatAmount(expense.amount) }}</span>
        </header>

        <div v-if="expense.description" class="detail-row">
          <span class="muted">Description</span>
          <span>{{ expense.description }}</span>
        </div>

        <button @click="deleteExpense(expense)" class="action-btn action-danger mobile-action" type="button">Delete</button>
      </article>
    </section>

    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <section class="modal-content glass-card">
        <header class="modal-header">
          <h3>Add New Expense</h3>
          <button class="modal-close" @click="closeModal" type="button" aria-label="Close">✕</button>
        </header>

        <form @submit.prevent="addExpense" class="expense-form">
          <div class="form-group">
            <label class="field-label" for="expense-name">Expense Name</label>
            <input
              id="expense-name"
              v-model="expenseForm.name"
              type="text"
              placeholder="Enter expense name"
              required
              class="field-input"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="field-label" for="expense-amount">Amount</label>
              <input
                id="expense-amount"
                v-model.number="expenseForm.amount"
                type="number"
                placeholder="Enter amount"
                required
                min="1"
                class="field-input"
              />
            </div>

            <div class="form-group">
              <label class="field-label" for="expense-date">Date</label>
              <input
                id="expense-date"
                v-model="expenseForm.date"
                type="date"
                required
                class="field-input date-input"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="field-label" for="expense-category">Category</label>
            <select id="expense-category" v-model="expenseForm.category" class="field-input">
              <option value="">Select category (optional)</option>
              <option value="Utilities">Utilities</option>
              <option value="Maintenance">Maintenance</option>
              <option value="Supplies">Supplies</option>
              <option value="Repair">Repair</option>
              <option value="Rent">Rent</option>
              <option value="Internet">Internet</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div class="form-group">
            <label class="field-label" for="expense-description">Description</label>
            <textarea
              id="expense-description"
              v-model="expenseForm.description"
              placeholder="Enter description (optional)"
              rows="3"
              class="field-input textarea"
            ></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn btn-ghost">Cancel</button>
            <button type="submit" :disabled="loading" class="btn btn-solid">
              {{ loading ? 'Adding...' : 'Add Expense' }}
            </button>
          </div>
        </form>
      </section>
    </div>
  </main>
</template>

<script>
import API from '../api'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'

export default {
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
          backgroundColor: 'var(--theme-panel-solid)',
          color: 'var(--theme-text-strong)',
          border: '1px solid var(--theme-brand-border)',
          borderRadius: '12px',
          boxShadow: 'var(--theme-shadow-soft)',
        },
        ...options,
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
      expenses: [],
      showModal: false,
      loading: false,
      expenseForm: {
        name: '',
        date: new Date().toISOString().slice(0, 10),
        amount: '',
        description: '',
        category: '',
      },
    }
  },

  computed: {
    totalExpenses() {
      return this.expenses.reduce((total, expense) => total + (expense.amount || 0), 0)
    },
  },

  mounted() {
    this.fetchExpenses()
  },

  watch: {
    selectedMonth: 'fetchExpenses',
  },

  methods: {
    async fetchExpenses() {
      this.loading = true
      try {
        const res = await API.get(`/monthly-expenses/${this.selectedMonth}`)
        this.expenses = res.data
      } catch (err) {
        this.showError('Error fetching monthly expenses')
      } finally {
        this.loading = false
      }
    },

    openExpenseModal() {
      this.showModal = true
      this.expenseForm = {
        name: '',
        date: new Date().toISOString().slice(0, 10),
        amount: '',
        description: '',
        category: '',
      }
    },

    closeModal() {
      this.showModal = false
    },

    async addExpense() {
      if (!this.expenseForm.name.trim() || !this.expenseForm.amount || !this.expenseForm.date) {
        this.showError('Please fill all required fields')
        return
      }

      this.loading = true
      try {
        await API.post('/monthly-expenses/', this.expenseForm)
        this.showSuccess('Expense added successfully!')
        this.closeModal()
        this.fetchExpenses()
      } catch (err) {
        this.showError('Error adding expense')
      } finally {
        this.loading = false
      }
    },

    async deleteExpense(expense) {
      if (!confirm(`Are you sure you want to delete "${expense.name}"?`)) return

      try {
        await API.delete(`/monthly-expenses/${expense.id}`)
        this.showSuccess('Expense deleted successfully')
        this.fetchExpenses()
      } catch (err) {
        this.showError('Error deleting expense')
      }
    },

    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      const day = String(date.getDate()).padStart(2, '0')
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const year = String(date.getFullYear()).slice(-2)
      return `${day}-${month}-${year}`
    },

    formatAmount(amount) {
      return Number(amount || 0).toLocaleString('en-IN')
    },

    formatMonth(monthString) {
      if (monthString && monthString.includes('-')) {
        const [year, month] = monthString.split('-')
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return `${monthNames[parseInt(month) - 1]} ${year}`
      }
      return monthString
    },
  },
}
</script>

<style scoped>
.monthly-expenses-page {
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

.control-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.6rem;
  align-items: end;
}

.field-wrap {
  display: grid;
  gap: 0.35rem;
}

.field-label {
  color: var(--theme-text-soft);
  font-size: 0.8rem;
  font-weight: 600;
}

.field-input {
  width: 100%;
  border: 1px solid var(--theme-input-border);
  border-radius: 12px;
  background: var(--theme-input-bg);
  color: var(--theme-text-strong);
  min-height: 42px;
  padding: 0.5rem 0.7rem;
  outline: none;
  box-sizing: border-box;
}

.field-input:focus {
  border-color: var(--theme-brand-border);
  box-shadow: 0 0 0 3px var(--theme-brand-ring);
}

.field-input option {
  color: var(--theme-text-strong);
}

.month-input,
.date-input {
  color-scheme: inherit;
}

.month-input::-webkit-calendar-picker-indicator,
.date-input::-webkit-calendar-picker-indicator {
  filter: var(--theme-picker-filter);
  opacity: 0.95;
}

.textarea {
  min-height: 88px;
  resize: vertical;
}

.btn {
  min-height: 42px;
  border-radius: 12px;
  border: 1px solid transparent;
  padding: 0.5rem 0.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-solid {
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
  box-shadow: var(--theme-shadow-elevated);
  color: var(--theme-brand-on);
}

.btn-ghost {
  background: var(--theme-surface-soft-strong);
  border-color: var(--theme-border-strong);
  color: var(--theme-text-primary);
}

.summary-grid {
  margin-top: 0.85rem;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
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

.expenses-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 980px;
}

.expenses-table th {
  text-align: left;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--theme-text-soft);
  border-bottom: 1px solid var(--theme-border);
  padding: 0.64rem 0.55rem;
}

.expenses-table td {
  padding: 0.64rem 0.55rem;
  border-bottom: 1px solid var(--theme-border-soft);
  color: var(--theme-text-primary);
  font-size: 0.9rem;
  vertical-align: middle;
  text-align: left;
}

.expenses-table tbody tr:hover {
  background: var(--theme-surface-soft);
}

.expense-name {
  margin: 0;
  font-weight: 700;
  font-size: 0.88rem;
}

.amount {
  font-weight: 700;
  color: var(--theme-danger-text);
  font-family: Monaco, Menlo, monospace;
}

.category-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 56px;
  padding: 0.22rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
}

.description {
  color: var(--theme-text-soft);
  font-size: 0.84rem;
  max-width: 220px;
  display: inline-block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.muted {
  color: var(--text-secondary);
  margin: 0;
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
}

.action-danger {
  background: var(--theme-danger-soft);
  color: var(--theme-danger-text);
  border-color: var(--theme-danger-border);
}

.loading-card,
.empty-state {
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

.empty-icon {
  width: 68px;
  height: 68px;
}

.mobile-view {
  display: none;
  margin-top: 0.85rem;
  gap: 0.55rem;
}

.expense-card {
  border-radius: 14px;
  padding: 0.7rem;
}

.card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.5rem;
}

.amount-badge {
  border-radius: 999px;
  background: var(--theme-danger-soft);
  color: var(--theme-danger-text);
  padding: 0.22rem 0.55rem;
  font-size: 0.75rem;
  font-weight: 700;
  font-family: Monaco, Menlo, monospace;
}

.detail-row {
  margin-top: 0.55rem;
  border-radius: 10px;
  background: var(--theme-surface-soft-heavy);
  padding: 0.45rem 0.55rem;
  display: flex;
  justify-content: space-between;
  gap: 0.55rem;
}

.mobile-action {
  width: 100%;
  margin-top: 0.55rem;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1500;
  background: var(--theme-overlay);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.7rem;
}

.modal-content {
  width: min(620px, 100%);
  max-height: min(92vh, 860px);
  border-radius: 16px;
  overflow-y: auto;
}

.modal-header {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.6rem;
  padding: 0.75rem;
  border-bottom: 1px solid var(--theme-border-soft);
  background: var(--theme-panel-solid);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.02rem;
}

.modal-close {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid var(--theme-border-strong);
  background: var(--theme-surface-soft-heavy);
  color: var(--theme-text-primary);
  cursor: pointer;
}

.expense-form {
  padding: 0.75rem;
}

.form-group {
  margin-bottom: 0.55rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.55rem;
}

.modal-actions {
  margin-top: 0.55rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.55rem;
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

@media (max-width: 920px) {
  .desktop-view {
    display: none;
  }

  .mobile-view {
    display: grid;
  }
}

@media (max-width: 767px) {
  .monthly-expenses-page {
    padding: 2rem 1rem 5rem 1rem;
  }

  .section-shell {
    width: min(1240px, calc(100% - 1rem));
  }

  .control-grid,
  .summary-grid,
  .form-row,
  .modal-actions {
    grid-template-columns: 1fr;
  }

  .modal-content {
    width: 100%;
  }

  .field-input {
    font-size: 16px;
  }
}
</style>
