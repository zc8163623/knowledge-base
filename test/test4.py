from utils.embedding_utils import generate_embeddings, get_bge_m3_ef

model = get_bge_m3_ef()


embeddings1 = model.encode_documents(["你好", "Hello World"])

print(embeddings1)

embeddings2 = generate_embeddings(["你好", "Hello World"])

print(embeddings2)