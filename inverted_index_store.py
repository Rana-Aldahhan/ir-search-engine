import math
import shelve
from collections import defaultdict
from typing import Dict

import ir_datasets

from text_preprocessing import get_preprocessed_text_terms

# Assign indexes and vectors to global variables, and initialize them at the runtime using [set_global_variables],
# for reducing database access time
_technology_weighted_inverted_index = None
_quora_weighted_inverted_index = None
_technology_documents_vector = None
_quora_documents_vector = None


def set_inverted_index_store_global_variables() -> None:
    """
    Get a weighted inverted index for both technology and quora from a "shelve" file and assign it to its global variable
    Get a documents vector for both technology and quora from a "shelve" file and assign it to its global variable

    Args:
        No args
    Returns:
        None
    """
    global _technology_weighted_inverted_index
    global _quora_weighted_inverted_index
    global _technology_documents_vector
    global _quora_documents_vector

    # Inverted index
    with shelve.open('db/' + "technology" + '_inverted_index.db') as db:
        _technology_weighted_inverted_index = db['inverted_index']
    with shelve.open('db/' + "quora" + '_inverted_index.db') as db:
        _quora_weighted_inverted_index = db['inverted_index']

    # Document Vector
    with shelve.open('db/' + "technology" + '_documents_vector.db') as db:
        _technology_documents_vector = db["documents_vector"]
    with shelve.open('db/' + "quora" + '_documents_vector.db') as db:
        _quora_documents_vector = db["documents_vector"]


def __get_corpus(dataset_name: str) -> Dict[str, str]:
    """
    Get a corpus of documents for a given dataset name.

    Args:
        dataset_name: The name of the dataset to use. Can be either "technology" or "quora".

    Returns:
        A dictionary mapping document IDs to document content.
    """
    if dataset_name == "technology":
        random_corpus = dict(ir_datasets.load("lotte/technology/test").docs_iter()[:100000])
        random_corpus_ids = set(random_corpus.keys())

        forum_qrels = list(ir_datasets.load("lotte/technology/test/forum").qrels_iter())
        search_qrels = list(ir_datasets.load("lotte/technology/test/search").qrels_iter())

        forum_qrels_docs_ids = set(qrel.doc_id for qrel in forum_qrels)
        search_qrels_docs_ids = set(qrel.doc_id for qrel in search_qrels)

        qrels_docs_ids = forum_qrels_docs_ids.union(search_qrels_docs_ids)

        docs_ids = random_corpus_ids.union(qrels_docs_ids)

        docs_store = ir_datasets.load("lotte/technology/test").docs_store()

        mapped_docs = dict(docs_store.get_many(docs_ids))

        corpus = {doc_id: doc.text for doc_id, doc in mapped_docs.items()}

    else:  # dataset_name == "quora":
        random_corpus = dict(ir_datasets.load("beir/quora/test").docs_iter()[:100000])
        random_corpus_ids = set(random_corpus.keys())

        qrels = list(ir_datasets.load("beir/quora/test").qrels_iter())
        qrels_docs_ids = set(qrel.doc_id for qrel in qrels)

        docs_ids = random_corpus_ids.union(qrels_docs_ids)

        docs_store = ir_datasets.load("beir/quora/test").docs_store()

        mapped_docs = dict(docs_store.get_many(docs_ids))

        corpus = {doc_id: doc.text for doc_id, doc in mapped_docs.items()}

    return corpus


def _get_preprocessed_text_terms(text: str, dataset_name: str):
    return get_preprocessed_text_terms(text, dataset_name)


def _create_unweighted_inverted_index(corpus: Dict[str, str], dataset_name: str) -> Dict[str, list]:
    """
    Create an unweighted inverted index from a corpus of documents.

    Args:
        corpus: A dictionary mapping document IDs to document content.
    Returns:
        A dictionary representing the unweighted inverted index. The keys are terms and the values are lists of document
         IDs containing the term.
    """
    inverted_index = defaultdict(list)
    for doc_id, doc_content in corpus.items():
        terms = _get_preprocessed_text_terms(doc_content, dataset_name)
        unique_terms = set(terms)
        for term in unique_terms:
            inverted_index[term].append(doc_id)
    return dict(inverted_index)


def _calculate_tf(document: str, dataset_name: str) -> Dict[str, float]:
    """
    Calculate the term frequency (TF) for a given document.

    Args:
        document: The document to calculate the TF for.
        dataset_name: The name of the dataset to use. Can be either "technology" or "quora".

    Returns:
        A dictionary representing the TF for the given document. The keys are terms and the values are the TF values for
         each term.
    """
    tf = {}
    terms = _get_preprocessed_text_terms(document, dataset_name)
    term_count = len(terms)
    for term in terms:
        tf[term] = terms.count(term) / term_count
    return tf


