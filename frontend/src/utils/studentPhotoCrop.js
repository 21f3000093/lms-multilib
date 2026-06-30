export const STUDENT_PHOTO_CROP_SIZE = 400
export const STUDENT_PHOTO_CROP_QUALITY = 0.92

export function buildCroppedPhotoName(originalName = 'student-photo') {
  const cleanBase = originalName
    .replace(/\.[^.]+$/, '')
    .replace(/[^A-Za-z0-9._-]/g, '_')
    .slice(0, 80) || 'student-photo'

  return `${cleanBase}_cropped.webp`
}

export function canvasToWebpFile(canvas, originalName) {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          reject(new Error('Could not generate the cropped photo. Please try again.'))
          return
        }

        resolve(new File(
          [blob],
          buildCroppedPhotoName(originalName),
          {
            type: 'image/webp',
            lastModified: Date.now(),
          }
        ))
      },
      'image/webp',
      STUDENT_PHOTO_CROP_QUALITY
    )
  })
}

export function canvasToBlob(canvas, type = 'image/webp', quality = STUDENT_PHOTO_CROP_QUALITY) {
  return new Promise((resolve, reject) => {
    canvas.toBlob((blob) => {
      if (!blob) {
        reject(new Error('Could not capture the photo.'))
        return
      }
      resolve(blob)
    }, type, quality)
  })
}
