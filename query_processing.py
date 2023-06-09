import math
import shelve
from collections import defaultdict
from typing import Dict

import ir_datasets

from text_preprocessing import get_preprocessed_text_terms


def __get_queries_corpus(dataset_name: str) -> Dict[str, str]:
    """
    Get a corpus of queries for a given dataset name.

    Args:
        dataset_name: The name of the dataset to use. Can be either "technology" or "quora".

    Returns:
        A dictionary mapping query IDs to query content.
    """
    if dataset_name == "technology":
        forum_subset = ir_datasets.load("lotte/technology/test/forum")
        search_subset = ir_datasets.load("lotte/technology/test/search")
        queries_corpus = {}
        for query_id, query_content in forum_subset.queries_iter():
            queries_corpus[query_id] = query_content
        for query_id, query_content in search_subset.queries_iter():
            queries_corpus[str(int(query_id) + forum_subset.queries_count())] = query_content
        queries_corpus = dict(queries_corpus)
    else:  # dataset_name == "quora":
        queries_corpus = dict(ir_datasets.load("beir/quora/test").queries_iter())
    return queries_corpus


def _get_preprocessed_text_terms(text: str, dataset_name: str):
    return get_preprocessed_text_terms(text, dataset_name)


def create_unweighted_inverted_index(dataset_name) -> None:
    corpus = __get_queries_corpus(dataset_name)
    inverted_index = defaultdict(list)
    for query_id, query_content in corpus.items():
        terms = _get_preprocessed_text_terms(query_content, dataset_name)
        unique_terms = set(terms)
        for term in unique_terms:
            inverted_index[term].append(query_id)
    # storing inverted index in shelve
    # Open a "shelve" file to store the inverted index
    with shelve.open('db/' + dataset_name + '_queries_inverted_index.db') as db:
        # Store the inverted index in the "shelve" file
        db['inverted_index'] = inverted_index


def _get_unweighted_inverted_index(dataset_name) -> Dict[str, list]:
    # Inverted index
    with shelve.open('db/' + dataset_name + '_queries_inverted_index.db') as db:
        queries_inverted_index = db['inverted_index']
    return queries_inverted_index


def _calculate_tf(query: str, dataset_name: str) -> Dict[str, float]:
    """
    Calculate the term frequency (TF) for a given query.

    Args:
        query: The query to calculate the TF for.
        dataset_name:The name of the dataset

    Returns:
        A dictionary representing the TF for the given query. The keys are terms and the values are the TF values for
         each term.
    """
    tf = {}
    terms = _get_preprocessed_text_terms(query, dataset_name)
    term_count = len(terms)
    for term in terms:
        tf[term] = terms.count(term) / term_count
    return tf


def _calculate_idf(corpus: Dict[str, str], unweighted_inverted_index: Dict[str, list]) -> Dict[str, float]:
    """
    Calculate the inverse document frequency (IDF) for a given corpus and unweighted inverted index.

    Args:
        corpus: A dictionary mapping query IDs to query content.
        unweighted_inverted_index: An unweighted inverted index for the given corpus.

    Returns:
        A dictionary representing the IDF for the given corpus. The keys are terms and the values are the IDF values for
         each term.
    """
    idf = {}
    n_queries = len(corpus)
    # inverted_index = create_inverted_index(corpus)
    for term, query_ids in unweighted_inverted_index.items():
        idf[term] = math.log10(n_queries / len(query_ids))
    return idf


def calculate_query_tfidf(query: str, dataset_name: str) -> Dict[
    str, float]:
    """
    Calculate the TF-IDF for a given query and dataset name.

    Args:
        query: The query to calculate the TF-IDF for.
        dataset_name:The name of the dataset

    Returns:
        A dictionary representing the TF-IDF for the given query. The keys are terms and the values are the TF-IDF
        values for each term.
    """
    tfidf = {}
    tf = _calculate_tf(query, dataset_name)
    corpus = __get_queries_corpus(dataset_name)
    unweighted_inverted_index = _get_unweighted_inverted_index(dataset_name)
    idf = _calculate_idf(corpus, unweighted_inverted_index)
    for term in tf:
        tfidf[term] = tf[term] * idf.get(term, math.log10(
            len(corpus) / 1))  # we need a default value of idf in case of a new term in query(high idf)
    return tfidf


__all__ = [calculate_query_tfidf, create_unweighted_inverted_index]
