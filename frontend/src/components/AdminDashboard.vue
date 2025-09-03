<template>
  <div class="dashboard-container">
    <div class="header-section">
      <h2 class="dashboard-title">Admin Dashboard</h2>
      <p class="dashboard-subtitle">Library Management Overview</p>
    </div>

    <!-- Quick Stats Summary -->
    <div class="quick-stats">
      <div class="stat-item">
        <span class="stat-number">{{ data.total_students || 0 }}</span>
        <span class="stat-label">Total Students</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">{{ overallOccupancy }}%</span>
        <span class="stat-label">Overall Occupancy</span>
      </div>
      <div class="stat-item">
        <span class="stat-number">₹{{ formatNumber(monthlyCollected) }}</span>
        <span class="stat-label">Collected</span>
      </div>
    </div>

    <div class="dashboard-grid">
      <!-- Shift Cards -->
      <div class="dashboard-card shift-card">
        <div class="card-header">
          <!-- <div class="card-icon shift-icon">🌅</div> -->
           <div class=" shift-icon card-icon">
             <img src="../assets/svg/sunrise-svgrepo-com1.svg" class="svg" alt="" loading="lazy">
           </div>
          <h3>Shift 1</h3>
          <span class="shift-time">Morning</span>
        </div>
        <div class="occupancy-display">
          <div class="occupancy-numbers">
            <span class="current">{{ data.shift1_count || 0 }}</span>
            <span class="separator">/</span>
            <span class="total">{{ data.max_seats || 0 }}</span>
          </div>
          <div class="occupancy-percentage">{{ getShiftPercentage(1) }}% occupied</div>
        </div>
        <div class="progress-container">
          <div class="progress-bar">
            <div 
              class="progress-fill shift1" 
              :style="{ width: getShiftPercentage(1) + '%' }"
            ></div>
          </div>
        </div>
        <div class="availability-status" :class="getStatusClass(1)">
          {{ getAvailabilityText(1) }}
        </div>
      </div>

      <div class="dashboard-card shift-card">
        <div class="card-header">
          <!-- <div class="card-icon shift-icon">☀️</div> -->
           <div class=" shift-icon card-icon">
             <img src="../assets/svg/afternoonsun.svg" class="svg" alt="" loading="lazy">
           </div>
          <h3>Shift 2</h3>
          <span class="shift-time">Afternoon</span>
        </div>
        <div class="occupancy-display">
          <div class="occupancy-numbers">
            <span class="current">{{ data.shift2_count || 0 }}</span>
            <span class="separator">/</span>
            <span class="total">{{ data.max_seats || 0 }}</span>
          </div>
          <div class="occupancy-percentage">{{ getShiftPercentage(2) }}% occupied</div>
        </div>
        <div class="progress-container">
          <div class="progress-bar">
            <div 
              class="progress-fill shift2" 
              :style="{ width: getShiftPercentage(2) + '%' }"
            ></div>
          </div>
        </div>
        <div class="availability-status" :class="getStatusClass(2)">
          {{ getAvailabilityText(2) }}
        </div>
      </div>

      <div class="dashboard-card shift-card">
        <div class="card-header">
          <!-- <div class="card-icon shift-icon">🌙</div> -->
           <div class="shift-icon card-icon ">
             <img src="../assets/svg/night-svgrepo-com.svg" class="svg" alt="" loading="lazy">
           </div>
          <h3>Shift 3</h3>
          <span class="shift-time">Evening</span>
        </div>
        <div class="occupancy-display">
          <div class="occupancy-numbers">
            <span class="current">{{ data.shift3_count || 0 }}</span>
            <span class="separator">/</span>
            <span class="total">{{ data.max_seats || 0 }}</span>
          </div>
          <div class="occupancy-percentage">{{ getShiftPercentage(3) }}% occupied</div>
        </div>
        <div class="progress-container">
          <div class="progress-bar">
            <div 
              class="progress-fill shift3" 
              :style="{ width: getShiftPercentage(3) + '%' }"
            ></div>
          </div>
        </div>
        <div class="availability-status" :class="getStatusClass(3)">
          {{ getAvailabilityText(3) }}
        </div>
      </div>

      <!-- Total Students Card -->
      <div class="dashboard-card students-card">
        <div class="card-header">
          <div class="card-icon students-icon">
            <!-- 👥 -->
            <img src="../assets/svg/student-white.svg" class="svg" alt="" loading="lazy">
          </div>

          <h3>Total Students</h3>
        </div>
        <div class="metric-display">
          <div class="main-number">{{ data.total_students || 0 }}</div>
          <div class="metric-subtitle">Active Enrollments</div>
        </div>
        <div class="students-breakdown">
          <div class="breakdown-item">
            <span class="breakdown-label">Morning</span>
            <span class="breakdown-value">{{ data.shift1_count || 0 }}</span>
          </div>
          <div class="breakdown-item">
            <span class="breakdown-label">Afternoon</span>
            <span class="breakdown-value">{{ data.shift2_count || 0 }}</span>
          </div>
          <div class="breakdown-item">
            <span class="breakdown-label">Evening</span>
            <span class="breakdown-value">{{ data.shift3_count || 0 }}</span>
          </div>
        </div>
      </div>

      <!-- Revenue Cards -->
      <div class="dashboard-card revenue-card">
        <div class="card-header">
          <div class="card-icon revenue-icon">
            <!-- 💰 -->
            <img src="../assets/svg/money-dollar.svg" class="svg" alt="" loading="lazy">
          </div>
          <h3>Monthly Revenue</h3>
        </div>
        <div class="metric-display">
          <div class="main-number revenue-amount">₹{{ formatNumber(totalRevenue) }}</div>
          <div class="metric-subtitle">Expected This Month</div>
        </div>
        <div class="revenue-details">
          <div class="detail-row">
            <span class="detail-label">Per Student Avg:</span>
            <span class="detail-value">₹{{ getAverageRevenue() }}</span>
          </div>
        </div>
      </div>

      <div class="dashboard-card collection-card">
        <div class="card-header">
          <div class="card-icon collection-icon">
            <!-- 💳 -->
            <img src="../assets/svg/money-recive-white.svg" class="svg" alt="" loading="lazy">
          </div>
          <h3>Collected This Month</h3>
        </div>
        <div class="metric-display">
          <div class="main-number collection-amount">₹{{ formatNumber(monthlyCollected) }}</div>
          <div class="metric-subtitle">{{ collectionPercentage }}% of target</div>
        </div>
        <div class="collection-progress">
          <div class="progress-container">
            <div class="progress-bar collection-bar">
              <div 
                class="progress-fill collection-fill" 
                :style="{ width: Math.min(collectionPercentage, 100) + '%' }"
              ></div>
            </div>
          </div>
          <div class="pending-amount">
            Pending: ₹{{ formatNumber(pendingAmount) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Additional Insights -->
    <div class="insights-section">

      <div class="insights-header">
        <img src="../assets/svg/chart1.svg" class="svg" alt="" loading="lazy">
        <h3>Quick Insights</h3>
      </div>

      <div class="insights-grid">
        <div class="insight-card">
          <div class="insight-icon">
            <img src="../assets/svg/star.svg" class="svg" alt="" loading="lazy">
          </div>
          <div class="insight-content">
            <h4>Best Performing Shift</h4>
            <p>{{ getBestShift() }}</p>
          </div>
        </div>
        <div class="insight-card">
          <div class="insight-icon">
            <!-- 📊 -->
            <img src="../assets/svg/chart-2.svg" class="svg" alt="" loading="lazy">
          </div>
          <div class="insight-content">
            <h4>Occupancy Rate</h4>
            <p>{{ overallOccupancy }}% average across all shifts</p>
          </div>
        </div>
        <div class="insight-card">
          <div class="insight-icon">
            <img src="../assets/svg/empty.svg" class="svg" alt="" loading="lazy">  
          </div>
          <div class="insight-content">
            <h4>Available Seats</h4>
            <p>{{ availableSeats }} seats can be filled</p>
          </div>
        </div>
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
    },
    
    collectionPercentage() {
      if (this.totalRevenue === 0) return 0;
      return Math.round((this.monthlyCollected / this.totalRevenue) * 100);
    },
    
    pendingAmount() {
      return Math.max(0, this.totalRevenue - this.monthlyCollected);
    },
    
    overallOccupancy() {
      const totalOccupied = (this.data.shift1_count || 0) + 
                           (this.data.shift2_count || 0) + 
                           (this.data.shift3_count || 0);
      const totalCapacity = (this.data.max_seats || 73) * 3;
      return totalCapacity > 0 ? Math.round((totalOccupied / totalCapacity) * 100) : 0;
    },
    
    availableSeats() {
      const totalCapacity = (this.data.max_seats || 73) * 3;
      const totalOccupied = (this.data.shift1_count || 0) + 
                           (this.data.shift2_count || 0) + 
                           (this.data.shift3_count || 0);
      return totalCapacity - totalOccupied;
    }
  },

  methods: {
    formatNumber(num) {
      return num.toLocaleString('en-IN');
    },
    
    getShiftPercentage(shiftNumber) {
      const maxSeats = this.data.max_seats || 73;
      let currentCount = 0;
      
      switch(shiftNumber) {
        case 1: currentCount = this.data.shift1_count || 0; break;
        case 2: currentCount = this.data.shift2_count || 0; break;
        case 3: currentCount = this.data.shift3_count || 0; break;
      }
      
      return maxSeats > 0 ? Math.round((currentCount / maxSeats) * 100) : 0;
    },
    
    getStatusClass(shiftNumber) {
      const percentage = this.getShiftPercentage(shiftNumber);
      if (percentage >= 90) return 'status-full';
      if (percentage >= 70) return 'status-high';
      if (percentage >= 40) return 'status-medium';
      return 'status-low';
    },
    
    getAvailabilityText(shiftNumber) {
      const percentage = this.getShiftPercentage(shiftNumber);
      const maxSeats = this.data.max_seats || 73;
      let currentCount = 0;
      
      switch(shiftNumber) {
        case 1: currentCount = this.data.shift1_count || 0; break;
        case 2: currentCount = this.data.shift2_count || 0; break;
        case 3: currentCount = this.data.shift3_count || 0; break;
      }
      
      const available = maxSeats - currentCount;
      
      if (percentage >= 90) return `Almost Full (${available} left)`;
      if (percentage >= 70) return `High Occupancy (${available} available)`;
      if (percentage >= 40) return `Moderate (${available} seats open)`;
      return `Low Occupancy (${available} seats available)`;
    },
    
    getBestShift() {
      const shift1 = this.data.shift1_count || 0;
      const shift2 = this.data.shift2_count || 0;
      const shift3 = this.data.shift3_count || 0;
      
      if (shift2 >= shift1 && shift2 >= shift3) return 'Afternoon Shift (Shift 2)';
      if (shift1 >= shift3) return 'Morning Shift (Shift 1)';
      return 'Evening Shift (Shift 3)';
    },
    
    getAverageRevenue() {
      const totalStudents = this.data.total_students || 0;
      return totalStudents > 0 ? Math.round(this.totalRevenue / totalStudents) : 0;
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
  min-height: 100vh;
  /* background: linear-gradient(90deg, #7e00d0 0%, #007bff 100%); */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  padding-top: 3rem;
}

.header-section {
  text-align: center;
  margin-bottom: 2rem;
  color: white;
}

.dashboard-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.dashboard-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  font-weight: 300;
  margin: 0;
}

