import cv2

try:
    import easyocr
    _HAS_EASYOCR = True
except ImportError:
    easyocr = None
    _HAS_EASYOCR = False

_reader = None

def _get_reader():
    global _reader
    if not _HAS_EASYOCR:
        return None
    if _reader is None:
        _reader = easyocr.Reader(['de', 'en'], gpu=False)
    return _reader

def ocr_in_roi_easy(screen_bgr, roi, search_text: str, min_conf: float = 0.4):
    reader = _get_reader()
    if reader is None:
        print("[EasyOCR] Nicht installiert.")
        return None

    x, y, w, h = roi
    if w <= 0 or h <= 0:
        return None

    sub = screen_bgr[y:y+h, x:x+w]
    sub_rgb = cv2.cvtColor(sub, cv2.COLOR_BGR2RGB)

    results = reader.readtext(sub_rgb)

    search_low = search_text.strip().lower()
    best = None
    best_conf = 0.0

    for box, text, conf in results:
        if conf < min_conf:
            continue
        clean = " ".join(text.split()).lower()
        if search_low in clean:
            if conf > best_conf:
                best_conf = conf
                best = (box, text, conf)

    if best is None:
        return None

    box, found_text, conf = best
    xs = [p[0] for p in box]
    ys = [p[1] for p in box]
    x1, x2 = min(xs), max(xs)
    y1, y2 = min(ys), max(ys)
    bw = int(x2 - x1)
    bh = int(y2 - y1)

    gx = x + int(x1)
    gy = y + int(y1)
    cx = gx + bw // 2
    cy = gy + bh // 2

    return (cx, cy), (gx, gy, bw, bh), float(conf), found_text
