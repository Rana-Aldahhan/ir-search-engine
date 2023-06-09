
from crawler import expand_document_with_crawled_data,__extractURLs
from inverted_index_store import __get_corpus
from text_preprocessing import get_preprocessed_text_terms

corpus = __get_corpus("technology")
urls=[]
for id, content in corpus.items():
    urls+=__extractURLs(content)
print(urls)
print(f"urls length is : {len(urls)}")


# expanded_corpus = dict()
# i = 0
# for id, content in corpus.items():
#         terms_before=set(get_preprocessed_text_terms(content))
#         expanded_corpus[id] = expand_document_with_crawled_data(content)
#         terms_after=set(get_preprocessed_text_terms(expanded_corpus[id]))
#         if len(terms_after)>len(terms_before):
#             print(len(terms_before))
#             print(terms_before)
#             print(len(terms_after))
#             print(terms_after)
    # i += 1
    # if i > 2500:
    #     break
