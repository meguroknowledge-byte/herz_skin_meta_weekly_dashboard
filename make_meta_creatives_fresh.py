from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os


W, H = 1080, 1350
SRC = "herz_skin_ad_creative_v4.png"
FONT_BLACK = "/Library/Fonts/ZenKakuGothicNew-Black.ttf"
FONT_BOLD = "/Library/Fonts/ZenKakuGothicNew-Bold.ttf"
FONT_MED = "/Library/Fonts/ZenKakuGothicNew-Medium.ttf"


def f(path, size):
    return ImageFont.truetype(path, size)


def background(top, bottom):
    img = Image.new("RGB", (W, H), top)
    px = img.load()
    tr, tg, tb = Image.new("RGB", (1, 1), top).getpixel((0, 0))
    br, bg, bb = Image.new("RGB", (1, 1), bottom).getpixel((0, 0))
    for y in range(H):
        t = y / (H - 1)
        wave = int(6 * math.sin((y * 0.8) / 46))
        for x in range(W):
            glint = int(5 * math.sin((x + y) / 70))
            px[x, y] = (
                int(tr * (1 - t) + br * t) + wave + glint,
                int(tg * (1 - t) + bg * t) + wave + glint,
                int(tb * (1 - t) + bb * t) + wave + glint,
            )
    return img.convert("RGBA")


def rr(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def product():
    src = Image.open(SRC).convert("RGBA")
    crop = src.crop((74, 520, 555, 1010))
    mask = Image.new("L", crop.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, crop.size[0], crop.size[1]), radius=46, fill=235)
    crop.putalpha(mask.filter(ImageFilter.GaussianBlur(2)))
    return crop


def paste_shadow(base, img, xy, blur=28, opacity=50):
    shadow = Image.new("RGBA", img.size, (30, 42, 38, opacity))
    shadow.putalpha(img.getchannel("A").filter(ImageFilter.GaussianBlur(blur)))
    base.alpha_composite(shadow, (xy[0] + 14, xy[1] + 18))
    base.alpha_composite(img, xy)


def text(draw, xy, s, font, fill, anchor=None, stroke=0, stroke_fill=None):
    draw.text(xy, s, font=font, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=stroke_fill)


def stock_fresh():
    img = background("#eef6f2", "#dfe8e2")
    d = ImageDraw.Draw(img)
    d.ellipse((-260, 465, 840, 1565), fill=(218, 218, 199, 175))
    d.ellipse((-145, 580, 700, 1425), outline=(185, 199, 195, 145), width=4)
    d.line((720, 0, 460, 760), fill=(255, 255, 255, 70), width=36)
    d.line((810, 0, 510, 820), fill=(255, 255, 255, 48), width=20)

    text(d, (62, 72), "Herz skin", f(FONT_BOLD, 42), (93, 110, 103, 230))
    rr(d, (72, 160, 360, 218), 29, (70, 85, 78, 232))
    text(d, (216, 189), "お試しセット", f(FONT_BOLD, 29), "white", anchor="mm")
    text(d, (72, 282), "迷っている間に", f(FONT_BLACK, 58), (60, 73, 68))
    text(d, (70, 362), "なくなるかも。", f(FONT_BLACK, 86), (255, 255, 255), stroke=3, stroke_fill=(88, 104, 98))
    text(d, (74, 480), "送料のみで3日間", f(FONT_BLACK, 64), (60, 73, 68))

    prod = product().resize((560, 570))
    paste_shadow(img, prod, (86, 585))

    rr(d, (76, 1040, 904, 1254), 0, (48, 54, 50, 210))
    text(d, (118, 1082), "まずは肌で試す", f(FONT_BLACK, 68), "white")
    text(d, (118, 1160), "ミネラルリッチ導入美容液", f(FONT_BLACK, 52), "white")
    text(d, (118, 1222), "フルボ酸天然原液90%配合 ※整肌成分", f(FONT_MED, 28), (255, 255, 255, 235))
    rr(d, (726, 1264, 1014, 1322), 14, (255, 255, 255, 245))
    text(d, (870, 1292), "今すぐ試す", f(FONT_BOLD, 32), (60, 73, 68), anchor="mm")
    img.convert("RGB").save("herz_skin_meta_stock_fresh_v1.png", quality=95)


def uv_fresh():
    img = background("#f7fbfb", "#eaf3f0")
    d = ImageDraw.Draw(img)
    d.ellipse((510, -165, 1310, 635), fill=(255, 229, 154, 165))
    d.ellipse((460, -215, 1360, 685), outline=(255, 211, 105, 100), width=5)
    d.ellipse((390, -285, 1430, 755), outline=(255, 211, 105, 66), width=4)
    d.line((0, 735, 1080, 445), fill=(255, 255, 255, 60), width=28)

    text(d, (62, 72), "Herz skin", f(FONT_BOLD, 42), (89, 111, 106, 235))
    rr(d, (76, 156, 338, 214), 29, (89, 111, 106, 230))
    text(d, (207, 185), "夏前ケア", f(FONT_BOLD, 29), "white", anchor="mm")
    text(d, (72, 282), "日差しのあと、", f(FONT_BLACK, 61), (60, 78, 73))
    text(d, (70, 362), "肌がつっぱる前に", f(FONT_BLACK, 74), (255, 255, 255), stroke=3, stroke_fill=(93, 116, 110))
    rr(d, (72, 478, 706, 568), 20, (255, 255, 255, 225), (118, 143, 136, 128), 2)
    text(d, (389, 523), "角質層までうるおい浸透", f(FONT_BLACK, 38), (66, 86, 80), anchor="mm")

    prod = product().resize((540, 550))
    paste_shadow(img, prod, (92, 620))

    rr(d, (74, 1042, 932, 1260), 0, (55, 73, 66, 205))
    text(d, (118, 1084), "夏の導入美容水", f(FONT_BLACK, 66), "white")
    text(d, (118, 1162), "洗顔後の一滴を習慣に", f(FONT_BLACK, 54), "white")
    text(d, (118, 1224), "無香料・アルコールフリー・界面活性剤不使用", f(FONT_MED, 26), (255, 255, 255, 235))
    rr(d, (726, 1264, 1014, 1322), 14, (255, 255, 255, 245))
    text(d, (870, 1292), "詳細を見る", f(FONT_BOLD, 32), (66, 86, 80), anchor="mm")
    img.convert("RGB").save("herz_skin_meta_uv_fresh_v1.png", quality=95)


if __name__ == "__main__":
    if not os.path.exists(SRC):
        raise SystemExit(f"Missing source image: {SRC}")
    stock_fresh()
    uv_fresh()
