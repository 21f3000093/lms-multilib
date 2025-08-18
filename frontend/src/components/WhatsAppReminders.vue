<template>
  <div class="booking-container">
    <h2>💰 Pending Fee Reminders</h2>

    <div class="filters">
      <button @click="$router.back()" class="action-button back">Back</button>
      <button @click="fetchReminders" class="action-button edit">Refresh</button>
    </div>

    <table v-if="pendingList.length > 0" class="student-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Phone</th>
          <th>Amount</th>
          <th>Month</th>
          <th>Due Date</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="student in pendingList" :key="student.phone">
          <!-- <td>{{ student.student_name }}</td> -->
           <td><router-link :to="`/students/${student.student_id}`" class="student-link" style="text-transform:uppercase;">{{ student.student_name }}</router-link></td>
          <td>{{ student.phone }}</td>
          <td>₹{{ student.amount }}</td>
          <td>{{ student.month }}</td>
          <td>{{ student.due_date }}</td>
          <td>
            <!-- <button class="action-button edit" @click="sendWhatsApp(student)">📩 WhatsApp</button> -->
            <button class="action-button edit" @click="openReminderModal(student)">Send Reminder</button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else class="no-data">✅ No pending reminders</p>

    <!-- Fee Reminder Modal -->
    <ConfirmationModal
      :show="showReminderModal"
      title="Send Fee Reminder 💰"
      :message="`Send payment reminder to ${selectedStudent?.student_name?.toUpperCase()}?`"
      @whatsapp="sendReminderWhatsApp"
      @sms="sendReminderSMS"
      @cancel="closeReminderModal" />

  </div>
</template>



<script>
import API from '../api';
import ConfirmationModal from './ConfirmationModal.vue';
import { useToast } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';

export default {

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

  components: {
    ConfirmationModal
  },

  data() {
    return {
      pendingList: [],
      showReminderModal: false,
      selectedStudent: null
    };
  },
  
  methods: {
    async fetchReminders() {
      try {
        const res = await API.get("/reminders/pending-fees");
        this.pendingList = res.data;
      } catch (err) {
        this.showError("Failed to fetch reminders: " + (err.response?.data?.detail || err.message));
      }
    },
    // Open the confirmation modal
    openReminderModal(student) {
      this.selectedStudent = student;
      this.showReminderModal = true;
    },

    // Close the modal
    closeReminderModal() {
      this.showReminderModal = false;
      this.selectedStudent = null;
    },

    // Send reminder via WhatsApp
    sendReminderWhatsApp() {
      const message = this.generateReminderMessage();
      const phone = "91" + this.selectedStudent.phone.replace(/^0+/, "");
      const url = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
      window.open(url, "_blank");
      this.closeReminderModal();
      
      // Optional: Show success message
      // You can add toast notification here if you want
    },

    // Send reminder via SMS
    sendReminderSMS() {
      const message = this.generateReminderMessage();
      const phone = this.selectedStudent.phone.replace(/^(\+91|91)/, "");
      const url = `sms:${phone}?body=${encodeURIComponent(message)}`;
      window.open(url, "_blank");
      this.closeReminderModal();
      
      // Optional: Show success message
      // You can add toast notification here if you want
    },

    // Generate the reminder message
    generateReminderMessage() {
      const libraryName = localStorage.getItem('library_name') || "Your Library";
      
      return `Dear ${this.selectedStudent.student_name},\n` +
             `Your library fee of Rs.${this.selectedStudent.amount} for ${this.selectedStudent.month} was due on ${this.selectedStudent.due_date}.\n` +
             `Please pay it as soon as possible to avoid disruption.\n\n` +
             `Thanks,\n${libraryName}`;
    },

    // Keep the old method for backward compatibility (optional)
    sendWhatsApp(student) {
      this.openReminderModal(student);
    }
  },
  created() {
    this.fetchReminders();
  },
};
</script>

<style scoped>
.booking-container {
  max-width: 100%;
  margin: 2vh auto;
  padding: 2rem;
  border-radius: 12px;
  background: linear-gradient(to bottom right, #f7faff3e, #e0f7fa33); /* 👈 Updated: Light pleasant gradient */
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08); /* 👈 Softer shadow */
  font-family: "Segoe UI", "Poppins", sans-serif; /* 👈 Better font */
  height: 85vh;
  /* overflow: auto; */
  overflow-y: auto;
  scrollbar-width: none;
  padding-top: 7vh;
}