.quick-stats {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(255, 255, 255, 0.232);
  padding: 1rem 1.5rem;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  min-width: 120px;
}

.stat-number {
  font-size: 2rem;
  font-weight: 800;
  color: white;
  line-height: 1;
}

.stat-label {
  font-size: 0.9rem;
  color: rgba(255,255,255,0.8);
  margin-top: 4px;
  text-align: center;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-card {
  background: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  border: 2px solid transparent;
  animation: slideUp 0.6s ease-out forwards;
  opacity: 0;
}

.dashboard-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.15);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f3f4f6;
}

.card-icon {
  font-size: 2.5rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  background: linear-gradient(45deg, #667eea, #764ba2);
}

.shift-icon {
  background: linear-gradient(45deg, #4f46e5, #7c3aed);

}

.svg{
  width: 50px;
  height: 50px;
}




.students-icon {
  background: linear-gradient(45deg, #059669, #0d9488);
}

.revenue-icon {
  background: linear-gradient(45deg, #dc2626, #ea580c);
}

.collection-icon {
  background: linear-gradient(45deg, #16a34a, #15803d);
}

.card-header h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.shift-time {
  font-size: 0.9rem;
  color: #6b7280;
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 6px;
  margin-left: auto;
}

.occupancy-display {
  text-align: center;
  margin-bottom: 20px;
}

.occupancy-numbers {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
  margin-bottom: 8px;
}

.current {
  font-size: 3rem;
  font-weight: 800;
  color: #1f2937;
}

.separator {
  font-size: 2rem;
  color: #9ca3af;
  font-weight: 300;
}

.total {
  font-size: 2rem;
  color: #6b7280;
  font-weight: 600;
}

.occupancy-percentage {
  font-size: 1rem;
  color: #4f46e5;
  font-weight: 600;
}

.progress-container {
  margin-bottom: 16px;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.8s ease-out;
}

.shift1 { background: linear-gradient(90deg, #3b82f6, #1d4ed8); }
.shift2 { background: linear-gradient(90deg, #8b5cf6, #7c3aed); }
.shift3 { background: linear-gradient(90deg, #06b6d4, #0891b2); }
.collection-fill { background: linear-gradient(90deg, #10b981, #059669); }

.availability-status {
  text-align: center;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
}

.status-full {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
}

.status-high {
  background: #fef3c7;
  color: #d97706;
  border: 1px solid #fde68a;
}

.status-medium {
  background: #dbeafe;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.status-low {
  background: #dcfdf7;
  color: #059669;
  border: 1px solid #a7f3d0;
}

.metric-display {
  text-align: center;
  margin-bottom: 20px;
}

.main-number {
  font-size: 3rem;
  font-weight: 800;
  color: #1f2937;
  line-height: 1;
}

.revenue-amount {
  color: #dc2626;
}

.collection-amount {
  color: #059669;
}

.metric-subtitle {
  font-size: 1rem;
  color: #6b7280;
  margin-top: 8px;
}

.students-breakdown {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-direction: row;
}

.breakdown-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  background: #f9fafb;
  border-radius: 8px;
  width: fit-content;
}

.breakdown-label {
  font-size: 0.8rem;
  color: #6b7280;
  margin-bottom: 4px;
}

.breakdown-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #1f2937;
}

.revenue-details,
.collection-progress {
  margin-top: 16px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.detail-label {
  color: #6b7280;
  font-size: 0.9rem;
}

.detail-value {
  font-weight: 600;
  color: #1f2937;
}

.pending-amount {
  text-align: center;
  margin-top: 8px;
  font-size: 0.9rem;
  color: #dc2626;
  font-weight: 600;
}

.insights-section {
  max-width: 1200px;
  margin: 3rem auto 2rem auto;
  color: white;
}

.insights-header {
  text-align: center;
  margin-bottom: 2rem;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
}

.insights-section h3 {
  text-align: center;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 2rem;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-left: 1rem;
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.insight-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(255,255,255,0.2);
  padding: 20px;
  border-radius: 16px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.insight-card:hover {
  background: rgba(255,255,255,0.3);
  transform: translateY(-2px);
}

.insight-icon {
  font-size: 2rem;
  width: 50px;
  text-align: center;
}

.insight-content h4 {
  margin: 0 0 4px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #fbbf24;
}

.insight-content p {
  margin: 0;
  font-size: 0.9rem;
  opacity: 1;
  line-height: 1.4;
}

/* Animations */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dashboard-card:nth-child(1) { animation-delay: 0.1s; }
.dashboard-card:nth-child(2) { animation-delay: 0.2s; }
.dashboard-card:nth-child(3) { animation-delay: 0.3s; }
.dashboard-card:nth-child(4) { animation-delay: 0.4s; }
.dashboard-card:nth-child(5) { animation-delay: 0.5s; }
.dashboard-card:nth-child(6) { animation-delay: 0.6s; }

/* Responsive Design */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
    padding-top:3.5rem;
  }
  
  .dashboard-title {
    font-size: 2rem;
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .quick-stats {
    gap: 1rem;
  }
  
  .stat-item {
    min-width: 30vw;
    padding: 0.8rem 1rem;
  }
  
  .stat-number {
    font-size: 1.5rem;
  }
  
  .card-header {
    flex-direction: row;
    text-align: center;
    gap: 8px;
    /* justify-content: space-between; */
  }
  
  .card-icon {
    width: 50px;
    height: 50px;
    font-size: 2rem;
  }
  .svg{
  width: 40px;
  height: 40px;
}
  .shift-time {
    margin-left: auto;
  }
  
  .students-breakdown {
    flex-direction: row;
    gap: 8px;
  }
  
  .insights-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .current {
    font-size: 2.5rem;
  }
  
  .main-number {
    font-size: 2.5rem;
  }
  
  .dashboard-card {
    padding: 20px 16px;
  }
}
</style>
