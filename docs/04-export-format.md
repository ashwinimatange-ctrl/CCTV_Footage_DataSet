# Verint MediaExport format

## Package model

Each export is a **MediaExport** package:

- One or more **`.avi`** media clips
- Usually one companion **`.xml`** sidecar describing the export window, site, camera, and clip list
- Often shipped next to a full **offline Review** client so the package can be opened without a live NVR connection

Short-duration buckets keep AVI+XML flat under `ExportedMedia\`. Long (24-hour) exports often place multi-part AVIs in a subfolder named after the export, with the XML either beside those files or in a parent `ExportedMedia` folder.

## XML schema (observed)

Encoding: **UTF-8 with BOM**. Root element: `MediaExport`.

### Short clip example (`5 min`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<MediaExport name="Export__509 Chowk 1_Monday April 25 2022164216  a25123b">
  <StartTime>2022-04-20 04:30:00Z</StartTime>
  <EndTime>2022-04-20 04:35:00Z</EndTime>
  <Site name="VER-MASTER" id="818A317F-61F0-41C2-932A-BF3456F98749"
        masterTimeZoneId="India Standard Time" />
  <Camera name="509 Chowk 1" resourceId="4137" />
  <MediaClips folder=".">
    <MediaClip id="1" file="Export__509 Chowk 1_Monday April 25 2022164216  a25123b.avi" />
  </MediaClips>
</MediaExport>
```

### Multi-part / longer export example (`24 Hours`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<MediaExport name="Export__Axis Bank Chinchwad_3_Tuesday April 26 2022113445  cdf0032">
  <StartTime>2022-04-15 18:30:00Z</StartTime>
  <EndTime>2022-04-16 00:30:00Z</EndTime>
  <Site name="Master Server 2" id="1B3B649B-5F14-458C-A1C0-2999311AD5E7"
        masterTimeZoneId="India Standard Time" />
  <Camera name="Axis Bank Chinchwad_3" resourceId="1824" />
  <MediaClips folder="Export__Axis Bank Chinchwad_3_Tuesday April 26 2022113445  cdf0032">
    <MediaClip id="1" file="Export__Axis Bank Chinchwad_3_Tuesday April 26 2022113445  cdf0032.avi" />
    <MediaClip id="2" file="Export__Axis Bank Chinchwad_3_Tuesday April 26 2022113445  cdf0032_2.avi" />
    <MediaClip id="3" file="Export__Axis Bank Chinchwad_3_Tuesday April 26 2022113445  cdf0032_3.avi" />
  </MediaClips>
</MediaExport>
```

## Field reference

| Element / attribute | Meaning |
|---------------------|---------|
| `MediaExport/@name` | Export package id; matches base filename without extension |
| `StartTime` / `EndTime` | Recording window in **UTC** (`…Z`), wall-clock aligned to site TZ |
| `Site/@name` | NVR site label (`VER-MASTER` or `Master Server 2`) |
| `Site/@id` | Site GUID |
| `Site/@masterTimeZoneId` | Always `India Standard Time` in this archive |
| `Camera/@name` | Camera display name as configured on the NVR |
| `Camera/@resourceId` | Numeric camera resource id on that site |
| `MediaClips/@folder` | Relative folder containing clip files (`.` = same directory as XML) |
| `MediaClip/@id` | 1-based part index |
| `MediaClip/@file` | AVI filename (parts use `_2`, `_3`, … suffix) |

## Naming conventions

| Pattern | Example |
|---------|---------|
| Base export id | `Export__<Camera>_<Weekday> <Month> <D> <YYYY><HHmmss>  <7-hex>` |
| Video | `<base>.avi`, `<base>_2.avi`, … |
| Sidecar | `<base>.xml` |

- Double underscore after `Export` is intentional in Verint naming.
- The calendar stamp in the filename is the **export job** time on the operator workstation, **not** the clip’s `StartTime`.
- Hex suffix distinguishes parallel export jobs.

## Time conversion

Site timezone is India Standard Time (**UTC+05:30**).

| XML (UTC) | Local IST |
|-----------|-----------|
| 2022-04-20 04:30:00Z | 2022-04-20 10:00:00 |
| 2022-04-20 04:35:00Z | 2022-04-20 10:05:00 |

Short-bucket operator `.txt` notes use IST and match these conversions.

### Short-bucket recording windows (509 Chowk XML sample)

| Bucket | Start (UTC) | End (UTC) | IST (from notes / conversion) |
|--------|-------------|-----------|-------------------------------|
| 5 min | 2022-04-20 04:30:00Z | 04:35:00Z | 10:00–10:05 |
| 10 min | 2022-04-20 05:00:00Z | 05:10:00Z | 10:30–10:40 |
| 15 min | 2022-04-20 05:15:00Z | 05:30:00Z | 10:45–11:00 |
| 20 min | 2022-04-20 06:00:00Z | 06:20:00Z | 11:30–11:50 |
| 25 min | 2022-04-20 07:30:00Z | 07:55:00Z | 13:00–13:25 |
| 30 min | 2022-04-20 08:30:00Z | 09:00:00Z | 14:00–14:30 |
| 45 min | 2022-04-20 09:30:00Z | 10:15:00Z | 15:00–15:45 |
| 1 Hours | 2022-04-20 11:30:00Z | 12:30:00Z | 17:00–18:00 |

## Known packaging gaps

- **509 Chowk 1** under `24 Hours`: AVI parts exist; **no** `Export__*509*.xml` sidecars found — Review may still play folders, but automated inventory cannot recover Start/End from XML.
- Recursive `*.xml` under the archive includes many Review config files; filter on `Export__` + root `MediaExport` when parsing.
- Nested 24-hour packs (`Axix Bank 3`, `sangvi phata ptz`) keep their own `ExportedMedia` and sometimes deeper export subfolders — resolve `MediaClips/@folder` relative to the XML location.
