#!/usr/bin/env python3
"""
Supplementary material S3, S4 and S6
Limitations of the Student Model in High-Demand Contexts:
A Structured Review of Underrepresented Functional State Variables

Reproduces, from the raw database exports, every count reported in the article:
the de-duplication log, the pre-filter exclusions, and the coverage figures of
Table 2. Requires only pandas.

    python3 S6_reproduce_analysis.py --scopus-a FILE --scopus-b FILE \
                                     --wos-a FILE [FILE ...] --wos-b FILE

Searches executed 28-29 July 2026.
"""
import argparse, re, unicodedata
from pathlib import Path
import pandas as pd

# ---------------------------------------------------------------- utilidades

def norm_title(s):
    """Título normalizado: sin diacríticos, sin puntuación, en minúsculas."""
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '', s.lower())


def norm_doi(s):
    """DOI normalizado: minúsculas, sin prefijo de resolución."""
    if pd.isna(s) or not str(s).strip():
        return ''
    return re.sub(r'^https?://(dx\.)?doi\.org/', '', str(s).strip().lower())


# ---------------------------------------------------------------- carga

def load_scopus(path, branch):
    d = pd.read_csv(path)
    return pd.DataFrame({
        'db': 'Scopus', 'branch': branch,
        'authors': d['Authors'], 'year': d['Year'], 'title': d['Title'],
        'venue': d['Source title'], 'doi': d['DOI'], 'abstract': d['Abstract'],
        'keywords': d['Author Keywords'].fillna('') + '; ' + d['Index Keywords'].fillna(''),
        'doctype': d['Document Type'],
    })


def load_wos(paths, branch):
    d = pd.concat([pd.read_excel(p) for p in paths], ignore_index=True)
    tc = [c for c in d.columns if c.lower().startswith('article title')][0]
    sc = [c for c in d.columns if c.lower().startswith('source title')][0]
    ab = [c for c in d.columns if c.lower() == 'abstract'][0]
    kw = [c for c in d.columns if 'keyword' in c.lower()]
    return pd.DataFrame({
        'db': 'WoS', 'branch': branch,
        'authors': d['Authors'], 'year': d['Publication Year'], 'title': d[tc],
        'venue': d[sc], 'doi': d['DOI'], 'abstract': d[ab],
        'keywords': d[kw].fillna('').agg('; '.join, axis=1) if kw else '',
        'doctype': d['Publication Type'],
    })


# ---------------------------------------------------------------- S3

def deduplicate(all_):
    """Tres pasos sucesivos. Devuelve el corpus único y el log de eliminados."""
    all_ = all_.copy()
    all_['_t'] = all_['title'].map(norm_title)
    all_['_d'] = all_['doi'].map(norm_doi)
    log = []

    # Paso 0 - duplicados internos entre las ramas A y B de una misma base
    dup = all_.duplicated(subset=['db', '_t'], keep='first')
    log.append(all_[dup].assign(step='0 intra-base (ramas A/B)'))
    m = all_[~dup]

    # Paso 1 - coincidencia exacta de DOI
    has = m['_d'] != ''
    dup = m[has].duplicated(subset=['_d'], keep='first')
    log.append(m[has][dup].assign(step='1 DOI exacto'))
    m = pd.concat([m[has][~dup], m[~has]], ignore_index=True)

    # Paso 2 - coincidencia de título normalizado
    dup = m.duplicated(subset=['_t'], keep='first')
    log.append(m[dup].assign(step='2 titulo normalizado'))
    m = m[~dup].reset_index(drop=True)

    return m, pd.concat(log, ignore_index=True)


# ---------------------------------------------------------------- S4

SYSTEM_TERMS = [
    "intelligent tutor", "tutoring system", "student model", "learner model",
    "user model", "adaptive learning", "adaptive educational", "adaptive instruction",
    "knowledge tracing", "cognitive diagnos", "adaptive system", "adaptive testing",
    "adaptive assessment", "recommender", "personaliz", "adaptive support",
    "learning system", "e-learning system", "tutor", "learning analytics",
    "learner profil", "student profil", "learning path", "learning environment",
]

NON_RESEARCH = r'^(editorial|erratum|retracted|note|letter|conference review|correction)'


