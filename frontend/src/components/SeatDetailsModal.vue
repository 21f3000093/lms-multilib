<template>
  <div v-if="show" class="modal-overlay" @click="onCancel">
    <section class="modal-content" @click.stop>
      <header class="modal-header">
        <h2>Seat {{ seatData?.seat_number || 'Details' }}</h2>
        <button type="button" class="close-btn" @click="onCancel" aria-label="Close">×</button>
      </header>

      <div class="modal-body">
        <div v-if="loading" class="loading-state">
          <div class="loader"></div>
          <p>Loading seat details...</p>
        </div>

        <div v-else-if="seatData?.shifts?.length" class="shift-details">
          <article
            v-for="shift in seatData.shifts"
            :key="shift.shift"
            class="shift-row"
            :class="shift.is_occupied ? 'occupied' : 'empty'"
          >
            <div class="shift-info">
              <p class="shift-label">{{ shift.shift_name }} (Shift {{ shift.shift }})</p>
              <div class="student-line">
                <StudentAvatar
                  v-if="shift.is_occupied"
                  :name="shift.student_name"
                  :photo-url="shift.photo_url"
                  :size="34"
                />
                <p class="student-name">{{ shift.student_name || 'No student assigned' }}</p>
              </div>
            </div>
            <span class="status-pill" :class="shift.is_occupied ? 'status-occupied' : 'status-empty'">
              {{ shift.is_occupied ? 'Occupied' : 'Available' }}
            </span>
          </article>
        </div>

        <div v-else class="empty-state">
          <p>No seat details available.</p>
        </div>
      </div>

      <footer class="modal-footer">
        <button type="button" @click="onCancel" class="btn btn-secondary">Close</button>
      </footer>
    </section>
  </div>
</template>

<script>
import StudentAvatar from './StudentAvatar.vue'

export default {
  components: {
    StudentAvatar,
  },
  props: {
    show: Boolean,
    seatData: Object,
    loading: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['close'],
  methods: {
    onCancel() {
      this.$emit('close')
    },
  },
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1700;
  background: var(--theme-overlay);
  backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.75rem;
}

.modal-content {
  width: min(560px, 100%);
  max-height: min(90vh, 760px);
  overflow-y: auto;
  border-radius: 16px;
  border: 1px solid var(--theme-surface-border);
  background: var(--theme-panel-solid);
  color: var(--theme-text-primary);
  box-shadow: var(--theme-shadow-soft);
}

.modal-header {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.85rem 0.95rem;
  border-bottom: 1px solid var(--theme-border-soft);
  background: var(--theme-panel-solid);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.02rem;
  font-weight: 800;
}

.close-btn {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid var(--theme-border-strong);
  background: var(--theme-surface-soft-heavy);
  color: var(--theme-text-primary);
  font-size: 1rem;
  cursor: pointer;
}

.modal-body {
  padding: 0.9rem;
}

.shift-details {
  display: grid;
  gap: 0.55rem;
}

.shift-row {
  border: 1px solid var(--theme-border);
  border-radius: 12px;
  background: var(--theme-panel);
  padding: 0.68rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.55rem;
}

.shift-row.occupied {
  border-color: var(--theme-success-border);
  background: var(--theme-success-soft);
}

.shift-row.empty {
  border-color: var(--theme-info-border);
  background: var(--theme-info-soft);
}

.shift-info {
  min-width: 0;
}

.student-line {
  margin-top: 0.2rem;
  display: flex;
  align-items: center;
  gap: 0.45rem;
  min-width: 0;
}

.shift-label,
.student-name {
  margin: 0;
}

.shift-label {
  color: var(--theme-text-soft);
  font-size: 0.82rem;
  font-weight: 700;
}

.student-name {
  font-size: 0.9rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--theme-text-strong);
  word-break: break-word;
}

.status-pill {
  border-radius: 999px;
  padding: 0.22rem 0.55rem;
  font-size: 0.74rem;
  font-weight: 800;
  white-space: nowrap;
}

.status-occupied {
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
}

.status-empty {
  background: var(--theme-info-soft);
  color: var(--theme-info-text);
}

.loading-state,
.empty-state {
  display: grid;
  place-items: center;
  gap: 0.35rem;
  text-align: center;
  min-height: 120px;
}

.loading-state p,
.empty-state p {
  margin: 0;
  color: var(--theme-text-soft);
}

.loader {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 3px solid var(--theme-border-strong);
  border-top-color: var(--theme-brand-a);
  animation: spin 1s linear infinite;
}

.modal-footer {
  padding: 0 0.9rem 0.9rem;
  display: flex;
  justify-content: center;
}

.btn {
  min-height: 40px;
  min-width: 140px;
  border-radius: 11px;
  border: 1px solid transparent;
  font-weight: 700;
  cursor: pointer;
}

.btn-secondary {
  background: var(--theme-surface-soft-heavy);
  border-color: var(--theme-border-strong);
  color: var(--theme-text-primary);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 600px) {
  .modal-content {
    border-radius: 14px;
  }

  .shift-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
