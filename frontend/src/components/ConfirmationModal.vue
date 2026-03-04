<template>
  <div v-if="show" class="modal-overlay" @click="onCancel">
    <div class="modal-content" @click.stop>
      <header class="modal-header">
        <h3>{{ title }}</h3>
        <button type="button" class="close-btn" @click="onCancel" aria-label="Close">×</button>
      </header>

      <div class="modal-body">
        <p>{{ message }}</p>
      </div>

      <footer class="modal-footer">
        <button type="button" @click="onConfirm" class="btn btn-whatsapp">WhatsApp</button>
        <button type="button" @click="onSMS" class="btn btn-sms">SMS</button>
        <button type="button" @click="onCancel" class="btn btn-secondary">{{ cancelText }}</button>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    show: Boolean,
    title: { type: String, default: 'Confirmation' },
    message: String,
    cancelText: { type: String, default: 'Cancel' },
  },
  emits: ['whatsapp', 'sms', 'cancel'],
  methods: {
    onConfirm() {
      this.$emit('whatsapp')
    },
    onSMS() {
      this.$emit('sms')
    },
    onCancel() {
      this.$emit('cancel')
    },
  },
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1600;
  background: rgba(2, 6, 23, 0.72);
  backdrop-filter: blur(5px);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.75rem;
}

.modal-content {
  width: min(520px, 100%);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(15, 23, 42, 0.92);
  color: #e2e8f0;
  box-shadow: 0 24px 48px rgba(2, 6, 23, 0.45);
}

.modal-header {
  padding: 0.85rem 0.9rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(148, 163, 184, 0.22);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.02rem;
  font-weight: 700;
}

.close-btn {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.32);
  background: rgba(148, 163, 184, 0.12);
  color: #e2e8f0;
  font-size: 1rem;
  cursor: pointer;
}

.modal-body {
  padding: 0.9rem;
}

.modal-body p {
  margin: 0;
  color: #cbd5e1;
  line-height: 1.6;
}

.modal-footer {
  padding: 0 0.9rem 0.9rem;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.5rem;
}

.btn {
  min-height: 40px;
  border-radius: 11px;
  border: 1px solid transparent;
  font-weight: 700;
  cursor: pointer;
  color: #fff;
}

.btn-whatsapp {
  background: linear-gradient(90deg, #22c55e, #16a34a);
}

.btn-sms {
  background: linear-gradient(90deg, #0ea5e9, #3b82f6);
}

.btn-secondary {
  background: rgba(148, 163, 184, 0.16);
  border-color: rgba(148, 163, 184, 0.35);
  color: #e2e8f0;
}

@media (max-width: 600px) {
  .modal-content {
    border-radius: 14px;
  }

  .modal-footer {
    grid-template-columns: 1fr;
  }
}
</style>
