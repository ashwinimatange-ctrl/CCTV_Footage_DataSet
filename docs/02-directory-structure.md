# Directory structure

## Top level (`C:\CCTV`)

```
C:\CCTV\
├── README.md
├── docs\                          # This documentation suite
├── Data_Traffic_Dataset_Pune.docx
├── Scientific Data Journal -Response Document Major Revisions.docx
└── CCTV FOOTAGE DATA\
    ├── 5 min\
    ├── 10 min\
    ├── 15 min\
    ├── 20 min\
    ├── 25 min\
    ├── 30 min\
    ├── 45 min\
    ├── 1 Hours\                   # 60-minute class
    └── 24 Hours\                  # Majority of storage (~88 GB AVI)
```

## Typical short-duration bucket (`5 min` … `1 Hours`)

Each short bucket follows the same pattern:

```
<duration>\
├── ReviewLauncher.exe             # Starts bundled offline Review
├── New Text Document.txt          # Operator note (IST date/time window)
├── ExportedMedia\                 # AVI + MediaExport XML (flat)
│   ├── Export__<Camera>_....avi
│   └── Export__<Camera>_....xml
└── Review\                        # Full Verint Review 7.6.747.0 client
    ├── Review.exe
    ├── App.config
    ├── Review.exe.config
    └── … (200+ DLLs, help, redistributables)
```

### Operator notes (IST)

| Bucket | Note content |
|--------|----------------|
| 5 min | Date :- 20-04-2022 / Time :- 10:00 to 10:05 |
| 10 min | Date :- 20-04-2022 / Time :- 10:30 to 10:40 |
| 15 min | Date :- 20-04-2022 / Time :- 10:45 to 11:00 |
| 20 min | Date :- 20-04-2022 / Time :- 11:30 to 11:50 |
| 25 min | Date :- 20-04-2022 / Time :- 13:00 to 13:25 |
| 30 min | Date :- 20-04-2022 / Time :- 14:00 to 14:30 |
| 45 min | Date :- 20-04-2022 / Time :- 15:00 to 15:45 |
| 1 Hours | Date :- 20-04-2022 / Time :- 17:00 to 18:00 |
| 24 Hours | Date :- 21-04-2022 / Time :- 00:00 to 11:59 |

These IST windows match MediaExport `StartTime`/`EndTime` in UTC after applying India Standard Time (+05:30) for the short buckets (e.g. 5 min XML `04:30:00Z`–`04:35:00Z` ≡ 10:00–10:05 IST).

## `24 Hours` layout (irregular)

Unlike short buckets, `24 Hours` mixes flat export folders, nested camera packs (each with their own `Review\`), and some duplicated Mahavir Chowk folders at the bucket root:

```
24 Hours\
├── ReviewLauncher.exe
├── New Text Document.txt
├── Review\                                 # Bucket-level player
├── Export__Mahavir Chowk 1_... b2c09d2\    # Duplicate-style loose pack at root
├── Export__Mahavir Chowk 1_... dc8633c\
└── ExportedMedia\
    ├── Axix Bank 3\                        # Typo: "Axix"; own Review + ExportedMedia
    │   ├── ReviewLauncher.exe
    │   ├── Review\
    │   └── ExportedMedia\...
    ├── sangvi phata ptz\                   # Own Review + ExportedMedia
    │   ├── ReviewLauncher.exe
    │   ├── Review\
    │   └── ExportedMedia\...
    ├── Export__509 Chowk 1_... \           # Multi-part AVI folders (often no XML)
    ├── Export__Bhel Chowk- 4_... \
    └── Export__Mahavir Chowk 1_... \
```

**Notes:**

- Nested packs under `Axix Bank 3` and `sangvi phata ptz` each ship a complete Review client — this is why Review folder count is **11**, not 9.
- Longer recordings split into multiple AVI parts (`*_2.avi`, `*_3.avi`, …) listed in one MediaExport XML when the sidecar exists.
- Root-level Mahavir folders appear to mirror content also under `ExportedMedia\` — treat as possible copy/export residue when inventorying unique footage.

## What lives under `Review\`

The Review tree is a proprietary Verint Systems **Nextiva Review** offline smart client (WCF `netTcpBinding` on localhost). It is **vendor software**, not project source. Useful entry points:

| Path | Role |
|------|------|
| `ReviewLauncher.exe` | Convenience launcher beside `ExportedMedia` |
| `Review\Review.exe` | Main player UI |
| `Review\App.config` / `Review.exe.config` | Local service endpoints and export options |
| `Review\ReviewHelp\` | Bundled product help |

Do not expect project-owned configuration beyond these vendor defaults.

## Non-media XML noise

A recursive `*.xml` count under `CCTV FOOTAGE DATA` is **~438**, but only **~53** files are Verint **`Export__*.xml`** MediaExport manifests. The rest are Review/player configuration and module XML inside the duplicated `Review\` trees.
