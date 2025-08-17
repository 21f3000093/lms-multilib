<template>
  <div v-if="show" class="modal-overlay" @click="onCancel">
    <div class="modal-content seat-details-modal" @click.stop>
      <div class="modal-header">
        <h2>Seat Number: {{ seatData?.seat_number || 'Details' }}</h2>
        <!-- <button @click="onCancel" class="close-btn">&times;</button> -->
      </div>
      <div class="modal-body">
        <div v-if="seatData" class="shift-details">
          <div 
            v-for="shift in seatData.shifts" 
            :key="shift.shift" 
            class="shift-row"
            :class="{ 'occupied': shift.is_occupied, 'empty': !shift.is_occupied }"
          >
            <div class="shift-info">
              <span class="shift-label">{{ shift.shift_name }} (Shift {{ shift.shift }})</span>
              <span class="student-name">{{ shift.student_name }}</span>
            </div>
            <div class="status-indicator">
              {{ shift.is_occupied ? '✅' : '❌' }}
            </div>
          </div>
        </div>
        <div v-else class="loading">
          Loading seat details...
        </div>
      </div>
      <div class="modal-footer">
        <button @click="onCancel" class="btn btn-secondary">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    show: Boolean,
    seatData: Object
  },
  methods: {
    onCancel() {
      this.$emit('close');
    }
  }
}
</script>

<style scoped>
.seat-details-modal {
  max-width: 450px;
  width: 90%;
}

.modal-header {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.shift-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.shift-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  border: 2px solid #e9ecef;
}

.shift-row.occupied {
  background-color: #d4edda;
  border-color: #c3e6cb;
}

.shift-row.empty {
  background-color: #f8d7da;
  border-color: #f1b0b7;
}

.shift-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.shift-label {
  font-weight: bold;
  color: #495057;
  font-size: 14px;
}

.student-name {
  font-size: 16px;
  color: #212529;
  text-transform: uppercase;
  font-weight: 500;
}

.status-indicator {
  font-size: 20px;
}

.modal-footer {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 15px 24px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 500;
  font-size: medium;
  width: 90%;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.loading {
  text-align: center;
  padding: 20px;
  color: #6c757d;
}



/* Mobile Responsive */
@media(max-width: 786px) {
  .seat-details-modal {
    max-width: 80%;
    margin: 15px;
  }
  .modal-header{
    margin-bottom: 0px;
    /* padding-bottom: 5px; */
  }
  
  .shift-row {
    padding: 10px;
  }
  
  .shift-label {
    font-size: 13px;
  }
  
  .student-name {
    font-size: 15px;
  }
}

/* Common modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-height: 90vh;
  overflow-y: auto;
}
</style>