h2 {
  text-align: center;
  margin-bottom: 1rem;
  color: #333;
  font-size: 1.6rem; /* 👈 Better visual hierarchy */
  font-weight: 600;
}

/* Filters (Back + Load Buttons) */
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  justify-content: space-between;
}

.filters button {
    display: flex;
    width: 30%;
    flex-direction: row;
    gap: 0.8rem;
    margin: auto;     
    justify-content: center;
    
  }

.action-button {
  padding: 10px 16px; /* 👈 Slightly larger */
  border: none;
  border-radius: 8px; /* 👈 More modern curve */
  color: #f6f1f1;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  min-width: 130px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1); /* 👈 Button shadow */
}

.action-button.edit {
  background-color: #8725d3; /* WhatsApp Green */
}
.action-button.edit:hover {
  background-color: #7f22c6;
  transform: scale(1.03); /* 👈 Slight hover scale */
}

.action-button.back {
  background-color: #8725d3;
}
.action-button.back:hover {
  background-color: #7f22c6;
  transform: scale(1.03);
}

/* Student Table */
.student-table {
  width: 100%;
  border-collapse: collapse;
  background: rgba(255, 255, 255, 0.211); /* 👈 Light card background */
  border-radius: 10px;
  overflow: hidden; /* 👈 Rounded corners applied */
}

.student-table th,
.student-table td {
  border: 1px solid #e0e0e0;
  padding: 12px;
  text-align: center;
  font-size: 0.95rem;
  text-transform: capitalize;
}

.student-table th {
  background-color: #f3f3f364;
  font-weight: 600;
  color: #444;
}

.student-table tbody tr:nth-child(even) {
  background-color: #fafafa4e;
}

.no-data {
  margin-top: 2rem;
  text-align: center;
  color: green;
  font-style: italic;
  font-size: 1rem;
}

.student-link {
  color: #494ed5;
  /* color: #2c2929; */
  text-decoration: none;
  font-weight: 500;
  text-transform: capitalize;
}

.student-link:hover {
  text-decoration: none;
  color: #8725d3;
  transform: scale(1.03);

}

/* 🔧 Responsive Design for Mobiles */
@media (max-width: 768px) {
  .booking-container {
    padding: 0.5rem 1rem;
    margin: 0vh 0rem;
    height: 90vh;
    overflow: auto;
    background: #f4fbff00; /* 👈 Subtle mobile bg */
    padding-top: 7vh;
  }

  .student-table thead {
    display: none;
  }

  .student-table tbody,
  .student-table td {
    display: block;
    width: 98%;
  }

  .student-table {
    display: block;
    width: 98%;
  }

  .student-table tr {
    display: block;
    width: 97%;
    margin-bottom: 1.2rem;
    border: 1px solid #dcdcdc;
    border-radius: 10px;
    padding: 1rem;
    background-color: #ffffff57;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05); /* 👈 Card shadow on mobile */
  }

  .student-table td {
    text-align: left;
    padding-left: 45%;
    position: relative;
    white-space: pre-wrap;
    box-sizing: border-box;
    font-size: 0.95rem;
    line-height: 1.5;
  }

  .student-table td::before {
    position: absolute;
    left: 1rem;
    top: 0.6rem;
    font-weight: 600;
    color: #333;
  }

  .student-table td:nth-child(1)::before { content: "Name"; }
  .student-table td:nth-child(2)::before { content: "Phone"; }
  .student-table td:nth-child(3)::before { content: "Amount"; }
  .student-table td:nth-child(4)::before { content: "Month"; }
  .student-table td:nth-child(5)::before { content: "Due Date"; }
  .student-table td:nth-child(6)::before { content: "Action"; }

  .action-button {
    width: 90%;
    margin-top: 0.6rem;
    font-size: 1rem;
    font-weight: 600;
  }

  .filters button {
    display: flex;
    max-width: 40%;
    flex-direction: row;
    gap: 0.8rem;
    margin: auto;   
    
  }
}
</style>
