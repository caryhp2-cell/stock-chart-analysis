import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import datetime, timedelta

# ── 設定 ──
plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "SimHei", "Arial"]
plt.rcParams["axes.unicode_minus"] = False


def plot_stock(ticker: str):
    """繪製指定個股近半年股價走勢圖，含 20MA / 60MA 與黃金交叉 / 死亡交叉標註。"""

    # 多抓 120 天讓 60MA 在半年起點就有值
    end = datetime.today()
    start = end - timedelta(days=300)

    df = yf.download(ticker, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
    if df.empty:
        print(f"找不到 {ticker} 的資料，請確認代碼是否正確。")
        return

    # 若 columns 是 MultiIndex，取第一層
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA60"] = df["Close"].rolling(window=60).mean()

    # 只顯示近半年
    cutoff = end - timedelta(days=180)
    df = df.loc[df.index >= cutoff.strftime("%Y-%m-%d")].copy()

    # ── 找交叉點 ──
    df["diff"] = df["MA20"] - df["MA60"]
    df["prev_diff"] = df["diff"].shift(1)

    golden = df[(df["prev_diff"] <= 0) & (df["diff"] > 0)]  # 黃金交叉
    death = df[(df["prev_diff"] >= 0) & (df["diff"] < 0)]   # 死亡交叉

    # ── 畫圖 ──
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(df.index, df["Close"], label="收盤價", color="steelblue", linewidth=1.2)
    ax.plot(df.index, df["MA20"], label="20MA", color="orange", linewidth=1)
    ax.plot(df.index, df["MA60"], label="60MA", color="purple", linewidth=1)

    # 黃金交叉 ↑ 綠色箭頭
    for idx in golden.index:
        ax.annotate(
            "⬆",
            xy=(idx, df.loc[idx, "MA20"]),
            fontsize=16,
            color="green",
            ha="center",
            va="bottom",
        )

    # 死亡交叉 ↓ 紅色箭頭
    for idx in death.index:
        ax.annotate(
            "⬇",
            xy=(idx, df.loc[idx, "MA20"]),
            fontsize=16,
            color="red",
            ha="center",
            va="top",
        )

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    fig.autofmt_xdate()

    ax.set_title(f"{ticker}  近半年股價走勢（含 20MA / 60MA）", fontsize=15)
    ax.set_xlabel("日期")
    ax.set_ylabel("價格")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("stock_chart.png", dpi=150)
    plt.show()
    print("圖表已儲存為 stock_chart.png")


if __name__ == "__main__":
    symbol = input("請輸入股票代碼（例如 2330.TW 或 AAPL）：").strip()
    plot_stock(symbol)
