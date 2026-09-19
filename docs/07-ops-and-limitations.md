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
| Raw Verint AVI exports (**train/calibrate here**) | Original unpublished author YOLO configs (if different from demo) |
| MediaExport XML (most packs) | Frame-level gold labels / bounding boxes |
| Verint Review 7.6 offline players | Live NVR / RTSP connectivity |
| Data Descriptor + draft response `.docx` | — |
| Mendeley **2023 published** count dataset (download separately) | **2022 train** video cannot be published online (privacy) |
| Detect–track–count pipeline (`scripts/`) | — |

**Pipeline policy:** Train on the **2022** local CCTV database when available (not online). Use the **2023** Mendeley deposit as the published count dataset.

## Tooling caveats

| Tool | Guidance |
|------|----------|
| Verint Review | Preferred for playback; see [05-verint-review-player.md](05-verint-review-player.md) |
| VLC / generic players | May work on some AVIs; codec/container issues are common with NVR exports |
| ffmpeg | Validate on a 5-minute sample before batch jobs |
| Parallel Review instances | Avoid — localhost WCF ports **7020** / **7030** collide |
| Antivirus | First launch of `Review\` can be slow while DLLs are scanned |

## Packaging / data-quality issues on disk

1. **509 Chowk 1 (24 Hours):** 10 AVIs, **0** MediaExport XML — time bounds unknown without player UI or binary probing.  
2. **Mahavir Chowk:** Export folders appear both under `24 Hours\ExportedMedia\` and as siblings under `24 Hours\` — possible duplicates.  
3. **Folder typo:** `Axix Bank 3` (Axis).  
4. **XML inventory noise:** ~438 `*.xml` files recursively vs ~53 true `Export__` manifests.  
5. **Filename dates ≠ recording dates:** Export job stamps in names vs `StartTime`/`EndTime` in XML.  
6. **Review duplication:** Eleven near-identical player trees waste space but keep each pack self-contained.

## Security / compliance

- Treat all AVI content as **sensitive CCTV**. Restrict access; the **2022 train video is not published online** (privacy).  
- The **published** research product is the **2023 count CSV** dataset on Mendeley (CC BY 4.0).  
- Vendor `ConnectToSiteTemplate` hostnames in Review configs are placeholders — unused for offline export playback.

## Suggested operator workflow

1. Read [01-overview-and-insights.md](01-overview-and-insights.md) for train-2022 vs published-2023.  
2. Play a **5 min** export with Review to verify the workstation (if you have institutional 2022 footage).  
3. Use [03-media-inventory.md](03-media-inventory.md) to pick camera/duration.  
4. **Train/calibrate** detect–track–count on local 2022 AVIs; document cameras/`resourceId`s and UTC windows from XML.  
5. Download **2023** Mendeley CSVs (see `data/README.md`) for published-dataset schema/share checks after site-label mapping.

## Non-goals of this documentation

- No redistribution of the 2022 train video (privacy)  
- No reverse-engineering of Verint Review internals  
- No claim that every Mendeley row is regenerated bit-exactly without site mapping + frozen Methods
