"""Holdout rule (PROTOCOL.md rule 4). A country is in the holdout if the first hex digit of
sha256(ISO3 code) is 0-4. The rule depends only on the code, so it is the same for every dataset.
Loaders must call split() and must not read holdout rows until a question's final test."""
import hashlib
def is_holdout(iso3): return hashlib.sha256(iso3.strip().upper().encode()).hexdigest()[0] in '01234'
def split(df, col='countrycode'):
    m=df[col].map(is_holdout); return df[~m].copy(), df[m].copy()
