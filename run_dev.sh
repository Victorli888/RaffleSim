#!/usr/bin/env bash
# Run Streamlit with explicit auto-reload settings (from project root).
set -euo pipefail
cd "$(dirname "$0")"
exec streamlit run app.py \
  --server.fileWatcherType poll \
  --server.runOnSave true \
  --runner.fastReruns true
