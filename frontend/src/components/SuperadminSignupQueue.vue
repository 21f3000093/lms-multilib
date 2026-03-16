<template>
  <main class="queue-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="section-shell hero">
      <div>
        <p class="kicker">Superadmin Onboarding</p>
        <h1>
          Signup
          <span class="gradient-text">Queue</span>
        </h1>
        <p class="hero-subtitle">
          Review verified signup requests, assess risk signals, and approve or reject onboarding before any library is provisioned.
        </p>
      </div>
      <button class="btn btn-ghost" type="button" :disabled="loading" @click="loadRequests">
        <RefreshCw class="btn-icon" aria-hidden="true" />
        <span>{{ loading ? 'Refreshing...' : 'Refresh' }}</span>
      </button>
    </section>

    <section v-if="bannerText" class="section-shell">
      <div class="banner" :class="bannerType === 'success' ? 'success' : 'error'">{{ bannerText }}</div>
    </section>

    <section class="section-shell glass-card filter-card">
      <form class="filter-grid" @submit.prevent="applyFilters">
        <label class="field">
          <span>Status</span>
          <select v-model="filters.status">
            <option value="pending_approval">Pending Approval</option>
            <option value="pending_email_verification">Pending Email Verification</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="expired">Expired</option>
            <option value="">All</option>
          </select>
        </label>

        <label class="field search-field">
          <span>Search</span>
          <div class="search-input">
            <Search class="field-icon" aria-hidden="true" />
            <input
              v-model="filters.q"
              type="text"
              placeholder="Library, email, username, or phone"
            />
          </div>
        </label>

        <div class="filter-actions">
          <button class="btn btn-solid" type="submit">Apply</button>
          <button class="btn btn-ghost" type="button" @click="resetFilters">Reset</button>
        </div>
      </form>
    </section>

    <section class="section-shell glass-card table-card">
      <header class="card-head">
        <div>
          <h2>Signup Requests</h2>
          <p>{{ rows.length }} request{{ rows.length === 1 ? '' : 's' }} loaded</p>
        </div>
      </header>

      <div v-if="loading" class="state">
        <LoaderCircle class="spinner" aria-hidden="true" />
        <span>Loading signup queue...</span>
      </div>
      <div v-else-if="error" class="state error">{{ error }}</div>
      <div v-else-if="!rows.length" class="state">No signup requests match the current filters.</div>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Library</th>
              <th>Owner</th>
              <th>Status</th>
              <th>Timeline</th>
              <th>Risk</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.id">
              <td>
                <div class="cell-title">{{ row.library_name }}</div>
                <div class="cell-sub">Seats: {{ row.max_seats }}</div>
                <div class="cell-sub">Phone: {{ row.contact_phone }}</div>
                <div v-if="row.address" class="cell-sub">{{ row.address }}</div>
              </td>
              <td>
                <div class="cell-title">{{ row.admin_username }}</div>
                <div class="cell-sub">{{ row.admin_email }}</div>
                <a class="inline-link" :href="statusHref(row)" target="_blank" rel="noopener">
                  Public status
                  <ExternalLink class="link-icon" aria-hidden="true" />
                </a>
              </td>
              <td>
                <span class="status-pill" :class="statusClass(row.status)">
                  {{ humanStatus(row.status) }}
                </span>
                <div v-if="row.rejection_reason" class="cell-sub rejection-copy">
                  {{ row.rejection_reason }}
                </div>
              </td>
              <td>
                <div class="timeline-stack">
                  <div class="timeline-line">
                    <span class="timeline-label">Submitted</span>
                    <span>{{ formatDateTime(row.submitted_at) }}</span>
                  </div>
                  <div class="timeline-line" v-if="row.verified_at">
                    <span class="timeline-label">Verified</span>
                    <span>{{ formatDateTime(row.verified_at) }}</span>
                  </div>
                  <div class="timeline-line" v-if="row.approved_at">
                    <span class="timeline-label">Approved</span>
                    <span>{{ formatDateTime(row.approved_at) }}</span>
                  </div>
                  <div class="timeline-line" v-if="row.rejected_at">
                    <span class="timeline-label">Rejected</span>
                    <span>{{ formatDateTime(row.rejected_at) }}</span>
                  </div>
                </div>
              </td>
              <td>
                <div class="risk-stack">
                  <span class="risk-pill" :class="row.recent_risk_events > 0 ? 'risk-high' : 'risk-low'">
                    {{ row.recent_risk_events > 0 ? `${row.recent_risk_events} recent flag${row.recent_risk_events === 1 ? '' : 's'}` : 'No recent flags' }}
                  </span>
                  <div class="cell-sub">
                    {{ riskCopy(row.recent_risk_events) }}
                  </div>
                </div>
              </td>
              <td>
                <div class="row-actions">
                  <button
                    class="btn btn-solid tiny"
                    type="button"
                    :disabled="busyRequestId === row.id || row.status !== 'pending_approval'"
                    @click="approveRow(row)"
                  >
                    Approve
                  </button>
                  <button
                    class="btn btn-danger tiny"
                    type="button"
                    :disabled="busyRequestId === row.id || row.status !== 'pending_approval'"
                    @click="openRejectModal(row)"
                  >
                    Reject
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <div v-if="rejectTarget" class="modal-backdrop" @click.self="closeRejectModal">
      <div class="modal-card glass-card">
        <header class="modal-head">
          <div>
            <p class="kicker">Reject Signup</p>
            <h3>{{ rejectTarget.library_name }}</h3>
          </div>
          <button class="icon-btn" type="button" @click="closeRejectModal">
            <X class="btn-icon" aria-hidden="true" />
          </button>
        </header>

        <p class="modal-copy">
          Send a clear reason so the applicant can update the request using the secure resubmit link.
        </p>

        <label class="field full">
          <span>Rejection reason</span>
          <textarea
            v-model="rejectReason"
            rows="5"
            maxlength="500"
            placeholder="Example: Please use a unique admin email address and confirm the correct library contact number."
          ></textarea>
        </label>

        <p v-if="rejectError" class="inline-error">{{ rejectError }}</p>

        <div class="modal-actions">
          <button class="btn btn-ghost" type="button" :disabled="rejectLoading" @click="closeRejectModal">Cancel</button>
          <button class="btn btn-danger" type="button" :disabled="rejectLoading" @click="submitReject">
            <LoaderCircle v-if="rejectLoading" class="spinner" aria-hidden="true" />
            <span>{{ rejectLoading ? 'Sending...' : 'Reject Request' }}</span>
          </button>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import {
  ExternalLink,
  LoaderCircle,
  RefreshCw,
  Search,
  X,
} from 'lucide-vue-next'
import API from '../api'

