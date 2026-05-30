<template>
  <main class="super-subs-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="section-shell hero">
      <div>
        <p class="kicker">Superadmin Billing</p>
        <h1>
          Subscription
          <span class="gradient-text">Management</span>
        </h1>
        <p class="hero-subtitle">
          Activate, deactivate, grant trials, change plans, and correct validity for each library.
        </p>
      </div>
      <div class="hero-actions">
        <button class="btn btn-ghost" type="button" :disabled="loading || busyBulk" @click="loadAll">
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
        <button class="btn btn-danger" type="button" :disabled="loading || busyBulk" @click="clearGraceForAll">
          {{ busyBulk ? 'Clearing...' : 'Clear Existing Grace' }}
        </button>
      </div>
    </section>

    <section class="section-shell" v-if="message">
      <div class="banner" :class="bannerType === 'success' ? 'success' : 'error'">{{ message }}</div>
    </section>

    <section class="section-shell panel glass-card">
      <header class="panel-head">
        <h2>Libraries</h2>
        <p>Manual controls for plan, validity, status, trials, and grace cleanup.</p>
      </header>

      <div v-if="loading" class="state">Loading subscriptions...</div>
      <div v-else-if="error" class="state error">{{ error }}</div>
      <div v-else-if="!rows.length" class="state">No libraries found.</div>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Library</th>
              <th>Status</th>
              <th>Plan</th>
              <th>Valid Until</th>
              <th>Grace Until</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.library.id">
              <td>
                <div class="cell-title">{{ row.library.name }}</div>
                <div class="cell-sub">Seats: {{ row.library.max_seats }}</div>
              </td>
              <td>
                <span class="status-pill" :class="statusClass(row.subscription?.status)">
                  {{ row.subscription?.status || 'not_configured' }}
                </span>
              </td>
              <td>
                {{ row.subscription?.plan_config?.name || row.subscription?.plan || '—' }}
              </td>
              <td>
                {{ formatDate(row.subscription?.valid_until) }}
              </td>
              <td>
                {{ formatDate(row.subscription?.grace_until) }}
              </td>
              <td>
                <div class="actions">
                  <div class="action-group">
                    <select v-model="row.selectedPlanId" class="field">
                      <option :value="null">Select Plan</option>
                      <option v-for="plan in plans" :key="plan.id" :value="plan.id">
                        {{ plan.name }}
                      </option>
                    </select>
                    <button class="btn btn-ghost tiny" :disabled="busyLibraryId === row.library.id" @click="updatePlan(row)">
                      Update Plan
                    </button>
                  </div>

                  <div class="action-group">
                    <input
                      v-model="row.manualValidUntil"
                      class="field date-field"
                      type="date"
                      :aria-label="`Set valid until date for ${row.library.name}`"
                    />
                    <button class="btn btn-ghost tiny" :disabled="busyLibraryId === row.library.id" @click="updateValidity(row)">
                      Set Validity
                    </button>
                  </div>

                  <div class="action-group">
                    <select v-model="row.selectedStatus" class="field" :aria-label="`Set status for ${row.library.name}`">
                      <option v-for="status in statusOptions" :key="status" :value="status">
                        {{ status }}
                      </option>
                    </select>
                    <button class="btn btn-ghost tiny" :disabled="busyLibraryId === row.library.id" @click="updateStatus(row)">
                      Set Status
                    </button>
                  </div>

                  <button class="btn btn-solid tiny" :disabled="busyLibraryId === row.library.id" @click="activate(row)">
                    Activate
                  </button>
                  <button class="btn btn-danger tiny" :disabled="busyLibraryId === row.library.id" @click="deactivate(row)">
                    Deactivate
                  </button>
                  <button class="btn btn-ghost tiny" :disabled="busyLibraryId === row.library.id" @click="grantTrial(row)">
                    Trial 14d
                  </button>
                  <button class="btn btn-danger tiny" :disabled="busyLibraryId === row.library.id" @click="expireNow(row)">
                    Expire Now
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import API from '../api'

const rows = ref([])
const plans = ref([])
const loading = ref(true)
const error = ref('')
const message = ref('')
const bannerType = ref('success')
const busyLibraryId = ref(null)
const busyBulk = ref(false)
const statusOptions = ['active', 'inactive', 'expired', 'trialing', 'grace', 'canceled']

function formatDate(value) {
  if (!value) return '—'
  const dt = new Date(value)
  if (Number.isNaN(dt.getTime())) return '—'
  return dt.toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: '2-digit' })
}

