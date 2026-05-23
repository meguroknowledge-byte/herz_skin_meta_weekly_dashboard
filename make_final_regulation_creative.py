from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


SRC = "/Users/meguro/Downloads/LIENA_0782.jpg のコピー.jpg"
REF = "/Users/meguro/Downloads/夏の肌、 なんとなく 不安なら。 (2).png"
OUT = "herz_skin_final_regulation_1080x1350.png"

FONT_SERIF = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
FONT_SERIF_BOLD = "/Library/Fonts/SourceHanSerif-SemiBold.otf"
FONT_SANS = "/Library/Fonts/ZenKakuGothicNew-Regular.ttf"
FONT_SANS_MED = "/Library/Fonts/ZenKakuGothicNew-Medium.ttf"
FONT_GARAMOND = "/Library/Fonts/GARA.TTF"

GOFUN = (250, 250, 248, 255)
USUTAMAGO = (247, 244, 225, 255)
OMINAESHI = (245, 244, 174, 255)
TSUKI = (232, 242, 250, 255)
WAKABA = (210, 215, 181, 255)
INK = (69, 69, 68, 255)
SUB_INK = (107, 107, 104, 255)


def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


def cover_crop(src, size, focus_x=0.66, focus_y=0.51):
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


def tint_for_regulation(img):
    img = ImageEnhance.Color(img).enhance(0.66)
    img = ImageEnhance.Contrast(img).enhance(0.92)
    img = ImageEnhance.Brightness(img).enhance(1.06)

    w, h = img.size
    warm = Image.new("RGBA", (w, h), USUTAMAGO[:3] + (42,))
    img = Image.alpha_composite(img, warm)

    mist = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    px = mist.load()
    for y in range(h):
        for x in range(w):
            left = max(0, 1 - x / (w * 0.64))
            top = max(0, 1 - y / (h * 0.72))
            alpha = int(152 * (left ** 1.35) + 38 * (top ** 2.2))
            px[x, y] = GOFUN[:3] + (min(205, alpha),)
    return Image.alpha_composite(img, mist)


def paste_sample_packets(base):
    ref = Image.open(REF).convert("RGBA")
    crop = ref.crop((0, 746, 408, 1350))
    crop = ImageEnhance.Color(crop).enhance(0.55)
    crop = ImageEnhance.Brightness(crop).enhance(1.08)

    mask = Image.new("L", crop.size, 255)
    mp = mask.load()
    w, h = crop.size
    for y in range(h):
        for x in range(w):
            top_fade = min(1, y / 76)
            right_fade = min(1, (w - x) / 92) if x > w - 112 else 1
            mp[x, y] = int(210 * min(top_fade, right_fade))
    crop.putalpha(mask.filter(ImageFilter.GaussianBlur(1.8)))
    base.alpha_composite(crop, (0, 746))


def draw_centered(draw, box, text, fnt, fill, spacing=8):
    lines = text.split("\n")
    heights = []
    for line in lines:
        b = draw.textbbox((0, 0), line, font=fnt)
        heights.append(b[3] - b[1])
    total_h = sum(heights) + spacing * (len(lines) - 1)
    y = box[1] + (box[3] - box[1] - total_h) / 2 - 2
    for line, lh in zip(lines, heights):
        b = draw.textbbox((0, 0), line, font=fnt)
        x = box[0] + (box[2] - box[0] - (b[2] - b[0])) / 2
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh + spacing


def rounded_panel(base, box, radius, fill, outline=None, width=1, shadow_alpha=0):
    d = ImageDraw.Draw(base)
    if shadow_alpha:
        shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle(
            (box[0] + 4, box[1] + 5, box[2] + 4, box[3] + 5),
            radius=radius,
            fill=(80, 80, 72, shadow_alpha),
        )
        base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(1.4)))
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def main():
    src = Image.open(SRC).convert("RGB")
    img = cover_crop(src, (1080, 1350))
    img = tint_for_regulation(img)
    paste_sample_packets(img)
    d = ImageDraw.Draw(img)

    serif_title = font(FONT_SERIF_BOLD, 67)
    serif_mid = font(FONT_SERIF, 34)
    serif_small = font(FONT_SERIF, 26)
    sans = font(FONT_SANS_MED, 27)
    sans_small = font(FONT_SANS, 20)
    garamond = font(FONT_GARAMOND, 31)

    d.text((78, 116), "HERZ SKIN", font=garamond, fill=SUB_INK)
    d.line((79, 158, 218, 158), fill=WAKABA, width=3)

    d.multiline_text(
        (76, 226),
        "夏肌、\nゆらぎが\n気になるなら",
        font=serif_title,
        fill=INK,
        spacing=19,
    )

    d.text((80, 570), "化粧水前に、プラスワン美容", font=serif_mid, fill=INK)
    d.text((82, 626), "Fulfillment Serum Water Intense 90", font=garamond, fill=SUB_INK)

    rounded_panel(img, (408, 790, 1038, 944), 6, GOFUN[:3] + (228,), WAKABA, 2, 18)
    draw_centered(
        d,
        (408, 790, 1038, 944),
        "化粧水のなじみにくさや\nメイクのりが気になる日に。",
        serif_mid,
        INK,
        spacing=12,
    )

    rounded_panel(img, (672, 986, 1038, 1088), 4, WAKABA, None, 1, 14)
    draw_centered(d, (672, 986, 1038, 1088), "送料のみ ¥550(税込)", sans, INK, spacing=0)

    d.text((828, 1160), "6日間で肌にお試し", font=serif_mid, fill=INK, anchor="mm")
    d.text(
        (410, 1238),
        "フルフィルメント セラム ウォーター インテンス90 サンプルセット",
        font=sans_small,
        fill=SUB_INK,
    )

    d.rectangle((0, 1318, 1080, 1350), fill=USUTAMAGO)
    d.text((540, 1332), "初回限定 / サンプルセット", font=serif_small, fill=SUB_INK, anchor="mm")

    img.convert("RGB").save(OUT, quality=96)


if __name__ == "__main__":
    main()
