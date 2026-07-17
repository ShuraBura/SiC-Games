import rdata, numpy as np, pandas as pd, glob, os, warnings
warnings.filterwarnings('ignore')
from rdata.conversion import _conversion as C
def df_ctor(obj, attrs):
    fixed={}
    for k,v in obj.items():
        a = v if isinstance(v,pd.Categorical) else np.asarray(v)
        if hasattr(a,'ndim') and getattr(a,'ndim',1)>1: a=np.squeeze(a)
        fixed[k]=a
    return pd.DataFrame(fixed)
ctors=dict(C.DEFAULT_CLASS_MAP); ctors['data.frame']=df_ctor; ctors['Date']=lambda o,a: np.asarray(o)

BIOME={'Hill_Kintigh':('Ache, Paraguay','FOREST (subtrop rain forest)'),
 'Bird_Bird_Codding':('Martu, Australia','DESERT'),
 'Ziker':('Dolgan, Russia','tundra (migratory reindeer)'),
 'Winterhalder':('Cree, Canada','boreal'),
 'Alvard':('Piro, Peru','trop forest'),'Reyes_Garcia':('Tsimane, Bolivia','trop forest'),
 'Fernandez_Llamazares':('Tsimane, Bolivia','trop forest'),'Gallois':('Baka, Cameroon','trop rain forest'),
 'Duda':('Baka, Cameroon','trop rain forest'),'Gueze':('Punan, Indonesia','trop rain forest'),
 'Napitupulu':('Punan, Indonesia','trop rain forest'),'Sillitoe':('Wola, PNG','montane forest'),
 'Headland':('Agta, Philippines','trop rain forest')}

def stats(s):
    n=len(s)
    if n<30: return None
    fail=float((s==0).mean()); mu=float(s.mean()); sd=float(s.std(ddof=1))
    return n,fail,mu,(sd/mu if mu>0 else np.nan)

rows=[]
for f in sorted(glob.glob('literature/cchunts/*.rda')):
    name=os.path.basename(f)[:-4]
    try: conv=rdata.conversion.convert(rdata.parser.parse_file(f), constructor_dict=ctors)
    except Exception: continue
    d=list(conv.values())[0]
    if 'harvest' not in d.columns or 'observed' not in d.columns: continue
    m = (d['observed'].astype(float)==1)
    if 'day_trip' in d: m &= (d['day_trip'].astype(float)==1)
    if 'pooled'   in d: m &= (d['pooled'].astype(float)==0)
    if 'sex'      in d: m &= (d['sex'].astype(str)=='M')
    if 'age_type' in d and 'age_dist_1' in d:
        m &= ~((d['age_type'].astype(str)=='Exact') & (pd.to_numeric(d['age_dist_1'],errors='coerce')<18))
    st=stats(pd.to_numeric(d.loc[m,'harvest'],errors='coerce').dropna())
    if st: rows.append((name,)+st)

print(f"{'people':26} {'biome':28} {'n':>6} {'fail%':>6} {'kg/day':>7} {'CV':>5}")
print('-'*86)
for name,n,fail,mu,cv in sorted(rows,key=lambda r:r[4]):
    ppl,bio = BIOME.get(name,(name,'?'))
    print(f"{ppl:26} {bio:28} {n:>6} {fail*100:>5.1f}% {mu:>7.2f} {cv:>5.2f}")
cvs=np.array([r[4] for r in rows])
print()
print(f"{len(rows)} societies (directly-observed, single-day, individually-attributed, adult male)")
print(f"  daily-harvest CV : median {np.median(cvs):.2f}   mean {cvs.mean():.2f}   range {cvs.min():.2f}-{cvs.max():.2f}")
