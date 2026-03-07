# Account-level SNA Feature Plan（12 個 MVP）

> 目標：建立「帳戶級」SNA 特徵，並將其回填到交易級樣本，用於提升 `isFraud` 預測。

---

## 1) 問題定義與時間原則

- 任務仍是**交易級分類**（預測每筆交易 `isFraud`）。
- 但每筆交易會帶入兩個帳戶的狀態：
  - 來源帳戶（`nameOrig`）
  - 目的帳戶（`nameDest`）

### 防洩漏核心規則
對於交易 `i`（時間 `t_i`），任一特徵 `f_i` 必須只依賴歷史資料：

\[
f_i = g(\{e_j \mid t_j < t_i\})
\]

> 嚴格使用 `< t_i`（不含當前筆），先取值再更新狀態。

---

## 2) 12 個帳戶級 SNA MVP 特徵

以下每個特徵都要做兩份：
- `orig_*`：對來源帳戶（`nameOrig`）
- `dest_*`：對目的帳戶（`nameDest`）

為了先控成本，第一版先做 **6 種帳戶指標 × 2 角色 = 12 欄**。

## A. 活躍度與連結結構（4 欄）

### 1) `orig_out_degree_hist`
定義：來源帳戶歷史轉出交易次數（截至 `t_i` 前）
\[
orig\_out\_degree\_hist(i)=\sum_{j:t_j<t_i} \mathbf{1}[nameOrig_j = nameOrig_i]
\]

### 2) `orig_unique_dest_hist`
定義：來源帳戶歷史不同目的帳戶數
\[
orig\_unique\_dest\_hist(i)=\left|\{nameDest_j\mid t_j<t_i,\ nameOrig_j=nameOrig_i\}\right|
\]

### 3) `dest_in_degree_hist`
定義：目的帳戶歷史轉入交易次數
\[
dest\_in\_degree\_hist(i)=\sum_{j:t_j<t_i} \mathbf{1}[nameDest_j = nameDest_i]
\]

### 4) `dest_unique_orig_hist`
定義：目的帳戶歷史不同來源帳戶數
\[
dest\_unique\_orig\_hist(i)=\left|\{nameOrig_j\mid t_j<t_i,\ nameDest_j=nameDest_i\}\right|
\]

---

## B. 資金流量統計（4 欄）

### 5) `orig_out_amount_sum_hist`
定義：來源帳戶歷史轉出金額總和
\[
orig\_out\_amount\_sum\_hist(i)=\sum_{j:t_j<t_i,\ nameOrig_j=nameOrig_i} amount_j
\]

### 6) `orig_out_amount_mean_hist`
定義：來源帳戶歷史平均轉出金額
\[
orig\_out\_amount\_mean\_hist(i)=\frac{orig\_out\_amount\_sum\_hist(i)}{\max(orig\_out\_degree\_hist(i),1)}
\]

### 7) `dest_in_amount_sum_hist`
定義：目的帳戶歷史轉入金額總和
\[
dest\_in\_amount\_sum\_hist(i)=\sum_{j:t_j<t_i,\ nameDest_j=nameDest_i} amount_j
\]

### 8) `dest_in_amount_mean_hist`
定義：目的帳戶歷史平均轉入金額
\[
dest\_in\_amount\_mean\_hist(i)=\frac{dest\_in\_amount\_sum\_hist(i)}{\max(dest\_in\_degree\_hist(i),1)}
\]

---

## C. 關係多樣性與新穎性 proxy（4 欄）

### 9) `orig_repeat_counterparty_ratio_hist`
定義：來源帳戶歷史中「重複對手」比例（越高代表關係集中）
\[
orig\_repeat\_counterparty\_ratio\_hist(i)=1-\frac{orig\_unique\_dest\_hist(i)}{\max(orig\_out\_degree\_hist(i),1)}
\]

### 10) `dest_repeat_counterparty_ratio_hist`
定義：目的帳戶歷史中「重複來源」比例
\[
dest\_repeat\_counterparty\_ratio\_hist(i)=1-\frac{dest\_unique\_orig\_hist(i)}{\max(dest\_in\_degree\_hist(i),1)}
\]

### 11) `orig_activity_burst_proxy_hist`
定義：來源帳戶短期活躍 proxy（MVP 版以 step-level 累積近似）
\[
orig\_activity\_burst\_proxy\_hist(i)=\frac{orig\_out\_degree\_hist(i)}{\max(step_i,1)}
\]
> 第二版可替換成滑動窗口（1d/7d）比例。

### 12) `dest_activity_burst_proxy_hist`
定義：目的帳戶短期活躍 proxy（MVP 版）
\[
dest\_activity\_burst\_proxy\_hist(i)=\frac{dest\_in\_degree\_hist(i)}{\max(step_i,1)}
\]

---

## 3) 實作流程（Lea​​kage-safe）

1. 依 `step`（必要時再加原始順序）排序資料。
2. 逐筆迭代交易：
   - 先讀取 `nameOrig/nameDest` 的歷史狀態產生特徵
   - 再用當前交易更新各帳戶統計
3. 輸出 feature table，與原交易資料按 row 對齊。

### 重要：
- 絕對不能先 `groupby(account)` 全表聚合再 merge 回去。
- 這會把未來交易資訊帶回過去（嚴重 leakage）。

---

## 4) 與模型整合方式

## 4.1 比較實驗
- Exp-1：Base（原 baseline）
- Exp-2：Base + 12 account-SNA
- Exp-3：Base + account-SNA + pair-SNA（後續）

## 4.2 模型順序
1. Logistic Regression（可解釋）
2. LightGBM（主力）
3. XGBoost（對照）

## 4.3 評估指標
- PR-AUC（主）
- Recall@Precision（如 Precision >= 0.2）
- Risk tier（High/Medium/Low）fraud capture

---

## 5) 冷啟動與缺值策略

新帳戶（歷史為空）時：
- 次數/金額類：填 0
- 比例類：以 0 或安全值（避免除零）

MVP 建議統一使用：
- 分母 `max(count, 1)`
- 未知歷史特徵設為 0

---

## 6) 計算成本與版本規劃

### MVP（本文件）
- 12 欄帳戶級特徵
- 單 pass 增量更新
- 筆電可跑（配合 20~50% train 子集）

### V2（資源允許）
- 滑動窗口 1d/7d 統計
- PageRank/社群特徵
- 更精細 burst 與時間衰減權重

---

## 7) 驗收標準（建議）

至少達成以下任一：
1. `Base + account-SNA` 的 PR-AUC 高於 Base
2. 在固定 Precision 下 Recall 提升
3. 在固定審核量（Top-K）下抓到更多 fraud

---

## 8) 面試敘事（一句版）

> 我把每筆交易映射到兩個帳戶的歷史網路狀態，使用嚴格時間因果（只看過去）建立帳戶級 SNA 特徵，再與原始交易特徵融合，驗證是否在相同誤報成本下提高詐欺捕獲率。
