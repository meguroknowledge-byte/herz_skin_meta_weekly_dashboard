from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


SRC = "003-250620Herzskin.jpg"
OUT = "herz_skin_fulvic_acid_regulation_1080x1350.png"

FONT_SERIF = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
FONT_SERIF_BOLD = "/Library/Fonts/SourceHanSerif-SemiBold.otf"
FONT_SANS = "/Library/Fonts/ZenKakuGothicNew-Regular.ttf"
FONT_GARAMOND = "/Library/Fonts/GARA.TTF"

GOFUN = (250, 250, 248, 255)
USUTAMAGO = (247, 244, 225, 255)
WAKABA = (210, 215, 181, 255)
TSUKI = (232, 242, 250, 255)
INK = (66, 66, 64, 255)
SUB_INK = (108, 108, 103, 255)


def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


def cover_crop(src, size, focus_x=0.50, focus_y=0.50):
    target_w, target_h = size
    src_w, src_h = src.size
    scale = max(target_w / src_w, target_h / src_h)
    resized = src.resize((round(src_w * scale), round(src_h * scale)), Image.Resampling.LANCZOS)
    rw, rh = resized.size
    left = int(rw * focus_x - target_w * focus_x)
    top = int(rh * focus_y - target_h * focus_y)
    left = max(0, min(left, rw - target_w))
    top = max(0, min(top, rh - target_h))
    return resized.crop((left, top, left + target_w, top + target_h)).convert("RGBA")


def soften_brand_tone(img):
    img = ImageEnhance.Color(img).enhance(0.62)
    img = ImageEnhance.Contrast(img).enhance(0.90)
    img = ImageEnhance.Brightness(img).enhance(1.06)

    w, h = img.size
    wash = Image.new("RGBA", (w, h), GOFUN[:3] + (34,))
    img = Image.alpha_composite(img, wash)

    veil = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    px = veil.load()
    for y in range(h):
        for x in range(w):
            top = max(0, 1 - y / (h * 0.58))
            right = max(0, (x - w * 0.34) / (w * 0.66))
            alpha = int(122 * (top ** 1.8) * (0.35 + 0.65 * right))
            px[x, y] = GOFUN[:3] + (alpha,)
    return Image.alpha_composite(img, veil)


def draw_letter_spaced(draw, xy, text, fnt, fill, tracking=5):
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=fnt, fill=fill)
        b = draw.textbbox((0, 0), char, font=fnt)
        x += (b[2] - b[0]) + tracking


def text_size(draw, text, fnt):
    b = draw.textbbox((0, 0), text, font=fnt)
    return b[2] - b[0], b[3] - b[1]


def center_text(draw, x, y, text, fnt, fill):
    w, h = text_size(draw, text, fnt)
    draw.text((x - w / 2, y - h / 2), text, font=fnt, fill=fill)


def main():
    src = Image.open(SRC).convert("RGB")
    img = cover_crop(src, (1080, 1350), focus_x=0.46, focus_y=0.47)
    img = soften_brand_tone(img)
    d = ImageDraw.Draw(img)

    garamond = font(FONT_GARAMOND, 32)
    serif_small = font(FONT_SERIF, 37)
    serif_main = font(FONT_SERIF_BOLD, 82)
    serif_sub = font(FONT_SERIF, 25)
    sans = font(FONT_SANS, 22)

    d.text((86, 96), "HERZ SKIN", font=garamond, fill=SUB_INK)
    d.line((86, 137, 224, 137), fill=WAKABA, width=3)

    # Keep the copy spacious and centered in the quiet top-right blank area.
    d.text((548, 206), "フルボ酸でととのう", font=serif_small, fill=INK)
    d.text((544, 278), "潤い満ち肌", font=serif_main, fill=INK)
    d.line((548, 394, 938, 394), fill=WAKABA, width=2)

    draw_letter_spaced(d, (552, 432), "FULVO-BOOSTER JELLY", garamond, SUB_INK, tracking=3)
    d.text((552, 482), "すこやかな毎日に、内側から満ちる一包を。", font=serif_sub, fill=SUB_INK)

    panel = (552, 1048, 964, 1124)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rectangle((panel[0] + 3, panel[1] + 4, panel[2] + 3, panel[3] + 4), fill=(72, 72, 66, 18))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(1.2)))
    d.rectangle(panel, fill=WAKABA)
    center_text(d, (panel[0] + panel[2]) / 2, (panel[1] + panel[3]) / 2, "14 STICKS / JELLY TYPE", sans, INK)

    d.rectangle((0, 1298, 1080, 1350), fill=USUTAMAGO)
    center_text(d, 540, 1322, "Fulfillment Fulvo-Booster Jelly", garamond, SUB_INK)

    img.convert("RGB").save(OUT, quality=96)


if __name__ == "__main__":
    main()
