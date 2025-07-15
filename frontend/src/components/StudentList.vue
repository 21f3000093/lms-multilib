<template>
  <div class="booking-container">
    <h2>All Student Bookings</h2>
    <!-- Student Filters -->
    <div class="filters">
      <input type="text" v-model="searchName" placeholder="Search by name" />

      <select v-model="shiftFilter">
        <option value="">All Shifts</option>
        <option value="1">Shift 1</option>
        <option value="2">Shift 2</option>
        <option value="3">Shift 3</option>
      </select>

      <!-- <select v-model="statusFilter">
        <option value="">All</option>
        <option value="active">Active</option>
        <option value="left">Left</option>
      </select> -->
    </div>

    <table class="student-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Contact</th>
          <th>Seat No</th>
          <th>Shifts</th>
          
          <!-- <th>Shift 2</th> -->
          <!-- <th>Shift 3</th> -->

          <th>Total Fees</th>
          <!-- <th>Paid</th> -->
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <!-- <tr v-for="student in students" :key="student.id"> -->
          <tr v-for="student in filteredStudents" :key="student.id">

          <!-- <td>{{ student.name }}</td> -->
          <td><router-link :to="`/students/${student.id}`" class="student-link">{{ student.name }}</router-link></td>
          
          <td>{{ student.contact }}</td>
          <td>{{ student.seat?.seat_number || '—' }}</td>
          <td>{{ student.shift1 ? '✅' : '❌' }} {{ student.shift2 ? '✅' : '❌' }} {{ student.shift3 ? '✅' : '❌' }}</td>

          <!-- <td>{{ student.shift2 ? '✅' : '❌' }}</td> -->
          <!-- <td>{{ student.shift3 ? '✅' : '❌' }}</td> -->
           
          <td>₹{{ student.custom_fees ?? student.total_fee }}</td>
          <!-- <td>{{ student.paid ? '✅' : '❌' }}</td> -->
          <td>
            <button class="action-button edit" @click="editStudent(student)">✏️ Edit</button>
            <button
              v-if="student.status === 'active'"
              class="action-button mark-left"
              @click="markLeft(student.id)"
            >
              Delete
            </button>
            <span v-else class="status-left">Left</span>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- <StudentForm
      v-if="editingStudent"
      :existingStudent="editingStudent"
      @close="editingStudent = null"
      @updated="handleUpdate"
    /> -->
    <div v-if="editingStudent" class="modal-overlay" @click.self="editingStudent = null">
      <div class="modal-content">
        <StudentForm
          :existingStudent="editingStudent"
          @close="editingStudent = null"
          @updated="handleUpdate"
        />
      </div>
    </div>

  </div>
</template>

<script>
import API from '../api';
import StudentForm from './StudentForm.vue';

export default {
  components: { StudentForm },
  data() {
    return {
      students: [],
      editingStudent: null,
      searchName: '',
      shiftFilter: '',
      statusFilter: ''
    };
  },
  methods: {
    async fetchStudents() {
      try {
        const res = await API.get('/students/');
        this.students = res.data;
      } catch (err) {
        alert('Failed to fetch students: ' + (err.response?.data?.detail || err.message));
      }
    },
    async markLeft(id) {
      if (confirm("Are you sure you want to mark this student as left?")) {
        try {
          await API.put(`/students/${id}/mark-left`);
          alert("Student marked as left!");
          this.fetchStudents(); // reload data
        } catch (err) {
          alert("Error: " + (err.response?.data?.detail || err.message));
        }
      }
    },
    editStudent(student) {
      this.editingStudent = { ...student }; // open form with data
    },
    handleUpdate() {
      this.editingStudent = null;
      this.fetchStudents();
    }
  },

  computed: {
  filteredStudents() {
      return this.students.filter(student => {
        const matchesName = student.name.toLowerCase().includes(this.searchName.toLowerCase());

        const matchesShift =
          this.shiftFilter === '' ||
          (this.shiftFilter === '1' && student.shift1) ||
          (this.shiftFilter === '2' && student.shift2) ||
          (this.shiftFilter === '3' && student.shift3);

        const matchesStatus =
          this.statusFilter === '' || student.status === this.statusFilter;

        return matchesName && matchesShift && matchesStatus;
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
  max-width: 1200px;
  margin: 2vh auto;
  padding: 2rem;
  background-color: #ffffff00;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  font-family: "Segoe UI", sans-serif;
}

h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: #333;
}

/* Filters */
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  justify-content: space-between;
}

.filters input,
.filters select {
  padding: 10px;
  font-size: 1rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  flex: 1;
  min-width: 150px;
}

/* Table */
.student-table {
  width: 100%;
  border-collapse: collapse;
  /* overflow-x: auto; */
}

.student-table th,
.student-table td {
  border: 1px solid #ffffff64;
  padding: 10px;
  text-align: center;
  font-size: 0.95rem;
}

.student-table th {
  background-color: #f0f0f000;
  font-weight: 600;
}

.student-table tbody tr:nth-child(even) {
  background-color: #fafafa00;
}

.student-link {
  color: #2c2929;
  text-decoration: none;
  font-weight: 500;
  text-transform: capitalize;
}

.student-link:hover {
  text-decoration: none;

}

/* Action Buttons */
.action-button {
  padding: 6px 10px;
  margin: 4px 0;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
  width: 100%; /* For mobile layout */
  box-sizing: border-box;
}

.action-button.edit {
  background-color: #007bff;
}

.action-button.edit:hover {
  background-color: #0056b3;
}

.action-button.mark-left {
  background-color: #dc3545;
}

.action-button.mark-left:hover {
  background-color: #b02a37;
}

.status-left {
  color: #999;
  font-weight: 500;
  font-style: italic;
}

/* ✅ Responsive Design: Mobile and Tablet (≤768px) */
@media (max-width: 768px) {
  .booking-container {
    padding: 1rem;
    margin: 2vh 1rem;
    max-height: 90vh;
    overflow: auto;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }

  .filters {
    flex-direction: row;
    gap: 0.8rem;
  }

  .filters input,
  .filters select {
    width: 95%;
  }

  .student-table thead {
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
    width: 99%;
    /* box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15); */
  }
  .student-table tr{
    display: block;
    width: 99%;
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

  .student-table td:nth-child(1)::before { content: "Name"; }
  .student-table td:nth-child(2)::before { content: "Contact"; }
  .student-table td:nth-child(3)::before { content: "Seat No"; }
  .student-table td:nth-child(4)::before { content: "Shifts"; }
  /* .student-table td:nth-child(5)::before { content: "Shift 2"; } */
  /* .student-table td:nth-child(6)::before { content: "Shift 3"; } */
  .student-table td:nth-child(5)::before { content: "Total Fees"; }
  .student-table td:nth-child(6)::before { content: "Actions"; }

  .action-button {
    margin: 4px 0;
    width: 100%;
  }

  .status-left {
    display: block;
    margin-top: 6px;
    font-size: 0.9rem;
  }
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 9999;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  max-width: 600px;
  width: 90%;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
}

</style>
