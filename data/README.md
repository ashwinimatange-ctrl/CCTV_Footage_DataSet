# Data (download links only)

This folder is a **placeholder**. Large datasets are **not** committed to GitHub.

## Published dataset (2023) — online

| Field | Value |
|-------|--------|
| Title | Heterogeneous Traffic Count Dataset, Pune |
| Year | **2023** (published online) |
| DOI | [10.17632/xnf2k6n288.1](https://doi.org/10.17632/xnf2k6n288.1) |
| Landing page | https://data.mendeley.com/datasets/xnf2k6n288/1 |
| License | CC BY 4.0 |
| Contents | CSV vehicle counts by junction / camera / day (**no video**) |

This is the only traffic dataset published online for this project.

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

## Train dataset (2022) — not published online

| Layer | Year | Online? | Role |
|-------|------|---------|------|
| Local Verint AVI + XML | **2022** | **No** | Train / calibrate detect–track–count |
| Mendeley CSV deposit | **2023** | **Yes** | Published count dataset (privacy-safe) |

Raw CCTV may contain faces and plates. Because of **privacy limitations**, the **2022 train video is not published online** and is not included in this repository.

If you have institutional access to the 2022 footage:

1. Place duration buckets (`5 min`, `10 min`, …, `24 Hours`) under one root folder.
2. Set `FOOTAGE_ROOT` to that root (each bucket should contain `ExportedMedia\*.avi`).
3. Prefer short buckets (`5 min` / `10 min`) before the large `24 Hours` set.

See [`docs/02-directory-structure.md`](../docs/02-directory-structure.md) and [`docs/06-academic-dataset.md`](../docs/06-academic-dataset.md).

## Spotcheck CSV (optional, for eval)

`event_spotcheck_23_18_9.csv` — event-level flags (`is_rickshaw`, plates) used by
`eval/audit_rickshaw_confusion.py`. Contains **no video frames**; ~6 MB. Not a
substitute for the Mendeley count deposit.
