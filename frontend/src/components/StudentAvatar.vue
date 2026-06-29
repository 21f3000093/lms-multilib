<template>
  <span
    class="student-avatar"
    :class="{ clickable }"
    :style="avatarStyle"
    role="img"
    :aria-label="avatarLabel"
    @click="$emit('click')"
  >
    <img
      v-if="resolvedPhotoUrl && !imageFailed"
      :src="resolvedPhotoUrl"
      :alt="avatarLabel"
      loading="lazy"
      @error="imageFailed = true"
    />
    <span v-else class="avatar-initial">{{ initial }}</span>
  </span>
</template>

<script>
export default {
  name: 'StudentAvatar',
  props: {
    student: {
      type: Object,
      default: null,
    },
    photoUrl: {
      type: String,
      default: '',
    },
    name: {
      type: String,
      default: '',
    },
    size: {
      type: Number,
      default: 40,
    },
    clickable: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['click'],
  data() {
    return {
      imageFailed: false,
    }
  },
  computed: {
    resolvedPhotoUrl() {
      return this.photoUrl || this.student?.photo_url || ''
    },
    resolvedName() {
      return this.name || this.student?.name || this.student?.student_name || 'Student'
    },
    initial() {
      return this.resolvedName.trim().charAt(0).toUpperCase() || 'S'
    },
    avatarLabel() {
      return `${this.resolvedName} profile photo`
    },
    avatarStyle() {
      return {
        '--avatar-size': `${this.size}px`,
        '--avatar-font-size': `${Math.max(13, Math.round(this.size * 0.38))}px`,
      }
    },
  },
  watch: {
    resolvedPhotoUrl() {
      this.imageFailed = false
    },
  },
}
</script>

<style scoped>
.student-avatar {
  width: var(--avatar-size);
  height: var(--avatar-size);
  border-radius: 50%;
  display: inline-grid;
  place-items: center;
  overflow: hidden;
  flex-shrink: 0;
  background: linear-gradient(135deg, var(--theme-brand-a), var(--theme-brand-b));
  color: var(--theme-brand-on);
  box-shadow: inset 0 0 0 1px var(--theme-border-soft);
}

.student-avatar.clickable {
  cursor: pointer;
}

.student-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.avatar-initial {
  font-size: var(--avatar-font-size);
  font-weight: 800;
  line-height: 1;
}
</style>
