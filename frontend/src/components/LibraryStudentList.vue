<template>
  <div class="library-students-page">
    <h2>👨‍🎓 Students of {{ libraryName || `Library ID ${libraryId}` }}</h2>
    <h3>Total Students: {{ students.length }}</h3>

    <button @click="$router.back()">🔙 Back</button>

    <table v-if="students.length">
      <thead>
        <tr>
          <th>Name</th>
          <th>Contact</th>
          <th>Seat</th>
          <th>Shifts</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="s in students" :key="s.id">
          <td>{{ s.name }}</td>
          <td>{{ s.contact }}</td>
          <td>{{ s.seat?.seat_number || '—' }}</td>
          <td>
            <span v-if="s.shift1">1 </span>
            <span v-if="s.shift2">2 </span>
            <span v-if="s.shift3">3</span>
          </td>
          <td>{{ s.status }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else>🙁 No students found.</p>
  </div>
</template>

<script>
import API from '../api'

export default {
  name: 'LibraryStudentsView',
  data() {
    return {
      students: [],
      libraryName: '',
    }
  },
  computed: {
    libraryId() {
      return this.$route.params.library_id
    }
  },
  async mounted() {
    try {
      const res = await API.get(`/superadmin/libraries/${this.libraryId}/students`)
      this.students = res.data

      const lib = await API.get(`/superadmin/libraries/${this.libraryId}`)
      this.libraryName = lib.data.name
    } catch (err) {
      alert('Error loading students')
    }
  }
}
</script>

<style scoped>
.library-students-page {
  padding-top: 5rem;
  height: 90vh;
  overflow-y: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
th, td {
  border: 1px solid #ccc;
  padding: 8px;
}
th {
  background-color: #f9f9f9;
}
button {
  /* margin-bottom: 1rem; */
  padding: 0.5rem 1rem;
  background-color: #8725d3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  width: 30%;
}
</style>
