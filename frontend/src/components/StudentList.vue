<template>
  <div class="booking-container">
    <div class="header-section">
      <h2 class="page-title">All Student Bookings</h2>
      <p class="page-subtitle">Manage and view all student registrations</p>
    </div>

    <!-- Enhanced Filters Section -->
    <div class="filters-section">
      <div class="search-container">
        <div class="search-input-wrapper">
          <!-- <span class="search-icon">🔍</span> -->
          <input 
            type="text" 
            v-model="searchName" 
            placeholder="🔍 Search by name or seat number..." 
            class="search-input"
          />
          <button 
            v-if="searchName" 
            @click="searchName = ''" 
            class="clear-search"
          >
            ✕
          </button>
        </div>
      </div>

      <div class="filter-group">
        <div class="filter-item">
          <label for="shift-filter">Shift Filter</label>
          <select id="shift-filter" v-model="shiftFilter" class="filter-select">
            <option value="">All Shifts</option>
            <option value="1">🌅 Morning Shift</option>
            <option value="2">☀️ Afternoon Shift</option>
            <option value="3">🌙 Evening Shift</option>
          </select>
        </div>

        <div class="results-count">
          <span class="count-badge">{{ filteredStudents.length }} students</span>
        </div>
      </div>
    </div>

    <!-- Desktop Table View -->
    <div class="table-container desktop-view">
      <table class="student-table">
        <thead>
          <tr>
            <th>Student Details</th>
            <th>Contact</th>
            <th>Seat</th>
            <th>Shifts</th>
            <th>Fees</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(student) in filteredStudents" :key="student.id" class="student-row">
            <td class="student-info">
              <router-link :to="`/students/${student.id}`" class="student-link">
                <div class="student-avatar">
                  {{ student.name.charAt(0).toUpperCase() }}
                </div>
                <div class="student-details">
                  <span class="student-name">{{ student.name }}</span>
                  <!-- <span class="student-id">ID: {{ student.id }}</span> -->
                </div>
              </router-link>
            </td>
            
            <td class="contact-cell">
              <span class="contact-number">{{ student.contact }}</span>
            </td>
            
            <td class="seat-cell">
              <span class="seat-badge" v-if="student.seat?.seat_number">
                {{ student.seat.seat_number }}
              </span>
              <span class="no-seat" v-else>Not assigned</span>
            </td>
            
            <td class="shifts-cell">
              <div class="shift-indicators">
                <span class="shift-badge" :class="{ active: student.shift1, inactive: !student.shift1 }">
                  <span class="shift-icon">🌅</span>
                  <span class="shift-label">M</span>
                </span>
                <span class="shift-badge" :class="{ active: student.shift2, inactive: !student.shift2 }">
                  <span class="shift-icon">☀️</span>
                  <span class="shift-label">A</span>
                </span>
                <span class="shift-badge" :class="{ active: student.shift3, inactive: !student.shift3 }">
                  <span class="shift-icon">🌙</span>
                  <span class="shift-label">E</span>
                </span>
              </div>
            </td>
            
            <td class="fees-cell">
              <span class="fee-amount">₹{{ formatAmount(student.custom_fees ?? student.total_fee) }}</span>
            </td>
            
            <td class="actions-cell">
              <div class="action-buttons">
                <button class="action-btn edit-btn" @click="editStudent(student)" title="Edit Student">
                  <span class="btn-icon">✏️</span>
                  <span class="btn-text">Edit</span>
                </button>
                <button
                  v-if="student.status === 'active'"
                  class="action-btn delete-btn"
                  @click="markLeft(student.id)"
                  title="Delete Student"
                >
                  <span class="btn-icon">🗑️</span>
                  <span class="btn-text">Delete</span>
                </button>
                <span v-else class="status-left">
                  <span class="left-icon">👋</span>
                  Left
                </span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Mobile Card View -->
    <div class="mobile-view">
      <div 
        v-for="student in filteredStudents" 
        :key="student.id" 
        class="student-card"
      >
        <div class="card-header">
          <router-link :to="`/students/${student.id}`" class="student-link">
            <div class="student-avatar mobile">
              {{ student.name.charAt(0).toUpperCase() }}
            </div>
            <div class="student-info-mobile">
              <h3 class="student-name-mobile">{{ student.name }}</h3>
              <p class="student-contact">{{ student.contact }}</p>
            </div>
          </router-link>
          
          <div class="seat-info-mobile">
            <span class="seat-badge mobile" v-if="student.seat?.seat_number">
              Seat {{ student.seat.seat_number }}
            </span>
            <span class="no-seat mobile" v-else>No Seat</span>
          </div>
        </div>

        <div class="card-body">
          <div class="shifts-section-mobile">
            <h4>Enrolled Shifts</h4>
            <div class="shift-indicators mobile">
              <span class="shift-badge mobile" :class="{ active: student.shift1, inactive: !student.shift1 }">
                <span class="shift-icon">🌅</span>
                <span class="shift-name">Morning</span>
              </span>
              <span class="shift-badge mobile" :class="{ active: student.shift2, inactive: !student.shift2 }">
                <span class="shift-icon">☀️</span>
                <span class="shift-name">Afternoon</span>
              </span>
              <span class="shift-badge mobile" :class="{ active: student.shift3, inactive: !student.shift3 }">
                <span class="shift-icon">🌙</span>
                <span class="shift-name">Evening</span>
              </span>
            </div>
          </div>

          <div class="fees-section-mobile">
            <span class="fees-label">Total Fees:</span>
            <span class="fee-amount mobile">₹{{ formatAmount(student.custom_fees ?? student.total_fee) }}</span>
          </div>
        </div>

        <div class="card-footer">
          <div class="action-buttons mobile">
            <button class="action-btn edit-btn mobile" @click="editStudent(student)">
              <!-- <span class="btn-icon">✏️</span> -->
              <span class="btn-text">Edit</span>
            </button>
            <button
              v-if="student.status === 'active'"
              class="action-btn delete-btn mobile"
              @click="markLeft(student.id)"
            >
              <!-- <span class="btn-icon">🗑️</span> -->
              <span class="btn-text">Delete</span>
            </button>
            <span v-else class="status-left mobile">
              <!-- <span class="left-icon">👋</span> -->
              Left
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- No Results State -->
    <div v-if="filteredStudents.length === 0" class="no-results">
      <div class="no-results-icon">📭</div>
      <h3>No Students Found</h3>
      <p v-if="searchName || shiftFilter">Try adjusting your search criteria or filters.</p>
      <p v-else>No students have been registered yet.</p>
    </div>

    <!-- Modal for Student Form -->
    <div v-if="editingStudent" class="modal-overlay" @click.self="editingStudent = null">
      <div class="modal-content">
        <div class="modal-header">
          <h3>✏️ Edit Student</h3>
          <button class="modal-close" @click="editingStudent = null">✕</button>
        </div>
        <div class="modal-body">
          <StudentForm
            :existingStudent="editingStudent"
            @close="editingStudent = null"
            @updated="handleUpdate"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>

