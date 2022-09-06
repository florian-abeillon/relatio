
import os
import pandas as pd

from triplestore import build_triplestore


def main():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'triplestore/complete_narratives.csv')
    df = pd.read_csv(path).iloc[:250]
    _ = build_triplestore(df, spacy=False, wikidata=False, wordnet=False, path='triplestore/blazegraph')


if __name__ == "__main__":
    main()
