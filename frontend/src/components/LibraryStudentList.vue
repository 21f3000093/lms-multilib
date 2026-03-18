<template>
  <main class="library-students-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="section-shell hero">
      <div>
        <p class="kicker">Superadmin View</p>
        <h1>
          Library
          <span class="gradient-text">Students</span>
        </h1>
        <p class="hero-subtitle">
          {{ libraryName || `Library ID ${libraryId}` }}
          <span v-if="libraryName" class="library-id">(ID: {{ libraryId }})</span>
        </p>
      </div>

      <div class="hero-actions">
        <button class="btn btn-ghost" type="button" @click="$router.back()">
          <ArrowLeft class="btn-icon" aria-hidden="true" />
          <span>Back</span>
        </button>
      </div>
    </section>

    <section class="section-shell quick-stats">
      <article class="glass-card stat-card">
        <p class="stat-label">Total Students</p>
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
    </section>

    <section class="section-shell glass-card filters-card">
      <div class="search-wrap">
        <Search class="search-icon" aria-hidden="true" />
        <input
          v-model="searchTerm"
          type="text"
          class="search-input"
          placeholder="Search by name, contact, or seat"
        />
      </div>

      <div class="filters-row">
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

    <section v-if="loading" class="section-shell glass-card loading-card">
      <div class="loader"></div>
      <p>Loading students...</p>
    </section>

    <section v-else-if="errorMessage" class="section-shell glass-card empty-state">
      <Users class="empty-icon" aria-hidden="true" />
      <h3>Unable to load students</h3>
      <p>{{ errorMessage }}</p>
      <button class="btn btn-solid" type="button" @click="loadData">Retry</button>
    </section>

    <section v-else-if="filteredStudents.length > 0" class="section-shell table-shell glass-card desktop-view">
      <div class="table-wrap">
        <table class="student-table">
          <thead>
            <tr>
              <th>Student</th>
              <th>Contact</th>
              <th>Seat</th>
              <th>Shifts</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in filteredStudents" :key="student.id" class="student-row">
              <td>
                <router-link :to="`/students/${student.id}`" class="student-link">
                  <span class="avatar">{{ student.name.charAt(0).toUpperCase() }}</span>
                  <div>
                    <p class="name">{{ student.name }}</p>
                    <p class="id-text">ID: {{ student.id }}</p>
                  </div>
                </router-link>
              </td>
              <td>
                <span class="contact-pill">
                  <Phone class="inline-icon" aria-hidden="true" />
                  {{ student.contact || 'N/A' }}
                </span>
              </td>
              <td>
                <span v-if="student.seat?.seat_number" class="seat-pill">
                  <Armchair class="inline-icon" aria-hidden="true" />
                  {{ student.seat.seat_number }}
                </span>
                <span v-else class="muted">Not assigned</span>
              </td>
              <td>
                <div class="shift-pills">
                  <span class="shift-pill" :class="{ active: !!student.shift1, inactive: !student.shift1 }">
                    <Sunrise class="shift-icon" aria-hidden="true" />
                    <span>S1</span>
                  </span>
                  <span class="shift-pill" :class="{ active: !!student.shift2, inactive: !student.shift2 }">
                    <Sun class="shift-icon" aria-hidden="true" />
                    <span>S2</span>
                  </span>
                  <span class="shift-pill" :class="{ active: !!student.shift3, inactive: !student.shift3 }">
                    <MoonStar class="shift-icon" aria-hidden="true" />
                    <span>S3</span>
                  </span>
                </div>
              </td>
              <td>
                <span class="status-pill" :class="student.status === 'active' ? 'status-active' : 'status-left'">
                  {{ formatStatus(student.status) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-else-if="!loading" class="section-shell glass-card empty-state">
      <Users class="empty-icon" aria-hidden="true" />
      <h3>No Students Found</h3>
      <p v-if="searchTerm || statusFilter">Try adjusting filters.</p>
      <p v-else>No students are registered in this library yet.</p>
    </section>

    <section v-if="!loading && filteredStudents.length > 0" class="section-shell mobile-view">
      <article v-for="student in filteredStudents" :key="student.id" class="glass-card mobile-card">
        <header class="card-head">
          <router-link :to="`/students/${student.id}`" class="student-link">
            <span class="avatar">{{ student.name.charAt(0).toUpperCase() }}</span>
            <div>
              <p class="name">{{ student.name }}</p>
              <p class="id-text">ID: {{ student.id }}</p>
            </div>
          </router-link>
          <span class="status-pill" :class="student.status === 'active' ? 'status-active' : 'status-left'">
            {{ formatStatus(student.status) }}
          </span>
        </header>

        <div class="mobile-row">
          <p class="row-label">Contact</p>
          <span class="contact-pill">
            <Phone class="inline-icon" aria-hidden="true" />
            {{ student.contact || 'N/A' }}
          </span>
        </div>

        <div class="mobile-row">
          <p class="row-label">Seat</p>
          <span v-if="student.seat?.seat_number" class="seat-pill">
            <Armchair class="inline-icon" aria-hidden="true" />
            {{ student.seat.seat_number }}
          </span>
          <span v-else class="muted">Not assigned</span>
        </div>

        <div class="mobile-row">
          <p class="row-label">Shifts</p>
          <div class="shift-pills">
            <span class="shift-pill" :class="{ active: !!student.shift1, inactive: !student.shift1 }">S1</span>
            <span class="shift-pill" :class="{ active: !!student.shift2, inactive: !student.shift2 }">S2</span>
            <span class="shift-pill" :class="{ active: !!student.shift3, inactive: !student.shift3 }">S3</span>
          </div>
        </div>
      </article>
    </section>
  </main>
</template>

<script>
import {
  Armchair,
  ArrowLeft,
  Filter,
  MoonStar,
  Phone,
  Search,
  Sun,
  Sunrise,
  Users,
} from 'lucide-vue-next'
import API from '../api'

export default {
  name: 'LibraryStudentsView',
  components: {
    Armchair,
    ArrowLeft,
    Filter,
    MoonStar,
    Phone,
    Search,
    Sun,
    Sunrise,
    Users,
  },
  data() {
    return {
      students: [],
      libraryName: '',
      loading: false,
      errorMessage: '',
      searchTerm: '',
      statusFilter: '',
    }
  },
  computed: {
    libraryId() {
      return this.$route.params.library_id
    },
    activeCount() {
      return this.students.filter((student) => student.status === 'active').length
    },
    leftCount() {
      return this.students.filter((student) => student.status === 'left').length
    },
    filteredStudents() {
      const query = this.searchTerm.trim().toLowerCase()

      return this.students.filter((student) => {
        const statusMatches = !this.statusFilter || student.status === this.statusFilter

        const searchable = [
          student.name,
          student.contact,
          String(student.seat?.seat_number ?? ''),
        ]
          .join(' ')
          .toLowerCase()

        const searchMatches = !query || searchable.includes(query)
        return statusMatches && searchMatches
      })
    },
  },
  mounted() {
    this.loadData()
  },
  watch: {
    libraryId() {
      this.loadData()
    },
  },
  methods: {
    async loadData() {
      this.loading = true
      this.errorMessage = ''

      try {
        const [studentsRes, libraryRes] = await Promise.all([
          API.get(`/superadmin/libraries/${this.libraryId}/students`),
          API.get(`/superadmin/libraries/${this.libraryId}`),
        ])

        this.students = Array.isArray(studentsRes.data) ? studentsRes.data : []
        this.libraryName = libraryRes?.data?.name || ''
      } catch (err) {
        this.students = []
        this.errorMessage = err?.response?.data?.detail || 'Please try again in a moment.'
      } finally {
        this.loading = false
      }
    },
    formatStatus(status) {
      if (!status) return 'Unknown'
      return status.charAt(0).toUpperCase() + status.slice(1)
    },
  },
}
</script>

<style scoped>
.library-students-page {
  --surface: var(--theme-surface);
  --surface-border: var(--theme-surface-border);
  --text-primary: var(--theme-text-primary);
  --text-secondary: var(--theme-text-secondary);

  position: relative;
  min-height: 100vh;
  padding: 2rem 2rem 2.8rem;
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
  width: min(1140px, calc(100% - 2rem));
  margin: 0 auto;
}

.hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 1.5rem;
}

.kicker {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.74rem;
  font-weight: 600;
  color: var(--theme-brand-pill-text);
}

.hero h1 {
  margin: 0.4rem 0 0;
  font-size: clamp(2rem, 3.8vw, 3rem);
  line-height: 1.1;
}

.gradient-text {
  background: linear-gradient(135deg, var(--theme-brand-a), var(--theme-brand-b));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-subtitle {
  margin: 0.8rem 0 0;
  color: var(--text-secondary);
  font-size: 1rem;
}

.library-id {
  color: var(--theme-text-info);
}

.hero-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.quick-stats {
  margin-top: 1.4rem;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.9rem;
}

.glass-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  border-radius: 1rem;
  backdrop-filter: blur(12px);
  box-shadow: var(--theme-shadow-soft);
}

.stat-card {
  padding: 1rem 1.2rem;
  text-align: left;
}

.stat-label {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.stat-value {
  margin: 0.35rem 0 0;
  font-size: clamp(1.5rem, 2.4vw, 2rem);
  font-weight: 700;
}

.filters-card {
  margin-top: 1.1rem;
  padding: 1rem;
}

.search-wrap {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 0.9rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  color: var(--theme-text-muted);
}

.search-input {
  width: 100%;
  border-radius: 0.78rem;
  border: 1px solid var(--theme-input-border);
  background: var(--theme-input-bg);
  color: var(--text-primary);
  padding: 0.7rem 0.9rem 0.7rem 2.4rem;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.search-input::placeholder {
  color: var(--theme-input-placeholder);
}

.search-input:focus {
  border-color: var(--theme-brand-border);
  box-shadow: 0 0 0 3px var(--theme-brand-ring);
}

.filters-row {
  margin-top: 0.8rem;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.8rem;
}

.filter-item {
  display: grid;
  gap: 0.35rem;
  text-align: left;
  color: var(--theme-text-soft);
  font-size: 0.82rem;
}

.filter-select {
  min-width: 180px;
  border-radius: 0.7rem;
  border: 1px solid var(--theme-input-border);
  background: var(--theme-input-bg);
  color: var(--theme-text-primary);
  padding: 0.6rem 0.8rem;
}

.results-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  border-radius: 999px;
  border: 1px solid var(--theme-info-border);
  background: var(--theme-info-soft);
  color: var(--theme-info-text);
  padding: 0.42rem 0.72rem;
  font-size: 0.82rem;
  white-space: nowrap;
}

.chip-icon {
  width: 0.88rem;
  height: 0.88rem;
}

.table-shell {
  margin-top: 1rem;
  overflow: hidden;
}

.table-wrap {
  overflow-x: auto;
}

.student-table {
  width: 100%;
  min-width: 860px;
  border-collapse: collapse;
}

.student-table th,
.student-table td {
  padding: 0.9rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--theme-border-soft);
}

.student-table th {
  color: var(--theme-text-soft);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 600;
}

.student-row:hover {
  background: var(--theme-surface-soft);
}

.student-link {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  color: inherit;
  text-decoration: none;
}

.avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--theme-brand-on);
  background: linear-gradient(135deg, var(--theme-brand-a), var(--theme-brand-b));
  box-shadow: inset 0 0 0 1px var(--theme-border-soft);
}

