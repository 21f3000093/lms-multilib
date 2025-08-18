<template>
  <div class="container">
    <h2>Monthly Payment Management</h2>

    <!-- Month Selector and Generate Button -->
    <div class="month-controls">
      <!-- <label> -->
        <!-- Select Month: -->
      <input type="month" v-model="selectedMonth" />
      <!-- </label> -->
      <button @click="generatePayments">Generate</button>
      <button @click="downloadCSV">📥 Export CSV</button>
      
      
    <router-link to="/reminders" class="reminder-btn">
      <button >🔔 Send Fee Reminders</button>
    </router-link>
    </div>

    <!-- Filters -->
    <div class="filters">
      <input type="text" v-model="searchTerm" placeholder="Search by Name or Seat Number" />
      <select v-model="statusFilter">
        <option value="">All</option>
        <option value="paid">Paid</option>
        <option value="unpaid">Unpaid</option>
      </select>
    </div>


    <table v-if="payments.length" class="student-table">
        <thead>
            <tr>
            <th>Name</th>
            <th>Seat</th>
            <th>Amount</th>
            <th>Date of Joining</th>
            <th>Status</th>
            <th>Actions</th> <!-- New -->
            </tr>
        </thead>
        <tbody>
            <!-- <tr v-for="payment in payments" :key="payment.id"> -->
            <tr v-for="payment in filteredPayments" :key="payment.id">
            <!-- <td>{{ payment.student.name }}</td> -->
            <td><router-link :to="`/students/${payment.student.id}`" class="student-link" style="text-transform:uppercase;">{{ payment.student.name }}</router-link></td>
            <td>{{ payment.student.seat?.seat_number || '—' }}</td>  <!-- This should be the seat number . Will change in future-->
            <!-- <td>{{ payment.student.seat_id }}</td>  This should be the seat number . Will change in future -->
            <td>₹{{ payment.amount }}</td>
            <td>{{ formatDate(payment.student.date_of_joining) }}</td>
            <td>
                <span :style="{ color: payment.paid ? 'green' : 'red' }">
                {{ payment.paid ?  '✅ Paid' : '❌ Unpaid' }}
                </span>
            </td>

            <td>
                <button class="action-button edit" @click="togglePaid(payment)" :style="{ backgroundColor: payment.paid ? 'blue' : 'green' }">
                {{ payment.paid ? 'Mark Unpaid' : 'Mark Paid' }}
                </button>
                <button class="action-button mark-left" @click="deletePayment(payment)" >Delete</button>
            </td>
            </tr>
        </tbody>
    </table>

    <p v-else class="no-data">No records found. Try generating for this month.</p>


    <!-- Replace alert with custom modal -->
    <ConfirmationModal
      :show="showConfirmationModal"
      title="Payment Confirmed! 🎉"
      :message="`Send confirmation message to ${selectedPayment?.student?.name.toUpperCase()}?`"
      @whatsapp="sendWhatsAppConfirmation"
      @sms="sendSMSConfirmation"
      @cancel="closeModal"
    />



  </div>
</template>

<script>
import API from '../api';
import { useToast } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';
import ConfirmationModal from './ConfirmationModal.vue';

