"""Stage A of Add.128: apply the code edits of enable_village_ceiling (held dark). Each edit must match once."""
def sub(path, pairs):
    s = open(path, encoding="utf-8", newline="").read()
    crlf = "\r\n" in s
    for old, new in pairs:
        if crlf:
            old, new = old.replace("\n", "\r\n"), new.replace("\n", "\r\n")
        if s.count(new) == 1:
            continue
        assert s.count(old) == 1, (path, old[:60], s.count(old))
        s = s.replace(old, new)
    open(path, "w", encoding="utf-8", newline="").write(s)

sub("sic_games/src/sic_games/phase1_model.py", [
("""        for (cx, cy), occ in occ_lists.items():
            excl_mask = None
            if excl_on:
                excl_mask = [(a.is_juvenile() and self._family_head(a) is not None) for a in occ]
                if not any(excl_mask):
                    excl_mask = None
            S = tf.level(cx, cy)
            if settle_on and (cx, cy) in self._settlement_sites:
                # Layer 2 catchment tier-2 (2b: × yearly shock; B1: × per-site soil — farms degrade it, fisheries stay 1)
                S += (self._settlement_catchment_yield((cx, cy)) * self._tier2_shock
                      * self._settlement_soil.get((cx, cy), 1.0))
            if aggl_on and aggl_R is not None:
                # AGGLOMERATION: REALIZED intensive output added to the cell pool, matching the movement-perceived
                # per-capita → increasing returns are real, no over-subscription death.
                no = len(occ)
                if aggl_mode == "point":
                    S += float(aggl_R[cy, cx]) * (no ** aggl_a - no)         # premium O(n)-baseline = A_cell·(n^β-n) → split n → A_cell·(n^(β-1)-1) each
                else:
                    na = no ** aggl_a
                    S += float(aggl_R[cy, cx]) * (na / (na + aggl_h ** aggl_a))  # catchment R·L(n) (falsified)
            # R-105: the ceiling must cover the AGGLOMERATION bonus too. It was gated on settlement sites only,
            # so the superlinear (n**aggl_a - n) term at NON-settlement cells was UNCAPPED — an unbounded
            # increasing-returns loop with no Malthusian limit (R-104: pop 3259→97551, zero starvation).
            _cap_here = (settle_on and (cx, cy) in self._settlement_sites) or (
                aggl_on and aggl_R is not None and getattr(self._demog, "enable_aggl_ceiling", False))
            if ceiling_on and _cap_here:
                S = min(S, self._settlement_carrying_capacity((cx, cy)))         # R-63: a village can't out-produce its catchment
            if self._diag_pool is not None:""",
"""        def _cell_pool(cx, cy, no):
            \"\"\"The food pool of one occupied cell, after the per-cell ceiling. This function reads state and draws no
            RNG, so `enable_village_ceiling` can call it before the harvest loop.\"\"\"
            S = tf.level(cx, cy)
            if settle_on and (cx, cy) in self._settlement_sites:
                # Layer 2 catchment tier-2 (2b: × yearly shock; B1: × per-site soil — farms degrade it, fisheries stay 1)
                S += (self._settlement_catchment_yield((cx, cy)) * self._tier2_shock
                      * self._settlement_soil.get((cx, cy), 1.0))
            if aggl_on and aggl_R is not None:
                # AGGLOMERATION: REALIZED intensive output added to the cell pool, matching the movement-perceived
                # per-capita → increasing returns are real, no over-subscription death.
                if aggl_mode == "point":
                    S += float(aggl_R[cy, cx]) * (no ** aggl_a - no)         # premium O(n)-baseline = A_cell·(n^β-n) → split n → A_cell·(n^(β-1)-1) each
                else:
                    na = no ** aggl_a
                    S += float(aggl_R[cy, cx]) * (na / (na + aggl_h ** aggl_a))  # catchment R·L(n) (falsified)
            # R-105: the ceiling must cover the AGGLOMERATION bonus too. It was gated on settlement sites only,
            # so the superlinear (n**aggl_a - n) term at NON-settlement cells was UNCAPPED — an unbounded
            # increasing-returns loop with no Malthusian limit (R-104: pop 3259→97551, zero starvation).
            _cap_here = (settle_on and (cx, cy) in self._settlement_sites) or (
                aggl_on and aggl_R is not None and getattr(self._demog, "enable_aggl_ceiling", False))
            if ceiling_on and _cap_here:
                S = min(S, self._settlement_carrying_capacity((cx, cy)))         # R-63: a village can't out-produce its catchment
            return S

        # VILLAGE CEILING (see `enable_village_ceiling`, Add.128): the ceiling above applies cell by cell, and each
        # cell has its own overlapping 9-cell sum, so a village of 7-10 cells collects several ceilings. Here the
        # pools of one village are scaled pro rata, so that their sum does not exceed the ceiling at the site.
        vpool: dict = {}                       # occupied village cell → its pool before the scale
        vscale: dict = {}                      # site → the pro-rata scale of its village
        if vceil_on:
            vsum: dict = {}
            for c, occ_c in occ_lists.items():
                s = vkey.get(c)
                if s is not None:
                    v = _cell_pool(c[0], c[1], len(occ_c))
                    vpool[c] = v
                    vsum[s] = vsum.get(s, 0.0) + v
            for s, tot in vsum.items():
                cap_s = self._settlement_carrying_capacity(s)
                vscale[s] = cap_s / tot if tot > cap_s else 1.0
        for (cx, cy), occ in occ_lists.items():
            excl_mask = None
            if excl_on:
                excl_mask = [(a.is_juvenile() and self._family_head(a) is not None) for a in occ]
                if not any(excl_mask):
                    excl_mask = None
            S = vpool[(cx, cy)] * vscale[vkey[(cx, cy)]] if (cx, cy) in vpool else _cell_pool(cx, cy, len(occ))
            if self._diag_pool is not None:"""),
("""        village_draw: dict = {}                # site → the members who draw from it (filled in the loop)
        if vgran_on:
            for c, occ_c in occ_lists.items():
                s = self._nearest_settlement(c)
                if s is not None:
                    vkey[c] = s
                    vmembers[s] = vmembers.get(s, 0) + len(occ_c)
""",
"""        village_draw: dict = {}                # site → the members who draw from it (filled in the loop)
        vceil_on = (settle_on and ceiling_on and getattr(demog, "enable_village_ceiling", False)
                    and bool(self._settlement_sites))
        if vgran_on or vceil_on:
            for c, occ_c in occ_lists.items():
                s = self._nearest_settlement(c)
                if s is not None:
                    vkey[c] = s
                    vmembers[s] = vmembers.get(s, 0) + len(occ_c)
"""),
])

