<template>
  <div class="seat-map-container">
    <!-- Header -->
    <div class="header">
      <h2>Seat Map Viewer</h2>
      <p>View and manage seat assignments</p>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="shift-filters">
        <h3>Select Shifts</h3>
        <div class="checkboxes">
          <label :class="{ active: selectedShifts.includes('1') }">
            <input type="checkbox" value="1" v-model="selectedShifts" />
            🌅 Shift 1
          </label>
          <label :class="{ active: selectedShifts.includes('2') }">
            <input type="checkbox" value="2" v-model="selectedShifts" />
            ☀️ Shift 2
          </label>
          <label :class="{ active: selectedShifts.includes('3') }">
            <input type="checkbox" value="3" v-model="selectedShifts" />
            🌙 Shift 3
          </label>
        </div>
      </div>

      <label class="empty-seats" :class="{ active: onlyEmpty }">
        <input type="checkbox" v-model="onlyEmpty" />
        Show Only Empty Seats
      </label>

      <button @click="fetchSeats" :disabled="selectedShifts.length === 0" class="apply-btn">
        {{ loading ? '⏳ Loading...' : 'Apply Filters' }}
      </button>
    </div>

    <!-- Legend -->
    <div class="legend">
      <div class="legend-item">
        <span class="available">❌</span> Available
      </div>
      <div class="legend-item">
        <span class="occupied">✅</span> Occupied
      </div>
    </div>

    <!-- Seat Count -->
    <!-- <div class="seat-count">
      {{ filteredSeats.length }} seats
    </div> -->

    <!-- Loading -->
    <div v-if="loading" class="loading">
      <div class="spinner">⏳</div>
      <p>Loading seats...</p>
    </div>

    <!-- Seat Grid -->
    <div v-else-if="filteredSeats.length > 0" class="seat-grid">
      <div 
        v-for="seat in filteredSeats" 
        :key="seat.seat_number" 
        class="seat-card"
        @click="openSeatDetails(seat.seat_number)"
      >
        <div class="seat-number">{{ seat.seat_number }}</div>
        <div class="shifts">
          <span v-for="(status, index) in seat.shifts" :key="index">
            {{ status ? '✅' : '❌' }}
          </span>
        </div>
        <!-- <div class="click-hint">Details</div> -->
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <div class="empty-icon">🪑</div>
      <h3>No Seats Found</h3>
      <p v-if="selectedShifts.length === 0">Please select at least one shift</p>
      <p v-else-if="onlyEmpty">No empty seats available</p>
      <p v-else>No seats match your filters</p>
    </div>

    <!-- Seat Details Modal -->
    <SeatDetailsModal
      :show="showSeatModal"
      :seatData="selectedSeatData"
      :loading="loadingSeatDetails"
      @close="closeSeatModal" 
    />
  </div>
</template>

<script>
import API from '../api';
import SeatDetailsModal from './SeatDetailsModal.vue';
import { useToast } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';

