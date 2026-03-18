<template>
  <main class="student-list-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="section-shell hero">
      <div>
        <p class="kicker">Student Registry</p>
        <h1>
          Student
          <span class="gradient-text">Bookings</span>
        </h1>
        <p class="hero-subtitle">Search, filter, and manage student records with seat and shift visibility in one place.</p>
      </div>

      <div class="quick-stats">
        <article class="glass-card stat-card">
          <p class="stat-label">Total</p>
          <p class="stat-value">{{ students.length }}</p>
        </article>
        <article class="glass-card stat-card">
          <p class="stat-label">Active</p>
          <p class="stat-value">{{ activeCount }}</p>
        </article>
        <article class="glass-card stat-card">
          <p class="stat-label">Left</p>
          <p class="stat-value">{{ leftCount }}</p>
        </article>
      </div>
    </section>

    <section class="section-shell glass-card filters-card">
      <div class="search-wrap">
        <Search class="search-icon" aria-hidden="true" />
        <input
          type="text"
          v-model="searchName"
          placeholder="Search by name or seat number"
          class="search-input"
        />
        <button v-if="searchName" @click="searchName = ''" class="clear-search" type="button" aria-label="Clear search">
          <X class="clear-icon" aria-hidden="true" />
        </button>
      </div>

      <div class="filters-row">
        <label class="filter-item" for="shift-filter">
          <span>Shift</span>
          <select id="shift-filter" v-model="shiftFilter" class="filter-select">
            <option value="">All Shifts</option>
            <option value="1">Shift 1</option>
            <option value="2">Shift 2</option>
            <option value="3">Shift 3</option>
          </select>
        </label>

        <label class="filter-item" for="status-filter">
          <span>Status</span>
          <select id="status-filter" v-model="statusFilter" class="filter-select">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="left">Left</option>
          </select>
        </label>

        <div class="results-chip">
          <Filter class="chip-icon" aria-hidden="true" />
          <span>{{ filteredStudents.length }} results</span>
        </div>
      </div>
    </section>

    <section class="section-shell table-shell glass-card desktop-view">
      <div class="table-wrap">
        <table class="student-table">
          <thead>
            <tr>
              <th>Student</th>
              <th>Contact</th>
              <th>Seat</th>
              <th>Shifts</th>
              <th>Fee</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in filteredStudents" :key="student.id" class="student-row">
              <td>
                <router-link :to="`/students/${student.id}`" class="student-link">
                  <span class="avatar">{{ student.name.charAt(0).toUpperCase() }}</span>
                  <div>
                    <p class="name">{{ student.name }}</p>
                    <!-- <p class="id-text">ID: {{ student.id }}</p> -->
                  </div>
                </router-link>
              </td>

              <td>
                <span class="mono">{{ student.contact }}</span>
              </td>

              <td>
                <span v-if="student.seat?.seat_number" class="seat-pill">{{ student.seat.seat_number }}</span>
                <span v-else class="muted">Not assigned</span>
              </td>

              <td>
                <div class="shift-pills">
                  <span class="shift-pill" :class="{ active: student.shift1, inactive: !student.shift1 }">
                    <Sunrise class="shift-icon" aria-hidden="true" />
                    <span>S1</span>
                  </span>
                  <span class="shift-pill" :class="{ active: student.shift2, inactive: !student.shift2 }">
                    <Sun class="shift-icon" aria-hidden="true" />
                    <span>S2</span>
                  </span>
                  <span class="shift-pill" :class="{ active: student.shift3, inactive: !student.shift3 }">
                    <MoonStar class="shift-icon" aria-hidden="true" />
                    <span>S3</span>
                  </span>
                </div>
              </td>

              <td>
                <span class="fee-amount">₹{{ formatAmount(student.custom_fees ?? student.total_fee) }}</span>
              </td>

              <td>
                <span class="status-pill" :class="student.status === 'active' ? 'status-active' : 'status-left'">
                  {{ student.status === 'active' ? 'Active' : 'Left' }}
                </span>
              </td>

              <td>
                <div class="actions">
                  <button class="action-btn edit-btn" @click="editStudent(student)" type="button">
                    <PenLine class="action-icon" aria-hidden="true" />
                    <span>Edit</span>
                  </button>
                  <button
                    v-if="student.status === 'active'"
                    class="action-btn delete-btn"
                    @click="markLeft(student.id)"
                    type="button"
                  >
                    <Trash2 class="action-icon" aria-hidden="true" />
                    <span>Delete</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="section-shell mobile-view">
      <article v-for="student in filteredStudents" :key="student.id" class="glass-card mobile-card">
        <header class="card-head">
          <router-link :to="`/students/${student.id}`" class="student-link">
            <span class="avatar">{{ student.name.charAt(0).toUpperCase() }}</span>
            <div>
              <p class="name">{{ student.name }}</p>
              <p class="mono">{{ student.contact }}</p>
            </div>
          </router-link>
          <span v-if="student.seat?.seat_number" class="seat-pill">Seat {{ student.seat.seat_number }}</span>
          <span v-else class="muted">No Seat</span>
        </header>

        <div class="mobile-row">
          <p class="row-label">Shifts</p>
          <div class="shift-pills">
            <span class="shift-pill" :class="{ active: student.shift1, inactive: !student.shift1 }">S1</span>
            <span class="shift-pill" :class="{ active: student.shift2, inactive: !student.shift2 }">S2</span>
            <span class="shift-pill" :class="{ active: student.shift3, inactive: !student.shift3 }">S3</span>
          </div>
        </div>

        <div class="mobile-row">
          <p class="row-label">Fee</p>
          <p class="fee-amount">₹{{ formatAmount(student.custom_fees ?? student.total_fee) }}</p>
        </div>

        <div class="mobile-row footer-row">
          <span class="status-pill" :class="student.status === 'active' ? 'status-active' : 'status-left'">
            {{ student.status === 'active' ? 'Active' : 'Left' }}
          </span>

          <div class="actions">
            <button class="action-btn edit-btn" @click="editStudent(student)" type="button">
              <PenLine class="action-icon" aria-hidden="true" />
              <span>Edit</span>
            </button>
            <button
              v-if="student.status === 'active'"
              class="action-btn delete-btn"
              @click="markLeft(student.id)"
              type="button"
            >
              <UserX class="action-icon" aria-hidden="true" />
              <span>Delete</span>
            </button>
          </div>
        </div>
      </article>
    </section>

    <section v-if="filteredStudents.length === 0" class="section-shell empty-state glass-card">
      <Users class="empty-icon" aria-hidden="true" />
      <h3>No Students Found</h3>
      <p v-if="searchName || shiftFilter || statusFilter">Try adjusting search or filters.</p>
      <p v-else>No students have been registered yet.</p>
    </section>

    <div v-if="editingStudent" class="modal-overlay" @click.self="editingStudent = null">
      <div class="modal-content glass-card">
        <header class="modal-head">
          <h3>Edit Student</h3>
          <button class="modal-close" @click="editingStudent = null" type="button" aria-label="Close modal">
            <X class="modal-close-icon" aria-hidden="true" />
          </button>
        </header>

        <div class="modal-body">
          <StudentForm
            :existingStudent="editingStudent"
            @close="editingStudent = null"
            @updated="handleUpdate"
          />
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import {
  Filter,
  MoonStar,
  PenLine,
  Search,
  Sun,
  Sunrise,
  Trash2,
  UserX,
  Users,
  X,
} from 'lucide-vue-next'
import API from '../api'
import StudentForm from './StudentForm.vue'
import { useToast } from 'vue-toast-notification'
import 'vue-toast-notification/dist/theme-sugar.css'

