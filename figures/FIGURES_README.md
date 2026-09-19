# Manuscript figures

Neutral production assets. Shared palette: ink `#1a2332`, green `#2f5d3a`, warm `#8a5a1a`, paper `#f4f7fb`.

| Figure | Files |
|------|-------|
| Fig 1 | `Fig01_folder_hierarchy.svg` |
| Fig 2 | Rebuild with `build_fig02_map.py` → `Fig02_junction_map.png` (not committed; needs OSM tiles) |
| Fig 3 | `Fig03_pipeline.svg` |

Coordinates (published deposit):

- Alankar Chowk: 18.52804 N, 73.87624 E
- Jehangir Chowk: 18.5304 N, 73.8767 E
- RTO Chowk: 18.5305 N, 73.8636 E

```bat
cd figures
python build_fig02_map.py
```

Requires network access to `tile.openstreetmap.org` (falls back to a schematic plot if tiles fail). Optional deps: `matplotlib`, `pillow`, `requests`, `numpy`.
