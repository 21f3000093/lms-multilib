<template>
  <div class="student-form">
    <form @submit.prevent="submitForm" class="form-box">
      <h2>{{ isEdit ? 'Update Student' : 'Add Student' }}</h2>

      <input v-model="student.name" placeholder="Name" required @blur="onNameBlur" />
      <input v-model="student.contact" placeholder="Contact (10 digits)" required maxlength="10" @input="onContactInput" @blur="onContactBlur" />
      <div v-if="contactError" style="color: red; font-size: 0.95rem;">{{ contactError }}</div>

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
        <button type="submit" :disabled="loading">
            {{ loading ? 'Please wait...' : (isEdit ? 'Update' : 'Submit') }}
        </button>
        <button type="button" @click="$emit('close')">Cancel</button>
      </div>
    </form>

    <!-- Welcome Message Modal - Using your existing ConfirmationModal -->
    <ConfirmationModal
      :show="showWelcomeModal"
      title="Student Registered Successfully! 🎉"
      :message="welcomeModalMessage"
      @whatsapp="sendWelcomeWhatsApp"
      @sms="sendWelcomeSMS"
      @cancel="closeWelcomeModal"
    />
  </div>
</template>

<script>

/* eslint-disable */
import API from '../api';
import { useToast } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';
import ConfirmationModal from './ConfirmationModal.vue';

export default {
  props: {
    existingStudent: Object
  },

  components: {
    ConfirmationModal
  },

  setup() {
    const toast = useToast();
    
    const showSuccess = (message, options = {}) => {
      toast.success(message, {
        position: 'top',
        timeout: 3000,
        closeOnClick: true,
        pauseOnFocusLoss: true,
        pauseOnHover: true,
        draggable: true,
        draggablePercent: 0.6,
        showCloseButtonOnHover: false,
        hideProgressBar: true,
        closeButton: "button",
        icon: true,
        rtl: false,
        style: {
          backgroundColor: '#8725d3',
          color: '#fff',
          borderRadius: '8px'
        },       
        ...options
      });
    };
    
    const showError = (message) => {
      toast.error(message);
    };
    
    return {
      showSuccess,
      showError
    };
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
      availableSeats: [],
      loading: false,
      contactError: '',
      // Welcome modal data
      showWelcomeModal: false,
      newStudentData: null
    };
  },

  computed: {
    isEdit() {
      return !!this.existingStudent;
    },

    isContactValid() {
      return /^\d{10}$/.test(this.student.contact);
    },

    welcomeModalMessage() {
      if (!this.newStudentData) return '';
      return `Send welcome message to ${this.newStudentData.name.toUpperCase()}?`;
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

    onContactInput(event) {
      this.student.contact = this.student.contact.replace(/\D/g, '');
      if (!this.isContactValid && this.student.contact.length > 0) {
        this.contactError = 'Contact number must be exactly 10 digits';
      } else {
        this.contactError = '';
      }
    },

    capitalizeName(name) {
      return name.replace(/\b\w/g, l => l.toUpperCase()).replace(/\s+/g, ' ').trim();
    },

    onNameBlur() {
      this.student.name = this.student.name.trim().replace(/\s+/g, ' ');
    },

    onContactBlur() {
      this.student.contact = this.student.contact.replace(/\s+/g, '');
    },

    async submitForm() {
      if (this.loading) return;

      if (!this.isContactValid) {
        this.contactError = 'Contact number must be exactly 10 digits';
        return;
      }

      this.student.name = this.capitalizeName(this.student.name);
      this.loading = true;

      try {
        if (this.isEdit) {
          await API.put(`/students/${this.student.id}`, this.student);
          this.showSuccess('Student updated successfully!');
        } else {
          // Create new student
          const response = await API.post('/students/', this.student);
          this.newStudentData = response.data;
          
          this.showSuccess('Student registered successfully!');
          
          // Show welcome modal for new students only
          this.showWelcomeModal = true;
          
          // Reset form
          this.resetForm();
        }

        this.$emit('updated');
        
        // Only close immediately if it's an edit, for new students close after modal
        if (this.isEdit) {
          this.$emit('close');
        }
      } catch (err) {
        this.showError('Error: ' + (err.response?.data?.detail || err.message));
      } finally {
        this.loading = false;
      }
    },

    resetForm() {
      this.student = {
        name: '',
        contact: '',
        shift1: false,
        shift2: false,
        shift3: false,
        seat_id: '',
        custom_fees: null,
        paid: false,
        date_of_joining: null,
        library_id: localStorage.getItem('library_id')
      };
    },

    // Welcome message methods
    sendWelcomeWhatsApp() {
      const message = this.generateWelcomeMessage();
      const phone = "91" + this.newStudentData.contact.replace(/^0+/, "");
      const url = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
      window.open(url, "_blank");
      this.closeWelcomeModal();
      this.showSuccess('Welcome message sent via WhatsApp!');
    },

    sendWelcomeSMS() {
      const message = this.generateWelcomeMessage();
      const phone = this.newStudentData.contact.replace(/^(\+91|91)/, "");
      const url = `sms:${phone}?body=${encodeURIComponent(message)}`;
      window.open(url, "_blank");
      this.closeWelcomeModal();
      this.showSuccess('Welcome message sent via SMS!');
    },

    closeWelcomeModal() {
      this.showWelcomeModal = false;
      this.newStudentData = null;
      this.$emit('close'); // Close the form after welcome modal
    },

    generateWelcomeMessage() {
      const libraryName = localStorage.getItem('library_name') || "Your Library";
      const seatNumber = this.newStudentData.seat?.seat_number || 'Will be assigned soon';
      const joiningDate = this.formatDate(this.newStudentData.date_of_joining);
      const monthlyFees = this.newStudentData.custom_fees || 0;
      
      // Get selected shifts
      const shifts = [];
      if (this.newStudentData.shift1) shifts.push('Morning (Shift 1)');
      if (this.newStudentData.shift2) shifts.push('Afternoon (Shift 2)');
      if (this.newStudentData.shift3) shifts.push('Evening (Shift 3)');
      const shiftsText = shifts.join(', ');
      
      return `Welcome to ${libraryName}! \n\n` +
             `Dear ${this.newStudentData.name},\n` +
             `Thank you for joining our library!\n\n` +
             `Your Registration Details:\n` +
             `* Joining Date: ${joiningDate}\n` +
             `* Seat Number: ${seatNumber}\n` +
             `* Shifts: ${shiftsText}\n` +
             `* Monthly Fee: ₹${monthlyFees}\n\n` +
             `We're excited to have you with us!\n\n` +
             `Best regards,\n${libraryName}`;
    },

    formatDate(dateString) {
      if (!dateString) return new Date().toLocaleDateString('en-GB');
      const date = new Date(dateString);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      return `${day}-${month}-${year}`;
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
  padding-top: 15vh;
}

.form-box {
  background-color: #ffffff4f;
  padding: 1.5rem;
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
  margin-bottom: 0rem;
  margin-top: 0%;
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
  .student-form {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  max-width: 80%;
  margin: auto;
  margin-top: 15vh;


}
  
  .form-box {
    padding: 1rem;
    gap: 1rem;
  }

  .form-box h2 {
    text-align: center;
    margin-bottom: 0rem;
    font-size: 1.6rem;
    color: #333;
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
