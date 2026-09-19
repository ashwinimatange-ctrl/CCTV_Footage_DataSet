# Academic dataset (Word docs and external release)

This page summarizes the scientific materials stored beside the footage and the **external** published count dataset they describe.

## Documents in this workspace

| File | Role |
|------|------|
| [`Data_Traffic_Dataset_Pune.docx`](../Data_Traffic_Dataset_Pune.docx) | Data Descriptor draft: *Direction-Resolved Heterogeneous Traffic Count Dataset for Pune Traffic Junctions* |
| [`Scientific Data Journal -Response Document Major Revisions.docx`](../Scientific%20Data%20Journal%20-Response%20Document%20Major%20Revisions.docx) | Incomplete revision-response letter (14 Aug 2026); partly references FAAR / ambulance routing — **not** authoritative for the footage archive |

## Data Descriptor — summary

**Authors:** Ashwini Matange (COEP / PCCOE), Jibi Abraham (COEP Technological University, Pune).

**Problem:** Public traffic datasets often assume homogeneous, lane-disciplined traffic. Indian urban junctions are heterogeneous and weakly lane-disciplined; models trained elsewhere generalize poorly.

**Contribution:** Direction-resolved, vehicle-class traffic **counts** derived from Pune Traffic Police CCTV at three signalized junctions over seven days, released as CSV (no raw video in the public deposit).

### Study junctions (paper codes — map to local Verint names)

| Prefix | Junction (paper) | Lat / Lon (paper) | Cameras |
|--------|------------------|-------------------|---------|
| `a` | Alankar Chowk | 18.52804° N, 73.87624° E | a2, a3 |
| `j` | Jehangir Chowk | 18.5304° N, 73.8767° E | j1, j2, j3 |
| `r` | RTO Chowk | 18.5305° N, 73.8636° E | r1, r2, r3 |

**Author clarification:** The **train dataset is from 2022** (local Verint video) and is **not published online** due to privacy. The **published dataset is from 2023** (Mendeley counts). Local training video uses Verint camera names (509 Chowk, Axis Bank, etc.); map codes ↔ Verint labels.

**Source note in paper:** Raw footage used nine duration classes — **5, 10, 15, 20, 25, 30, 45, 60 minutes, and 24 hours** — later harmonised into per-day CSV outputs. That duration taxonomy matches the local 2022 train archive. **Train/calibrate on 2022 CCTV** (offline); the online release is the **2023** privacy-safe count dataset only.


### Published CSV organization

Hierarchy: **junction → camera → daily file**.

| Pattern | Meaning |
|---------|---------|
| `<cameraID>_<day>.csv` | Primary day file, e.g. `a2_11.csv` = camera a2, day code 11 (**published dataset year 2023**) |
| `<cameraID>_<day>_one.csv` | Continuation of the same session; concatenate in order |

**Coverage (paper Table 3, summary):** Alankar 16+16 files; Jehangir 26+20; RTO 24+16 (primary + `_one`). Some camera-days incomplete (notably j3, r3).

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

1. **Frame extraction** — fixed sampling rate  
2. **Vehicle detection** — YOLO-family detector  
3. **Classification** — car / motorbike / bus / truck  
4. **Multi-object tracking** — SORT / DeepSORT / ByteTrack-style identity across frames  
5. **NMS + directional aggregation** — count by direction into time bins → CSV  

**Compute (paper):** COEP cluster — 4× NVIDIA Tesla V100, Xeon E5-2698 v4, 256 GB RAM, Ubuntu + Python DL stack (TEQIP-III).

### Known limitations (paper)

- Occlusion / lighting / weather → under-count risk  
- Four-class taxonomy: auto-/e-rickshaw intentionally mapped to **car**; event spotcheck taxonomy hit **87.8%** on 2,352 flagged rickshaw events (does not measure detector misses)
- Uneven camera-day coverage  

### Privacy / license (paper)

- Public release: **counts only** (no frames, faces, plates)  
- License: **CC BY 4.0**  
- Footage obtained with institutional permission from Traffic Police Commissioner, Pune  

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

The response letter is a **template draft**: blank submission ID/title, truncated reviewer replies, and at least one response discussing **FAAR (Fog-Assisted Ambulance Routing)**. Use it only as evidence that a Scientific Data–style submission was in progress — **not** as a description of the Verint exports on this disk.
