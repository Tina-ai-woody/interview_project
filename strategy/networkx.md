# NetworkX 開發規劃（Pandas + NetworkX，含抽樣與小圖驗證）

> 目標：使用 `pandas/networkx` 進行交易網路分析，在筆電資源下可執行，並能產出可視化小圖驗證方向，再把有效特徵導入 fraud 預測流程。

---

## 1) 開發定位

- 工具：`pandas` + `networkx`（不依賴 Spark）
- 分析單位：交易級（`isFraud`）
- 方法：先抽樣建立子圖 → 驗證網路模式 → 生成 SNA 特徵 → 導入模型比較

---

## 2) 資料與抽樣策略（核心）

資料量大（約 636 萬筆），不可直接全量建圖。採用分層抽樣：

## 2.1 基本抽樣（必要）
1. 時間抽樣：依 `step` 分段，保留時序代表性
2. 標籤抽樣：`isFraud` 分層（保留 fraud 比例）
3. 建議起始規模：20%（Stage A）

## 2.2 圖抽樣（建議）
從基本抽樣後資料再做子圖抽樣：
- **Node-centric sampling**：選高活躍帳戶 + 其 1-hop 鄰居
- **Fraud-seed sampling**：以 fraud 交易相關帳戶為 seed 展開 k-hop
- **Top-K by degree/amount**：保留高連結/大額核心節點

> 目的：先得到可視化與特徵驗證友善的小圖（例如 500~5000 節點）。

---

## 3) 圖建模規格

## 3.1 Node / Edge 定義
- Node：帳戶（`nameOrig`, `nameDest`）
- Edge：交易（`src=nameOrig`, `dst=nameDest`）

## 3.2 Edge 屬性
- `amount`
- `type`
- `step`
- `isFraud`
- `count`（若聚合為多重交易）

## 3.3 圖型態
- 主要：`nx.DiGraph`（方向重要）
- 若要聚合關係強度，可在 edge weight 使用交易次數或金額總和

---

## 4) 特徵工程規劃（NetworkX 可實作）

## 4.1 低成本先做（MVP）
1. out-degree / in-degree
2. unique counterparties
3. weighted degree（by amount/count）
4. pair transaction count
5. pair amount mean/sum
6. first-time pair flag（需結合時間）

## 4.2 中成本（第二階段）
1. PageRank（weight 可選）
2. reciprocal ratio（互轉比例）
3. local clustering proxy（無向化後）
4. 2-hop neighbors count

## 4.3 進階（資源允許）
1. community detection（Louvain，需額外套件）
2. betweenness（只在小圖近似）
3. anomaly score（基於局部結構/金額行為）

---

## 5) 小圖可視化驗證（必做）

每輪特徵更新後，產出 2~3 張可視化：

1. **Fraud subgraph view**
- 節點顏色：是否涉 fraud
- 邊顏色：fraud/non-fraud
- 邊粗細：amount 或 count

2. **High-risk hub view**
- 節點大小：out-degree / PageRank
- 標註 top 10 風險節點

3. **Community/cluster view**（若有）
- 顯示社群分布與 fraud 密度

> 目的：用圖像快速檢查特徵是否反映直覺模式（集中/分散/快進快出）。

---

## 6) 與模型流程整合

## 6.1 A/B 實驗框架
- Exp-1: Base features
- Exp-2: SNA features (networkx)
- Exp-3: Base + SNA

## 6.2 模型
- Logistic Regression
- Decision Tree
- LightGBM（主力）
- XGBoost（可選）

## 6.3 指標
- PR-AUC（主）
- threshold scan（precision/recall/f1）
- risk tier（Low/Medium/High）

---

## 7) 雙模式策略（對齊既有規劃）

## Mode A：Retrospective Exploratory
- 可用全歷史統計特徵
- 目的：找關聯、做洞察、確認 SNA 是否有訊號

## Mode B：Leakage-safe Transfer
- 特徵必須 `t_j < t_i`
- 只把可因果落地的特徵導入 baseline

---

## 8) 實作節奏（建議）

## Stage A（20% train）
- pandas 抽樣 + 建小圖
- 完成 MVP 特徵 + 小圖可視化
- 跑 Logistic/Tree 做方向驗證

## Stage B（50% train）
- 加入 PageRank / reciprocal 等中成本特徵
- 跑 LightGBM 比較 Base vs Base+SNA

## Stage C（近全量）
- 保留最有效特徵
- 跑最終模型比較與風險分級

---

## 9) 交付物

1. `notebooks/networkx_feature_engineering.ipynb`（後續實作）
2. `plots/networkx_subgraph_*.png`
3. `networkx_feature_table.csv`
4. `networkx_model_compare.csv`
5. `networkx_findings.md`

---

## 10) 風險與注意事項

1. NetworkX 在大圖容易記憶體爆炸 → 必須抽樣與分段
2. 視覺化僅作方向驗證，不代表統計顯著
3. 不要為了圖好看而破壞抽樣代表性
4. 導入 baseline 前一定要過 Mode B（防洩漏）檢查

---

## 一句話總結

先用 pandas/networkx 在可控子圖上快速驗證 SNA 訊號與可視化直覺，再把經過防洩漏檢查的交易級 SNA 特徵導入 baseline，追求可解釋且可落地的 fraud 提升。