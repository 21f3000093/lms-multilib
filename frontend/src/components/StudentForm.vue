<template>
  <main class="student-form-page" :class="{ embedded: isEdit }">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="form-shell glass-card">
      <header class="form-header">
        <p class="kicker">{{ isEdit ? 'Student Management' : 'Admissions Desk' }}</p>
        <h1>
          {{ isEdit ? 'Update Student' : 'Register New' }}
          <span class="gradient-text">{{ isEdit ? 'Profile' : 'Student' }}</span>
        </h1>
        <p class="subtitle">
          {{ isEdit ? 'Modify seat, shift, and fee details for this student.' : 'Capture student details and assign seat + shifts in one flow.' }}
        </p>
      </header>

      <form @submit.prevent="submitForm" class="form-grid" novalidate>
        <section class="form-section">
          <h2>Student Details</h2>

          <div class="field-grid">
            <label class="field-wrap" for="student-name">
              <span class="field-label">Full Name</span>
              <div class="input-wrap">
                <User class="input-icon" aria-hidden="true" />
                <input
                  id="student-name"
                  v-model="student.name"
                  placeholder="Enter student's full name"
                  required
                  @blur="onNameBlur"
                />
              </div>
            </label>

            <label class="field-wrap" for="student-contact">
              <span class="field-label">Contact Number</span>
              <div class="input-wrap" :class="{ error: contactError, success: student.contact.length === 10 && !contactError }">
                <Phone class="input-icon" aria-hidden="true" />
                <input
                  id="student-contact"
                  v-model="student.contact"
                  placeholder="10-digit mobile number"
                  required
                  maxlength="10"
                  @input="onContactInput"
                  @blur="onContactBlur"
                />
              </div>
              <p v-if="contactError" class="error-msg">{{ contactError }}</p>
            </label>
          </div>
        </section>

        <section class="form-section">
          <h2>Shift Selection</h2>

          <div class="shift-grid">
            <label class="shift-card" :class="{ selected: student.shift1 }">
              <input type="checkbox" v-model="student.shift1" />
              <div class="shift-content">
                <Sunrise class="shift-icon" aria-hidden="true" />
                <div>
                  <p class="shift-name">Shift 1</p>
                  <p class="shift-time">Morning</p>
                </div>
              </div>
            </label>

            <label class="shift-card" :class="{ selected: student.shift2 }">
              <input type="checkbox" v-model="student.shift2" />
              <div class="shift-content">
                <Sun class="shift-icon" aria-hidden="true" />
                <div>
                  <p class="shift-name">Shift 2</p>
                  <p class="shift-time">Afternoon</p>
                </div>
              </div>
            </label>

            <label class="shift-card" :class="{ selected: student.shift3 }">
              <input type="checkbox" v-model="student.shift3" />
              <div class="shift-content">
                <MoonStar class="shift-icon" aria-hidden="true" />
                <div>
                  <p class="shift-name">Shift 3</p>
                  <p class="shift-time">Evening</p>
                </div>
              </div>
            </label>
          </div>
        </section>

        <section class="form-section">
          <h2>Seat & Fees</h2>

          <div class="field-grid">
            <label class="field-wrap" for="seat-id">
              <span class="field-label">Seat Assignment</span>
              <div class="input-wrap">
                <Armchair class="input-icon" aria-hidden="true" />
                <select id="seat-id" v-model="student.seat_id" required>
                  <option disabled value="">Choose available seat</option>
                  <option v-for="seat in availableSeats" :key="seat.id" :value="seat.id">
                    Seat {{ seat.seat_number }}
                  </option>
                </select>
              </div>
            </label>

            <label class="field-wrap" for="date-joining">
              <span class="field-label">Date of Joining</span>
              <div class="input-wrap">
                <CalendarDays class="input-icon" aria-hidden="true" />
                <input id="date-joining" type="date" v-model="student.date_of_joining" required />
              </div>
            </label>

            <label class="field-wrap" for="custom-fees">
              <span class="field-label">Monthly Fees</span>
              <div class="input-wrap amount-wrap">
                <IndianRupee class="input-icon" aria-hidden="true" />
                <input
                  id="custom-fees"
                  v-model.number="student.custom_fees"
                  type="number"
                  placeholder="Enter monthly fees"
                  min="0"
                  required
                />
              </div>
            </label>
          </div>
        </section>

        <div class="button-row">
          <button type="button" @click="$emit('close')" class="btn btn-ghost">Cancel</button>
          <button type="submit" :disabled="loading || !formValid" class="btn btn-solid">
            <LoaderCircle v-if="loading" class="spinner" aria-hidden="true" />
            <span>{{ loading ? 'Please wait...' : (isEdit ? 'Update Student' : 'Register Student') }}</span>
          </button>
        </div>
      </form>
    </section>

    <ConfirmationModal
      :show="showWelcomeModal"
      title="Student Registered Successfully!"
      :message="welcomeModalMessage"
      @whatsapp="sendWelcomeWhatsApp"
      @sms="sendWelcomeSMS"
      @cancel="closeWelcomeModal"
    />
  </main>
