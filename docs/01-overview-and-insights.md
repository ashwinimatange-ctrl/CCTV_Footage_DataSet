# Overview and insights

## Verdict

The **train dataset is from 2022**: local Verint NVR-exported CCTV video (AVI + XML), used to train/calibrate detect–track–count. Because of **privacy limitations** (faces/plates), that train video is **not published online**.

The **published dataset is from 2023**: the Mendeley Data deposit of privacy-safe **counts only** (no video) — [doi:10.17632/xnf2k6n288.1](https://doi.org/10.17632/xnf2k6n288.1).

Pipeline code for this release lives under `scripts/`, `config/`, and `docker/` in this repository.

## Key findings

1. **Raw video is present and large.** About **100 AVI files** (~**99.4 GB** of video; ~**101.4 GB** including player trees). The `24 Hours` bucket alone holds ~**87.8 GB** / 60 AVIs.
2. **Exports are Verint MediaExport packages.** Each clip typically has a companion UTF-8 XML sidecar describing site, camera `resourceId`, UTC time window, and clip file list.
3. **Duration bucketing matches the paper’s acquisition note.** Folders exist for 5 / 10 / 15 / 20 / 25 / 30 / 45 / 60 minutes (`1 Hours`) and 24 hours — the same nine duration classes mentioned in the Data Descriptor.
4. **Short buckets are uniform.** Each of `5 min` … `1 Hours` contains **5 cameras × 1 AVI**. Operator text notes (IST) align with XML UTC times (+5:30).
5. **Six cameras appear on disk** (see [03-media-inventory.md](03-media-inventory.md)). Only **Sangvi Phata PTZ** is exclusive to the 24-hour set among short-bucket cameras; **Axis Bank Chinchwad_1** appears in short buckets but not in the 24-hour AVI set.
6. **Player is duplicated.** There are **11** `Review\` trees (Verint Review **7.6.747.0**), repeating hundreds of DLLs — most of the non-AVI disk use.
7. **Train 2022 vs published 2023.** Local AVIs = **2022 train** video (**not online**, privacy). Mendeley = **2023 published** counts-only dataset (**online**). Camera/junction **labels** differ and must be mapped in the manuscript.
8. **Public CSVs are not shipped in this repo.** Download from the Mendeley DOI (see `data/README.md`). Related external code: `SUMO-Dataset`.
9. **Some 24-hour packs are incomplete as packages.** Example: **509 Chowk 1** has 10 AVIs under `24 Hours` but **0** matching MediaExport XML sidecars. Mahavir Chowk export folders also appear duplicated at the `24 Hours\` root and under `ExportedMedia\`.
10. **The revision-response Word doc is incomplete / mixed.** It references FAAR in places — do not treat it as authoritative for this footage.

## Train dataset (2022) vs published dataset (2023)

| Aspect | Train dataset (local video) | Published dataset (Mendeley) |
|--------|----------------------------|------------------------------|
| Role | **Train / calibrate** pipeline | **Published** reuse / count schema |
| Year | **2022** | **2023** |
| Online? | **No** — not published (privacy) | **Yes** — DOI above |
| Junctions / labels | 509 Chowk, Axis Bank, Bhel, Mahavir, Sangvi Phata PTZ | Alankar, Jehangir, RTO (`a*`, `j*`, `r*`) |
| Artifact | Raw Verint AVI + XML | CSV counts only |
| Scope | Fuller duration-bucket footage | Public count release |
| Processing code | This repository (`scripts/`) | GitHub `SUMO-Dataset` (external) |

**Insight:** Use **2022** local video only under institutional access for training. Cite the **2023** Mendeley deposit as the online published dataset. Do not claim the train video is available on GitHub or Mendeley.

## Privacy and ethics

- **Train video (2022):** Raw traffic CCTV may contain faces, plates, and other PII. **Not published online** for that reason. Use only under institutional permission (paper credits Office of the Traffic Police Commissioner, Pune).
- **Published dataset (2023, Mendeley):** Aggregated counts only — no video/frames/faces/plates — **CC BY 4.0**.
- This repository describes structure and ships code; it does not redistribute video.

## Research / reuse insights

1. Use **5 min / 10 min** packs to calibrate detect–track–count when local 2022 footage is available.
2. Document Verint camera names ↔ paper `a*/j*/r*` codes.
3. Manuscript framing: **train dataset 2022 (unpublished online) / published dataset 2023**.
4. Compare published CSVs at count-structure level after mapping; gold frame GT still needs human labels on local video.

## Related docs

- [02-directory-structure.md](02-directory-structure.md) · [03-media-inventory.md](03-media-inventory.md) · [06-academic-dataset.md](06-academic-dataset.md) · [../README.md](../README.md)