def _calculate_idf(corpus: Dict[str, str], unweighted_inverted_index: Dict[str, list]) -> Dict[str, float]:
    """
    Calculate the inverse document frequency (IDF) for a given corpus and unweighted inverted index.

    Args:
        corpus: A dictionary mapping document IDs to document content.
        unweighted_inverted_index: An unweighted inverted index for the given corpus.

    Returns:
        A dictionary representing the IDF for the given corpus. The keys are terms and the values are the IDF values for
         each term.
    """
    idf = {}
    n_docs = len(corpus)
    # inverted_index = create_inverted_index(corpus)
    for term, doc_ids in unweighted_inverted_index.items():
        idf[term] = math.log10(n_docs / len(doc_ids))
    return idf


def _calculate_tfidf(document: str, corpus: Dict[str, str], unweighted_inverted_index: Dict[str, list],
                     dataset_name: str) -> Dict[
    str, float]:
    """
    Calculate the TF-IDF for a given document and corpus.

    Args:
        document: The document to calculate the TF-IDF for.
        corpus: A dictionary mapping document IDs to document content.
        unweighted_inverted_index: An unweighted inverted index for the given corpus.
        dataset_name: The name of the dataset to use. Can be either "technology" or "quora".

    Returns:
        A dictionary representing the TF-IDF for the given document. The keys are terms and the values are the TF-IDF
        values for each term.
    """
    tfidf = {}
    tf = _calculate_tf(document, dataset_name)
    idf = _calculate_idf(corpus, unweighted_inverted_index)
    for term in tf:
        tfidf[term] = tf[term] * idf[term]
    return tfidf


def _create_docs_vectors(corpus: Dict[str, str], dataset_name: str) -> Dict[str, Dict[str, float]]:
    """
    Create a dictionary of TF-IDF vectors for each document in the corpus.

    Args:
        corpus: A dictionary mapping document IDs to document content.
        dataset_name: The name of the dataset to use. Can be either "technology" or "quora".

    Returns:
        A dictionary where the keys are document IDs and the values are dictionaries representing the TF-IDF vector for
        each document. The keys of the inner dictionaries are terms and the values are the TF-IDF weights for each term.
    """
    unweighted_inverted_index = _create_unweighted_inverted_index(corpus, dataset_name)
    vectors = {}
    for doc_id, doc_content in corpus.items():
        vectors[doc_id] = _calculate_tfidf(doc_content, corpus, unweighted_inverted_index, dataset_name)
    with shelve.open('db/' + dataset_name + '_documents_vector.db') as db:
        # Access the inverted index like a normal dictionary
        db["documents_vector"] = vectors
    return vectors


def create_weighted_inverted_index(dataset_name: str) -> None:
    """
    Create a weighted inverted index from a corpus of documents.

    Args:
        dataset_name: The name of the dataset to use. Can be either "technology" or "quora".

    Returns:
        None
    """
    corpus = __get_corpus(dataset_name)
    weighted_inverted_index = defaultdict(list)
    vectors = _create_docs_vectors(corpus, dataset_name)
    for doc_id, doc_weighted_terms in vectors.items():
        for term, weight in doc_weighted_terms.items():
            weighted_inverted_index[term].append({doc_id: weight})
    # storing inverted index in shelve
    # Open a "shelve" file to store the inverted index
    with shelve.open('db/' + dataset_name + '_inverted_index.db') as db:
        # Store the inverted index in the "shelve" file
        db['inverted_index'] = weighted_inverted_index


def get_weighted_inverted_index(dataset_name: str) -> Dict[str, list]:
    """
    Get a weighted inverted index from a "shelve" file.

    Args:
        dataset_name: The name of the dataset to use. Can be either "technology" or "quora".

    Returns:
        A dictionary representing the weighted inverted index. The keys are terms and the values are lists of
        dictionaries representing the documents containing the term. The keys of the inner dictionaries are document IDs
        and the values are the TF-IDF weights for each term in each document.
    Examples of use:
        index=get_weighted_inverted_index("technology")\n
        print(index["You"])
    """
    return globals()["_" + dataset_name + "_weighted_inverted_index"]


def get_document_vector(dataset_name: str, doc_id: str) -> Dict[str, float]:
    """
    Get the TF-IDF vector for a specified document in a given dataset.

    Args:
        dataset_name (str): The name of the dataset to use. Can be either "technology" or "quora".
        doc_id (str): The ID of the document to get the vector for.
        
    Returns:
        A dictionary representing the TF-IDF vector for the specified document. The keys are terms and the values are
        the TF-IDF values for each term.
    """
    return globals()["_" + dataset_name + "_documents_vector"][doc_id]


def get_documents_vector(dataset_name: str) -> Dict[str, Dict[str, float]]:
    """
    Get the TF-IDF vector for a documents in a given dataset.

    Args:
        dataset_name (str): The name of the dataset to use. Can be either "technology" or "quora".

    Returns:
        A dictionary representing the TF-IDF vector for documents. The keys are document ids and the values are lists of
        dictionaries representing the terms in the document. The keys of the inner dictionaries are terms
        and the values are the TF-IDF weights for each term in each document.
    """
    return globals()["_" + dataset_name + "_documents_vector"]


__all__ = ['create_weighted_inverted_index', 'get_weighted_inverted_index', 'get_document_vector',
           'set_inverted_index_store_global_variables', 'get_documents_vector']
