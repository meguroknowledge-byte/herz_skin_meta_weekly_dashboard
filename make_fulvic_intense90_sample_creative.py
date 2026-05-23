from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


SRC = "/Users/meguro/Downloads/LIENA_0782.jpg のコピー.jpg"
SAMPLE_REF = "/Users/meguro/Downloads/夏の肌、 なんとなく 不安なら。 (2).png"
OUT = "herz_skin_fulvic_intense90_sample_1080x1350.png"

FONT_SERIF = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
FONT_SERIF_BOLD = "/Library/Fonts/SourceHanSerif-SemiBold.otf"
FONT_SANS = "/Library/Fonts/ZenKakuGothicNew-Regular.ttf"
FONT_SANS_MED = "/Library/Fonts/ZenKakuGothicNew-Medium.ttf"
FONT_GARAMOND = "/Library/Fonts/GARA.TTF"

GOFUN = (250, 250, 248, 255)
USUTAMAGO = (247, 244, 225, 255)
WAKABA = (210, 215, 181, 255)
TSUKI = (232, 242, 250, 255)
INK = (64, 64, 62, 255)
SUB_INK = (106, 106, 101, 255)


def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


def cover_crop(src, size, focus_x=0.66, focus_y=0.50):
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


def brand_soften(img):
    img = ImageEnhance.Color(img).enhance(0.72)
    img = ImageEnhance.Contrast(img).enhance(0.91)
    img = ImageEnhance.Brightness(img).enhance(1.05)

    w, h = img.size
    wash = Image.new("RGBA", (w, h), GOFUN[:3] + (28,))
    img = Image.alpha_composite(img, wash)

    veil = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    px = veil.load()
    for y in range(h):
        for x in range(w):
            left = max(0, 1 - x / (w * 0.72))
            top = max(0, 1 - y / (h * 0.58))
            center = max(0, 1 - abs(x - w * 0.34) / (w * 0.46))
            alpha = int(132 * (left ** 1.35) + 42 * (top ** 1.8) + 22 * center)
            px[x, y] = GOFUN[:3] + (min(190, alpha),)
    return Image.alpha_composite(img, veil)


def paste_sample_packets(base):
    ref = Image.open(SAMPLE_REF).convert("RGBA")
    crop = ref.crop((0, 744, 386, 1320))
    crop = ImageEnhance.Color(crop).enhance(0.58)
    crop = ImageEnhance.Contrast(crop).enhance(0.92)
    crop = ImageEnhance.Brightness(crop).enhance(1.08)

    mask = Image.new("L", crop.size, 255)
    mp = mask.load()
    w, h = crop.size
    for y in range(h):
        for x in range(w):
            top_fade = min(1, y / 82)
            right_fade = min(1, (w - x) / 120) if x > w - 150 else 1
            bottom_fade = min(1, (h - y) / 54) if y > h - 72 else 1
            mp[x, y] = int(222 * min(top_fade, right_fade, bottom_fade))
    crop.putalpha(mask.filter(ImageFilter.GaussianBlur(1.7)))
    base.alpha_composite(crop, (-4, 744))


def centered_text(draw, box, text, fnt, fill, spacing=8):
    lines = text.split("\n")
    line_heights = []
    for line in lines:
        b = draw.textbbox((0, 0), line, font=fnt)
        line_heights.append(b[3] - b[1])
    total_h = sum(line_heights) + spacing * (len(lines) - 1)
    y = box[1] + (box[3] - box[1] - total_h) / 2 - 2
    for line, line_h in zip(lines, line_heights):
        b = draw.textbbox((0, 0), line, font=fnt)
        x = box[0] + (box[2] - box[0] - (b[2] - b[0])) / 2
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_h + spacing


def rounded_panel(base, box, radius, fill, outline=None, width=1, shadow=0):
    if shadow:
        sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle(
            (box[0] + 5, box[1] + 6, box[2] + 5, box[3] + 6),
            radius=radius,
            fill=(65, 65, 58, shadow),
        )
        base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.0)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def main():
    src = Image.open(SRC).convert("RGB")
    img = cover_crop(src, (1080, 1350), focus_x=0.68, focus_y=0.49)
    img = brand_soften(img)
    paste_sample_packets(img)
    d = ImageDraw.Draw(img)

    garamond = font(FONT_GARAMOND, 31)
    serif_kicker = font(FONT_SERIF, 35)
    serif_main = font(FONT_SERIF_BOLD, 74)
    serif_body = font(FONT_SERIF, 31)
    serif_small = font(FONT_SERIF, 24)
    sans = font(FONT_SANS_MED, 24)
    sans_small = font(FONT_SANS, 19)

    d.text((78, 106), "HERZ SKIN", font=garamond, fill=SUB_INK)
    d.line((79, 148, 220, 148), fill=WAKABA, width=3)

    d.text((80, 230), "フルボ酸でととのう", font=serif_kicker, fill=INK)
    d.text((78, 292), "潤い満ち肌", font=serif_main, fill=INK)
    d.line((82, 408, 450, 408), fill=WAKABA, width=2)

    d.text((82, 458), "化粧水前に、プラスワン美容", font=serif_body, fill=INK)
    d.text((84, 510), "Fulfillment Serum Water Intense 90", font=garamond, fill=SUB_INK)

    rounded_panel(img, (72, 598, 490, 686), 5, GOFUN[:3] + (224,), WAKABA, 2, 14)
    centered_text(d, (72, 598, 490, 686), "サンプルセット +\nインテンス90 現品", serif_small, INK, spacing=8)

    rounded_panel(img, (594, 986, 1018, 1086), 4, WAKABA, None, 1, 12)
    centered_text(d, (594, 986, 1018, 1086), "サンプルで試して、現品で続ける", sans, INK, spacing=0)

    d.text((804, 1148), "肌になじむ一滴を、毎日のリズムへ。", font=serif_small, fill=SUB_INK, anchor="mm")

    d.rectangle((0, 1302, 1080, 1350), fill=USUTAMAGO)
    d.text((540, 1326), "フルフィルメント セラム ウォーター インテンス90", font=sans_small, fill=SUB_INK, anchor="mm")

    img.convert("RGB").save(OUT, quality=96)


if __name__ == "__main__":
    main()