sub("sic_games/src/sic_games/demography.py", [
("""    enable_density_fill_matched_radius: bool = False
""",
"""    enable_density_fill_matched_radius: bool = False
    # VILLAGE CEILING (R-106 Add.128, 2026-11-06). `_settlement_carrying_capacity` states that a village's total food
    # is capped at the catchment sum, but the harvest applies `S = min(S, cap)` cell by cell, and each occupied cell has
    # its own overlapping 9-cell sum. So a village of 7-10 cells collected 1.7-3.6 × the ceiling that the brake reads
    # (Add.128). ON ⇒ the pools of one village are scaled pro rata, so that their sum does not exceed the ceiling at
    # the site. No new parameter. The perceived food that agents read in movement does not change. It is a CORRECTION
    # under evaluation (Stage A of Add.128), so it stays dark, and `run_campaign.py` `_skip` must exclude it.
    # Default OFF ⇒ bit-exact.
    enable_village_ceiling: bool = False
"""),
])

sub("config/mechanisms.toml", [
("""[enable_density_fill_matched_radius]
value = false
""",
"""[enable_village_ceiling]
value = false
owner = "DemographyConfig"
type  = "bool"
# VILLAGE CEILING (R-106 Addendum 128, 2026-11-06). The harvest applies the catchment ceiling cell by cell,
# and each occupied cell has its own overlapping 9-cell sum, so a village of 7-10 cells collected 1.7-3.6 ×
# the ceiling that the density brake reads. ON ⇒ the pools of one village are scaled pro rata, so that their
# sum does not exceed the ceiling at the site. No new parameter. A correction under evaluation (Stage A of
# Add.128), held dark. Default OFF ⇒ bit-exact.

[enable_density_fill_matched_radius]
value = false
"""),
])

sub("config/runs/full_campaign.toml", [
("""enable_village_catchment_spread = false
""", """enable_village_catchment_spread = false
enable_village_ceiling = false
"""),
])

sub("sic_games/outputs/substrate_run/run_campaign.py", [
("""            "enable_density_fill_matched_radius",
            # FOOD-VIABLE DAUGHTER SITE""",
"""            "enable_density_fill_matched_radius",
            # VILLAGE CEILING (R-106 Add.128). Scales the pools of a village so that their sum obeys the ceiling at
            # the site. A correction under evaluation that cuts village food on every world, so C_ALLON must not
            # adopt it by side effect.
            "enable_village_ceiling",
            # FOOD-VIABLE DAUGHTER SITE"""),
])

sub("sic_games/outputs/phase1_biome_mortality/audit_flag_invariants.py", [
("""    "enable_aggl_ceiling": "P",  """, """    "enable_village_ceiling": "P",                 # bounds field→agent extraction over a village: Σ pools ≤ ceiling
    "enable_aggl_ceiling": "P",  """),
("""    "enable_aggl_ceiling": ("enable_agglomeration", "enable_catchment_ceiling", "enable_aggregation_sedentism"),
""", """    "enable_aggl_ceiling": ("enable_agglomeration", "enable_catchment_ceiling", "enable_aggregation_sedentism"),
    "enable_village_ceiling": ("enable_catchment_ceiling", "enable_aggregation_sedentism"),
"""),
])

sub("sic_games/tests/test_campaign_knobs.py", [
("""               "enable_density_fill_matched_radius",
               # STICKY PIN RELEASE""",
"""               "enable_density_fill_matched_radius",
               # VILLAGE CEILING (R-106 Add.128): a correction under evaluation, held dark.
               "enable_village_ceiling",
               # STICKY PIN RELEASE"""),
])

sub("sic_games/tests/test_runconfig_sync.py", [
("""               "enable_bud_household_closure", "enable_density_fill_matched_radius",
               #   sticky_pin_release""",
"""               "enable_bud_household_closure", "enable_density_fill_matched_radius",
               #   village_ceiling     a correction under evaluation (Add.128)
               "enable_village_ceiling",
               #   sticky_pin_release"""),
])
print("ok")
