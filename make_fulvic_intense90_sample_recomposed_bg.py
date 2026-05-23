from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


BG = "018-250620Herzskin.jpg"
BOTTLE_SRC = "/Users/meguro/Downloads/LIENA_0782.jpg のコピー.jpg"
SAMPLE_REF = "/Users/meguro/Downloads/夏の肌、 なんとなく 不安なら。 (2).png"
OUT = "herz_skin_fulvic_intense90_sample_recomposed_bg_1080x1350.png"

FONT_SERIF = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
FONT_SERIF_BOLD = "/Library/Fonts/SourceHanSerif-SemiBold.otf"
FONT_SANS = "/Library/Fonts/ZenKakuGothicNew-Regular.ttf"
FONT_SANS_MED = "/Library/Fonts/ZenKakuGothicNew-Medium.ttf"
FONT_GARAMOND = "/Library/Fonts/GARA.TTF"

GOFUN = (250, 250, 248, 255)
USUTAMAGO = (247, 244, 225, 255)
WAKABA = (210, 215, 181, 255)
INK = (64, 64, 62, 255)
SUB_INK = (106, 106, 101, 255)


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


def soften_background(img):
    img = ImageEnhance.Color(img).enhance(0.50)
    img = ImageEnhance.Contrast(img).enhance(0.84)
    img = ImageEnhance.Brightness(img).enhance(1.11)

    w, h = img.size
    warm = Image.new("RGBA", (w, h), USUTAMAGO[:3] + (52,))
    img = Image.alpha_composite(img, warm)

    veil = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    px = veil.load()
    for y in range(h):
        for x in range(w):
            upper = max(0, 1 - y / (h * 0.64))
            center = max(0, 1 - abs(x - w * 0.52) / (w * 0.62))
            alpha = int(138 * (upper ** 1.55) + 54 * (center ** 1.4))
            px[x, y] = GOFUN[:3] + (min(200, alpha),)
    return Image.alpha_composite(img, veil)


def soft_crop_bottle():
    src = Image.open(BOTTLE_SRC).convert("RGBA")
    # Crop the existing Intense 90 product from the prior water-background photo.
    crop = src.crop((4480, 900, 5960, 3740))
    crop = ImageEnhance.Color(crop).enhance(0.82)
    crop = ImageEnhance.Contrast(crop).enhance(0.94)
    crop = ImageEnhance.Brightness(crop).enhance(1.04)
    crop = crop.resize((420, 806), Image.Resampling.LANCZOS)

    w, h = crop.size
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((160, 6, 260, 172), radius=50, fill=232)
    md.rounded_rectangle((92, 138, 328, 264), radius=34, fill=240)
    md.polygon(
        [(102, 238), (318, 238), (404, 716), (16, 716)],
        fill=232,
    )
    md.ellipse((14, 654, 406, 790), fill=220)
    mask = mask.filter(ImageFilter.GaussianBlur(8))
    crop.putalpha(mask)
    return crop


def sample_packets():
    ref = Image.open(SAMPLE_REF).convert("RGBA")
    crop = ref.crop((0, 744, 386, 1320))
    crop = ImageEnhance.Color(crop).enhance(0.58)
    crop = ImageEnhance.Contrast(crop).enhance(0.92)
    crop = ImageEnhance.Brightness(crop).enhance(1.08)
    crop = crop.resize((416, 622), Image.Resampling.LANCZOS)

    w, h = crop.size
    mask = Image.new("L", crop.size, 255)
    mp = mask.load()
    for y in range(h):
        for x in range(w):
            top_fade = min(1, y / 82)
            right_fade = min(1, (w - x) / 122) if x > w - 156 else 1
            bottom_fade = min(1, (h - y) / 58) if y > h - 78 else 1
            mp[x, y] = int(224 * min(top_fade, right_fade, bottom_fade))
    crop.putalpha(mask.filter(ImageFilter.GaussianBlur(1.8)))
    return crop


def centered_text(draw, box, text, fnt, fill, spacing=8):
    lines = text.split("\n")
    heights = []
    for line in lines:
        b = draw.textbbox((0, 0), line, font=fnt)
        heights.append(b[3] - b[1])
    total_h = sum(heights) + spacing * (len(lines) - 1)
    y = box[1] + (box[3] - box[1] - total_h) / 2 - 2
    for line, h in zip(lines, heights):
        b = draw.textbbox((0, 0), line, font=fnt)
        x = box[0] + (box[2] - box[0] - (b[2] - b[0])) / 2
        draw.text((x, y), line, font=fnt, fill=fill)
        y += h + spacing


def rounded_panel(base, box, radius, fill, outline=None, width=1, shadow=0):
    if shadow:
        sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle(
            (box[0] + 5, box[1] + 6, box[2] + 5, box[3] + 6),
            radius=radius,
            fill=(72, 72, 64, shadow),
        )
        base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(1.8)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def main():
    bg = Image.open(BG).convert("RGB")
    img = cover_crop(bg, (1080, 1350), focus_x=0.62, focus_y=0.50)
    img = soften_background(img)

    # Change the composition: samples anchor the left, the Intense 90 bottle becomes the right hero.
    img.alpha_composite(sample_packets(), (-20, 728))
    bottle = soft_crop_bottle()
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse((632, 1088, 988, 1198), fill=(80, 78, 70, 35))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(16)))
    img.alpha_composite(bottle, (618, 506))

    d = ImageDraw.Draw(img)
    garamond = font(FONT_GARAMOND, 30)
    serif_kicker = font(FONT_SERIF, 34)
    serif_main = font(FONT_SERIF_BOLD, 76)
    serif_body = font(FONT_SERIF, 29)
    serif_small = font(FONT_SERIF, 24)
    sans = font(FONT_SANS_MED, 24)
    sans_small = font(FONT_SANS, 19)

    d.text((540, 82), "HERZ SKIN", font=garamond, fill=SUB_INK, anchor="mt")
    d.line((470, 126, 610, 126), fill=WAKABA, width=3)

    d.text((540, 196), "フルボ酸でととのう", font=serif_kicker, fill=INK, anchor="mt")
    d.text((540, 258), "潤い満ち肌", font=serif_main, fill=INK, anchor="mt")
    d.line((332, 382, 748, 382), fill=WAKABA, width=2)

    d.text((540, 426), "化粧水前に、プラスワン美容", font=serif_body, fill=INK, anchor="mt")
    d.text((540, 474), "Fulfillment Serum Water Intense 90", font=garamond, fill=SUB_INK, anchor="mt")

    rounded_panel(img, (96, 574, 500, 664), 5, GOFUN[:3] + (230,), WAKABA, 2, 12)
    centered_text(d, (96, 574, 500, 664), "サンプルセット +\nインテンス90 現品", serif_small, INK, spacing=8)

    rounded_panel(img, (532, 1162, 1018, 1252), 4, WAKABA, None, 1, 14)
    centered_text(d, (532, 1162, 1018, 1252), "サンプルで試して、現品で続ける", sans, INK)

    d.text((775, 1284), "肌になじむ一滴を、毎日のリズムへ。", font=serif_small, fill=SUB_INK, anchor="mm")

    d.rectangle((0, 1302, 1080, 1350), fill=USUTAMAGO)
    d.text((540, 1326), "フルフィルメント セラム ウォーター インテンス90", font=sans_small, fill=SUB_INK, anchor="mm")

    img.convert("RGB").save(OUT, quality=96)


if __name__ == "__main__":
    main()