export default {
  components: {
    Filter,
    MoonStar,
    PenLine,
    Search,
    StudentForm,
    Sun,
    Sunrise,
    Trash2,
    UserX,
    Users,
    X,
  },
  data() {
    return {
      students: [],
      editingStudent: null,
      searchName: '',
      shiftFilter: '',
      statusFilter: '',
      loading: false,
    }
  },

  setup() {
    const toast = useToast()

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
        closeButton: 'button',
        icon: true,
        rtl: false,
        style: {
          backgroundColor: 'var(--theme-panel-solid)',
          color: 'var(--theme-text-strong)',
          border: '1px solid var(--theme-brand-border)',
          borderRadius: '12px',
          boxShadow: 'var(--theme-shadow-soft)',
        },
        ...options,
      })
    }

    const showError = (message) => {
      toast.error(message, {
        style: {
          backgroundColor: 'var(--theme-panel-solid)',
          color: 'var(--theme-text-strong)',
          border: '1px solid var(--theme-danger-border)',
          borderRadius: '12px',
          boxShadow: 'var(--theme-shadow-soft)',
        },
      })
    }

    return {
      showSuccess,
      showError,
    }
  },

  computed: {
    filteredStudents() {
      return this.students.filter((student) => {
        const search = this.searchName.trim().toLowerCase()

        const matchesName = student.name.toLowerCase().includes(search)
        const seatNum = student.seat?.seat_number ? String(student.seat.seat_number) : ''
        const matchesSeat = seatNum.includes(search)

        const matchesShift =
          this.shiftFilter === '' ||
          (this.shiftFilter === '1' && student.shift1) ||
          (this.shiftFilter === '2' && student.shift2) ||
          (this.shiftFilter === '3' && student.shift3)

        const matchesStatus =
          this.statusFilter === '' || student.status === this.statusFilter

        return (matchesName || matchesSeat) && matchesShift && matchesStatus
      })
    },
    activeCount() {
      return this.students.filter((student) => student.status === 'active').length
    },
    leftCount() {
      return this.students.filter((student) => student.status !== 'active').length
    },
  },

  methods: {
    async fetchStudents() {
      this.loading = true
      try {
        const res = await API.get('/students/')
        this.students = res.data
      } catch (err) {
        this.showError('Failed to fetch students: ' + (err.response?.data?.detail || err.message))
      } finally {
        this.loading = false
      }
    },

    async markLeft(id) {
      if (confirm('Are you sure you want to delete this student? This action cannot be undone.')) {
        try {
          await API.put(`/students/${id}/mark-left`)
          this.showSuccess('Student deleted successfully!')
          this.fetchStudents()
        } catch (err) {
          this.showError('Error: ' + (err.response?.data?.detail || err.message))
        }
      }
    },

    editStudent(student) {
      this.editingStudent = { ...student }
    },

    handleUpdate() {
      this.editingStudent = null
      this.fetchStudents()
    },

    formatAmount(amount) {
      return amount ? amount.toLocaleString('en-IN') : '0'
    },
  },

  created() {
    this.fetchStudents()
  },
}
</script>

