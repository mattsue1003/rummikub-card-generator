#!/usr/bin/env python3
"""拉密牌卡 PDF 生成器 — 完整106張，63x88mm，A4列印裁剪用。"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

PAGE_W, PAGE_H = A4  # 595 x 842 pt
CARD_W = 63 * mm
CARD_H = 88 * mm
MARGIN = 8 * mm
GAP = 2 * mm
RADIUS = 3 * mm

COLORS = {
    "red": HexColor("#D32F2F"),
    "blue": HexColor("#1565C0"),
    "yellow": HexColor("#EF8E00"),
    "black": HexColor("#212121"),
}
PURPLE = HexColor("#6A1B9A")
GRAY = HexColor("#999999")

# 四色底圖（已用 PIL 以 50% 預先淡化為不透明白底，列印最穩定）
BG = {
    "red": "assets/bg_red_cat.png",      # 紅：圓滾滾小黃貓
    "blue": "assets/bg_blue_dog.png",    # 藍：棕色小狗
    "yellow": "assets/bg_yellow_cat.jpg",  # 黃：灰色小貓手繪
    "black": "assets/bg_black_dog.jpg",  # 黑：微笑大狗手繪
}
_BG_SIZE = {}
for _k, _p in BG.items():
    try:
        _BG_SIZE[_k] = ImageReader(_p).getSize()
    except Exception:
        pass

OUTPUT = "Rummikub_A4_63x88mm.pdf"


def build_deck(sets=2):
    deck = []
    for _ in range(sets):
        for c in ["red", "blue", "yellow", "black"]:
            for n in range(1, 14):
                deck.append(("num", n, c))
    deck += [("joker", 0, "joker")] * (2 if sets == 2 else 1)
    order = {"red": 0, "blue": 1, "yellow": 2, "black": 3}
    deck.sort(key=lambda t: (0, order[t[2]], t[1]) if t[0] == "num" else (1, 0, 0))
    return deck


def draw_bg(c, x, y, color):
    """在牌卡中央繪製淡化底圖（等比置中，裁切於圓角內）。"""
    path = BG.get(color)
    size = _BG_SIZE.get(color)
    if not path or not size:
        return
    iw, ih = size
    box_w, box_h = CARD_W * 0.90, CARD_H * 0.62
    s = min(box_w / iw, box_h / ih)
    dw, dh = iw * s, ih * s
    dx = x + (CARD_W - dw) / 2
    dy = y + (CARD_H - dh) / 2
    c.saveState()
    p = c.beginPath()
    p.roundRect(x, y, CARD_W, CARD_H, RADIUS)
    c.clipPath(p, stroke=0, fill=0)
    c.drawImage(path, dx, dy, dw, dh, mask="auto")
    c.restoreState()


def draw_card(c, x, y, card):
    # x,y 為左下角
    # 白底
    c.setFillColor(HexColor("#FFFFFF"))
    c.setStrokeColor(HexColor("#333333"))
    c.setLineWidth(0.8)
    c.roundRect(x, y, CARD_W, CARD_H, RADIUS, fill=1, stroke=0)

    if card[0] == "joker":
        c.setFillColor(PURPLE)
        c.setFont("Helvetica-Bold", 40)
        c.drawCentredString(x + CARD_W / 2, y + CARD_H / 2 + 6, "*")
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(x + CARD_W / 2, y + CARD_H / 2 - 20, "JOKER")
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(x + CARD_W / 2, y + CARD_H / 2 - 32, "WILD")
    else:
        _, num, color = card
        col = COLORS[color]
        draw_bg(c, x, y, color)
        c.setFillColor(col)
        # 中央大數字
        c.setFont("Helvetica-Bold", 52)
        c.drawCentredString(x + CARD_W / 2, y + CARD_H / 2 - 8, str(num))
        # 角落小數字
        c.setFont("Helvetica-Bold", 15)
        c.drawString(x + 5, y + CARD_H - 18, str(num))
        c.saveState()
        c.translate(x + CARD_W - 5, y + 18)
        c.rotate(180)
        c.drawString(0, 0, str(num))
        c.restoreState()
        # 下方小字
        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(col)
        c.drawCentredString(x + CARD_W / 2, y + 10, "RUMMIKUB")

    # 黑框（裁切線）壓在最上層
    c.setStrokeColor(HexColor("#333333"))
    c.setLineWidth(0.8)
    c.setFillColor(HexColor("#FFFFFF"), alpha=0)
    c.roundRect(x, y, CARD_W, CARD_H, RADIUS, fill=0, stroke=1)


def main():
    deck = build_deck(sets=2)
    cols = int((210 * mm - MARGIN * 2 + GAP) // (CARD_W + GAP))
    rows = int((297 * mm - MARGIN * 2 + GAP) // (CARD_H + GAP))
    per_page = cols * rows
    print(f"每頁 {cols}x{rows}={per_page} 張，共 {len(deck)} 張")

    c = canvas.Canvas(OUTPUT, pagesize=A4)
    c.setTitle("Rummikub Cards 63x88mm A4")
    c.setAuthor("Rummikub Generator")

    for i, card in enumerate(deck):
        if i % per_page == 0 and i > 0:
            c.showPage()
        idx = i % per_page
        r, col_i = divmod(idx, cols)
        # 由上往下排
        x = MARGIN + col_i * (CARD_W + GAP)
        y_top = PAGE_H - MARGIN - r * (CARD_H + GAP)
        y = y_top - CARD_H
        draw_card(c, x, y, card)

    c.showPage()
    c.save()
    print(f"已輸出 {OUTPUT}")


if __name__ == "__main__":
    main()