export default {

  components: {
    ConfirmationModal
  },
  setup() {
    const toast = useToast();
    
    // Create wrapper methods instead
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
        style: {                               // object - inline styles
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
    const today = new Date();
    const defaultMonth = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
    return {
      selectedMonth: defaultMonth,
      payments: [],
      searchTerm: '',
      statusFilter: '',
      showConfirmationModal: false,
      selectedPayment: null
    };
    
  },
  mounted() {
    this.fetchPayments();
  },

  watch: {
    selectedMonth: {
      handler: 'fetchPayments',
      immediate: false // We already fetch in mounted, so no need for immediate
    }
  },

  methods: {
    async fetchPayments() {
      try {
        const res = await API.get(`/monthly-payments/${this.selectedMonth}`);
        this.payments = res.data;
      } catch (err) {
        this.showError('Error fetching monthly payments');
      }
    },
    // async togglePaid(payment) {
    //     try {
    //     const res = await API.put(`/monthly-payments/toggle/${payment.id}`);
    //     payment.paid = res.data.paid;
    //     } catch (err) {
    //     alert('Failed to toggle status');
    //     }
    // },

    async togglePaid(payment) {
      try {
        const res = await API.put(`/monthly-payments/toggle/${payment.id}`);
        payment.paid = res.data.paid;
        
        if (payment.paid) {
          this.showSuccess('Payment marked as paid!');
          
          // Show confirmation modal instead of alert
          this.showConfirmationModal = true;
          this.selectedPayment = payment;
        }
      } catch (err) {
        this.showError('Failed to toggle status');
      }
    },

    sendWhatsAppConfirmation() {
      this.sendPaymentConfirmation(this.selectedPayment);
      this.closeModal();
    },

    sendSMSConfirmation() {
      this.sendSMS(this.selectedPayment);
      this.closeModal();
    },

    closeModal() {
      this.showConfirmationModal = false;
      this.selectedPayment = null;
    },

    sendPaymentConfirmation(payment) {
    const libraryName = localStorage.getItem('library_name') || "Your Library";
    
    // Format the month from selectedMonth (YYYY-MM to readable format)
    const monthDate = new Date(this.selectedMonth + '-01');
    const monthName = monthDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    
    const msg = `Dear ${payment.student.name},\n` +
                // `Thank you for your payment!\n` +
                `We have received your library fee of ₹${payment.amount} for ${monthName}.\n` +
                `Your payment has been successfully recorded.\n\n` +
                `Thanks,\n${libraryName}`;
    
    const phone = "91" + payment.student.contact.replace(/^0+/, "");
    const url = `https://wa.me/${phone}?text=${encodeURIComponent(msg)}`;
    window.open(url, "_blank");
  },


  sendSMS(payment) {
    const libraryName = localStorage.getItem('library_name') || "Your Library";
    
    // Format the month from selectedMonth (YYYY-MM to readable format)
    const monthDate = new Date(this.selectedMonth + '-01');
    const monthName = monthDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
    
    const msg = `Dear ${payment.student.name},\n` +
                // `Thank you for your payment! \n` +
                `We have received your library fee of ₹${payment.amount} for ${monthName}.\n` +
                `Your payment has been successfully recorded.\n\n` +
                `Thanks,\n${libraryName}`;
    
    // Remove country code prefix if present
    const phone = payment.student.contact.replace(/^(\+91|91)/, "");
    const url = `sms:${phone}?body=${encodeURIComponent(msg)}`;
    window.open(url, "_blank");
  },
    

  async deletePayment(payment) {
        if (!confirm('Are you sure you want to delete this payment?')) return;
        try {
        await API.delete(`/monthly-payments/${payment.id}`);
        this.payments = this.payments.filter(p => p.id !== payment.id);
        this.showSuccess('Payment deleted successfully');
        } catch (err) {
        this.showError('Error deleting payment');
        }
    },
    async generatePayments() {
      try {
        const monthDate = new Date(this.selectedMonth + '-01');
        const monthName = monthDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
        await API.post(`/generate-monthly-payments/${this.selectedMonth}`);
        this.showSuccess(`Records generated for ${monthName}`);
        this.fetchPayments(); // refresh the list
      } catch (err) {
        this.showError('Error generating monthly records');
      }
    },

    async downloadCSV() {
      try {
        const response = await API.get(`/export-monthly-payments/${this.selectedMonth}`, {
          responseType: 'blob',
        });
        const blob = new Blob([response.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `monthly_payments_${this.selectedMonth}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } catch (err) {
        this.showError('Failed to export CSV');
      }
    },

    formatDate(dateString) {
        const date = new Date(dateString);
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0'); // JS months are 0-indexed
        const year = String(date.getFullYear()).slice(-2); // get last 2 digits
        return `${day}-${month}-${year}`;
    },

  },

  computed: {    

        filteredPayments() {
          return this.payments.filter(payment => {
            const search = this.searchTerm.trim().toLowerCase();
            // Student name search
            const matchesName = payment.student.name.toLowerCase().includes(search);
            // Seat number search (convert to string, handle null)
            const seatNum = payment.student.seat?.seat_number ? String(payment.student.seat.seat_number) : '';
            const matchesSeat = seatNum.includes(search);

            const matchesStatus =
              this.statusFilter === '' ||
              (this.statusFilter === 'paid' && payment.paid) ||
              (this.statusFilter === 'unpaid' && !payment.paid);

            // Search should match name OR seat number
            return (matchesName || matchesSeat) && matchesStatus;
          });
        }


    },

};
</script>

<style scoped>
.container {
  max-width: 100%;
  margin: 5vh auto;
  padding: 2rem;
  font-family: "Segoe UI", "Poppins", sans-serif;
  background: linear-gradient(to bottom right, #f7faff3e, #e0f7fa33);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  /* max-height: 70vh; */
  height: 80vh;
  overflow-y: auto;
  scrollbar-width: none;
  padding-top: 5vh;
}

h2 {
  text-align: center;
  margin-bottom: 1rem;
  color: #333;
  font-size: 1.6rem;
  font-weight: 600;
}

/* Month Controls + Filters */
.month-controls,
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.month-controls input[type="month"],
.filters input[type="text"],
.filters select {
  padding: 10px;
  font-size: 0.95rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  min-width: 140px;
  width: 40%;
}

.month-controls button,
.reminder-btn {
  padding: 10px 16px;
  font-size: 0.95rem;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  min-width: fit-content;
  width: 14%;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  background-color: #8725d3;
}

.reminder-btn {
  padding: 0px 0px;
  font-size: 0.95rem;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  min-width: fit-content;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  background-color: #8725d3;
}


.month-controls button:hover {
  background-color: #7f22c6;
  transform: scale(1.03); /* 👈 Slight hover scale */
  filter: brightness(1.08);
}


.reminder-btn button:hover {
  background-color: #1ebe54;
}

/* Action Buttons */
.action-button {
  padding: 8px 8px;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
  /* margin-right: 1rem;
  margin-left: 1rem; */
  margin: 0.3rem;
  width: 40%;
}

.action-button.edit:hover {
  background-color: #006400;
  transform: scale(1.03);
}

.action-button.mark-left {
  background-color: #dc3545;
}

.action-button.mark-left:hover {
  background-color: #b02a37;
  transform: scale(1.03);
}

/* Table Base */
table {
  width: 98%;
  border-collapse: collapse;
  margin-top: 1rem;
  margin-left: auto;
  margin-right: auto;
}

th, td {
  padding: 0.75rem;
  /* border: 1px solid #e0e0e0; */
  border: 1px solid #ffffff64;
  text-align: left;
  font-size: 0.95rem;
  text-decoration: none;
  font-weight: 500;
  text-transform: capitalize;
}

thead {
  background-color: #f3f3f3;
}

tbody tr:nth-child(even) {
  background-color: #fafafaa6;
}

.no-data {
  text-align: center;
  margin-top: 2rem;
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

/* ✅ Responsive: Mobile Card Layout */
@media (max-width: 768px) {

  .container {
    padding: 1rem;
    margin: 0vh 0rem;
    height: 98vh;
    overflow: auto;
    background: #f4fbff00; /* 👈 Subtle mobile bg */
    padding-top: 7vh;
  }
  
  thead {
    display: none;
    
  }

.student-table tbody,
  .student-table td {
    display: block;
    width: 98%;
    /* box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15); */
  }
  .student-table {
    display: block;
    width: 95%;
    /* box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15); */
  }
  .student-table tr{
    display: block;
    width: 95%;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }

  .student-table tr {
    margin-bottom: 1rem;
    border: 1px solid #bca9ce;
    border-radius: 8px;
    padding: 0.8rem;
    background-color: #fefefe1b;
  }

  .student-table td {
    text-align: left;
    padding-left: 50%;
    position: relative;
    white-space: pre-wrap;
    box-sizing: border-box;
    
    
  }

  .student-table td::before {
    position: absolute;
    left: 1rem;
    top: 0.6rem;
    font-weight: bold;
    white-space: nowrap;
    color: #444;    
  }


  td:nth-child(1)::before { content: "Name";  }
  td:nth-child(2)::before { content: "Seat"; }
  td:nth-child(3)::before { content: "Amount"; }
  td:nth-child(4)::before { content: "Date of Joining"; }
  td:nth-child(5)::before { content: "Status"; }
  td:nth-child(6)::before { content: "Actions"; }

  .action-button {
    width: 90%;
    margin-top: 0.5rem;
    font-size: 1rem;
    
  }

  .month-controls,
  .filters {
    flex-direction: row;
    gap: 0.8rem;
    /* max-width: 20%; */
    /* margin: auto; */
    padding: auto;
    
  }

  .month-controls input[type="month"],
  .month-controls button,
  .reminder-btn {
    /* display: flex; */
    width: 90%;
    /* flex-direction: row; */
    gap: 0.8rem;
    margin: auto;
    
  }

  .filters input[type="text"]{
    display: flex;
    flex-direction: row;
    gap: 0.1rem;
    margin: auto;
    width: 40%;
  }
  
  .filters select {
    display: flex;
    flex-direction: row;
    gap: 0.1rem;
    margin: auto;
    width: 40%;
  }

  .reminder-btn:hover {
  background-color: #1ebe54;
}

  .month-controls .reminder-btn button {
    width: 100%;
    
  }
}
</style>