<style scoped>
.student-list-page {
  --surface: var(--theme-surface);
  --surface-border: var(--theme-surface-border);
  --text-primary: var(--theme-text-primary);
  --text-secondary: var(--theme-text-secondary);

  position: relative;
  min-height: 100vh;
  padding: 2rem 2rem 2.8rem 2rem;
  color: var(--text-primary);
  overflow: hidden;
  isolation: isolate;
}

.mesh-layer {
  position: absolute;
  inset: 0;
  z-index: -1;
  background: var(--theme-mesh-background);
  filter: saturate(115%);
  animation: mesh-drift 18s ease-in-out infinite alternate;
}

.section-shell {
  width: min(1240px, calc(100% - 2rem));
  margin: 0 auto;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
}

.kicker {
  margin: 0;
  display: inline-flex;
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
  border: 1px solid var(--theme-border);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--theme-text-soft);
  background: var(--theme-surface-soft);
}

.hero h1 {
  margin: 0.9rem 0 0;
  font-size: clamp(1.9rem, 4.4vw, 3rem);
  line-height: 1.05;
  letter-spacing: -0.03em;
}

.gradient-text {
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-subtitle {
  margin: 0.75rem 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
  max-width: 58ch;
}

.quick-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.7rem;
  width: min(360px, 100%);
}

