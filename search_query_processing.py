import time

import ir_datasets

from matching_and_ranking import ranking



def _get_docs_store(dataset: str):
    if dataset == "technology":
        return ir_datasets.load("lotte/technology/test").docs_store()
    else:
        return ir_datasets.load("beir/quora/test").docs_store()


def _get_full_docs_content(docs: list, dataset: str):
    docs_store = _get_docs_store(dataset)
    return docs_store.get_many(docs)


def _get_ordered_full_docs(docs: list, full_docs: dict):
    return {doc_id: full_docs[doc_id] for doc_id in docs if doc_id in full_docs}


def _get_sliced_results_template(ordered_full_docs: dict) -> dict:
    total_result = [{'id': doc_id, 'text': doc.text} for doc_id, doc in ordered_full_docs.items()]
    sliced_result = total_result[:100]
    return {"results": sliced_result, "result_count": len(total_result)}


def ranking_call(retrieving_relevant_on: str, query: str, dataset: str) -> list:
    return list(ranking(query, dataset).keys())


def get_search_result(query: str, dataset: str, retrieving_relevant_on: str) -> dict:
    start_time = time.time()
    docs = ranking_call(retrieving_relevant_on, query, dataset)
    full_docs = _get_full_docs_content(docs, dataset)
    ordered_full_docs = _get_ordered_full_docs(docs, full_docs)
    response = _get_sliced_results_template(ordered_full_docs)
    end_time = time.time()
    # append elapsed time to response
    response["elapsed_time"] = end_time - start_time
    return response


__all__ = ["get_search_result"]
