# Raffle Prize Distribution Simulator

## Run locally

```bash
cd raffle-sim
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Auto-reload on save

The app is configured in `.streamlit/config.toml` to rerun when you save a file (`runOnSave = true`).

If changes still do not appear:

1. **Restart Streamlit** after editing `config.toml` (stop the terminal with `Ctrl+C`, then run again).
2. Run from the **project root** so `.streamlit/config.toml` is picked up:
   ```bash
   cd /path/to/raffle-sim
   streamlit run app.py
   ```
3. In the app menu (⋮ top-right) → **Settings** → turn on **Run on save** if it is off.
4. Force poll mode explicitly:
   ```bash
   streamlit run app.py --server.fileWatcherType poll --server.runOnSave true
   ```
5. Confirm you see **“File change.”** in the app header a few seconds after saving. If you do not, the watcher is not seeing your files (wrong directory or remote filesystem).

`fileWatcherType = "poll"` is intentional: it works better with Cursor/VS Code than `watchdog` on macOS.
