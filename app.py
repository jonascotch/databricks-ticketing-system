from uuid import UUID

import psycopg
from databricks.sdk.errors import DatabricksError
from flask import Flask, abort, redirect, render_template, request, url_for

from lakebase import LakebaseConfigurationError, connect

app = Flask(__name__)
VALID_STATUSES = {"open", "in_progress", "resolved"}


def current_actor():
    actor = request.headers.get("X-Forwarded-Preferred-Username", "").strip()
    if not actor:
        abort(401)
    return actor


def load_ticket(conn, ticket_id: UUID):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT ticket_id, title, status, created_by, created_at
            FROM tickets
            WHERE ticket_id = %s
            """,
            (ticket_id,),
        )
        return cursor.fetchone()


def load_messages(conn, ticket_id: UUID):
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT message_id, message_text, author, created_at
            FROM ticket_messages
            WHERE ticket_id = %s
            ORDER BY created_at, message_id
            """,
            (ticket_id,),
        )
        return cursor.fetchall()


def ticket_detail_response(conn, ticket_id: UUID, error=None, status_code=200):
    ticket = load_ticket(conn, ticket_id)
    if ticket is None:
        abort(404)
    return (
        render_template(
            "ticket_detail.html",
            ticket=ticket,
            messages=load_messages(conn, ticket_id),
            error=error,
            statuses=sorted(VALID_STATUSES),
        ),
        status_code,
    )


@app.before_request
def require_forwarded_user():
    if request.endpoint != "healthz":
        current_actor()


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/")
def ticket_list():
    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT ticket_id, title, status, created_by, created_at
                FROM tickets
                ORDER BY created_at DESC, ticket_id
                """
            )
            tickets = cursor.fetchall()
    return render_template(
        "ticket_list.html",
        tickets=tickets,
        error=None,
        title_value="",
    )


@app.get("/tickets/<uuid:ticket_id>")
def ticket_detail(ticket_id):
    with connect() as conn:
        return ticket_detail_response(conn, ticket_id)


@app.post("/tickets")
def create_ticket():
    title = request.form.get("title", "").strip()
    if not 1 <= len(title) <= 200:
        with connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT ticket_id, title, status, created_by, created_at
                    FROM tickets
                    ORDER BY created_at DESC, ticket_id
                    """
                )
                tickets = cursor.fetchall()
        return (
            render_template(
                "ticket_list.html",
                tickets=tickets,
                error="Enter a title between 1 and 200 characters.",
                title_value=title,
            ),
            400,
        )

    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tickets (title, status, created_by)
                VALUES (%s, 'open', %s)
                RETURNING ticket_id
                """,
                (title, current_actor()),
            )
            ticket_id = cursor.fetchone()["ticket_id"]
    return redirect(url_for("ticket_detail", ticket_id=ticket_id), code=303)


@app.post("/tickets/<uuid:ticket_id>/messages")
def create_message(ticket_id):
    message_text = request.form.get("message_text", "").strip()
    with connect() as conn:
        ticket = load_ticket(conn, ticket_id)
        if ticket is None:
            abort(404)
        if not 1 <= len(message_text) <= 5000:
            return ticket_detail_response(
                conn,
                ticket_id,
                error="Enter a message between 1 and 5000 characters.",
                status_code=400,
            )
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ticket_messages (ticket_id, message_text, author)
                VALUES (%s, %s, %s)
                """,
                (ticket_id, message_text, current_actor()),
            )
    return redirect(url_for("ticket_detail", ticket_id=ticket_id), code=303)


@app.post("/tickets/<uuid:ticket_id>/status")
def update_status(ticket_id):
    status = request.form.get("status", "")
    with connect() as conn:
        ticket = load_ticket(conn, ticket_id)
        if ticket is None:
            abort(404)
        if status not in VALID_STATUSES:
            return ticket_detail_response(
                conn,
                ticket_id,
                error="Choose a valid ticket status.",
                status_code=400,
            )
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE tickets
                    SET status = %s
                    WHERE ticket_id = %s
                    """,
                    (status, ticket_id),
                )
        except psycopg.Error:
            conn.rollback()
            return ticket_detail_response(
                conn,
                ticket_id,
                error="The status update failed. The ticket below shows its latest saved state.",
                status_code=409,
            )
    return redirect(url_for("ticket_detail", ticket_id=ticket_id), code=303)


@app.errorhandler(psycopg.Error)
@app.errorhandler(DatabricksError)
@app.errorhandler(LakebaseConfigurationError)
def handle_database_error(_error):
    app.logger.error("Lakebase request failed; connection details were omitted.")
    return (
        render_template(
            "error.html",
            message="The app could not reach Lakebase. Check the app resource and database permissions, then try again.",
        ),
        503,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
