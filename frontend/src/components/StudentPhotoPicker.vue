<template>
  <section class="photo-section">
    <header class="photo-header">
      <h2>Student Photo</h2>
      <span v-if="showProgress" class="uploading-chip" :class="{ failed: uploadFailed }">
        <LoaderCircle v-if="uploading && !uploadFailed" class="chip-spinner" aria-hidden="true" />
        <span>{{ activeStatus }}</span>
        <strong>{{ activeProgress }}%</strong>
      </span>
    </header>

    <div v-if="showProgress" class="progress-track" :class="{ failed: uploadFailed }">
      <span class="progress-fill" :style="{ width: activeProgress + '%' }"></span>
    </div>

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
          :disabled="isBusy"
          aria-label="Change student photo"
          @click="openFileDialog"
        >
          Change Photo
        </button>
      </div>

      <div class="photo-actions">
        <button type="button" class="photo-btn" :disabled="isBusy || cameraActive" aria-label="Take photo" @click="startCamera">
          <Camera class="photo-btn-icon" aria-hidden="true" />
          <span>Take Photo</span>
        </button>
        <button type="button" class="photo-btn" :disabled="isBusy" aria-label="Upload photo" @click="openFileDialog">
          <ImagePlus class="photo-btn-icon" aria-hidden="true" />
          <span>Upload Photo</span>
        </button>
        <button
          v-if="uploadFailed && preparedPhotoFile"
          type="button"
          class="photo-btn warning"
          :disabled="disabled || uploading"
          aria-label="Retry photo upload"
          @click="retryPreparedPhoto"
        >
          <RefreshCw class="photo-btn-icon" aria-hidden="true" />
          <span>Retry</span>
        </button>
        <button type="button" class="photo-btn danger" :disabled="isBusy || !hasPhoto" aria-label="Remove photo" @click="removePhoto">
          <Trash2 class="photo-btn-icon" aria-hidden="true" />
          <span>Remove Photo</span>
        </button>
      </div>
    </div>

    <div v-if="cameraActive" class="camera-panel">
      <div class="camera-card">
        <video ref="cameraVideo" class="camera-video" autoplay playsinline muted></video>
        <div v-if="countdownValue" class="countdown-badge" aria-live="assertive">{{ countdownValue }}</div>
        <div v-if="cameraFlash" class="camera-flash" aria-hidden="true"></div>
      </div>

      <div class="camera-actions">
        <button type="button" class="photo-btn solid" :disabled="capturePending" aria-label="Capture photo" @click="capturePhoto">
          <Aperture class="photo-btn-icon" aria-hidden="true" />
          <span>{{ capturePending ? 'Capturing...' : 'Capture' }}</span>
        </button>
        <button type="button" class="photo-btn" :disabled="capturePending" aria-label="Switch camera" @click="switchCamera">
          <RefreshCw class="photo-btn-icon" aria-hidden="true" />
          <span>{{ cameraFacingMode === 'user' ? 'Rear Camera' : 'Front Camera' }}</span>
        </button>
        <button
          type="button"
          class="photo-btn"
          :class="{ active: countdownEnabled }"
          :disabled="capturePending"
          aria-label="Toggle camera countdown"
          @click="toggleCountdown"
        >
          <Timer class="photo-btn-icon" aria-hidden="true" />
          <span>Timer {{ countdownEnabled ? 'On' : 'Off' }}</span>
        </button>
        <button type="button" class="photo-btn" :disabled="capturePending" aria-label="Cancel camera" @click="stopCamera">
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

    <StudentPhotoCropper
      v-if="cropperOpen"
      :show="cropperOpen"
      :source-url="cropSourceUrl"
      :source-name="cropSourceName"
      @save="handleCropSave"
      @cancel="cancelCrop"
      @error="handleCropError"
    />
  </section>
</template>

<script>
import { defineAsyncComponent } from 'vue'
import {
  Aperture,
  Camera,
  ImagePlus,
  LoaderCircle,
  RefreshCw,
  Timer,
  Trash2,
  X,
} from 'lucide-vue-next'
import {
  compressStudentPhoto,
  createPreviewUrl,
  revokePreviewUrl,
  validateStudentPhotoFile,
} from '../utils/studentPhotos'
import { canvasToBlob } from '../utils/studentPhotoCrop'

const CAMERA_FACING_STORAGE_KEY = 'student_photo_camera_facing'
const CAMERA_TIMER_STORAGE_KEY = 'student_photo_camera_timer'