.glass-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.stat-card {
  border-radius: 14px;
  padding: 0.75rem;
}

.stat-label {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.stat-value {
  margin: 0.32rem 0 0;
  font-size: 1.35rem;
  font-weight: 800;
}

.filters-card {
  margin-top: 0.85rem;
  border-radius: 16px;
  padding: 0.8rem;
}

.search-wrap {
  position: relative;
  display: flex;
  align-items: center;
  border: 1px solid var(--theme-input-border);
  border-radius: 12px;
  background: var(--theme-input-bg);
}

.search-wrap:focus-within {
  border-color: var(--theme-brand-border);
  box-shadow: 0 0 0 3px var(--theme-brand-ring);
}

.search-icon {
  width: 1rem;
  height: 1rem;
  margin-left: 0.75rem;
  color: var(--theme-text-muted);
  flex-shrink: 0;
}

.search-input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--theme-text-strong);
  font-size: 0.95rem;
  padding: 0.72rem;
}

.search-input::placeholder {
  color: var(--theme-input-placeholder);
}

.clear-search {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 0;
  margin-right: 0.3rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--theme-surface-soft-heavy);
  color: var(--theme-text-primary);
  cursor: pointer;
}

.clear-icon {
  width: 0.94rem;
  height: 0.94rem;
}

.filters-row {
  margin-top: 0.65rem;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.62rem;
  align-items: end;
}

.filter-item {
  display: grid;
  gap: 0.34rem;
}

.filter-item span {
  color: var(--theme-text-soft);
  font-size: 0.8rem;
  font-weight: 600;
}

.filter-select {
  border: 1px solid var(--theme-input-border);
  border-radius: 12px;
  background: var(--theme-input-bg);
  color: var(--theme-text-strong);
  min-height: 42px;
  padding: 0.45rem 0.6rem;
  outline: none;
}

.filter-select:focus {
  border-color: var(--theme-brand-border);
}

.filter-select option {
  color: var(--theme-text-strong);
}

.results-chip {
  min-height: 42px;
  border: 1px solid var(--theme-border);
  border-radius: 12px;
  background: var(--theme-surface-soft-strong);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.42rem;
  color: var(--theme-text-primary);
  font-weight: 600;
  font-size: 0.86rem;
}

.chip-icon {
  width: 0.92rem;
  height: 0.92rem;
  color: var(--theme-brand-pill-text);
}

.table-shell {
  margin-top: 0.85rem;
  border-radius: 16px;
  padding: 0.75rem;
}

.table-wrap {
  overflow-x: auto;
}

.student-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 980px;
}

.student-table th {
  text-align: left;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--theme-text-soft);
  border-bottom: 1px solid var(--theme-border);
  padding: 0.64rem 0.55rem;
}

.student-table td {
  padding: 0.64rem 0.55rem;
  border-bottom: 1px solid var(--theme-border-soft);
  color: var(--theme-text-primary);
  font-size: 0.9rem;
  vertical-align: middle;
  text-align: left;
}

.student-row:hover {
  background: var(--theme-surface-soft);
}

.student-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  color: inherit;
}

.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: inline-grid;
  place-items: center;
  font-weight: 800;
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
  color: var(--theme-brand-on);
  flex-shrink: 0;
}

.name {
  margin: 0;
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.88rem;
}

.id-text {
  margin: 0.18rem 0 0;
  color: var(--text-secondary);
  font-size: 0.72rem;
}

.mono {
  font-family: Monaco, Menlo, monospace;
}

.muted {
  color: var(--text-secondary);
}

.seat-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 56px;
  padding: 0.3rem 0.58rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
}

