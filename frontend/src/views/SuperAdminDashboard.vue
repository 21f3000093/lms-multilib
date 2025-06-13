<template>
  <div class="dashboard">
    <h1>🛠️ Superadmin Dashboard</h1>

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
    <section>
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
          </tr>
        </thead>
        <tbody>
          <tr v-for="lib in libraries" :key="lib.id">
            <td>{{ lib.id }}</td>
            <td>{{ lib.name }}</td>
            <td>{{ lib.max_seats }}</td>
            <td>{{ lib.contact_email }}</td>
            <td>{{ lib.contact_phone }}</td>
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
    <section>
      <h2>🧑‍💼 Admins</h2>
      <button @click="loadAdmins">🔁 Refresh</button>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Role</th>
            <th>Library ID</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="admin in admins" :key="admin.id">
            <td>{{ admin.id }}</td>
            <td>{{ admin.username }}</td>
            <td>{{ admin.role }}</td>
            <td>{{ admin.library_id || '—' }}</td>
            <td>{{ admin.status }}</td>
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
        const res = await API.get('/superadmin/admins')
        this.admins = res.data
      } catch (err) {
        alert('Failed to load admins')
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
  padding: 2rem;
}

h1, h2 {
  margin-bottom: 0.75rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 2rem;
  font-size: 0.95rem;
}

th, td {
  border: 1px solid #ccc;
  padding: 8px 12px;
  text-align: left;
}

th {
  background-color: #f4f4f4;
}

button {
  margin-bottom: 1rem;
  padding: 6px 12px;
  font-size: 0.9rem;
  cursor: pointer;
}

.create-form form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 2rem;
}

.create-form input {
  padding: 6px 10px;
  font-size: 0.9rem;
  flex: 1 1 200px;
}
</style>