/* eslint-disable */

import API from '../api';
import StudentForm from './StudentForm.vue';
import { useToast } from 'vue-toast-notification';
import 'vue-toast-notification/dist/theme-sugar.css';

export default {
  components: { StudentForm },
  data() {
    return {
      students: [],
      editingStudent: null,
      searchName: '',
      shiftFilter: '',
      statusFilter: '',
      loading: false
    };
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
          backgroundColor: '#667eea',
          color: '#fff',
          borderRadius: '12px'
        },       
        ...options
      });
    };
    
    const showError = (message) => {
      toast.error(message, {
        style: {
          backgroundColor: '#dc2626',
          color: '#fff',
          borderRadius: '12px'
        }
      });
    };
    
    return {
      showSuccess,
      showError
    };
  },

  methods: {
    async fetchStudents() {
      this.loading = true;
      try {
        const res = await API.get('/students/');
        this.students = res.data;
      } catch (err) {
        this.showError('Failed to fetch students: ' + (err.response?.data?.detail || err.message));
      } finally {
        this.loading = false;
      }
    },
    
    async markLeft(id) {
      if (confirm("⚠️ Are you sure you want to delete this student? This action cannot be undone.")) {
        try {
          await API.put(`/students/${id}/mark-left`);
          this.showSuccess("✅ Student deleted successfully!");
          this.fetchStudents();
        } catch (err) {
          this.showError("❌ Error: " + (err.response?.data?.detail || err.message));
        }
      }
    },
    
    editStudent(student) {
      this.editingStudent = { ...student };
    },
    
    handleUpdate() {
      this.editingStudent = null;
      this.fetchStudents();
      // this.showSuccess("✅ Student updated successfully!");
    },
    
    formatAmount(amount) {
      return amount ? amount.toLocaleString('en-IN') : '0';
    }
  },

  computed: {
    filteredStudents() {
      return this.students.filter(student => {
        const search = this.searchName.trim().toLowerCase();

        const matchesName = student.name.toLowerCase().includes(search);
        const seatNum = student.seat?.seat_number ? String(student.seat.seat_number) : '';
        const matchesSeat = seatNum.includes(search);

        const matchesShift =
          this.shiftFilter === '' ||
          (this.shiftFilter === '1' && student.shift1) ||
          (this.shiftFilter === '2' && student.shift2) ||
          (this.shiftFilter === '3' && student.shift3);

        const matchesStatus =
          this.statusFilter === '' || student.status === this.statusFilter;

        return (matchesName || matchesSeat) && matchesShift && matchesStatus;
      });
    }
  },

  created() {
    this.fetchStudents();
  }
};
</script>

