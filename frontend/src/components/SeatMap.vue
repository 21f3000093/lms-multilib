<template>
  <div class="seat-map-container">
    <h2>📍 Seat Map Viewer</h2>

    <div class="filters">
      <label><input type="checkbox" value="1" v-model="selectedShifts" /> Shift 1</label>
      <label><input type="checkbox" value="2" v-model="selectedShifts" /> Shift 2</label>
      <label><input type="checkbox" value="3" v-model="selectedShifts" /> Shift 3</label>

      <label>
        <input type="checkbox" v-model="onlyEmpty" />
        Show only empty seats
      </label>

      <button @click="fetchSeats">Apply Filters</button>
    </div>

    <div class="seat-grid">
      <div v-for="seat in seats" :key="seat.seat_number" class="seat-box">
        <div><strong>Seat {{ seat.seat_number }}</strong></div>
        <div class="shift-status">
          <span v-for="(status, index) in seat.shifts" :key="index">
            {{ status ? '✅' : '❌' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// import axios from 'axios';
import API from '../api';
export default {
    
  data() {
    return {
      selectedShifts: [1,2,3],
      onlyEmpty: false,
      seats: []
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
        const response = await API.get("/seats/view", {
          params: {
            shifts: this.selectedShifts,
            only_empty: this.onlyEmpty,
            library_id: localStorage.getItem('library_id')
          }          
        });
        this.seats = response.data;
      } catch (err) {
        console.error("Failed to fetch seats:", err);
      }
    }
  }
};
</script>
<style scoped>
.seat-map-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  background: #f9fafc;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
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

@media (max-width: 768px) {
  .seat-map-container {
    padding: 1rem;
    margin: 1rem;
  }

  .filters {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .filters label,
  .filters button {
    width: 100%;
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
