import threading

from flask import Flask, request
from flask_cors import CORS, cross_origin

from inverted_index_store import set_inverted_index_store_global_variables, get_weighted_inverted_index, \
    create_weighted_inverted_index, get_document_vector, get_documents_vector
from matching_and_ranking import ranking
from query_processing import calculate_query_tfidf
from query_refinement import set_query_refinement_global_variables, get_ranked_query_suggestions, index_query
from search_query_processing import get_search_result
from text_preprocessing import get_preprocessed_text_terms

app = Flask(__name__)
cors = CORS(app)


@app.route('/search', methods=['GET'])
@cross_origin()
def search():
    query = request.args.get('query')
    dataset = request.args.get('dataset')
    retrieving_relevant_on = "terms"  # "terms" or "topics"
    index_query(query, dataset)
    return get_search_result(query, dataset, retrieving_relevant_on)


@app.route('/suggestions', methods=['GET'])
@cross_origin()
def get_suggestions():
    query = request.args.get('query')
    dataset = request.args.get('dataset')
    return get_ranked_query_suggestions(query, dataset)


@app.route('/process-text', methods=['GET'])
@cross_origin()
def get_processed_text():
    text = request.args.get('text')
    dataset = request.args.get('dataset')
    return get_preprocessed_text_terms(text, dataset)


@app.route('/inverted-index', methods=['GET'])
@cross_origin()
def get_inverted_index():
    dataset = request.args.get('dataset')
    return get_weighted_inverted_index(dataset)


@app.route('/inverted-index', methods=['POST'])
@cross_origin()
def create_inverted_index():
    dataset = request.get_json()['dataset']
    thread = threading.Thread(target=create_weighted_inverted_index(dataset))
    thread.start()
    return "Start creating..."


@app.route('/document-vector', methods=['GET'])
@cross_origin()
def document_vector():
    dataset = request.args.get('dataset')
    doc_id = request.args.get('doc_id')
    return get_document_vector(dataset, doc_id)


@app.route('/documents-vector', methods=['GET'])
@cross_origin()
def documents_vector():
    dataset = request.args.get('dataset')
    return get_documents_vector(dataset)


@app.route('/query-tfidf', methods=['GET'])
@cross_origin()
def get_query_tfidf():
    dataset = request.args.get('dataset')
    query = request.args.get('query')
    return calculate_query_tfidf(query, dataset)


@app.route('/ranking', methods=['GET'])
@cross_origin()
def get_ranking():
    dataset = request.args.get('dataset')
    query = request.args.get('query')
    return ranking(query, dataset)


if __name__ == "__main__":
    set_inverted_index_store_global_variables()
    set_query_refinement_global_variables()
    app.run(debug=True)