<style scoped>
.booking-container {
  min-height: 100vh;
  /* background: linear-gradient(90deg, #7e00d0 0%, #007bff 100%); */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  padding-top: 3.5rem;
}

.header-section {
  text-align: center;
  margin-bottom: 2rem;
  color: white;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.page-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  font-weight: 300;
  margin: 0;
}

.filters-section {
  max-width: 1200px;
  margin: 0 auto 2rem auto;
  background: rgba(255,255,255,0.95);
  padding: 24px;
  border-radius: 20px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.search-container {
  margin-bottom: 20px;
}

.search-input-wrapper {
  position: relative;
  max-width: 500px;
  margin: 0 auto;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.2rem;
  color: #9ca3af;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 16px 16px 16px 10px;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  outline: none;
  font-size: 16px;
  transition: all 0.3s ease;
  background: white;
}

.search-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.clear-search {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: #f3f4f6;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.clear-search:hover {
  background: #e5e7eb;
}

.filter-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-item label {
  font-weight: 600;
  color: #374151;
  font-size: 0.9rem;
}

.filter-select {
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  outline: none;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: border-color 0.3s ease;
  min-width: 180px;
}

.filter-select:focus {
  border-color: #667eea;
}

.results-count {
  margin-left: auto;
}

.count-badge {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.table-container {
  max-width: 1200px;
  margin: 0 auto;
  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}

.student-table {
  width: 100%;
  border-collapse: collapse;
}

.student-table th {
  background: #764ba2;
  /* background: linear-gradient(45deg, #667eea, #764ba2); */
  color: white;
  padding: 20px 16px;
  text-align: center;
  font-weight: 600;
  font-size: 0.95rem;
  border: none;
}

.student-row {
  transition: all 0.3s ease;
  animation: slideIn 0.6s ease-out forwards;
  opacity: 0;
}

.student-row:hover {
  background: #f8faff;
  transform: scale(1.01);
}

.student-row:nth-child(even) {
  background: rgba(102, 126, 234, 0.02);
}

.student-table td {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  vertical-align: middle;
}

.student-info {
  min-width: 200px;
}

.student-link {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s ease;
}

.student-link:hover {
  transform: translateX(4px);
}

.student-avatar {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.2rem;
  flex-shrink: 0;
}

.student-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.student-name {
  font-weight: 600;
  color: #1f2937;
  text-transform: uppercase;
  font-size: 0.95rem;
}

.student-id {
  font-size: 0.8rem;
  color: #6b7280;

}

.contact-number {
  font-family: 'Monaco', 'Menlo', monospace;
  color: #374151;
  font-weight: 500;
}

.seat-badge {
  background: linear-gradient(45deg, #10b981, #059669);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  display: inline-block;
}

.no-seat {
  color: #9ca3af;
  font-style: italic;
}

.shift-indicators {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.shift-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 8px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  transition: all 0.3s ease;
}

.shift-badge.active {
  background: linear-gradient(45deg, #10b981, #059669);
  color: white;
  box-shadow: 0 2px 6px rgba(16, 185, 129, 0.3);
}

.shift-badge.inactive {
  background: #f3f4f6;
  color: #9ca3af;
}

.shift-icon {
  font-size: 0.9rem;
}

.shift-label {
  font-weight: 700;
  min-width: 12px;
}

.fee-amount {
  font-weight: 700;
  color: #dc2626;
  font-size: 1.1rem;
  font-family: 'Monaco', 'Menlo', monospace;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.3s ease;
  min-width: 80%;
  justify-content: center;
}

.edit-btn {
  background: linear-gradient(45deg, #3b82f6, #764ba2);
  color: white;
}

.edit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.delete-btn {
  background: linear-gradient(45deg, #dc2626, #b91c1c);
  color: white;
}

.delete-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
}

.status-left {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #9ca3af;
  font-style: italic;
  font-weight: 500;
  padding: 8px 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.no-results {
  text-align: center;
  padding: 4rem 2rem;
  color: white;
  max-width: 500px;
  margin: 0 auto;
}

.no-results-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.no-results h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.no-results p {
  opacity: 0.9;
  line-height: 1.5;
}

/* Mobile View */
.mobile-view {
  display: none;
  gap: 20px;
}

.student-card {
  background: rgba(255,255,255,0.95);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.student-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f3f4f6;
}

.student-avatar.mobile {
  width: 50px;
  height: 50px;
  font-size: 1.4rem;
}

.student-info-mobile {
  flex: 1;
  margin-left: 12px;
}

.student-name-mobile {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0 0 4px 0;
  color: #1f2937;
  text-transform: uppercase;
}

.student-contact {
  margin: 0;
  color: #6b7280;
  font-size: 0.9rem;
}

.seat-badge.mobile {
  font-size: 0.8rem;
  padding: 6px 12px;
  white-space: nowrap;
  margin: 10px;
}

.no-seat.mobile {
  font-size: 0.8rem;
  padding: 4px 8px;
  background: #f3f4f6;
  border-radius: 12px;
}

.card-body {
  margin-bottom: 0px;
}

.shifts-section-mobile h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 8px 0;
}

.shift-indicators.mobile {
  gap: 8px;
  justify-content: center;
}

.shift-badge.mobile {
  padding: 8px 12px;
  min-width: unset;
}

.shift-name {
  font-weight: 600;
  font-size: 0.8rem;
}

.fees-section-mobile {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding: 12px;
  background: #f8faff;
  border-radius: 8px;
}

.fees-label {
  font-weight: 600;
  color: #374151;
}

.fee-amount.mobile {
  font-size: 1.2rem;
}

.card-footer {
  padding-top: 16px;
  border-top: 2px solid #f3f4f6;
}

.action-buttons.mobile {
  justify-content: stretch;
}

.action-btn.mobile {
  flex: 1;
  min-width: unset;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  /* z-index: 9999; */
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
  overflow: auto;
}

.modal-content {
  background: rgba(255, 255, 255, 0);
  border-radius: 20px;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  /* overflow: auto; */
  /* box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); */
  animation: modalSlideIn 0.3s ease-out;
  scrollbar-width: none;
  -ms-overflow-style: none;
  margin-bottom: 4rem;
}

.modal-header {
  display: none;
  align-items: center;
  justify-content: space-between;
  padding: 24px 24px 16px 24px;
  border-bottom: 2px solid #f3f4f6;
}

.modal-header h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.modal-close {
  background: #f3f4f6;
  border: none;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  transition: all 0.3s ease;
}

.modal-close:hover {
  background: #e5e7eb;
  transform: scale(1.1);
}

.modal-body {
  padding: 0px;
}

/* Animations */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.student-row:nth-child(1) { animation-delay: 0.1s; }
.student-row:nth-child(2) { animation-delay: 0.2s; }
.student-row:nth-child(3) { animation-delay: 0.3s; }
.student-row:nth-child(4) { animation-delay: 0.4s; }
.student-row:nth-child(5) { animation-delay: 0.5s; }

/* Responsive Design */
@media (max-width: 1024px) {
  .desktop-view {
    display: none;
  }

  .search-input {
    width: 85%;
  }
  
  .mobile-view {
    display: flex;
    flex-direction: column;
    max-width: 800px;
    margin: 0 auto;
  }
}

@media (max-width: 768px) {
  .booking-container {
    padding: 16px;
    padding-top: 4rem;
  }
  
  .page-title {
    font-size: 2rem;
  }

  .search-input {
    width: 85%;
  }
  
  .filters-section {
    padding: 20px;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .filter-select {
    min-width: unset;
    width: 100%;
  }
  
  .results-count {
    margin-left: 0;
    text-align: center;
  }
  
  .student-card {
    padding: 16px;
  }
  
  .card-header {
    flex-direction: row;
    align-items: flex-start;
    gap: 12px;
  }
  
  .student-link {
    width: 100%;
  }
  
  .seat-info-mobile {
    align-self: flex-end;
  }
  
  .shift-indicators.mobile {
    flex-wrap: wrap;
  }
  
  .action-buttons.mobile {
    flex-direction: row;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  
  .search-input {
    font-size: 16px; /* Prevent zoom on iOS */
  }
  .search-input {
    width: 85%;
  }
  
  .student-avatar.mobile {
    width: 40px;
    height: 40px;
    font-size: 1.2rem;
  }
  
  .student-name-mobile {
    font-size: 1.1rem;
  }
  
  .shift-badge.mobile {
    padding: 6px 8px;
    font-size: 0.75rem;
  }
}
</style>
