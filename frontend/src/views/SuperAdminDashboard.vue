<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Superadmin Dashboard</h1>
      <router-link to="/superadmin/notifications">
        <button class="notify-link-btn">Notification Center</button>
      </router-link>
    </div>

    <!-- Create Library Form -->
    <section class="create-form">
      <h2>➕ Create New Library</h2>
      <form @submit.prevent="createLibrary">
        <input v-model="newLibrary.name" placeholder="Library Name" required />
        <input v-model="newLibrary.max_seats" type="number" placeholder="Max Seats" required />
        <input v-model="newLibrary.contact_email" type="email" placeholder="Email" />
        <input v-model="newLibrary.contact_phone" placeholder="Phone" />
        <input type="text" v-model="newLibrary.address" placeholder="Address">
        <button type="submit">Create</button>
      </form>
    </section>

    <!-- Libraries Table -->
    <section class="library-table">
      <h2>📚 Libraries</h2>
      <button @click="loadLibraries">🔁 Refresh</button>
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
            <td>{{ lib.contact_email }}</td>
            <td>{{ lib.contact_phone }}</td>
            <td>
              <router-link :to="`/superadmin/library/${lib.id}/students`">
                <button>👁️ View Students</button>
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </section>


    <!-- Create Admin Form -->
<section class="create-form">
  <h2>➕ Create New Admin</h2>
  <form @submit.prevent="createAdmin">
    <input v-model="newAdmin.username" placeholder="Username" required />
    <input v-model="newAdmin.password" type="password" placeholder="Password" required />

    <select v-model="newAdmin.library_id" required>
      <option disabled value="">Select Library</option>
      <option v-for="lib in libraries" :key="lib.id" :value="lib.id">
        {{ lib.name }} (ID: {{ lib.id }})
      </option>
    </select>

    <button type="submit">Create Admin</button>
  </form>
</section>


    <!-- Admins Table -->
    <section class="admin-table" >
      <h2>Admins</h2>
      <button @click="loadAdmins">🔁 Refresh</button>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
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
            <td>{{ admin.role }}</td>
            <td>{{ admin.library_id || '—' }}</td>
            <td>{{ admin.status }}</td>
            <td>
              <select v-model="admin.newStatus">
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="blocked">Blocked</option>
              </select>
              <button @click="confirmStatusChange(admin)" :disabled="admin.status === admin.newStatus">Change</button>
              <button @click="deleteAdmin(admin.id)">Delete</button>
            </td>
            
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script>
import API from '../api'

export default {
  name: 'SuperAdminDashboard',
  data() {
    return {
      libraries: [],
      admins: [],
      newAdmin: {
        username: '',
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
  methods: {

    async createAdmin() {
      try {
        const payload = {
          username: this.newAdmin.username,
          password: this.newAdmin.password,
          library_id: parseInt(this.newAdmin.library_id)
        };
        await API.post('/superadmin/admins', payload);
        this.loadAdmins();
        this.newAdmin = { username: '', password: '', library_id: '' };
        alert('Admin created successfully!');
      } catch (err) {
        alert('Failed to create admin');
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
        const res = await API.get('/superadmin/admins');
        this.admins = res.data.map(admin => ({
          ...admin,
          newStatus: admin.status // For UI selection
        }));
      } catch (err) {
        alert('Failed to load admins');
      }
    },
    async confirmStatusChange(admin) {
      if (!confirm(`Are you sure you want to change status of '${admin.username}' to '${admin.newStatus}'?`)) return;

      try {
        await API.patch(`/superadmin/admins/${admin.id}/status`, null, {
          params: { status: admin.newStatus }
        });
        alert('Status updated successfully');
        this.loadAdmins(); // Refresh table
      } catch (err) {
        alert('Failed to update status: ' + (err.response?.data?.detail || err.message));
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
        this.newLibrary = { name: '', max_seats: '', contact_email: '', contact_phone: '' }
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
    }
  },
  mounted() {
    this.loadLibraries()
    this.loadAdmins()
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 3vh auto;
  padding: 2rem;
  font-family: "Segoe UI", sans-serif;
  background-color: rgb(244, 247, 250 , 0.3) ;
  color: #333;
  ;
}

h1 {
  font-size: 2rem;
  margin-bottom: 0;
  color: #2c3e50;
}

.dashboard-header {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.notify-link-btn {
  border: none;
  border-radius: 8px;
  background-color: #4f46e5;
  color: #fff;
  padding: 0.65rem 1rem;
  font-weight: 600;
}

h2 {
  margin-top: 1rem;
  font-size: 1.5rem;
  color: #34495e;
  border-bottom: 2px solid #ddd;
  padding-bottom: 0.5rem;
}

.create-form {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 10px;
  margin-top: 1rem;
  box-shadow: 0 4px 8px rgba(0,0,0,0.05);
}

.create-form form {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.create-form input,
.create-form select {
  flex: 1 1 200px;
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
  background-color: #fefefe;
}

.create-form button {
  padding: 0.75rem 1.5rem;
  background-color: #8725d3;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.3s;
}

.create-form button:hover {
  background-color: #8725d3;
}

section {
  margin-top: 2rem;
}

button {
  cursor: pointer;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  background-color: #fff;
  border-radius: 8px;
  overflow:scroll;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

table thead {
  background-color: #34495e;
  color: #fff;
}

table th,
table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

table tbody tr:hover {
  background-color: #f1f1f1;
}

select {
  padding: 0.5rem;
  border-radius: 5px;
  border: 1px solid #ccc;
}

td select {
  min-width: 120px;
}

td button {
  margin-left: 0.5rem;
  padding: 0.4rem 0.8rem;
  border-radius: 5px;
  border: none;
  background-color: #2980b9;
  color: white;
  font-size: 0.9rem;
  transition: background 0.3s;
}

td button:hover {
  background-color: #1c6ea4;
}

@media(max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: stretch;
  }

  .notify-link-btn {
    width: 100%;
  }

  .library-table table {
    overflow-x: auto;
    display: block;
    margin: 30px 0px 30px 0px;
  }

  .admin-table table {
    overflow-x: auto;
    display: block;
  }

  td button {
    margin-left: 0;
    margin-top: 0.5rem;
    display: block;
    width: 100%;
  }

  .create-form form{
    display: flex;
    flex-direction: row;

  }
  form button {
    width: 100%;
    font-size: 1rem;
  }
}
</style>
