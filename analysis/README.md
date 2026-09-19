# Analysis scripts

Deposit completeness, coverage Table 4, and comparison helpers. No video required.

| Script | Role |
|--------|------|
| `scan_mendeley_completeness.py` | Scan local Mendeley CSVs → completeness matrix + time spans |
| `hours_covered.py` | Per-file first–last hour spans + short flags |
| `build_table4_coverage.py` | Camera-day Table 4 (24 h expected operating day) |
| `comparison_table.py` | Public-dataset positioning table |

## Quick demo (bundled examples)

```bat
cd github-submission
python analysis\build_table4_coverage.py
```

Uses [`examples/HOURS_COVERED.csv`](../examples/HOURS_COVERED.csv) and
[`examples/COMPLETENESS_MATRIX.csv`](../examples/COMPLETENESS_MATRIX.csv).

## Full local scan

```bat
set MENDELEY_CSV=D:\path\to\extracted\traffic
python analysis\scan_mendeley_completeness.py
set TIME_SPANS_CSV=%CD%\artifacts\analysis\TIME_SPANS.csv
set HOURS_CSV=%CD%\artifacts\analysis\HOURS_COVERED.csv
set MATRIX_CSV=%CD%\artifacts\analysis\COMPLETENESS_MATRIX.csv
python analysis\hours_covered.py
python analysis\build_table4_coverage.py
```
