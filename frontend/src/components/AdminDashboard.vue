<template>
  <main class="admin-dashboard">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="section-shell hero">
      <div>
        <p class="kicker">Admin Workspace</p>
        <h1>
          Library
          <span class="gradient-text">Performance Dashboard</span>
        </h1>
        <p class="hero-subtitle">Track occupancy, revenue, and collection health across all shifts in one view.</p>
      </div>
    </section>

    <section class="section-shell quick-stats">
      <article class="glass-card stat-card">
        <p class="stat-label">Total Students</p>
        <p class="stat-value">{{ data.total_students || 0 }}</p>
      </article>
      <article class="glass-card stat-card">
        <p class="stat-label">Overall Occupancy</p>
        <p class="stat-value">{{ overallOccupancy }}%</p>
      </article>
      <article class="glass-card stat-card">
        <p class="stat-label">Collected</p>
        <p class="stat-value">₹{{ formatNumber(monthlyCollected) }}</p>
      </article>
    </section>

    <section class="section-shell dashboard-grid">
      <article class="glass-card dashboard-card shift-card">
        <header class="card-header">
          <div class="card-icon shift-icon">
            <img src="../assets/svg/sunrise-svgrepo-com1.svg" class="svg" alt="Morning" loading="lazy">
          </div>
          <div>
            <h3>Shift 1</h3>
            <p>Morning</p>
          </div>
        </header>
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
            <div class="progress-fill shift1" :style="{ width: getShiftPercentage(1) + '%' }"></div>
          </div>
        </div>
        <div class="availability-status" :class="getStatusClass(1)">{{ getAvailabilityText(1) }}</div>
      </article>

      <article class="glass-card dashboard-card shift-card">
        <header class="card-header">
          <div class="card-icon shift-icon">
            <img src="../assets/svg/afternoonsun.svg" class="svg" alt="Afternoon" loading="lazy">
          </div>
          <div>
            <h3>Shift 2</h3>
            <p>Afternoon</p>
          </div>
        </header>
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
            <div class="progress-fill shift2" :style="{ width: getShiftPercentage(2) + '%' }"></div>
          </div>
        </div>
        <div class="availability-status" :class="getStatusClass(2)">{{ getAvailabilityText(2) }}</div>
      </article>

      <article class="glass-card dashboard-card shift-card">
        <header class="card-header">
          <div class="card-icon shift-icon">
            <img src="../assets/svg/night-svgrepo-com.svg" class="svg" alt="Evening" loading="lazy">
          </div>
          <div>
            <h3>Shift 3</h3>
            <p>Evening</p>
          </div>
        </header>
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
            <div class="progress-fill shift3" :style="{ width: getShiftPercentage(3) + '%' }"></div>
          </div>
        </div>
        <div class="availability-status" :class="getStatusClass(3)">{{ getAvailabilityText(3) }}</div>
      </article>

      <article class="glass-card dashboard-card">
        <header class="card-header">
          <div class="card-icon students-icon">
            <img src="../assets/svg/student-white.svg" class="svg" alt="Students" loading="lazy">
          </div>
          <div>
            <h3>Total Students</h3>
            <p>Active enrollments</p>
          </div>
        </header>
        <div class="metric-display">
          <div class="main-number">{{ data.total_students || 0 }}</div>
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
      </article>

      <article class="glass-card dashboard-card">
        <header class="card-header">
          <div class="card-icon revenue-icon">
            <img src="../assets/svg/money-dollar.svg" class="svg" alt="Revenue" loading="lazy">
          </div>
          <div>
            <h3>Monthly Revenue</h3>
            <p>Expected this month</p>
          </div>
        </header>
        <div class="metric-display">
          <div class="main-number revenue-amount">₹{{ formatNumber(totalRevenue) }}</div>
        </div>
        <div class="revenue-details">
          <div class="detail-row">
            <span class="detail-label">Per Student Avg</span>
            <span class="detail-value">₹{{ getAverageRevenue() }}</span>
          </div>
        </div>
      </article>

      <article class="glass-card dashboard-card">
        <header class="card-header">
          <div class="card-icon collection-icon">
            <img src="../assets/svg/money-recive-white.svg" class="svg" alt="Collected" loading="lazy">
          </div>
          <div>
            <h3>Collected</h3>
            <p>{{ collectionPercentage }}% of target</p>
          </div>
        </header>
        <div class="metric-display">
          <div class="main-number collection-amount">₹{{ formatNumber(monthlyCollected) }}</div>
        </div>
        <div class="collection-progress">
          <div class="progress-container">
            <div class="progress-bar collection-bar">
              <div class="progress-fill collection-fill" :style="{ width: Math.min(collectionPercentage, 100) + '%' }"></div>
            </div>
          </div>
          <div class="pending-amount">Pending: ₹{{ formatNumber(pendingAmount) }}</div>
        </div>
      </article>
    </section>

    <section class="section-shell insights-section glass-card">
      <header class="insights-header">
        <img src="../assets/svg/chart1.svg" class="svg" alt="Insights" loading="lazy">
        <h3>Quick Insights</h3>
      </header>
      <div class="insights-grid">
        <article class="insight-card">
          <div class="insight-icon">
            <img src="../assets/svg/star.svg" class="svg" alt="Best shift" loading="lazy">
          </div>
          <div>
            <h4>Best Performing Shift</h4>
            <p>{{ getBestShift() }}</p>
          </div>
        </article>
        <article class="insight-card">
          <div class="insight-icon">
            <img src="../assets/svg/chart-2.svg" class="svg" alt="Occupancy" loading="lazy">
          </div>
          <div>
            <h4>Occupancy Rate</h4>
            <p>{{ overallOccupancy }}% average across all shifts</p>
          </div>
        </article>
        <article class="insight-card">
          <div class="insight-icon">
            <img src="../assets/svg/empty.svg" class="svg" alt="Available seats" loading="lazy">
          </div>
          <div>
            <h4>Available Seats</h4>
            <p>{{ availableSeats }} seats can be filled</p>
          </div>
        </article>
      </div>
    </section>
  </main>