def prefilter(m):
    """Tres reglas deterministas. Ninguna excluye estudio alguno del corpus analizado."""
    blob = (m['title'].fillna('') + ' || ' + m['abstract'].fillna('')
            + ' || ' + m['keywords'].fillna('')).str.lower()
    r1 = m['doctype'].fillna('').str.lower().str.match(NON_RESEARCH)
    r2 = m['abstract'].isna() & (
        m['keywords'].fillna('').str.strip().str.strip(';').str.len() == 0)
    r3 = ~blob.apply(lambda b: any(s in b for s in SYSTEM_TERMS))
    return ~(r1 | r2 | r3), r1, r2, r3


# ---------------------------------------------------------------- S6

FSV_PATTERNS = {
    'Sleep quality':      r'\bsleep\b|sleep quality|sleep deprivation|sleep restriction|circadian',
    'Training load':      r'training load|physical training|exercise load|athletic training|physical activity load',
    'Mental fatigue':     r'mental fatigue|cognitive fatigue|mental exhaustion|fatigue',
    'Perceived stress':   r'perceived stress|psychological stress|stress level|cortisol|academic stress',
    'Competition phase':  r'competition phase|competitive season|pre-competition|athletic competition',
    'Academic pressure':  r'academic pressure|academic stress|academic workload|exam stress',
}
RELATED_PATTERNS = {
    'Cognitive load':       r'cognitive load|mental workload|working memory load',
    'Physiological signal': (r'\beeg\b|electroencephal|heart rate variability|\bhrv\b|galvanic skin'
                             r'|electroderm|eye.track|pupillometr|wearable|physiological (signal|sensor|measure)'),
}


def coverage(m):
    blob = (m['title'].fillna('') + ' || ' + m['abstract'].fillna('')
            + ' || ' + m['keywords'].fillna('')).str.lower()
    rows, any_ = [], pd.Series(False, index=m.index)
    for name, pat in FSV_PATTERNS.items():
        hit = blob.str.contains(pat, regex=True)
        any_ |= hit
        rows.append((name, int(hit.sum()), round(100 * hit.mean(), 2)))
    rows.append(('Any of the six', int(any_.sum()), round(100 * any_.mean(), 2)))
    rows.append(('None', int((~any_).sum()), round(100 * (~any_).mean(), 2)))
    for name, pat in RELATED_PATTERNS.items():
        hit = blob.str.contains(pat, regex=True)
        rows.append((name + ' (related construct)', int(hit.sum()), round(100 * hit.mean(), 2)))
    return pd.DataFrame(rows, columns=['Variable', 'Records', '%'])


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scopus-a', required=True)
    ap.add_argument('--scopus-b', required=True)
    ap.add_argument('--wos-a', required=True, nargs='+')
    ap.add_argument('--wos-b', required=True)
    ap.add_argument('--outdir', default='.', help='directorio de salida para S3 y S4')
    a = ap.parse_args()
    out = Path(a.outdir); out.mkdir(parents=True, exist_ok=True)

    all_ = pd.concat([
        load_scopus(a.scopus_a, 'A'), load_scopus(a.scopus_b, 'B'),
        load_wos(a.wos_a, 'A'), load_wos([a.wos_b], 'B'),
    ], ignore_index=True)

    print(f'Records identified            {len(all_):>6}')
    print(all_.groupby(['db', 'branch']).size().to_string(), '\n')

    m, log = deduplicate(all_)
    print(f'Duplicates removed            {len(log):>6}')
    print(log['step'].value_counts().to_string())
    print(f'Unique records                {len(m):>6}\n')
    log.drop(columns=['_t', '_d']).to_csv(out / 'S3_deduplication_log.csv', index=False)

    keep, r1, r2, r3 = prefilter(m)
    print(f'Excluded by pre-filter        {(~keep).sum():>6}')
    print(f'  R1 non-research type        {r1.sum():>6}')
    print(f'  R2 no abstract nor keywords {r2.sum():>6}')
    print(f'  R3 no system-related term   {r3.sum():>6}')
    excl = m.loc[~keep].drop(columns=['_t', '_d']).copy()
    excl['exclusion_rule'] = [
        ' + '.join(x for x, f in (('R1 non-research document type', b1),
                                  ('R2 no abstract nor keywords', b2),
                                  ('R3 no system-related term', b3)) if f)
        for b1, b2, b3 in zip(r1[~keep], r2[~keep], r3[~keep])]
    excl.to_csv(out / 'S4_prefilter_excluded_records.csv', index=False)

    corpus = m[keep].reset_index(drop=True)
    print(f'VERIFICATION CORPUS           {len(corpus):>6}\n')
    print('Table 2 - Coverage of functional state variables')
    print(coverage(corpus).to_string(index=False))


if __name__ == '__main__':
    main()