const filters = reactive({
  status: 'pending_approval',
  q: '',
})

const rows = ref([])
const loading = ref(true)
const error = ref('')
const bannerType = ref('success')
const bannerText = ref('')
const busyRequestId = ref(null)
const rejectTarget = ref(null)
const rejectReason = ref('')
const rejectError = ref('')
const rejectLoading = ref(false)

const statusHref = (row) => `/signup/status/${row.public_id}`

const humanStatus = (status) => {
  const map = {
    pending_email_verification: 'Email Verification Pending',
    pending_approval: 'Pending Approval',
    approved: 'Approved',
    rejected: 'Rejected',
    expired: 'Expired',
  }
  return map[status] || status
}

const statusClass = (status) => {
  if (status === 'approved') return 'status-approved'
  if (status === 'pending_approval') return 'status-pending'
  if (status === 'pending_email_verification' || status === 'expired') return 'status-verification'
  if (status === 'rejected') return 'status-rejected'
  return 'status-muted'
}

const formatDateTime = (value) => {
  if (!value) return '—'
  const dt = new Date(value)
  if (Number.isNaN(dt.getTime())) return '—'
  return new Intl.DateTimeFormat('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'Asia/Kolkata',
  }).format(dt)
}

const riskCopy = (count) => {
  if (!count) return 'No failed or challenged auth events logged for this request yet.'
  if (count === 1) return 'Review the request, but this is not necessarily suspicious on its own.'
  return 'There were repeated failures or challenge events. Review carefully before approval.'
}

const setBanner = (type, text) => {
  bannerType.value = type
  bannerText.value = text
}

const extractError = (err, fallback) => {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string' && detail.trim()) return detail
  if (typeof detail === 'object' && detail?.message) return detail.message
  return fallback
}

