# 個股股價走勢分析

Streamlit Web 應用程式，提供個股近半年走勢圖（含 20MA / 60MA 與黃金交叉 / 死亡交叉標註）以及過去十年績效統計（CAGR、Max Drawdown）。

## 安裝

```bash
pip install -r requirements.txt
```

## 啟動

```bash
streamlit run app.py
```

開啟瀏覽器 http://localhost:8501，在側邊欄輸入股票代碼即可查詢：
- 台股：輸入數字（如 `2330`），系統自動加上 `.TW`
- 美股：直接輸入代碼（如 `AAPL`）

## 功能
- 近半年收盤價走勢 + 20MA / 60MA 均線
- 黃金交叉（綠色 ▲）與死亡交叉（紅色 ▼）標註
- 交叉事件明細表
- 過去十年績效統計：總報酬率、3/5/10 年 CAGR、前三大跌幅區間
- 十年走勢圖（標記前三大跌幅區間）
