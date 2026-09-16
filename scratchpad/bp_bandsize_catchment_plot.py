"""R-106 figure: widening the food catchment grows POPULATION, not band size -> the food ceiling is not the band-size cap."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rad = [1, 2, 3]
cells = [9, 25, 49]
t_band = [10.5, 10.2, 9.0]; t_pop = [1289, 1855, 2199]
s_band = [10.5, 7.3, 8.8];  s_pop = [1089, 1181, 1085]
HILL = 28.2

fig, ax = plt.subplots(1, 2, figsize=(12.5, 5.0))

ax[0].axhline(HILL, ls="--", c="crimson", lw=1.4, label="Hill 2011 = 28.2")
ax[0].plot(cells, t_band, "o-", c="#1f77b4", label="temperate")
ax[0].plot(cells, s_band, "s-", c="#e0a030", label="savanna")
ax[0].set_xlabel("catchment size (cells; rad 1/2/3)")
ax[0].set_ylabel("band_med_adults")
ax[0].set_title("Band size is FLAT as the food ceiling rises\n(2.8x, 5.4x more catchment food -> no bigger bands)")
ax[0].set_xticks(cells); ax[0].set_ylim(0, 31); ax[0].legend(fontsize=9); ax[0].grid(alpha=0.3)

ax[1].plot(cells, t_pop, "o-", c="#1f77b4", label="temperate pop")
ax[1].plot(cells, s_pop, "s-", c="#e0a030", label="savanna pop")
ax[1].set_xlabel("catchment size (cells; rad 1/2/3)")
ax[1].set_ylabel("total population")
ax[1].set_title("The extra food grows POPULATION instead\n(Malthusian: more people + more bands, same band size)")
ax[1].set_xticks(cells); ax[1].legend(fontsize=9); ax[1].grid(alpha=0.3)

fig.suptitle("R-106 — the residence food ceiling caps POPULATION, not band size; the band-size cap is elsewhere "
             "(agglomeration clustering)", fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.95))
fig.savefig(r"C:\Users\syatom\Projects\SiC Games\scratchpad\bp_bandsize_catchment.png", dpi=110)
print("wrote bp_bandsize_catchment.png")
