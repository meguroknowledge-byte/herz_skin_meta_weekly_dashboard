from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os


W, H = 1080, 1350
FONT_BOLD = "/Library/Fonts/ZenKakuGothicNew-Black.ttf"
FONT_MED = "/Library/Fonts/ZenKakuGothicNew-Bold.ttf"
FONT_REG = "/Library/Fonts/ZenKakuGothicNew-Medium.ttf"
SRC = "herz_skin_ad_creative_v4.png"


def font(path, size):
    return ImageFont.truetype(path, size)


def bg(kind):
    img = Image.new("RGB", (W, H), "#edf3f1" if kind == "stock" else "#f4f8fb")
    px = img.load()
    for y in range(H):
        for x in range(W):
            wave = int(10 * math.sin((x + y * 0.7) / 56))
            if kind == "stock":
                r = 221 + wave + int(y / H * 12)
                g = 229 + wave + int(y / H * 12)
                b = 226 + wave + int(y / H * 16)
            else:
                r = 238 + wave + int(y / H * 9)
                g = 246 + wave + int(y / H * 3)
                b = 250 + wave
            px[x, y] = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
    overlay = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    d = ImageDraw.Draw(overlay)
    for i in range(-H, W, 58):
        d.line([(i, 0), (i + H, H)], fill=(255, 255, 255, 32), width=14)
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def shadowed_text(draw, xy, text, fnt, fill, shadow=(0, 0, 0, 90), offset=(4, 5), anchor=None, spacing=8):
    sx, sy = xy[0] + offset[0], xy[1] + offset[1]
    draw.multiline_text((sx, sy), text, font=fnt, fill=shadow, anchor=anchor, spacing=spacing)
    draw.multiline_text(xy, text, font=fnt, fill=fill, anchor=anchor, spacing=spacing)


def vertical(draw, x, y, text, fnt, fill, gap=4, shadow=False):
    yy = y
    for ch in text:
        if ch == "\n":
            yy += fnt.size
            continue
        if shadow:
            draw.text((x + 4, yy + 4), ch, font=fnt, fill=(0, 0, 0, 70), anchor="mt")
        draw.text((x, yy), ch, font=fnt, fill=fill, anchor="mt")
        yy += fnt.size + gap


def product_cutout():
    src = Image.open(SRC).convert("RGBA")
    crop = src.crop((44, 500, 510, 992))
    # Keep the existing product/photo treatment but feather the hard square edges.
    mask = Image.new("L", crop.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, crop.size[0], crop.size[1]), radius=42, fill=235)
    mask = mask.filter(ImageFilter.GaussianBlur(3))
    crop.putalpha(mask)
    return crop


def paste_with_shadow(base, img, xy):
    shadow = Image.new("RGBA", img.size, (18, 28, 28, 28))
    shadow.putalpha(img.getchannel("A").filter(ImageFilter.GaussianBlur(24)))
    base.alpha_composite(shadow, (xy[0] + 10, xy[1] + 14))
    base.alpha_composite(img, xy)


def stock():
    img = bg("stock")
    d = ImageDraw.Draw(img)
    d.ellipse((-240, 485, 760, 1485), fill=(219, 217, 201, 178), outline=(238, 239, 232, 210), width=8)
    d.ellipse((-135, 570, 676, 1380), outline=(190, 199, 199, 160), width=5)
    prod = product_cutout().resize((520, 548))
    paste_with_shadow(img, prod, (72, 556))
    d.text((58, 60), "Herz skin", font=font(FONT_MED, 42), fill=(255, 255, 255, 235))
    shadowed_text(d, (84, 145), "在庫わずか", font(FONT_BOLD, 96), "white", shadow=(75, 80, 76, 75), offset=(5, 6))
    d.text((90, 260), "なくなり次第終了", font=font(FONT_BOLD, 74), fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(112, 120, 115))
    rounded_rect(d, (90, 366, 566, 456), 18, (255, 255, 255, 215), (158, 166, 160, 130), 2)
    d.text((328, 410), "お試し無料セット", font=font(FONT_BOLD, 43), fill=(73, 82, 78), anchor="mm")
    rounded_rect(d, (74, 1018, 896, 1268), 0, (57, 59, 54, 202))
    d.text((118, 1056), "送料のみで", font=font(FONT_BOLD, 58), fill="white")
    d.text((118, 1125), "3日間お試し", font=font(FONT_BOLD, 78), fill="white")
    d.text((118, 1228), "フルボ酸天然原液90%配合の導入美容水", font=font(FONT_MED, 29), fill=(255, 255, 255, 235))
    rounded_rect(d, (732, 1248, 1012, 1310), 12, (255, 255, 255, 242))
    d.text((872, 1278), "今すぐ試す", font=font(FONT_BOLD, 33), fill=(80, 84, 78), anchor="mm")
    img.convert("RGB").save("herz_skin_meta_stock_meguro_v1.png", quality=95)


def uv():
    img = bg("uv")
    d = ImageDraw.Draw(img)
    d.ellipse((450, -120, 1260, 690), fill=(255, 241, 191, 130))
    for r, a in [(330, 65), (430, 45), (535, 32)]:
        d.ellipse((855 - r, 280 - r, 855 + r, 280 + r), outline=(255, 229, 160, a), width=5)
    prod = product_cutout().resize((500, 528))
    paste_with_shadow(img, prod, (88, 620))
    d.text((58, 58), "Herz skin", font=font(FONT_MED, 42), fill=(112, 128, 125, 230))
    d.text((86, 166), "紫外線を浴びた日の肌へ", font=font(FONT_BOLD, 56), fill=(72, 91, 88))
    d.text((82, 242), "先に、うるおい", font=font(FONT_BOLD, 92), fill=(255, 255, 255), stroke_width=3, stroke_fill=(116, 139, 135))
    d.text((86, 350), "仕込みケア", font=font(FONT_BOLD, 92), fill=(255, 255, 255), stroke_width=3, stroke_fill=(116, 139, 135))
    rounded_rect(d, (86, 482, 724, 574), 18, (255, 255, 255, 218), (133, 155, 151, 120), 2)
    d.text((405, 527), "角質層まで、すばやく浸透", font=font(FONT_BOLD, 38), fill=(80, 102, 98), anchor="mm")
    rounded_rect(d, (70, 1038, 930, 1268), 0, (66, 78, 73, 198))
    d.text((112, 1078), "夏のスキンケア、", font=font(FONT_BOLD, 52), fill="white")
    d.text((112, 1144), "導入美容水から", font=font(FONT_BOLD, 72), fill="white")
    d.text((112, 1231), "フルボ酸天然原液90%配合 ※整肌成分", font=font(FONT_MED, 27), fill=(255, 255, 255, 235))
    rounded_rect(d, (732, 1248, 1012, 1310), 12, (255, 255, 255, 242))
    d.text((872, 1278), "詳細を見る", font=font(FONT_BOLD, 33), fill=(80, 102, 98), anchor="mm")
    img.convert("RGB").save("herz_skin_meta_uv_meguro_v1.png", quality=95)


if __name__ == "__main__":
    if not os.path.exists(SRC):
        raise SystemExit(f"Missing source image: {SRC}")
    stock()
    uv()
