import shelve
from collections import Counter

import ir_datasets
from nltk.corpus import words
from spellchecker import SpellChecker

_technology_queries = set()  # empty set
_quora_queries = set()  # empty set


def initialize_queries_db() -> None:
    with shelve.open('C:/Users/Hamza/Desktop/ir-search-engine/db/' + "technology" + '_queries.db') as db:
        db['queries'] = set()

    with shelve.open('C:/Users/Hamza/Desktop/ir-search-engine/db/' + "quora" + '_queries.db') as db:
        db['queries'] = set()


def index_query(query: str, dataset_name: str) -> None:
    global _technology_queries
    global _quora_queries

    if dataset_name == 'technology':
        _technology_queries.add(query)
    else:
        _quora_queries.add(query)

    with shelve.open('C:/Users/Hamza/Desktop/ir-search-engine/db/' + dataset_name + '_queries.db') as db:
        queries = db['queries']
        queries.add(query)
        db['queries'] = queries


def set_query_refinement_global_variables() -> None:
    global _technology_queries
    global _quora_queries

    ############## Technology ##############

    forum_generic_queries = set(ir_datasets.load("lotte/technology/test/forum").queries_iter())
    search_generic_queries = set(ir_datasets.load("lotte/technology/test/search").queries_iter())

    forum_queries = set(query.text for query in forum_generic_queries)
    search_queries = set(query.text for query in search_generic_queries)

    with shelve.open('C:/Users/Hamza/Desktop/ir-search-engine/db/' + "technology" + '_queries.db') as db:
        stored_technology_queries = db['queries']

    _technology_queries = forum_queries.union(search_queries).union(stored_technology_queries)

    ############## Quora ##############

    quora_generic_queries = set(ir_datasets.load("beir/quora/test").queries_iter())

    with shelve.open('C:/Users/Hamza/Desktop/ir-search-engine/db/' + "quora" + '_queries.db') as db:
        stored_quora_queries = db['queries']

    _quora_queries = set(query.text for query in quora_generic_queries).union(stored_quora_queries)


def _get_query_suggestions(query: str, dataset_name: str) -> list:
    global _technology_queries
    global _quora_queries

    if dataset_name == 'technology':
        queries = _technology_queries
    else:
        queries = _quora_queries

    suggestions = []
    query_terms = query.lower().split()
    query_freq = Counter(query_terms)

    for suggest_query in queries:
        suggest_query_terms = suggest_query.lower().split()
        if set(query_terms).intersection(set(suggest_query_terms)):
            freq = sum([query_freq[term] for term in set(query_terms) & set(suggest_query_terms)])
            suggestions.append((suggest_query, freq))

    return suggestions


def _get_ranked_suggestion(suggestions: list) -> list:
    ranked_suggestions = sorted(suggestions, key=lambda x: -x[1])
    return [suggestion[0] for suggestion in ranked_suggestions]


def _suggest_corrected_query(text: str):
    spell = SpellChecker()

    word_set = set(words.words())

    # Create a list to store the corrected tokens
    corrected_tokens = []

    # Spell check each token
    for token in text.split():
        if token in word_set:
            corrected_tokens.append(token)
        else:
            suggestions = spell.candidates(token)
            if suggestions:
                corrected_tokens.append(spell.correction(token))
            else:
                corrected_tokens.append(token)

    return ' '.join(corrected_tokens)


def get_ranked_query_suggestions(query: str, dataset_name: str):
    corrected_query = _suggest_corrected_query(query)
    suggestions = _get_query_suggestions(corrected_query, dataset_name)
    ranked_suggestions = _get_ranked_suggestion(suggestions)
    ranked_suggestions.insert(0, corrected_query)
    return ranked_suggestions[:15]


__all__ = ['set_query_refinement_global_variables', 'get_ranked_query_suggestions', 'initialize_queries_db',
           'index_query']
