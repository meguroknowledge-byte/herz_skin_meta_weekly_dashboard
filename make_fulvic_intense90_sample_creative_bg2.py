from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


SRC = "018-250620Herzskin.jpg"
OUT = "herz_skin_fulvic_intense90_sample_bg2_1080x1350.png"

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


def cover_crop(src, size, focus_x=0.58, focus_y=0.50):
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


def soften(img):
    img = ImageEnhance.Color(img).enhance(0.58)
    img = ImageEnhance.Contrast(img).enhance(0.88)
    img = ImageEnhance.Brightness(img).enhance(1.08)

    w, h = img.size
    warm = Image.new("RGBA", (w, h), USUTAMAGO[:3] + (44,))
    img = Image.alpha_composite(img, warm)

    veil = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    px = veil.load()
    for y in range(h):
        for x in range(w):
            left = max(0, 1 - x / (w * 0.82))
            top = max(0, 1 - y / (h * 0.62))
            alpha = int(154 * (left ** 1.35) + 34 * (top ** 1.7))
            px[x, y] = GOFUN[:3] + (min(206, alpha),)
    return Image.alpha_composite(img, veil)


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
    src = Image.open(SRC).convert("RGB")
    img = cover_crop(src, (1080, 1350), focus_x=0.57, focus_y=0.48)
    img = soften(img)
    d = ImageDraw.Draw(img)

    garamond = font(FONT_GARAMOND, 31)
    serif_kicker = font(FONT_SERIF, 35)
    serif_main = font(FONT_SERIF_BOLD, 74)
    serif_body = font(FONT_SERIF, 31)
    serif_small = font(FONT_SERIF, 24)
    sans = font(FONT_SANS_MED, 24)
    sans_small = font(FONT_SANS, 19)

    d.text((76, 92), "HERZ SKIN", font=garamond, fill=SUB_INK)
    d.line((77, 134, 218, 134), fill=WAKABA, width=3)

    d.text((78, 214), "フルボ酸でととのう", font=serif_kicker, fill=INK)
    d.text((76, 276), "潤い満ち肌", font=serif_main, fill=INK)
    d.line((80, 392, 450, 392), fill=WAKABA, width=2)

    d.text((80, 444), "化粧水前に、プラスワン美容", font=serif_body, fill=INK)
    d.text((82, 496), "Fulfillment Serum Water Intense 90", font=garamond, fill=SUB_INK)

    rounded_panel(img, (74, 584, 500, 672), 5, GOFUN[:3] + (226,), WAKABA, 2, 12)
    centered_text(d, (74, 584, 500, 672), "サンプルセット +\nインテンス90 現品", serif_small, INK, spacing=8)

    rounded_panel(img, (560, 1094, 1018, 1194), 4, WAKABA, None, 1, 14)
    centered_text(d, (560, 1094, 1018, 1194), "サンプルで試して、現品で続ける", sans, INK)

    d.text((790, 1254), "肌になじむ一滴を、毎日のリズムへ。", font=serif_small, fill=SUB_INK, anchor="mm")

    d.rectangle((0, 1302, 1080, 1350), fill=USUTAMAGO)
    d.text((540, 1326), "フルフィルメント セラム ウォーター インテンス90", font=sans_small, fill=SUB_INK, anchor="mm")

    img.convert("RGB").save(OUT, quality=96)


if __name__ == "__main__":
    main()
