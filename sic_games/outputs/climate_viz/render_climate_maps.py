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
from sic_games.terrain import generate_world, world_lottery, world_lottery_climate, N

# representative terrain × climate worlds (biomes fall out of Whittaker) — the eyeball set
REPRESENTATIVE = [
    ("flat", "tropical"), ("flat", "subtropical"), ("flat", "temperate"), ("flat", "boreal"),
    ("mountainous", "temperate"), ("coastal", "tropical"),
]

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
    ("river_temp",  lambda F: _river_only(F),          "RdBu_r", "river water T (°C)",  None),
    ("aquatic",     lambda F: _mask(F, F.aquatic_food),"cividis","aquatic food [0-1]",  (0, 1)),
    ("wateracc",    lambda F: F.wateracc,    "Blues",   "water access [0-1]",         (0, 1)),
]
LATS = [(0.12, "tropical"), (0.32, "subtropical"), (0.52, "temperate"), (0.82, "subpolar")]


def _mask(F, fld):
    """NaN out open water so it renders blank (colormap 'bad' colour)."""
    out = fld.astype(float).copy()
    out[F.isWater == 1] = np.nan
    return out


def _river_only(F):
    """Show river water temperature (C6) only on river cells; NaN elsewhere (so montane-fed cold rivers stand out)."""
    out = np.full(F.water_temp.shape, np.nan)
    riv = (F.isRiver == 1)
    out[riv] = F.water_temp[riv]
    return out


def _worlds(archetype, seed):
    base = world_lottery(seed, archetype=archetype)
    return [(lbl, cl, generate_world({**base, "climate_latitude": cl}, mode="climate")) for cl, lbl in LATS]


def _rep_worlds(seed):
    """Representative terrain × climate worlds (biomes emergent) — for eyeballing realistic landscapes."""
    out = []
    for terr, clim in REPRESENTATIVE:
        k = world_lottery_climate(seed, terrain=terr, climate=clim)
        out.append((f"{terr}\n{clim}", f"{terr}-{clim}", generate_world(k, mode="climate")))
    return out


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


def contact_sheet(worlds, path_png, suptitle):
    nrow, ncol = len(worlds), len(LAYERS)
    fig, axes = plt.subplots(nrow, ncol, figsize=(2.6 * ncol, 2.6 * nrow))
    for r, (lbl, cl, F) in enumerate(worlds):
        for c, layer in enumerate(LAYERS):
            ax = axes[r, c]
            im, label = _render_cell(ax, F, layer)
            if r == 0:
                ax.set_title(label, fontsize=9)
            if c == 0:
                ax.set_ylabel(lbl, fontsize=9)
            if layer[0] in ("temperature", "precip", "npp"):
                fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    fig.suptitle(suptitle, fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.98))
    fig.savefig(path_png, dpi=90, bbox_inches="tight")
    plt.close(fig)


def per_layer_pngs(worlds):
    """base64 PNG per (world, layer) for the interactive HTML toggle."""
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


def write_html(worlds, path_html, title):
    imgs = per_layer_pngs(worlds)
    names = [w[1] for w in worlds]                       # stable key per world (cl)
    labels = {w[1]: w[0].replace("\n", " ") for w in worlds}
    layers = [l[0] for l in LAYERS]
    data_js = "{" + ",".join(f'"{nm}|{ly}":"{imgs[(lbl, ly)]}"'
                             for (lbl, nm, _F) in worlds for ly in layers) + "}"
    lab_js = "{" + ",".join(f'"{nm}":"{labels[nm]}"' for nm in names) + "}"
    html = f"""<!doctype html><meta charset=utf-8><title>EFC climate — {title}</title>
<style>body{{font-family:system-ui;background:#12181f;color:#dde;margin:0;padding:16px}}
button{{background:#223;color:#dde;border:1px solid #445;padding:6px 12px;margin:2px;border-radius:5px;cursor:pointer}}
button.on{{background:#2a6;color:#012;border-color:#2a6}} h2{{font-weight:600}} .row{{margin:8px 0}}
img{{background:#0b1a28;border-radius:6px;max-width:min(560px,90vw)}}</style>
<h2>EFC climate layers — {title}</h2>
<div class=row>World (terrain × climate): <span id=lat></span></div>
<div class=row>Layer: <span id=lay></span></div>
<div class=row><img id=img></div>
<p style="color:#89a;max-width:660px">What to look for — <b>temperature</b>: mountains as distinct cold patches (elevation drives the spread).
<b>precip</b>: mountains wet, their lee dry (rain shadow); tropical world wet / subtropical world dry.
<b>NPP</b>: green where warm AND wet; low where cold OR dry. <b>biome</b>: EMERGES from Whittaker(T,P) — tropical→forest, subtropical→desert, temperate→forest/grass mosaic.</p>
<script>const D={data_js},LAB={lab_js},NAMES={names!r},LAYS={layers!r};let cl=NAMES[0],cy=LAYS[1];
function draw(){{document.getElementById('img').src='data:image/png;base64,'+D[cl+'|'+cy];
[['lat',NAMES,v=>cl=v,n=>LAB[n]],['lay',LAYS,v=>cy=v,n=>n]].forEach(([id,arr,set,lab])=>{{const box=document.getElementById(id);box.innerHTML='';
arr.forEach(v=>{{const b=document.createElement('button');b.textContent=lab(v);b.className=(v==cl||v==cy)?'on':'';
b.onclick=()=>{{set(v);draw();}};box.appendChild(b);}});}});}}
draw();</script>"""
    with open(path_html, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--archetype", default=None, help="legacy: fix a terrain archetype, vary latitude (rows)")
    a = ap.parse_args()
    out = os.path.dirname(os.path.abspath(__file__))
    if a.archetype:                                     # legacy view: one terrain, four latitudes
        worlds = _worlds(a.archetype, a.seed)
        png = os.path.join(out, f"climate_{a.archetype}_seed{a.seed}.png")
        html = os.path.join(out, f"climate_{a.archetype}_seed{a.seed}.html")
        title = f"archetype {a.archetype}, seed {a.seed} (rows = latitude)"
    else:                                               # representative terrain × climate worlds (biomes emergent)
        worlds = _rep_worlds(a.seed)
        png = os.path.join(out, f"climate_representative_seed{a.seed}.png")
        html = os.path.join(out, f"climate_representative_seed{a.seed}.html")
        title = f"representative terrain × climate worlds, seed {a.seed}"
    contact_sheet(worlds, png, f"EFC climate layers — {title}")
    write_html(worlds, html, title)
    print(f"contact sheet: {png}")
    print(f"interactive:   {html}   (open in a browser; toggle world + layer)")


if __name__ == "__main__":
    main()
