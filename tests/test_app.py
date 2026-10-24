import pytest
from app import create_app

@pytest.fixture
def app(tmp_path):
    return create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.sqlite"), "SECRET_KEY": "test"})

@pytest.fixture
def client(app): return app.test_client()
def register(c,email="owner@example.com"): return c.post("/register",data={"full_name":"Owner","email":email,"password":"password1","confirm":"password1"})
def login(c,email="owner@example.com"): return c.post("/login",data={"email":email,"password":"password1"})
def add(c,name="Coffee",price="10"): return c.post("/menu/add",data={"name":name,"description":"Fresh","category":"Drinks","price":price,"available":"on"})

def test_auth_and_protection(client):
    assert client.get("/menu").status_code == 302
    assert b"valid email" in client.post("/register",data={"full_name":"A","email":"no","password":"short","confirm":"short"}).data
    register(client); assert b"already" in register(client).data
    assert login(client).status_code == 302
    assert client.post("/logout").status_code == 302

def test_menu_crud_search_and_invalid_price(client):
    register(client);login(client);add(client)
    assert b"Coffee" in client.get("/menu?q=Cof").data
    assert b"non-negative" in add(client,"Bad","-1").data
    client.post("/menu/edit/1",data={"name":"Latte","description":"","category":"Drinks","price":"12","available":"on"})
    assert client.post("/menu/delete/1").status_code == 302

def test_order_snapshots_edit_cancel_and_ownership(client):
    register(client);login(client);add(client,"Coffee","10");add(client,"Tea","5")
    client.post("/order/create",data={"customer_name":"Sam","qty_1":"2","qty_2":"3"})
    assert b"35.00" in client.get("/order/1").data
    client.post("/menu/edit/1",data={"name":"Coffee","description":"","category":"Drinks","price":"99","available":"on"})
    assert b"10.00" in client.get("/order/1").data
    client.post("/order/1/edit",data={"customer_name":"Sam","qty_1":"1","qty_2":"1"})
    assert b"104.00" in client.get("/order/1").data
    # A master-menu deletion must not change the saved bill, and its stale ID
    # must be rejected in every future order.
    assert client.post("/menu/delete/1").status_code == 302
    assert b"Coffee" in client.get("/order/1").data
    assert b"99.00" in client.get("/order/1").data
    assert b"unavailable" in client.post("/order/create",data={"customer_name":"New","qty_1":"1"}).data
    client.post("/order/1/cancel");client.post("/logout");register(client,"other@example.com");login(client,"other@example.com")
    assert client.get("/order/1").status_code == 404

def test_invalid_order_rolls_back(client,app):
    register(client);login(client);add(client)
    assert b"positive" in client.post("/order/create",data={"customer_name":"Sam","qty_1":"0"}).data
    assert b"unavailable" in client.post("/order/create",data={"customer_name":"Sam","qty_99":"1"}).data
    with app.app_context():
        from database import get_db
        assert get_db().execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0

def test_main_pages_render(client):
    register(client);login(client)
    for route in ("/","/menu","/menu/add","/order/create","/orders"): assert client.get(route).status_code == 200

def test_new_order_starts_with_empty_cart(client):
    register(client);login(client);add(client)
    page = client.get("/order/create").data
    assert b"Your order is empty" in page
    assert b'name="qty_1"' not in page
    assert b"Coffee" in page  # it is available in the Add Menu Items selector
