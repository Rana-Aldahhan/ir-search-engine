# Information Retrieval System

***

A university project that uses two datasets from [ir-datasets](https://ir-datasets.com/) and build a search engine on them using Python and Flask.

## Datasets

- [**Quora**](https://ir-datasets.com/beir.html#beir/quora).

- [**Technology**](https://ir-datasets.com/lotte.html#lotte/technology/dev).
## Branches

In this project, we use branches to work on different features. Our main branch is called "main" and represents the main and stable features of our code.

The purpose of each branch is as follows:

- **main branch**: This branch represents the main stable requirements of the search engine system.


- **crawling branch**: This branch is where crawling feature is enabled to get data from links found inside the documents.


- **query_refinement branch**: This branch is where query suggestions feature is enabled to suggest queries to the user based on old queries searched.


## How to use the search engine?

you can go to the following link, add your query and get the results of the chosen dataset easily with a simple Vue web app.

www.google.com
## Services


- **Inverted Index Factory**:

Creates a documents weighted inverted index and a queries unweighted inverted index for each dataset and stores them. 


the following API runs the inverted index factory:

    - /inverted-index-factory

- **Set Global Variables**:

Gets a weighted inverted index and documents vector for both technology and quora from a "shelve" file and assign it to its global variable.


the following API runs the set global variables service:

    - /set-global-variables

- **Search**:

Performs search query and get full documnents results based on passed query, dataset and ranking type passed.

the following APIs runs the search service on our project:

        - /search?query="YOUR-QUERY"&dataset="quora/technology"?ranking-type="terms/topics"

- **Evaluation**:

The implemented evaluation metrics are **Precision**, **Recall**, **F1_score**, **MAP**, **MRR** and **Precision@10**.

the following APIs run the evaluation service on our datasets:

        - /evaluation/quora

        - /evaluation/technology/search

        - /evaluation/technology/forum

- **Text Processing**:

The implemented text processing steps are:


1. **Tokenizing**


2. **Cleaning**


3. **Filtration**


4. **Normalize dates**


5. **Normalize countries**


6. **Correction**


7. **Lowerization**


8. **Lemmatization**


the following API runs the text processing service on the provided text:

    - /text-processing/THE-TEXT-YOU-WANT-TO-PROCESS


- **Terms Ranking**:

Performs a query search and returns ranked documents based on cosine similarity calculation between the given query and related documents. 

the following API runs the Ranking service:

    - /terms-ranking?query="YOUR-QUERY"&dataset="quora/technology"

- **LSI Factory**:

Creates a LSI trained model for each dataset and stores them. 

the following API runs the set global variables service:

    - /LSI-factory

- **Topic Detection Ranking**:

Performs a query search and return ranked documents based on topic detection feature. 

the following API runs the Topic Detection Ranking service:

    - /topic-detection-ranking?query="YOUR-QUERY"&dataset="quora/technology"

- **Query TF-IDF**:

Calculates the TF-IDF for a given query and dataset name.

the following API runs the Query TF-IDF service:

    - /query-tf-idf?query="YOUR-QUERY"&dataset="quora/technology"

- **Initialize Queries Database** (query_refinement Branch):

Initializes queries database to store performed queries in it.

the following API runs the Initialize Queries Database service:

    - /initialize-queries-db

- **Set Query Refinement Global Variables** (query_refinement Branch):

Gets queries for both technology and quora from a "shelve" file and assign it to its global variable.

the following API runs the Set Query Refinement Global Variables service:

    - /set-query-refinement-global-variables

- **Get Ranked Query Suggestions** (query_refinement Branch):

Performs a query suggestions search and returns ranked suggestions to the given query and dataset.

the following API runs the Get Ranked Query Suggestions service:

    - /suggestions?query="YOUR-QUERY"&dataset="quora/technology"

- **Expand Document With Crawled Data** (crawler Branch):

Takes a document content string as input and returns an updated document content string with crawled data from any URLs present in the input document content.

*this service is used inside inverted index store for this branch*

the following API runs the Expand Document With Crawled Data service:

    - /expand-document-with-crawled-data?doc_content="CONTENT"


## Students

- [**Ahmad Sultan**](https://github.com/ahmadsultan39)
- [**Hamza Ammar**](https://github.com/HamzaSamirAmmar)
- [**Rama Alranneh**](https://github.com/Ramrosh)
- [**Rana Aldahan**](https://github.com/Rana-Aldahhan)