</template>

<script>
import API from '../api'

export default {
  data() {
    return {
      data: {},
    }
  },

  computed: {
    totalRevenue() {
      return this.data.revenue || 0
    },

    monthlyCollected() {
      return this.data.monthly_collected || 0
    },

    collectionPercentage() {
      if (this.totalRevenue === 0) return 0
      return Math.round((this.monthlyCollected / this.totalRevenue) * 100)
    },

    pendingAmount() {
      return Math.max(0, this.totalRevenue - this.monthlyCollected)
    },

    overallOccupancy() {
      const totalOccupied = (this.data.shift1_count || 0) +
                           (this.data.shift2_count || 0) +
                           (this.data.shift3_count || 0)
      const totalCapacity = (this.data.max_seats || 0) * 3
      return totalCapacity > 0 ? Math.round((totalOccupied / totalCapacity) * 100) : 0
    },

    availableSeats() {
      const totalCapacity = (this.data.max_seats || 0) * 3
      const totalOccupied = (this.data.shift1_count || 0) +
                           (this.data.shift2_count || 0) +
                           (this.data.shift3_count || 0)
      return totalCapacity - totalOccupied
    }
  },

  methods: {
    formatNumber(num) {
      return num.toLocaleString('en-IN')
    },

    getShiftPercentage(shiftNumber) {
      const maxSeats = this.data.max_seats || 0
      let currentCount = 0

      switch(shiftNumber) {
        case 1: currentCount = this.data.shift1_count || 0; break
        case 2: currentCount = this.data.shift2_count || 0; break
        case 3: currentCount = this.data.shift3_count || 0; break
      }

      return maxSeats > 0 ? Math.round((currentCount / maxSeats) * 100) : 0
    },

    getStatusClass(shiftNumber) {
      const percentage = this.getShiftPercentage(shiftNumber)
      if (percentage >= 90) return 'status-full'
      if (percentage >= 70) return 'status-high'
      if (percentage >= 40) return 'status-medium'
      return 'status-low'
    },

    getAvailabilityText(shiftNumber) {
      const percentage = this.getShiftPercentage(shiftNumber)
      const maxSeats = this.data.max_seats || 0
      let currentCount = 0

      switch(shiftNumber) {
        case 1: currentCount = this.data.shift1_count || 0; break
        case 2: currentCount = this.data.shift2_count || 0; break
        case 3: currentCount = this.data.shift3_count || 0; break
      }

      const available = maxSeats - currentCount

      if (percentage >= 90) return `Almost Full (${available} left)`
      if (percentage >= 70) return `High Occupancy (${available} available)`
      if (percentage >= 40) return `Moderate (${available} seats open)`
      return `Low Occupancy (${available} seats available)`
    },

    getBestShift() {
      const shift1 = this.data.shift1_count || 0
      const shift2 = this.data.shift2_count || 0
      const shift3 = this.data.shift3_count || 0

      if (shift2 >= shift1 && shift2 >= shift3) return 'Afternoon Shift (Shift 2)'
      if (shift1 >= shift3) return 'Morning Shift (Shift 1)'
      return 'Evening Shift (Shift 3)'
    },

    getAverageRevenue() {
      const totalStudents = this.data.total_students || 0
      return totalStudents > 0 ? Math.round(this.totalRevenue / totalStudents) : 0
    }
  },

  async created() {
    try {
      const res = await API.get('/dashboard/')
      this.data = res.data
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  --surface: rgba(148, 163, 184, 0.03);
  --surface-border: rgba(255, 255, 255, 0.03);
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;

  position: relative;
  min-height: 100vh;
  padding: 2rem 0 4rem 2.8rem;
  /* margin-bottom: 2rem; */
  color: var(--text-primary);
  overflow: hidden;
  isolation: isolate;
}

.mesh-layer {
  position: absolute;
  inset: 0;
  z-index: -1;
  background:
    radial-gradient(45rem 24rem at 10% 15%, rgba(34, 211, 238, 0.14), transparent 70%),
    radial-gradient(40rem 24rem at 86% 8%, rgba(59, 130, 246, 0.14), transparent 68%),
    radial-gradient(36rem 22rem at 65% 88%, rgba(14, 165, 233, 0.11), transparent 70%),
    linear-gradient(180deg, #0f172a 0%, #0b1222 100%);
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
  border: 1px solid rgba(148, 163, 184, 0.25);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #cbd5e1;
  background: rgba(148, 163, 184, 0.07);
}

.gradient-text {
  background: linear-gradient(90deg, #22d3ee, #3b82f6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-subtitle {
  margin: 0.75rem 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.glass-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.quick-stats {
  margin-top: 1.2rem;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.7rem;
}

.stat-card {
  border-radius: 14px;
  padding: 0.85rem;
}

.stat-label {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.84rem;
}

.stat-value {
  margin: 0.45rem 0 0;
  font-size: 1.5rem;
  font-weight: 800;
}

.dashboard-grid {
  margin-top: 0.95rem;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
}

.dashboard-card {
  border-radius: 16px;
  padding: 1rem;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.62rem;
  margin-bottom: 0.7rem;
}

.card-header h3 {
  margin: 0;
  font-size: 1.08rem;
}

.card-header p {
  margin: 0.2rem 0 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.card-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: rgba(148, 163, 184, 0.14);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.shift-icon {
  background: rgba(59, 130, 246, 0.2);
}

.students-icon {
  background: rgba(16, 185, 129, 0.2);
}

.revenue-icon {
  background: rgba(239, 68, 68, 0.2);
}

.collection-icon {
  background: rgba(14, 165, 233, 0.2);
}

.svg {
  width: 36px;
  height: 36px;
}

.occupancy-display,
.metric-display {
  text-align: center;
  margin-bottom: 0.75rem;
}

.occupancy-numbers {
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 6px;
}

.current,
.main-number {
  font-size: 2.4rem;
  font-weight: 800;
}

.separator,
.total {
  color: var(--text-secondary);
}

.occupancy-percentage,
.pending-amount,
.metric-subtitle {
  margin-top: 0.35rem;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.revenue-amount {
  color: #fecaca;
}

.collection-amount {
  color: #a7f3d0;
}

.progress-container {
  margin-bottom: 0.7rem;
}

.progress-bar {
  width: 100%;
  height: 10px;
  background: rgba(148, 163, 184, 0.24);
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: width 0.8s ease-out;
}

.shift1 { background: linear-gradient(90deg, #3b82f6, #1d4ed8); }
.shift2 { background: linear-gradient(90deg, #8b5cf6, #7c3aed); }
.shift3 { background: linear-gradient(90deg, #06b6d4, #0891b2); }
.collection-fill { background: linear-gradient(90deg, #10b981, #059669); }

.availability-status {
  text-align: center;
  padding: 0.42rem 0.58rem;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 700;
}

.status-full {
  background: rgba(239, 68, 68, 0.18);
  color: #fecaca;
}

.status-high {
  background: rgba(245, 158, 11, 0.18);
  color: #fde68a;
}

.status-medium {
  background: rgba(59, 130, 246, 0.18);
  color: #bfdbfe;
}

.status-low {
  background: rgba(16, 185, 129, 0.18);
  color: #a7f3d0;
}

.students-breakdown {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.45rem;
}

.breakdown-item {
  border-radius: 10px;
  background: rgba(148, 163, 184, 0.12);
  padding: 0.5rem;
  text-align: center;
}

.breakdown-label {
  display: block;
  font-size: 0.72rem;
  color: var(--text-secondary);
}

.breakdown-value {
  display: block;
  margin-top: 0.2rem;
  font-weight: 700;
}

.revenue-details,
.collection-progress {
  margin-top: 0.6rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  gap: 0.6rem;
  font-size: 0.86rem;
}

.detail-label {
  color: var(--text-secondary);
}

.detail-value {
  font-weight: 700;
}

.insights-section {
  margin-top: 0.9rem;
  border-radius: 16px;
  padding: 1rem;
}

.insights-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.58rem;
  margin-bottom: 0.8rem;
}

.insights-header h3 {
  margin: 0;
  font-size: 1.3rem;
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.65rem;
}

.insight-card {
  border-radius: 12px;
  background: rgba(148, 163, 184, 0.12);
  padding: 0.65rem;
  display: flex;
  align-items: center;
  gap: 0.58rem;
}

.insight-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.45);
  display: grid;
  place-items: center;
}

.insight-content h4,
.insight-card h4 {
  margin: 0;
  font-size: 0.88rem;
}

.insight-card p {
  margin: 0.24rem 0 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
}

@keyframes mesh-drift {
  0% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  100% {
    transform: translate3d(-1.5%, 1.2%, 0) scale(1.04);
  }
}

@media (max-width: 1100px) {
  .dashboard-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .insights-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 767px) {
  .admin-dashboard {
    padding: 2rem 1rem 5rem 1rem;
    /* margin-bottom: 2rem; */
  }

  .section-shell {
    width: min(1240px, calc(100% - 1rem));
  }

  .quick-stats,
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .current,
  .main-number {
    font-size: 2rem;
  }

  .students-breakdown {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