</template>

<script>
import {
  Armchair,
  CalendarDays,
  IndianRupee,
  LoaderCircle,
  MoonStar,
  Phone,
  Sun,
  Sunrise,
  User,
} from 'lucide-vue-next'
import API from '../api'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'
import ConfirmationModal from './ConfirmationModal.vue'

export default {
  props: {
    existingStudent: Object,
  },

  components: {
    Armchair,
    CalendarDays,
    ConfirmationModal,
    IndianRupee,
    LoaderCircle,
    MoonStar,
    Phone,
    Sun,
    Sunrise,
    User,
  },

  setup() {
    const toast = useToast()

    const showSuccess = (message) => {
      toast.success(message, {
        position: 'top',
        timeout: 3000,
        style: {
          backgroundColor: '#0ea5e9',
          color: '#fff',
          borderRadius: '12px',
        },
      })
    }

    const showError = (message) => {
      toast.error(message, {
        style: {
          backgroundColor: '#dc2626',
          color: '#fff',
          borderRadius: '12px',
        },
      })
    }

    return { showSuccess, showError }
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
      newStudentData: null,
    }
  },

  computed: {
    isEdit() {
      return !!this.existingStudent
    },

    isContactValid() {
      return /^\d{10}$/.test(this.student.contact)
    },

    formValid() {
      return this.student.name.trim() &&
             this.isContactValid &&
             (this.student.shift1 || this.student.shift2 || this.student.shift3) &&
             this.student.seat_id
    },

    welcomeModalMessage() {
      if (!this.newStudentData) return ''
      return `Send welcome message to ${this.newStudentData.name.toUpperCase()}?`
    },
  },

  watch: {
    'student.shift1': 'fetchAvailableSeats',
    'student.shift2': 'fetchAvailableSeats',
    'student.shift3': 'fetchAvailableSeats',
  },

  mounted() {
    if (this.isEdit) {
      this.student = { ...this.existingStudent }
    }
    this.fetchAvailableSeats()
  },

  methods: {
    async fetchAvailableSeats() {
      try {
        const params = {
          shift1: this.student.shift1,
          shift2: this.student.shift2,
          shift3: this.student.shift3,
          student_id: this.isEdit ? this.student.id : null,
        }

        const res = await API.get('/available-seats', { params })
        this.availableSeats = res.data

        const seatIds = this.availableSeats.map((seat) => seat.id)
        if (!seatIds.includes(this.student.seat_id)) {
          this.student.seat_id = ''
        }
      } catch (err) {
        console.error('Error fetching available seats:', err)
      }
    },

    onContactInput() {
      this.student.contact = this.student.contact.replace(/\D/g, '')
      if (!this.isContactValid && this.student.contact.length > 0) {
        this.contactError = 'Contact number must be exactly 10 digits'
      } else {
        this.contactError = ''
      }
    },

    capitalizeName(name) {
      return name.replace(/\b\w/g, (letter) => letter.toUpperCase()).replace(/\s+/g, ' ').trim()
    },

    onNameBlur() {
      this.student.name = this.student.name.trim().replace(/\s+/g, ' ')
    },

    onContactBlur() {
      this.student.contact = this.student.contact.replace(/\s+/g, '')
    },

    async submitForm() {
      if (this.loading || !this.formValid) return

      if (!this.isContactValid) {
        this.contactError = 'Contact number must be exactly 10 digits'
        return
      }

      this.student.name = this.capitalizeName(this.student.name)
      this.loading = true

      try {
        if (this.isEdit) {
          await API.put(`/students/${this.student.id}`, this.student)
          this.showSuccess('Student updated successfully!')
          this.$emit('close')
        } else {
          const response = await API.post('/students/', this.student)
          this.newStudentData = response.data

          this.showSuccess('Student registered successfully!')
          this.resetForm()
        }

        this.$emit('updated')
      } catch (err) {
        this.showError('Error: ' + (err.response?.data?.detail || err.message))
      } finally {
        this.loading = false
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
        library_id: localStorage.getItem('library_id'),
      }
    },

    sendWelcomeWhatsApp() {
      const message = this.generateWelcomeMessage()
      const phone = '91' + this.newStudentData.contact.replace(/^0+/, '')
      const url = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`
      window.open(url, '_blank')
      this.closeWelcomeModal()
      this.showSuccess('Welcome message sent via WhatsApp!')
    },

    sendWelcomeSMS() {
      const message = this.generateWelcomeMessage()
      const phone = this.newStudentData.contact.replace(/^(\+91|91)/, '')
      const url = `sms:${phone}?body=${encodeURIComponent(message)}`
      window.open(url, '_blank')
      this.closeWelcomeModal()
      this.showSuccess('Welcome message sent via SMS!')
    },

    closeWelcomeModal() {
      this.showWelcomeModal = false
      this.newStudentData = null
      this.$emit('close')
    },

    generateWelcomeMessage() {
      const libraryName = localStorage.getItem('library_name') || 'Your Library'
      const seatNumber = this.newStudentData.seat?.seat_number || 'Will be assigned soon'
      const joiningDate = this.formatDate(this.newStudentData.date_of_joining)
      const monthlyFees = this.newStudentData.custom_fees || 0

      const shifts = []
      if (this.newStudentData.shift1) shifts.push('Morning (Shift 1)')
      if (this.newStudentData.shift2) shifts.push('Afternoon (Shift 2)')
      if (this.newStudentData.shift3) shifts.push('Evening (Shift 3)')
      const shiftsText = shifts.join(', ')

      return `Welcome to ${libraryName}! \n\n` +
             `Dear ${this.newStudentData.name},\n` +
             `Thank you for joining our library!\n\n` +
             `Your Registration Details:\n` +
             `* Joining Date: ${joiningDate}\n` +
             `* Seat Number: ${seatNumber}\n` +
             `* Shifts: ${shiftsText}\n` +
             `* Monthly Fee: ₹${monthlyFees}\n\n` +
             `We're excited to have you with us!\n\n` +
             `Best regards,\n${libraryName}`
    },

    formatDate(dateString) {
      if (!dateString) return new Date().toLocaleDateString('en-GB')
      const date = new Date(dateString)
      const day = String(date.getDate()).padStart(2, '0')
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const year = date.getFullYear()
      return `${day}-${month}-${year}`
    },
  },
}
</script>

