# Information Retrieval System

***

A university project that uses two datasets from [ir-datasets](https://ir-datasets.com/) and build a search engine on them using Python and Flask.

## Datasets

- [**Quora**](https://ir-datasets.com/beir.html#beir/quora).

- [**Technology**](https://ir-datasets.com/lotte.html#lotte/technology/dev).
## Branches

In this project, we use branches to work on different features. Our main branch is called "master" and represents the main and stable features of our code.

The purpose of each branch is as follows:

- [**master branch**](https://github.com/Rana-Aldahhan/ir-search-engine): This branch represents the main stable requirements of the search engine system.


- [**crawling branch**](https://github.com/Rana-Aldahhan/ir-search-engine/tree/crawling): This branch is where crawling feature is enabled to get data from links found inside the documents.


- [**query_refinement branch**](https://github.com/Rana-Aldahhan/ir-search-engine/tree/query_refinement): This branch is where query suggestions feature is enabled to suggest queries to the user based on old queries searched.


- [**topic_detection branch**](https://github.com/Rana-Aldahhan/ir-search-engine/tree/topic_detection): This branch is where topic detection feature is enabled to rank documents based on query topic.


## How to use the search engine?

After running your project locally you can perform your query and get the results of the chosen dataset easily with a [simple Vue web app](https://gitlab.com/rana-aldahhan/ir-search-engine).


## How to run the project?

Install required packages. 

Run inverted_index_factory.py file for the first time to set the database on your device.

Running *query_refinement* branch for the first time requires running queries_db_initializer.py file first.

Running *topic_detection* branch for the first time requires running LSI_model_factory.py file first.

Running *crawler* branch for requires running inverted_index_factory.py file first.

Run app.py file then you can access any service by you localhost:YOUR-PORT/SERVICE-ENDPOINT


## Services

*note that service might behave differently based on the selected branch*

- **Search**:

Performs search query and get full documnents results based on passed query and dataset passed.

the following APIs runs the search service on our project:

    - GET: /search?query="YOUR-QUERY"&dataset="quora/technology"

- **Text Processing**:

The implemented text processing steps are:


1. **Tokenizing**


2. **Lowerization**


3. **Cleaning**


3. **Filtration**


5. **Normalize dates**


6. **Normalize countries**


7. **Stemming**


the following API runs the text processing service on the provided text and dataset:

    - GET: /process-text?text="YOUR-TEXT"&dataset="quora/technology"


- **Ranking**:

Performs a query search and returns ranked documents. 

the following API runs the Ranking service:

    - GET: /ranking?query="YOUR-QUERY"&dataset="quora/technology"

- **Get Inverted Index**:

Gets the weighted inverted index for the given dataset. 

the following API runs the Get Inverted Index service:

    - GET: /inverted-index?dataset="quora/technology"

- **Create Inverted Index**:

Creates the weighted inverted index for the given dataset. 

the following API runs the Create Inverted Index service:

    - POST: /inverted-index

        body : {dataset : "quora/technology"}

- **Get Document Vector**:

Gets the document vector for the given document and dataset. 

the following API runs the Get Document Vector service:

    - GET: /document-vector?dataset="quora/technology"&doc_id="DOCUMENT-ID"

- **Get Documents Vector**:

Gets the documents vector for the given dataset. 

the following API runs the Get Documents Vector service:

    - GET: /documents-vector?dataset="quora/technology"

- **Get Query TF-IDF**:

Calculates the query TF-Idf for the given query and dataset. 

the following API runs the Get Documents Vector service:

    - GET: /query-tfidf?query="YOUR-QUERY"&dataset="quora/technology"

- **Query Suggestions** (query_refinement Branch):

Performs a query suggestions search and returns ranked suggestions to the given query and dataset.

the following API runs the Query Suggestions service:

    - GET: /suggestions?query="YOUR-QUERY"&dataset="quora/technology"

- ## Evaluation:

The implemented evaluation metrics are **Precision**, **Recall**, **F1_score**, **MAP**, **MRR** and **Precision@10**.

to run the evaluation just go to evaluation.py file and run it.


## Students

- [**Ahmad Sultan**](https://github.com/ahmadsultan39)
- [**Hamza Ammar**](https://github.com/HamzaSamirAmmar)
- [**Rama Alranneh**](https://github.com/Ramrosh)
- [**Rana Aldahan**](https://github.com/Rana-Aldahhan)
