<template>
  <div class="container">
    <h2>Monthly Expenses</h2>
    <!-- Month Selector & Controls -->
    <div class="month-controls">
      <input type="month" v-model="selectedMonth" />
      <button @click="openExpenseModal" style="font-size: 1.1rem;">Add Expense</button>      
    </div>

    <!-- Add Expense Modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal">
        <h3>Add New Expense</h3>
        <form @submit.prevent="addExpense">
          <input v-model="expenseForm.name" type="text" placeholder="Expense Name*" required />
          <input v-model="expenseForm.date" type="date" required />
          <input v-model.number="expenseForm.amount" type="number" placeholder="Amount*" required min="1" />
          <select v-model="expenseForm.category">
            <option value="">Select Category (optional)</option>
            <option value="Utilities">Utilities</option>
            <option value="Maintenance">Maintenance</option>
            <option value="Supplies">Supplies</option>
            <option value="Repair">Repair</option>
            <option value="Other">Other</option>
          </select>
          <textarea v-model="expenseForm.description" placeholder="Description (optional)" rows="2"></textarea>
          <div class="modal-actions">
            <button type="submit">Add</button>
            <button @click.prevent="closeModal" type="button">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Expenses Table -->
    <table v-if="expenses.length">
      <thead>
        <tr>
          <th>Name</th>
          <th>Amount</th>
          <th>Date</th>
          <th>Category</th>
          <th>Description</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="expense in expenses" :key="expense.id" >
          <td>{{ expense.name }}</td>
          <td>₹{{ expense.amount }}</td>
          <td>{{ formatDate(expense.date) }}</td>
          <td>{{ expense.category || '—' }}</td>
          <td>{{ expense.description || '—' }}</td>
          <td>
            <button class="action-button mark-left" @click="deleteExpense(expense)">Delete</button>
          </td>
        </tr>
        <!-- Monthly Total Row -->
        <tr style="font-weight: bold; background: #E8E8EE">
          <td colspan="1">Total</td>
          <td colspan="1">₹{{ totalExpenses }}</td>
          <!-- <td colspan="3"></td> -->
        </tr>
      </tbody>
    </table>
    <p v-else class="no-data">No expenses for this month yet. Add one!</p>
  </div>
</template>

<script>
import API from '../api';

