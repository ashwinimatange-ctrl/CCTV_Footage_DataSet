# Overview and insights

## Verdict

The **local video is April 2022**: Verint AVI + XML. Short clips record 20 April 2022. The 25 April text in the file name is the export stamp. Because of privacy (faces and plates), that video is not published online. It is not shown to be the source of the Mendeley rows: the camera names do not match.

The **Mendeley deposit** is counts only — [doi:10.17632/xnf2k6n288.1](https://doi.org/10.17632/xnf2k6n288.1). The title says January 2023. The CSV `Time` column has no year. Values are running totals (last timestamp **12:02:48**; end-of-file total **470,654** vehicles). The saved API record says Version 1 was published on 23 July 2026.

Pipeline code for this release lives under `scripts/`, `config/`, and `docker/` in this repository.

## Key findings

1. **Raw video is present and large.** About **100 AVI files** (~**99.4 GB** of video; ~**101.4 GB** including player trees). The `24 Hours` bucket alone holds ~**87.8 GB** / 60 AVIs.
2. **Exports are Verint MediaExport packages.** Each clip typically has a companion UTF-8 XML sidecar describing site, camera `resourceId`, UTC time window, and clip file list.
3. **Nine duration folders are buffer settings on the April 2022 video.** They are not the length of the Mendeley files. Deposited timestamps run about 08:59–12:02 (last time 12:02:48), about 3.00 h.
4. **Short buckets are uniform.** Each of `5 min` … `1 Hours` contains **5 cameras × 1 AVI**. Operator text notes (IST) align with XML UTC times (+5:30).
5. **Six cameras appear on disk** (see [03-media-inventory.md](03-media-inventory.md)). Only **Sangvi Phata PTZ** is exclusive to the 24-hour set among short-bucket cameras; **Axis Bank Chinchwad_1** appears in short buckets but not in the 24-hour AVI set.
6. **Player is duplicated.** There are **11** `Review\` trees (Verint Review **7.6.747.0**), repeating hundreds of DLLs — most of the non-AVI disk use.
7. **Two label systems.** Local AVIs use 509, Axis Bank, Bhel, Mahavir, and Sangvi (April 2022). Mendeley uses `a*` / `j*` / `r*` and day codes 11–18. The files do not join them.
8. **Public CSVs are not shipped in this repo.** Download from the Mendeley DOI (see `data/README.md`). Related external code: `SUMO-Dataset`.
9. **`24 Hours` is not one shared day.** Bhel and Sangvi cover about 21 April 2022. Axis Bank 3 is 16 April with a 6-hour gap. Mahavir is 19 April, missing parts 4 and 5, and the same 8 AVIs are stored twice (12.7 GB). 509 Chowk has 10 AVIs and no XML. Unique video is 86.67 GB.
10. **The older response draft that mentions FAAR is not authoritative.** Use the current manuscript and this repository’s `config/config.yaml` and `config/bytetrack.yaml`.

## Train dataset (2022) vs published dataset (2023)

| Aspect | Train dataset (local video) | Published dataset (Mendeley) |
|--------|----------------------------|------------------------------|
| Role | **Train / calibrate** pipeline | **Published** reuse / count schema |
| What the files show | April 2022 XML. Names say 25 April on short clips | Day codes 11–18. Title says Jan 2023. No year in `Time` |
| How to read a number | XML `StartTime` / `EndTime` | Last value in each file. `_one` restarts at zero |
| Online? | **No** — not published (privacy) | **Yes** — DOI above |
| Junctions / labels | 509 Chowk, Axis Bank, Bhel, Mahavir, Sangvi Phata PTZ | Alankar, Jehangir, RTO (`a*`, `j*`, `r*`) |
| Artifact | Raw Verint AVI + XML | CSV counts only |
| Scope | Fuller duration-bucket footage | Public count release |
| Processing code | This repository (`scripts/`) | GitHub `SUMO-Dataset` (external) |

**Insight:** Use the local video with its XML dates. Cite Mendeley as the public morning-count deposit. Do not sum its rows, and do not claim the full footage is on GitHub or Mendeley.

## Privacy and ethics

- **Source footage:** The Office of the Traffic Police Commissioner, Pune, provided the full CCTV footage, collected over a continuous recording period. It may contain faces, plates, and other personal information, and it is not published. Training and testing used selected high-volume morning intervals from that footage.
- **Published dataset (2023, Mendeley):** Aggregated counts only — no video/frames/faces/plates — **CC BY 4.0**.
- This repository describes structure and ships code; it does not redistribute video.

## Research / reuse insights

1. Use **5 min / 10 min** packs to calibrate detect–track–count when local 2022 footage is available.
2. Document Verint camera names ↔ paper `a*/j*/r*` codes.
3. Manuscript framing: **train dataset 2022 (unpublished online) / published dataset 2023**.
4. Compare published CSVs at count-structure level after mapping; gold frame GT still needs human labels on local video.

## Related docs

- [02-directory-structure.md](02-directory-structure.md) · [03-media-inventory.md](03-media-inventory.md) · [06-academic-dataset.md](06-academic-dataset.md) · [../README.md](../README.md)
