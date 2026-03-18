<template>
  <main class="seat-map-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="section-shell hero">
      <div>
        <p class="kicker">Seat Operations</p>
        <h1>
          Live
          <span class="gradient-text">Seat Map</span>
        </h1>
        <p class="hero-subtitle">Filter shifts, inspect occupancy, and open seat-level details instantly.</p>
      </div>
    </section>

    <section class="section-shell glass-card filters-card">
      <div class="filter-head">
        <h2>Filters</h2>
      </div>

      <div class="filter-grid">
        <div class="shift-group">
          <p class="group-label">Select Shifts</p>
          <div class="shift-pills">
            <label class="shift-pill" :class="{ active: selectedShifts.includes('1') }">
              <input type="checkbox" value="1" v-model="selectedShifts" />
              Shift 1
            </label>
            <label class="shift-pill" :class="{ active: selectedShifts.includes('2') }">
              <input type="checkbox" value="2" v-model="selectedShifts" />
              Shift 2
            </label>
            <label class="shift-pill" :class="{ active: selectedShifts.includes('3') }">
              <input type="checkbox" value="3" v-model="selectedShifts" />
              Shift 3
            </label>
          </div>
        </div>

        <label class="empty-only" :class="{ active: onlyEmpty }">
          <input type="checkbox" v-model="onlyEmpty" />
          Show only empty seats
        </label>

        <button @click="fetchSeats" :disabled="selectedShifts.length === 0" class="btn btn-solid" type="button">
          {{ loading ? 'Loading...' : 'Apply Filters' }}
        </button>
      </div>
    </section>

    <section class="section-shell legend-row">
      <span class="legend-pill">
        <span class="dot dot-empty"></span>
        Available
      </span>
      <span class="legend-pill">
        <span class="dot dot-filled"></span>
        Occupied
      </span>
      <span class="legend-pill">
        {{ filteredSeats.length }} seats
      </span>
    </section>

    <section v-if="loading" class="section-shell glass-card loading-card">
      <div class="loader"></div>
      <p>Loading seats...</p>
    </section>

    <section v-else-if="filteredSeats.length > 0" class="section-shell seat-grid">
      <article
        v-for="seat in filteredSeats"
        :key="seat.seat_number"
        class="glass-card seat-card"
        @click="openSeatDetails(seat.seat_number)"
      >
        <div class="seat-top">
          <p class="seat-title">Seat {{ seat.seat_number }}</p>
          <!-- <p class="seat-subtitle">Tap for details</p> -->
        </div>

        <div class="seat-shifts">
          <span
            v-for="(status, index) in seat.shifts"
            :key="index"
            class="shift-status"
            :class="status ? 'is-filled' : 'is-empty'"
          >
            S{{ orderedSelectedShifts[index] || index + 1 }}
          </span>
        </div>
      </article>
    </section>

    <section v-else class="section-shell glass-card empty-state">
      <h3>No Seats Found</h3>
      <p v-if="selectedShifts.length === 0">Please select at least one shift.</p>
      <p v-else-if="onlyEmpty">No empty seats available for selected filters.</p>
      <p v-else>No seats match the selected filters.</p>
    </section>

    <SeatDetailsModal
      :show="showSeatModal"
      :seatData="selectedSeatData"
      :loading="loadingSeatDetails"
      @close="closeSeatModal"
    />
  </main>
</template>

<script>
import API from '../api'
import SeatDetailsModal from './SeatDetailsModal.vue'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'

export default {
  components: {
    SeatDetailsModal,
  },

  setup() {
    const toast = useToast()

    const showSuccess = (message) => {
      toast.success(message, {
        position: 'top',
        timeout: 2000,
        style: {
          backgroundColor: 'var(--theme-panel-solid)',
          color: 'var(--theme-text-strong)',
          border: '1px solid var(--theme-brand-border)',
          borderRadius: '8px',
          boxShadow: 'var(--theme-shadow-soft)',
        },
      })
    }

    const showError = (message) => {
      toast.error(message, {
        style: {
          backgroundColor: 'var(--theme-panel-solid)',
          color: 'var(--theme-text-strong)',
          border: '1px solid var(--theme-danger-border)',
          borderRadius: '8px',
          boxShadow: 'var(--theme-shadow-soft)',
        },
      })
    }

    return { showSuccess, showError }
  },

  data() {
    return {
      selectedShifts: ['1', '2', '3'],
      onlyEmpty: false,
      seats: [],
      showSeatModal: false,
      selectedSeatData: null,
      loadingSeatDetails: false,
      loading: false,
    }
  },

  computed: {
    orderedSelectedShifts() {
      return [...this.selectedShifts].sort((first, second) => Number(first) - Number(second))
    },
    filteredSeats() {
      return this.seats || []
    },
  },

  mounted() {
    this.fetchSeats()
  },

  methods: {
    async fetchSeats() {
      if (this.selectedShifts.length === 0) {
        this.showError('Please select at least one shift')
        return
      }

      this.loading = true
      try {
        const response = await API.get('/seats/view', {
          params: {
            shifts: this.orderedSelectedShifts,
            only_empty: this.onlyEmpty,
            library_id: localStorage.getItem('library_id'),
          },
        })
        this.seats = response.data
      } catch (err) {
        console.error('Failed to fetch seats:', err)
        this.showError('Failed to fetch seats')
        this.seats = []
      } finally {
        this.loading = false
      }
    },

    async openSeatDetails(seatNumber) {
      this.loadingSeatDetails = true
      this.showSeatModal = true
      this.selectedSeatData = null

      try {
        const response = await API.get(`/seats/${seatNumber}/details`)
        this.selectedSeatData = response.data
      } catch (err) {
        console.error('Failed to fetch seat details:', err)
        this.showError('Failed to load seat details')
        this.closeSeatModal()
      } finally {
        this.loadingSeatDetails = false
      }
    },

    closeSeatModal() {
      this.showSeatModal = false
      this.selectedSeatData = null
    },
  },
}
</script>

