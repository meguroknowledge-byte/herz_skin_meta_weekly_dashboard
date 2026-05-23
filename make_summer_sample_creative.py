from PIL import Image, ImageDraw, ImageFont, ImageFilter


SRC = "/Users/meguro/Downloads/LIENA_0782.jpg のコピー.jpg"
FONT_BLACK = "/Library/Fonts/ZenKakuGothicNew-Black.ttf"
FONT_BOLD = "/Library/Fonts/ZenKakuGothicNew-Bold.ttf"
FONT_MED = "/Library/Fonts/ZenKakuGothicNew-Medium.ttf"
FONT_SERIF_HEAVY = "/Library/Fonts/SourceHanSerif-Heavy.otf"


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


def add_text_gradient(img, strength=188):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    px = overlay.load()
    for y in range(h):
        for x in range(w):
            t = max(0, 1 - x / (w * 0.72))
            alpha = int(strength * (t ** 1.7))
            px[x, y] = (255, 255, 255, alpha)
    return Image.alpha_composite(img, overlay)


def add_soft_vignette(img):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    d = ImageDraw.Draw(overlay)
    d.rectangle((0, 0, w, h), fill=(245, 251, 255, 18))
    d.ellipse((int(w * 0.58), int(h * 0.14), int(w * 1.35), int(h * 0.78)), fill=(255, 255, 255, 24))
    return Image.alpha_composite(img, overlay)


def text(draw, xy, content, fnt, fill, anchor=None, spacing=8, stroke_width=0, stroke_fill=None):
    draw.multiline_text(
        xy,
        content,
        font=fnt,
        fill=fill,
        anchor=anchor,
        spacing=spacing,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )


def rounded(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def centered_box_text(draw, box, content, fnt, fill, spacing=8, left_padding=34):
    lines = content.split("\n")
    line_heights = []
    max_width = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=fnt)
        line_heights.append(bbox[3] - bbox[1])
        max_width = max(max_width, bbox[2] - bbox[0])
    total_height = sum(line_heights) + spacing * (len(lines) - 1)
    y = box[1] + (box[3] - box[1] - total_height) / 2 - 2
    x = box[0] + left_padding
    draw.multiline_text((x, y), content, font=fnt, fill=fill, spacing=spacing)


def gradient_text(base, xy, content, fnt, top, bottom, stroke=(255, 255, 255, 230), shadow=(0, 52, 150, 125), spacing=8):
    x, y = xy
    tmp = Image.new("L", base.size, 0)
    md = ImageDraw.Draw(tmp)
    md.multiline_text((x, y), content, font=fnt, fill=255, spacing=spacing, stroke_width=2, stroke_fill=255)

    stroke_mask = Image.new("L", base.size, 0)
    sd = ImageDraw.Draw(stroke_mask)
    sd.multiline_text((x, y), content, font=fnt, fill=255, spacing=spacing, stroke_width=6, stroke_fill=255)

    glow = Image.new("RGBA", base.size, shadow)
    glow.putalpha(stroke_mask.filter(ImageFilter.GaussianBlur(3)))
    base.alpha_composite(glow)

    edge = Image.new("RGBA", base.size, stroke)
    edge_mask = Image.new("L", base.size, 0)
    edge_px = edge_mask.load()
    stroke_px = stroke_mask.load()
    text_px = tmp.load()
    w, h = base.size
    for yy in range(h):
        for xx in range(w):
            edge_px[xx, yy] = max(0, stroke_px[xx, yy] - text_px[xx, yy])
    edge.putalpha(edge_mask)
    base.alpha_composite(edge)

    grad = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gp = grad.load()
    tr, tg, tb, ta = top
    br, bg, bb, ba = bottom
    for yy in range(base.size[1]):
        t = yy / max(1, base.size[1] - 1)
        r = int(tr * (1 - t) + br * t)
        g = int(tg * (1 - t) + bg * t)
        b = int(tb * (1 - t) + bb * t)
        a = int(ta * (1 - t) + ba * t)
        for xx in range(base.size[0]):
            gp[xx, yy] = (r, g, b, a)

    grad.putalpha(Image.eval(tmp, lambda p: int(p * 0.78)))
    base.alpha_composite(grad)

    shine = Image.new("L", base.size, 0)
    shd = ImageDraw.Draw(shine)
    shd.multiline_text((x - 3, y - 3), content, font=fnt, fill=160, spacing=spacing)
    highlight = Image.new("RGBA", base.size, (255, 255, 255, 115))
    highlight.putalpha(shine.filter(ImageFilter.GaussianBlur(0.4)))
    base.alpha_composite(highlight)


