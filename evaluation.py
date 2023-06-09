from typing import Dict

from matching_and_ranking import ranking
import ir_datasets


def __get_queries_corpus(dataset_name: str) -> Dict[str, str]:
    if dataset_name == "technology":
        queries_corpus = dict(ir_datasets.load("lotte/technology/test/search").queries_iter())
    else:
        queries_corpus = dict(ir_datasets.load("beir/quora/test").queries_iter()[:3000])
    return queries_corpus


def compute_metrics(ranked_docs, qrels, k=None):
    metrics = {}
    ap_sum = 0
    mrr_sum = 0
    p10_sum = 0
    overall_precision = 0
    overall_recall = 0
    overall_f1_score = 0
    for query_id in ranked_docs.keys():
        ranked_list = ranked_docs[query_id]
        relevant_docs = [doc_id for doc_id, score in qrels[query_id].items() if score > 0]
        if k is not None:
            ranked_list = {key: value for key, value in list(ranked_list.items())[:k]}
        tp = len(set(ranked_list).intersection(set(relevant_docs)))
        precision = tp / len(ranked_list) if len(ranked_list) > 0 else 0
        recall = tp / len(relevant_docs) if len(relevant_docs) > 0 else 0
        f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        overall_precision += precision
        overall_recall += recall
        overall_f1_score += f1_score
        ap = 0
        relevant_docs_seen = set()
        for i, doc_id in enumerate(ranked_list):
            if doc_id in relevant_docs and doc_id not in relevant_docs_seen:
                ap += (len(relevant_docs_seen) + 1) / (i + 1)
                relevant_docs_seen.add(doc_id)
                if len(relevant_docs_seen) == 1:
                    mrr_sum += 1 / (i + 1)
                if len(relevant_docs_seen) == len(relevant_docs):
                    break
        ap /= len(relevant_docs) if len(relevant_docs) > 0 else 1
        ap_sum += ap
        p10 = len(set(list(tuple(ranked_list))[:10]).intersection(set(relevant_docs)))
        p10_sum += p10 / 10
        metrics[query_id] = {
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'ap': ap,
            'p10': p10
        }
    overall_precision = overall_precision / len(ranked_docs)
    overall_recall = overall_recall / len(ranked_docs)
    overall_f1_score = overall_f1_score / len(ranked_docs)
    overall_ap = ap_sum / len(ranked_docs)
    overall_mrr = mrr_sum / len(ranked_docs)
    overall_p10 = p10_sum / len(ranked_docs)
    metrics['overall'] = {
        'precision': overall_precision,
        'recall': overall_recall,
        'f1_score': overall_f1_score,
        'map': overall_ap,
        'mrr': overall_mrr,
        'p10': overall_p10
    }
    # return metrics
    return metrics["overall"]


def _get_qrels(dataset: str):
    qrels = list(ir_datasets.load(dataset).qrels_iter())
    return qrels


def evaluate(dataset: str, dataset_name: str, k=None):
    qrelsMap = dict()
    qrels = _get_qrels(dataset)
    # i = 0
    for qrel in qrels:
        if qrel.query_id in qrelsMap:
            qrelsMap[qrel.query_id].update({qrel.doc_id: qrel.relevance})
        else:
            qrelsMap[qrel.query_id] = {qrel.doc_id: qrel.relevance}
            # i = i + 1
            # if i == 600:
            #     break
    ranked_docs = {}
    queries = dict(ir_datasets.load(dataset).queries_iter())
    i = 0
    for query_id in queries.keys():
        results = ranking(queries[query_id], dataset_name)
        ranked_docs[query_id] = results
        print(f"currently ranking {query_id}")
        i = i + 1
        if i == 3000:
            break
    evaluation = compute_metrics(ranked_docs, qrelsMap, k)
    print(evaluation)


from inverted_index_store import set_inverted_index_store_global_variables
set_inverted_index_store_global_variables()
print("technology forum evaluation")
#evaluate("lotte/technology/test/forum", "technology")
print("technology search evaluation")
#evaluate("lotte/technology/test/search", "technology")
print("quora evaluation")
evaluate("beir/quora/test", "quora")

#evaluation metrics with k=10, docs index on: docs of qrels + 500 doc
# quora {'precision': 0.13150972645896886, 'recall': 0.8388516746411483, 'f1_score': 0.22737333563894174}
# lotte {'precision': 0.11789438277833837, 'recall': 0.3427872860635697, 'f1_score': 0.17544737830058818}


#evaluation metrics with k=non, docs index on: docs of qrels + 500 doc
# quora {'precision': 0.000328158462073879, 'recall': 0.9949601275917065, 'f1_score': 0.0006561005286013829}
# lotte {'precision': 0.0010802808342276413, 'recall': 0.8171149144254278, 'f1_score': 0.002157709032097697}