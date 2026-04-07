from js import document, Blob, URL
from pyodide.ffi import create_proxy
import random

from koch_core import (
    box_count_dimension,
    koch_snowflake,
    normalize_points,
    safe_float,
    safe_int,
)

WIDTH = 800
HEIGHT = 800
DIM_WIDTH = 800
DIM_HEIGHT = 500

current_svg_text = ""
_event_proxies = []

def qs(element_id):
    return document.getElementById(element_id)

def set_status(message):
    qs("status").textContent = message

def clear_svg(svg):
    while svg.firstChild:
        svg.removeChild(svg.firstChild)

def svg_el(tag, attrs=None):
    elem = document.createElementNS("http://www.w3.org/2000/svg", tag)
    if attrs:
        for key, value in attrs.items():
            elem.setAttribute(key, str(value))
    return elem

def read_inputs():
    order = safe_int(qs("order").value, default=3, min_value=0, max_value=6)
    randomness = safe_float(qs("randomness").value, default=0.08, min_value=0.0, max_value=0.45)
    try:
        seed = int(qs("seed").value)
    except ValueError:
        seed = 42
    show_dimension = bool(qs("show-dimension").checked)
    return order, randomness, seed, show_dimension

def update_labels():
    qs("order-value").textContent = qs("order").value
    qs("randomness-value").textContent = f"{float(qs('randomness').value):.2f}"

def polyline_points_str(points):
    return " ".join(f"{x:.3f},{y:.3f}" for x, y in points)

def draw_main_plot(points):
    svg = qs("plot")
    clear_svg(svg)

    bg = svg_el("rect", {"x": 0, "y": 0, "width": WIDTH, "height": HEIGHT, "fill": "white"})
    svg.appendChild(bg)

    polyline = svg_el("polyline", {
        "points": polyline_points_str(points),
        "fill": "none",
        "stroke": "#111827",
        "stroke-width": 1.5,
        "stroke-linejoin": "round",
        "stroke-linecap": "round",
    })
    svg.appendChild(polyline)

def draw_dimension_plot(log_eps, log_n, slope, intercept):
    svg = qs("dimension-plot")
    clear_svg(svg)

    bg = svg_el("rect", {"x": 0, "y": 0, "width": DIM_WIDTH, "height": DIM_HEIGHT, "fill": "white"})
    svg.appendChild(bg)

    left, right = 70, 30
    top, bottom = 30, 55
    inner_w = DIM_WIDTH - left - right
    inner_h = DIM_HEIGHT - top - bottom

    x_min = min(log_eps)
    x_max = max(log_eps)
    y_min = min(log_n)
    y_max = max(log_n)

    x_span = max(x_max - x_min, 1e-9)
    y_span = max(y_max - y_min, 1e-9)

    def sx(x):
        return left + (x - x_min) / x_span * inner_w

    def sy(y):
        return top + inner_h - (y - y_min) / y_span * inner_h

    svg.appendChild(svg_el("line", {
        "x1": left, "y1": top + inner_h, "x2": left + inner_w, "y2": top + inner_h,
        "stroke": "#64748b", "stroke-width": 1
    }))
    svg.appendChild(svg_el("line", {
        "x1": left, "y1": top, "x2": left, "y2": top + inner_h,
        "stroke": "#64748b", "stroke-width": 1
    }))

    for x, y in zip(log_eps, log_n):
        svg.appendChild(svg_el("circle", {
            "cx": sx(x), "cy": sy(y), "r": 4.5, "fill": "#2563eb"
        }))

    x1, x2 = x_min, x_max
    y1 = intercept + slope * x1
    y2 = intercept + slope * x2
    svg.appendChild(svg_el("line", {
        "x1": sx(x1), "y1": sy(y1), "x2": sx(x2), "y2": sy(y2),
        "stroke": "#dc2626", "stroke-width": 2, "stroke-dasharray": "8 6"
    }))

    x_label = svg_el("text", {
        "x": left + inner_w / 2, "y": DIM_HEIGHT - 16,
        "text-anchor": "middle", "fill": "#334155", "font-size": 16
    })
    x_label.textContent = "log(1 / ε)"
    svg.appendChild(x_label)

    y_label = svg_el("text", {
        "x": 20, "y": top + inner_h / 2,
        "text-anchor": "middle", "fill": "#334155", "font-size": 16,
        "transform": f"rotate(-90 20 {top + inner_h / 2})"
    })
    y_label.textContent = "log(N(ε))"
    svg.appendChild(y_label)

def download_svg(event=None):
    global current_svg_text
    if not current_svg_text:
        set_status("Nothing to download yet.")
        return

    blob = Blob.new([current_svg_text], {"type": "image/svg+xml"})
    url = URL.createObjectURL(blob)

    anchor = document.createElement("a")
    anchor.href = url
    anchor.download = "koch-random.svg"
    anchor.click()

    URL.revokeObjectURL(url)
    set_status("SVG downloaded.")

def randomize_seed(event=None):
    qs("seed").value = str(random.randint(0, 999999))
    redraw()

def redraw(event=None):
    global current_svg_text
    update_labels()
    order, randomness, seed, show_dimension = read_inputs()

    raw_points = koch_snowflake(order=order, randomness=randomness, seed=seed)
    points = normalize_points(raw_points, WIDTH, HEIGHT, padding=26)

    draw_main_plot(points)

    dimension, log_eps, log_n, intercept, r_squared = box_count_dimension(raw_points)
    if dimension is None:
        qs("dimension-label").textContent = "N/A"
    else:
        label = f"{dimension:.4f}"
        if r_squared is not None:
            label += f"  (r² {r_squared:.4f})"
        qs("dimension-label").textContent = label

    dimension_card = qs("dimension-card")
    if show_dimension and dimension is not None:
        dimension_card.classList.remove("hidden")
        draw_dimension_plot(log_eps, log_n, dimension, intercept)
    else:
        dimension_card.classList.add("hidden")

    current_svg_text = qs("plot").outerHTML
    set_status(f"Rendered order {order}, randomness {randomness:.2f}, seed {seed}.")

def bind_events():
    for element_id in ["order", "randomness", "seed", "show-dimension"]:
        element = qs(element_id)
        proxy = create_proxy(lambda event, eid=element_id: redraw())
        _event_proxies.append(proxy)
        event_name = "input" if element_id != "show-dimension" else "change"
        element.addEventListener(event_name, proxy)

bind_events()
redraw()

