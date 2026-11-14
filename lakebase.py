import os

import psycopg
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import DatabricksError
from psycopg.rows import dict_row


class LakebaseConfigurationError(RuntimeError):
    pass


def connect():
    local_dev = os.environ.get("APP_ENV") == "development"
    required = ["PGHOST", "PGDATABASE", "PGUSER"]
    if local_dev:
        required.append("PGPASSWORD")
    else:
        required.append("ENDPOINT_NAME")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise LakebaseConfigurationError(
            "Database connection configuration is incomplete."
        )

    if local_dev:
        password = os.environ["PGPASSWORD"]
    else:
        try:
            credential = WorkspaceClient().postgres.generate_database_credential(
                endpoint=os.environ["ENDPOINT_NAME"]
            )
        except (DatabricksError, ValueError) as error:
            raise LakebaseConfigurationError(
                "Could not obtain Lakebase database credentials."
            ) from error
        password = credential.token

    return psycopg.connect(
        host=os.environ["PGHOST"],
        port=int(os.environ.get("PGPORT", "5432")),
        dbname=os.environ["PGDATABASE"],
        user=os.environ["PGUSER"],
        password=password,
        sslmode=os.environ.get(
            "PGSSLMODE", "disable" if local_dev else "require"
        ),
        row_factory=dict_row,
    )
