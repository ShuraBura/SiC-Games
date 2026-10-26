"""Run the test_runconfig_sync FIDELITY check with an explicit stdin.

The three remaining failures in `sic_games/tests/test_runconfig_sync.py` are `OSError: [WinError 6] The handle
is invalid`, raised inside `subprocess._make_inheritable` BEFORE the child process starts. The tests call
`subprocess.run(...)` without `stdin=`, so the child inherits this shell's stdin, and this shell's stdin handle
is not valid on Windows. That is an environment artifact, not a defect in the code under test.

This script runs the SAME campaign the test runs, with `stdin=subprocess.DEVNULL`, and performs the same
comparison, so the fidelity guarantee is actually checked.
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = r"C:\Users\syatom\Projects\SiC Games"
camp = os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py")
tag = "_t_hhclosure_fidelity"
out = os.path.join(os.path.dirname(camp), f"campaign_trajectory{tag}.json")
env = dict(os.environ, C_ALLON="1", C_TAG=tag, C_STEPS="2", C_FOUNDERS="150", C_MAXMIN="5",
           C_LOGEVERY="600", C_GENEA="0")

with tempfile.TemporaryFile() as devnull:
    p = subprocess.run([sys.executable, "-u", camp], cwd=ROOT, env=env,
                       stdin=subprocess.DEVNULL, stdout=devnull,
                       stderr=subprocess.PIPE, text=True, timeout=900)
print("campaign returncode:", p.returncode)
if p.returncode != 0 or not os.path.exists(out):
    print(p.stderr[-2000:])
    raise SystemExit(1)

meta = json.load(open(out, encoding="utf-8"))["meta"]
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
from sic_games import runconfig                                    # noqa: E402
from sic_games.demography import DemographyConfig                  # noqa: E402

files = runconfig.load(refresh=True)["DemographyConfig"]
ran = meta["demography_config"]
diff = {k: (files.get(k), ran.get(k)) for k in DemographyConfig.model_fields
        if k in ran and files.get(k) != ran.get(k)}
print("FIDELITY mismatches (files vs the run):", len(diff))
for k, v in list(diff.items())[:10]:
    print("   ", k, "files=", v[0], "run=", v[1])
print()
print("new flag  in config/mechanisms.toml:", files.get("enable_bud_household_closure"))
print("new flag  in the C_ALLON=1 run     :", ran.get("enable_bud_household_closure"),
      "   <- must be False: it is in run_campaign's _skip")
try:
    os.remove(out)
    os.remove(out.replace("trajectory", "progress").replace(".json", ".txt"))
except OSError:
    pass