<style scoped>
.seat-map-page {
  --surface: var(--theme-surface);
  --surface-border: var(--theme-surface-border);
  --text-primary: var(--theme-text-primary);
  --text-secondary: var(--theme-text-secondary);

  position: relative;
  min-height: 100vh;
  padding: 2rem 1rem 2.8rem 3rem;
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
  /* max-width: 58ch; */
}

.glass-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.filters-card,
.loading-card,
.empty-state {
  margin-top: 0.9rem;
  border-radius: 16px;
  padding: 0.9rem;
}

.filter-head h2 {
  margin: 0;
  font-size: 1.05rem;
}

.filter-grid {
  margin-top: 0.65rem;
  display: grid;
  gap: 0.65rem;
}

.group-label {
  margin: 0;
  color: var(--theme-text-soft);
  font-size: 0.8rem;
  font-weight: 600;
}

.shift-pills {
  margin-top: 0.4rem;
  display: flex;
  /* flex-wrap: wrap; */
  gap: 0.45rem;
}

.shift-pill{
  border: 1px solid var(--theme-input-border);
  border-radius: 12px;
  background: var(--theme-input-bg);
  color: var(--theme-text-primary);
  min-height: 40px;
  padding: 0.35rem 0.65rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
  font-weight: 700;
  cursor: pointer;
  width: 30%;
}

.empty-only {
  border: 1px solid var(--theme-input-border);
  border-radius: 12px;
  background: var(--theme-input-bg);
  color: var(--theme-text-primary);
  min-height: 40px;
  padding: 0.35rem 0.65rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
  font-weight: 700;
  cursor: pointer;
}

.shift-pill.active,
.empty-only.active {
  border-color: var(--theme-brand-border);
  box-shadow: inset 0 0 0 1px var(--theme-brand-border);
  background-color: var(--theme-brand-soft);
}

.shift-pill input,
.empty-only input {
  display: none;
}

.btn {
  min-height: 42px;
  border-radius: 12px;
  border: 1px solid transparent;
  padding: 0.5rem 0.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-solid {
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
  box-shadow: var(--theme-shadow-elevated);
  color: var(--theme-brand-on);
}

.legend-row {
  margin-top: 0.75rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  justify-content: center;
}

.legend-pill {
  border-radius: 999px;
  border: 1px solid var(--theme-border);
  background: var(--theme-panel);
  color: var(--theme-text-info);
  padding: 0.3rem 0.58rem;
  font-size: 0.76rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot-empty {
  background: var(--theme-danger-solid);
}

.dot-filled {
  background: var(--theme-success-solid);
}

.loading-card,
.empty-state {
  text-align: center;
  display: grid;
  place-items: center;
  gap: 0.35rem;
}

.loader {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 3px solid var(--theme-border-strong);
  border-top-color: var(--theme-brand-a);
  animation: spin 1s linear infinite;
}

.seat-grid {
  margin-top: 0.9rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  gap: 0.6rem;
}

.seat-card {
  border-radius: 14px;
  padding: 0.72rem;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.seat-card:hover {
  transform: translateY(-2px);
  border-color: var(--theme-brand-border);
}

.seat-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 800;
}

.seat-subtitle {
  margin: 0.25rem 0 0;
  color: var(--text-secondary);
  font-size: 0.76rem;
}

.seat-shifts {
  margin-top: 0.58rem;
  display: flex;
  gap: 0.35rem;
  flex-wrap: wrap;
  justify-content: center;
}

.shift-status {
  border-radius: 999px;
  padding: 0.2rem 0.45rem;
  font-size: 0.72rem;
  font-weight: 700;
}

.shift-status.is-filled {
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
}

.shift-status.is-empty {
  background: var(--theme-danger-soft);
  color: var(--theme-danger-text);
}

@keyframes mesh-drift {
  0% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  100% {
    transform: translate3d(-1.5%, 1.2%, 0) scale(1.04);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1000px) {
  .seat-map-page {
    padding: 2rem 1rem 5rem 1rem;
  }
/* 
  .section-shell {
    width: min(1240px, calc(100% - 1rem));
  } */

  .seat-grid {
    grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
  }

  .shift-pill {
    padding: 0rem;
  }
}

@media (max-width: 500px) {
  .seat-grid {
    grid-template-columns: 1fr 1fr 1fr;
  }
  .seat-card {
    padding: 0.3rem;
  }

   .shift-status {
    font-size: 0.65rem;
    padding: 0.15rem 0.35rem;
   }

   .seat-title {
    font-size: 0.8rem;
   }
}
</style>
