from playhouse.pool import PooledPostgresqlExtDatabase


class EmbeddingQueryResult:
    def __init__(self, namespace: str, document: str, chunk: int, similarity: float):
        self.namespace = namespace
        self.document = document
        self.chunk = chunk
        self.similarity = similarity


class EmbeddingStore:
    _TABLE_NAME = "embedding"

    def __init__(self, db: PooledPostgresqlExtDatabase):
        self.db = db
        pass

    def create_table(self):
        self.db.execute_sql(
            f"""CREATE TABLE IF NOT EXISTS {self._TABLE_NAME} (
                    namespace VARCHAR(255),
                    document VARCHAR(255),
                    chunk INT,
                    embedding vector(1536))"""
        )

    def delete_embeddings(self, namespace: str, document: str = ""):
        _prefix = f"DELETE FROM {self._TABLE_NAME} "
        if document == "":
            self.db.execute_sql(
                f"""{_prefix} WHERE namespace = %s""",
                (namespace,),
            )
        else:
            self.db.execute_sql(
                f"""{_prefix} WHERE namespace = %s AND document = %s""",
                (namespace, document),
            )

    def insert_embeddings(
        self, namespace: str, document: str, chunk: int, embeddings: list[float]
    ):
        self.db.execute_sql(
            f"""INSERT INTO {self._TABLE_NAME} (namespace, document, chunk, embedding) VALUES (%s, %s, %s, %s)""",
            (
                namespace,
                document,
                chunk,
                embeddings,
            ),
        )

    def get_embeddings(self, namespace: str, document: str = ""):
        query_str = f"SELECT embedding FROM {self._TABLE_NAME} WHERE namespace = %s"
        query_args = (namespace, )

        if document != "":
            query_str += " AND document = %s"
            query_args += (document, )

        cur = self.db.execute_sql(query_str, query_args)

        return cur.fetchall()

    def similarity_search(
        self,
        query_embedding: list[float],
        namespace: str,
        document: str = "",
        limit: int = 5,
    ):
        _prefix = f"""
        SELECT namespace, document, chunk, 1 - (embedding <-> %s::vector) AS similarity FROM {self._TABLE_NAME}
        """
        _suffix = "ORDER BY embedding <-> %s::vector LIMIT %s"
        cur = None
        if document == "":
            cur = self.db.execute_sql(
                f"{_prefix} WHERE namespace = %s AND document = %s {_suffix}",
                (query_embedding, namespace, query_embedding, limit),
            )
        else:
            cur = self.db.execute_sql(
                f"{_prefix} WHERE namespace = %s AND document = %s {_suffix}",
                (query_embedding, namespace, document, query_embedding, limit),
            )

        return [
            EmbeddingQueryResult(namespace, document, chunk, similarity)
            for (namespace, document, chunk, similarity) in cur.fetchall()
        ]