def soft_watermark_text(base, xy, content, fnt, top, bottom, spacing=8):
    x, y = xy
    w, h = base.size
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.multiline_text((x, y), content, font=fnt, fill=255, spacing=spacing, stroke_width=1, stroke_fill=255)

    edge_mask = Image.new("L", (w, h), 0)
    ed = ImageDraw.Draw(edge_mask)
    ed.multiline_text((x, y), content, font=fnt, fill=255, spacing=spacing, stroke_width=4, stroke_fill=255)

    white_edge = Image.new("RGBA", (w, h), (255, 255, 255, 210))
    white_edge.putalpha(Image.eval(edge_mask, lambda p: int(p * 0.55)))
    base.alpha_composite(white_edge)

    grad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gp = grad.load()
    tr, tg, tb, ta = top
    br, bg, bb, ba = bottom
    for yy in range(h):
        t = yy / max(1, h - 1)
        r = int(tr * (1 - t) + br * t)
        g = int(tg * (1 - t) + bg * t)
        b = int(tb * (1 - t) + bb * t)
        a = int(ta * (1 - t) + ba * t)
        for xx in range(w):
            gp[xx, yy] = (r, g, b, a)
    grad.putalpha(Image.eval(mask, lambda p: int(p * 0.68)))
    base.alpha_composite(grad)

    shine = Image.new("RGBA", (w, h), (255, 255, 255, 95))
    shine_mask = Image.new("L", (w, h), 0)
    sd = ImageDraw.Draw(shine_mask)
    sd.multiline_text((x - 2, y - 2), content, font=fnt, fill=130, spacing=spacing)
    shine.putalpha(shine_mask)
    base.alpha_composite(shine)


def make_feed(src):
    w, h = 1080, 1350
    img = cover_crop(src, (w, h), focus_x=0.66, focus_y=0.51)
    img = add_soft_vignette(add_text_gradient(img, 205))
    d = ImageDraw.Draw(img)

    ink = (48, 68, 86, 255)
    sub = (76, 96, 112, 245)
    pale = (255, 255, 255, 235)

    text(d, (76, 94), "導入美容液", font(FONT_BOLD, 34), sub)
    d.line((76, 146, 238, 146), fill=(96, 129, 154, 150), width=3)

    text(d, (76, 218), "夏の肌、", font(FONT_BLACK, 70), ink)
    text(d, (76, 312), "なんとなく\n不安なら。", font(FONT_BLACK, 82), ink, spacing=9)
    text(d, (76, 528), "いつものケアにプラスワン美容を", font(FONT_BOLD, 33), sub)
    text(d, (74, 586), "6日間", font(FONT_BLACK, 124), ink, stroke_width=2, stroke_fill=pale)

    info_box = (74, 768, 746, 902)
    rounded(d, info_box, 10, (255, 255, 255, 198), (140, 170, 190, 82), 2)
    centered_box_text(d, info_box, "乾燥、ゆらぎ、メイクのりが\n気になる季節に。", font(FONT_BOLD, 32), sub, spacing=8)

    rounded(d, (74, 1014, 680, 1096), 41, (55, 78, 96, 224))
    text(d, (377, 1054), "送料550円(税込)で気軽にお試し", font(FONT_BOLD, 31), "white", anchor="mm")
    text(d, (76, 1158), "フルフィルメント セラム ウォーター インテンス 90", font(FONT_BOLD, 25), (56, 82, 100, 230))
    text(d, (76, 1198), "6日間で試す導入美容液", font(FONT_BOLD, 31), (56, 82, 100, 230))

    out = img.convert("RGB")
    out.save("herz_skin_summer_sample_feed_4x5_v2.png", quality=96)
    out.save("herz_skin_summer_sample_1080x1350.png", quality=96)


def make_feed_watermark(src):
    w, h = 1080, 1350
    img = cover_crop(src, (w, h), focus_x=0.66, focus_y=0.51)
    img = add_soft_vignette(add_text_gradient(img, 198))
    d = ImageDraw.Draw(img)

    sub = (66, 88, 108, 245)

    text(d, (76, 94), "導入美容液", font(FONT_BOLD, 34), sub)
    d.line((76, 146, 238, 146), fill=(96, 129, 154, 150), width=3)

    gradient_text(
        img,
        (68, 220),
        "夏の肌、\nなんとなく\n不安なら。",
        font(FONT_SERIF_HEAVY, 76),
        (0, 113, 230, 190),
        (0, 26, 118, 230),
        stroke=(255, 255, 255, 230),
        shadow=(0, 49, 150, 130),
        spacing=5,
    )
    d = ImageDraw.Draw(img)
    text(d, (76, 538), "", font(FONT_BOLD, 33), sub)
    gradient_text(
        img,
        (70, 590),
        "6日間",
        font(FONT_SERIF_HEAVY, 128),
        (84, 198, 245, 190),
        (0, 32, 136, 235),
        stroke=(255, 255, 255, 236),
        shadow=(0, 50, 145, 120),
        spacing=2,
    )
    d = ImageDraw.Draw(img)

    text(d, (76, 742), "いつものケアにプラスワン美容を", font(FONT_BOLD, 33), sub)
    rounded(d, (74, 806, 746, 940), 10, (255, 255, 255, 198), (91, 151, 203, 115), 2)
    text(d, (108, 840), "乾燥、ゆらぎ、メイクのりが\n気になる季節に。", font(FONT_BOLD, 32), sub, spacing=8)

    rounded(d, (74, 1014, 690, 1096), 41, (9, 37, 106, 220))
    text(d, (382, 1054), "送料550円(税込)で気軽にお試し", font(FONT_BOLD, 31), "white", anchor="mm")
    text(d, (76, 1168), "サンプル6日間セット", font(FONT_BOLD, 32), (31, 67, 116, 230))

    img.convert("RGB").save("herz_skin_summer_sample_1080x1350_watermark.png", quality=96)


