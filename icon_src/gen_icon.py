"""
Tạo bộ icon thương hiệu MỚI theo đúng design system Premium Blue Enterprise
(thay bộ icon đồng/nâu cũ, lệch với giao diện đã redesign).

Ý tưởng: mặt cắt lõi cáp điện (ring) màu trắng nổi trên nền gradient xanh
thương hiệu 135deg #0068FF -> #2388FF — nhất quán với --primary / gradient
dùng trong toàn bộ app.

Xuất ra:
  assets/icon-192.png              (PWA, có padding an toàn cho maskable)
  assets/icon-512.png              (PWA, có padding an toàn cho maskable)
  icon_src/icon-1024.png           (master, dùng làm nguồn cho Capacitor assets)
  android-app/resources/icon.png   (nguồn icon cho @capacitor/assets)
  android-app/resources/splash.png (nguồn splash cho @capacitor/assets)
  electron-app/build/icon.ico      (Windows, đa kích thước 16..256)
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SS = 4
SIZE = 1024
S = SIZE * SS

TOP = np.array([0x00, 0x68, 0xFF], dtype=np.float64)
BOT = np.array([0x23, 0x88, 0xFF], dtype=np.float64)


def make_gradient(size):
    ys, xs = np.mgrid[0:size, 0:size]
    t = (xs.astype(np.float64) + ys.astype(np.float64)) / (2 * (size - 1))
    t = np.clip(t, 0, 1)[..., None]
    rgb = TOP[None, None, :] * (1 - t) + BOT[None, None, :] * t
    return rgb.astype(np.uint8)


def cable_ring_mask(size, outer_ratio, inner_ratio):
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    c = size / 2
    ro = size * outer_ratio
    ri = size * inner_ratio
    d.ellipse([c - ro, c - ro, c + ro, c + ro], fill=255)
    d.ellipse([c - ri, c - ri, c + ri, c + ri], fill=0)
    return mask


def build_master():
    grad = make_gradient(S)
    base = Image.fromarray(grad, "RGB").convert("RGBA")

    shadow_mask = cable_ring_mask(S, 0.335, 0.155)
    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    shadow.paste((0, 30, 110, 90), (0, 0), shadow_mask)
    shadow = shadow.filter(ImageFilter.GaussianBlur(S * 0.01))
    base = Image.alpha_composite(base, shadow)

    ring_mask = cable_ring_mask(S, 0.32, 0.165)
    ring = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ring.paste((255, 255, 255, 255), (0, 0), ring_mask)
    base = Image.alpha_composite(base, ring)

    hi_mask = cable_ring_mask(S, 0.318, 0.30)
    hi = Image.new("L", (S, S), 0)
    grad_hi = Image.new("L", (S, S), 0)
    gd = ImageDraw.Draw(grad_hi)
    c = S / 2
    gd.ellipse([c - S * 0.34, c - S * 0.34, c + S * 0.10, c + S * 0.10], fill=90)
    hi = Image.composite(grad_hi, Image.new("L", (S, S), 0), hi_mask)
    hi_layer = Image.new("RGBA", (S, S), (255, 255, 255, 0))
    hi_layer.putalpha(hi)
    base = Image.alpha_composite(base, hi_layer)

    return base.resize((SIZE, SIZE), Image.LANCZOS)


def make_maskable(master, pad_ratio=0.10):
    size = master.size[0]
    inner = int(size * (1 - 2 * pad_ratio))
    inner_img = master.resize((inner, inner), Image.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    grad = make_gradient(size)
    bgfull = Image.fromarray(grad, "RGB").convert("RGBA")
    canvas.paste(bgfull, (0, 0))
    off = (size - inner) // 2
    canvas.paste(inner_img, (off, off), inner_img)
    return canvas


if __name__ == "__main__":
    import os
    os.makedirs("/home/claude/proj/MES_CABLE_WEB/assets", exist_ok=True)
    os.makedirs("/home/claude/proj/icon_src", exist_ok=True)
    os.makedirs("/home/claude/proj/MES_CABLE_WEB/electron-app/build", exist_ok=True)
    os.makedirs("/home/claude/proj/MES_CABLE_WEB/android-app/resources", exist_ok=True)

    master = build_master()
    master.save("/home/claude/proj/icon_src/icon-1024.png")
    master.save("/home/claude/proj/MES_CABLE_WEB/android-app/resources/icon.png")

    maskable_512 = make_maskable(master, pad_ratio=0.10)
    maskable_512.resize((512, 512), Image.LANCZOS).save("/home/claude/proj/MES_CABLE_WEB/assets/icon-512.png")
    maskable_512.resize((192, 192), Image.LANCZOS).save("/home/claude/proj/MES_CABLE_WEB/assets/icon-192.png")

    ico_sizes = [16, 24, 32, 48, 64, 128, 256]
    master.save(
        "/home/claude/proj/MES_CABLE_WEB/electron-app/build/icon.ico",
        sizes=[(s, s) for s in ico_sizes],
    )

    splash = Image.new("RGBA", (2732, 2732), (244, 247, 251, 255))
    mark = master.resize((900, 900), Image.LANCZOS)
    splash.paste(mark, ((2732 - 900) // 2, (2732 - 900) // 2), mark)
    splash.convert("RGB").save("/home/claude/proj/MES_CABLE_WEB/android-app/resources/splash.png")

    print("done")
