<template>
  <main class="plan-page">
    <div class="mesh-layer" aria-hidden="true"></div>

    <section class="section-shell hero">
      <div>
        <p class="kicker">Superadmin Billing</p>
        <h1>
          Plan
          <span class="gradient-text">Catalog</span>
        </h1>
        <p class="hero-subtitle">
          Create, update, deactivate, and delete subscription plans used by library admins.
        </p>
      </div>
      <button class="btn btn-ghost" type="button" :disabled="loading" @click="loadPlans">
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </section>

    <section class="section-shell" v-if="bannerText">
      <div class="banner" :class="bannerType === 'success' ? 'success' : 'error'">
        {{ bannerText }}
      </div>
    </section>

    <section class="section-shell glass-card create-card">
      <header class="card-head">
        <h2>Create New Plan</h2>
        <p>Add a new plan into the catalog.</p>
      </header>

      <div class="form-grid">
        <label class="field">
          <span>Code</span>
          <input v-model="createForm.code" type="text" placeholder="monthly_plus" />
        </label>
        <label class="field">
          <span>Name</span>
          <input v-model="createForm.name" type="text" placeholder="Monthly Plus" />
        </label>
        <label class="field">
          <span>Billing Months</span>
          <input v-model.number="createForm.billing_months" type="number" min="1" max="36" />
        </label>
        <label class="field">
          <span>Price / Seat / Month (Paise)</span>
          <input v-model.number="createForm.price_per_seat_paise" type="number" min="1" />
        </label>
        <label class="field">
          <span>Discount %</span>
          <input v-model.number="createForm.discount_percent" type="number" min="0" max="100" />
        </label>
        <label class="field">
          <span>Bonus Months</span>
          <input v-model.number="createForm.bonus_months" type="number" min="0" max="12" />
        </label>
        <label class="field">
          <span>Sort Order</span>
          <input v-model.number="createForm.sort_order" type="number" />
        </label>
        <label class="field checkbox">
          <input v-model="createForm.is_active" type="checkbox" />
          <span>Active</span>
        </label>
      </div>

      <label class="field full">
        <span>Description</span>
        <textarea v-model="createForm.description" rows="2" placeholder="Short plan details"></textarea>
      </label>

      <div class="actions">
        <button class="btn btn-solid" type="button" :disabled="createBusy" @click="createPlan">
          {{ createBusy ? 'Creating...' : 'Create Plan' }}
        </button>
      </div>
    </section>

    <section class="section-shell glass-card table-card">
      <header class="card-head">
        <h2>Existing Plans</h2>
        <p>Edit plan configuration and status.</p>
      </header>

      <div v-if="loading" class="state">Loading plans...</div>
      <div v-else-if="error" class="state error">{{ error }}</div>
      <div v-else-if="!plans.length" class="state">No plans found.</div>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Code</th>
              <th>Name</th>
              <th>Months</th>
              <th>Price (Paise)</th>
              <th>Discount</th>
              <th>Bonus</th>
              <th>Sort</th>
              <th>Active</th>
              <th>Description</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="plan in plans" :key="plan.id">
              <td><input v-model="plan.edit.code" type="text" class="cell-input" /></td>
              <td><input v-model="plan.edit.name" type="text" class="cell-input" /></td>
              <td><input v-model.number="plan.edit.billing_months" type="number" min="1" max="36" class="cell-input num" /></td>
              <td><input v-model.number="plan.edit.price_per_seat_paise" type="number" min="1" class="cell-input num" /></td>
              <td><input v-model.number="plan.edit.discount_percent" type="number" min="0" max="100" class="cell-input num" /></td>
              <td><input v-model.number="plan.edit.bonus_months" type="number" min="0" max="12" class="cell-input num" /></td>
              <td><input v-model.number="plan.edit.sort_order" type="number" class="cell-input num" /></td>
              <td>
                <label class="checkbox compact">
                  <input v-model="plan.edit.is_active" type="checkbox" />
                  <span>{{ plan.edit.is_active ? 'Yes' : 'No' }}</span>
                </label>
              </td>
              <td>
                <textarea v-model="plan.edit.description" rows="2" class="cell-textarea"></textarea>
              </td>
              <td>
                <div class="row-actions">
                  <button class="btn btn-solid tiny" type="button" :disabled="busyPlanId === plan.id" @click="savePlan(plan)">
                    Save
                  </button>
                  <button class="btn btn-ghost tiny" type="button" :disabled="busyPlanId === plan.id" @click="togglePlanActive(plan)">
                    {{ plan.edit.is_active ? 'Deactivate' : 'Activate' }}
                  </button>
                  <button class="btn btn-danger tiny" type="button" :disabled="busyPlanId === plan.id" @click="deletePlan(plan)">
                    Delete
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

