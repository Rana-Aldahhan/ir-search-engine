from inverted_index_store import create_weighted_inverted_index
from query_processing import create_unweighted_inverted_index as create_queries_unweighted_inverted_index

# creating documents inverted indexes
create_weighted_inverted_index("technology")
print("finished creating technology index")

create_weighted_inverted_index("quora")
print("finished creating quora index")

# creating queries inverted indexes
create_queries_unweighted_inverted_index("technology")
print("finished creating technology queries index")
create_queries_unweighted_inverted_index("quora")
print("finished creating quora queries index")




