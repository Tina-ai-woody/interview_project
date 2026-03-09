export default defineNuxtConfig({
  devtools: { enabled: true },
  runtimeConfig: {
    public: {
      featureApiBase: process.env.NUXT_PUBLIC_FEATURE_API_BASE || 'http://localhost:8001',
      modelApiBase: process.env.NUXT_PUBLIC_MODEL_API_BASE || 'http://localhost:8002'
    }
  },
  css: []
})
