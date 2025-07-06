<template>
  <div class="dashboard-container">
    <h2 class="dashboard-title">📊 Admin Dashboard</h2>
    <div class="dashboard-grid">
      <div class="dashboard-card">
        <h3>Shift 1</h3>
        <p>{{ data.shift1_count }}/{{ data.max_seats }}</p>
      </div>
      <div class="dashboard-card">
        <h3>Shift 2</h3>
        <p>{{ data.shift2_count }}/{{ data.max_seats }}</p>
      </div>
      <div class="dashboard-card">
        <h3>Shift 3</h3>
        <p>{{ data.shift3_count }}/{{ data.max_seats }}</p>
      </div>
      <div class="dashboard-card">
        <h3>Total Students</h3>
        <p>{{ data.total_students }}</p>
      </div>
      <div class="dashboard-card revenue">
        <h3>Monthly Revenue</h3>
        <p>₹{{ totalRevenue }}</p>
      </div>
      <div class="dashboard-card revenue">
        <h3>Collected This Month</h3>
        <p>₹{{ monthlyCollected }}</p>
      </div>

    </div>
  </div>
</template>

<script>
import API from '../api';

export default {
  data() {
    return {
      data: {},
    };
  },
  computed: {
    totalRevenue() {
      return this.data.revenue || 0;
    },
    monthlyCollected() {
      return this.data.monthly_collected || 0;
    }
  },

  async created() {
    try {
      const res = await API.get('/dashboard/');
      this.data = res.data;
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    }
  }
};
</script>

<style scoped>
.dashboard-container {
  max-width: 800px;
  margin: auto;
  padding: 1.5rem;
}

.dashboard-title {
  text-align: center;
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.dashboard-card {
  background-color: rgba(249, 249, 249, 0.119);
  border-left: 6px solid #3498db;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  text-align: center;
}

.dashboard-card h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

.dashboard-card p {
  margin-top: 0.5rem;
  font-size: 1.4rem;
  font-weight: bold;
  color: #2c3e50;
}

.dashboard-card.revenue {
  border-left-color: #27ae60;
}

@media (min-width: 600px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 900px) {
  .dashboard-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
