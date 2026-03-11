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
        <p class="stat-label">This Month Collected</p>
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
            <h3>This Month Collected</h3>
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
        <div class="collection-details">
          <div class="detail-row">
            <span class="detail-label">Current month delta</span>
            <span class="detail-value">₹{{ formatNumber(Math.abs(monthOverMonthDelta)) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Month-over-month</span>
            <span class="trend-chip" :class="monthOverMonthDelta >= 0 ? 'trend-up' : 'trend-down'">
              {{ monthOverMonthDelta >= 0 ? '+' : '' }}{{ monthOverMonthPercent }}%
            </span>
          </div>
        </div>
      </article>

      <article class="glass-card dashboard-card">
        <header class="card-header">
          <div class="card-icon collection-icon">
            <img src="../assets/svg/money-recive-white.svg" class="svg" alt="Last month" loading="lazy">
          </div>
          <div>
            <h3>Last Month Collected</h3>
            <p>Previous month benchmark</p>
          </div>
        </header>
        <div class="metric-display">
          <div class="main-number last-month-amount">₹{{ formatNumber(lastMonthCollected) }}</div>
          <div class="metric-subtitle">Benchmark against current month</div>
        </div>
      </article>

      <article class="glass-card dashboard-card trend-card">
        <header class="card-header trend-header">
          <div class="trend-head-left">
            <div class="card-icon collection-icon">
              <img src="../assets/svg/chart-2.svg" class="svg" alt="Trend" loading="lazy">
            </div>
            <div>
              <h3>Collections Trend</h3>
              <p>{{ trendSubtitle }}</p>
            </div>
          </div>
          <div class="trend-head-actions" role="group" aria-label="Select trend range">
            <button
              class="range-btn"
              :class="{ active: selectedTrendMonths === 4 }"
              :disabled="isDashboardLoading"
              type="button"
              @click="setTrendMonths(4)"
            >
              Last 4
            </button>
            <button
              class="range-btn"
              :class="{ active: selectedTrendMonths === 6 }"
              :disabled="isDashboardLoading"
              type="button"
              @click="setTrendMonths(6)"
            >
              Last 6
            </button>
          </div>
        </header>

        <div v-if="trendBars.length" class="trend-chart">
          <article
            v-for="(point, index) in trendBars"
            :key="point.month"
            class="trend-column"
          >
            <button
              class="trend-bar-track trend-hitbox"
              type="button"
              @mouseenter="setActiveTrendIndex(index)"
              @mouseleave="clearActiveTrendIndex"
              @focus="setActiveTrendIndex(index)"
              @blur="clearActiveTrendIndex"
              @click="toggleActiveTrendIndex(index)"
              :aria-label="getTrendAriaLabel(point)"
            >
              <div class="trend-bar-fill" :style="{ height: point.height + '%' }"></div>
            </button>
            <div v-if="activeTrendIndex === index" class="trend-tooltip" role="tooltip">
              <p class="tooltip-month">{{ point.fullLabel }}</p>
              <p class="tooltip-value">₹{{ formatNumber(point.collected) }}</p>
              <p v-if="point.deltaText" class="tooltip-delta">{{ point.deltaText }}</p>
            </div>
            <p class="trend-month">{{ point.label }}</p>
            <p class="trend-value">₹{{ formatCompactNumber(point.collected) }}</p>
          </article>
        </div>
        <p v-else class="metric-subtitle">No paid collection data yet.</p>
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
      selectedTrendMonths: 4,
      isDashboardLoading: false,
      activeTrendIndex: null,
    }
  },

  computed: {
    totalRevenue() {
      return this.data.revenue || 0
    },

    monthlyCollected() {
      return this.data.monthly_collected || 0
    },

    lastMonthCollected() {
      return this.data.last_month_collected || 0
    },

    monthOverMonthDelta() {
      return this.monthlyCollected - this.lastMonthCollected
    },

    monthOverMonthPercent() {
      if (this.lastMonthCollected <= 0) {
        return this.monthlyCollected > 0 ? 100 : 0
      }
      return Math.round((this.monthOverMonthDelta / this.lastMonthCollected) * 100)
    },

    collectionTrend() {
      if (!Array.isArray(this.data.collection_trend)) return []
      return this.data.collection_trend.map((item) => ({
        month: item.month,
        collected: Number(item.collected || 0),
      }))
    },

    trendMaxValue() {
      const max = this.collectionTrend.reduce((acc, point) => Math.max(acc, point.collected), 0)
      return max > 0 ? max : 1
    },

    trendBars() {
      return this.collectionTrend.map((point, index) => {
        const previous = index > 0 ? this.collectionTrend[index - 1] : null
        const deltaValue = previous ? point.collected - previous.collected : 0
        const deltaPercent = previous && previous.collected > 0
          ? Math.round((deltaValue / previous.collected) * 100)
          : null

        if (point.collected <= 0) {
          return {
            ...point,
            label: this.formatMonthShort(point.month),
            fullLabel: this.formatMonthFull(point.month),
            height: 6,
            deltaText: previous ? `vs prev: ₹${this.formatNumber(Math.abs(deltaValue))}` : null,
          }
        }

        return {
          ...point,
          label: this.formatMonthShort(point.month),
          fullLabel: this.formatMonthFull(point.month),
          height: Math.max(18, Math.round((point.collected / this.trendMaxValue) * 100)),
          deltaText: previous
            ? `vs prev: ${deltaValue >= 0 ? '+' : '-'}₹${this.formatNumber(Math.abs(deltaValue))}${
              deltaPercent !== null ? ` (${deltaPercent >= 0 ? '+' : ''}${deltaPercent}%)` : ''
            }`
            : null,
        }
      })
    },

    trendSubtitle() {
      return `Last ${this.selectedTrendMonths} months (paid only)`
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
      return Number(num || 0).toLocaleString('en-IN')
    },

    formatCompactNumber(num) {
      return new Intl.NumberFormat('en-IN', {
        notation: 'compact',
        compactDisplay: 'short',
        maximumFractionDigits: 1,
      }).format(Number(num || 0))
    },

    formatMonthShort(monthString) {
      if (!monthString) return '--'
      const [year, month] = monthString.split('-')
      const date = new Date(Number(year), Number(month) - 1, 1)
      return date.toLocaleDateString('en-US', { month: 'short' })
    },

    formatMonthFull(monthString) {
      if (!monthString) return '--'
      const [year, month] = monthString.split('-')
      const date = new Date(Number(year), Number(month) - 1, 1)
      return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })
    },

    getTrendAriaLabel(point) {
      return `${point.fullLabel}, collected ${this.formatNumber(point.collected)} rupees`
    },

    setActiveTrendIndex(index) {
      this.activeTrendIndex = index
    },

    clearActiveTrendIndex() {
      this.activeTrendIndex = null
    },

    toggleActiveTrendIndex(index) {
      this.activeTrendIndex = this.activeTrendIndex === index ? null : index
    },

    async fetchDashboard() {
      this.isDashboardLoading = true
      try {
        const res = await API.get('/dashboard/', {
          params: { trend_months: this.selectedTrendMonths },
        })
        this.data = res.data || {}
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        this.isDashboardLoading = false
      }
    },

    async setTrendMonths(months) {
      if (this.selectedTrendMonths === months || this.isDashboardLoading) return
      this.selectedTrendMonths = months
      this.activeTrendIndex = null
      await this.fetchDashboard()
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
    await this.fetchDashboard()
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

.last-month-amount {
  color: #bfdbfe;
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

.collection-details {
  margin-top: 0.45rem;
  display: grid;
  gap: 0.3rem;
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

.trend-chip {
  border-radius: 999px;
  padding: 0.22rem 0.55rem;
  font-size: 0.8rem;
  font-weight: 800;
  letter-spacing: 0.01em;
}

.trend-up {
  background: rgba(16, 185, 129, 0.2);
  color: #a7f3d0;
}

.trend-down {
  background: rgba(239, 68, 68, 0.2);
  color: #fecaca;
}

.trend-card {
  grid-column: span 2;
}

.trend-header {
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.7rem;
}

.trend-head-left {
  display: flex;
  align-items: center;
  gap: 0.62rem;
}

.trend-head-actions {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.34);
  background: rgba(15, 23, 42, 0.55);
  padding: 0.2rem;
}

.range-btn {
  border: 0;
  background: transparent;
  color: #cbd5e1;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.28rem 0.55rem;
  border-radius: 999px;
  cursor: pointer;
}

.range-btn.active {
  background: linear-gradient(90deg, rgba(34, 211, 238, 0.25), rgba(59, 130, 246, 0.28));
  color: #e0f2fe;
}

.range-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.trend-chart {
  margin-top: 0.5rem;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.55rem;
}

.trend-column {
  position: relative;
  border-radius: 10px;
  background: rgba(148, 163, 184, 0.08);
  padding: 0.45rem 0.45rem 0.5rem;
  text-align: center;
}

.trend-bar-track {
  height: 92px;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.2);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  overflow: hidden;
}

.trend-hitbox {
  appearance: none;
  -webkit-appearance: none;
  width: 100%;
  padding: 0;
  cursor: pointer;
}

.trend-hitbox:focus-visible {
  outline: 2px solid rgba(56, 189, 248, 0.75);
  outline-offset: 2px;
}

.trend-bar-fill {
  width: 100%;
  border-radius: 6px 6px 0 0;
  background: linear-gradient(180deg, rgba(34, 211, 238, 0.95) 0%, rgba(59, 130, 246, 0.9) 100%);
  transition: height 0.6s ease;
}

.trend-tooltip {
  position: absolute;
  top: -0.55rem;
  left: 50%;
  transform: translate(-50%, -100%);
  min-width: 132px;
  z-index: 3;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.34);
  background: rgba(15, 23, 42, 0.92);
  box-shadow: 0 12px 22px rgba(2, 8, 23, 0.35);
  padding: 0.42rem 0.5rem;
  text-align: left;
}

.tooltip-month {
  margin: 0;
  font-size: 0.72rem;
  color: #bae6fd;
}

.tooltip-value {
  margin: 0.2rem 0 0;
  font-size: 0.78rem;
  color: #e2e8f0;
  font-weight: 700;
}

.tooltip-delta {
  margin: 0.18rem 0 0;
  font-size: 0.7rem;
  color: #cbd5e1;
}

.trend-month {
  margin: 0.4rem 0 0;
  font-size: 0.76rem;
  color: var(--text-secondary);
}

.trend-value {
  margin: 0.12rem 0 0;
  font-size: 0.8rem;
  font-weight: 700;
  color: #dbeafe;
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

  .trend-card {
    grid-column: span 2;
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

  .quick-stats {
    grid-template-columns: 1fr 1fr 1fr;
    justify-content: center;
    
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .trend-card {
    grid-column: span 1;
  }

  .trend-header {
    flex-direction: column;
    align-items: flex-start;
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
