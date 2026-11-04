"""Insert Add.126 into RESULTS, the anchor entry into LITERATURE, and update the audit pointer."""
s = open("scratchpad/add126_text.md", encoding="utf-8").read()
r = open("docs/RESULTS.md", encoding="utf-8").read()
end = "*End of RESULTS — seeded"
assert r.count(end) == 1
open("docs/RESULTS.md", "w", encoding="utf-8").write(r.replace(end, s + end))

ENTRY = """
### Dribe, M., Olsson, M. & Svensson, P. (2010). "Economic Crisis, Manorialism, and Demographic Response: Southern Sweden in the Preindustrial Period." In Kurosu, Bengtsson & Campbell (eds.), *Demographic Responses to Economic and Environmental Crises*, Proceedings of the IUSSP Seminar, May 21–23, 2009, Reitaku University, Kashiwa, pp. 17–44. (Open PDF of the volume: iussp.org/sites/default/files/AllArticles.pdf. Not filed in `literature/`. Table 3 read 2026-11-04.)
**What was lifted — the short-run response to a food-supply shock, by age (Add.126):** Scania, about 400 parishes, 1749–1859, OLS, annual, elasticities at the means. To grain OUTPUT, model with one lag: births −0.001 (p 0.945) same year, +0.082 lag; deaths ages 1–9 −0.521, −0.612; deaths ages 15–24 −0.261, −0.404. To rye PRICE: births −0.041, −0.144; deaths 1–9 +0.147, +0.286; deaths 15–24 +0.118, +0.148. **How used:** the direction and the shape of the split between mortality and fertility under a food shock, against the drought test of Add.125. **Rejected:** use as a calibration target: agrarian, with markets, one-year deviations in the normal range, not foragers and not a −30% shock. Manorial parishes respond less in the same year, so institutions change the size.
**Citation tag:** [DIRECTION + SHAPE — food shock: mortality carries more than births; agrarian comparator, not a forager target]

### Cai, Y. & Wang, F. (2010). "Reproductive Consequences of China's Great Leap Forward Famine." Same volume, from p. 133. (Introduction read 2026-11-04.)
**What was lifted — the upper reference for a birth collapse:** official statistics: crude death rate 10.8 (1957) → 25.3 per 1000 (1960); crude birth rate 34 (1957) → 18 (1961), then 43.4 (1963). **How used:** a scale for the model's first-years fall in births (Add.126). **Rejected:** any use as a size for a ×0.70 drought.
**Citation tag:** [COMPARATOR — extreme famine]

### Jennings, J.A., Quaranta, L. & Bengtsson, T. (2017). "Inequality and demographic response to short-term economic stress in North Orkney, Scotland, 1855–1910: sector differences." *Population Studies* 71(3):313–328. (Open: PMC5663246. Read through a summary of the full text, 2026-11-04; numbers to confirm against the tables before any use as more than a comparator.)
**What was lifted — responses to a 10% rise in oatmeal price:** child mortality ages 1–15 +20% (p 0.02); infants −2.9% (n.s.); higher-order births −0.1% same year, −4.2% lagged (p 0.06). The paper cites other work: Italy +11%, Sweden +4% (real wages), Belgium +3%. **How used:** the range of the price response (Add.126). **Rejected:** a price is not a food supply.
**Citation tag:** [COMPARATOR — price response; infants do not respond]

### de Waal, A., Taffesse, A.S. & Carruth, L. (2006). "Child survival during the 2002–2003 drought in Ethiopia." *Global Public Health*. (Publisher summary only, 2026-11-04.)
**What was lifted:** 4,816 households; no measurable rise in child mortality in the general population; the higher mortality of drought areas is attributed to chronic conditions. **How used:** a real drought can pass without a mortality response, so a null is possible (Add.126). **Rejected:** transfer to foragers; food aid was present.
**Citation tag:** [COMPARATOR — null mortality response, summary only]

### Dyson, T. (1993). "Demographic Responses to Famines in South Asia." *IDS Bulletin*. (Abstract only, 2026-11-04.)
**What was lifted:** conceptions fall promptly and almost universally; the rise in deaths is less certain and depends on disease, migration, relief and rain. **How used:** the ORDER of the response (Add.126). **Rejected:** any size; the abstract gives none.
**Citation tag:** [DIRECTION — order of response, abstract only]
"""
p = "docs/LITERATURE.md"
t = open(p, encoding="utf-8").read()
marker = "\nSource: [Man the Hunter, Lee & DeVore]"
assert t.count(marker) == 1
open(p, "w", encoding="utf-8").write(t.replace(marker, "\n" + ENTRY + marker))

q = "audit/2026-10-26/00_START_HERE.md"
a = "corrects Add.119 (Add.125, 2026-11-04). **For the current verdicts read"
u = open(q, encoding="utf-8").read()
assert u.count(a) == 1
open(q, "w", encoding="utf-8").write(u.replace(a, "corrects Add.119 (Add.125, 2026-11-04); and the anchor for that test (Add.126). **For the current verdicts read"))
