<template>
  <div class="seat-map-container">
    <h2>📍 Seat Map Viewer</h2>

    <div class="filters">
      <label><input type="checkbox" value="1" v-model="selectedShifts" /> Shift 1</label>
      <label><input type="checkbox" value="2" v-model="selectedShifts" /> Shift 2</label>
      <label><input type="checkbox" value="3" v-model="selectedShifts" /> Shift 3</label>


      <label id="empty-checkbox">
        <input type="checkbox" v-model="onlyEmpty" />
        Show Only Empty Seats
      </label>

      <button @click="fetchSeats">Apply Filters</button>
    </div>

    <div class="seat-grid">
      <div v-for="seat in seats" :key="seat.seat_number" class="seat-box clickable" @click="openSeatDetails(seat.seat_number)" >
        <div><strong>Seat {{ seat.seat_number }}</strong></div>
        <div class="shift-status">
          <span v-for="(status, index) in seat.shifts" :key="index">
            {{ status ? '✅' : '❌' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Seat Details Modal -->
    <SeatDetailsModal
      :show="showSeatModal"
      :seatData="selectedSeatData"
      @close="closeSeatModal" />

  </div>
</template>

<script>
// import axios from 'axios';
import API from '../api';
import SeatDetailsModal from './SeatDetailsModal.vue';
import { useToast } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';



export default {

  components: {
    SeatDetailsModal
  },
    
  data() {
    return {
      selectedShifts: [1,2,3],
      onlyEmpty: false,
      seats: [],
      showSeatModal: false,
      selectedSeatData: null,
      loadingSeatDetails: false
    };
  },
  mounted() {
    this.fetchSeats();
    },
    
  methods: {
    async fetchSeats() {
      if (this.selectedShifts.length === 0) {
        alert("Select at least one shift");
        return;
      }

      try {
        this.selectedShifts = this.selectedShifts.sort((a, b) => a - b); // Sort the selected shifts
        const response = await API.get("/seats/view", {
          params: {
            shifts: this.selectedShifts,
            only_empty: this.onlyEmpty,
            library_id: localStorage.getItem('library_id')
          }          
        });
        this.seats = [];
        this.seats = response.data;
      } catch (err) {
        console.error("Failed to fetch seats:", err);
      }
    },

    async openSeatDetails(seatNumber) {
      this.loadingSeatDetails = true;
      this.showSeatModal = true;
      this.selectedSeatData = null; // Show loading state

      try {
        const response = await API.get(`/seats/${seatNumber}/details`);
        this.selectedSeatData = response.data;
      } catch (err) {
        console.error("Failed to fetch seat details:", err);
        alert("Failed to load seat details");
        this.closeSeatModal();
      } finally {
        this.loadingSeatDetails = false;
      }
    },

    closeSeatModal() {
      this.showSeatModal = false;
      this.selectedSeatData = null;
    },


  }
};
</script>


<style scoped>
.seat-map-container {
  width: 95%;
  margin: 5vh auto;
  padding: 2rem;
  background: #f9fafc00;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  height: 80vh;
  overflow-y: auto;
  scrollbar-width: none;
  padding-top: 5vh;
}

.seat-map-container h2 {
  text-align: center;
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}

.filters label {
  font-weight: 500;
  color: #34495e;
}

.filters input[type="checkbox"] {
  margin-right: 6px;
}

.filters button {
  background-color: #3498db;
  color: white;
  padding: 8px 16px;
  font-weight: bold;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin:  auto;
  width: 50%;
}

.filters button:hover {
  background-color: #2980b9;
}

.seat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 1rem;
  justify-items: center;
}

.seat-box {
  width: 100px;
  height: 100px;
  background: #ecf0f1;
  border: 2px solid #bdc3c7;
  border-radius: 10px;
  text-align: center;
  padding: 10px;
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-shadow: 2px 2px 6px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
}

.seat-box:hover {
  transform: scale(1.05);
  border-color: #3498db;
}

.shift-status {
  margin-top: 8px;
  font-size: 1.3rem;
}

.seat-box.clickable {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.seat-box.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

@media (max-width: 768px) {
  .seat-map-container {
    padding: 1rem 0.5rem ;
    margin: auto;
    height: 90vh;
    overflow: auto;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    padding-top: 7vh;
    /* width: 95%; */
    

  }

  .filters {
    flex-direction: row;
    align-items: stretch;
    gap: 0.75rem;
  }

  .filters label{
    width: 30%;
    font-size: 1rem;
  }
  .filters #empty-checkbox{
    width: 100%;
    font-size: 1rem;
  }
  
  .filters button {
    width: 90%;
    font-size: 1rem;
  }

  .seat-grid {
    /* grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); */
    gap: 0.75rem;
  }

  .seat-box {
    width: 80%;
    height: auto;
    padding: 12px;
    font-size: 0.9rem;
    
  }

  .shift-status {
    font-size: 1.2rem;
    display: flex;
    justify-content: center;
    gap: 5px;
    flex-wrap: wrap;
  }
}

</style>
