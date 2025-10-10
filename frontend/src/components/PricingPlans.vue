<template>
  <div class="pricing-container">
    <div class="header-section">
      <h1 class="heading">Plans & Pricing</h1>
      <p class="subheading">Choose the perfect plan for your library</p>
    </div>

    <!-- Enhanced Seat Calculator -->
    <div class="seat-calculator">
      <label for="seat-input">Enter Number of Seats:</label>
      <div class="input-group">
        <input
          id="seat-input"
          v-model.number="seatCount"
          type="number"
          min="0"
          placeholder="e.g. 100"
          @input="validateInput"
        />
        <div class="preset-buttons">
          <button 
            v-for="preset in presetSeats" 
            :key="preset"
            @click="seatCount = preset"
            class="preset-btn"
            :class="{ active: seatCount === preset }"
          >
            {{ preset }}
          </button>
        </div>
      </div>
      <div class="cost-preview">
        <span>Estimated monthly cost: <strong>₹{{ estimatedMonthlyCost }}</strong></span>
      </div>
    </div>

    <!-- Trust Indicators -->
    <!-- <div class="trust-indicators">
      <div class="trust-item">
        <span class="icon">🏛️</span>
        <span>Trusted by 500+ libraries</span>
      </div>
      <div class="trust-item">
        <span class="icon">🔒</span>
        <span>Secure payments</span>
      </div>
      <div class="trust-item">
        <span class="icon">💰</span>
        <span>30-day money back</span>
      </div>
    </div> -->

    <!-- Pricing Cards -->
    <div class="pricing-grid">
      <div
        v-for="(plan, index) in plans"
        :key="index"
        class="pricing-card"
        :class="{ 
          'featured': plan.featured,
          'best-value': plan.bestValue 
        }"
      >
        <!-- Plan Badge -->
        <div v-if="plan.badge" class="plan-badge">{{ plan.badge }}</div>
        
        <div class="card-header">
          <div class="plan-icon">{{ plan.icon }}</div>
          <h2>{{ plan.name }}</h2>
          <p class="description">{{ plan.description }}</p>
        </div>

        <div class="pricing-display">
          <div class="price-main">
            <span class="currency">₹</span>
            <span class="amount">{{ plan.price }}</span>
            <span class="unit">/seat</span>
          </div>
          <p class="duration">{{ plan.duration }}</p>
          
          <!-- Savings Display -->
          <div v-if="plan.discount" class="savings-badge">
            <span class="discount">{{ plan.discount }}% OFF</span>
            <span class="savings-amount">Save ₹{{ calculateSavings(plan) }}</span>
          </div>
        </div>

        <div class="features">
          <ul>
            <li v-for="(feature, i) in plan.features" :key="i">
              <span class="checkmark">✓</span>
              {{ feature }}
            </li>
          </ul>
        </div>

        <!-- Enhanced Total Section -->
        <div class="total-section">
          <div class="total-cost">
            <span class="total-label">Total Cost</span>
            <span class="total-amount">₹{{ calculateTotal(plan) }}</span>
          </div>
          
          <div v-if="plan.extraMonth" class="bonus-offer">
            <div class="bonus-icon">🎁</div>
            <div class="bonus-text">
              <strong>+{{ plan.extraMonth }} month{{ plan.extraMonth > 1 ? 's' : '' }} FREE</strong>
              <small>for first-time buyers</small>
            </div>
          </div>
          
          <div class="effective-cost">
            Pay for {{ plan.multiplier }} months, get {{ plan.multiplier + (plan.extraMonth || 0) }} months
          </div>
        </div>

        <div class="card-footer">
          <!-- <button class="cta-button" :class="{ 'primary': plan.featured }">
            {{ plan.featured ? 'Start Free Trial' : 'Choose Plan' }}
          </button> -->
          
          <div v-if="plan.featured" class="popular-choice">
            <span class="fire">🔥</span> Most Popular Choice
          </div>
        </div>
      </div>
    </div>

    <!-- Features Comparison -->
    <div class="features-section">
      <h3>What's Included in All Plans</h3>
      <div class="feature-grid">
        <div class="feature-item">
          <span class="feature-icon">
            <!-- 📊 -->
             <img src="../assets/svg/student-white.svg" class="feature-icon" style="width: 25px;" alt="">
          </span>
          <span>Student Management</span>
        </div>
        <div class="feature-item">
          <!-- <span class="feature-icon">💺</span> -->
           <span class="feature-icon">
            <!-- 📊 -->
             <img src="../assets/svg/map-w.svg" class="feature-icon" style="width: 25px;" alt="">
          </span>
          <span>Seat Allocation</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">💳</span>
          <span>Fee Management</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">📱</span>
          <span>WhatsApp Integration</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">
            <!-- 📊 -->
             <img src="../assets/svg/chart-2.svg" class="feature-icon" style="width: 25px;" alt="">
          </span>
          <span>Analytics & Reports</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">🔧</span>
          <span>24/7 Support</span>
        </div>
      </div>
    </div>

    <!-- FAQ Section -->
    <div class="faq-section">
      <h3>Frequently Asked Questions</h3>
      <div class="faq-grid">
        <div class="faq-item">
          <h4>Can I change my plan anytime?</h4>
          <p>Yes, you can upgrade your plan at any time. Changes take effect immediately.</p>
        </div>
        <!-- <div class="faq-item">
          <h4>What happens to unused seats?</h4>
          <p>Unused seats can be reassigned to new students. You only pay for active seats in your library.</p>
        </div> -->
        <div class="faq-item">
          <h4>Is there a setup fee?</h4>
          <p>No setup fees! We'll help you get started for free with our onboarding team.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue"

