from typing import Dict, Set, List, Tuple
from inverted_index_store import get_document_vector, get_weighted_inverted_index, get_documents_vector
from gensim import corpora, models, similarities

from query_processing import calculate_query_tfidf


def create_trained_lsi_model(dataset: str):
    weighted_inverted_index = get_weighted_inverted_index(dataset)
    document_vectors = get_documents_vector(dataset)
    dictionary, corpus = create_lsi_corpus_and_dictionary(weighted_inverted_index, document_vectors)
    print("training the lsi model...")
    lsi_model = models.LsiModel(corpus=corpus, id2word=dictionary, num_topics=300)
    lsi_model.save('lsi_models/' + dataset + '_lsi_model')
    print("finished training the lsi model")
    print("creating matrix of similarity between docs...")
    doc_similarity_index = similarities.MatrixSimilarity(lsi_model[corpus])
    doc_similarity_index.save('lsi_models/' + dataset + '_index_file')
    print("finished creating matrix of similarity between docs")


def create_lsi_corpus_and_dictionary(weighted_inverted_index: Dict[str, List[Dict[str, float]]],
                                     document_vectors: Dict[str, Dict[str, float]]) -> Tuple[
    corpora.Dictionary, List[List[Tuple[int, float]]]]:
    # Create a dictionary for the LSI model
    dictionary = corpora.Dictionary()
    dictionary.token2id = {term: i for i, term in enumerate(weighted_inverted_index.keys())}

    # Create a corpus for the LSI model
    corpus = []
    for doc_id, doc_vector in document_vectors.items():
        bow = [(dictionary.token2id[term], tfidf) for term, tfidf in doc_vector.items()]
        corpus.append(bow)

    return dictionary, corpus


def compute_similarity_and_rank_documents(index: similarities.MatrixSimilarity, query_lsi: List[Tuple[int, float]],
                                          document_vectors: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    # Compute the similarity between the query and each document
    similarity = index[query_lsi]

    # Rank documents based on similarity to the query
    doc_ids = list(document_vectors.keys())
    similarity_dict = dict(zip(doc_ids, similarity))
    sorted_ranking = dict(sorted(similarity_dict.items(), key=lambda item: item[1], reverse=True)[:15])

    return sorted_ranking


def ranking(query: str, dataset: str) -> Dict[str, float]:
    weighted_inverted_index = get_weighted_inverted_index(dataset)
    document_vectors = get_documents_vector(dataset)
    query_vector = calculate_query_tfidf(query, dataset)

    # Create a dictionary for the LSI model
    dictionary = corpora.Dictionary()
    dictionary.token2id = {term: i for i, term in enumerate(weighted_inverted_index.keys())}

    # loaded from file
    lsi_model = models.LsiModel.load('lsi_models/' + dataset + '_lsi_model')

    doc_similarity_index = similarities.MatrixSimilarity.load('lsi_models/' + dataset + '_index_file')

    query_bow = []
    for term, tfidf in query_vector.items():
        if term in dictionary.token2id:
            query_bow.append((dictionary.token2id[term], tfidf))

    # Transform the query into the topic space defined by the LSI model
    query_lsi = lsi_model[query_bow]

    sorted_ranking = compute_similarity_and_rank_documents(doc_similarity_index, query_lsi, document_vectors)

    return sorted_ranking
