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

      <!-- <article class="glass-card dashboard-card">
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
      </article> -->

      <article class="glass-card dashboard-card">
        <header class="card-header">
          <div class="card-icon collection-icon">
            <img src="../assets/svg/money-recive-white.svg" class="svg" alt="Collected" loading="lazy">
          </div>
          <div>
            <h3>This Month Collected</h3>
            <p>Collection pipeline status</p>
          </div>
        </header>
        <div class="metric-display">
          <div class="main-number collection-amount">₹{{ formatNumber(monthlyCollected) }}</div>
          <div class="metric-subtitle">{{ collectionPercentage }}% of month target</div>
        </div>
        <div class="collection-progress">
          <div class="progress-container">
            <div class="progress-bar collection-bar">
              <div
                class="progress-fill"
                :class="collectionFillClass"
                :style="{ width: Math.min(collectionPercentage, 100) + '%' }"
              ></div>
            </div>
          </div>
          <div class="pace-caption">
            As of today: {{ duePacePercentage }}% due pace (₹{{ formatNumber(collectedTillToday) }} / ₹{{ formatNumber(dueTillToday) }})
          </div>
        </div>
        <div class="collection-details">
          <div class="detail-row">
            <span class="detail-label">Due this month</span>
            <span class="detail-value">₹{{ formatNumber(totalRevenue) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Collected</span>
            <span class="detail-value">₹{{ formatNumber(monthlyCollected) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Outstanding</span>
            <span class="detail-value">₹{{ formatNumber(pendingAmount) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Collection %</span>
            <span class="detail-value">{{ collectionPercentage }}%</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Last month collected</span>
            <span class="detail-value">₹{{ formatNumber(lastMonthCollected) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Pace (as of today)</span>
            <span class="pace-chip" :class="duePaceClass">{{ duePaceLabel }}</span>
          </div>
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
              :class="{ active: selectedCollectionTrendMonths === 4 }"
              :disabled="isDashboardLoading"
              type="button"
              @click="setCollectionTrendMonths(4)"
            >
              Last 4
            </button>
            <button
              class="range-btn"
              :class="{ active: selectedCollectionTrendMonths === 6 }"
              :disabled="isDashboardLoading"
              type="button"
              @click="setCollectionTrendMonths(6)"
            >
              Last 6
            </button>
          </div>
        </header>

        <div
          v-if="trendBars.length"
          class="trend-chart"
          :style="{ gridTemplateColumns: `repeat(${trendBars.length}, minmax(0, 1fr))` }"
        >
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

      <article class="glass-card dashboard-card movement-card">
        <header class="card-header movement-header">
          <div class="movement-head-left">
            <div class="card-icon movement-icon">
              <img src="../assets/svg/chart1.svg" class="svg" alt="Movement" loading="lazy">
            </div>
            <div>
              <h3>Enrollment & Exits</h3>
              <p>Growth vs churn (last {{ selectedMovementTrendMonths }} months)</p>
            </div>
          </div>
          <div class="movement-head-actions" role="group" aria-label="Select movement trend range">
            <button
              class="range-btn movement-range-btn"
              :class="{ active: selectedMovementTrendMonths === 4 }"
              :disabled="isDashboardLoading"
              type="button"
              @click="setMovementTrendMonths(4)"
            >
              Last 4
            </button>
            <button
              class="range-btn movement-range-btn"
              :class="{ active: selectedMovementTrendMonths === 6 }"
              :disabled="isDashboardLoading"
              type="button"
              @click="setMovementTrendMonths(6)"
            >
              Last 6
            </button>
          </div>
        </header>

        <!-- <div class="movement-grid">
          <div class="movement-item">
            <span class="movement-label">New this month</span>
            <span class="movement-value">+{{ movementNewThisMonth }}</span>
          </div>
          <div class="movement-item">
            <span class="movement-label">Left this month</span>
            <span class="movement-value">-{{ movementLeftThisMonth }}</span>
          </div>
          <div class="movement-item">
            <span class="movement-label">Active total</span>
            <span class="movement-value">{{ movementActiveTotal }}</span>
          </div>
          <div class="movement-item">
            <span class="movement-label">Net movement</span>
            <span
              class="movement-value"
              :class="movementNetThisMonth >= 0 ? 'movement-positive' : 'movement-negative'"
            >
              {{ movementNetThisMonth >= 0 ? '+' : '' }}{{ movementNetThisMonth }}
            </span>
          </div>
        </div> -->

        <div v-if="movementChartData.length" class="movement-chart-wrap">
          <div class="movement-legend">
            <span><i class="dot dot-new"></i>New</span>
            <span><i class="dot dot-left"></i>Left</span>
            <span><i class="dot dot-net"></i>Net</span>
          </div>

          <svg
            class="movement-chart"
            viewBox="0 0 260 100"
            preserveAspectRatio="none"
            role="img"
            aria-label="Student movement combo trend chart"
          >
            <line
              class="movement-zero-line"
              x1="14"
              :y1="movementZeroLineY"
              x2="246"
              :y2="movementZeroLineY"
            ></line>

            <g v-for="item in movementChartData" :key="item.month">
              <rect
                class="movement-bar movement-bar-new"
                :x="item.newBarX"
                :y="item.newBarY"
                :width="item.barWidth"
                :height="item.newBarHeight"
                rx="2"
              ></rect>
              <rect
                class="movement-bar movement-bar-left"
                :x="item.leftBarX"
                :y="item.leftBarY"
                :width="item.barWidth"
                :height="item.leftBarHeight"
                rx="2"
              ></rect>
            </g>

            <polyline class="movement-net-line" :points="movementNetPolyline"></polyline>
            <circle
              v-for="item in movementChartData"
              :key="`${item.month}-net`"
              class="movement-net-point"
              :cx="item.xCenter"
              :cy="item.netY"
              r="2.2"
            ></circle>
          </svg>

          <div class="movement-month-chips" :style="{ gridTemplateColumns: movementMonthGridTemplate }">
            <button
              v-for="(item, index) in movementChartData"
              :key="`${item.month}-chip`"
              type="button"
              class="movement-chip"
              :class="{ active: movementActiveDetailIndex === index }"
              @focus="setActiveMovementIndex(index)"
              @click="setActiveMovementIndex(index)"
            >
              {{ item.label }}
            </button>
          </div>

          <div v-if="activeMovementDetail" class="movement-detail-panel">
            <p class="movement-detail-month">{{ activeMovementDetail.fullLabel }}</p>
            <div class="movement-detail-grid">
              <p><span>New</span><strong>+{{ activeMovementDetail.newCount }}</strong></p>
              <p><span>Left</span><strong>-{{ activeMovementDetail.leftCount }}</strong></p>
              <p><span>Net</span><strong>{{ activeMovementDetail.net >= 0 ? '+' : '' }}{{ activeMovementDetail.net }}</strong></p>
              <p><span>Join Share</span><strong>{{ activeMovementDetail.joinShare }}%</strong></p>
            </div>
          </div>
        </div>
        <p v-else class="metric-subtitle">No movement data for selected range.</p>
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
      selectedCollectionTrendMonths: 4,
      selectedMovementTrendMonths: 4,
      isDashboardLoading: false,
      activeTrendIndex: null,
      activeMovementIndex: null,
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
      return `Last ${this.selectedCollectionTrendMonths} months (paid only)`
    },

    collectionPercentage() {
      if (this.totalRevenue === 0) return 0
      return Math.round((this.monthlyCollected / this.totalRevenue) * 100)
    },

    dueTillToday() {
      return Number(this.data.due_till_today || 0)
    },

    collectedTillToday() {
      return Number(this.data.collected_till_today || 0)
    },

    duePacePercentage() {
      const backendValue = this.data.due_pace_percentage
      if (backendValue !== undefined && backendValue !== null) {
        return Number(backendValue)
      }
      if (this.dueTillToday <= 0) return 100
      return Math.round((this.collectedTillToday / this.dueTillToday) * 100)
    },

    duePaceStatusKey() {
      const rawStatus = String(this.data.due_pace_status || '').trim().toLowerCase()
      if (rawStatus === 'on-track' || rawStatus === 'watch' || rawStatus === 'at-risk') {
        return rawStatus
      }

      if (this.duePacePercentage >= 100) return 'on-track'
      if (this.duePacePercentage >= 85) return 'watch'
      return 'at-risk'
    },

    duePaceLabel() {
      if (this.duePaceStatusKey === 'on-track') return 'On track'
      if (this.duePaceStatusKey === 'watch') return 'Watch'
      return 'At risk'
    },

    duePaceClass() {
      if (this.duePaceStatusKey === 'on-track') return 'pace-on-track'
      if (this.duePaceStatusKey === 'watch') return 'pace-watch'
      return 'pace-at-risk'
    },

    collectionFillClass() {
      if (this.duePaceStatusKey === 'on-track') return 'collection-fill-on-track'
      if (this.duePaceStatusKey === 'watch') return 'collection-fill-watch'
      return 'collection-fill-at-risk'
    },

    pendingAmount() {
      return Math.max(0, this.totalRevenue - this.monthlyCollected)
    },

    movementTrend() {
      if (!Array.isArray(this.data.movement_trend)) return []
      return this.data.movement_trend.map((item) => ({
        month: item.month,
        newCount: Number(item.new_count || 0),
        leftCount: Number(item.left_count || 0),
        net: Number(item.net_movement || 0),
      }))
    },

    movementNewThisMonth() {
      return Number(this.data.new_this_month || 0)
    },

    movementLeftThisMonth() {
      return Number(this.data.left_this_month || 0)
    },

    movementActiveTotal() {
      if (this.data.active_total !== undefined && this.data.active_total !== null) {
        return Number(this.data.active_total)
      }
      return Number(this.data.total_students || 0)
    },

    movementNetThisMonth() {
      if (this.data.net_movement_this_month !== undefined && this.data.net_movement_this_month !== null) {
        return Number(this.data.net_movement_this_month)
      }
      return this.movementNewThisMonth - this.movementLeftThisMonth
    },

    movementChartData() {
      if (!this.movementTrend.length) return []

      const chartTop = 10
      const chartBottom = 88
      const chartLeft = 14
      const chartRight = 246
      const chartHeight = chartBottom - chartTop
      const slotWidth = (chartRight - chartLeft) / this.movementTrend.length
      const barWidth = Math.max(6, Math.min(12, slotWidth * 0.24))
      const barGap = 2

      const maxCount = Math.max(
        1,
        ...this.movementTrend.map((item) => Math.max(item.newCount, item.leftCount)),
      )
      const netMin = Math.min(0, ...this.movementTrend.map((item) => item.net))
      const netMax = Math.max(0, ...this.movementTrend.map((item) => item.net))
      const netRange = netMax - netMin || 1
      const zeroY = chartBottom - ((0 - netMin) / netRange) * chartHeight

      return this.movementTrend.map((item, index) => {
        const xCenter = chartLeft + (slotWidth * (index + 0.5))
        const newBarHeight = (item.newCount / maxCount) * chartHeight
        const leftBarHeight = (item.leftCount / maxCount) * chartHeight
        const netY = chartBottom - ((item.net - netMin) / netRange) * chartHeight
        const totalMove = item.newCount + item.leftCount
        const joinShare = totalMove > 0 ? Math.round((item.newCount / totalMove) * 100) : 0

        return {
          ...item,
          label: this.formatMonthShort(item.month),
          fullLabel: this.formatMonthFull(item.month),
          xCenter: Number(xCenter.toFixed(2)),
          barWidth: Number(barWidth.toFixed(2)),
          newBarX: Number((xCenter - barWidth - barGap).toFixed(2)),
          leftBarX: Number((xCenter + barGap).toFixed(2)),
          newBarY: Number((chartBottom - newBarHeight).toFixed(2)),
          leftBarY: Number((chartBottom - leftBarHeight).toFixed(2)),
          newBarHeight: Number(Math.max(1, newBarHeight).toFixed(2)),
          leftBarHeight: Number(Math.max(1, leftBarHeight).toFixed(2)),
          netY: Number(netY.toFixed(2)),
          zeroY: Number(zeroY.toFixed(2)),
          joinShare,
        }
      })
    },

    movementNetPolyline() {
      return this.movementChartData.map((item) => `${item.xCenter},${item.netY}`).join(' ')
    },

    movementZeroLineY() {
      if (!this.movementChartData.length) return 88
      return this.movementChartData[0].zeroY
    },

    movementMonthGridTemplate() {
      if (!this.movementChartData.length) return 'repeat(1, minmax(0, 1fr))'
      return `repeat(${this.movementChartData.length}, minmax(0, 1fr))`
    },

    movementActiveDetailIndex() {
      if (!this.movementChartData.length) return -1
      if (this.activeMovementIndex === null || this.activeMovementIndex === undefined) {
        return this.movementChartData.length - 1
      }
      return Math.max(0, Math.min(this.activeMovementIndex, this.movementChartData.length - 1))
    },

    activeMovementDetail() {
      if (this.movementActiveDetailIndex < 0) return null
      return this.movementChartData[this.movementActiveDetailIndex]
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

    setActiveMovementIndex(index) {
      this.activeMovementIndex = index
    },

    async fetchDashboard() {
      this.isDashboardLoading = true
      try {
        const res = await API.get('/dashboard/', {
          params: {
            collection_trend_months: this.selectedCollectionTrendMonths,
            movement_trend_months: this.selectedMovementTrendMonths,
          },
        })
        this.data = res.data || {}
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        this.isDashboardLoading = false
      }
    },

    async setCollectionTrendMonths(months) {
      if (this.selectedCollectionTrendMonths === months || this.isDashboardLoading) return
      this.selectedCollectionTrendMonths = months
      this.activeTrendIndex = null
      await this.fetchDashboard()
    },

    async setMovementTrendMonths(months) {
      if (this.selectedMovementTrendMonths === months || this.isDashboardLoading) return
      this.selectedMovementTrendMonths = months
      this.activeMovementIndex = null
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

  },

  async created() {
    await this.fetchDashboard()
  }
}
</script>

<style scoped>
.admin-dashboard {
  --surface: var(--theme-surface);
  --surface-border: var(--theme-surface-border);
  --text-primary: var(--theme-text-primary);
  --text-secondary: var(--theme-text-secondary);

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
  background: var(--theme-mesh-background);
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
  border: 1px solid var(--theme-border);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--theme-text-soft);
  background: var(--theme-surface-soft);
}

.gradient-text {
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
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
  /* text-align: left; */
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
  text-align: left;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.62rem;
  margin-bottom: 0.7rem;
  text-align: left;
}

.card-header > div {
  text-align: left;
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
  background: var(--theme-surface-soft-strong);
  border: 1px solid var(--theme-border-soft);
}

.shift-icon {
  /* background: var(--theme-brand-background); */
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
  /* background: rgba(59, 131, 246, 0.24); */
}

.students-icon {
  background: rgba(16, 185, 129, 0.2);
}

.revenue-icon {
  background: rgba(239, 68, 68, 0.2);
}

.collection-icon {
  /* background: rgba(14, 165, 233, 0.2); */
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
}

.movement-icon {
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
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
.metric-subtitle {
  margin-top: 0.35rem;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.collection-amount {
  color: var(--theme-success-text);
}

.progress-container {
  margin-bottom: 0.7rem;
}

.progress-bar {
  width: 100%;
  height: 10px;
  background: var(--theme-surface-muted);
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
.collection-fill-on-track { background: linear-gradient(90deg, #10b981, #059669); }
.collection-fill-watch { background: linear-gradient(90deg, #f59e0b, #d97706); }
.collection-fill-at-risk { background: linear-gradient(90deg, #ef4444, #dc2626); }

.availability-status {
  text-align: center;
  padding: 0.42rem 0.58rem;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 700;
}

.status-full {
  background: var(--theme-danger-soft);
  color: var(--theme-danger-text);
}

.status-high {
  background: var(--theme-warning-soft);
  color: var(--theme-warning-text);
}

.status-medium {
  background: var(--theme-info-soft);
  color: var(--theme-info-text);
}

.status-low {
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
}

.students-breakdown {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.45rem;
}

.breakdown-item {
  border-radius: 10px;
  background: var(--theme-surface-soft-strong);
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

.pace-caption {
  margin-top: 0.15rem;
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.pace-chip {
  border-radius: 999px;
  padding: 0.24rem 0.58rem;
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.01em;
}

.pace-on-track {
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
}

.pace-watch {
  background: var(--theme-warning-soft);
  color: var(--theme-warning-text);
}

.pace-at-risk {
  background: var(--theme-danger-soft);
  color: var(--theme-danger-text);
}

.movement-card {
  display: flex;
  flex-direction: column;
  grid-column: span 3;
}

.movement-header {
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.7rem;
}

.movement-head-left {
  display: flex;
  align-items: center;
  gap: 0.62rem;
}

.movement-head-actions {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  border: 1px solid var(--theme-success-border);
  background: var(--theme-panel);
  padding: 0.2rem;
}

.movement-range-btn.active {
  background: linear-gradient(90deg, rgba(34, 197, 94, 0.22), rgba(16, 185, 129, 0.28));
  color: var(--theme-success-text);
}

.movement-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.45rem;
}

.movement-item {
  border-radius: 10px;
  background: var(--theme-surface-soft-strong);
  padding: 0.5rem 0.56rem;
  display: flex;
  flex-direction: column;
  gap: 0.22rem;
}

.movement-label {
  color: var(--text-secondary);
  font-size: 0.74rem;
}

.movement-value {
  font-size: 1rem;
  font-weight: 800;
  color: var(--theme-text-primary);
}

.movement-positive {
  color: var(--theme-success-text);
}

.movement-negative {
  color: var(--theme-danger-text);
}

.movement-chart-wrap {
  margin-top: 0.58rem;
  border-radius: 12px;
  background: var(--theme-panel-soft);
  border: 1px solid var(--theme-border);
  padding: 0.5rem;
}

.movement-legend {
  display: flex;
  gap: 0.8rem;
  align-items: center;
  font-size: 0.72rem;
  color: var(--text-secondary);
}

.movement-legend span {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  display: inline-block;
}

.dot-new {
  background: #34d399;
}

.dot-left {
  background: #f87171;
}

.dot-net {
  background: var(--theme-brand-pill-text);
}

.movement-chart {
  width: 100%;
  /* height: 108px; */
  display: block;
  margin-top: 0.38rem;
}

.movement-zero-line {
  stroke: var(--theme-border-strong);
  stroke-width: 1;
  stroke-dasharray: 4 3;
}

.movement-bar {
  opacity: 0.95;
}

.movement-bar-new {
  fill: #34d399;
}

.movement-bar-left {
  fill: #f87171;
}

.movement-net-line {
  fill: none;
  stroke: var(--theme-brand-pill-text);
  stroke-width: 2.1;
  stroke-linejoin: round;
  stroke-linecap: round;
}

.movement-net-point {
  fill: var(--theme-brand-pill-text);
  stroke: rgba(12, 74, 110, 0.85);
  stroke-width: 1;
}

.movement-month-chips {
  margin-top: 0.3rem;
  display: grid;
  gap: 0.34rem;
}

.movement-chip {
  border: 1px solid var(--theme-border);
  border-radius: 8px;
  background: var(--theme-panel-soft);
  color: var(--theme-text-soft);
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.26rem 0.2rem;
  cursor: pointer;
}

.movement-chip.active {
  border-color: var(--theme-success-border);
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
}

.movement-detail-panel {
  margin-top: 0.42rem;
  border-radius: 10px;
  background: var(--theme-panel-soft);
  border: 1px solid var(--theme-border);
  padding: 0.42rem 0.5rem;
}

.movement-detail-month {
  margin: 0;
  color: var(--theme-text-info);
  font-size: 0.78rem;
  font-weight: 700;
}

.movement-detail-grid {
  margin-top: 0.26rem;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.2rem 0.48rem;
}

.movement-detail-grid p {
  margin: 0;
  display: flex;
  justify-content: space-between;
  gap: 0.35rem;
  font-size: 0.73rem;
  color: var(--theme-text-soft);
}

.movement-detail-grid strong {
  color: var(--theme-text-primary);
}

.trend-card {
  grid-column: span 2;
  display: flex;
  flex-direction: column;
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
  border: 1px solid var(--theme-border-strong);
  background: var(--theme-panel);
  padding: 0.2rem;
}

.range-btn {
  border: 0;
  background: transparent;
  color: var(--theme-text-soft);
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.28rem 0.55rem;
  border-radius: 999px;
  cursor: pointer;
}

.range-btn.active {
  background: linear-gradient(90deg, rgba(34, 211, 238, 0.22), rgba(59, 130, 246, 0.24));
  color: var(--theme-text-info);
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
  align-items: stretch;
  flex: 1;
  min-height: 150px;
}

.trend-column {
  position: relative;
  border-radius: 10px;
  background: var(--theme-surface-soft);
  padding: 0.45rem 0.45rem 0.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
}

.trend-bar-track {
  flex: 1;
  min-height: 112px;
  border-radius: 8px;
  background: var(--theme-panel-strong);
  border: 1px solid var(--theme-border);
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
  outline: 2px solid var(--theme-brand-border);
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
  border: 1px solid var(--theme-border-strong);
  background: var(--theme-panel-solid);
  box-shadow: 0 12px 22px rgba(2, 8, 23, 0.35);
  padding: 0.42rem 0.5rem;
  text-align: left;
}

.tooltip-month {
  margin: 0;
  font-size: 0.72rem;
  color: var(--theme-text-info);
}

.tooltip-value {
  margin: 0.2rem 0 0;
  font-size: 0.78rem;
  color: var(--theme-text-primary);
  font-weight: 700;
}

.tooltip-delta {
  margin: 0.18rem 0 0;
  font-size: 0.7rem;
  color: var(--theme-text-soft);
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
  color: var(--theme-text-info);
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
  background: var(--theme-surface-soft-strong);
  padding: 0.65rem;
  display: flex;
  align-items: center;
  gap: 0.58rem;
  text-align: left;
}

.insight-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
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
    grid-template-columns: repeat(3, minmax(0, 1fr));
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

  .movement-card {
    grid-column: span 1;
  }

  .movement-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .movement-detail-grid {
    grid-template-columns: 1fr 1fr;
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
