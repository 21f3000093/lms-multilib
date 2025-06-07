<template>
  <div class="container">
    <h2>Monthly Fee Management</h2>

    <!-- Month Selector and Generate Button -->
    <div class="month-controls">
      <label>
        Select Month:
        <input type="month" v-model="selectedMonth" />
      </label>
      <button @click="generatePayments">Generate</button>
      <button @click="downloadCSV">📥 Export CSV</button>

    </div>

    <!-- Filters -->
    <div class="filters">
      <input type="text" v-model="searchTerm" placeholder="Search by name" />
      <select v-model="statusFilter">
        <option value="">All</option>
        <option value="paid">Paid</option>
        <option value="unpaid">Unpaid</option>
      </select>
    </div>


    <table v-if="payments.length">
        <thead>
            <tr>
            <th>Name</th>
            <th>Seat</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Actions</th> <!-- New -->
            </tr>
        </thead>
        <tbody>
            <!-- <tr v-for="payment in payments" :key="payment.id"> -->
            <tr v-for="payment in filteredPayments" :key="payment.id">
            <td>{{ payment.student.name }}</td>
            <td>{{ payment.student.seat_id }}</td>
            <td>₹{{ payment.amount }}</td>
            <td>
                <span :style="{ color: payment.paid ? 'green' : 'red' }">
                {{ payment.paid ?  '✅ Paid' : '❌ Unpaid' }}
                </span>
            </td>
            <td>
                <button class="action-button edit" @click="togglePaid(payment)" :style="{ backgroundColor: payment.paid ? 'blue' : 'green' }">
                {{ payment.paid ? 'Mark Unpaid' : 'Mark Paid' }}
                </button>
                <button class="action-button mark-left" @click="deletePayment(payment)" >Delete</button>
            </td>
            </tr>
        </tbody>
    </table>

    <p v-else class="no-data">No records found. Try generating for this month.</p>
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
      payments: [],
      searchTerm: '',
      statusFilter: ''
    };
    
  },
  mounted() {
    this.fetchPayments();
  },
  methods: {
    async fetchPayments() {
      try {
        const res = await API.get(`/monthly-payments/${this.selectedMonth}`);
        this.payments = res.data;
      } catch (err) {
        alert('Error fetching monthly payments');
      }
    },
    async togglePaid(payment) {
        try {
        const res = await API.put(`/monthly-payments/toggle/${payment.id}`);
        payment.paid = res.data.paid;
        } catch (err) {
        alert('Failed to toggle status');
        }
    },

  async deletePayment(payment) {
        if (!confirm('Are you sure you want to delete this payment?')) return;
        try {
        await API.delete(`/monthly-payments/${payment.id}`);
        this.payments = this.payments.filter(p => p.id !== payment.id);
        } catch (err) {
        alert('Error deleting payment');
        }
    },
    async generatePayments() {
      try {
        await API.post(`/generate-monthly-payments/${this.selectedMonth}`);
        alert(`Records generated for ${this.selectedMonth}`);
        this.fetchPayments(); // refresh the list
      } catch (err) {
        alert('Error generating monthly records');
      }
    },

    async downloadCSV() {
      try {
        const response = await API.get(`/export-monthly-payments/${this.selectedMonth}`, {
          responseType: 'blob',
        });
        const blob = new Blob([response.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `monthly_payments_${this.selectedMonth}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } catch (err) {
        alert('Failed to export CSV');
      }
    }

  },

  computed: {
      filteredPayments() {
        return this.payments.filter(payment => {
          const matchesName = payment.student.name.toLowerCase().includes(this.searchTerm.toLowerCase());
          const matchesStatus =
            this.statusFilter === '' ||
            (this.statusFilter === 'paid' && payment.paid) ||
            (this.statusFilter === 'unpaid' && !payment.paid);
          return matchesName && matchesStatus;
        });
      }
    },

};
</script>

<style scoped>
.container {
  max-width: 960px;
  margin: 5vh auto;
  padding: 2rem;
  font-family: "Segoe UI", sans-serif;
  background-color: #fdfdfd;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

/* Month selector and buttons */
.month-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.month-controls label {
  font-weight: 500;
  font-size: 1rem;
}

.month-controls input[type="month"] {
  padding: 8px;
  font-size: 1rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  margin-left: 0.5rem;
}

.month-controls button {
  padding: 10px 14px;
  font-size: 0.95rem;
  border: none;
  border-radius: 6px;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  transition: background 0.3s;
}

.month-controls button:hover {
  background-color: #0056b3;
}

/* Filters */
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.filters input[type="text"],
.filters select {
  padding: 10px;
  font-size: 0.95rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  flex: 1;
  min-width: 140px;
}

/* Action buttons */
.action-button {
  padding: 6px 10px;
  margin: 0 4px;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.action-button.edit:hover {
  background-color: #006400;
}

.action-button.mark-left {
  background-color: #dc3545;
}

.action-button.mark-left:hover {
  background-color: #b02a37;
}

/* No data message */
.no-data {
  text-align: center;
  margin-top: 2rem;
  color: #666;
  font-style: italic;
}


table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th, td {
  padding: 0.75rem;
  border: 1px solid #ccc;
  text-align: left;
}

@media (max-width: 768px) {
  .container {
    padding: 1rem;
    margin: 2vh 1rem;
  }

  .month-controls,
  .filters {
    flex-direction: column;
    align-items: stretch;
  }

  .month-controls label,
  .month-controls input[type="month"],
  .month-controls button,
  .filters input[type="text"],
  .filters select {
    width: 100%;
    font-size: 1rem;
  }

  .month-controls button,
  .filters select {
    margin-top: 0.5rem;
  }

  table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }

  th, td {
    font-size: 0.85rem;
    padding: 0.5rem;
  }

  .action-button {
    margin: 4px 0;
    display: block;
    width: 100%;
    font-size: 0.9rem;
  }

  .action-button.edit,
  .action-button.mark-left {
    width: 100%;
    margin: 4px 0;
  }
}

</style>