# 個股股價走勢分析 Stock Chart Analysis

輸入台股或美股代碼，即時查看近半年技術走勢、均線交叉訊號，以及十年長期績效統計的 Streamlit 分析工具。

---

## 功能

### 近半年走勢圖
- 收盤價折線圖 + 20MA / 60MA 均線
- **黃金交叉**（綠色 ▲）：20MA 向上穿越 60MA，為多頭訊號
- **死亡交叉**（紅色 ▼）：20MA 向下穿越 60MA，為空頭訊號
- 交叉事件明細表（日期、價格）

### 十年績效統計
- 總報酬率
- 3 年 / 5 年 / 10 年 CAGR（年複合成長率）
- 最大回撤（Max Drawdown）
- 前三大跌幅區間（高點、低點、回撤幅度、復原日期）
- 十年走勢圖（標記前三大跌幅區間）

### 雙市場支援
| 市場 | 輸入方式 | 範例 |
|------|----------|------|
| 台股 | 輸入數字代碼，自動加 `.TW` | `2330` → `2330.TW` |
| 美股 | 直接輸入代碼 | `AAPL` |

---

## 技術架構

| 項目 | 技術 |
|------|------|
| Web 框架 | Streamlit |
| 資料來源 | Yahoo Finance（yfinance） |
| 圖表 | Plotly（互動式） |
| 資料處理 | pandas / numpy |
| 替代介面 | HTML + Plotly.js（server.py） |

---

## 專案結構

```
stock-chart-analysis/
├── app.py              # Streamlit 主程式
├── stock_chart.py      # 命令列走勢圖產生器
├── server.py           # HTML 介面用代理伺服器
├── index.html          # 替代前端介面
├── gen_prompt_jpg.py   # 需求文件圖片產生器
├── requirements.txt    # Python 依賴套件
└── start.bat           # Windows 一鍵啟動
```

---

## 安裝

```bash
git clone https://github.com/caryhp2-cell/stock-chart-analysis.git
cd stock-chart-analysis
pip install -r requirements.txt
```

**依賴套件：**
```
streamlit / yfinance / plotly / pandas / numpy / Pillow
```

---

## 啟動方式

### 方式一：Streamlit（推薦）

```bash
streamlit run app.py
```

開啟瀏覽器前往 `http://localhost:8501`，在左側邊欄輸入股票代碼，點擊「查詢」即可。

### 方式二：HTML 介面

```bash
python server.py
```

開啟瀏覽器前往 `http://localhost:8080`，使用 HTML + Plotly.js 的替代介面。

### 方式三：Windows 一鍵啟動

雙擊 `start.bat`，自動啟動 server.py。

### 方式四：命令列產圖

```bash
python stock_chart.py
```

互動式輸入股票代碼，輸出 `stock_chart.png` 靜態圖片。

---

## 使用流程

1. 在側邊欄輸入股票代碼（台股輸入數字，美股輸入英文代碼）
2. 點擊「查詢」按鈕
3. 查看近半年收盤價走勢與均線交叉標註
4. 瀏覽交叉事件明細表
5. 查看十年績效統計與跌幅區間分析
