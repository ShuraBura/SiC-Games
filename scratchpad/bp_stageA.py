"""R-106 Add.128 Stage A: run the three observers of Add.128 on one run, so that the signals, the store and the account come
from the same world at the same step.

The observers are not rewritten. Each source file is executed up to the line where it patches the model, and the patches are
chained here. Each observer reads state, draws no RNG and writes no model attribute (acct sets the documented `_diag_pool`).
Logs: design_logs/sig<tag>.jsonl, sto<tag>.jsonl, acc<tag>.jsonl.
"""
import os
import runpy
import sys

ROOT = r"C:\Users\syatom\Projects\SiC Games"
sys.path.insert(0, os.path.join(ROOT, "sic_games", "src"))
import sic_games.climate as CL   # noqa: E402
from sic_games.phase1_model import TerrainWorld   # noqa: E402


def load(fname, cut):
    path = os.path.join(ROOT, "scratchpad", fname)
    src = open(path, encoding="utf-8").read()
    assert src.count(cut) == 1, (fname, cut)
    ns = {"__name__": "obs_" + fname[:-3], "__file__": path}
    exec(compile(src[:src.index(cut)], path, "exec"), ns)
    return ns


sig = load("bp_design_signals.py", "CL.build_climate_field = _build")
CL.build_climate_field = sig["_build"]
TerrainWorld.step = sig["_step"]
sto = load("bp_design_store.py", "CL.build_climate_field = _build")
TerrainWorld.step = sto["_step"]
setattr(TerrainWorld, sto["_hook_name"], sto["_hook"])
acc = load("bp_design_acct.py", "TerrainWorld.step = _step")
TerrainWorld.step = acc["_step"]
runpy.run_path(os.path.join(ROOT, "sic_games", "outputs", "substrate_run", "run_campaign.py"), run_name="__main__")
