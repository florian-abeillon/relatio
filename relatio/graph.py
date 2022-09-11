
import asyncio
import os
import pandas as pd

from triplestore import build_triplestore, enrich_triplestore


async def main():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'triplestore/complete_narratives.csv')
    df = pd.read_csv(path).iloc[:50]
    path = 'triplestore/blazegraph'
    _ = await build_triplestore(df, path=path)
    _ = await enrich_triplestore(spacy=True, wikidata=True, wordnet=True, path=path)


if __name__ == "__main__":
    asyncio.run(main())