export default {
  data() {
    const today = new Date();
    const defaultMonth = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
    return {
      selectedMonth: defaultMonth,
      expenses: [],
      showModal: false,
      expenseForm: {
        name: '',
        date: new Date().toISOString().slice(0, 10),
        amount: '',
        description: '',
        category: '',
      }
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
      try {
        const res = await API.get(`/monthly-expenses/${this.selectedMonth}`);
        this.expenses = res.data;
      } catch (err) {
        alert('Error fetching monthly expenses');
      }
    },
    openExpenseModal() {
      this.showModal = true;
      // Reset form to defaults
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
      try {
        // Optional: basic input validation
        if (!this.expenseForm.name.trim() || !this.expenseForm.amount || !this.expenseForm.date) {
          alert("Fill all required fields.");
          return;
        }
        await API.post('/monthly-expenses/', this.expenseForm);
        this.closeModal();
        this.fetchExpenses();
      } catch (err) {
        alert('Error adding expense');
      }
    },
    async deleteExpense(expense) {
      if (!confirm('Delete this expense?')) return;
      try {
        await API.delete(`/monthly-expenses/${expense.id}`);
        this.fetchExpenses();
      } catch (err) {
        alert('Error deleting expense');
      }
    },
    
    formatDate(dateStr) {
      const d = new Date(dateStr);
      return `${String(d.getDate()).padStart(2, '0')}-${String(d.getMonth() + 1).padStart(2, '0')}-${d.getFullYear()}`;
    }
  },
  computed: {
    totalExpenses() {
      return this.expenses.reduce((total, exp) => total + (exp.amount || 0), 0);
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 100%;
  margin: 5vh auto;
  padding: 2rem;
  font-family: "Segoe UI", "Poppins", sans-serif;
  background: linear-gradient(to bottom right, #f7faff3e, #e0f7fa33);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  height: 80vh;
  overflow-y: auto;
  padding-top: 5vh;
  scrollbar-width: 0px;
}

h2 {
  text-align: center;
  margin-bottom: 1rem;
  color: #333;
  font-size: 1.6rem;
  font-weight: 600;
}

/* Controls */
.month-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 5rem;
  align-items: center;
  justify-content: flex-start;
  margin-bottom: 1.5rem;
  
}
.month-controls input[type="month"] {
  padding: 10px;
  font-size: 0.95rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  min-width: 140px;
  width: 25%;
}
.month-controls button {
  padding: 10px 16px;
  font-size: 0.95rem;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  background-color: #8725d3;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  width: 30%;
}
.month-controls button:hover {
  background-color: #7f22c6;
  transform: scale(1.03);
  filter: brightness(1.08);
  
}

/* Table Styles */
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  text-transform: capitalize;
}
th, td {
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
  text-align: left;
  font-size: 0.95rem;
  font-weight: 500;
  text-transform: capitalize;
}
thead {
  background-color: #f3f3f3;
}
tbody tr:nth-child(even) {
  background-color: #fafafaa6;
}
.no-data {
  text-align: center;
  margin-top: 2rem;
  color: green;
  font-style: italic;
  font-size: 1rem;
}

/* Action Buttons */
.action-button {
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-right: 0.5rem;
  width: 90%;
}
.action-button.mark-left {
  background-color: #dc3545;
}
.action-button.mark-left:hover {
  /* background-color: #b02a37; */
  transform: scale(1.03);
  filter: brightness(1.08);
}

/* Modal */
.modal-overlay {
  position: fixed;
  z-index: 9999;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.19);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal {
  background: #fff;
  padding: 2rem;
  border-radius: 12px;
  min-width: 320px;
  max-width: 50vw;
  box-shadow: 0 8px 32px rgba(50,32,81,0.18);
}

.modal h3 {
  margin-bottom: 1rem;
}
.modal input, .modal textarea, .modal select {
  width: 95%;
  margin-bottom: 1rem;
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #bbb;
}
.modal-actions {
  display: flex;
  gap: 2rem;
  justify-content: center;
}
.modal-actions button {
  padding: 0.8em 1.4em;
  font-size: 1rem;
  border-radius: 6px;
  background: #8725d3;
  color: #fff;
  border: none;
  cursor: pointer;
  width: 45%;
}
.modal-actions button[type="button"] {
  background: #bbb;
  color: #222;
}
.modal-actions button:hover {
  filter: brightness(1.08);
}

/* Responsive for mobile */
@media (max-width: 768px) {
  .container {
    padding: 0.5rem;
    margin: 0vh 0rem;
    height: 98vh;
    padding-top: 7vh;
  }

.month-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  justify-content: flex-start;
  margin-bottom: 1.5rem;
  
}

  .month-controls input[type="month"], .month-controls button {
    width: 90%;
    margin-bottom: 0.5rem;
    margin: auto;
    /* font-weight: 500; */
  }

.modal-overlay {
  position: fixed;
  z-index: 9999;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.19);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal {
  background: #fff;
  padding: 0.5rem;
  border-radius: 12px;
  /* min-width: 320px; */
  width: 80%;
  box-shadow: 0 8px 32px rgba(50,32,81,0.18);
}
.modal h3 {
  margin-bottom: 1rem;
}
.modal input, .modal textarea, .modal select {
  width: 80%;
  margin-bottom: 1rem;
  padding: 10px;
  border-radius: 5px;
  border: 1px solid #bbb;
}
.modal-actions {
  display: flex;
  gap: 1rem;
  margin: 1rem;
  justify-content: center;
}
.modal-actions button {
  padding: 0.8em 1.4em;
  font-size: 1rem;
  border-radius: 6px;
  background: #8725d3;
  color: #fff;
  border: none;
  cursor: pointer;
  width: 40%;
}
.modal-actions button[type="button"] {
  background: #bbb;
  color: #222;
  width: 40%;
}
.modal-actions button:hover {
  filter: brightness(1.08);
  transform:scale(1.03)
}


  table {
    display: block;
    width: 95%;
    margin: 2vh 0rem;
    text-transform: capitalize;
  }
  thead {
    display: none;
  }
  tbody, tr, td {
    display: block;
    width: 98%;
    text-transform: capitalize;
  }
  tr {
    margin-bottom: 1rem;
    background-color: #ffffff3f;
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 1rem;
    text-transform: capitalize;
  }
  td {
    text-align: left;
    padding-left: 45%;
    position: relative;
    box-sizing: border-box;
    font-size: 0.95rem;
    line-height: 1.5;
    border: 1px solid #ddd;
    text-transform: capitalize;
  }
  td::before {
    position: absolute;
    left: 1rem;
    top: 0.6rem;
    font-weight: 600;
    color: #333;
    /* text-transform: capitalize; */
  }
  td:nth-child(1)::before { content: "Name";  }
  td:nth-child(2)::before { content: "Amount"; }
  td:nth-child(3)::before { content: "Date"; }
  td:nth-child(4)::before { content: "Category"; }
  td:nth-child(5)::before { content: "Description"; }
  td:nth-child(6)::before { content: "Actions"; }
  .action-button {
    width: 100%;
    margin-top: 0.6rem;
    font-size: 1rem;
  }
}
</style>
