# Custom features extraction functions

import spacy
from alambic_app.models.input_models import Text


def tokenizer_lemmatizer(text, stop=False):
    nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
    tokens = nlp(text)

    if not stop:
        lemma_list = [token.lemma_ for token in tokens]
    else:
        lemma_list = [token.lemma_ for token in tokens if not token.is_stop]

    return (lemma_list)


def dependency_tree(text):
    nlp = spacy.load('en_core_web_sm', disable=['ner'])

    tokens = nlp(text)

    return [(token.dep_, token.head.text, [child for child in token.children]) for token in tokens]


def masking(text):
    # mask the entities in the text
    return text
