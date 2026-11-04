# Data (download links only)

This folder is a **placeholder**. Large datasets are **not** committed to GitHub.

## Published counts — online

| Field | Value |
|-------|--------|
| Title | Heterogeneous Traffic Count Dataset, Pune (Jan 2023) |
| What the files show | Day codes 11–18. No year in `Time`. Running totals. Last time 12:02:48. End-of-file total 470,654 vehicles |
| DOI | [10.17632/xnf2k6n288.1](https://doi.org/10.17632/xnf2k6n288.1) |
| Landing page | https://data.mendeley.com/datasets/xnf2k6n288/1 |
| License | CC BY 4.0 |
| Contents | CSV vehicle counts by junction / camera / day (**no video**). Do not sum the rows |

This is the only traffic count release published online for this project. No application is required. The raw video is not in the deposit. The saved API metadata says Version 1 was published on 23 July 2026.

Small supplements copied from the manuscript folder, not the 115 count files:

| File | What it lists |
|------|----------------|
| [`../supplement/Camera_Date_Inventory.csv`](../supplement/Camera_Date_Inventory.csv) | 64 camera-days: first time, last time, span, gap, usable duration, overlap, and whether a continuation file exists |
| [`../supplement/Human_Validation_560_Bins.csv`](../supplement/Human_Validation_560_Bins.csv) | 560 paired manual and automatic class-direction counts |

### Download steps

1. Open the DOI or Mendeley landing page.
2. Download `traffic.zip` (and optionally the data dictionary / deposit README).
3. Extract so you have a tree like:

```
traffic/
  AlankarChowk/
  JehangirChowk/
  RTOChowk/
```

4. Point the pipeline at that tree:

```bat
set MENDELEY_CSV=D:\path\to\traffic
```

Docker Compose mounts `MENDELEY_CSV` at `/mendeley_csv` inside the container.

## Local video (April 2022) — not published online

| Layer | Dates on the files | Online? | Role |
|-------|--------------------|---------|------|
| Local Verint AVI + XML | XML **April 2022**. Short-clip names say 25 April | **No** | Detect–track–count when you have access |
| Mendeley CSV deposit | Title says Jan 2023. CSV has no year | **Yes** | Public running totals (privacy-safe) |

Raw CCTV may contain faces and plates, so the video is not in this repository and is not the same camera list as the CSVs.

If you have institutional access to the April 2022 footage:

1. Place duration buckets (`5 min`, `10 min`, …, `24 Hours`) under one root folder.
2. Set `FOOTAGE_ROOT` to that root (each bucket should contain `ExportedMedia\*.avi`).
3. Prefer short buckets (`5 min` / `10 min`) before the large `24 Hours` set.

See [`docs/02-directory-structure.md`](../docs/02-directory-structure.md) and [`docs/06-academic-dataset.md`](../docs/06-academic-dataset.md).

## Spotcheck CSV (optional, for eval)

`event_spotcheck_23_18_9.csv` — event-level flags (`is_rickshaw`, plates) used by
`eval/audit_rickshaw_confusion.py`. Contains **no video frames**; ~6 MB. Not a
substitute for the Mendeley count deposit.
