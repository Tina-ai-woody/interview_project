# Frontend MVP (Nuxt)

## Setup

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

預設會呼叫：
- Feature API: `http://localhost:8001`
- Model API: `http://localhost:8002`

可在 `.env` 覆蓋：
- `NUXT_PUBLIC_FEATURE_API_BASE`
- `NUXT_PUBLIC_MODEL_API_BASE`