const loading = ref(true)
const createBusy = ref(false)
const busyPlanId = ref(null)
const error = ref('')
const bannerType = ref('success')
const bannerText = ref('')
const plans = ref([])

const createForm = ref({
  code: '',
  name: '',
  description: '',
  billing_months: 1,
  price_per_seat_paise: 900,
  discount_percent: 0,
  bonus_months: 0,
  is_active: true,
  sort_order: 0,
})

function setBanner(type, text) {
  bannerType.value = type
  bannerText.value = text
}

function extractError(err, fallback) {
  const detail = err?.response?.data?.detail
  if (typeof detail === 'string' && detail.trim()) return detail
  if (typeof detail === 'object' && detail?.message) return detail.message
  return fallback
}

function toEditModel(plan) {
  return {
    code: plan.code || '',
    name: plan.name || '',
    description: plan.description || '',
    billing_months: Number(plan.billing_months || 1),
    price_per_seat_paise: Number(plan.price_per_seat_paise || 1),
    discount_percent: Number(plan.discount_percent || 0),
    bonus_months: Number(plan.bonus_months || 0),
    is_active: Boolean(plan.is_active),
    sort_order: Number(plan.sort_order || 0),
  }
}

function normalizePlanRows(rawPlans) {
  return rawPlans.map((plan) => ({
    ...plan,
    edit: toEditModel(plan),
  }))
}

async function loadPlans() {
  loading.value = true
  error.value = ''
  try {
    const res = await API.get('/superadmin/subscription-plans', {
      params: { include_inactive: true },
    })
    plans.value = normalizePlanRows(Array.isArray(res.data) ? res.data : [])
  } catch (err) {
    error.value = extractError(err, 'Failed to load plans')
  } finally {
    loading.value = false
  }
}

function validatePlanPayload(payload) {
  if (!String(payload.code || '').trim()) return 'Plan code is required'
  if (!String(payload.name || '').trim()) return 'Plan name is required'
  if (!Number.isFinite(Number(payload.billing_months)) || Number(payload.billing_months) < 1) return 'Billing months must be at least 1'
  if (!Number.isFinite(Number(payload.price_per_seat_paise)) || Number(payload.price_per_seat_paise) < 1) return 'Price must be at least 1 paise'
  if (!Number.isFinite(Number(payload.discount_percent)) || Number(payload.discount_percent) < 0 || Number(payload.discount_percent) > 100) return 'Discount must be between 0 and 100'
  if (!Number.isFinite(Number(payload.bonus_months)) || Number(payload.bonus_months) < 0) return 'Bonus months cannot be negative'
  return ''
}

function getSanitizedPayload(source) {
  return {
    code: String(source.code || '').trim(),
    name: String(source.name || '').trim(),
    description: String(source.description || '').trim() || null,
    billing_months: Number(source.billing_months),
    price_per_seat_paise: Number(source.price_per_seat_paise),
    discount_percent: Number(source.discount_percent),
    bonus_months: Number(source.bonus_months),
    is_active: Boolean(source.is_active),
    sort_order: Number(source.sort_order || 0),
  }
}

