"""將逆向生成的 Prompt 渲染為 JPG 圖片。"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

OUTPUT = "prompt.jpg"

# ── 跨平台字型偵測 ──
FONT_CANDIDATES = [
    # Windows — 微軟正黑體
    (r"C:\Windows\Fonts\msjh.ttc", r"C:\Windows\Fonts\msjhbd.ttc"),
    # macOS — PingFang
    ("/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/PingFang.ttc"),
    # Linux — Noto Sans CJK
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
     "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
    ("/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
     "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc"),
]

FONT_PATH = None
FONT_BOLD_PATH = None
for regular, bold in FONT_CANDIDATES:
    if os.path.exists(regular):
        FONT_PATH = regular
        FONT_BOLD_PATH = bold if os.path.exists(bold) else regular
        break

if FONT_PATH is None:
    print("警告：找不到中文字型，將使用 PIL 預設字型（中文可能無法正常顯示）。")
    print("建議安裝 Noto Sans CJK 字型。")

# ── 內容定義 ──
lines = [
    ("title", "逆向生成 Prompt"),
    ("blank", ""),
    ("body", "使用 Streamlit + Plotly + yfinance 建立一個「個股股價走勢分析」Web 應用程式（app.py），需求如下："),
    ("blank", ""),
    ("h2", "一、基本設定"),
    ("bullet", "頁面標題「股價走勢分析」，wide layout"),
    ("bullet", "側邊欄提供股票代碼輸入框（預設值 2330）與「查詢」按鈕"),
    ("bullet", "台股代碼自動補全：若使用者輸入純數字（如 2330），自動加上 .TW；非純數字視為美股代碼直接使用"),
    ("blank", ""),
    ("h2", "二、近半年股價走勢圖（Plotly 互動圖表）"),
    ("bullet", "使用 yfinance 下載近 300 天日線資料（多抓以確保 60MA 在半年起點即有值），畫面只顯示近 180 天"),
    ("bullet", "繪製三條線：收盤價（steelblue）、20MA（orange）、60MA（purple）"),
    ("bullet", "黃金交叉標註：當 20MA 由下向上穿越 60MA 時，在交叉點標示綠色向上三角形 ▲ 並標註文字「黃金交叉」"),
    ("bullet", "死亡交叉標註：當 20MA 由上向下穿越 60MA 時，在交叉點標示紅色向下三角形 ▼ 並標註文字「死亡交叉」"),
    ("blank", ""),
    ("h2", "三、交叉事件表格"),
    ("bullet", "在走勢圖下方列出所有黃金交叉與死亡交叉事件的明細表（日期、類型、價位）"),
    ("bullet", "依日期排序；若半年內無交叉事件，顯示提示訊息"),
    ("blank", ""),
    ("h2", "四、過去十年績效統計"),
    ("bullet", "另外下載過去 10 年（3650 天）的歷史資料"),
    ("bullet", "以表格呈現：資料期間、起始價格（含日期）、最新價格（含日期）、總報酬率"),
    ("bullet", "3 年 CAGR、5 年 CAGR、10 年 CAGR（資料不足時顯示「資料不足」）"),
    ("bullet", "前三大跌幅（Max Drawdown）：找出不重疊的最大、第二大、第三大跌幅區間，顯示跌幅 % 及區間日期（peak → trough）"),
    ("blank", ""),
    ("h2", "五、十年走勢圖"),
    ("bullet", "繪製十年收盤價曲線（steelblue，帶淡色 fill）"),
    ("bullet", "在圖上以不同顏色標記前三大跌幅區間：最大（紅色）、第二大（深橘色）、第三大（金色）"),
    ("bullet", "每段標註其跌幅百分比"),
    ("blank", ""),
    ("h2", "六、技術細節"),
    ("bullet", "使用 streamlit、yfinance、plotly、pandas、numpy"),
    ("bullet", "處理 yfinance 回傳的 MultiIndex columns（取 level 0）"),
    ("bullet", "圖表皆使用 plotly_white 主題、hovermode=\"x unified\""),
    ("bullet", "Streamlit 設定 headless 模式，server port 8501"),
]

# ── 字型與尺寸 ──
if FONT_PATH:
    FONT_TITLE = ImageFont.truetype(FONT_BOLD_PATH, 36)
    FONT_H2 = ImageFont.truetype(FONT_BOLD_PATH, 26)
    FONT_BODY = ImageFont.truetype(FONT_PATH, 22)
else:
    FONT_TITLE = ImageFont.load_default(size=36)
    FONT_H2 = ImageFont.load_default(size=26)
    FONT_BODY = ImageFont.load_default(size=22)

WIDTH = 1200
MARGIN_X = 60
MARGIN_Y = 50
LINE_SPACING = {"title": 56, "h2": 44, "body": 36, "bullet": 36, "blank": 20}
TEXT_AREA_W = WIDTH - 2 * MARGIN_X


def wrap_text(text, font, max_width, draw):
    """手動斷行：逐字元累加寬度，超過 max_width 就換行。"""
    wrapped = []
    current = ""
    for ch in text:
        test = current + ch
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width:
            wrapped.append(current)
            current = ch
        else:
            current = test
    if current:
        wrapped.append(current)
    return wrapped


# ── 第一輪：計算總高度 ──
tmp_img = Image.new("RGB", (WIDTH, 100))
tmp_draw = ImageDraw.Draw(tmp_img)

total_h = MARGIN_Y
for style, text in lines:
    if style == "blank":
        total_h += LINE_SPACING["blank"]
        continue
    font = {"title": FONT_TITLE, "h2": FONT_H2}.get(style, FONT_BODY)
    prefix = "  •  " if style == "bullet" else ""
    display_text = prefix + text
    wrapped = wrap_text(display_text, font, TEXT_AREA_W, tmp_draw)
    total_h += len(wrapped) * LINE_SPACING[style]

total_h += MARGIN_Y

# ── 第二輪：繪製 ──
img = Image.new("RGB", (WIDTH, total_h), color=(255, 255, 255))
draw = ImageDraw.Draw(img)

y = MARGIN_Y
COLORS = {
    "title": (30, 60, 120),
    "h2": (50, 50, 50),
    "body": (60, 60, 60),
    "bullet": (60, 60, 60),
}

for style, text in lines:
    if style == "blank":
        y += LINE_SPACING["blank"]
        continue
    font = {"title": FONT_TITLE, "h2": FONT_H2}.get(style, FONT_BODY)
    color = COLORS.get(style, (0, 0, 0))
    prefix = "  •  " if style == "bullet" else ""
    display_text = prefix + text
    wrapped = wrap_text(display_text, font, TEXT_AREA_W, draw)
    for line in wrapped:
        draw.text((MARGIN_X, y), line, font=font, fill=color)
        y += LINE_SPACING[style]

# 底部加一條裝飾線
draw.line([(MARGIN_X, MARGIN_Y + 52), (WIDTH - MARGIN_X, MARGIN_Y + 52)], fill=(30, 60, 120), width=2)

img.save(OUTPUT, "JPEG", quality=95)
print(f"已儲存為 {OUTPUT}（{img.size[0]}x{img.size[1]}）")
