<template>
  <main class="superadmin-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="section-shell hero">
      <div>
        <p class="kicker">Superadmin Control Panel</p>
        <h1>
          Multi-library
          <span class="gradient-text">Operations Hub</span>
        </h1>
        <p class="hero-subtitle">
          Create libraries, onboard admins, and monitor account status from a single secured workspace.
        </p>
      </div>

      <div class="hero-actions">
        <router-link to="/superadmin/notifications" class="btn btn-solid">Notification Center</router-link>
        <button class="btn btn-ghost" type="button" @click="refreshAll">Refresh Data</button>
      </div>
    </section>

    <section class="section-shell quick-stats">
      <article class="stat-card glass-card">
        <p class="stat-label">Libraries</p>
        <p class="stat-value">{{ libraries.length }}</p>
      </article>
      <article class="stat-card glass-card">
        <p class="stat-label">Admins</p>
        <p class="stat-value">{{ admins.length }}</p>
      </article>
      <article class="stat-card glass-card">
        <p class="stat-label">Active Admins</p>
        <p class="stat-value">{{ activeAdmins }}</p>
      </article>
    </section>

    <section class="section-shell forms-grid">
      <article class="glass-card form-card">
        <header class="card-header">
          <h2>Create Library</h2>
          <p>Provision a new library workspace with seat capacity.</p>
        </header>

        <form class="grid-form" @submit.prevent="createLibrary">
          <input v-model="newLibrary.name" placeholder="Library Name" required />
          <input v-model="newLibrary.max_seats" type="number" min="1" placeholder="Max Seats" required />
          <input v-model="newLibrary.contact_email" type="email" placeholder="Email" />
          <input v-model="newLibrary.contact_phone" placeholder="Phone" />
          <input v-model="newLibrary.address" type="text" placeholder="Address" />
          <button type="submit" class="btn btn-solid full-width">Create Library</button>
        </form>
      </article>

      <article class="glass-card form-card">
        <header class="card-header">
          <h2>Create Admin</h2>
          <p>Assign a library and create login credentials for the admin.</p>
        </header>

        <form class="grid-form" @submit.prevent="createAdmin">
          <input v-model="newAdmin.username" placeholder="Username" required />
          <input v-model="newAdmin.email" type="email" placeholder="Email (optional)" />
          <input v-model="newAdmin.password" type="password" placeholder="Password" required />

          <select v-model="newAdmin.library_id" required>
            <option disabled value="">Select Library</option>
            <option v-for="lib in libraries" :key="lib.id" :value="lib.id">
              {{ lib.name }} (ID: {{ lib.id }})
            </option>
          </select>

          <button type="submit" class="btn btn-solid full-width">Create Admin</button>
        </form>
      </article>
    </section>

    <section class="section-shell table-grid">
      <article class="glass-card table-card">
        <header class="table-head">
          <div>
            <h2>Libraries</h2>
            <p>List of all registered libraries.</p>
          </div>
          <button class="btn btn-ghost" type="button" @click="loadLibraries">Refresh</button>
        </header>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Max Seats</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="lib in libraries" :key="lib.id">
                <td>{{ lib.id }}</td>
                <td>{{ lib.name }}</td>
                <td>{{ lib.max_seats }}</td>
                <td>{{ lib.contact_email || '—' }}</td>
                <td>{{ lib.contact_phone || '—' }}</td>
                <td>
                  <div class="library-actions">
                    <button class="btn btn-ghost tiny" type="button" @click="openEditLibraryModal(lib)">
                      Edit
                    </button>
                    <router-link :to="`/superadmin/library/${lib.id}/students`" class="inline-link">
                      View Students
                    </router-link>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <article class="glass-card table-card">
        <header class="table-head">
          <div>
            <h2>Admins</h2>
            <p>Manage admin account status and access.</p>
          </div>
          <button class="btn btn-ghost" type="button" @click="loadAdmins">Refresh</button>
        </header>

        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>Library ID</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="admin in admins" :key="admin.id">
                <td>{{ admin.id }}</td>
                <td>{{ admin.username }}</td>
                <td>{{ admin.email || '—' }}</td>
                <td>{{ admin.role }}</td>
                <td>{{ admin.library_id || '—' }}</td>
                <td>
                  <span class="status-pill" :class="`status-${admin.status}`">{{ admin.status }}</span>
                </td>
                <td>
                  <div class="admin-actions">
                    <select v-model="admin.newStatus">
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                      <option value="blocked">Blocked</option>
                    </select>
                    <button class="btn btn-ghost tiny" @click="confirmStatusChange(admin)" :disabled="admin.status === admin.newStatus">
                      Change
                    </button>
                    <button class="btn btn-danger tiny" @click="deleteAdmin(admin.id)">Delete</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>
    </section>

    <div v-if="editingLibrary" class="modal-overlay" @click.self="closeEditLibraryModal">
      <section class="glass-card modal-content">
        <header class="modal-head">
          <div>
            <h2>Edit Library</h2>
            <p>Update the library name and contact details.</p>
          </div>
          <button class="modal-close" type="button" @click="closeEditLibraryModal" aria-label="Close edit library modal">
            ×
          </button>
        </header>

        <form class="modal-form" @submit.prevent="submitEditLibrary">
          <label class="field-block">
            <span class="field-label">Library Name</span>
            <input v-model="editLibraryForm.name" class="field-input" type="text" required />
          </label>

          <label class="field-block">
            <span class="field-label">Email</span>
            <input v-model="editLibraryForm.contact_email" class="field-input" type="email" />
          </label>

          <label class="field-block">
            <span class="field-label">Phone Number</span>
            <input v-model="editLibraryForm.contact_phone" class="field-input" type="text" />
          </label>

          <label class="field-block">
            <span class="field-label">Address</span>
            <textarea v-model="editLibraryForm.address" class="field-input field-textarea" rows="3"></textarea>
          </label>

          <div class="modal-actions">
            <button class="btn btn-ghost" type="button" @click="closeEditLibraryModal" :disabled="savingLibrary">
              Cancel
            </button>
            <button class="btn btn-solid" type="submit" :disabled="savingLibrary">
              {{ savingLibrary ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </section>
    </div>
  </main>
</template>

<script>
import API from '../api'

export default {
  name: 'SuperAdminDashboard',
  data() {
    return {
      libraries: [],
      admins: [],
      editingLibrary: null,
      savingLibrary: false,
      editLibraryForm: {
        id: null,
        name: '',
        contact_email: '',
        contact_phone: '',
        address: ''
      },
      newAdmin: {
        username: '',
        email: '',
        password: '',
        library_id: ''
      },
      newLibrary: {
        name: '',
        max_seats: '',
        contact_email: '',
        contact_phone: '',
        address: ''
      }
    }
  },
  computed: {
    activeAdmins() {
      return this.admins.filter((admin) => admin.status === 'active').length
    }
  },
  methods: {
    openEditLibraryModal(library) {
      this.editingLibrary = library
      this.editLibraryForm = {
        id: library.id,
        name: library.name || '',
        contact_email: library.contact_email || '',
        contact_phone: library.contact_phone || '',
        address: library.address || ''
      }
    },

    closeEditLibraryModal() {
      this.editingLibrary = null
      this.savingLibrary = false
      this.editLibraryForm = {
        id: null,
        name: '',
        contact_email: '',
        contact_phone: '',
        address: ''
      }
    },

    async submitEditLibrary() {
      if (!this.editLibraryForm.id) return

      try {
        this.savingLibrary = true
        const payload = {
          name: this.editLibraryForm.name.trim(),
          contact_email: this.editLibraryForm.contact_email.trim() || null,
          contact_phone: this.editLibraryForm.contact_phone.trim() || null,
          address: this.editLibraryForm.address.trim() || null
        }

        await API.patch(`/superadmin/libraries/${this.editLibraryForm.id}`, payload)
        await this.loadLibraries()
        this.closeEditLibraryModal()
        alert('Library details updated successfully!')
      } catch (err) {
        alert('Failed to update library: ' + (err.response?.data?.detail || err.message))
      } finally {
        this.savingLibrary = false
      }
    },

    async createAdmin() {
      try {
        const payload = {
          username: this.newAdmin.username,
          email: this.newAdmin.email || null,
          password: this.newAdmin.password,
          library_id: parseInt(this.newAdmin.library_id)
        }
        await API.post('/superadmin/admins', payload)
        this.loadAdmins()
        this.newAdmin = { username: '', email: '', password: '', library_id: '' }
        alert('Admin created successfully!')
      } catch (err) {
        alert('Failed to create admin')
      }
    },

    async loadLibraries() {
      try {
        const res = await API.get('/superadmin/libraries')
        this.libraries = res.data
      } catch (err) {
        alert('Failed to load libraries')
      }
    },

    async loadAdmins() {
      try {
        const res = await API.get('/superadmin/admins')
        this.admins = res.data.map(admin => ({
          ...admin,
          newStatus: admin.status
        }))
      } catch (err) {
        alert('Failed to load admins')
      }
    },

    async confirmStatusChange(admin) {
      if (!confirm(`Are you sure you want to change status of '${admin.username}' to '${admin.newStatus}'?`)) return

      try {
        await API.patch(`/superadmin/admins/${admin.id}/status`, null, {
          params: { status: admin.newStatus }
        })
        alert('Status updated successfully')
        this.loadAdmins()
      } catch (err) {
        alert('Failed to update status: ' + (err.response?.data?.detail || err.message))
      }
    },

    async createLibrary() {
      try {
        const payload = {
          name: this.newLibrary.name,
          max_seats: parseInt(this.newLibrary.max_seats),
          contact_email: this.newLibrary.contact_email,
          contact_phone: this.newLibrary.contact_phone,
          address: this.newLibrary.address
        }
        await API.post('/superadmin/libraries', payload)
        this.loadLibraries()
        this.newLibrary = { name: '', max_seats: '', contact_email: '', contact_phone: '', address: '' }
        alert('Library created successfully!')
      } catch (err) {
        alert('Failed to create library')
      }
    },

    async deleteAdmin(id) {
      if (confirm('Are you sure you want to delete this admin?')) {
        try {
          await API.delete(`/superadmin/admins/${id}`)
          this.loadAdmins()
        } catch (err) {
          alert('Failed to delete admin')
        }
      }
    },

    async refreshAll() {
      await Promise.all([this.loadLibraries(), this.loadAdmins()])
    }
  },
  mounted() {
    this.refreshAll()
  }
}
</script>

<style scoped>
.superadmin-page {
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
  max-width: 60ch;
}

.hero-actions {
  display: inline-flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.glass-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.quick-stats {
  margin-top: 1.2rem;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.7rem;
}

.stat-card {
  border-radius: 14px;
  padding: 0.85rem;
}

.stat-label {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.stat-value {
  margin: 0.45rem 0 0;
  font-size: 1.6rem;
  font-weight: 800;
}

.forms-grid {
  margin-top: 1rem;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.8rem;
}

.form-card,
.table-card {
  border-radius: 16px;
  padding: 1rem;
  overflow: auto;
}

.card-header h2,
.table-head h2 {
  margin: 0;
  font-size: 1.2rem;
}

.card-header p,
.table-head p {
  margin: 0.45rem 0 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.grid-form {
  margin-top: 0.7rem;
  display: grid;
  gap: 0.58rem;
}

.grid-form input,
.grid-form select {
  width: 95%;
  border: 1px solid var(--theme-input-border);
  border-radius: 12px;
  background: var(--theme-input-bg);
  color: var(--theme-text-strong);
  font-size: 0.95rem;
  padding: 0.7rem 0.75rem;
  outline: none;
}

.grid-form input:focus,
.grid-form select:focus {
  border-color: var(--theme-brand-border);
  box-shadow: 0 0 0 3px var(--theme-brand-ring);
}

.grid-form select option {
  color: var(--theme-text-strong);
}

.table-grid {
  margin-top: 0.9rem;
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.8rem;
}

.table-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.7rem;
  margin-bottom: 0.7rem;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 680px;
}

thead th {
  text-align: left;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--theme-text-soft);
  border-bottom: 1px solid var(--theme-border);
  padding: 0.65rem 0.55rem;
}

tbody td {
  padding: 0.65rem 0.55rem;
  border-bottom: 1px solid var(--theme-border-soft);
  color: var(--theme-text-primary);
  font-size: 0.9rem;
}

tbody tr:hover {
  background: var(--theme-surface-soft);
}

.inline-link {
  color: var(--theme-brand-pill-text);
  text-decoration: none;
  font-weight: 600;
}

.inline-link:hover {
  text-decoration: underline;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: capitalize;
}

.status-active {
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
}

.status-inactive {
  background: var(--theme-warning-soft);
  color: var(--theme-warning-text);
}

.status-blocked {
  background: var(--theme-danger-soft);
  color: var(--theme-danger-text);
}

.admin-actions {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  flex-wrap: wrap;
}

.library-actions {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  flex-wrap: wrap;
}

.admin-actions select {
  border: 1px solid var(--theme-input-border);
  border-radius: 8px;
  background: var(--theme-input-bg);
  color: var(--theme-text-primary);
  padding: 0.35rem 0.45rem;
  font-size: 0.8rem;
}

.admin-actions select option {
  color: var(--theme-text-strong);
}

.btn {
  min-height: 40px;
  border-radius: 12px;
  border: 1px solid transparent;
  padding: 0.56rem 0.8rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  white-space: nowrap;
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-solid {
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
  color: var(--theme-brand-on);
  box-shadow: var(--theme-shadow-elevated);
}

.btn-ghost {
  background: var(--theme-surface-soft-strong);
  border-color: var(--theme-border-strong);
  color: var(--theme-text-primary);
}

.btn-danger {
  background: var(--theme-danger-soft);
  border-color: var(--theme-danger-border);
  color: var(--theme-danger-text);
}

.full-width {
  width: 100%;
}

.tiny {
  min-height: 32px;
  border-radius: 8px;
  padding: 0.35rem 0.55rem;
  font-size: 0.75rem;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1200;
  background: var(--theme-overlay);
  display: grid;
  place-items: center;
  padding: 1rem;
}

.modal-content {
  width: min(560px, calc(100% - 1rem));
  border-radius: 18px;
  padding: 1rem;
}

.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.8rem;
  margin-bottom: 0.85rem;
}

.modal-head h2 {
  margin: 0;
  font-size: 1.2rem;
}

.modal-head p {
  margin: 0.45rem 0 0;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.modal-close {
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 999px;
  border: 1px solid var(--theme-border-strong);
  background: var(--theme-surface-soft-strong);
  color: var(--theme-text-primary);
  cursor: pointer;
  font-size: 1.2rem;
  line-height: 1;
}

.modal-form {
  display: grid;
  gap: 0.85rem;
}

.field-block {
  display: grid;
  gap: 0.4rem;
}

.field-label {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--theme-text-soft);
}

.field-input {
  width: 100%;
  border: 1px solid var(--theme-input-border);
  border-radius: 12px;
  background: var(--theme-input-bg);
  color: var(--theme-text-strong);
  font-size: 0.95rem;
  padding: 0.7rem 0.75rem;
  outline: none;
  box-sizing: border-box;
}

.field-input:focus {
  border-color: var(--theme-brand-border);
  box-shadow: 0 0 0 3px var(--theme-brand-ring);
}

.field-textarea {
  resize: vertical;
  min-height: 5.5rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.65rem;
  flex-wrap: wrap;
  margin-top: 0.2rem;
}

@keyframes mesh-drift {
  0% {
    transform: translate3d(0, 0, 0) scale(1);
  }
  100% {
    transform: translate3d(-1.5%, 1.2%, 0) scale(1.04);
  }
}

@media (max-width: 1024px) {
  .forms-grid {
    grid-template-columns: 1fr;
  }

  .quick-stats {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 767px) {
  .superadmin-page {
    padding-top: 2rem;
  }

  .section-shell {
    width: min(1140px, calc(100% - 1rem));
  }

  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-actions {
    width: 100%;
  }

  .hero-actions .btn {
    flex: 1;
  }

  .table-head {
    flex-direction: row;
  }
}
</style>