function formatDateInput(value) {
  if (!value) return ''
  const dt = new Date(value)
  if (Number.isNaN(dt.getTime())) return ''
  const year = dt.getFullYear()
  const month = String(dt.getMonth() + 1).padStart(2, '0')
  const day = String(dt.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatLocalDateTimeInput(date = new Date()) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`
}

function validUntilPayload(dateValue) {
  return `${dateValue}T23:59:59`
}

function statusClass(status) {
  const normalized = String(status || '').toLowerCase()
  if (normalized === 'active') return 'status-active'
  if (normalized === 'trialing') return 'status-trial'
  if (normalized === 'grace') return 'status-grace'
  if (normalized === 'expired') return 'status-expired'
  if (normalized === 'inactive' || normalized === 'canceled') return 'status-inactive'
  return 'status-muted'
}

function setBanner(type, text) {
  bannerType.value = type
  message.value = text
}

function extractError(err, fallback) {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string' && detail) return detail
  if (typeof detail === 'object' && detail?.message) return detail.message
  return fallback
}

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    const [subsRes, plansRes] = await Promise.all([
      API.get('/superadmin/subscriptions', { params: { limit: 200, offset: 0 } }),
      API.get('/superadmin/subscription-plans', { params: { include_inactive: true } }),
    ])

    plans.value = Array.isArray(plansRes.data) ? plansRes.data : []
    rows.value = (Array.isArray(subsRes.data) ? subsRes.data : []).map((row) => ({
      ...row,
      selectedPlanId: row.subscription?.plan_id || null,
      selectedStatus: row.subscription?.status || 'inactive',
      manualValidUntil: formatDateInput(row.subscription?.valid_until),
    }))
  } catch (err) {
    error.value = extractError(err, 'Failed to load subscriptions')
  } finally {
    loading.value = false
  }
}

async function patchSubscription(libraryId, payload, successMsg) {
  busyLibraryId.value = libraryId
  try {
    const res = await API.patch(`/superadmin/subscriptions/${libraryId}`, payload)
    setBanner('success', successMsg || res.data?.message || 'Updated')
    await loadAll()
  } catch (err) {
    setBanner('error', extractError(err, 'Update failed'))
  } finally {
    busyLibraryId.value = null
  }
}

async function activate(row) {
  await patchSubscription(
    row.library.id,
    { status: 'active', extend_days: 30, clear_trial: true },
    `Activated ${row.library.name} (extended by 30 days)`
  )
}

async function deactivate(row) {
  await patchSubscription(
    row.library.id,
    { status: 'inactive', clear_trial: true },
    `Deactivated ${row.library.name}`
  )
}

async function updatePlan(row) {
  if (!row.selectedPlanId) {
    setBanner('error', 'Please select a plan first')
    return
  }
  await patchSubscription(
    row.library.id,
    { plan_id: Number(row.selectedPlanId) },
    `Plan updated for ${row.library.name}`
  )
}

async function updateValidity(row) {
  if (!row.manualValidUntil) {
    setBanner('error', 'Please choose a valid-until date first')
    return
  }
  await patchSubscription(
    row.library.id,
    {
      valid_until: validUntilPayload(row.manualValidUntil),
      status: 'active',
      clear_trial: true,
    },
    `Validity updated for ${row.library.name}`
  )
}

async function updateStatus(row) {
  if (!row.selectedStatus) {
    setBanner('error', 'Please select a status first')
    return
  }
  await patchSubscription(
    row.library.id,
    {
      status: row.selectedStatus,
      clear_trial: ['active', 'inactive', 'expired', 'canceled'].includes(row.selectedStatus),
    },
    `Status updated for ${row.library.name}`
  )
}

async function expireNow(row) {
  await patchSubscription(
    row.library.id,
    {
      status: 'expired',
      valid_until: formatLocalDateTimeInput(),
      clear_trial: true,
    },
    `Expired ${row.library.name}`
  )
}

async function grantTrial(row) {
  busyLibraryId.value = row.library.id
  try {
    const res = await API.post(`/superadmin/subscriptions/${row.library.id}/grant-trial`, { days: 14 })
    setBanner('success', res.data?.message || `Trial granted to ${row.library.name}`)
    await loadAll()
  } catch (err) {
    setBanner('error', extractError(err, 'Failed to grant trial'))
  } finally {
    busyLibraryId.value = null
  }
}

async function clearGraceForAll() {
  busyBulk.value = true
  try {
    const res = await API.post('/superadmin/subscriptions/clear-grace')
    const updated = Number(res.data?.updated_count || 0)
    const expired = Number(res.data?.expired_count || 0)
    setBanner('success', `${res.data?.message || 'Cleared grace state'}; ${expired} expired`)
    if (updated > 0) {
      await loadAll()
    }
  } catch (err) {
    setBanner('error', extractError(err, 'Failed to clear grace state'))
  } finally {
    busyBulk.value = false
  }
}

onMounted(async () => {
  await loadAll()
})
</script>

<style scoped>
.super-subs-page {
  --surface: var(--theme-surface);
  --surface-border: var(--theme-surface-border);
  --text-primary: var(--theme-text-primary);
  --text-secondary: var(--theme-text-secondary);

  position: relative;
  min-height: 100vh;
  padding: 2rem 2rem 2.8rem;
  color: var(--text-primary);
  isolation: isolate;
  overflow: hidden;
}

.mesh-layer {
  position: absolute;
  inset: 0;
  z-index: -1;
  background: var(--theme-mesh-background);
}

.section-shell {
  width: min(1140px, calc(100% - 2rem));
  margin: 0 auto;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 1rem;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.55rem;
}

.kicker {
  margin: 0;
  display: inline-flex;
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
  border: 1px solid var(--theme-border);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--theme-text-soft);
  background: var(--theme-surface-soft);
}

.hero h1 {
  margin: 0.9rem 0 0;
  font-size: clamp(1.9rem, 4.4vw, 3rem);
  line-height: 1.05;
}

.gradient-text {
  background: linear-gradient(90deg, var(--theme-brand-a), var(--theme-brand-b));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-subtitle {
  margin: 0.75rem 0 0;
  color: var(--text-secondary);
}

.glass-card {
  border: 1px solid var(--surface-border);
  background: var(--surface);
  border-radius: 18px;
  backdrop-filter: blur(12px);
}

.panel {
  margin-top: 1rem;
  padding: 1rem;
}

.panel-head h2 {
  margin: 0;
}

.panel-head p {
  margin: 0.35rem 0 0;
  color: var(--text-secondary);
}

.banner {
  margin-top: 0.8rem;
  padding: 0.7rem 0.9rem;
  border-radius: 10px;
}

.banner.success {
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
}

.banner.error {
  background: var(--theme-danger-soft);
  color: var(--theme-danger-text);
}

.state {
  margin-top: 0.9rem;
  color: var(--theme-text-soft);
}

.state.error {
  color: var(--theme-danger-text);
}

.table-wrap {
  margin-top: 0.9rem;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  text-align: left;
  padding: 0.72rem 0.6rem;
  border-bottom: 1px solid var(--theme-border-soft);
  vertical-align: top;
}

th {
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.86rem;
}

.cell-title {
  font-weight: 600;
}

.cell-sub {
  color: var(--text-secondary);
  font-size: 0.86rem;
  margin-top: 0.2rem;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  min-width: 540px;
}

.action-group {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.field {
  border-radius: 8px;
  border: 1px solid var(--theme-input-border);
  background: var(--theme-input-bg);
  color: var(--theme-text-primary);
  padding: 0.4rem 0.45rem;
}

.date-field {
  min-width: 9.4rem;
}

.btn {
  border-radius: 10px;
  border: 1px solid transparent;
  padding: 0.44rem 0.66rem;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-ghost {
  border-color: var(--theme-border-strong);
  background: var(--theme-panel);
  color: var(--theme-text-primary);
}

.btn-solid {
  background: linear-gradient(120deg, var(--theme-brand-a), var(--theme-brand-b));
  color: var(--theme-brand-on);
}

.btn-danger {
  background: var(--theme-danger-soft);
  border-color: var(--theme-danger-border);
  color: var(--theme-danger-text);
}

.status-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0.22rem 0.55rem;
  font-size: 0.75rem;
  font-weight: 700;
}

.status-active {
  background: var(--theme-success-soft);
  color: var(--theme-success-text);
}

.status-trial {
  background: var(--theme-info-soft);
  color: var(--theme-info-text);
}

.status-grace {
  background: var(--theme-warning-soft);
  color: var(--theme-warning-text);
}

.status-expired,
.status-inactive {
  background: var(--theme-danger-soft);
  color: var(--theme-danger-text);
}

.status-muted {
  background: var(--theme-surface-soft-heavy);
  color: var(--theme-text-soft);
}

@media (max-width: 1080px) {
  .super-subs-page {
    padding: 1.2rem 1rem 2rem;
  }

  .section-shell {
    width: min(1140px, 100%);
  }
}

@media (max-width: 767px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .actions {
    min-width: 420px;
  }
}
</style>
