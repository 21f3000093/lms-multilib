<template>
  <div class="student-detail">
    <!-- Student Profile Card -->
    <div class="profile-card">
      <div class="profile-header">
        <div class="avatar">{{ student?.name?.charAt(0) }}</div>
        <div class="info">
          <h2>{{ student?.name }}</h2>
          <p><strong>Contact:</strong> {{ student?.contact }}</p>
          <p><strong>Date of Joining:</strong> {{ formatDate(student?.date_of_joining) }}</p>
          <p><strong>Status:</strong> 
            <span class="status-badge" :class="student?.status">{{ student?.status }}</span>
          </p>
        </div>
      </div>
    </div>

    <h3>Monthly Payments</h3>
    <table v-if="payments.length">
      <thead>
        <tr>
          <th>Month</th>
          <th>Amount</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="payment in payments" :key="payment.id">
          <td>{{ formatMonth(payment.month) }}</td>
          <td>₹{{ payment.amount }}</td>
          <td>
            <span :class="{ paid: payment.paid, unpaid: !payment.paid }">
              {{ payment.paid ? "✅ Paid" : "❌ Unpaid" }}
            </span>
          </td>
          <td>
            <!-- <button @click="markAsPaid(payment)" :disabled="payment.paid">Mark Paid</button> -->
            <button @click="togglePaid(payment)" :style="{ backgroundColor: payment.paid ? 'blue' : 'green' }">{{ payment.paid ? 'Unpaid' : 'Paid' }}</button>
            <button @click="deletePayment(payment.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else>No payments found.</p>
  </div>
</template>

<script>
import API from '../api';

export default {
  data() {
    return {
      student: null,
      payments: [],
    };
  },
  async mounted() {
    const id = this.$route.params.id;
    await this.fetchStudent(id);
    await this.fetchPayments(id);
  },
  methods: {
    async fetchStudent(id) {
      const res = await API.get(`/students/${id}`);
      this.student = res.data;
    },
    async fetchPayments(id) {
      const res = await API.get(`/students/${id}/payments`);
      this.payments = res.data;
    },
    async markAsPaid(payment) {
      await API.put(`/monthly-payments/${payment.id}`);
      payment.paid = true;
    },
    async deletePayment(id) {
      if (confirm('Are you sure?')) {
        await API.delete(`/monthly-payments/${id}`);
        this.payments = this.payments.filter(p => p.id !== id);
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
    formatDate(dateStr) {
      if (!dateStr) return '';
      // remove time part if present
      const ymd = dateStr.split('T')[0];
      const parts = ymd.split('-');
      if (parts.length !== 3) return dateStr; // fallback
      const [y, m, d] = parts;
      // ensure two digits for day/month
      return `${d.padStart(2, '0')}-${m.padStart(2, '0')}-${y}`;
    },

    formatMonth(monthStr) {
      if (!monthStr) return '';
      // Accept both 'YYYY-MM' and 'YYYY-MM-DD' and 'YYYY-MM-DDTHH:MM:SS'
      const ymd = monthStr.split('T')[0];
      const parts = ymd.split('-');
      if (parts.length < 2) return monthStr;
      const year = parseInt(parts[0], 10);
      const monthIndex = parseInt(parts[1], 10) - 1; // JS monthIndex 0-11
      if (Number.isNaN(year) || Number.isNaN(monthIndex)) return monthStr;
      const dt = new Date(year, monthIndex, 1);
      // returns e.g. "August 2025"
      return dt.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    },
  }
};
</script>

<style scoped>
.student-detail {
  max-width: 100vw;
  margin: 2rem auto;
  padding: 1.5rem;
  background: #f9f9f968;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
  font-family: Arial, sans-serif;
  padding-top: 10vh;
}

.student-detail h2,
.student-detail h3 {
  margin-bottom: 1rem;
  color: #333;
}

.student-detail p {
  margin: 0.5rem 0;
  font-size: 1rem;
}


/* Profile Card */
.profile-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 3px 8px rgba(0,0,0,0.1);
  margin-bottom: 1rem;
  padding: 1rem;
  margin: auto;
  width: 40%;
}

.profile-header {
  display: flex;
  align-items: center;
  justify-content: center;
}
.avatar {
  width: 60px;
  height: 60px;
  background: #6200ea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  margin-right: 1rem;
}
.info h2 {
  margin: 0;
}

/* Status badge */
.status-badge {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
  color: white;
}
.status-badge.active { background: green; }
.status-badge.left { background: red; }
.status-badge.paid { background: green; }
.status-badge.unpaid { background: red; }

table {
  width: 90%;
  border-collapse: collapse;
  margin-top: 1rem;
  background: #fff;
  border-radius: 8px;
  overflow: auto;
  margin: auto;
}

thead {
  background-color: #3a00ccb8;
  color: white;
  
}

th, td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

td button {
  margin-right: 8px;
  padding: 6px 12px;
  font-size: 0.9rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease;
  width: 40%;
}

td button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

td button:first-of-type {
  background-color: #4caf50;
  color: white;
}

td button:first-of-type:hover:enabled {
  background-color: #43a047;
  transform: scale(1.03);
  
}

td button:last-of-type {
  background-color: #f44336;
  color: white;
}

td button:last-of-type:hover {
  background-color: #e53935;
  transform: scale(1.03);
}

.paid {
  color: green;
  /* font-weight: bold; */
}

.unpaid {
  color: red;
  /* font-weight: bold; */
}

@media(max-width: 768px) {
  .student-detail {
    padding: 1rem;
    /* overflow: auto; */
    padding-top: 7vh;
    background-color: #ffffff5e;
  }
  table {
    width: 100%;
    overflow: auto;
    background-color: #ffffff00;

  }

  thead {
  background-color: #3a00ccb8;
  color: white;
  /* width: 130%; */
  overflow: auto
  
}

td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
  width: 10%;
}

  td button {
  margin-right: 8px;
  margin-bottom: 8px;
  width: 80%;
  padding: 6px 12px;
  font-size: 0.9rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease;
  gap: 1rem;
}

.profile-card {
  width: 90%;

}

}



</style>