const loadRequests = async () => {
  loading.value = true
  error.value = ''
  try {
    const res = await API.get('/superadmin/signup-requests', {
      params: {
        status: filters.status || undefined,
        q: filters.q.trim() || undefined,
        limit: 200,
        offset: 0,
      },
    })
    rows.value = Array.isArray(res.data) ? res.data : []
  } catch (err) {
    error.value = extractError(err, 'Failed to load signup requests.')
  } finally {
    loading.value = false
  }
}

const applyFilters = async () => {
  await loadRequests()
}

const resetFilters = async () => {
  filters.status = 'pending_approval'
  filters.q = ''
  await loadRequests()
}

const approveRow = async (row) => {
  busyRequestId.value = row.id
  try {
    const res = await API.post(`/superadmin/signup-requests/${row.id}/approve`)
    setBanner('success', res.data?.message || `Approved ${row.library_name}`)
    await loadRequests()
  } catch (err) {
    setBanner('error', extractError(err, 'Failed to approve signup request.'))
  } finally {
    busyRequestId.value = null
  }
}

const openRejectModal = (row) => {
  rejectTarget.value = row
  rejectReason.value = row.rejection_reason || ''
  rejectError.value = ''
}

const closeRejectModal = () => {
  rejectTarget.value = null
  rejectReason.value = ''
  rejectError.value = ''
  rejectLoading.value = false
}

const submitReject = async () => {
  if (!rejectTarget.value) {
    return
  }
  const trimmedReason = rejectReason.value.trim()
  if (trimmedReason.length < 3) {
    rejectError.value = 'Please enter a clear rejection reason.'
    return
  }

  rejectLoading.value = true
  busyRequestId.value = rejectTarget.value.id
  rejectError.value = ''
  try {
    const res = await API.post(`/superadmin/signup-requests/${rejectTarget.value.id}/reject`, {
      reason: trimmedReason,
    })
    setBanner('success', res.data?.message || `Rejected ${rejectTarget.value.library_name}`)
    closeRejectModal()
    await loadRequests()
  } catch (err) {
    rejectError.value = extractError(err, 'Failed to reject signup request.')
  } finally {
    rejectLoading.value = false
    busyRequestId.value = null
  }
}

onMounted(async () => {
  await loadRequests()
})
</script>

<style scoped>
.queue-page {
  position: relative;
  min-height: 100vh;
  padding: 2rem 2rem 2.8rem;
  color: #e2e8f0;
  isolation: isolate;
  overflow: hidden;
}