def make_feed_watermark_soft(src):
    w, h = 1080, 1350
    img = cover_crop(src, (w, h), focus_x=0.66, focus_y=0.51)
    img = add_soft_vignette(add_text_gradient(img, 205))
    d = ImageDraw.Draw(img)

    sub = (61, 83, 103, 245)

    text(d, (76, 94), "導入美容液", font(FONT_BOLD, 34), sub)
    d.line((76, 146, 238, 146), fill=(96, 129, 154, 150), width=3)

    soft_watermark_text(
        img,
        (70, 220),
        "夏の肌、\nなんとなく\n不安なら。",
        font(FONT_SERIF_HEAVY, 78),
        (0, 121, 220, 185),
        (0, 34, 125, 220),
        spacing=5,
    )
    d = ImageDraw.Draw(img)
    text(d, (76, 538), "", font(FONT_BOLD, 33), sub)
    soft_watermark_text(
        img,
        (70, 590),
        "6日間",
        font(FONT_SERIF_HEAVY, 128),
        (54, 185, 232, 180),
        (0, 36, 132, 230),
        spacing=2,
    )
    d = ImageDraw.Draw(img)

    text(d, (76, 742), "いつものケアにプラスワン美容を", font(FONT_BOLD, 33), sub)
    rounded(d, (74, 806, 746, 940), 10, (255, 255, 255, 200), (85, 146, 198, 95), 2)
    text(d, (108, 840), "乾燥、ゆらぎ、メイクのりが\n気になる季節に。", font(FONT_BOLD, 32), sub, spacing=8)

    rounded(d, (74, 1014, 690, 1096), 41, (22, 69, 122, 218))
    text(d, (382, 1054), "送料550円(税込)で気軽にお試し", font(FONT_BOLD, 31), "white", anchor="mm")
    text(d, (76, 1168), "サンプル6日間セット", font(FONT_BOLD, 32), (39, 82, 123, 230))

    img.convert("RGB").save("herz_skin_summer_sample_1080x1350_watermark_soft.png", quality=96)


def make_square(src):
    w, h = 1080, 1080
    img = cover_crop(src, (w, h), focus_x=0.62, focus_y=0.50)
    img = add_soft_vignette(add_text_gradient(img, 215))
    d = ImageDraw.Draw(img)

    ink = (45, 65, 84, 255)
    sub = (76, 96, 112, 245)

    text(d, (70, 76), "導入美容液", font(FONT_BOLD, 31), sub)
    d.line((70, 124, 220, 124), fill=(96, 129, 154, 150), width=3)

    text(d, (70, 182), "夏の肌、\nなんとなく\n不安なら。", font(FONT_BLACK, 70), ink, spacing=8)
    text(d, (70, 456), "いつものケアにプラスワン美容を", font(FONT_BOLD, 29), sub)
    text(d, (68, 508), "6日間", font(FONT_BLACK, 108), ink, stroke_width=2, stroke_fill=(255, 255, 255, 235))

    rounded(d, (68, 694, 708, 818), 10, (255, 255, 255, 202), (140, 170, 190, 82), 2)
    text(d, (100, 724), "乾燥、ゆらぎ、メイクのりが\n気になる季節に。", font(FONT_BOLD, 29), sub, spacing=7)

    rounded(d, (68, 898, 650, 972), 37, (55, 78, 96, 226))
    text(d, (359, 934), "送料550円(税込)で気軽にお試し", font(FONT_BOLD, 29), "white", anchor="mm")

    img.convert("RGB").save("herz_skin_summer_sample_square_1x1_v2.png", quality=96)


if __name__ == "__main__":
    source = Image.open(SRC).convert("RGB")
    make_feed(source)
    make_feed_watermark(source)
    make_feed_watermark_soft(source)
    make_square(source)
