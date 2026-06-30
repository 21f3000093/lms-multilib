<template>
  <Teleport to="body">
    <Transition name="cropper-fade">
      <div
        v-if="show"
        class="cropper-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="student-photo-cropper-title"
      >
        <section class="cropper-card" ref="dialogCard" tabindex="-1">
          <header class="cropper-header">
            <div>
              <p class="cropper-kicker">Profile Photo</p>
              <h2 id="student-photo-cropper-title">Adjust Photo</h2>
            </div>
            <button class="icon-btn" type="button" aria-label="Cancel crop" @click="cancelCrop">
              <X class="icon" aria-hidden="true" />
            </button>
          </header>

          <div class="cropper-body">
            <div class="cropper-stage">
              <img
                ref="cropImage"
                :src="sourceUrl"
                alt="Selected student photo"
                class="cropper-image"
              />
            </div>

            <aside class="preview-panel">
              <div ref="livePreview" class="live-preview" aria-label="Live circular avatar preview"></div>
              <p>Live preview</p>
            </aside>
          </div>

          <div class="cropper-controls">
            <label class="zoom-control" for="student-photo-zoom">
              <span>Zoom</span>
              <strong>{{ zoomPercent }}%</strong>
            </label>
            <input
              id="student-photo-zoom"
              v-model.number="zoomPercent"
              class="zoom-slider"
              type="range"
              min="100"
              max="300"
              step="1"
              aria-label="Zoom photo"
              @input="applyZoom"
            />

            <div class="tool-row" role="group" aria-label="Photo rotation controls">
              <button class="tool-btn" type="button" aria-label="Rotate left" @click="rotateLeft">
                <RotateCcw class="tool-icon" aria-hidden="true" />
                <span>Rotate Left</span>
              </button>
              <button class="tool-btn" type="button" aria-label="Rotate right" @click="rotateRight">
                <RotateCw class="tool-icon" aria-hidden="true" />
                <span>Rotate Right</span>
              </button>
              <button class="tool-btn" type="button" aria-label="Reset crop" @click="resetCrop">
                <RefreshCcw class="tool-icon" aria-hidden="true" />
                <span>Reset</span>
              </button>
            </div>
          </div>

          <footer class="cropper-footer">
            <button class="footer-btn ghost" type="button" @click="cancelCrop">Cancel</button>
            <button class="footer-btn ghost" type="button" @click="resetCrop">Reset</button>
            <button class="footer-btn solid" type="button" :disabled="saving" @click="saveCrop">
              <LoaderCircle v-if="saving" class="spinner" aria-hidden="true" />
              <Check v-else class="footer-icon" aria-hidden="true" />
              <span>{{ saving ? 'Saving...' : 'Save' }}</span>
            </button>
          </footer>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
import Cropper from 'cropperjs'
import 'cropperjs/dist/cropper.css'
import {
  Check,
  LoaderCircle,
  RefreshCcw,
  RotateCcw,
  RotateCw,
  X,
} from 'lucide-vue-next'
import {
  STUDENT_PHOTO_CROP_SIZE,
  canvasToWebpFile,
} from '../utils/studentPhotoCrop'

