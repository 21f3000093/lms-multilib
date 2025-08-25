<template>
  <div class="pricing-container">
    <h1 class="heading">Plans & Pricing</h1>

    <!-- Seat Calculator -->
    <div class="seat-calculator">
      <label>Enter Number of Seats:</label>
      <input
        v-model.number="seatCount"
        type="number"
        min="1"
        placeholder="e.g. 100"
      />
    </div>

    <!-- Pricing Cards -->
    <div class="pricing-grid">
      <div
        v-for="(plan, index) in plans"
        :key="index"
        class="pricing-card"
      >
        <div>
          <h2>{{ plan.name }}</h2>
          <p class="description">{{ plan.description }}</p>
          <p class="price">₹{{ plan.price }}/seat</p>
          <p class="duration">{{ plan.duration }}</p>
        </div>

        <div class="features">
          <ul>
            <li v-for="(feature, i) in plan.features" :key="i">{{ feature }}</li>
          </ul>
        </div>

        <!-- Total Calculation -->
        <div class="total">
          <p>Total: ₹{{ calculateTotal(plan) }}</p>
          <p v-if="plan.extraMonth" class="extra">
            🎁 +{{ plan.extraMonth }} month free for first-time buyers <br />
            → Pay only for {{ plan.multiplier }} months and get {{ plan.multiplier + plan.extraMonth }} months access
          </p>
        </div>

        <div>
          <!-- <button class="choose-btn">Choose Plan</button> -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"

const seatCount = ref(100)

const plans = [
  {
    name: "Monthly Pack",
    description: "Best for trial or short-term use",
    price: 9,
    duration: "Per seat / per month",
    multiplier: 1,
    extraMonth: 1,
    features: ["₹9 × Seats", "+1 month FREE for first-time buyers", "Flexible & simple"],
  },
  {
    name: "3-Month Pack (5% OFF)",
    description: "Save more with a quarterly plan",
    price: 8.55,
    duration: "Per seat / per month (billed quarterly)",
    multiplier: 3,
    extraMonth: 1,
    features: ["₹8.55 × Seats × 3", "Save 5%", "+1 month FREE for first-time buyers"],
  },
  {
    name: "6-Month Pack (10% OFF)",
    description: "Great for growing libraries",
    price: 8.1,
    duration: "Per seat / per month (billed half-yearly)",
    multiplier: 6,
    extraMonth: 2,
    features: ["₹8.10 × Seats × 6", "Save 10%", "+2 month FREE for first-time buyers"],
  },
  {
    name: "12-Month Pack (15% OFF)",
    description: "Best value annual plan",
    price: 7.65,
    duration: "Per seat / per month (billed yearly)",
    multiplier: 12,
    extraMonth: 2,
    features: ["₹7.65 × Seats × 12", "Save 15%", "+2 month FREE for first-time buyers"],
  },
  {
    name: "24-Month Pack (20% OFF)",
    description: "Lowest cost, long-term plan",
    price: 7.2,
    duration: "Per seat / per month (billed every 2 years)",
    multiplier: 24,
    extraMonth: 4,
    features: ["₹7.20 × Seats × 24", "Save 20%", "+4 month FREE for first-time buyers"],
  },
]

function calculateTotal(plan) {
  return (seatCount.value * plan.price * plan.multiplier).toFixed(0)
}
</script>

<style scoped>
.pricing-container {
  min-height: 100vh;
  background: #f9fafb00;
  padding: 20px;
  font-family: "Inter", sans-serif;
  padding-top: 4rem;
  height: 100vh;
  overflow: auto;

}

.heading {
  text-align: center;
  font-size: 26px;
  font-weight: bold;
  margin-bottom: 24px;
}

.seat-calculator {
  max-width: 400px;
  margin: 0 auto 30px auto;
  background: #fff;
  padding: 16px;
  border-radius: 16px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.seat-calculator label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
}

.seat-calculator input {
  width: 90%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 12px;
  outline: none;
  font-size: 14px;
}

.seat-calculator input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
}

/* Grid for cards */
.pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}

.pricing-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.pricing-card h2 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 8px;
}

.description {
  color: #555;
  margin-bottom: 12px;
}

.price {
  font-size: 26px;
  font-weight: bold;
  margin-bottom: 4px;
}

.duration {
  font-size: 13px;
  color: #666;
}

.features {
  margin-top: 16px;
}

.features ul {
  padding-left: 18px;
}

.features li {
  margin-bottom: 6px;
  font-size: 14px;
  color: #444;
}

.total {
  margin-top: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #2563eb;
}

.extra {
  font-size: 13px;
  color: green;
  margin-top: 4px;
}

.choose-btn {
  margin-top: 20px;
  width: 100%;
  background: #2563eb;
  color: white;
  padding: 10px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.choose-btn:hover {
  background: #1e40af;
}
</style>
