"""Sprint BIZ-45 — book store ISBN / author / publisher metadata."""

from tests.conftest import login


def _switch(client, headers, business_type="book_store"):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Fiction"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _book(client, headers, category_id, name, **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "399",
        "gst_percentage": "5",
        "stock_quantity": "12",
        "uom": "pcs",
        "isbn": "9780140449136",
        "author": "Homer",
        "publisher": "Penguin Classics",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_book_store_module_flags(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner)
    modules = client.get("/api/v1/tenants/me/modules", headers=owner).get_json()["data"][
        "enabled_modules"
    ]
    for code in ("book_metadata", "barcode_pos", "bulk_pricing", "returns_exchange"):
        assert code in modules, code


def test_book_metadata_fields_and_update(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner)
    cat_id = _category(client, owner)
    book = _book(client, owner, cat_id, "The Odyssey")
    assert book["isbn"] == "9780140449136"
    assert book["author"] == "Homer"
    assert book["publisher"] == "Penguin Classics"

    updated = client.put(
        f"/api/v1/items/{book['id']}",
        headers=owner,
        json={"author": "Homer (tr. Rieu)", "publisher": "Penguin"},
    )
    assert updated.status_code == 200, updated.get_json()
    body = updated.get_json()["data"]
    assert body["author"] == "Homer (tr. Rieu)"
    assert body["publisher"] == "Penguin"
    assert body["isbn"] == "9780140449136"


def test_isbn_unique_per_tenant(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner)
    cat_id = _category(client, owner)
    _book(client, owner, cat_id, "Odyssey A", isbn="978-0-14-044913-6")
    dup = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Odyssey B",
            "category_id": cat_id,
            "price": "299",
            "gst_percentage": "5",
            "isbn": "9780140449136",
            "uom": "pcs",
        },
    )
    assert dup.status_code == 409, dup.get_json()


def test_search_by_isbn_author_and_books_api(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner)
    cat_id = _category(client, owner)
    book = _book(
        client,
        owner,
        cat_id,
        "Pride and Prejudice",
        isbn="9780141439518",
        author="Jane Austen",
        publisher="Penguin",
    )

    by_q = client.get(
        "/api/v1/items",
        headers=billing,
        query_string={"q": "Austen"},
    )
    assert by_q.status_code == 200, by_q.get_json()
    names = {row["name"] for row in by_q.get_json()["data"]}
    assert "Pride and Prejudice" in names

    by_isbn_param = client.get(
        "/api/v1/items",
        headers=billing,
        query_string={"isbn": "978-0141439518"},
    )
    assert by_isbn_param.status_code == 200, by_isbn_param.get_json()
    assert by_isbn_param.get_json()["data"][0]["id"] == book["id"]

    catalog = client.get(
        "/api/v1/books/catalog",
        headers=billing,
        query_string={"q": "9780141439518"},
    )
    assert catalog.status_code == 200, catalog.get_json()
    assert any(row["id"] == book["id"] for row in catalog.get_json()["data"])

    exact = client.get("/api/v1/books/by-isbn/978-0141-439518", headers=billing)
    assert exact.status_code == 200, exact.get_json()
    assert exact.get_json()["data"]["id"] == book["id"]


def test_books_forbidden_without_module(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    _switch(client, owner, "hotel_restaurant")
    assert client.get("/api/v1/books/catalog", headers=owner).status_code == 403