export default {
  name: 'StudentPhotoCropper',
  components: {
    Check,
    LoaderCircle,
    RefreshCcw,
    RotateCcw,
    RotateCw,
    X,
  },
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    sourceUrl: {
      type: String,
      required: true,
    },
    sourceName: {
      type: String,
      default: 'student-photo',
    },
  },
  emits: ['save', 'cancel', 'error'],
  data() {
    return {
      cropper: null,
      zoomPercent: 100,
      baseZoomRatio: 1,
      saving: false,
    }
  },
  watch: {
    show: {
      immediate: true,
      handler(isOpen) {
        if (isOpen) {
          this.$nextTick(this.initCropper)
        } else {
          this.destroyCropper()
        }
      },
    },
    sourceUrl() {
      if (this.show) {
        this.$nextTick(this.initCropper)
      }
    },
  },
  mounted() {
    window.addEventListener('keydown', this.handleKeydown)
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.handleKeydown)
    this.destroyCropper()
  },
  methods: {
    initCropper() {
      if (!this.$refs.cropImage || !this.sourceUrl) return

      this.destroyCropper()
      this.zoomPercent = 100
      this.saving = false

      this.cropper = new Cropper(this.$refs.cropImage, {
        aspectRatio: 1,
        viewMode: 1,
        dragMode: 'move',
        autoCropArea: 0.86,
        background: false,
        center: true,
        guides: false,
        modal: true,
        movable: true,
        cropBoxMovable: true,
        cropBoxResizable: true,
        responsive: true,
        restore: false,
        rotatable: true,
        scalable: false,
        toggleDragModeOnDblclick: false,
        checkOrientation: true,
        wheelZoomRatio: 0.05,
        minCropBoxWidth: 160,
        minCropBoxHeight: 160,
        preview: this.$refs.livePreview,
        ready: () => {
          const imageData = this.cropper.getImageData()
          this.baseZoomRatio = imageData.naturalWidth
            ? imageData.width / imageData.naturalWidth
            : 1
          this.zoomPercent = 100
          this.$refs.dialogCard?.focus()
        },
        zoom: (event) => {
          const nextPercent = Math.round((event.detail.ratio / this.baseZoomRatio) * 100)
          if (nextPercent < 100 || nextPercent > 300) {
            event.preventDefault()
            return
          }
          this.zoomPercent = nextPercent
        },
      })
    },

    destroyCropper() {
      if (this.cropper) {
        this.cropper.destroy()
        this.cropper = null
      }
    },

    applyZoom() {
      if (!this.cropper) return
      const targetRatio = this.baseZoomRatio * (this.zoomPercent / 100)
      this.cropper.zoomTo(targetRatio)
    },

    rotateLeft() {
      this.cropper?.rotate(-90)
    },

    rotateRight() {
      this.cropper?.rotate(90)
    },

    resetCrop() {
      if (!this.cropper) return
      this.cropper.reset()
      this.cropper.rotateTo(0)
      this.zoomPercent = 100
    },

    cancelCrop() {
      if (this.saving) return
      this.$emit('cancel')
    },

    async saveCrop() {
      if (!this.cropper || this.saving) return

      this.saving = true
      let canvas = null
      try {
        canvas = this.cropper.getCroppedCanvas({
          width: STUDENT_PHOTO_CROP_SIZE,
          height: STUDENT_PHOTO_CROP_SIZE,
          imageSmoothingEnabled: true,
          imageSmoothingQuality: 'high',
          fillColor: '#fff',
        })

        if (!canvas) {
          throw new Error('Could not crop the photo. Please try again.')
        }

        const croppedFile = await canvasToWebpFile(canvas, this.sourceName)
        this.$emit('save', croppedFile)
      } catch (error) {
        this.$emit('error', error?.message || 'Could not save the cropped photo.')
      } finally {
        if (canvas) {
          canvas.width = 0
          canvas.height = 0
        }
        this.saving = false
      }
    },

    handleKeydown(event) {
      if (!this.show) return
      if (event.key === 'Escape') {
        event.preventDefault()
        this.cancelCrop()
      }
      if (event.key === 'Enter') {
        event.preventDefault()
        this.saveCrop()
      }
    },
  },
}
</script>

<style scoped>
.cropper-overlay {
  position: fixed;
  inset: 0;
  z-index: 2300;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgba(11, 18, 32, 0.72);
  backdrop-filter: blur(10px);
}

.cropper-card {
  width: min(980px, 100%);
  max-height: min(92vh, 820px);
  overflow: hidden;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: var(--theme-panel-solid);
  color: var(--theme-text-primary);
  box-shadow: 0 26px 80px rgba(0, 0, 0, 0.34);
  outline: none;
}

.cropper-header,
.cropper-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.9rem 1rem;
}

.cropper-header {
  border-bottom: 1px solid var(--theme-border-soft);
}

