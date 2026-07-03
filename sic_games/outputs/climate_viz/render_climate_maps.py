"""Climate-layer visualizer (EFC eyeball tool) — renders the REAL Python climate fields (canonical), so there is no
second JS implementation to drift. Produces (1) a cross-latitude CONTACT SHEET (rows = regional climate_latitude,
cols = layer) and (2) a self-contained HTML with layer + latitude toggles. Open the HTML in any browser.

Layers: elevation, temperature (annual mean, °C), precipitation (mm/yr), NPP (Miami, g/m²/yr), biome, water access.

Run:  py -3 outputs/climate_viz/render_climate_maps.py
      py -3 outputs/climate_viz/render_climate_maps.py --archetype montane --seed 0
"""
import os, sys, io, base64, argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "biome_society_20260702"))
from sic_games.terrain import generate_world, world_lottery, N

# biome palette (matches the sic_terrain_prototype BIOME_COL)
BIOME_COL = np.array([
    [24, 72, 120], [29, 158, 117], [23, 80, 30], [186, 150, 40],
    [170, 185, 105], [216, 170, 120], [120, 118, 112]], dtype=float) / 255.0
BIOME_NAME = ["water", "wetland", "forest", "savanna", "grassland", "desert", "mountain"]
BIOME_CMAP = ListedColormap(BIOME_COL)
BIOME_NORM = BoundaryNorm(np.arange(-0.5, 7.5, 1.0), BIOME_CMAP.N)

# (field name, accessor, colormap, label, [vmin, vmax] or None)
LAYERS = [
    ("elevation",   lambda F: F.elev,        "terrain", "elevation [0-1]",          (0, 1)),
    ("temperature", lambda F: _mask(F, F.temperature), "RdBu_r", "annual mean T (°C)", None),
    ("precip",      lambda F: _mask(F, F.precip_mm),   "YlGnBu", "precip (mm/yr)",     (0, 3000)),
    ("npp",         lambda F: _mask(F, F.npp_gm2),     "YlGn",   "NPP Miami (g/m²/yr)",(0, 2500)),
    ("biome",       lambda F: F.biome.astype(float),   None,     "biome",              None),
    ("wateracc",    lambda F: F.wateracc,    "Blues",   "water access [0-1]",         (0, 1)),
]
LATS = [(0.12, "tropical"), (0.32, "subtropical"), (0.52, "temperate"), (0.82, "subpolar")]


def _mask(F, fld):
    """NaN out open water so it renders blank (colormap 'bad' colour)."""
    out = fld.astype(float).copy()
    out[F.isWater == 1] = np.nan
    return out


def _worlds(archetype, seed):
    base = world_lottery(seed, archetype=archetype)
    return [(lbl, cl, generate_world({**base, "climate_latitude": cl}, mode="climate")) for cl, lbl in LATS]


def _render_cell(ax, F, layer):
    name, acc, cmap, label, vlim = layer
    data = acc(F)
    if name == "biome":
        im = ax.imshow(data, cmap=BIOME_CMAP, norm=BIOME_NORM, interpolation="nearest")
    else:
        cm = plt.get_cmap(cmap).copy(); cm.set_bad("#0b1a28")
        vmin, vmax = (vlim if vlim else (np.nanmin(data), np.nanmax(data)))
        im = ax.imshow(data, cmap=cm, vmin=vmin, vmax=vmax, interpolation="nearest")
    ax.set_xticks([]); ax.set_yticks([])
    return im, label


