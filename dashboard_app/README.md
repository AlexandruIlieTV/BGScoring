# Board Game Dashboard

This is a new browser-based dashboard that reads from the existing `bgScore.db` file without changing the original Tkinter application.

## Run

```powershell
py -3 dashboard_app\app.py
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in a browser.

## Notes

- The dashboard code is fully separate from the original app.
- It uses only Python's standard library plus SQLite, so no extra packages are required.
- The current version is read-only and focuses on summary metrics, recent sessions, top games, and top players.
