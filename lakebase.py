import os

import psycopg
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import DatabricksError
from psycopg.rows import dict_row


class LakebaseConfigurationError(RuntimeError):
    pass


def connect():
    auth_mode = os.environ.get("DATABASE_AUTH_MODE")
    if auth_mode not in {"local_password", "lakebase_oauth"}:
        raise LakebaseConfigurationError(
            "DATABASE_AUTH_MODE must be local_password or lakebase_oauth."
        )

    local_password_mode = auth_mode == "local_password"
    required = ["PGHOST", "PGDATABASE", "PGUSER"]
    if local_password_mode:
        required.append("PGPASSWORD")
    else:
        required.append("ENDPOINT_NAME")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise LakebaseConfigurationError(
            "Database connection configuration is incomplete."
        )

    if local_password_mode:
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
            "PGSSLMODE", "disable" if local_password_mode else "require"
        ),
        row_factory=dict_row,
    )
