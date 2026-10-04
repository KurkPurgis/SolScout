#!/bin/bash
# run_phase4.sh - whole-world check: AFTER scene + renders with the BEFORE cameras, comparisons, report.
set -e
cd "$(dirname "$0")/.."
PY=/home/user/bvenv/bin/python
$PY tools/blender/build_after.py --render
mkdir -p renders/after
WO_SAMPLES=24 $PY tools/blender/lineups.py after blend/after.blend renders/after
if [ -d renders/before_lineups_new ] && ls renders/before_lineups_new/*.png >/dev/null 2>&1; then
  mv renders/before_lineups_new/*.png renders/before/ && rmdir renders/before_lineups_new
fi
python3 tools/apply_verdicts.py
$PY tools/compare.py
$PY tools/make_contact_sheets.py
python3 tools/verify_placements.py
python3 tools/write_import_plan.py
python3 tools/write_report.py
python3 tools/write_progress.py
echo PHASE4 DONE
