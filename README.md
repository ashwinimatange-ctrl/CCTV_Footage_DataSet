# Pune CCTV Traffic Detect–Track–Count Pipeline

YOLOv8n + ByteTrack **detect–track–count** code for direction-resolved heterogeneous traffic counts from Pune Traffic Police CCTV (Scientific Data corpus).

This repository ships **code and documentation only**. Raw video and large CSV dumps are **not** included.

## Datasets (links only)

| Resource | Year | What it is | Online? |
|----------|------|------------|---------|
| **Published dataset** | **2023** | Privacy-safe CSV counts (no video), CC BY 4.0 — [doi:10.17632/xnf2k6n288.1](https://doi.org/10.17632/xnf2k6n288.1) | **Yes** (Mendeley) |
| **Train dataset** | **2022** | Local Verint AVI + MediaExport XML for detect–track–count | **No** — not published online (privacy: faces/plates) |
| **Model weights** | — | COCO-pretrained `yolov8n.pt` | Download separately — see [`weights/README.md`](weights/README.md) |

Details: [`data/README.md`](data/README.md) · [`docs/06-academic-dataset.md`](docs/06-academic-dataset.md)

**Framing:** The **published dataset is from 2023** (online Mendeley counts). The **train dataset is from 2022** and is **not published online** due to privacy limitations; mount local footage via `FOOTAGE_ROOT` only if you have institutional access.

## Repository layout

```
.
├── config/config.yaml      # Frozen Methods config
├── scripts/                # Detect–track–count pipeline
├── analysis/               # Completeness, Table 4 coverage, comparison
├── eval/                   # Rickshaw audit + human GT metrics
├── prediction/             # Stratified KNN forecast helpers
├── figures/                # Fig01/Fig03 SVG + Fig02 builder
├── examples/               # Small coverage/completeness CSVs
├── docker/                 # Dockerfile + compose
├── docs/                   # Archive and dataset documentation
├── data/                   # DOI links + optional spotcheck CSV
├── weights/                # Place yolov8n.pt here (gitignored)
├── artifacts/              # Runtime outputs (gitignored)
├── requirements.txt
├── LICENSE                 # MIT (code)
└── CITATION.cff
```

## Requirements

- Docker (recommended) **or** Python 3.11+, FFmpeg, CPU PyTorch
- Local footage root (Verint export layout) for video runs
- Extracted Mendeley CSVs for count comparison (`blackbox_mendeley.py`)

## Quick start (Docker)

1. Clone this repo and place `yolov8n.pt` in `weights/` (see [`weights/README.md`](weights/README.md)).
2. Download and extract the Mendeley count archive (see [`data/README.md`](data/README.md)).
3. Set host paths and build:

```bat
cd docker
set FOOTAGE_ROOT=D:\path\to\CCTV FOOTAGE DATA
set MENDELEY_CSV=D:\path\to\extracted\traffic
docker compose build
docker compose run --rm pipe python -c "print('pipeline ok')"
```

4. Run a duration bucket (example: remaining short buckets):

```bat
docker compose run --rm -e MEM_BUDGET_GB=40 -e RUN_REMAINING=1 pipe python scripts/run_remaining_buckets.py
```

Single bucket:

```bat
docker compose run --rm -e MEM_BUDGET_GB=40 -e BUCKET=5 min pipe python scripts/run_pipeline.py
```

On Linux/macOS, export `FOOTAGE_ROOT` and `MENDELEY_CSV` the same way before `docker compose`.

### Environment variables

| Variable | Meaning | Default in container |
|----------|---------|----------------------|
| `WORK_ROOT` | Repo root inside container | `/work` |
| `FOOTAGE_ROOT` | Verint footage root | `/footage` (host path via compose) |
| `MENDELEY_CSV` | Extracted Mendeley CSV root | `/mendeley_csv` |
| `MEM_BUDGET_GB` | Soft/hard RAM throttle budget | `40` |
| `BUCKET` | Duration folder name | `5 min` |
| `RUN_REMAINING` | Resume incomplete short buckets | unset |

## Quick start (local Python)

```bat
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
set WORK_ROOT=%CD%
set FOOTAGE_ROOT=D:\path\to\CCTV FOOTAGE DATA
set MENDELEY_CSV=D:\path\to\extracted\traffic
python scripts/run_pipeline.py
```

## Scripts

### Pipeline (`scripts/`)

| Script | Role |
|--------|------|
| `scripts/run_pipeline.py` | Main YOLOv8n + ByteTrack multi-AVI runner |
| `scripts/run_remaining_buckets.py` | Resume unfinished short duration buckets |
| `scripts/blackbox_mendeley.py` | Compare pipeline counts to Mendeley CSVs |
| `scripts/probe_video.py` | Probe whether Verint AVI is decodable |
| `scripts/r7_semi_gt.py` | Semi ground-truth helper from count CSVs |
| `scripts/resource_guard.py` | Memory soft/hard throttle |

### Analysis / eval / prediction

| Script | Role |
|--------|------|
| `analysis/build_table4_coverage.py` | Camera-day coverage Table 4 (demo: `examples/`) |
| `analysis/scan_mendeley_completeness.py` | Local Mendeley tree → completeness + time spans |
| `analysis/hours_covered.py` | Per-file hour spans + short flags |
| `analysis/comparison_table.py` | Public-dataset comparison markdown |
| `eval/audit_rickshaw_confusion.py` | Rickshaw→car taxonomy hit audit |
| `eval/compute_human_gt_metrics.py` | Human gold MAE/RMSE/MAPE |
| `prediction/knn_stratified_eval.py` | Stratified KNN on count totals |
| `figures/build_fig02_map.py` | Rebuild junction map (OSM tiles) |

```bat
python analysis\build_table4_coverage.py
python eval\audit_rickshaw_confusion.py
```

Frozen stack: **YOLOv8n (COCO)** + **ByteTrack**, CPU, `imgsz` 640, frame stride 5 — see [`config/config.yaml`](config/config.yaml).

## Documentation

| Doc | Topic |
|-----|--------|
| [01 — Overview](docs/01-overview-and-insights.md) | Local CCTV vs public subset |
| [02 — Directory structure](docs/02-directory-structure.md) | Verint folder layout |
| [03 — Media inventory](docs/03-media-inventory.md) | Cameras and buckets |
| [04 — Export format](docs/04-export-format.md) | MediaExport XML |
| [05 — Verint Review](docs/05-verint-review-player.md) | Offline player |
| [06 — Academic dataset](docs/06-academic-dataset.md) | Paper summary, CSV schema |
| [07 — Ops & limitations](docs/07-ops-and-limitations.md) | Storage and caveats |

## License and citation

- **Code:** MIT — see [`LICENSE`](LICENSE)
- **Published count dataset (2023):** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) via Mendeley DOI above
- **Train dataset (2022 video):** not published online (privacy)
- Cite with [`CITATION.cff`](CITATION.cff)

Related external processing mirror: [light2802/SUMO-Dataset](https://github.com/light2802/SUMO-Dataset.git)

## What is intentionally excluded

- **2022 train video** (AVI) and Verint Review player trees — not published online (privacy)  
- Extracted Mendeley CSV trees and other multi-GB count copies (download the **2023** DOI instead)  
- `yolov8n.pt` and other weight files  
- Manuscript Word docs and large run artifact folders  