<style scoped>
.student-form-page {
  --surface: rgba(148, 163, 184, 0.03);
  --surface-border: rgba(255, 255, 255, 0.03);
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;

  position: relative;
  min-height: 100vh;
  padding: 2rem 1rem 2.8rem;
  color: var(--text-primary);
  overflow: hidden;
  isolation: isolate;
}

.student-form-page.embedded {
  min-height: auto;
  padding: 0;
  overflow: visible;
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

.student-form-page.embedded .mesh-layer {
  display: none;
}

.glass-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.form-shell {
  width: min(900px, 90%);
  margin: 0 auto;
  border-radius: 18px;
  padding: 1.1rem;
}

.student-form-page.embedded .form-shell {
  width: 100%;
  margin: 0;
  border-radius: 16px;
  padding: 1rem;
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

.form-header h1 {
  margin: 0.82rem 0 0;
  font-size: clamp(1.5rem, 3.8vw, 2.3rem);
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.gradient-text {
  background: linear-gradient(90deg, #22d3ee, #3b82f6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.subtitle {
  margin: 0.7rem 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.form-grid {
  margin-top: 1rem;
  display: grid;
  gap: 0.8rem;
}

.form-section {
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 14px;
  padding: 0.82rem;
  background: rgba(15, 23, 42, 0.42);
}

.form-section h2 {
  margin: 0;
  font-size: 1.02rem;
}

.field-grid {
  margin-top: 0.7rem;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.68rem;
}

.field-wrap {
  display: grid;
  gap: 0.32rem;
}

.field-label {
  color: #cbd5e1;
  font-size: 0.8rem;
  font-weight: 600;
}

.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.72);
}

.input-wrap:focus-within {
  border-color: rgba(34, 211, 238, 0.62);
  box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.16);
}

.input-wrap.error {
  border-color: rgba(239, 68, 68, 0.6);
}

.input-wrap.success {
  border-color: rgba(16, 185, 129, 0.58);
}

.input-icon {
  width: 1rem;
  height: 1rem;
  margin-left: 0.75rem;
  color: #94a3b8;
  flex-shrink: 0;
}

.input-wrap input,
.input-wrap select {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: #f8fafc;
  font-size: 0.95rem;
  padding: 0.7rem 0.75rem;
  min-height: 44px;
}

.input-wrap select option {
  color: #0f172a;
}

.input-wrap input::placeholder {
  color: #94a3b8;
}

.input-wrap input[type='date'] {
  color-scheme: dark;
}

.input-wrap input[type='date']::-webkit-calendar-picker-indicator {
  filter: invert(1) brightness(1.35) saturate(0.25);
  opacity: 0.95;
  cursor: pointer;
}

.input-wrap input[type='date']::-webkit-calendar-picker-indicator:hover {
  opacity: 1;
}

.amount-wrap input {
  padding-right: 0.8rem;
}

.error-msg {
  margin: 0;
  color: #fca5a5;
  font-size: 0.78rem;
}

.shift-grid {
  margin-top: 0.7rem;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.6rem;
}

.shift-card {
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.5);
  cursor: pointer;
  transition: 0.2s ease;
}

.shift-card:hover {
  border-color: rgba(34, 211, 238, 0.5);
}

.shift-card.selected {
  border-color: rgba(34, 211, 238, 0.75);
  box-shadow: inset 0 0 0 1px rgba(34, 211, 238, 0.35);
  background-color: #00ffff1c;
}

.shift-card input[type='checkbox'] {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.shift-content {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.72rem;
}

.shift-icon {
  width: 1rem;
  height: 1rem;
  color: #67e8f9;
}

.shift-name,
.shift-time {
  margin: 0;
}

.shift-name {
  font-size: 0.86rem;
  font-weight: 700;
}

.shift-time {
  margin-top: 0.1rem;
  font-size: 0.75rem;
  color: #94a3b8;
}

.button-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.6rem;
}

.btn {
  min-height: 44px;
  border-radius: 12px;
  border: 1px solid transparent;
  padding: 0.56rem 0.8rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  font-weight: 700;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-solid {
  background: linear-gradient(90deg, #0ea5e9, #3b82f6);
  color: #fff;
  box-shadow: 0 14px 28px rgba(59, 130, 246, 0.28);
}

.btn-ghost {
  background: rgba(148, 163, 184, 0.08);
  border-color: rgba(148, 163, 184, 0.32);
  color: #e2e8f0;
}

.spinner {
  width: 0.95rem;
  height: 0.95rem;
  animation: spin 1s linear infinite;
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

@media (max-width: 900px) {
  .field-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 767px) {
  .student-form-page {
    padding-top: 2rem;
    padding-left: 0.9rem;
    padding-right: 0.9rem;
    padding-bottom: 5rem;
  }

  .form-shell,
  .student-form-page.embedded .form-shell {
    padding: 0.8rem;
    width: 90%;
  }

  .shift-grid {
    grid-template-columns: 1fr;
  }

  .button-row {
    grid-template-columns: 1fr;
  }

  .input-wrap input,
  .input-wrap select {
    font-size: 16px;
  }
}
</style>
