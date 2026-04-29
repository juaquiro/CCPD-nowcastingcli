# NowcastingCLI

Terminal-based weather nowcasting dashboard.

Accepts periodic pressure, temperature, humidity, and altitude readings,
normalises pressure to QNH, classifies conditions as **IMPROVING / STABLE / WORSENING**,
and displays a live `rich` dashboard.

## Quick start

```bash
conda activate nowcastingcli
python -m nowcastingcli
```

See [Usage](usage.md) for full input reference, or [API Reference](api/physics.md)
for the underlying barometric formula implementation.
