<template>
  <div class="container">
    <h2>Monthly Fee Management</h2>

    <!-- Month Selector and Generate Button -->
    <div class="month-controls">
      <!-- <label> -->
        <!-- Select Month: -->
      <input type="month" v-model="selectedMonth" />
      <!-- </label> -->
      <button @click="generatePayments">Generate</button>
      <button @click="downloadCSV">📥 Export CSV</button>
      
      
    <router-link to="/reminders">
      <button class="reminder-btn">📩 WhatsApp</button>
    </router-link>
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
            <th>Date of Joining</th>
            <th>Status</th>
            <th>Actions</th> <!-- New -->
            </tr>
        </thead>
        <tbody>
            <!-- <tr v-for="payment in payments" :key="payment.id"> -->
            <tr v-for="payment in filteredPayments" :key="payment.id">
            <td>{{ payment.student.name }}</td>
            <td>{{ payment.student.seat?.seat_number || '—' }}</td>  <!-- This should be the seat number . Will change in future-->
            <!-- <td>{{ payment.student.seat_id }}</td>  This should be the seat number . Will change in future -->
            <td>₹{{ payment.amount }}</td>
            <td>{{ formatDate(payment.student.date_of_joining) }}</td>
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
    },

    formatDate(dateString) {
        const date = new Date(dateString);
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0'); // JS months are 0-indexed
        const year = String(date.getFullYear()).slice(-2); // get last 2 digits
        return `${day}-${month}-${year}`;
    },

  },

  computed: {
      // filteredPayments() {
      //   return this.payments.filter(payment => {
      //     const matchesName = payment.student.name.toLowerCase().includes(this.searchTerm.toLowerCase());
      //     const matchesStatus =
      //       this.statusFilter === '' ||
      //       (this.statusFilter === 'paid' && payment.paid) ||
      //       (this.statusFilter === 'unpaid' && !payment.paid);
      //     return matchesName && matchesStatus;
      //   });
      // },


      filteredPayments() {
    return this.payments
      .filter(payment => {
        const matchesName = payment.student.name.toLowerCase().includes(this.searchTerm.toLowerCase());
        const matchesStatus =
          this.statusFilter === '' ||
          (this.statusFilter === 'paid' && payment.paid) ||
          (this.statusFilter === 'unpaid' && !payment.paid);
        return matchesName && matchesStatus;
      })
      .sort((a, b) => {
        const seatA = a.student.seat?.seat_number || 0;
        const seatB = b.student.seat?.seat_number || 0;
        return seatA - seatB;
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
  font-family: "Segoe UI", "Poppins", sans-serif;
  background: linear-gradient(to bottom right, #f7faff3e, #e0f7fa33);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  max-height: 70vh;
  overflow-y: auto;
  scrollbar-width: none;
}

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
  font-size: 1.6rem;
  font-weight: 600;
}

/* Month Controls + Filters */
.month-controls,
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.month-controls input[type="month"],
.filters input[type="text"],
.filters select {
  padding: 10px;
  font-size: 0.95rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  min-width: 140px;
}

.month-controls button,
.reminder-btn {
  padding: 10px 16px;
  font-size: 0.95rem;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  min-width: fit-content;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  background-color: #8725d3;
}

.reminder-btn:hover {
  background-color: #1ebe54;
}

.month-controls button:hover {
  background-color: #7f22c6;
  transform: scale(1.03); /* 👈 Slight hover scale */
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
}

.action-button.edit:hover {
  background-color: #006400;
  transform: scale(1.03);
}

.action-button.mark-left {
  background-color: #dc3545;
}

.action-button.mark-left:hover {
  background-color: #b02a37;
  transform: scale(1.03);
}

/* Table Base */
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th, td {
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
  text-align: left;
  font-size: 0.95rem;
  text-decoration: none;
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

/* ✅ Responsive: Mobile Card Layout */
@media (max-width: 768px) {
  table {
    display: block;
    width: 98%;
    margin: auto;
    text-decoration: none;
  font-weight: 500;
  text-transform: capitalize;
  }

  thead {
    display: none;
    text-decoration: none;
  font-weight: 500;
  text-transform: capitalize;
  }

  tbody, tr, td {
    display: block;
    width: 98%;
    text-decoration: none;
  font-weight: 500;
  text-transform: capitalize;
  }

  tr {
    margin-bottom: 1rem;
    background-color: #ffffff3f;
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    text-decoration: none;
    font-weight: 500;
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
    text-decoration: none;
    font-weight: 500;
    text-transform: capitalize;
  }

  td::before {
    position: absolute;
    left: 1rem;
    top: 0.6rem;
    font-weight: 600;
    color: #333;
    text-decoration: none;
    font-weight: 500;
    text-transform: capitalize;
  }

  td:nth-child(1)::before { content: "Name";  }
  td:nth-child(2)::before { content: "Seat"; }
  td:nth-child(3)::before { content: "Amount"; }
  td:nth-child(4)::before { content: "Date of Joining"; }
  td:nth-child(5)::before { content: "Status"; }
  td:nth-child(6)::before { content: "Actions"; }

  .action-button {
    width: 100%;
    margin-top: 0.6rem;
    font-size: 1rem;
    
  }

  .month-controls,
  .filters {
    flex-direction: row;
    gap: 0.8rem;
    /* max-width: 20%; */
    /* margin: auto; */
    
  }

  .month-controls button{
    /* display: flex; */
    width: 40%;
    /* flex-direction: row; */
    gap: 0.8rem;
    /* margin: auto; */
  }

  /* .month-controls router-link .reminder-btn {
    width: 100%;
    margin-bottom: 1rem;
  } */
}
</style>