def contact_sheet(archetype, seed, path_png):
    worlds = _worlds(archetype, seed)
    nrow, ncol = len(worlds), len(LAYERS)
    fig, axes = plt.subplots(nrow, ncol, figsize=(2.6 * ncol, 2.6 * nrow))
    for r, (lbl, cl, F) in enumerate(worlds):
        for c, layer in enumerate(LAYERS):
            ax = axes[r, c]
            im, label = _render_cell(ax, F, layer)
            if r == 0:
                ax.set_title(label, fontsize=9)
            if c == 0:
                ax.set_ylabel(f"{lbl}\n(lat={cl})", fontsize=9)
            if layer[0] in ("temperature", "precip", "npp"):
                fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    fig.suptitle(f"EFC climate layers — archetype={archetype}, seed={seed}  (rows = regional latitude)", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    fig.savefig(path_png, dpi=90, bbox_inches="tight")
    plt.close(fig)


def per_layer_pngs(archetype, seed):
    """base64 PNG per (latitude, layer) for the interactive HTML toggle."""
    worlds = _worlds(archetype, seed)
    imgs = {}
    for lbl, cl, F in worlds:
        for layer in LAYERS:
            fig, ax = plt.subplots(figsize=(3.4, 3.4))
            im, label = _render_cell(ax, F, layer)
            ax.set_title(f"{layer[0]} — {lbl}", fontsize=10)
            if layer[0] in ("temperature", "precip", "npp"):
                fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
            buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=95, bbox_inches="tight"); plt.close(fig)
            imgs[(lbl, layer[0])] = base64.b64encode(buf.getvalue()).decode()
    return imgs


def write_html(archetype, seed, path_html):
    imgs = per_layer_pngs(archetype, seed)
    lats = [lbl for _, lbl in LATS]
    layers = [l[0] for l in LAYERS]
    data_js = "{" + ",".join(f'"{lbl}|{ly}":"{imgs[(lbl,ly)]}"' for lbl in lats for ly in layers) + "}"
    html = f"""<!doctype html><meta charset=utf-8><title>EFC climate — {archetype}</title>
<style>body{{font-family:system-ui;background:#12181f;color:#dde;margin:0;padding:16px}}
button{{background:#223;color:#dde;border:1px solid #445;padding:6px 12px;margin:2px;border-radius:5px;cursor:pointer}}
button.on{{background:#2a6;color:#012;border-color:#2a6}} h2{{font-weight:600}} .row{{margin:8px 0}}
img{{background:#0b1a28;border-radius:6px;max-width:min(560px,90vw)}}</style>
<h2>EFC climate layers — archetype <b>{archetype}</b>, seed {seed}</h2>
<div class=row>Region (latitude): <span id=lat></span></div>
<div class=row>Layer: <span id=lay></span></div>
<div class=row><img id=img></div>
<p style="color:#89a;max-width:640px">What to look for — <b>temperature</b>: mountains as distinct cold patches (elevation, not latitude, drives the spread).
<b>precip</b>: coherent wet/dry (wetter near water + windward), tropical region wet / subtropical region dry.
<b>NPP</b>: green where warm AND wet; low where cold OR dry. <b>biome</b>: coherent regions, not confetti (pre-Whittaker classifier for now).</p>
<script>const D={data_js},LATS={lats!r},LAYS={layers!r};let cl=LATS[2],cy=LAYS[1];
function draw(){{document.getElementById('img').src='data:image/png;base64,'+D[cl+'|'+cy];
[['lat',LATS,v=>cl=v],['lay',LAYS,v=>cy=v]].forEach(([id,arr,set])=>{{const box=document.getElementById(id);box.innerHTML='';
arr.forEach(v=>{{const b=document.createElement('button');b.textContent=v;b.className=(v==cl||v==cy)?'on':'';
b.onclick=()=>{{set(v);draw();}};box.appendChild(b);}});}});}}
draw();</script>"""
    with open(path_html, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archetype", default="montane")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    out = os.path.dirname(os.path.abspath(__file__))
    png = os.path.join(out, f"climate_{a.archetype}_seed{a.seed}.png")
    html = os.path.join(out, f"climate_{a.archetype}_seed{a.seed}.html")
    contact_sheet(a.archetype, a.seed, png)
    write_html(a.archetype, a.seed, html)
    print(f"contact sheet: {png}")
    print(f"interactive:   {html}   (open in a browser; toggle region + layer)")


if __name__ == "__main__":
    main()
