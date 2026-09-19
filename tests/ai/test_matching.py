from ai.embeddings.vector_utils import cosine_similarity
def test_vector_similarity(): assert cosine_similarity([1, 0], [1, 0]) == 1