.name {
  margin: 0;
  font-weight: 600;
}

.id-text {
  margin: 0.1rem 0 0;
  font-size: 0.78rem;
  color: var(--theme-text-secondary);
}

.contact-pill,
.seat-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border-radius: 999px;
  padding: 0.35rem 0.65rem;
  font-size: 0.78rem;
  white-space: nowrap;
}

.contact-pill {
  color: var(--theme-info-text);
  background: var(--theme-info-soft);
}

.seat-pill {
  color: var(--theme-success-text);
  background: var(--theme-success-soft);
}

.inline-icon {
  width: 0.82rem;
  height: 0.82rem;
}

.shift-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.shift-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  border-radius: 999px;
  padding: 0.26rem 0.56rem;
  border: 1px solid transparent;
}

.shift-pill.active {
  color: var(--theme-brand-pill-text);
  border-color: var(--theme-brand-border);
  background: var(--theme-brand-soft);
}

.shift-pill.inactive {
  color: var(--theme-text-muted);
  border-color: var(--theme-border);
  background: var(--theme-panel);
}

.shift-icon {
  width: 0.74rem;
  height: 0.74rem;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  padding: 0.34rem 0.72rem;
  font-size: 0.76rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.status-active {
  color: var(--theme-success-text);
  background: var(--theme-success-soft);
  border: 1px solid var(--theme-success-border);
}

.status-left {
  color: var(--theme-danger-text);
  background: var(--theme-danger-soft);
  border: 1px solid var(--theme-danger-border);
}

.mobile-view {
  display: none;
  margin-top: 1rem;
  gap: 0.9rem;
}

.mobile-card {
  padding: 1rem;
  text-align: left;
}

.card-head {
  display: flex;
  justify-content: space-between;
  gap: 0.7rem;
}

.mobile-row {
  margin-top: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
}

.row-label {
  margin: 0;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--theme-text-secondary);
}

