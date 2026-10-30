# Academic dataset (Word docs and external release)

This page summarizes the scientific materials stored beside the footage and the **external** published count dataset they describe.

## Documents in this workspace

| File | Role |
|------|------|
| [`Data_Traffic_Dataset_Pune.docx`](../Data_Traffic_Dataset_Pune.docx) | Data Descriptor draft: *Direction-Resolved Heterogeneous Traffic Count Dataset for Pune Traffic Junctions* |

## Data Descriptor — summary

**Authors:** Ashwini Matange (COEP / PCCOE), Jibi Abraham (COEP Technological University, Pune).

**Problem:** Public traffic datasets often assume homogeneous, lane-disciplined traffic. Indian urban junctions are heterogeneous and weakly lane-disciplined; models trained elsewhere generalize poorly.

**Contribution:** Direction-resolved, vehicle-class traffic **counts** derived from Pune Traffic Police CCTV at three signalized junctions, 11–18 January 2023 (eight days, eight cameras), released as 115 CSV files (no raw video in the public deposit).

### Study junctions (paper codes — map to local Verint names)

| Prefix | Junction (paper) | Lat / Lon (paper) | Cameras |
|--------|------------------|-------------------|---------|
| `a` | Alankar Chowk | 18.52804° N, 73.87624° E | a2, a3 |
| `j` | Jehangir Chowk | 18.5304° N, 73.8767° E | j1, j2, j3 |
| `r` | RTO Chowk | 18.5305° N, 73.8636° E | r1, r2, r3 |

**Author clarification:** The **train dataset is from 2022** (local Verint video) and is **not published online** due to privacy. The **published dataset is from 2023** (Mendeley counts). Local training video uses Verint camera names (509 Chowk, Axis Bank, etc.); map codes ↔ Verint labels.

**Source note in paper:** Camera buffers were 5, 10, 15, 20, 25, 30, 45, 60 minutes, and 24 hours. Those are buffer settings, not the length of the deposited count files. Deposited timestamps run about 09:00–12:00 local time (span about 3.00 h). A printed 0 is an observed zero. A clock second with no row is a gap and must not be filled with zero. **Train/calibrate on 2022 CCTV** (offline); the online release is the **2023** privacy-safe count dataset only.


### Published CSV organization

Hierarchy: **junction → camera → daily file**.

| Pattern | Meaning |
|---------|---------|
| `<cameraID>_<day>.csv` | Primary day file, e.g. `a2_11.csv` = camera a2, day code 11 (**published dataset year 2023**) |
| `<cameraID>_<day>_one.csv` | Continuation of the same session; concatenate in order |

**Coverage:** 64 primary + 51 continuation = 115 CSV files. Alankar 16+16, Jehangir 24+19, RTO 24+16. Every camera has a primary file on each date from 11 to 18 January 2023. Thirteen camera-days have no continuation file: j3 on 11, 12, 13, 17 and 18 January, and r3 on all eight dates.

### CSV schema (Table 4)

| Field | Type | Description |
|-------|------|-------------|
| `Time` | `HH:MM:SS` string | Aggregation interval start, **IST** |
| `Direction` | categorical | `UP`, `DOWN`, `LEFT`, or `RIGHT` |
| `car` | int | Car count for interval × direction |
| `motorbike` | int | Two-wheeler count |
| `bus` | int | Bus count |
| `truck` | int | Truck count |

One time interval yields up to **four rows** (one per direction).

### Video-to-count pipeline (paper)

Five stages:

1. **Frame extraction** — every 5th frame  
2. **Vehicle detection** — YOLOv8n, Ultralytics 8.3.57, COCO weights frozen, `imgsz` 640, `conf` 0.25, `iou` 0.45  
3. **Classification** — COCO 2/3/5/7 mapped to car / motorbike / bus / truck  
4. **Tracking** — ByteTrack through `config/bytetrack.yaml` (`track_high_thresh` 0.25, `track_low_thresh` 0.1, `new_track_thresh` 0.25, `track_buffer` 30, `match_thresh` 0.8, `fuse_score` True), dependency `lap` 0.5.12. SORT and DeepSORT are cited for comparison only.  
5. **Directional aggregation** — image-plane displacement into UP, DOWN, LEFT, RIGHT  

**Compute (paper):** COEP cluster — 4× NVIDIA Tesla V100, Xeon E5-2698 v4, 256 GB RAM, Ubuntu, Python 3.11, Ultralytics 8.3.57, CUDA 12 (TEQIP-III). The Docker image in this repository is a CPU archive of the method and did not produce the Mendeley counts.

**Config checksum:** SHA-256 of `config/config.yaml` as stored in git (LF): `2bbe990d6df5724b95e9d1703d3326266bfd67a2edc83ac85349ba78cf4db66e`.

### Known limitations (paper)

- Occlusion / lighting / weather → under-count risk  
- Four-class taxonomy: auto-/e-rickshaw intentionally mapped to **car**; event spotcheck taxonomy hit **87.8%** on 2,352 flagged rickshaw events (does not measure detector misses)
- Uneven camera-day coverage  

### Privacy / license (paper)

- Public release: **counts only** (no frames, faces, plates)  
- License: **CC BY 4.0**  
- COEP Technological University sent an official request to the Police Commissioner, routed through the university administrative office, under a signed non-disclosure agreement. The agreement bars release of the raw video.
- Others obtain the counts by downloading Mendeley Data Version 1 (CC BY 4.0). No application is required for those CSVs. The same video cannot be downloaded from Mendeley or GitHub.  

### External links

| Resource | URL |
|----------|-----|
| Mendeley Data (counts) | https://doi.org/10.17632/xnf2k6n288.1 |
| Pipeline code (this repo) | See repository root `README.md` |
| Related external code | https://github.com/light2802/SUMO-Dataset.git |
| Intended simulator reuse | SUMO (demand calibration under mixed traffic) |

**Mendeley CSVs** are **not** stored in this repository. Download from the DOI above and point `MENDELEY_CSV` at the extracted tree (see `data/README.md`). Related mirror: https://github.com/light2802/SUMO-Dataset.

## Relationship: train 2022 vs published 2023

**Train dataset (2022):** local Verint footage, mounted via `FOOTAGE_ROOT` when available. **Not published online** due to privacy limitations.  
**Published dataset (2023):** Mendeley DOI — privacy-safe CSV counts only (**online**).

| | Published dataset (Mendeley) | Train dataset (local CCTV) |
|--|----------------------------|----------------------------|
| Cameras (labels) | Alankar / Jehangir / RTO codes | 509 / Axis Bank / Bhel / Mahavir / Sangvi Phata |
| Year | **2023** | **2022** (AVI/XML show Apr 2022) |
| Online? | **Yes** | **No** (privacy) |
| Artifact | CSV counts only | Raw AVI + XML |
| Scope | Public count release | Fuller duration-bucket footage |
| Role | Public reuse / schema checks | **Primary training & Methods video** |

Manuscript should state **train dataset 2022 (unpublished online) / published dataset 2023**, privacy (counts only online), and camera-label mapping.

## Revision-response document

The current point-by-point response is kept with the manuscript, not in this code repository. Do not use the older response draft that mentions FAAR (Fog-Assisted Ambulance Routing) as a description of this dataset.
