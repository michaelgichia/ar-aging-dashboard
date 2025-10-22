from typing import Generator
from dagster import Any, ConfigurableResource, InitResourceContext
from pydantic import PrivateAttr
from sqlalchemy import create_engine, Engine
from sqlalchemy.engine import Connection
from contextlib import contextmanager


class DatabaseResource(ConfigurableResource):
    """A configurable resource for connecting to PostgreSQL via SQLAlchemy."""

    user: str
    password: str
    host: str
    port: int
    database: str

    _engine: Engine | None = PrivateAttr(default=None)

    def _get_uri(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def setup_for_execution(self, context: InitResourceContext) -> None:
        self._engine = create_engine(self._get_uri())

    def teardown_after_execution(self, context: InitResourceContext) -> None:
        if self._engine is not None:
            self._engine.dispose()

    @contextmanager
    def get_connection(self) -> Generator[Connection, Any, Any]:
        """
        Provides a raw SQLAlchemy connection.
        You must manage transactions manually if you use this method.
        """
        if self._engine is None:
            raise Exception("SQLAlchemy Engine not initialized.")

        conn = self._engine.connect()
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def get_transaction(self) -> Generator[Connection, Any, Any]:
        """
        Provides a SQLAlchemy connection wrapped in a transaction context.
        Automatically commits on success and rolls back on failure.
        Equivalent to `with engine.begin() as conn: ...`
        """
        if self._engine is None:
            raise Exception("SQLAlchemy Engine not initialized.")

        with self._engine.begin() as conn:
            yield conn
