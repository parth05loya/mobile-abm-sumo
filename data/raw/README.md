# Raw data

`synthetic_mobile_sample.csv` is a small example extract used for development and GitHub browsing.

The full V0.1 synthetic trajectory dataset is intentionally not committed because it is a generated ~20 MB file. Recreate it with:

```bash
python scripts/generate_synthetic_data.py
```

The generator writes the complete synthetic dataset to `data/generated/`.

All mobility data in this repository are synthetic; no real individual's location history is included.