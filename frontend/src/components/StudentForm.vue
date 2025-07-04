<template>
  <div class="student-form">
    <form @submit.prevent="submitForm" class="form-box">
      <h2>{{ isEdit ? 'Update Student' : 'Add Student' }}</h2>

      <input v-model="student.name" placeholder="Name" required />
      <input v-model="student.contact" placeholder="Contact" required />

      <div class="checkbox-group">
        <label><input type="checkbox" v-model="student.shift1" /> Shift 1</label>
        <label><input type="checkbox" v-model="student.shift2" /> Shift 2</label>
        <label><input type="checkbox" v-model="student.shift3" /> Shift 3</label>
      </div>

      <label>
        Seat:
        <select v-model="student.seat_id" required>
          <option disabled value="">Select a seat</option>
          <option v-for="seat in availableSeats" :key="seat.id" :value="seat.id">
            Seat {{ seat.seat_number }}
          </option>
        </select>
      </label>

      <label>
        Date of Joining:
        <input type="date" v-model="student.date_of_joining" />
      </label>

      <input v-model.number="student.custom_fees" type="number" placeholder="Monthly Fees (Rs)" />

      <div class="button-group">
        <button type="submit">{{ isEdit ? 'Update' : 'Submit' }}</button>
        <button type="button" @click="$emit('close')">Cancel</button>
      </div>
    </form>
  </div>
</template>

<script>
import API from '../api';

export default {
  props: {
    existingStudent: Object
  },
  data() {
    return {
      student: {
        name: '',
        contact: '',
        shift1: false,
        shift2: false,
        shift3: false,
        seat_id: '',
        custom_fees: null,
        paid: false,
        date_of_joining: null,
        library_id: localStorage.getItem('library_id'),

      },
      availableSeats: []
    };
  },
  computed: {
    isEdit() {
      return !!this.existingStudent;
    }
  },
  watch: {
    'student.shift1': 'fetchAvailableSeats',
    'student.shift2': 'fetchAvailableSeats',
    'student.shift3': 'fetchAvailableSeats'
  },
  mounted() {
    if (this.isEdit) {
      this.student = { ...this.existingStudent };
    }
    this.fetchAvailableSeats();
  },
  methods: {
    async fetchAvailableSeats() {
      try {
        const params = {
          shift1: this.student.shift1,
          shift2: this.student.shift2,
          shift3: this.student.shift3,
          student_id: this.isEdit ? this.student.id : null
        };

        const res = await API.get('/available-seats', { params });
        this.availableSeats = res.data;

        const seatIds = this.availableSeats.map(s => s.id);
        if (!seatIds.includes(this.student.seat_id)) {
          this.student.seat_id = '';
        }
      } catch (err) {
        console.error('Error fetching available seats:', err);
      }
    },
    async submitForm() {
      try {
        if (this.isEdit) {
          await API.put(`/students/${this.student.id}`, this.student);
          alert('Student updated!');
        } else {
          await API.post('/students/', this.student);
          alert('Student added!');
          this.student = {
            name: '',
            contact: '',
            shift1: false,
            shift2: false,
            shift3: false,
            seat_id: '',
            custom_fees: null,
            paid: false,
            date_of_joining: null
          };
        }

        this.$emit('updated');
        this.$emit('close');
      } catch (err) {
        alert('Error: ' + (err.response?.data?.detail || err.message));
      }
    }
  }
};
</script>

<style scoped>
.student-form {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 1rem;
}

.form-box {
  background-color: #89729900;
  padding: 2rem;
  border-radius: 12px;
  max-width: 450px;
  width: 100%;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-box h2 {
  text-align: center;
  margin-bottom: 1rem;
  font-size: 1.6rem;
  color: #333;
}

.form-box input,
.form-box select {
  padding: 0.7rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
  width: 100%;
  box-sizing: border-box;
}

.checkbox-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.checkbox-group label {
  font-size: 0.95rem;
}

.paid-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.button-group {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.button-group button {
  padding: 0.6rem 1.2rem;
  font-size: 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.button-group button[type="submit"] {
  background-color: #007bff;
  color: white;
}

.button-group button[type="submit"]:hover {
  background-color: #0056b3;
}

.button-group button[type="button"] {
  background-color: #eee;
}

.button-group button[type="button"]:hover {
  background-color: #ccc;
}

/* ✅ Responsive Design for tablets and mobile */
@media (max-width: 768px) {
  .form-box {
    padding: 1.2rem;
    gap: 1rem;
  }

  .checkbox-group {
    flex-direction:row;
    gap:1rem;
    align-items: center;
    justify-content: center;
  }

  .button-group {
    flex-direction: column;
  }

  .button-group button {
    width: 100%;
    text-align: center;
  }
}
</style>
