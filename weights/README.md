# Model weights (not included)

Place COCO-pretrained **YOLOv8n** weights here as:

```
weights/yolov8n.pt
```

This file is **gitignored** (~6 MB). Do not commit it.

## How to obtain

**Option A — Ultralytics auto-download (local Python)**

With `ultralytics` installed, first run can fetch `yolov8n.pt` into the current working directory; move it to `weights/yolov8n.pt`.

**Option B — Explicit download**

From the Ultralytics / GitHub release assets for YOLOv8, download `yolov8n.pt` and copy it into this folder.

**Option C — Docker note**

The Docker image does **not** rely on in-container download. Mount this `weights/` directory (compose does this read-only). Ensure `yolov8n.pt` exists on the host before running.

## Config reference

[`config/config.yaml`](../config/config.yaml) expects:

```yaml
detector:
  weights: weights/yolov8n.pt
```
