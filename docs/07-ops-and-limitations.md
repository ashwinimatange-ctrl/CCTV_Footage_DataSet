# Operations and limitations

## Storage footprint

| Component | Approx size | Notes |
|-----------|-------------|--------|
| All AVI video | ~99.4 GB | 100 files — **local CCTV training database** |
| `24 Hours` AVI alone | ~87.8 GB | 60 files — plan disk and copy time accordingly |
| Short buckets combined | ~11.5 GB | 40 files |
| Duplicated `Review\` trees (×11) | ~2 GB class (included in ~101.4 GB total) | Same player copied per pack |
| Mendeley download | ~15 MB zip + extract | Download via DOI — not in this repo |
| This repository (code) | < 1 MB | Scripts, config, Docker, docs |
| Local Verint footage (optional) | **~101.4 GB** | Video + players + XML — set `FOOTAGE_ROOT` |

Copying or backing up this archive is I/O-bound; prefer resume-capable tools (`robocopy /J`, etc.) for the 24-hour set.

## What is present vs missing

| Present | Missing / external |
|---------|-------------------|
| Raw Verint AVI exports (**train/calibrate here**) | The Mendeley counts were not produced by the CPU Docker image |
| MediaExport XML (most packs) | Frame-level gold labels / bounding boxes |
| Verint Review 7.6 offline players | Live NVR / RTSP connectivity |
| Data Descriptor + draft response `.docx` | — |
| Mendeley **2023 published** count dataset (download separately) | **2022 train** video cannot be published online (privacy) |
| Detect–track–count pipeline (`scripts/`) | — |

**Pipeline policy:** When footage is available, use the XML dates (short clips are 20 April 2022). Read Mendeley as running totals. Do not treat the camera lists as one mapped corpus. `config/bytetrack.yaml` is in this tree. LF SHA-256 of `config/config.yaml` is `2bbe990d6df5724b95e9d1703d3326266bfd67a2edc83ac85349ba78cf4db66e`. The PDF prints a different hash.

## Tooling caveats

| Tool | Guidance |
|------|----------|
| Verint Review | Preferred for playback; see [05-verint-review-player.md](05-verint-review-player.md) |
| VLC / generic players | May work on some AVIs; codec/container issues are common with NVR exports |
| ffmpeg | Validate on a 5-minute sample before batch jobs |
| Parallel Review instances | Avoid — localhost WCF ports **7020** / **7030** collide |
| Antivirus | First launch of `Review\` can be slow while DLLs are scanned |

## Packaging / data-quality issues on disk

1. **509 Chowk 1 (24 Hours):** 10 AVIs, **0** MediaExport XML. Recording window is not in the archive.  
2. **Mahavir Chowk:** The same 8 AVIs are stored twice (same name, same size, 12.7 GB). Parts 4 and 5 of the morning half are missing in both copies.  
3. **Axis Bank 3:** IST 16 April, gap 06:00–12:00. Folder typo `Axix Bank 3`.  
4. **XML inventory noise:** ~438 `*.xml` files recursively vs 53 true `Export__` manifests.  
5. **Filename dates are export stamps.** Short clips say 25 April 2022 in the name and 20 April 2022 in `StartTime`.  
6. **Review duplication:** Eleven player trees. Unique AVI bytes are 86.67 GB.  
7. **Mendeley values are running totals.** Do not sum rows. Last timestamp is 12:02:48. End-of-file total is 470,654 vehicles.

## Security / compliance

- Treat all AVI content as **sensitive CCTV**. Restrict access; the **2022 train video is not published online** (privacy).  
- The **published** research product is the **2023 count CSV** dataset on Mendeley (CC BY 4.0).  
- Vendor `ConnectToSiteTemplate` hostnames in Review configs are placeholders — unused for offline export playback.

## Suggested operator workflow

1. Read [01-overview-and-insights.md](01-overview-and-insights.md) for train-2022 vs published-2023.  
2. Play a **5 min** export with Review to verify the workstation (if you have institutional 2022 footage).  
3. Use [03-media-inventory.md](03-media-inventory.md) to pick camera/duration.  
4. **Train/calibrate** detect–track–count on local 2022 AVIs; document cameras/`resourceId`s and UTC windows from XML.  
5. Download the Mendeley CSVs (see `data/README.md`). Take the last value in each file. Do not sum rows.

## Non-goals of this documentation

- No claim that the April 2022 video and the Mendeley CSVs are the same recordings
- No reverse-engineering of Verint Review internals
- No claim that summing Mendeley rows is a vehicle total
