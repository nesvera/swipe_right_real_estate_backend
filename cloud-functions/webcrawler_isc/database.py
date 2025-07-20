import os
from typing import Dict, Any, List
import psycopg2  # used inside the connector
from contextlib import contextmanager

POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_NAME = "swipe_right_real_estate"
POSTGRES_USER = "swipe_right_real_estate_dev"
POSTGRES_PASS = "3@TRmWkx+xp!w6hPyBps6HmQd1%,RAK*1=]Gt"


@contextmanager
def get_conn():
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_NAME,
        user=POSTGRES_USER,
        password=POSTGRES_PASS,
    )
    try:
        yield conn
    finally:
        conn.close()


class Search:
    """Class based in Search model from Django"""

    class QueryStatus:
        NOT_STARTED = "not_started"
        STARTED = "started"
        PARTIAL = "partial"
        FINISHED = "finished"

    id: str
    filter: str
    query_status: str
    number_real_estate_found: str


class RealEstate:
    """Class based in RealEstate model from Django"""

    class PropertyType:
        APARTMENT = "apartment"
        HOUSE = "house"
        TERRAIN = "terrain"
        OFFICE = "office"
        STORE = "store"
        WAREHOUSE = "warehouse"
        RURAL = "rural"

    class TransactionType:
        BUY = "buy"
        RENT = "rent"


def fetch_search(search_id: str) -> Dict[str, Any]:
    """
    Fetch a Search row by UUID.
    Raises ValueError if not found.
    """
    sql = """
        SELECT id
        FROM   search_filter
        WHERE  id = %s
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (search_id,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"Search {search_id} not found")
        cols = [c[0] for c in cur.description]
        return dict(zip(cols, row))


def get_filter_property_type(search_id: str) -> List[str]:
    """
    Fetch property type from filter related to a Search ID.
    Raises ValueError if not found.
    """
    sql = """
        SELECT sf.transaction_type
        FROM search_search ss
        INNER JOIN search_filter sf on ss.filter_id = sf.id
        WHERE ss.id = %s
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (search_id,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"Search {search_id} not found")
        # cols = [c[0] for c in cur.description]
        return row


def get_filter_fields(search_id: str) -> List[str]:
    """
    Fetch property type from filter related to a Search ID.
    Raises ValueError if not found.
    """
    sql = """
        SELECT sf.property_type, sf.transaction_type, sf.city, sf.neighborhood, sf.bedroom_quantity, sf.suite_quantity, sf.garage_slots_quantity, sf.min_price, sf.max_price, sf.min_area, sf.max_area
        FROM search_search ss
        INNER JOIN search_filter sf on ss.filter_id = sf.id
        WHERE ss.id = %s
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (search_id,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"Search {search_id} not found")
        cols = [c[0] for c in cur.description]

        filter_dict = {}
        for i, col in enumerate(cols):
            filter_dict[col] = row[i]

        return filter_dict

def set_search_number_real_estate_found(search_id: str, re_found: int) -> None:
    sql = """
        UPDATE search_search ss
        SET    number_real_estate_found = %s
        WHERE  ss.id = %s
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (re_found, search_id))
        if cur.rowcount == 0:
            raise ValueError(f"Search {search_id} not found")
        conn.commit()

def set_search_query_status(search_id: str, status: str) -> None:
    sql = """
        UPDATE search_search ss
        SET    query_status = %s
        WHERE  ss.id = %s
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (status, search_id))
        if cur.rowcount == 0:
            raise ValueError(f"Search {search_id} not found")
        conn.commit()