const seatCount = ref(100)
const presetSeats = [35, 50, 70, 100, 120]

const plans = [
  {
    name: "Monthly Pack",
    description: "Perfect for trial or short-term use",
    price: 9,
    duration: "Per seat / per month",
    multiplier: 1,
    extraMonth: 1,
    discount: 0,
    icon: "📅",
    badge: null,
    featured: false,
    bestValue: false,
    features: [
      "₹9 × Seats",
      // "Flexible cancellation",
      "Full feature access",
      "Email support"
    ],
  },
  {
    name: "3-Month Pack",
    description: "Save more with a quarterly plan",
    price: 8.55,
    duration: "Per seat / per month (billed quarterly)",
    multiplier: 3,
    extraMonth: 1,
    discount: 5,
    icon: "📈",
    badge: "5% OFF",
    featured: false,
    bestValue: false,
    features: [
      "₹8.55 × Seats × 3",
      "Save 5% vs monthly",
      "Priority support",
      // "Advanced analytics"
    ],
  },
  {
    name: "6-Month Pack",
    description: "Great for growing libraries",
    price: 8.1,
    duration: "Per seat / per month (billed half-yearly)",
    multiplier: 6,
    extraMonth: 1,
    discount: 10,
    icon: "🚀",
    badge: "MOST POPULAR",
    featured: true,
    bestValue: false,
    features: [
      "₹8.10 × Seats × 6",
      "Save 10% vs monthly",
      // "Custom integrations",
      // "Advanced analytics",
      "Dedicated support"
    ],
  },
  {
    name: "12-Month Pack",
    description: "Best value annual plan",
    price: 7.65,
    duration: "Per seat / per month (billed yearly)",
    multiplier: 12,
    extraMonth: 2,
    discount: 15,
    icon: "🏆",
    badge: "BEST VALUE",
    featured: false,
    bestValue: true,
    features: [
      "₹7.65 × Seats × 12",
      "Save 15% vs monthly",
      // "Advanced analytics",
      "Dedicated support",
      // "Custom training",
      // "Account manager"
    ],
  },
  {
    name: "24-Month Pack",
    description: "Lowest cost, long-term plan",
    price: 7.2,
    duration: "Per seat / per month (billed every 2 years)",
    multiplier: 24,
    extraMonth: 4,
    discount: 20,
    icon: "💎",
    badge: "MAXIMUM SAVINGS",
    featured: false,
    bestValue: false,
    features: [
      "₹7.20 × Seats × 24",
      "Save 20% vs monthly",
      // "Enterprise features",
      "Custom development"
    ],
  },
]

const estimatedMonthlyCost = computed(() => {
  return (seatCount.value * 9).toLocaleString()
})

function calculateTotal(plan) {
  return (seatCount.value * plan.price * plan.multiplier).toLocaleString()
}

function calculateSavings(plan) {
  const monthlyTotal = seatCount.value * 9 * plan.multiplier
  const planTotal = seatCount.value * plan.price * plan.multiplier
  return (monthlyTotal - planTotal).toLocaleString()
}

function validateInput() {
  if (seatCount.value < 1) seatCount.value = 0
  if (seatCount.value > 300) seatCount.value = 300
}
</script>

<style scoped>
.pricing-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
  padding-top: 3rem;
}

.header-section {
  text-align: center;
  margin-bottom: 2rem;
  color: white;
}

