import os

import psycopg
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import DatabricksError
from psycopg.rows import dict_row


class LakebaseConfigurationError(RuntimeError):
    pass


def connect():
    required = ("PGHOST", "PGDATABASE", "PGUSER", "ENDPOINT_NAME")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise LakebaseConfigurationError(
            "Lakebase app resource configuration is incomplete."
        )

    try:
        credential = WorkspaceClient().postgres.generate_database_credential(
            endpoint=os.environ["ENDPOINT_NAME"]
        )
    except (DatabricksError, ValueError) as error:
        raise LakebaseConfigurationError(
            "Could not obtain Lakebase database credentials."
        ) from error

    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=int(os.environ.get("PGPORT", "5432")),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=credential.token,
        sslmode=os.environ.get("PGSSLMODE", "require"),
        row_factory=dict_row,
    )
