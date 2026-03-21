export const storeAdminSession = (admin) => {
  if (!admin) {
    return
  }

  localStorage.setItem('role', admin.role || '')
  localStorage.setItem('username', admin.username || '')
  localStorage.setItem('library_id', admin.library_id ?? '')
  localStorage.setItem('library_name', admin.library?.name || '')
}

export const clearAdminSession = () => {
  localStorage.removeItem('role')
  localStorage.removeItem('username')
  localStorage.removeItem('library_id')
  localStorage.removeItem('library_name')
}

export const homeRouteForRole = (role) => (role === 'superadmin' ? '/superadmin' : '/dashboard')
