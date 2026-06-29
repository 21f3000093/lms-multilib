import imageCompression from 'browser-image-compression'
import API from '../api'

export const MAX_STUDENT_PHOTO_BYTES = 10 * 1024 * 1024
export const ALLOWED_STUDENT_PHOTO_TYPES = ['image/jpeg', 'image/png', 'image/webp']

const COMPRESSION_OPTIONS = {
  maxSizeMB: 0.1,
  maxWidthOrHeight: 400,
  useWebWorker: true,
  fileType: 'image/webp',
  initialQuality: 0.8,
}

const EXTENSION_PATTERN = /\.(jpe?g|png|webp)$/i

export function validateStudentPhotoFile(file) {
  if (!file) {
    throw new Error('Please select an image file.')
  }

  if (!ALLOWED_STUDENT_PHOTO_TYPES.includes(file.type)) {
    throw new Error('Only JPG, PNG, and WebP images are allowed.')
  }

  if (!EXTENSION_PATTERN.test(file.name || 'photo.webp')) {
    throw new Error('Only JPG, PNG, and WebP images are allowed.')
  }

  if (file.size > MAX_STUDENT_PHOTO_BYTES) {
    throw new Error('Please choose an image smaller than 10 MB.')
  }
}

function buildWebpName(originalName = 'student-photo') {
  const cleanBase = originalName
    .replace(/\.[^.]+$/, '')
    .replace(/[^A-Za-z0-9._-]/g, '_')
    .slice(0, 80) || 'student-photo'

  return `${cleanBase}.webp`
}

export async function compressStudentPhoto(file) {
  validateStudentPhotoFile(file)

  try {
    const compressedBlob = await imageCompression(file, COMPRESSION_OPTIONS)
    return new File(
      [compressedBlob],
      buildWebpName(file.name),
      {
        type: 'image/webp',
        lastModified: Date.now(),
      }
    )
  } catch (error) {
    throw new Error(error?.message || 'Could not compress the image. Please try another photo.')
  }
}

export function createPreviewUrl(file) {
  return URL.createObjectURL(file)
}

export function revokePreviewUrl(previewUrl) {
  if (previewUrl && previewUrl.startsWith('blob:')) {
    URL.revokeObjectURL(previewUrl)
  }
}

export async function uploadStudentPhoto(file, studentId) {
  if (!studentId) {
    throw new Error('Student must be saved before uploading a photo.')
  }

  const formData = new FormData()
  formData.append('student_id', studentId)
  formData.append('file', file, file.name || 'student-photo.webp')

  const response = await API.post('/upload/student-photo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

  return response.data?.photo_url
}

export async function deleteStudentPhoto(photoUrl) {
  if (!photoUrl) return false
  const response = await API.delete('/upload/student-photo', {
    data: { photo_url: photoUrl },
  })
  return Boolean(response.data?.deleted)
}
