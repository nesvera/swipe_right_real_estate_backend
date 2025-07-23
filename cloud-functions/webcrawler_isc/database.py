import os
from typing import Dict, Any, List
import psycopg2  # used inside the connector
from contextlib import contextmanager
from uuid import uuid4
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_NAME = os.environ.get("POSTGRES_NAME", "")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "")
POSTGRES_PASS = os.environ.get("POSTGRES_PASS", "")

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


class ObjectNotFoundError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(f"{errors}")


class GenericInsertError(Exception):
    pass


def fetch_search(search_id: str) -> Dict[str, Any]:
    """
    Fetch a Search row by UUID.
    Raises ObjectNotFoundError if not found.
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
            raise ObjectNotFoundError(f"Search {search_id} not found")
        cols = [c[0] for c in cur.description]
        return dict(zip(cols, row))


def get_filter_property_type(search_id: str) -> List[str]:
    """
    Fetch property type from filter related to a Search ID.
    Raises ObjectNotFoundError if not found.
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
            raise ObjectNotFoundError(f"Search {search_id} not found")
        return row


def get_filter_fields(search_id: str) -> Dict[str, Any]:
    """
    Fetch property type from filter related to a Search ID.
    Raises ObjectNotFoundError if not found.
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
            raise ObjectNotFoundError(f"Search {search_id} not found")
        cols = [c[0] for c in cur.description]

        filter_dict = {}
        for i, col in enumerate(cols):
            filter_dict[col] = row[i]

        return filter_dict


def get_real_estate_by_reference_code(reference_code: str) -> Dict[str, Any]:
    """
    Fetch real estate object based in the reference code.
    Raises ObjectNotFoundError if not found.
    """
    sql = """
        SELECT *
        FROM real_estate_realestate rer
        WHERE rer.reference_code = %s
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (reference_code,))
        row = cur.fetchone()
        if row is None:
            raise ObjectNotFoundError(f"Search {reference_code} not found")
        cols = [c[0] for c in cur.description]

        real_estate_dict = {}
        for i, col in enumerate(cols):
            real_estate_dict[col] = row[i]

        return real_estate_dict


def insert_real_estate(
    reference_code: str,
    property_type: str,
    transaction_type: str,
    city: str,
    neighborhood: str,
    bedroom_quantity: str,
    suite_quantity: str,
    bathroom_quantity: str,
    garage_slots_quantity: str,
    price: str,
    area: str,
    area_total: str,
    available: str,
    agency: str,
    cond_price: str,
    description: str,
    thumb_url: str,
    url: str,
):
    real_estate_id = str(uuid4())
    payload = {
        "id": real_estate_id,
        "reference_code": reference_code,
        "property_type": property_type,
        "transaction_type": transaction_type,
        "city": city,
        "neighborhood": neighborhood,
        "bedroom_quantity": bedroom_quantity,
        "suite_quantity": suite_quantity,
        "bathroom_quantity": bathroom_quantity,
        "garage_slots_quantity": garage_slots_quantity,
        "price": price,
        "area": area,
        "area_total": area_total,
        "available": available,
        "agency_id": agency,
        "cond_price": cond_price,
        "description": description,
        "thumb_url": thumb_url,
        "url": url,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    sql = """
        INSERT INTO real_estate_realestate (
            id, reference_code, property_type, transaction_type,
            city, neighborhood,
            bedroom_quantity, suite_quantity, bathroom_quantity,
            garage_slots_quantity,
            price, area, area_total, available,
            agency_id, cond_price,
            description, thumb_url, url, created_at, updated_at
        )
        VALUES (
            %(id)s, %(reference_code)s, %(property_type)s, %(transaction_type)s,
            %(city)s, %(neighborhood)s,
            %(bedroom_quantity)s, %(suite_quantity)s, %(bathroom_quantity)s,
            %(garage_slots_quantity)s,
            %(price)s, %(area)s, %(area_total)s, %(available)s,
            %(agency_id)s, %(cond_price)s,
            %(description)s, %(thumb_url)s, %(url)s, %(created_at)s, %(updated_at)s
        )
        RETURNING *;
    """

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, payload)
        new_row = cur.fetchone()
        conn.commit()

    return new_row


def get_agency_by_profile_url(profile_url: str) -> Dict[str, Any]:
    """
    Fetch agency object based in the profile url.
    Raises ObjectNotFoundError if not found.
    """
    sql = """
        SELECT *
        FROM real_estate_agency_agency reaa
        WHERE reaa.profile_url = %s
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (profile_url,))
        row = cur.fetchone()
        if row is None:
            raise ObjectNotFoundError(f"Search {profile_url} not found")
        cols = [c[0] for c in cur.description]

        agency_dict = {}
        for i, col in enumerate(cols):
            agency_dict[col] = row[i]

        return agency_dict


def insert_agency(
    name: str,
    logo_url: str,
    profile_url: str,
    creci: str,
    city: str,
    address_street: str,
    address_number: str,
    contact_number_1: str,
    contact_number_2: str,
    contact_whatsapp: str,
):
    agency_id = str(uuid4())
    payload = {
        "id": agency_id,
        "name": name,
        "logo_url": logo_url,
        "profile_url": profile_url,
        "creci": creci,
        "city": city,
        "address_street": address_street,
        "address_number": address_number,
        "contact_number_1": contact_number_1,
        "contact_number_2": contact_number_2,
        "contact_whatsapp": contact_whatsapp,
    }

    sql = """
        INSERT INTO real_estate_agency_agency (
            id, name, logo_url, profile_url,
            creci, city,
            address_street, address_number,
            contact_number_1, contact_number_2, contact_whatsapp
        ) VALUES (
            %(id)s, %(name)s, %(logo_url)s, %(profile_url)s,
            %(creci)s, %(city)s,
            %(address_street)s, %(address_number)s,
            %(contact_number_1)s, %(contact_number_2)s, %(contact_whatsapp)s
        )
        RETURNING *;
    """

    # Use a dict‑based cursor so we get column names back.
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, payload)
        new_row = cur.fetchone()
        conn.commit()

    return new_row


def set_search_number_real_estate_found(search_id: str, re_found: int) -> None:
    sql = """
        UPDATE search_search ss
        SET    number_real_estate_found = %s
        WHERE  ss.id = %s
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (re_found, search_id))
        if cur.rowcount == 0:
            raise ObjectNotFoundError(f"Search {search_id} not found")
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
            raise ObjectNotFoundError(f"Search {search_id} not found")
        conn.commit()
