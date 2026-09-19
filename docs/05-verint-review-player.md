# Verint Review offline player

## What it is

Each duration bucket (and some nested 24-hour camera packs) includes a full **Verint Systems Nextiva Review** offline client:

| Property | Value |
|----------|--------|
| Product | Verint Review / Nextiva Review |
| File version | **7.6.747.0** |
| Company | Verint Systems Inc. |
| Role | Play and inspect MediaExport packages without connecting to a live NVR |

This is **vendor binary software**, not source code for this archive.

## How to launch

### Short buckets (`5 min` … `1 Hours`)

1. Navigate to e.g. `C:\CCTV\CCTV FOOTAGE DATA\5 min\`
2. Run **`ReviewLauncher.exe`**
3. Alternatively run `Review\Review.exe`

Keep `ExportedMedia\` next to the launcher so the offline package resolves clips correctly.

### 24-hour nested packs

For Axis Bank 3 or Sangvi Phata PTZ packs that ship their own player:

```
...\24 Hours\ExportedMedia\Axix Bank 3\ReviewLauncher.exe
...\24 Hours\ExportedMedia\sangvi phata ptz\ReviewLauncher.exe
```

Or use the bucket-level launcher:

```
...\24 Hours\ReviewLauncher.exe
```

Prefer launching from the folder that sits beside the specific `ExportedMedia` you intend to open.

## Runtime expectations

- **OS:** Windows (x86/x64). Review trees include Visual C++ redistributables (`vc_redist.x64.exe`, `vcredist_x86.exe`).
- **Architecture:** .NET smart client with Enterprise Library / log4net and local **WCF** services.
- **Local services (from `App.config`):**
  - `net.tcp://localhost:7020/Review` — Review application / subscription services
  - `net.tcp://localhost:7030/ReviewGatewayService` — gateway service

These endpoints are for the **local offline player**, not a public CCTV API.

## Notable `App.config` settings

Observed under e.g. `5 min\Review\App.config`:

| Setting | Observed value | Meaning |
|---------|----------------|---------|
| `AutoCloseExport` | `true` | Export-related UI auto-close behavior |
| `HideExportGenericAVIOption` | `false` | Generic AVI export option visibility |
| `EnableConnectToSiteByTemplate` | `False` | Offline / no template connect by default |
| `ConnectToSiteTemplate` | `server.sXXXXX.us.verint.com` | Placeholder Verint site template (not used for local exports) |

Do not treat these as secrets for this research archive; they are vendor defaults for a Review install.

## Operator environment residue

Some Review config/temp artifacts (e.g. `temp0.ini` in prior exploration) may reference older operator paths such as `C:\Users\cc-op1\...` or leftover camera names. Those are **historical workstation leftovers**, not instructions for this machine.

## Playing without Review

- Many AVIs may open in **VLC**, **ffplay**, or similar, but Verint packaging / codecs can fail outside Review.
- Prefer Review for authoritative playback, bookmarks, and multi-part export continuity.
- If using ffmpeg for research pipelines, validate decode on a short-bucket sample before batch-processing ~88 GB of 24-hour video.

## Practical tips

1. Start with **`5 min`** to confirm Review starts and codecs work.
2. Avoid running multiple Review copies from different folders at once (shared localhost ports 7020/7030).
3. Disk: ensure tens of GB free before opening long 24-hour sessions; the player may cache or index locally.
4. Antivirus may slow first launch while scanning the large `Review\` DLL set.
