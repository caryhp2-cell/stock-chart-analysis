import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

import numpy as np

st.set_page_config(page_title="股價走勢分析", page_icon="📈", layout="wide")
st.title("📈 個股股價走勢分析")
st.caption("含 20MA / 60MA 均線、黃金交叉 / 死亡交叉標註，以及十年績效統計")

# ── 側邊欄 ──
symbol = st.sidebar.text_input("股票代碼", value="2330", help="台股輸入數字即可，例如 2330；美股直接輸入，例如 AAPL")

if st.sidebar.button("查詢", type="primary") or symbol:
    # 純數字視為台股，自動加 .TW
    ticker = f"{symbol}.TW" if symbol.isdigit() else symbol

    with st.spinner("下載資料中…"):
        end = datetime.today()
        start = end - timedelta(days=300)
        df = yf.download(ticker, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))

    if df.empty:
        st.error(f"找不到 **{ticker}** 的資料，請確認代碼是否正確。")
        st.stop()

    # 處理 MultiIndex columns
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

    golden = df[(df["prev_diff"] <= 0) & (df["diff"] > 0)]
    death = df[(df["prev_diff"] >= 0) & (df["diff"] < 0)]

    # ── Plotly 互動圖 ──
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"], name="收盤價",
        line=dict(color="steelblue", width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MA20"], name="20MA",
        line=dict(color="orange", width=1),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MA60"], name="60MA",
        line=dict(color="purple", width=1),
    ))

    # 黃金交叉
    if not golden.empty:
        fig.add_trace(go.Scatter(
            x=golden.index, y=golden["MA20"],
            mode="markers+text", name="黃金交叉",
            marker=dict(symbol="triangle-up", size=14, color="green"),
            text=["黃金交叉"] * len(golden),
            textposition="top center",
            textfont=dict(color="green", size=11),
        ))

    # 死亡交叉
    if not death.empty:
        fig.add_trace(go.Scatter(
            x=death.index, y=death["MA20"],
            mode="markers+text", name="死亡交叉",
            marker=dict(symbol="triangle-down", size=14, color="red"),
            text=["死亡交叉"] * len(death),
            textposition="bottom center",
            textfont=dict(color="red", size=11),
        ))

    fig.update_layout(
        title=f"{ticker} 近半年股價走勢（含 20MA / 60MA）",
        xaxis_title="日期",
        yaxis_title="價格",
        hovermode="x unified",
        template="plotly_white",
        height=550,
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── 交叉事件表 ──
    events = []
    for idx in golden.index:
        events.append({"日期": idx.strftime("%Y-%m-%d"), "類型": "🟢 黃金交叉", "價位": f"{golden.loc[idx, 'MA20']:.2f}"})
    for idx in death.index:
        events.append({"日期": idx.strftime("%Y-%m-%d"), "類型": "🔴 死亡交叉", "價位": f"{death.loc[idx, 'MA20']:.2f}"})

    if events:
        st.subheader("交叉事件")
        st.dataframe(pd.DataFrame(events).sort_values("日期"), use_container_width=True, hide_index=True)
    else:
        st.info("近半年內無黃金交叉或死亡交叉事件。")

    # ── 十年績效統計 ──
    st.divider()
    st.subheader("📊 過去十年績效統計")

    with st.spinner("下載十年歷史資料…"):
        end_10y = datetime.today()
        start_10y = end_10y - timedelta(days=3650)
        df_10y = yf.download(ticker, start=start_10y.strftime("%Y-%m-%d"), end=end_10y.strftime("%Y-%m-%d"))

    if df_10y.empty:
        st.warning("無法取得十年歷史資料。")
    else:
        if isinstance(df_10y.columns, pd.MultiIndex):
            df_10y.columns = df_10y.columns.get_level_values(0)

        close = df_10y["Close"].dropna()
        first_price = close.iloc[0]
        last_price = close.iloc[-1]
        first_date = close.index[0]
        last_date = close.index[-1]
        years = (last_date - first_date).days / 365.25

        # 1. 總報酬率
        total_return = (last_price / first_price - 1) * 100

        # 2. 年化複合成長率 (CAGR) — 3 / 5 / 10 年
        def calc_cagr(series, n_years):
            cutoff_date = last_date - timedelta(days=int(n_years * 365.25))
            subset = series.loc[series.index >= cutoff_date]
            if len(subset) < 2:
                return None
            p0 = subset.iloc[0]
            p1 = subset.iloc[-1]
            actual_years = (subset.index[-1] - subset.index[0]).days / 365.25
            if actual_years <= 0:
                return None
            return ((p1 / p0) ** (1 / actual_years) - 1) * 100

        cagr_3y = calc_cagr(close, 3)
        cagr_5y = calc_cagr(close, 5)
        cagr_10y = calc_cagr(close, 10)

        # 3. 找出前三大跌幅區間 (non-overlapping)
        cummax = close.cummax()
        drawdown = (close - cummax) / cummax

        def find_top_drawdowns(dd_series, price_series, n=3):
            """找出前 n 大不重疊的跌幅區間。"""
            results = []
            dd_remaining = dd_series.copy()
            for _ in range(n):
                if dd_remaining.empty or dd_remaining.min() >= 0:
                    break
                trough_idx = dd_remaining.idxmin()
                trough_val = dd_remaining.loc[trough_idx] * 100
                # 找高點（trough 之前的最高價位置）
                peak_idx = price_series.loc[:trough_idx].idxmax()
                # 找恢復點（trough 之後回到高點的位置，或資料結尾）
                post_trough = price_series.loc[trough_idx:]
                recovery = post_trough[post_trough >= price_series.loc[peak_idx]]
                if not recovery.empty:
                    recovery_idx = recovery.index[0]
                else:
                    recovery_idx = price_series.index[-1]
                results.append({
                    "peak": peak_idx,
                    "trough": trough_idx,
                    "recovery": recovery_idx,
                    "drawdown": trough_val,
                })
                # 移除此區間，避免重疊
                dd_remaining = dd_remaining.loc[
                    (dd_remaining.index < peak_idx) | (dd_remaining.index > recovery_idx)
                ]
            return results

        top_dds = find_top_drawdowns(drawdown, close, n=3)

        # 表格呈現
        stats_rows = [
            ("資料期間", f"{years:.1f} 年"),
            (f"起始價格（{first_date.strftime('%Y-%m-%d')}）", f"{first_price:.2f}"),
            (f"最新價格（{last_date.strftime('%Y-%m-%d')}）", f"{last_price:.2f}"),
            ("總報酬率", f"{total_return:.2f}%"),
            ("3 年 CAGR", f"{cagr_3y:.2f}%" if cagr_3y is not None else "資料不足"),
            ("5 年 CAGR", f"{cagr_5y:.2f}%" if cagr_5y is not None else "資料不足"),
            ("10 年 CAGR", f"{cagr_10y:.2f}%" if cagr_10y is not None else "資料不足"),
        ]
        for i, dd_info in enumerate(top_dds):
            rank = ["最大", "第二大", "第三大"][i]
            stats_rows.append((
                f"{rank}跌幅",
                f"{dd_info['drawdown']:.2f}%（{dd_info['peak'].strftime('%Y-%m-%d')} → {dd_info['trough'].strftime('%Y-%m-%d')}）",
            ))
        stats = pd.DataFrame(stats_rows, columns=["指標", "數值"])

        st.dataframe(stats, use_container_width=True, hide_index=True)

        # 十年走勢縮圖
        fig_10y = go.Figure()
        fig_10y.add_trace(go.Scatter(
            x=close.index, y=close, name="收盤價",
            line=dict(color="steelblue", width=1.2),
            fill="tozeroy", fillcolor="rgba(70,130,180,0.1)",
        ))
        # 標記前三大跌幅區間
        dd_colors = [
            ("red", "rgba(255,0,0,0.12)"),
            ("darkorange", "rgba(255,140,0,0.10)"),
            ("goldenrod", "rgba(218,165,32,0.08)"),
        ]
        for i, dd_info in enumerate(top_dds):
            rank = ["最大", "第二大", "第三大"][i]
            color, fill = dd_colors[i]
            dd_range = close.loc[dd_info["peak"]:dd_info["trough"]]
            fig_10y.add_trace(go.Scatter(
                x=dd_range.index, y=dd_range,
                name=f"{rank}跌幅 ({dd_info['drawdown']:.1f}%)",
                line=dict(color=color, width=1.5),
                fill="tozeroy", fillcolor=fill,
            ))
        fig_10y.update_layout(
            title=f"{ticker} 過去十年股價走勢",
            xaxis_title="日期", yaxis_title="價格",
            hovermode="x unified", template="plotly_white", height=400,
        )
        st.plotly_chart(fig_10y, use_container_width=True)
