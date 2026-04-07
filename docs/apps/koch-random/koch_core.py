import math
import random

def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))

def safe_int(value, default=3, min_value=0, max_value=6):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return clamp(parsed, min_value, max_value)

def safe_float(value, default=0.08, min_value=0.0, max_value=0.45):
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return clamp(parsed, min_value, max_value)

def normalize_points(points, width, height, padding=24):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    span_x = max(max_x - min_x, 1e-9)
    span_y = max(max_y - min_y, 1e-9)

    inner_w = max(width - 2 * padding, 1)
    inner_h = max(height - 2 * padding, 1)

    scale = min(inner_w / span_x, inner_h / span_y)

    out = []
    for x, y in points:
        sx = padding + (x - min_x) * scale
        sy = padding + (y - min_y) * scale
        sy = height - sy
        out.append((sx, sy))
    return out

def koch_curve(p1, p2, depth, randomness, rng):
    if depth == 0:
        return [p1, p2]

    x1, y1 = p1
    x2, y2 = p2

    dx = (x2 - x1) / 3.0
    dy = (y2 - y1) / 3.0

    a = (x1 + dx, y1 + dy)
    b = (x1 + 2.0 * dx, y1 + 2.0 * dy)

    mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)

    seg_len = math.hypot(dx, dy)
    base_height = seg_len * math.sqrt(3) / 2.0

    perp_x = dy
    perp_y = -dx
    perp_len = math.hypot(perp_x, perp_y) or 1.0
    perp_x /= perp_len
    perp_y /= perp_len

    height_scale = 1.0 + rng.uniform(-randomness, randomness)
    c = (
        mid[0] + perp_x * base_height * height_scale,
        mid[1] + perp_y * base_height * height_scale,
    )

    return (
        koch_curve(p1, a, depth - 1, randomness, rng)
        + koch_curve(a, c, depth - 1, randomness, rng)[1:]
        + koch_curve(c, b, depth - 1, randomness, rng)[1:]
        + koch_curve(b, p2, depth - 1, randomness, rng)[1:]
    )

def koch_snowflake(order, scale=1.0, randomness=0.08, seed=42):
    rng = random.Random(seed)
    height = math.sqrt(3) / 2.0 * scale

    p1 = (0.0, 0.0)
    p2 = (scale, 0.0)
    p3 = (scale / 2.0, height)

    points = (
        koch_curve(p1, p2, order, randomness, rng)
        + koch_curve(p2, p3, order, randomness, rng)[1:]
        + koch_curve(p3, p1, order, randomness, rng)[1:]
    )

    if points[0] != points[-1]:
        points.append(points[0])

    return points

def box_count_dimension(points, box_sizes=(8, 16, 32, 64, 128)):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max(max_x - min_x, 1e-9)
    span_y = max(max_y - min_y, 1e-9)

    log_eps = []
    log_n = []

    for size in box_sizes:
        occupied = set()
        for x, y in points:
            xi = min(size - 1, int(size * (x - min_x) / span_x))
            yi = min(size - 1, int(size * (y - min_y) / span_y))
            occupied.add((xi, yi))
        n = len(occupied)
        if n > 0:
            log_eps.append(math.log(1.0 / size))
            log_n.append(math.log(n))

    if len(log_eps) < 2:
        return None, log_eps, log_n, None, None

    x_mean = sum(log_eps) / len(log_eps)
    y_mean = sum(log_n) / len(log_n)

    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(log_eps, log_n))
    den = sum((x - x_mean) ** 2 for x in log_eps)

    if den == 0:
        return None, log_eps, log_n, None, None

    slope = num / den
    intercept = y_mean - slope * x_mean

    ss_res = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(log_eps, log_n))
    ss_tot = sum((y - y_mean) ** 2 for y in log_n)
    r_squared = None if ss_tot == 0 else 1.0 - ss_res / ss_tot

    return slope, log_eps, log_n, intercept, r_squared
