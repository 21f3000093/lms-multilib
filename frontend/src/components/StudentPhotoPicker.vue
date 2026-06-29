<template>
  <section class="photo-section">
    <header class="photo-header">
      <h2>Student Photo</h2>
      <span v-if="uploading" class="uploading-chip">
        <LoaderCircle class="chip-spinner" aria-hidden="true" />
        Uploading
      </span>
    </header>

    <div class="photo-content">
      <div class="photo-preview-wrap" :style="previewStyle">
        <img
          v-if="currentPreview && !imageFailed"
          :src="currentPreview"
          :alt="`${studentName || 'Student'} profile photo`"
          class="photo-preview"
          loading="lazy"
          @error="imageFailed = true"
        />
        <span v-else class="photo-placeholder">{{ initial }}</span>
        <button
          class="change-overlay"
          type="button"
          :disabled="disabled || uploading"
          @click="openFileDialog"
        >
          Change Photo
        </button>
      </div>

      <div class="photo-actions">
        <button type="button" class="photo-btn" :disabled="disabled || uploading || cameraActive" @click="startCamera">
          <Camera class="photo-btn-icon" aria-hidden="true" />
          <span>Take Photo</span>
        </button>
        <button type="button" class="photo-btn" :disabled="disabled || uploading" @click="openFileDialog">
          <ImagePlus class="photo-btn-icon" aria-hidden="true" />
          <span>Upload Photo</span>
        </button>
        <button type="button" class="photo-btn danger" :disabled="disabled || uploading || !hasPhoto" @click="removePhoto">
          <Trash2 class="photo-btn-icon" aria-hidden="true" />
          <span>Remove Photo</span>
        </button>
      </div>
    </div>

    <div v-if="cameraActive" class="camera-panel">
      <video ref="cameraVideo" class="camera-video" autoplay playsinline muted></video>
      <div class="camera-actions">
        <button type="button" class="photo-btn solid" @click="capturePhoto">
          <Aperture class="photo-btn-icon" aria-hidden="true" />
          <span>Capture</span>
        </button>
        <button type="button" class="photo-btn" @click="stopCamera">
          <X class="photo-btn-icon" aria-hidden="true" />
          <span>Cancel</span>
        </button>
      </div>
    </div>

    <input
      ref="fileInput"
      type="file"
      accept="image/jpeg,image/png,image/webp"
      class="sr-only"
      @change="handleFileInput"
    />
  </section>
</template>

<script>
import {
  Aperture,
  Camera,
  ImagePlus,
  LoaderCircle,
  Trash2,
  X,
} from 'lucide-vue-next'
import {
  compressStudentPhoto,
  createPreviewUrl,
  revokePreviewUrl,
} from '../utils/studentPhotos'

export default {
  name: 'StudentPhotoPicker',
  components: {
    Aperture,
    Camera,
    ImagePlus,
    LoaderCircle,
    Trash2,
    X,
  },
  props: {
    photoUrl: {
      type: String,
      default: '',
    },
    studentName: {
      type: String,
      default: '',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    uploading: {
      type: Boolean,
      default: false,
    },
    size: {
      type: Number,
      default: 124,
    },
  },
  emits: ['selected', 'removed', 'error'],
  data() {
    return {
      localPreviewUrl: '',
      imageFailed: false,
      cameraStream: null,
      cameraActive: false,
    }
  },
  computed: {
    currentPreview() {
      return this.localPreviewUrl || this.photoUrl || ''
    },
    hasPhoto() {
      return Boolean(this.currentPreview)
    },
    initial() {
      return (this.studentName || 'Student').trim().charAt(0).toUpperCase() || 'S'
    },
    previewStyle() {
      return {
        '--photo-size': `${this.size}px`,
        '--photo-font-size': `${Math.max(28, Math.round(this.size * 0.38))}px`,
      }
    },
  },
  watch: {
    photoUrl() {
      this.imageFailed = false
    },
  },
  beforeUnmount() {
    this.stopCamera()
    this.clearLocalPreview()
  },
  methods: {
    openFileDialog() {
      if (this.disabled || this.uploading) return
      this.$refs.fileInput?.click()
    },

    async handleFileInput(event) {
      const [file] = event.target.files || []
      event.target.value = ''
      if (!file) return
      await this.processFile(file)
    },

    async processFile(file) {
      try {
        const compressedFile = await compressStudentPhoto(file)
        this.setLocalPreview(compressedFile)
        this.$emit('selected', compressedFile)
      } catch (error) {
        this.$emit('error', error?.message || 'Could not prepare the photo.')
      }
    },

    setLocalPreview(file) {
      this.clearLocalPreview()
      this.imageFailed = false
      this.localPreviewUrl = createPreviewUrl(file)
    },

    clearLocalPreview() {
      revokePreviewUrl(this.localPreviewUrl)
      this.localPreviewUrl = ''
    },

    restorePrevious() {
      this.clearLocalPreview()
      this.imageFailed = false
    },

    commitPreview() {
      this.clearLocalPreview()
      this.imageFailed = false
    },

    removePhoto() {
      this.clearLocalPreview()
      this.imageFailed = false
      this.$emit('removed')
    },

    async startCamera() {
      if (!navigator.mediaDevices?.getUserMedia) {
        this.$emit('error', 'Camera is not available in this browser.')
        return
      }

      try {
        this.cameraStream = await navigator.mediaDevices.getUserMedia({
          audio: false,
          video: {
            facingMode: 'user',
            width: { ideal: 640 },
            height: { ideal: 640 },
          },
        })
        this.cameraActive = true
        await this.$nextTick()
        if (this.$refs.cameraVideo) {
          this.$refs.cameraVideo.srcObject = this.cameraStream
          await this.$refs.cameraVideo.play()
        }
      } catch (error) {
        this.stopCamera()
        this.$emit('error', 'Camera permission was denied or the camera could not be opened.')
      }
    },

    capturePhoto() {
      const video = this.$refs.cameraVideo
      if (!video?.videoWidth || !video?.videoHeight) {
        this.$emit('error', 'Camera is still starting. Please try again.')
        return
      }

      const sourceSize = Math.min(video.videoWidth, video.videoHeight)
      const sourceX = (video.videoWidth - sourceSize) / 2
      const sourceY = (video.videoHeight - sourceSize) / 2
      const canvas = document.createElement('canvas')
      canvas.width = 400
      canvas.height = 400
      const context = canvas.getContext('2d')
      context.drawImage(video, sourceX, sourceY, sourceSize, sourceSize, 0, 0, 400, 400)

      canvas.toBlob(async (blob) => {
        this.stopCamera()
        if (!blob) {
          this.$emit('error', 'Could not capture the photo.')
          return
        }

        const file = new File([blob], `camera_${Date.now()}.webp`, {
          type: 'image/webp',
          lastModified: Date.now(),
        })
        await this.processFile(file)
      }, 'image/webp', 0.9)
    },

    stopCamera() {
      if (this.cameraStream) {
        this.cameraStream.getTracks().forEach((track) => track.stop())
      }
      this.cameraStream = null
      this.cameraActive = false
    },
  },
}
</script>

<style scoped>
.photo-section {
  border: 1px solid var(--theme-border-soft);
  border-radius: 14px;
  padding: 0.82rem;
  background: var(--theme-panel-soft);
}

.photo-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.photo-header h2 {
  margin: 0;
  font-size: 1.02rem;
}

.uploading-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  border-radius: 999px;
  padding: 0.22rem 0.55rem;
  background: var(--theme-brand-soft);
  color: var(--theme-brand-pill-text);
  font-size: 0.75rem;
  font-weight: 700;
}