.shift-pills {
  display: flex;
  gap: 0.38rem;
  flex-wrap: wrap;
}

.shift-pill {
  border-radius: 999px;
  padding: 0.22rem 0.5rem;
  font-size: 0.74rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 0.2rem;
}

.shift-pill.active {
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
}

.shift-pill.inactive {
  background: var(--theme-surface-soft-heavy);
  color: var(--theme-text-secondary);
}

.shift-icon {
  width: 0.8rem;
  height: 0.8rem;
}

.fee-amount {
  font-weight: 700;
  color: var(--theme-danger-text);
  font-family: Monaco, Menlo, monospace;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.status-active {
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
}

.status-left {
  background: var(--theme-warning-soft);
  color: var(--theme-warning-text);
}

.actions {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.action-btn {
  min-height: 34px;
  border-radius: 10px;
  border: 1px solid transparent;
  padding: 0.35rem 0.55rem;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.76rem;
  font-weight: 700;
  cursor: pointer;
}

.action-icon {
  width: 0.84rem;
  height: 0.84rem;
}

.edit-btn {
  background: var(--theme-info-soft);
  border-color: var(--theme-info-border);
  color: var(--theme-info-text);
}

.delete-btn {
  background: var(--theme-danger-soft);
  border-color: var(--theme-danger-border);
  color: var(--theme-danger-text);
}

.mobile-view {
  display: none;
  margin-top: 0.8rem;
  gap: 0.58rem;
}

.mobile-card {
  border-radius: 14px;
  padding: 0.68rem;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.mobile-row {
  margin-top: 0.58rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.row-label {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.footer-row {
  align-items: flex-end;
}

.empty-state {
  margin-top: 0.85rem;
  border-radius: 16px;
  padding: 1.1rem;
  text-align: center;
}

.empty-icon {
  width: 1.9rem;
  height: 1.9rem;
  color: var(--theme-brand-pill-text);
}

.empty-state h3 {
  margin: 0.55rem 0 0;
}

.empty-state p {
  margin: 0.4rem 0 0;
  color: var(--text-secondary);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1400;
  background: var(--theme-overlay);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6rem 1rem 1rem 17rem;
}

.modal-content {
  width: min(980px, 90%);
  max-height: min(90vh, 980px);
  border-radius: 16px;
  padding: 0rem 2rem;
  overflow-y: scroll;
}

.modal-head {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--theme-panel-solid);
  border-bottom: 1px solid var(--theme-border-soft);
}

.modal-head h3 {
  margin: 0;
  font-size: 1rem;
}

.modal-close {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid var(--theme-input-border);
  background: var(--theme-surface-soft-heavy);
  color: var(--theme-text-primary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.modal-close-icon {
  width: 0.94rem;
  height: 0.94rem;
}

.modal-body {
  padding: 0.75rem;
}

@keyframes mesh-drift {
  0% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  100% {
    transform: translate3d(-1.5%, 1.2%, 0) scale(1.04);
  }
}

@media (max-width: 1080px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .quick-stats {
    width: 100%;
  }

  .filters-row {
    grid-template-columns: 1fr;
  }

  .modal-overlay {
    padding: 5rem 1rem 0rem 1rem;
  }

  .modal-content {
    width: 100%;
    max-height: 80vh;
    /* padding: 5rem 1rem 5rem 1rem; */
    margin: 0rem 0rem 5rem 0rem;
  }
}

@media (max-width: 920px) {
  .desktop-view {
    display: none;
  }

  .mobile-view {
    display: grid;
  }
}

@media (max-width: 767px) {
  .student-list-page {
    padding-top: 2rem;
    padding-bottom: 5rem;
    padding-inline: 1rem;
  }

  .section-shell {
    width: min(1240px, calc(100% - 1rem));
  }

  .quick-stats {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .modal-content {
    width: 100%;
    max-height: 80vh;
    padding-inline: 0rem;
  }
}
</style>
