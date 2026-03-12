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
          Activate, deactivate, grant trials, and change plans for each library.
        </p>
      </div>
      <button class="btn btn-ghost" type="button" :disabled="loading" @click="loadAll">
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </section>

    <section class="section-shell" v-if="message">
      <div class="banner" :class="bannerType === 'success' ? 'success' : 'error'">{{ message }}</div>
    </section>

    <section class="section-shell panel glass-card">
      <header class="panel-head">
        <h2>Libraries</h2>
        <p>Minimal controls for subscription lifecycle management.</p>
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
                <div class="actions">
                  <select v-model="row.selectedPlanId" class="field">
                    <option :value="null">Select Plan</option>
                    <option v-for="plan in plans" :key="plan.id" :value="plan.id">
                      {{ plan.name }}
                    </option>
                  </select>
                  <button class="btn btn-ghost tiny" :disabled="busyLibraryId === row.library.id" @click="updatePlan(row)">
                    Plan
                  </button>

                  <button class="btn btn-solid tiny" :disabled="busyLibraryId === row.library.id" @click="activate(row)">
                    Activate
                  </button>
                  <button class="btn btn-danger tiny" :disabled="busyLibraryId === row.library.id" @click="deactivate(row)">
                    Deactivate
                  </button>
                  <button class="btn btn-ghost tiny" :disabled="busyLibraryId === row.library.id" @click="grantTrial(row)">
                    Trial 14d
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

function formatDate(value) {
  if (!value) return '—'
  const dt = new Date(value)
  if (Number.isNaN(dt.getTime())) return '—'
  return dt.toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: '2-digit' })
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

onMounted(async () => {
  await loadAll()
})
</script>

<style scoped>
.super-subs-page {
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
  width: min(1140px, calc(100% - 2rem));
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
  margin: 0.9rem 0 0;
  font-size: clamp(1.9rem, 4.4vw, 3rem);
  line-height: 1.05;
}

.gradient-text {
  background: linear-gradient(90deg, #22d3ee, #3b82f6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-subtitle {
  margin: 0.75rem 0 0;
  color: #94a3b8;
}

.glass-card {
  border: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(148, 163, 184, 0.03);
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
  color: #94a3b8;
}

.banner {
  margin-top: 0.8rem;
  padding: 0.7rem 0.9rem;
  border-radius: 10px;
}

.banner.success {
  background: rgba(34, 197, 94, 0.18);
  color: #86efac;
}

.banner.error {
  background: rgba(239, 68, 68, 0.18);
  color: #fecaca;
}

.state {
  margin-top: 0.9rem;
  color: #cbd5e1;
}

.state.error {
  color: #fecaca;
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
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  vertical-align: top;
}

th {
  color: #94a3b8;
  font-weight: 600;
  font-size: 0.86rem;
}

.cell-title {
  font-weight: 600;
}

.cell-sub {
  color: #94a3b8;
  font-size: 0.86rem;
  margin-top: 0.2rem;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  min-width: 250px;
}

.field {
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.6);
  color: #e2e8f0;
  padding: 0.4rem 0.45rem;
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
  border-color: rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.5);
  color: #e2e8f0;
}

.btn-solid {
  background: linear-gradient(120deg, #06b6d4, #2563eb);
  color: #fff;
}

.btn-danger {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.35);
  color: #fecaca;
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
  background: rgba(34, 197, 94, 0.22);
  color: #86efac;
}

.status-trial {
  background: rgba(14, 165, 233, 0.22);
  color: #67e8f9;
}

.status-grace {
  background: rgba(245, 158, 11, 0.2);
  color: #fcd34d;
}

.status-expired,
.status-inactive {
  background: rgba(239, 68, 68, 0.2);
  color: #fecaca;
}

.status-muted {
  background: rgba(148, 163, 184, 0.2);
  color: #cbd5e1;
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
}
</style>
