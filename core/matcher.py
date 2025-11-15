import cv2

def template_match(screen_bgr, template_bgr):
    screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
    tpl_gray = cv2.cvtColor(template_bgr, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(screen_gray, tpl_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    h, w = template_bgr.shape[:2]
    return float(max_val), (int(max_loc[0]), int(max_loc[1])), int(w), int(h)

def multi_crop_match(screen_bgr, template_bgr, scales=(0.3, 0.6, 1.0)):
    best_val = -1.0
    best_loc = (0, 0)
    best_w = 0
    best_h = 0
    h, w = template_bgr.shape[:2]
    screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)

    for s in scales:
        ch = int(h * s)
        cw = int(w * s)
        if ch < 5 or cw < 5:
            continue
        y0 = (h - ch) // 2
        x0 = (w - cw) // 2
        crop = template_bgr[y0:y0+ch, x0:x0+cw]
        crop_gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(screen_gray, crop_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val > best_val:
            best_val = float(max_val)
            best_loc = (int(max_loc[0]), int(max_loc[1]))
            best_w = cw
            best_h = ch

    return best_val, best_loc, best_w, best_h
