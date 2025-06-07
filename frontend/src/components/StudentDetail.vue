<template>
  <div class="student-detail">
    <h2>Student: {{ student?.name }}</h2>
    <p><strong>Contact:</strong> {{ student?.contact }}</p>
    <p><strong>Date of Joining:</strong> {{ student?.date_of_joining }}</p>
    <p><strong>Status:</strong> {{ student?.status }}</p>

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
          <td>{{ payment.month }}</td>
          <td>₹{{ payment.amount }}</td>
          <td>
            <span :class="{ paid: payment.paid, unpaid: !payment.paid }">
              {{ payment.paid ? "✅ Paid" : "❌ Unpaid" }}
            </span>
          </td>
          <td>
            <button @click="markAsPaid(payment)" :disabled="payment.paid">Mark Paid</button>
            <button @click="deletePayment(payment.id)">🗑️ Delete</button>
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
      const res = await API.get(`/students`);
      this.student = res.data.find((s) => s.id == id);
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
    }
  }
};
</script>

<style scoped>
.student-detail {
  max-width: 800px;
  margin: 2rem auto;
  padding: 1.5rem;
  background: #f9f9f9;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
  font-family: Arial, sans-serif;
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

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}

thead {
  background-color: #0066cc;
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
}

td button:last-of-type {
  background-color: #f44336;
  color: white;
}

td button:last-of-type:hover {
  background-color: #e53935;
}

.paid {
  color: green;
  font-weight: bold;
}

.unpaid {
  color: red;
  font-weight: bold;
}
</style>

