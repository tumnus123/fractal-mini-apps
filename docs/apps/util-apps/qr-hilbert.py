from PIL import Image, ImageDraw
import qrcode, cv2, os, shutil

url = "https://tumnus123.github.io/fractal-mini-apps"
out_path = "C:\\temp\\hilbert_qr_fractal_mini_apps_final.png"

def rot(n, x, y, rx, ry):
    if ry == 0:
        if rx == 1:
            x = n - 1 - x
            y = n - 1 - y
        x, y = y, x
    return x, y

def d2xy(order, d):
    n = 2 ** order
    x = y = 0
    t = d
    s = 1
    while s < n:
        rx = 1 & (t // 2)
        ry = 1 & (t ^ rx)
        x, y = rot(s, x, y, rx, ry)
        x += s * rx
        y += s * ry
        t //= 4
        s *= 2
    return x, y

def hilbert_points(order):
    n = 2 ** order
    return [d2xy(order, d) for d in range(n*n)]

# create a standard QR as image
qr = qrcode.QRCode(
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=16,
    border=6,  # extra quiet zone
)
qr.add_data(url)
qr.make(fit=True)
qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
w, h = qr_img.size

# create outer canvas with roomy decorative margin
margin = 120
img = Image.new("RGB", (w + margin*2, h + margin*2), "white")
img.paste(qr_img, (margin, margin))
draw = ImageDraw.Draw(img)

# draw Hilbert-curve-inspired border entirely in the outer margin
pts = hilbert_points(6)
n = 2**6

def scaled(points, x0, y0, w, h):
    return [(x0 + (x + 0.5)/n*w, y0 + (y + 0.5)/n*h) for x, y in points]

# Four bands outside the QR's quiet zone
top = scaled(pts, 24, 24, img.width - 48, 42)
bottom = scaled(pts, 24, img.height - 66, img.width - 48, 42)
left = scaled(pts, 24, 78, 42, img.height - 156)
right = scaled(pts, img.width - 66, 78, 42, img.height - 156)

for band in (top, bottom, left, right):
    draw.line(band, fill="black", width=4)

# optional corner motifs, still well away from QR
for x0, y0 in [(24,24),(img.width-66,24),(24,img.height-66),(img.width-66,img.height-66)]:
    mini = scaled(hilbert_points(4), x0, y0, 42, 42)
    draw.line(mini, fill="black", width=3)

img.save(out_path)

# verify decode
detector = cv2.QRCodeDetector()
val, points, _ = detector.detectAndDecode(cv2.imread(out_path))
print("Decoded:", repr(val))
print("PASS" if val == url else "FAIL")
print(out_path)