<!-- ConfirmationModal.vue -->
<template>
  <div v-if="show" class="modal-overlay" @click="onCancel">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>{{ title }}</h3>
        <!-- <button @click="onCancel" class="close-btn">&times;</button> -->
      </div>
      <div class="modal-body">
        <p>{{ message }}</p>
      </div>
      <div class="modal-footer">
        <button @click="onConfirm" class="btn btn-whatsapp">WhatsApp</button>
        <button @click="onSMS" class="btn btn-sms">SMS</button>
        <button @click="onCancel" class="btn btn-secondary">{{ cancelText }}</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    show: Boolean,
    title: { type: String, default: 'Confirmation' },
    message: String,
    cancelText: { type: String, default: 'Cancel' }
  },
  methods: {
    onConfirm() {
      this.$emit('whatsapp');
    },
    onSMS() {
      this.$emit('sms');
    },
    onCancel() {
      this.$emit('cancel');
    }
  }
}
</script>

<style scoped>
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
  max-width: 400px;
  width: 90%;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-footer {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  width: 30%;
  
}
.btn:hover {  
  transform: scale(1.03);  
}

.btn-whatsapp { background: #1b9648; color: white; }
.btn-sms { background: #007bff; color: white; }
.btn-secondary { background: #6c757d; color: white; }

@media(max-width: 786px){

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
  max-width: 90%;
  width: 85%;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  height: auto;
}

.modal-body p {
  font-size: 1.1rem;
  
}

.modal-footer {
  display: flex;
  flex-direction: column;
  gap: 10px;
  justify-content: center;
  margin-top: 20px;
}

.btn {
  padding: 12px 16px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: bold;
  font-size: medium;
  width: 70%;
  margin: auto;
  
}
.btn:hover {  
  transform: scale(1.03);  
}

    
}



</style>