.chip-spinner {
  width: 0.85rem;
  height: 0.85rem;
  animation: spin 0.8s linear infinite;
}

.photo-content {
  margin-top: 0.75rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.photo-preview-wrap {
  position: relative;
  width: var(--photo-size);
  height: var(--photo-size);
  border-radius: 50%;
  overflow: hidden;
  display: inline-grid;
  place-items: center;
  flex-shrink: 0;
  background: linear-gradient(135deg, var(--theme-brand-a), var(--theme-brand-b));
  color: var(--theme-brand-on);
  box-shadow: 0 14px 28px rgba(0, 0, 0, 0.16), inset 0 0 0 1px var(--theme-border-soft);
}

.photo-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.photo-placeholder {
  font-size: var(--photo-font-size);
  font-weight: 800;
}

.change-overlay {
  position: absolute;
  inset: auto 0 0;
  min-height: 38px;
  border: 0;
  background: rgba(14, 18, 32, 0.72);
  color: #fff;
  font-size: 0.74rem;
  font-weight: 800;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.18s ease, transform 0.18s ease;
  cursor: pointer;
}

.photo-preview-wrap:hover .change-overlay,
.photo-preview-wrap:focus-within .change-overlay {
  opacity: 1;
  transform: translateY(0);
}

.change-overlay:disabled {
  cursor: not-allowed;
}

.photo-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.photo-btn {
  min-height: 38px;
  border-radius: 11px;
  border: 1px solid var(--theme-border-strong);
  background: var(--theme-surface-soft-heavy);
  color: var(--theme-text-primary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.38rem;
  padding: 0.4rem 0.62rem;
  font-size: 0.8rem;
  font-weight: 800;
  cursor: pointer;
}

.photo-btn:hover:not(:disabled) {
  border-color: var(--theme-brand-border);
  color: var(--theme-brand-pill-text);
}

.photo-btn:disabled {
  opacity: 0.52;
  cursor: not-allowed;
}

.photo-btn.danger {
  border-color: var(--theme-danger-border);
  background: var(--theme-danger-soft);
  color: var(--theme-danger-text);
}

.photo-btn.solid {
  border-color: transparent;
  color: var(--theme-brand-on);
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
}

.photo-btn-icon {
  width: 0.95rem;
  height: 0.95rem;
  flex-shrink: 0;
}

.camera-panel {
  margin-top: 0.8rem;
  border-radius: 14px;
  border: 1px solid var(--theme-border);
  background: var(--theme-panel);
  padding: 0.7rem;
}

.camera-video {
  width: 100%;
  max-height: 360px;
  border-radius: 12px;
  background: #111827;
  object-fit: cover;
}

.camera-actions {
  margin-top: 0.55rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.45rem;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 680px) {
  .photo-content {
    align-items: flex-start;
    flex-direction: column;
  }

  .photo-preview-wrap {
    margin: 0 auto;
  }

  .photo-actions,
  .camera-actions {
    width: 100%;
  }

  .photo-btn {
    flex: 1 1 120px;
  }
}
</style>
