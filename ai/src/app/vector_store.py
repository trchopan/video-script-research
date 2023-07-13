from typing import Callable
from peewee import PostgresqlDatabase
from pgvector.psycopg2 import register_vector


class EmbeddingQueryResult:
    def __init__(self, namespace: str, document: str, chunk: int, similarity: float):
        self.namespace = namespace
        self.document = document
        self.chunk = chunk
        self.similarity = similarity


class VectorStore:
    _TABLE_NAME = "embedding"

    def __init__(self, get_db: Callable[[], PostgresqlDatabase]):
        self.get_db = get_db
        self._conn = get_db()
        self.register_vector_plugin()
        self.create_table()

    def register_vector_plugin(self):
        register_vector(self.get_db())


    def execute(self, sql, args=None):
        """
        This is a simple hack to fix the issue when psycopg2 unable to handle
        connection got disconnected by the server:
        - First check the current connection success.
        - If not close it and open new connection.
        - Then proceed to execute the query.
        """
        try:
            if self._conn is None:
                raise Exception("Not yet have connection.")

            with self._conn.cursor() as cursor:
                cursor.execute("SELECT 1 + 1;")

        except Exception as e:
            if self._conn is not None:
                self._conn.close()

            self._conn = self.get_db()
            print("Reconnected db", e)
            pass

        with self._conn.cursor() as cursor:
            cursor.execute(sql, args)
            if cursor is not None and cursor.pgresult_ptr is not None:
                return cursor.fetchall()

    def create_table(self):
        self.execute(
            f"""CREATE TABLE IF NOT EXISTS {self._TABLE_NAME} (
                    namespace VARCHAR(255),
                    document VARCHAR(255),
                    chunk INT,
                    embedding vector(1536))"""
        )

    def delete_embeddings(self, namespace: str, document: str = ""):
        query_str = f"DELETE FROM {self._TABLE_NAME} WHERE namespace = %s"
        query_args = (namespace, )
        if document != "":
            query_str += " AND document = %s"
            query_args += (document, )

        self.execute(query_str, query_args)

    def insert_embeddings(
        self, namespace: str, document: str, chunk: int, embeddings: list[float]
    ):
        self.execute(
            f"""INSERT INTO {self._TABLE_NAME} (namespace, document, chunk, embedding) VALUES (%s, %s, %s, %s)""",
            (
                namespace,
                document,
                chunk,
                embeddings,
            ),
        )

    def get_embeddings(self, namespace: str, document: str = "") -> list[list[float]]:
        query_str = f"SELECT embedding FROM {self._TABLE_NAME} WHERE namespace = %s"
        query_args = (namespace, )

        if document != "":
            query_str += " AND document = %s"
            query_args += (document, )

        return [e for (e, ) in self.execute(query_str, query_args) or []]

    def similarity_search(
        self,
        query_embedding: list[float],
        namespace: str,
        document: str = "",
        limit: int = 5,
    ):
        query_str = f"""
        SELECT namespace, document, chunk, 1 - (embedding <-> %s::vector) AS similarity FROM {self._TABLE_NAME}
        WHERE namespace = %s
        """
        query_args = (query_embedding, namespace) 
        if document != "":
            query_str += " AND document = %s"
            query_args += (document, )

        query_str += " ORDER BY embedding <-> %s::vector LIMIT %s"
        query_args += (query_embedding, limit)
        result = self.execute(query_str, query_args) or []

        return [
            EmbeddingQueryResult(namespace, document, chunk, similarity)
            for (namespace, document, chunk, similarity) in result
        ]
