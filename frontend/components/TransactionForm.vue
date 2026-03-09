<script setup lang="ts">
export type TransactionInput = {
  step: number
  type: 'CASH_IN' | 'CASH_OUT' | 'DEBIT' | 'PAYMENT' | 'TRANSFER'
  amount: number
  oldbalanceOrg: number
  newbalanceOrig: number
  oldbalanceDest: number
  newbalanceDest: number
  isFlaggedFraud: 0 | 1
}

const emit = defineEmits<{
  submit: [payload: TransactionInput]
}>()

const form = reactive<TransactionInput>({
  step: 1,
  type: 'TRANSFER',
  amount: 1000,
  oldbalanceOrg: 5000,
  newbalanceOrig: 4000,
  oldbalanceDest: 2000,
  newbalanceDest: 3000,
  isFlaggedFraud: 0
})

function onSubmit() {
  emit('submit', { ...form })
}
</script>

<template>
  <form class="card" @submit.prevent="onSubmit">
    <h2>Transaction Input</h2>

    <div class="grid">
      <label>Step<input v-model.number="form.step" type="number" min="1" required /></label>

      <label>
        Type
        <select v-model="form.type" required>
          <option>CASH_IN</option>
          <option>CASH_OUT</option>
          <option>DEBIT</option>
          <option>PAYMENT</option>
          <option>TRANSFER</option>
        </select>
      </label>

      <label>Amount<input v-model.number="form.amount" type="number" min="0" step="0.01" required /></label>
      <label>oldbalanceOrg<input v-model.number="form.oldbalanceOrg" type="number" step="0.01" required /></label>
      <label>newbalanceOrig<input v-model.number="form.newbalanceOrig" type="number" step="0.01" required /></label>
      <label>oldbalanceDest<input v-model.number="form.oldbalanceDest" type="number" step="0.01" required /></label>
      <label>newbalanceDest<input v-model.number="form.newbalanceDest" type="number" step="0.01" required /></label>

      <label>
        isFlaggedFraud
        <select v-model.number="form.isFlaggedFraud">
          <option :value="0">0</option>
          <option :value="1">1</option>
        </select>
      </label>
    </div>

    <button type="submit">Predict Risk</button>
  </form>
</template>

<style scoped>
.card { background: #fff; border: 1px solid #ddd; border-radius: 12px; padding: 16px; }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
label { display: flex; flex-direction: column; gap: 6px; font-size: 14px; }
input, select { padding: 8px; border: 1px solid #ccc; border-radius: 8px; }
button { margin-top: 12px; padding: 10px 14px; border-radius: 8px; border: none; background: #111827; color: white; cursor: pointer; }
</style>
