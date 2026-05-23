from PIL import Image, ImageDraw, ImageFont, ImageFilter


SRC = "/Users/meguro/Downloads/LIENA_0782.jpg のコピー.jpg"
REF = "/Users/meguro/Downloads/夏の肌、 なんとなく 不安なら。 (2).png"
OUT = "herz_skin_final_plusone_1080x1350.png"

FONT_BLACK = "/Library/Fonts/ZenKakuGothicNew-Black.ttf"
FONT_BOLD = "/Library/Fonts/ZenKakuGothicNew-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def cover_crop(src, size, focus_x=0.63, focus_y=0.50):
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


def add_left_readability(img):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    px = overlay.load()
    for y in range(h):
        for x in range(w):
            t = max(0, 1 - x / (w * 0.66))
            alpha = int(110 * (t ** 1.55))
            px[x, y] = (255, 255, 255, alpha)
    return Image.alpha_composite(img, overlay)


def rounded(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def centered_text(draw, box, text, fnt, fill, spacing=8):
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


def paste_sample_packets(base):
    ref = Image.open(REF).convert("RGBA")
    crop = ref.crop((0, 746, 408, 1350))
    # Feather only the top/right edge so the sample packet crop blends back into the photo.
    mask = Image.new("L", crop.size, 255)
    mp = mask.load()
    w, h = crop.size
    for y in range(h):
        for x in range(w):
            top_fade = min(1, y / 58)
            right_fade = min(1, (w - x) / 70) if x > w - 90 else 1
            mp[x, y] = int(255 * min(top_fade, right_fade))
    crop.putalpha(mask.filter(ImageFilter.GaussianBlur(1.4)))
    base.alpha_composite(crop, (0, 746))


def main():
    src = Image.open(SRC).convert("RGB")
    img = cover_crop(src, (1080, 1350), focus_x=0.66, focus_y=0.51)
    img = add_left_readability(img)
    paste_sample_packets(img)

    d = ImageDraw.Draw(img)
    ink = (20, 48, 61, 255)

    d.multiline_text(
        (80, 142),
        "夏肌、\nゆらぎが\n気になるなら",
        font=font(FONT_BLACK, 72),
        fill=ink,
        spacing=34,
    )

    d.text((82, 604), "化粧水前に、プラスワン美容", font=font(FONT_BLACK, 40), fill=ink)

    info_box = (406, 802, 1038, 962)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    rounded(sd, (info_box[0] + 6, info_box[1] + 7, info_box[2] + 6, info_box[3] + 7), 19, (0, 0, 0, 58))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(1.2)))
    rounded(d, info_box, 19, (255, 255, 255, 238), (17, 26, 31, 255), 4)
    centered_text(
        d,
        info_box,
        "化粧水のなじみにくさや\nメイクのりが気になる日に。",
        font(FONT_BLACK, 36),
        ink,
        spacing=14,
    )

    price_box = (674, 994, 1038, 1106)
    rounded(d, price_box, 42, (20, 58, 72, 255))
    centered_text(d, price_box, "送料のみ¥550(税込)", font(FONT_BLACK, 33), "white", spacing=0)

    d.text((810, 1164), "6日間で肌にお試し", font=font(FONT_BLACK, 47), fill=ink, anchor="mm")
    d.text(
        (410, 1238),
        "フルフィルメント セラム ウォーター インテンス90サンプルセット",
        font=font(FONT_BLACK, 18),
        fill=ink,
    )

    img.convert("RGB").save(OUT, quality=96)


if __name__ == "__main__":
    main()