export default {
  components: {
    SeatDetailsModal
  },

  setup() {
    const toast = useToast();
    
    const showSuccess = (message) => {
      toast.success(message, {
        position: 'top',
        timeout: 2000,
        style: {
          backgroundColor: '#667eea',
          color: '#fff',
          borderRadius: '8px'
        }
      });
    };
    
    const showError = (message) => {
      toast.error(message, {
        style: {
          backgroundColor: '#dc2626',
          color: '#fff',
          borderRadius: '8px'
        }
      });
    };
    
    return { showSuccess, showError };
  },
    
  data() {
    return {
      selectedShifts: ['1', '2', '3'],
      onlyEmpty: false,
      seats: [],
      showSeatModal: false,
      selectedSeatData: null,
      loadingSeatDetails: false,
      loading: false
    };
  },

  computed: {
    filteredSeats() {
      return this.seats || [];
    }
  },

  mounted() {
    this.fetchSeats();
  },
    
  methods: {
    async fetchSeats() {
      if (this.selectedShifts.length === 0) {
        this.showError("Please select at least one shift");
        return;
      }

      this.loading = true;
      try {
        const response = await API.get("/seats/view", {
          params: {
            shifts: this.selectedShifts.sort(),
            only_empty: this.onlyEmpty,
            library_id: localStorage.getItem('library_id')
          }          
        });
        this.seats = response.data;
        // this.showSuccess(`Loaded ${this.seats.length} seats`);
      } catch (err) {
        console.error("Failed to fetch seats:", err);
        this.showError("Failed to fetch seats");
        this.seats = [];
      } finally {
        this.loading = false;
      }
    },

    async openSeatDetails(seatNumber) {
      this.loadingSeatDetails = true;
      this.showSeatModal = true;
      this.selectedSeatData = null;

      try {
        const response = await API.get(`/seats/${seatNumber}/details`);
        this.selectedSeatData = response.data;
      } catch (err) {
        console.error("Failed to fetch seat details:", err);
        this.showError("Failed to load seat details");
        this.closeSeatModal();
      } finally {
        this.loadingSeatDetails = false;
      }
    },

    closeSeatModal() {
      this.showSeatModal = false;
      this.selectedSeatData = null;
    }
  }
};
</script>

<style scoped>
.seat-map-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  padding-top: 80px;
  font-family: "Inter", sans-serif;
}

.header {
  text-align: center;
  margin-bottom: 24px;
  color: white;
}

.header h2 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.header p {
  font-size: 1rem;
  opacity: 0.9;
  margin: 0;
}

.filters {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.shift-filters h3 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
}

.checkboxes {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
  justify-content: center;
}

.checkboxes label,
.empty-seats {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  background: white;
}

.checkboxes label:hover,
.empty-seats:hover {
  border-color: #667eea;
}

.checkboxes label.active,
.empty-seats.active {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.316);
}

.checkboxes input,
.empty-seats input {
  display: none;
}

.empty-seats {
  margin-bottom: 16px;
  width: 100%;
  box-sizing: border-box;
  justify-content: center;
}

.apply-btn {
  width: 100%;
  padding: 12px 20px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.apply-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.apply-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 12px;
  color: white;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.available,
.occupied {
  font-size: 1.2rem;
}

.seat-count {
  text-align: center;
  color: white;
  font-weight: 600;
  margin-bottom: 20px;
  background: rgba(255,255,255,0.2);
  display: inline-block;
  padding: 8px 16px;
  border-radius: 20px;
  margin-left: 50%;
  transform: translateX(-50%);
}

.loading {
  text-align: center;
  color: white;
  padding: 40px;
}

.spinner {
  font-size: 3rem;
  margin-bottom: 16px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.seat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
  max-width: 1000px;
  margin: 0 auto;
}

.seat-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.seat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.seat-number {
  font-size: 1.1rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 12px;
}

.shifts {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 1.2rem;
}

.click-hint {
  font-size: 0.8rem;
  color: #666;
  border-top: 1px solid #f0f0f0;
  padding-top: 8px;
}

.empty-state {
  text-align: center;
  color: white;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 1.5rem;
  margin-bottom: 8px;
  font-weight: 600;
}

.empty-state p {
  opacity: 0.9;
  font-size: 1rem;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .seat-map-container {
    padding: 12px;
    padding-top: 80px;
  }

  .header h2 {
    font-size: 1.8rem;
  }

  .filters {
    padding: 16px;
    margin-bottom: 16px;
  }

  .checkboxes {
    flex-direction: row;
    align-content: center;
  }

  .checkboxes label {
    width: fit-content;
    justify-content: center;
  }

  .seat-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 12px;
  }

  .seat-card {
    padding: 12px;
  }

  .legend {
    
    flex-direction: row;
    gap: 2rem;
    align-items: center;
  }
}

@media (max-width: 480px) {
  .seat-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 10px;
  }

  .seat-card {
    padding: 10px;
  }

  .seat-number {
    font-size: 1rem;
  }

  .shifts {
    font-size: 1.1rem;
  }
}
</style>
