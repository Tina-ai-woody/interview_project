# Retrospective Pattern Mining Plan（SNA 回顧式關聯分析）

> 任務目標：基於全歷史資料，使用 Social Network Analysis（SNA）與帳戶行為特徵，找出與 `isFraud` 高度相關的行為模式（關聯分析，不主張即時預測因果）。

---

## 1) 分析定位（先定義清楚）

本計畫是 **retrospective pattern mining**：
- 用既有全資料回顧詐欺行為樣態
- 目標是「找出關聯特徵與可解釋規則」
- 不直接宣稱可上線即時預測（因為可包含全期間統計）

### 交付重點
1. 帳戶級風險行為特徵庫
2. 關聯強度排序（與 fraud involvement 的關聯）
3. 可解釋 high-risk behavior archetypes

---

## 2) 資料與分析單位

## 2.1 原始單位
- 交易級資料（每列一筆交易）
- 主要欄位：`step, type, amount, nameOrig, nameDest, old/new balances, isFraud`

## 2.2 目標單位（本分析）
- **帳戶級**（Account-level）
- 每個帳戶整合其歷史交易行為與網路結構

## 2.3 帳戶標記（用於關聯）
定義帳戶是否「曾涉及 fraud」：
- 若帳戶在任一交易中作為 origin 或 dest，且該交易 `isFraud=1`，則 `account_fraud_involved=1`
- 否則為 0

> 這是回顧式標記，適用於關聯分析。

---

## 3) 特徵框架（對應你提出的風險行為）

## A. 資金流動異常（快進快出、分散/整合）

1. `out_degree`, `in_degree`
2. `unique_counterparty_count`
3. `out_in_amount_ratio`
4. `same_day_turnover_ratio`（同日轉入後轉出占比，若 step 可映射日）
5. `flow_velocity_proxy`（資金週轉速度 proxy）
6. `fan_out_ratio`（單位時間內轉出到多帳戶比例）

## B. 小額多筆與大額並存

1. `txn_count`
2. `amount_mean`, `amount_std`, `amount_cv`
3. `small_txn_ratio`（低金額分位數內交易比例）
4. `large_txn_ratio`（高金額分位數內交易比例）
5. `mixed_size_index`（同時具高 small + high large 的程度）
6. `threshold_proximity_ratio`（接近申報門檻區間比例，資料可行時）

## C. 閒置後突然活躍

1. `max_inactive_gap`
2. `recent_burst_ratio`（最近窗口交易數 / 長窗口交易數）
3. `post_dormancy_volume_spike`

## D. SNA 結構特徵

1. `pagerank`
2. `betweenness_approx`（可用近似算法）
3. `clustering_coeff`
4. `reciprocal_edge_ratio`
5. `counterparty_entropy`
6. `community_id` + `community_density`

---

## 4) 實作路線（分階段）

## Stage 1：基礎帳戶特徵建表
- 從交易級彙總到帳戶級（origin + dest 合併）
- 先完成 A/B/C 類特徵（低成本高收益）

## Stage 2：SNA 圖特徵
- 建有向加權圖（node=account, edge=transfer）
- 計算 PageRank、度分布、熵、社群
- 視資源決定是否做 betweenness 近似

## Stage 3：關聯分析與模式萃取
- 單變量比較：fraud_involved vs non-fraud
- 多變量模型：LightGBM（或 XGBoost）+ SHAP
- 輸出 top features 與 high-risk pattern 組合

---

## 5) 關聯分析方法

## 5.1 單變量層級
- 統計檢定：Mann-Whitney U / KS（連續特徵）
- 效果量：Cliff’s delta 或 standardized mean difference
- 類別特徵：卡方檢定 + Cramér’s V

## 5.2 多變量層級
- 模型：LightGBM / XGBoost（account-level label）
- 評估：PR-AUC（不平衡資料）
- 解釋：SHAP summary + dependence plots

## 5.3 模式表述
形成「規則化描述」：
- 例：`high burst + high entropy + high fan-out` -> 高風險群
- 輸出風險 archetype（3~5 類）

---

## 6) 實作輸出（Deliverables）

1. `account_feature_table.csv`
   - 帳戶級特徵總表
2. `account_pattern_stats.csv`
   - 單變量關聯檢定與效果量
3. `account_pattern_model_importance.csv`
   - 模型重要度 / SHAP摘要
4. `retrospective_pattern_findings.md`
   - 高風險行為樣態、解釋與限制
5. `notebooks/retrospective_pattern_mining.ipynb`
   - 全流程可重現 notebook

---

## 7) 風險與限制聲明

1. 這是回顧式關聯，不等於因果
2. 全歷史聚合特徵可能不適合即時預測
3. 若要上線，需再做時間因果版（strictly past-only）重建
4. 帳戶標記可能受資料生成機制影響（真實場景需外部驗證）

---

## 8) 成功標準

1. 能明確找出 5~10 個與 fraud 強關聯且可解釋的帳戶行為特徵
2. 形成可溝通的 high-risk archetypes
3. 為下一步 time-aware 模型提供可遷移的候選特徵集合

---

## 9) 一句話總結

以帳戶為節點建立 SNA + 行為特徵，透過回顧式關聯分析萃取詐欺行為圖譜，先做可解釋風險洞察，再銜接到時間因果版預測模型。