.heading {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.subheading {
  font-size: 1.1rem;
  opacity: 0.9;
  font-weight: 300;
}

.seat-calculator {
  max-width: 500px;
  margin: 0 auto 2rem auto;
  background: white;
  padding: 24px;
  border-radius: 20px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.seat-calculator label {
  display: block;
  margin-bottom: 12px;
  font-weight: 600;
  color: #333;
  font-size: 1.1rem;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.seat-calculator input {
  width: 90%;
  padding: 16px;
  border: 2px solid #e1e5e9;
  border-radius: 12px;
  outline: none;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.seat-calculator input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.preset-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.preset-btn {
  padding: 8px 16px;
  background: #f8f9fa;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.preset-btn:hover, .preset-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.cost-preview {
  text-align: center;
  padding: 12px;
  background: #f8f9ff;
  border-radius: 8px;
  margin-top: 12px;
  color: #4f46e5;
}

.trust-indicators {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.trust-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  font-size: 0.9rem;
  opacity: 0.9;
}

.icon {
  font-size: 1.2rem;
}

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.pricing-card {
  background: white;
  border-radius: 20px;
  padding: 32px 24px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  position: relative;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.pricing-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.15);
}

.pricing-card.featured {
  border-color: #667eea;
  transform: scale(1.02);
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
}

.pricing-card.best-value {
  border-color: #f59e0b;
}

.plan-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.card-header {
  text-align: center;
  margin-bottom: 24px;
}

.plan-icon {
  font-size: 3rem;
  margin-bottom: 12px;
}

.pricing-card h2 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: #1f2937;
}

.description {
  color: #6b7280;
  margin-bottom: 0;
  line-height: 1.5;
}

.pricing-display {
  text-align: center;
  margin-bottom: 24px;
  padding: 20px 0;
  border-bottom: 2px solid #f3f4f6;
}

.price-main {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
  margin-bottom: 8px;
}

.currency {
  font-size: 1.5rem;
  font-weight: 600;
  color: #6b7280;
}

.amount {
  font-size: 3rem;
  font-weight: 800;
  color: #1f2937;
}

.unit {
  font-size: 1.1rem;
  color: #6b7280;
  font-weight: 500;
}

.duration {
  font-size: 0.9rem;
  color: #6b7280;
  margin-bottom: 12px;
}

.savings-badge {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #dcfdf7;
  color: #065f46;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
}

.discount {
  background: #10b981;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.features {
  flex-grow: 1;
  margin-bottom: 24px;
}

.features ul {
  padding: 0;
  margin: 0;
  list-style: none;
}

.features li {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 0.95rem;
  color: #374151;
}

.checkmark {
  color: #10b981;
  font-weight: bold;
  background: #dcfdf7;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
}

.total-section {
  margin-bottom: 24px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 12px;
}

.total-cost {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.total-label {
  font-weight: 600;
  color: #374151;
}

.total-amount {
  font-size: 1.5rem;
  font-weight: 800;
  color: #667eea;
}

.bonus-offer {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #f0f9ff;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.bonus-icon {
  font-size: 1.5rem;
}

.bonus-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.bonus-text strong {
  color: #0369a1;
  font-weight: 700;
}

.bonus-text small {
  color: #64748b;
  font-size: 0.8rem;
}

.effective-cost {
  text-align: center;
  font-size: 0.85rem;
  color: #059669;
  font-weight: 600;
}

.card-footer {
  text-align: center;
}

.cta-button {
  width: 100%;
  padding: 16px;
  background: #f3f4f6;
  color: #374151;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 12px;
}

.cta-button.primary {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  border-color: #667eea;
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.popular-choice {
  font-size: 0.85rem;
  color: #dc2626;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.features-section {
  max-width: 1000px;
  margin: 4rem auto 3rem auto;
  text-align: center;
  color: white;
}

.features-section h3 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 2rem;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255,255,255,0.1);
  padding: 16px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: rgba(255,255,255,0.2);
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 1.5rem;
}

.faq-section {
  max-width: 1000px;
  margin: 3rem auto 2rem auto;
  color: white;
}

.faq-section h3 {
  text-align: center;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 2rem;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.faq-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.faq-item {
  background: rgba(255,255,255,0.1);
  padding: 24px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.faq-item h4 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: #fbbf24;
}

.faq-item p {
  line-height: 1.6;
  opacity: 0.9;
  margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .pricing-container {
    padding: 16px;
    padding-top: 4rem;
  }
  
  .heading {
    font-size: 2rem;
  }
  
  .pricing-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .pricing-card.featured {
    transform: none;
  }
  
  .trust-indicators {
    gap: 1rem;
  }
  
  .trust-item {
    font-size: 0.8rem;
  }
  
  .feature-grid {
    grid-template-columns: 1fr;
  }
  
  .faq-grid {
    grid-template-columns: 1fr;
  }
  
  .preset-buttons {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .amount {
    font-size: 2.5rem;
  }
  
  .pricing-card {
    padding: 24px 20px;
  }
  
  .seat-calculator {
    padding: 20px;
  }
}

/* Loading Animation */
.pricing-card {
  animation: slideUp 0.6s ease-out forwards;
  opacity: 0;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.pricing-card:nth-child(1) { animation-delay: 0.1s; }
.pricing-card:nth-child(2) { animation-delay: 0.2s; }
.pricing-card:nth-child(3) { animation-delay: 0.3s; }
.pricing-card:nth-child(4) { animation-delay: 0.4s; }
.pricing-card:nth-child(5) { animation-delay: 0.5s; }
</style>