async function createPlan() {
  const payload = getSanitizedPayload(createForm.value)
  const validationError = validatePlanPayload(payload)
  if (validationError) {
    setBanner('error', validationError)
    return
  }

  createBusy.value = true
  try {
    await API.post('/superadmin/subscription-plans', payload)
    setBanner('success', `Plan "${payload.name}" created successfully`)
    createForm.value = {
      code: '',
      name: '',
      description: '',
      billing_months: 1,
      price_per_seat_paise: 900,
      discount_percent: 0,
      bonus_months: 0,
      is_active: true,
      sort_order: 0,
    }
    await loadPlans()
  } catch (err) {
    setBanner('error', extractError(err, 'Failed to create plan'))
  } finally {
    createBusy.value = false
  }
}

async function savePlan(plan) {
  const payload = getSanitizedPayload(plan.edit)
  const validationError = validatePlanPayload(payload)
  if (validationError) {
    setBanner('error', validationError)
    return
  }

  busyPlanId.value = plan.id
  try {
    const res = await API.patch(`/superadmin/subscription-plans/${plan.id}`, payload)
    setBanner('success', `Plan "${res.data?.name || payload.name}" updated`)
    await loadPlans()
  } catch (err) {
    setBanner('error', extractError(err, 'Failed to update plan'))
  } finally {
    busyPlanId.value = null
  }
}

async function togglePlanActive(plan) {
  busyPlanId.value = plan.id
  try {
    const nextActive = !Boolean(plan.edit.is_active)
    const res = await API.patch(`/superadmin/subscription-plans/${plan.id}`, { is_active: nextActive })
    setBanner('success', `Plan "${res.data?.name || plan.name}" ${nextActive ? 'activated' : 'deactivated'}`)
    await loadPlans()
  } catch (err) {
    setBanner('error', extractError(err, 'Failed to update plan status'))
  } finally {
    busyPlanId.value = null
  }
}

async function deletePlan(plan) {
  const ok = window.confirm(`Delete plan "${plan.name}"? If plan is already used, it will be deactivated instead.`)
  if (!ok) return

  busyPlanId.value = plan.id
  try {
    const res = await API.delete(`/superadmin/subscription-plans/${plan.id}`)
    setBanner('success', res.data?.message || 'Plan processed successfully')
    await loadPlans()
  } catch (err) {
    setBanner('error', extractError(err, 'Failed to delete/deactivate plan'))
  } finally {
    busyPlanId.value = null
  }
}

onMounted(async () => {
  await loadPlans()
})
</script>

<style scoped>
.plan-page {
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

.create-card,
.table-card {
  margin-top: 1rem;
  padding: 1rem;
}

.card-head h2 {
  margin: 0;
}

.card-head p {
  margin: 0.35rem 0 0;
  color: #94a3b8;
}

.banner {
  margin-top: 0.8rem;
  padding: 0.72rem 0.9rem;
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

.form-grid {
  margin-top: 0.85rem;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.6rem;
}

.field {
  display: grid;
  gap: 0.35rem;
}

.field span {
  color: #94a3b8;
  font-size: 0.8rem;
}

.field.full {
  margin-top: 0.7rem;
}

.field input,
.field textarea {
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.6);
  color: #e2e8f0;
  padding: 0.48rem 0.6rem;
}

.checkbox {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
}

.checkbox input {
  width: 16px;
  height: 16px;
}

.actions {
  margin-top: 0.8rem;
  display: flex;
  justify-content: flex-end;
}

.btn {
  border-radius: 10px;
  border: 1px solid transparent;
  padding: 0.5rem 0.8rem;
  font-size: 0.82rem;
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

.tiny {
  padding: 0.4rem 0.6rem;
  font-size: 0.76rem;
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
  padding: 0.6rem 0.5rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  vertical-align: top;
}

th {
  color: #94a3b8;
  font-size: 0.82rem;
  font-weight: 600;
}

.cell-input,
.cell-textarea {
  width: 100%;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: rgba(15, 23, 42, 0.5);
  color: #e2e8f0;
  padding: 0.36rem 0.45rem;
}

.cell-input.num {
  min-width: 90px;
}

.cell-textarea {
  min-width: 160px;
}

.checkbox.compact {
  gap: 0.35rem;
}

.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  min-width: 190px;
}

@media (max-width: 1080px) {
  .plan-page {
    padding: 1.2rem 1rem 2rem;
  }

  .section-shell {
    width: min(1180px, 100%);
  }

  .form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
