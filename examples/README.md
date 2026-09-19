# Example artifacts (small)

| File | Role |
|------|------|
| `HOURS_COVERED.csv` | Per-file time-span hours + short flags (115 files) |
| `COMPLETENESS_MATRIX.csv` | Camera × day primary / `_one` presence |
| `TABLE4_COVERAGE.csv` | Camera-day coverage table (24 h expected) |

Rebuild Table 4:

```bat
python analysis\build_table4_coverage.py
```