export default {
  name: 'StudentPhotoPicker',
  components: {
    Aperture,
    Camera,
    ImagePlus,
    LoaderCircle,
    RefreshCw,
    StudentPhotoCropper: defineAsyncComponent(() => import('./StudentPhotoCropper.vue')),
    Timer,
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
  emits: ['selected', 'removed', 'error', 'retry'],
  data() {
    return {
      localPreviewUrl: '',
      cropSourceUrl: '',
      cropSourceName: 'student-photo',
      cropperOpen: false,
      preparedPhotoFile: null,
      imageFailed: false,
      cameraStream: null,
      cameraActive: false,
      cameraFacingMode: localStorage.getItem(CAMERA_FACING_STORAGE_KEY) || 'user',
      countdownEnabled: localStorage.getItem(CAMERA_TIMER_STORAGE_KEY) === 'true',
      countdownValue: null,
      capturePending: false,
      cameraFlash: false,
      progressStatus: '',
      progressValue: 0,
      uploadFailed: false,
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
    isBusy() {
      return this.disabled || this.uploading || this.cropperOpen
    },
    activeStatus() {
      if (this.uploadFailed) return 'Upload failed. Retry available.'
      if (this.uploading) return 'Uploading to cloud...'
      return this.progressStatus
    },
    activeProgress() {
      if (this.uploadFailed) return 100
      if (this.uploading) return Math.max(this.progressValue, 85)
      return this.progressValue
    },
    showProgress() {
      return Boolean(this.activeStatus)
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
    this.clearCropSource()
  },
  methods: {
    openFileDialog() {
      if (this.isBusy) return
      this.$refs.fileInput?.click()
    },

    async handleFileInput(event) {
      const [file] = event.target.files || []
      event.target.value = ''
      if (!file) return
      await this.openCropperForFile(file)
    },

    async openCropperForFile(file) {
      try {
        validateStudentPhotoFile(file)
        this.clearCropSource()
        this.progressStatus = 'Preparing image...'
        this.progressValue = 18
        this.cropSourceName = file.name || 'student-photo.webp'
        this.cropSourceUrl = createPreviewUrl(file)
        this.cropperOpen = true
      } catch (error) {
        this.resetProgress()
        this.$emit('error', error?.message || 'This image cannot be used.')
      }
    },

    async handleCropSave(croppedFile) {
      this.cropperOpen = false
      this.clearCropSource()
      await this.processCroppedFile(croppedFile)
    },

    cancelCrop() {
      this.cropperOpen = false
      this.clearCropSource()
      this.resetProgress()
    },

    handleCropError(message) {
      this.$emit('error', message || 'Could not crop the photo.')
    },

    async processCroppedFile(file) {
      try {
        this.progressStatus = 'Compressing image...'
        this.progressValue = 54
        const compressedFile = await compressStudentPhoto(file)
        this.preparedPhotoFile = compressedFile
        this.setLocalPreview(compressedFile)
        this.progressStatus = 'Ready to upload'
        this.progressValue = 100
        this.$emit('selected', compressedFile)
      } catch (error) {
        this.progressStatus = 'Compression failed'
        this.progressValue = 100
        this.$emit('error', error?.message || 'Could not compress the photo.')
      }
    },

    setLocalPreview(file) {
      this.clearLocalPreview()
      this.imageFailed = false
      this.uploadFailed = false
      this.localPreviewUrl = createPreviewUrl(file)
    },

    clearLocalPreview() {
      revokePreviewUrl(this.localPreviewUrl)
      this.localPreviewUrl = ''
    },

    clearCropSource() {
      revokePreviewUrl(this.cropSourceUrl)
      this.cropSourceUrl = ''
    },

    restorePrevious() {
      if (this.localPreviewUrl && this.preparedPhotoFile) {
        this.uploadFailed = true
        this.progressStatus = ''
        this.progressValue = 100
        return
      }

      this.clearLocalPreview()
      this.resetPreparedState()
      this.imageFailed = false
    },

    commitPreview() {
      this.clearLocalPreview()
      this.resetPreparedState()
      this.imageFailed = false
    },

    resetPreparedState() {
      this.preparedPhotoFile = null
      this.uploadFailed = false
      this.resetProgress()
    },

    resetProgress() {
      this.progressStatus = ''
      this.progressValue = 0
    },

    retryPreparedPhoto() {
      if (!this.preparedPhotoFile) return
      this.uploadFailed = false
      this.progressStatus = 'Retrying upload...'
      this.progressValue = 100
      this.$emit('selected', this.preparedPhotoFile)
      this.$emit('retry')
    },

    removePhoto() {
      this.clearLocalPreview()
      this.resetPreparedState()
      this.imageFailed = false
      this.$emit('removed')
    },

    async startCamera() {
      if (!navigator.mediaDevices?.getUserMedia) {
        this.$emit('error', 'Camera is not available in this browser.')
        return
      }

      try {
        this.stopCamera()
        this.cameraStream = await navigator.mediaDevices.getUserMedia({
          audio: false,
          video: {
            facingMode: { ideal: this.cameraFacingMode },
            width: { ideal: 960 },
            height: { ideal: 960 },
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
        this.$emit('error', this.getCameraErrorMessage(error))
      }
    },

    async switchCamera() {
      if (this.capturePending) return
      this.cameraFacingMode = this.cameraFacingMode === 'user' ? 'environment' : 'user'
      localStorage.setItem(CAMERA_FACING_STORAGE_KEY, this.cameraFacingMode)
      if (this.cameraActive) {
        await this.startCamera()
      }
    },

    toggleCountdown() {
      this.countdownEnabled = !this.countdownEnabled
      localStorage.setItem(CAMERA_TIMER_STORAGE_KEY, String(this.countdownEnabled))
    },

    async capturePhoto() {
      if (this.capturePending) return

      const video = this.$refs.cameraVideo
      if (!video?.videoWidth || !video?.videoHeight) {
        this.$emit('error', 'Camera is still starting. Please try again.')
        return
      }

      this.capturePending = true
      try {
        if (this.countdownEnabled) {
          await this.runCountdown()
        }

        const blob = await this.captureFrameBlob(video)
        await this.playFlash()
        this.stopCamera()

        const file = new File([blob], `camera_${Date.now()}.webp`, {
          type: 'image/webp',
          lastModified: Date.now(),
        })
        await this.openCropperForFile(file)
      } catch (error) {
        this.$emit('error', error?.message || 'Could not capture the photo.')
      } finally {
        this.capturePending = false
        this.countdownValue = null
      }
    },

    async captureFrameBlob(video) {
      const sourceSize = Math.min(video.videoWidth, video.videoHeight)
      const sourceX = (video.videoWidth - sourceSize) / 2
      const sourceY = (video.videoHeight - sourceSize) / 2
      const canvas = document.createElement('canvas')
      canvas.width = 400
      canvas.height = 400
      const context = canvas.getContext('2d')
      context.drawImage(video, sourceX, sourceY, sourceSize, sourceSize, 0, 0, 400, 400)

      try {
        return await canvasToBlob(canvas)
      } finally {
        canvas.width = 0
        canvas.height = 0
      }
    },

    async runCountdown() {
      for (let value = 3; value >= 1; value -= 1) {
        this.countdownValue = value
        await this.delay(700)
      }
      this.countdownValue = null
    },

    async playFlash() {
      this.cameraFlash = true
      await this.delay(140)
      this.cameraFlash = false
    },

    delay(ms) {
      return new Promise((resolve) => {
        setTimeout(resolve, ms)
      })
    },

    stopCamera() {
      if (this.cameraStream) {
        this.cameraStream.getTracks().forEach((track) => track.stop())
      }
      if (this.$refs.cameraVideo) {
        this.$refs.cameraVideo.srcObject = null
      }
      this.cameraStream = null
      this.cameraActive = false
      this.countdownValue = null
      this.cameraFlash = false
    },

    getCameraErrorMessage(error) {
      if (error?.name === 'NotAllowedError' || error?.name === 'PermissionDeniedError') {
        return 'Camera permission was denied. Please allow camera access and try again.'
      }
      if (error?.name === 'NotFoundError' || error?.name === 'DevicesNotFoundError') {
        return 'No camera was found on this device.'
      }
      if (error?.name === 'NotReadableError' || error?.name === 'TrackStartError') {
        return 'Camera is already in use by another app.'
      }
      return 'Camera could not be opened. Please try upload instead.'
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

.uploading-chip.failed {
  background: var(--theme-danger-soft);
  color: var(--theme-danger-text);
}

.chip-spinner {
  width: 0.85rem;
  height: 0.85rem;
  animation: spin 0.8s linear infinite;
}

.progress-track {
  margin-top: 0.62rem;
  height: 7px;
  border-radius: 999px;
  overflow: hidden;
  background: var(--theme-surface-soft-heavy);
}

.progress-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
  transition: width 0.24s ease;
}

.progress-track.failed .progress-fill {
  background: var(--theme-danger-text);
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
  transition: border-color 0.16s ease, transform 0.16s ease;
}

.photo-btn:hover:not(:disabled) {
  border-color: var(--theme-brand-border);
  color: var(--theme-brand-pill-text);
}

.photo-btn:active:not(:disabled) {
  transform: translateY(1px);
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

.photo-btn.warning,
.photo-btn.active {
  border-color: var(--theme-warning-border);
  background: var(--theme-warning-soft);
  color: var(--theme-warning-text);
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
  border-radius: 16px;
  border: 1px solid var(--theme-border);
  background: var(--theme-panel);
  padding: 0.7rem;
}

.camera-card {
  position: relative;
  overflow: hidden;
  border-radius: 16px;
  background: #111827;
}

.camera-video {
  width: 100%;
  max-height: 430px;
  min-height: 260px;
  display: block;
  object-fit: cover;
}

.countdown-badge {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  color: #fff;
  font-size: clamp(3rem, 13vw, 6rem);
  font-weight: 900;
  background: rgba(17, 24, 39, 0.24);
}

.camera-flash {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.9);
  animation: camera-flash 0.16s ease-out;
}

.camera-actions {
  margin-top: 0.65rem;
  display: flex;
  flex-wrap: wrap;
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

button:focus-visible,
input:focus-visible {
  outline: 3px solid var(--theme-brand-ring);
  outline-offset: 2px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes camera-flash {
  from {
    opacity: 1;
  }
  to {
    opacity: 0;
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
    flex: 1 1 132px;
  }
}
</style>
