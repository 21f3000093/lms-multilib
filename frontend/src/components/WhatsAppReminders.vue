<template>
  <div class="container">
    <h2>📬 WhatsApp Fee Reminders</h2>

    <button @click="fetchReminders" class="fetch-btn">🔄 Load Reminders</button>

    <table v-if="pendingList.length > 0" class="reminder-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Phone</th>
          <th>Amount</th>
          <th>Month</th>
          <th>Due Date</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="student in pendingList" :key="student.phone">
          <td>{{ student.student_name }}</td>
          <td>{{ student.phone }}</td>
          <td>₹{{ student.amount }}</td>
          <td>{{ student.month }}</td>
          <td>{{ student.due_date }}</td>
          <td>
            <button @click="sendWhatsApp(student)">Send WhatsApp</button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else class="no-data">✅ No pending reminders</p>
  </div>
</template>

<script>
import API from '../api';

export default {
  data() {
    return {
      pendingList: [],
    };
  },
  methods: {
    async fetchReminders() {
      try {
        const res = await API.get("/reminders/pending-fees");
        this.pendingList = res.data;
      } catch (err) {
        alert("Failed to fetch reminders: " + (err.response?.data?.detail || err.message));
      }
    },
    sendWhatsApp(student) {
      const msg = `Dear ${student.student_name}, your library fee of ₹${student.amount} for ${student.month} was due on ${student.due_date}. Please pay it soon.`;
      const phone = "91" + student.phone.replace(/^0+/, "");
      const url = `https://wa.me/${phone}?text=${encodeURIComponent(msg)}`;
      window.open(url, "_blank");
    },
  },
  created() {
    this.fetchReminders();
  },
};
</script>

<style scoped>
.container {
  padding: 20px;
  max-width: 1000px;
  margin: auto;
}

.fetch-btn {
  margin-bottom: 20px;
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
}

.reminder-table {
  width: 100%;
  border-collapse: collapse;
}

.reminder-table th,
.reminder-table td {
  border: 1px solid #ccc;
  padding: 10px;
  text-align: center;
}

.reminder-table th {
  background-color: #f2f2f2;
}

.no-data {
  margin-top: 20px;
  font-style: italic;
  color: green;
}
</style>
