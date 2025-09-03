<template>
  <div class="student-form">
    <div class="form-header">
      <!-- <h2>{{ isEdit ? '✏️ Update Student' : '👨‍🎓 Add New Student' }}</h2>
      <p>{{ isEdit ? 'Modify student information' : 'Register a new student to your library' }}</p> -->
    </div>

    <form @submit.prevent="submitForm" class="form-container">
      <!-- Personal Information -->
      <div class="section">
        <h3>Student Details</h3>
        
        <div class="form-group">
          <!-- <label>Full Name</label> -->
          <div class="input-wrapper">
            <span class="icon">👤</span>
            <input 
              v-model="student.name" 
              placeholder="Enter student's full name" 
              required 
              @blur="onNameBlur"
            />
          </div>
        </div>

        <div class="form-group">
          <!-- <label>Contact Number</label> -->
          <div class="input-wrapper">
            <span class="icon">📱</span>
            <input 
              v-model="student.contact" 
              placeholder="10-digit mobile number" 
              required 
              maxlength="10" 
              @input="onContactInput" 
              @blur="onContactBlur"
              :class="{ error: contactError, success: student.contact.length === 10 && !contactError }"
            />
          </div>
          <div v-if="contactError" class="error-msg">{{ contactError }}</div>
        </div>
      </div>

      <!-- Shift Selection -->
      <div class="section">
        <h3>🕐 Shift Selection</h3>
        <!-- <p class="subtitle">Choose the shifts this student will attend</p> -->
        
        <div class="shifts">
          <label class="shift-card" :class="{ selected: student.shift1 }">
            <input type="checkbox" v-model="student.shift1" />
            <div class="shift-content">
              <span class="shift-icon">🌅</span>
              <div>
                <!-- <div class="shift-name">Morning Shift</div> -->
                <div class="shift-time">Shift 1</div>
              </div>
            </div>
          </label>

          <label class="shift-card" :class="{ selected: student.shift2 }">
            <input type="checkbox" v-model="student.shift2" />
            <div class="shift-content">
              <span class="shift-icon">☀️</span>
              <div>
                <!-- <div class="shift-name">Afternoon Shift</div> -->
                <div class="shift-time">Shift 2</div>
              </div>
            </div>
          </label>

          <label class="shift-card" :class="{ selected: student.shift3 }">
            <input type="checkbox" v-model="student.shift3" />
            <div class="shift-content">
              <span class="shift-icon">🌙</span>
              <div>
                <!-- <div class="shift-name">Evening Shift</div> -->
                <div class="shift-time">Shift 3</div>
              </div>
            </div>
          </label>
        </div>
      </div>

      <!-- Seat & Details -->
      <div class="section">
        <!-- <h3>🪑 Seat & Details</h3> -->
        
        <div class="form-group">
          <!-- <label>Seat Assignment</label> -->
          <div class="input-wrapper">
            <span class="icon">🪑</span>
            <select v-model="student.seat_id" required>
              <option disabled value="">Choose available seat</option>
              <option v-for="seat in availableSeats" :key="seat.id" :value="seat.id">
                Seat {{ seat.seat_number }}
              </option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <!-- <label>Date of Joining</label> -->
          <div class="input-wrapper">
            <span class="icon">📅</span>
            <input type="date" v-model="student.date_of_joining" />
          </div>
        </div>

        <div class="form-group">
          <!-- <label>Monthly Fees</label> -->
          <div class="input-wrapper">
            <span class="icon">💰</span>
            <input 
              v-model.number="student.custom_fees" 
              type="number" 
              placeholder="Enter monthly fees amount"
              min="0"
            />
            <span class="currency">₹</span>
          </div>
        </div>
      </div>

      <!-- Buttons -->
      <div class="buttons">
        <button type="button" @click="$emit('close')" class="btn-cancel">
          Cancel
        </button>
        <button type="submit" :disabled="loading || !formValid" class="btn-submit">
          {{ loading ? '⏳ Please wait...' : (isEdit ? 'Update' : 'Register') }}
        </button>
      </div>
    </form>

    <!-- Welcome Modal -->
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
    
    const showSuccess = (message) => {
      toast.success(message, {
        position: 'top',
        timeout: 3000,
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

    formValid() {
      return this.student.name.trim() && 
             this.isContactValid && 
             (this.student.shift1 || this.student.shift2 || this.student.shift3) &&
             this.student.seat_id;
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

    onContactInput() {
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
      if (this.loading || !this.formValid) return;

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
          this.$emit('close');
        } else {
          const response = await API.post('/students/', this.student);
          this.newStudentData = response.data;
          
          this.showSuccess('Student registered successfully!');
          this.showWelcomeModal = true;
          this.resetForm();
        }

        this.$emit('updated');
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

    sendWelcomeWhatsApp() {
      const message = this.generateWelcomeMessage();
      const phone = "91" + this.newStudentData.contact.replace(/^0+/, "");
      const url = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
      window.open(url, "_blank");
      this.closeWelcomeModal();
      this.showSuccess('📱 Welcome message sent via WhatsApp!');
    },

    sendWelcomeSMS() {
      const message = this.generateWelcomeMessage();
      const phone = this.newStudentData.contact.replace(/^(\+91|91)/, "");
      const url = `sms:${phone}?body=${encodeURIComponent(message)}`;
      window.open(url, "_blank");
      this.closeWelcomeModal();
      this.showSuccess('💬 Welcome message sent via SMS!');
    },

    closeWelcomeModal() {
      this.showWelcomeModal = false;
      this.newStudentData = null;
      this.$emit('close');
    },

    generateWelcomeMessage() {
      const libraryName = localStorage.getItem('library_name') || "Your Library";
      const seatNumber = this.newStudentData.seat?.seat_number || 'Will be assigned soon';
      const joiningDate = this.formatDate(this.newStudentData.date_of_joining);
      const monthlyFees = this.newStudentData.custom_fees || 0;
      
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
  height: 80vh;
  /* background: linear-gradient(90deg, #7e00d0 0%, #007bff 100%); */
  padding: 16px;
  padding-top: 3rem;
  font-family: "Inter", sans-serif;
  backdrop-filter: blur(4px);
  
}

.form-header {
  text-align: center;
  margin-bottom: 24px;
  color: white;
}

.form-header h2 {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.form-header p {
  font-size: 1rem;
  opacity: 0.9;
  margin: 0;
}

.form-container {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  max-width: 500px;
  margin: 0 auto;
}

.section {
  margin-bottom: 32px;
}

.section:last-child {
  margin-bottom: 24px;
}

.section h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 18px;
}

.subtitle {
  font-size: 0.9rem;
  color: #6b7280;
  margin-bottom: 16px;
  margin-top: 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  font-size: 0.95rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.icon {
  position: absolute;
  left: 12px;
  font-size: 1.1rem;
  color: #9ca3af;
  z-index: 1;
}

.currency {
  position: absolute;
  right: 12px;
  font-weight: 600;
  color: #6b7280;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 14px 12px 14px 40px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  outline: none;
  font-size: 16px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #667eea;
}

.form-group input.success {
  border-color: #10b981;
}

.form-group input.error {
  border-color: #dc2626;
}

.error-msg {
  color: #dc2626;
  font-size: 0.85rem;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.shifts {
  display: flex;
  flex-direction: row;
  gap: 12px;
  justify-content: center;
}

.shift-card {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.shift-card:hover {
  border-color: #667eea;
}

.shift-card.selected {
  border-color: #667eea;
  background: #d3b5f299;
}

.shift-card input[type="checkbox"] {
  display: none;
}

.shift-content {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.shift-icon {
  font-size: 1.5rem;
  min-width: 30px;
}

.shift-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 1rem;
}

.shift-time {
  font-size: 0.85rem;
  color: #000000;
}

.buttons {
  display: flex;
  gap: 12px;
  margin-top: 32px;
}

.btn-cancel,
.btn-submit {
  flex: 1;
  padding: 14px 20px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-submit {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Mobile Optimizations */
@media (max-width: 480px) {
  .student-form {
    padding: 12px;
    padding-top: 5rem;
    /* margin-top: 3rem; */
    /* height: fit-content; */
    height: 90vh;
    overflow-y: auto;
  }

  .form-container {
    padding: 20px;
    overflow-y: auto;
  }

  .form-header h2 {
    font-size: 1.6rem;
  }

  .shifts {
    gap: 10px;
    /* overflow-x: auto; */
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    /* grid-template-columns: repeat(auto-fit, minmax(45%, 1fr)); */

    /* place-items: center; */

  }

  .shift-card {
    padding: 10px;
  }

  .shift-icon {
    font-size: 1.3rem;
  }

  .buttons {
    flex-direction: row;
  }

  .form-group input,
  .form-group select {
    font-size: 16px; /* Prevent zoom on iOS */
  }
}
</style>
