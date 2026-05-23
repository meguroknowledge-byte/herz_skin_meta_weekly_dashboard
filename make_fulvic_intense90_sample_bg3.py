from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


BG = "001-250620Herzskin.jpg"
BOTTLE_SRC = "/Users/meguro/Downloads/LIENA_0782.jpg のコピー.jpg"
SAMPLE_REF = "/Users/meguro/Downloads/夏の肌、 なんとなく 不安なら。 (2).png"
OUT = "herz_skin_fulvic_intense90_sample_bg3_1080x1350.png"

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


def cover_crop(src, size, focus_x=0.52, focus_y=0.47):
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


def soften_bg(img):
    img = ImageEnhance.Color(img).enhance(0.56)
    img = ImageEnhance.Contrast(img).enhance(0.86)
    img = ImageEnhance.Brightness(img).enhance(1.10)

    w, h = img.size
    wash = Image.new("RGBA", (w, h), GOFUN[:3] + (42,))
    img = Image.alpha_composite(img, wash)

    veil = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    px = veil.load()
    for y in range(h):
        for x in range(w):
            top = max(0, 1 - y / (h * 0.72))
            mid = max(0, 1 - abs(x - w * 0.48) / (w * 0.68))
            alpha = int(168 * (top ** 1.6) + 32 * (mid ** 1.5))
            px[x, y] = GOFUN[:3] + (min(210, alpha),)
    return Image.alpha_composite(img, veil)


def bottle_crop():
    src = Image.open(BOTTLE_SRC).convert("RGBA")
    crop = src.crop((4480, 900, 5960, 3740))
    crop = ImageEnhance.Color(crop).enhance(0.82)
    crop = ImageEnhance.Contrast(crop).enhance(0.94)
    crop = ImageEnhance.Brightness(crop).enhance(1.04)
    crop = crop.resize((356, 684), Image.Resampling.LANCZOS)

    w, h = crop.size
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((136, 6, 220, 146), radius=42, fill=232)
    md.rounded_rectangle((78, 118, 278, 224), radius=30, fill=240)
    md.polygon([(86, 202), (270, 202), (344, 608), (14, 608)], fill=232)
    md.ellipse((12, 554, 344, 670), fill=218)
    crop.putalpha(mask.filter(ImageFilter.GaussianBlur(7)))
    return crop


def sample_crop():
    ref = Image.open(SAMPLE_REF).convert("RGBA")
    crop = ref.crop((0, 744, 386, 1320))
    crop = ImageEnhance.Color(crop).enhance(0.56)
    crop = ImageEnhance.Contrast(crop).enhance(0.92)
    crop = ImageEnhance.Brightness(crop).enhance(1.08)
    crop = crop.resize((384, 574), Image.Resampling.LANCZOS)

    w, h = crop.size
    mask = Image.new("L", (w, h), 255)
    mp = mask.load()
    for y in range(h):
        for x in range(w):
            top_fade = min(1, y / 82)
            right_fade = min(1, (w - x) / 126) if x > w - 156 else 1
            bottom_fade = min(1, (h - y) / 62) if y > h - 82 else 1
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
            (box[0] + 4, box[1] + 5, box[2] + 4, box[3] + 5),
            radius=radius,
            fill=(72, 72, 64, shadow),
        )
        base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(1.6)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def main():
    bg = Image.open(BG).convert("RGB")
    img = cover_crop(bg, (1080, 1350), focus_x=0.46, focus_y=0.48)
    img = soften_bg(img)

    # Diagonal product composition: copy occupies the quiet top, assets sit in a low product band.
    img.alpha_composite(sample_crop(), (12, 720))

    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse((560, 1046, 900, 1144), fill=(80, 78, 70, 34))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(15)))
    img.alpha_composite(bottle_crop(), (560, 498))

    d = ImageDraw.Draw(img)
    garamond = font(FONT_GARAMOND, 30)
    serif_kicker = font(FONT_SERIF, 34)
    serif_main = font(FONT_SERIF_BOLD, 78)
    serif_body = font(FONT_SERIF, 29)
    serif_small = font(FONT_SERIF, 23)
    sans = font(FONT_SANS_MED, 24)
    sans_small = font(FONT_SANS, 19)

    d.text((78, 94), "HERZ SKIN", font=garamond, fill=SUB_INK)
    d.line((79, 136, 218, 136), fill=WAKABA, width=3)

    d.text((80, 218), "フルボ酸でととのう", font=serif_kicker, fill=INK)
    d.text((78, 284), "潤い満ち肌", font=serif_main, fill=INK)
    d.line((82, 404, 454, 404), fill=WAKABA, width=2)

    d.text((82, 466), "化粧水前に、プラスワン美容", font=serif_body, fill=INK)
    d.text((84, 514), "Fulfillment Serum Water Intense 90", font=garamond, fill=SUB_INK)

    rounded_panel(img, (80, 600, 486, 690), 5, GOFUN[:3] + (232,), WAKABA, 2, 12)
    centered_text(d, (80, 600, 486, 690), "サンプルセット +\nインテンス90 現品", serif_small, INK, spacing=8)

    rounded_panel(img, (560, 1124, 1016, 1218), 4, WAKABA, None, 1, 14)
    centered_text(d, (560, 1124, 1016, 1218), "サンプルで試して、現品で続ける", sans, INK)
    d.text((788, 1266), "一滴ずつ、うるおいを満たす毎日へ。", font=serif_small, fill=SUB_INK, anchor="mm")

    d.rectangle((0, 1302, 1080, 1350), fill=USUTAMAGO)
    d.text((540, 1326), "フルフィルメント セラム ウォーター インテンス90", font=sans_small, fill=SUB_INK, anchor="mm")

    img.convert("RGB").save(OUT, quality=96)


if __name__ == "__main__":
    main()
