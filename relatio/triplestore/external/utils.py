
import spacy

pipes_to_disable = [ 
    'tok2vec', 'tagger', 'parser', 
    'attribute_ruler', 'lemmatizer' 
]
nlp = spacy.load("en_core_web_sm", disable=pipes_to_disable)