.cropper-kicker {
  margin: 0;
  color: var(--theme-text-soft);
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.cropper-header h2 {
  margin: 0.18rem 0 0;
  font-size: 1.15rem;
}

.icon-btn {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  border: 1px solid var(--theme-border-strong);
  background: var(--theme-surface-soft-heavy);
  color: var(--theme-text-primary);
  display: inline-grid;
  place-items: center;
  cursor: pointer;
}

.icon,
.tool-icon,
.footer-icon {
  width: 1rem;
  height: 1rem;
}

.cropper-body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 170px;
  gap: 1rem;
  padding: 1rem;
}

.cropper-stage {
  height: min(62vh, 540px);
  min-height: 360px;
  border-radius: 16px;
  overflow: hidden;
  background: #111827;
}

.cropper-image {
  display: block;
  max-width: 100%;
}

.preview-panel {
  display: grid;
  align-content: start;
  justify-items: center;
  gap: 0.7rem;
  padding: 0.85rem;
  border-radius: 16px;
  border: 1px solid var(--theme-border-soft);
  background: var(--theme-panel);
}

.live-preview {
  width: 118px;
  height: 118px;
  overflow: hidden;
  border-radius: 50%;
  background: var(--theme-surface-soft-heavy);
  box-shadow: inset 0 0 0 1px var(--theme-border-soft);
}

.preview-panel p {
  margin: 0;
  color: var(--theme-text-soft);
  font-size: 0.8rem;
  font-weight: 700;
}

.cropper-controls {
  padding: 0 1rem 0.85rem;
  display: grid;
  gap: 0.7rem;
}

.zoom-control {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  color: var(--theme-text-soft);
  font-size: 0.82rem;
  font-weight: 800;
}

.zoom-control strong {
  color: var(--theme-text-strong);
}

.zoom-slider {
  width: 100%;
  accent-color: var(--theme-brand-a);
}

.tool-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tool-btn,
.footer-btn {
  min-height: 40px;
  border-radius: 12px;
  border: 1px solid var(--theme-border-strong);
  background: var(--theme-surface-soft-heavy);
  color: var(--theme-text-primary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.45rem 0.7rem;
  font-weight: 800;
  cursor: pointer;
  transition: transform 0.16s ease, border-color 0.16s ease, background 0.16s ease;
}

.tool-btn:hover,
.footer-btn:hover,
.icon-btn:hover {
  border-color: var(--theme-brand-border);
}

.tool-btn:active,
.footer-btn:active {
  transform: translateY(1px);
}

.cropper-footer {
  border-top: 1px solid var(--theme-border-soft);
}

.footer-btn.ghost {
  min-width: 96px;
}

.footer-btn.solid {
  min-width: 118px;
  border-color: transparent;
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
  color: var(--theme-brand-on);
}

.footer-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 1rem;
  height: 1rem;
  animation: spin 0.8s linear infinite;
}

.cropper-fade-enter-active,
.cropper-fade-leave-active {
  transition: opacity 0.18s ease;
}

.cropper-fade-enter-from,
.cropper-fade-leave-to {
  opacity: 0;
}

:deep(.cropper-view-box),
:deep(.cropper-face) {
  border-radius: 0;
}

:deep(.cropper-point),
:deep(.cropper-line) {
  background-color: var(--theme-brand-a);
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

@media (max-width: 760px) {
  .cropper-overlay {
    padding: 0;
  }

  .cropper-card {
    width: 100%;
    height: 100%;
    max-height: none;
    border-radius: 0;
    display: flex;
    flex-direction: column;
  }

  .cropper-body {
    grid-template-columns: 1fr;
    overflow-y: auto;
  }

  .cropper-stage {
    height: min(58vh, 460px);
    min-height: 300px;
  }

  .preview-panel {
    grid-template-columns: auto 1fr;
    justify-items: start;
    align-items: center;
  }

  .live-preview {
    width: 76px;
    height: 76px;
  }

  .cropper-footer {
    margin-top: auto;
  }

  .tool-btn,
  .footer-btn {
    flex: 1 1 120px;
  }
}
</style>