.mesh-layer {
  position: absolute;
  inset: 0;
  z-index: -1;
  background:
    radial-gradient(45rem 24rem at 10% 15%, rgba(34, 211, 238, 0.14), transparent 70%),
    radial-gradient(40rem 24rem at 86% 8%, rgba(59, 130, 246, 0.14), transparent 68%),
    radial-gradient(36rem 22rem at 65% 88%, rgba(14, 165, 233, 0.11), transparent 70%),
    linear-gradient(180deg, #0f172a 0%, #0b1222 100%);
}

.section-shell {
  width: min(1180px, calc(100% - 2rem));
  margin: 0 auto;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
}

.kicker {
  margin: 0;
  display: inline-flex;
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #cbd5e1;
  background: rgba(148, 163, 184, 0.07);
}

.hero h1 {
  margin: 0.7rem 0 0;
  font-size: clamp(2rem, 4vw, 3.15rem);
  line-height: 1.04;
  letter-spacing: -0.03em;
}

.gradient-text {
  background: linear-gradient(90deg, #22d3ee, #3b82f6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-subtitle,
.card-head p,
.cell-sub,
.modal-copy,
.timeline-label {
  color: #94a3b8;
}

.glass-card {
  border: 1px solid rgba(255, 255, 255, 0.04);
  background: rgba(148, 163, 184, 0.03);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 24px;
}

.filter-card,
.table-card {
  margin-top: 1rem;
  padding: 1.2rem;
}

.filter-grid {
  display: grid;
  grid-template-columns: minmax(0, 220px) minmax(0, 1fr) auto;
  gap: 0.85rem;
  align-items: end;
}

.field {
  display: grid;
  gap: 0.45rem;
}

.field span {
  font-size: 0.88rem;
  font-weight: 600;
  color: #cbd5e1;
}

.field select,
.field textarea,
.search-input {
  width: 100%;
  min-height: 46px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(15, 23, 42, 0.62);
  color: #e2e8f0;
}

.field select,
.field textarea {
  padding: 0.8rem 0.95rem;
}

.search-input {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0 0.95rem;
}

.search-input input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: #e2e8f0;
}

.filter-actions,
.row-actions,
.modal-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.btn {
  min-height: 44px;
  border-radius: 14px;
  border: 1px solid transparent;
  padding: 0.72rem 1rem;
  cursor: pointer;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  text-decoration: none;
}

.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-solid {
  background: linear-gradient(135deg, #22d3ee, #3b82f6);
  color: #06111f;
}

.btn-ghost {
  background: rgba(15, 23, 42, 0.56);
  border-color: rgba(148, 163, 184, 0.18);
  color: #dbeafe;
}

.btn-danger {
  background: rgba(127, 29, 29, 0.24);
  border-color: rgba(248, 113, 113, 0.34);
  color: #fecaca;
}

.tiny {
  min-height: 38px;
  padding: 0.55rem 0.8rem;
  border-radius: 12px;
  font-size: 0.84rem;
}

.banner {
  margin-top: 1rem;
  padding: 0.95rem 1rem;
  border-radius: 16px;
}

.banner.success {
  background: rgba(16, 185, 129, 0.12);
  color: #d1fae5;
}

.banner.error {
  background: rgba(239, 68, 68, 0.12);
  color: #fecaca;
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.card-head h2 {
  margin: 0;
}

.card-head p {
  margin: 0.25rem 0 0;
}

.state {
  min-height: 220px;
  display: grid;
  place-items: center;
  gap: 0.65rem;
  color: #cbd5e1;
}

.state.error {
  color: #fecaca;
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1020px;
}

th,
 td {
  padding: 1rem 0.85rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  text-align: left;
  vertical-align: top;
}

th {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94a3b8;
}

.cell-title {
  font-weight: 700;
  color: #f8fafc;
}

.cell-sub {
  margin-top: 0.22rem;
  font-size: 0.86rem;
}

.inline-link {
  margin-top: 0.55rem;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: #7dd3fc;
  text-decoration: none;
  font-size: 0.9rem;
}

.status-pill,
.risk-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.42rem 0.75rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
}

.status-approved {
  background: rgba(16, 185, 129, 0.14);
  color: #bbf7d0;
}

.status-pending {
  background: rgba(245, 158, 11, 0.14);
  color: #fde68a;
}

.status-verification {
  background: rgba(59, 130, 246, 0.14);
  color: #bfdbfe;
}

.status-rejected {
  background: rgba(239, 68, 68, 0.14);
  color: #fecaca;
}

.status-muted {
  background: rgba(148, 163, 184, 0.14);
  color: #cbd5e1;
}

.risk-low {
  background: rgba(16, 185, 129, 0.12);
  color: #d1fae5;
}

.risk-high {
  background: rgba(244, 63, 94, 0.14);
  color: #fecdd3;
}

.timeline-stack,
.risk-stack {
  display: grid;
  gap: 0.5rem;
}

.timeline-line {
  display: grid;
  gap: 0.12rem;
  font-size: 0.88rem;
}

.rejection-copy {
  max-width: 260px;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.72);
  display: grid;
  place-items: center;
  padding: 1rem;
  z-index: 40;
}

.modal-card {
  width: min(560px, 100%);
  padding: 1.25rem;
}

.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.modal-head h3 {
  margin: 0.55rem 0 0;
}

.icon-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: rgba(15, 23, 42, 0.56);
  color: #dbeafe;
  cursor: pointer;
}

.modal-copy {
  margin-top: 0.85rem;
}

.field.full {
  margin-top: 1rem;
}

.field textarea {
  min-height: 130px;
  resize: vertical;
}

.inline-error {
  margin: 0.8rem 0 0;
  color: #fecaca;
}

.btn-icon,
.field-icon,
.link-icon,
.spinner {
  width: 1rem;
  height: 1rem;
}

.spinner {
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 960px) {
  .queue-page {
    padding: 1.2rem 0 6rem;
  }

  .section-shell {
    width: min(100%, calc(100% - 1rem));
  }

  .hero,
  .card-head,
  .filter-grid {
    grid-template-columns: 1fr;
    display: grid;
  }
}
</style>