.empty-state,
.loading-card {
  margin-top: 1.1rem;
  padding: 1.8rem 1.2rem;
  text-align: center;
}

.empty-state h3,
.loading-card p {
  margin: 0.7rem 0 0;
}

.empty-state p {
  margin: 0.6rem 0 0;
  color: var(--theme-text-secondary);
}

.empty-icon {
  width: 2rem;
  height: 2rem;
  color: var(--theme-brand-pill-text);
}

.loader {
  width: 2rem;
  height: 2rem;
  margin: 0 auto;
  border-radius: 999px;
  border: 2px solid var(--theme-border);
  border-top-color: var(--theme-brand-a);
  animation: spin 0.8s linear infinite;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  border-radius: 0.78rem;
  border: 1px solid transparent;
  padding: 0.6rem 0.92rem;
  font-size: 0.83rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background-color 0.18s ease, border-color 0.18s ease;
}

.btn:active {
  transform: translateY(1px);
}

.btn-solid {
  color: var(--theme-brand-on);
  background: linear-gradient(135deg, var(--theme-brand-a), var(--theme-brand-b));
  box-shadow: var(--theme-shadow-elevated);
}

.btn-ghost {
  color: var(--theme-text-primary);
  border-color: var(--theme-border-strong);
  background: var(--theme-panel);
}

.btn:hover {
  transform: translateY(-1px);
}

.btn-icon {
  width: 0.95rem;
  height: 0.95rem;
}

.muted {
  color: var(--theme-text-secondary);
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

@media (max-width: 1080px) {
  .library-students-page {
    padding: 1.5rem 1rem 2.1rem;
  }

  .section-shell {
    width: min(100%, calc(100% - 0.4rem));
  }

  .hero {
    flex-direction: column;
    align-items: stretch;
  }

  .hero-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 860px) {
  .quick-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-select {
    width: 100%;
    min-width: 0;
  }

  .results-chip {
    justify-content: center;
  }

  .desktop-view {
    display: none;
  }

  .mobile-view {
    display: grid;
  }
}

@media (max-width: 560px) {
  .quick-stats {
    grid-template-columns: 1fr;
  }

  .student-link {
    gap: 0.55rem;
  }

  .avatar {
    width: 1.84rem;
    height: 1.84rem;
    font-size: 0.82rem;
  }

  .status-pill {
    font-size: 0.72rem;
  }
}
</style>
