# Media inventory

Inventory generated from on-disk AVI files under `CCTV FOOTAGE DATA` (file sizes; names parsed from Verint export filenames).

## Totals

| Metric | Value |
|--------|-------|
| AVI files | **100** |
| AVI total size | **~99.38 GB** |
| MediaExport XML (`Export__*.xml`) | **~53** |
| All `*.xml` including Review configs | **~438** |
| Full folder size (video + players) | **~101.39 GB** |
| `Review\` directory copies | **11** |

## Size by duration bucket

| Bucket | AVI count | Approx. AVI GB | MediaExport-style XML* |
|--------|-----------|----------------|-------------------------|
| 5 min | 5 | 0.28 | 5 (+ Review XMLs → 40 recursive) |
| 10 min | 5 | 0.55 | 5 (40 recursive) |
| 15 min | 5 | 0.83 | 5 (40 recursive) |
| 20 min | 5 | 1.10 | 5 (40 recursive) |
| 25 min | 5 | 1.37 | 5 (40 recursive) |
| 30 min | 5 | 1.64 | 5 (40 recursive) |
| 45 min | 5 | 2.47 | 5 (40 recursive) |
| 1 Hours | 5 | 3.30 | 5 (40 recursive) |
| 24 Hours | 60 | 87.84 | ~13+ under exports (118 recursive) |

\*Recursive XML counts include Review player configs. Short buckets each have **5** MediaExport sidecars next to AVIs.

## Camera registry (from MediaExport XML)

| Camera name | resourceId | NVR site | Site GUID |
|-------------|------------|----------|-----------|
| 509 Chowk 1 | 4137 | VER-MASTER | `818A317F-61F0-41C2-932A-BF3456F98749` |
| Axis Bank Chinchwad_1 | 1828 | Master Server 2 | `1B3B649B-5F14-458C-A1C0-2999311AD5E7` |
| Axis Bank Chinchwad_3 | 1824 | Master Server 2 | same as above |
| Bhel Chowk- 4 | 2266 | Master Server 2 | same |
| Mahavir Chowk 1 | 1954 | Master Server 2 | same |
| Sangvi Phata PTZ | 3141 | Master Server 2 | same |

All sites use `masterTimeZoneId="India Standard Time"`.

## AVI count and size by bucket × camera

### Short buckets (5 cameras × 1 clip each)

| Camera | 5m | 10m | 15m | 20m | 25m | 30m | 45m | 1h | Approx GB each short clip* |
|--------|----|-----|-----|-----|-----|-----|-----|----|----------------------------|
| 509 Chowk 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0.06 → 0.66 |
| Axis Bank Chinchwad_1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | similar |
| Axis Bank Chinchwad_3 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | similar |
| Bhel Chowk- 4 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | similar |
| Mahavir Chowk 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | similar |
| Sangvi Phata PTZ | — | — | — | — | — | — | — | — | not in short buckets |

\*Per-camera GB grows with duration (e.g. ~0.06 GB at 5 min, ~0.66 GB at 1 hour).

### 24 Hours

| Camera | AVI count | Approx GB | Notes |
|--------|-----------|-----------|--------|
| 509 Chowk 1 | 10 | 15.87 | Multi-part folders; **no MediaExport XML** found |
| Axis Bank Chinchwad_3 | 12 | 15.07 | Nested under `ExportedMedia\Axix Bank 3\` |
| Bhel Chowk- 4 | 10 | 15.71 | Multi-part export folders |
| Mahavir Chowk 1 | 16 | 25.41 | Largest; some folders duplicated at bucket root |
| Sangvi Phata PTZ | 12 | 15.78 | Nested under `ExportedMedia\sangvi phata ptz\` |
| Axis Bank Chinchwad_1 | 0 | — | Present in short buckets only |

**24 Hours AVI subtotal:** 60 files · ~87.84 GB

## Recording time span (from MediaExport XML)

| Bound | UTC value | Approx IST |
|-------|-----------|------------|
| Earliest `StartTime` | 2022-04-15 18:30:00Z | 2022-04-16 00:00 |
| Latest `EndTime` | 2022-04-21 18:30:00Z | 2022-04-22 00:00 |

Short-bucket clips on 20 Apr 2022 cover daytime IST windows listed in [02-directory-structure.md](02-directory-structure.md).

### 24-hour export coverage (where XML exists)

| Camera | MediaExport count | Listed clips | Observed Start–End (UTC) |
|--------|-------------------|--------------|---------------------------|
| Axis Bank Chinchwad_3 | 3 | 9 | 2022-04-15 18:30 → 2022-04-16 17:29:59 |
| Bhel Chowk- 4 | 2 | 10 | 2022-04-20 18:30 → 2022-04-21 18:30 |
| Mahavir Chowk 1 | 4 | 20 | 2022-04-18 18:30 → 2022-04-19 18:30 |
| Sangvi Phata PTZ | 4 | 12 | 2022-04-20 18:30 → 2022-04-21 18:29:59 |
| 509 Chowk 1 | 0 | (10 AVIs on disk) | unknown from XML |

## Filename pattern

```
Export__<CameraName>_<Weekday> <Month> <Day> <Year><HHmmss>  <hexid>.avi
Export__<CameraName>_<Weekday> <Month> <Day> <Year><HHmmss>  <hexid>.xml
Export__..._<hexid>_2.avi   # continuation parts for long exports
```

Example (5 min):

`Export__509 Chowk 1_Monday April 25 2022164216  a25123b.avi`

The date in the filename is the **export generation** timestamp (operator machine), not necessarily the recording start (recording times live in the XML).
