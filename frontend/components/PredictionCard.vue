<script setup lang="ts">
const props = defineProps<{
  fraudProb: number
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH'
  tMid?: number
  tHigh?: number
}>()

const riskColor = computed(() => {
  if (props.riskLevel === 'HIGH') return '#dc2626'
  if (props.riskLevel === 'MEDIUM') return '#d97706'
  return '#16a34a'
})
</script>

<template>
  <div class="card" :style="{ borderColor: riskColor }">
    <h2>Prediction Result</h2>
    <p><strong>Fraud Probability:</strong> {{ (fraudProb * 100).toFixed(2) }}%</p>
    <p><strong>Risk Level:</strong> <span :style="{ color: riskColor }">{{ riskLevel }}</span></p>
    <p v-if="tMid !== undefined && tHigh !== undefined" class="muted">
      thresholds: t_mid={{ tMid }}, t_high={{ tHigh }}
    </p>
  </div>
</template>

<style scoped>
.card { background: #fff; border: 2px solid; border-radius: 12px; padding: 16px; }
.muted { color: #6b7280; font-size: 13px; }
</style>
