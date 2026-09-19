#!/usr/bin/env python3
"""Build Fig02 junction map PNG from published lat/lon (OSM tiles + markers).

Output: Fig02_junction_map.png (RGB, 300 dpi, no Matplotlib Software metadata).
"""
from __future__ import annotations

import os
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import requests
from PIL import Image

OUT = Path(__file__).resolve().parent
OUT_PNG = Path(os.environ.get("FIG02_OUT", str(OUT / "Fig02_junction_map.png")))
INK = "#1a2332"
JUNCTIONS = [
    ("Alankar Chowk", 18.52804, 73.87624),
    ("Jehangir Chowk", 18.5304, 73.8767),
    ("RTO Chowk", 18.5305, 73.8636),
]


def lonlat_to_pixel(lon: float, lat: float, z: int, tile_size: int = 256) -> tuple[float, float]:
    n = 2.0**z
    x = (lon + 180.0) / 360.0 * n
    lat_r = np.radians(lat)
    y = (1.0 - np.log(np.tan(lat_r) + 1.0 / np.cos(lat_r)) / np.pi) / 2.0 * n
    return x * tile_size, y * tile_size


def fetch_tile(x: int, y: int, z: int) -> Image.Image:
    url = f"https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    headers = {"User-Agent": "CCTV-manuscript-figures/1.0 (research; local rebuild)"}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return Image.open(BytesIO(r.content)).convert("RGB")


def build_map(z: int = 15, pad_tiles: int = 0) -> tuple[Image.Image, float, float, int]:
    lats = [j[1] for j in JUNCTIONS]
    lons = [j[2] for j in JUNCTIONS]
    lat_c = float(np.mean(lats))
    lon_c = float(np.mean(lons))
    cx, cy = lonlat_to_pixel(lon_c, lat_c, z)
    # tighter crop around the three junctions
    tx0 = int(cx // 256) - pad_tiles - 1
    ty0 = int(cy // 256) - pad_tiles - 1
    nx = 2 * pad_tiles + 3
    ny = 2 * pad_tiles + 3
    canvas = Image.new("RGB", (nx * 256, ny * 256))
    for i in range(nx):
        for j in range(ny):
            tile = fetch_tile(tx0 + i, ty0 + j, z)
            canvas.paste(tile, (i * 256, j * 256))
    return canvas, tx0 * 256, ty0 * 256, z


def save_clean_png(path: Path, fig: plt.Figure) -> None:
    """Save RGB PNG at 300 dpi with no Software/exif metadata."""
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    im = Image.open(buf).convert("RGB")
    im.save(path, format="PNG", dpi=(300, 300), optimize=True)
    print(f"Wrote {path} size={im.size}")


def main() -> int:
    try:
        base, ox, oy, z = build_map()
    except Exception as e:
        print(f"OSM tile fetch failed ({e}); writing schematic fallback")
        return schematic_fallback()

    fig, ax = plt.subplots(figsize=(8.5, 6.5), dpi=150)
    ax.imshow(base)
    ax.set_axis_off()
    for name, lat, lon in JUNCTIONS:
        px, py = lonlat_to_pixel(lon, lat, z)
        x = px - ox
        y = py - oy
        ax.scatter(
            [x],
            [y],
            s=140,
            c=INK,
            edgecolors="white",
            linewidths=2.0,
            zorder=5,
        )
        ax.annotate(
            name,
            (x, y),
            textcoords="offset points",
            xytext=(12, 10),
            fontsize=11,
            fontweight="bold",
            color=INK,
            fontfamily="Arial",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.9),
        )
    # No "Figure 2." title in artwork - caption belongs in Word
    fig.text(
        0.5,
        0.01,
        "Map data (c) OpenStreetMap contributors | Coordinates from Data Descriptor (Alankar / Jehangir / RTO)",
        ha="center",
        fontsize=8,
        color="#64748b",
        fontfamily="Arial",
    )
    save_clean_png(OUT_PNG, fig)
    return 0


def schematic_fallback() -> int:
    fig, ax = plt.subplots(figsize=(8.5, 6.5), dpi=150)
    ax.set_facecolor("#eef2f6")
    for name, lat, lon in JUNCTIONS:
        ax.scatter([lon], [lat], s=160, c=INK, edgecolors="white", linewidths=2.0, zorder=5)
        ax.annotate(
            f"{name}\n({lat:.5f} N, {lon:.5f} E)",
            (lon, lat),
            textcoords="offset points",
            xytext=(12, 8),
            fontsize=10,
            fontweight="bold",
            color=INK,
            fontfamily="Arial",
        )
    ax.set_xlabel("Longitude (E)", fontfamily="Arial")
    ax.set_ylabel("Latitude (N)", fontfamily="Arial")
    ax.grid(True, alpha=0.3)
    save_clean_png(OUT_PNG, fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
