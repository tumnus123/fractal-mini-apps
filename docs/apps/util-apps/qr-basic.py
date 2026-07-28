# generate_qr_codes.py
# pip install qrcode[pil]

from pathlib import Path
import qrcode

OUTPUT_DIR = Path("qr_codes")
OUTPUT_DIR.mkdir(exist_ok=True)

FIGURES = {
    "chapter_01_figure_05": {
            "label": "Koch Snowflake Mini-App",
            "caption": "",
            "url": "https://tumnus123.github.io/fractal-mini-apps/docs/apps/koch_snowflake_rnd/"
    },
    "chapter_01_figure_06": {
                "label": "Dragon Curve Mini-App",
                "caption": "",
        "url": "https://tumnus123.github.io/fractal-mini-apps/docs/apps/dragon-curve-rnd/"
    },
    "chapter_01_figure_08": {
        "label": "Terrain Pyramid Mini-App",
        "caption": "",
        "url": "https://tumnus123.github.io/fractal-mini-apps/docs/apps/terrain-pyramid-rnd/"
    },
    "chapter_01_figure_09": {
        "label": "Figure 9",
        "caption": "The eponymous Mandelbrot Set, rendered using The Stone Soup Group's definitive program, Fractint.",
        "url": "https://www.fractint.org/",
    },
}


def make_qr(url: str, output_path: Path) -> None:
    qr = qrcode.QRCode(
        version=None,  # auto-size
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=4,  # required quiet zone
    )

    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    img.save(output_path)


def main() -> None:
    for key, figure in FIGURES.items():
        output_path = OUTPUT_DIR / f"{key}.png"
        make_qr(figure["url"], output_path)

        print(f"Created {output_path}")
        print(f"{figure['label']}. {figure['caption']}")
        print()

if __name__ == "__main__":
    main()