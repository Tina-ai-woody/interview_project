<script setup lang="ts">
import type { TransactionInput } from '~/components/TransactionForm.vue'

type PredictResp = {
  fraud_prob: number
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH'
  thresholds?: { t_mid: number; t_high: number }
}

const config = useRuntimeConfig()
const featureApiBase = config.public.featureApiBase
const modelApiBase = config.public.modelApiBase

const loading = ref(false)
const errorMsg = ref('')
const result = ref<PredictResp | null>(null)

async function runPrediction(payload: TransactionInput) {
  loading.value = true
  errorMsg.value = ''
  result.value = null

  try {
    const featureResp = await $fetch(`${featureApiBase}/v1/features/transform`, {
      method: 'POST',
      body: payload
    })

    const predictResp = await $fetch<PredictResp>(`${modelApiBase}/v1/model/predict`, {
      method: 'POST',
      body: featureResp
    })

    result.value = predictResp
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || err?.message || 'Prediction failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="container">
    <h1>Fraud Risk Demo (Nuxt + FastAPI)</h1>
    <p class="muted">Input transaction -> Feature API -> Model API -> Risk level</p>

    <TransactionForm @submit="runPrediction" />

    <p v-if="loading" class="muted">Predicting...</p>
    <p v-if="errorMsg" class="error">{{ errorMsg }}</p>

    <PredictionCard
      v-if="result"
      :fraud-prob="result.fraud_prob"
      :risk-level="result.risk_level"
      :t-mid="result.thresholds?.t_mid"
      :t-high="result.thresholds?.t_high"
    />
  </main>
</template>

<style scoped>
.container { max-width: 860px; margin: 24px auto; padding: 0 16px; display: grid; gap: 16px; }
.muted { color: #6b7280; }
.error { color: #dc2626; }
h1 { margin: 0; }
</style>
