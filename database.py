import sqlite3
from pathlib import Path
from flask import current_app, g

def get_db():
    if "db" not in g:
        path = current_app.config["DATABASE"]; Path(path).parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(path); g.db.row_factory = sqlite3.Row; g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

def close_db(_error=None):
    db = g.pop("db", None)
    if db: db.close()

def init_db():
    db = get_db(); db.executescript((Path(current_app.root_path) / "schema.sql").read_text(encoding="utf-8"))
    columns = {r["name"] for r in db.execute("PRAGMA table_info(orders)")}
    if "status" not in columns: db.execute("ALTER TABLE orders ADD COLUMN status TEXT NOT NULL DEFAULT 'pending'")
    if "total" not in columns: db.execute("ALTER TABLE orders ADD COLUMN total REAL NOT NULL DEFAULT 0")
    db.commit()
    # Older databases linked order_items to menu_items. Bills already contain
    # immutable name/price snapshots, so remove that link without touching rows;
    # menu items can then be safely deleted from the master menu.
    references_menu = any(row["table"] == "menu_items" for row in db.execute("PRAGMA foreign_key_list(order_items)"))
    if references_menu:
        db.execute("PRAGMA foreign_keys = OFF")
        db.executescript("""
            CREATE TABLE order_items_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                menu_item_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                unit_price REAL NOT NULL CHECK (unit_price >= 0),
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                line_total REAL NOT NULL CHECK (line_total >= 0),
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
            );
            INSERT INTO order_items_new (id, order_id, menu_item_id, item_name, unit_price, quantity, line_total)
            SELECT id, order_id, menu_item_id, item_name, unit_price, quantity, line_total FROM order_items;
            DROP TABLE order_items;
            ALTER TABLE order_items_new RENAME TO order_items;
        """)
        db.execute("PRAGMA foreign_keys = ON")
        db.commit()

def init_app(app): app.teardown_appcontext(close_db)

def get_all_menu_items(category="", availability=""):
    sql, values = "SELECT * FROM menu_items WHERE 1=1", []
    if category: sql += " AND category=?"; values.append(category)
    if availability in ("0", "1"): sql += " AND available=?"; values.append(int(availability))
    return get_db().execute(sql + " ORDER BY category, name", values).fetchall()

def get_menu_item(item_id): return get_db().execute("SELECT * FROM menu_items WHERE id=?", (item_id,)).fetchone()
def get_categories(): return get_db().execute("SELECT DISTINCT category FROM menu_items ORDER BY category").fetchall()
def search_menu_items(query, category="", availability=""):
    sql, values = "SELECT * FROM menu_items WHERE (name LIKE ? OR category LIKE ?)", [f"%{query}%", f"%{query}%"]
    if category: sql += " AND category=?"; values.append(category)
    if availability in ("0", "1"): sql += " AND available=?"; values.append(int(availability))
    return get_db().execute(sql + " ORDER BY category, name", values).fetchall()

def add_menu_item(name, description, category, price, available):
    try:
        db=get_db(); db.execute("INSERT INTO menu_items (name,description,category,price,available) VALUES (?,?,?,?,?)", (name,description,category,price,available)); db.commit()
    except sqlite3.IntegrityError as exc: get_db().rollback(); raise ValueError("A menu item with that name already exists.") from exc

def update_menu_item(item_id, name, description, category, price, available):
    try:
        db=get_db(); cur=db.execute("UPDATE menu_items SET name=?,description=?,category=?,price=?,available=? WHERE id=?", (name,description,category,price,available,item_id))
        if not cur.rowcount: raise ValueError("Menu item not found.")
        db.commit()
    except sqlite3.IntegrityError as exc: get_db().rollback(); raise ValueError("A menu item with that name already exists.") from exc

def delete_menu_item(item_id):
    try:
        db=get_db(); cur=db.execute("DELETE FROM menu_items WHERE id=?", (item_id,))
        if not cur.rowcount: raise ValueError("Menu item not found.")
        db.commit()
    except sqlite3.IntegrityError as exc: get_db().rollback(); raise ValueError("This item is in an order and cannot be deleted. Mark it unavailable instead.") from exc

def _lines(selections):
    quantities={}
    for sel in selections:
        try: item_id, qty=int(sel["menu_item_id"]), int(sel["quantity"])
        except (KeyError, TypeError, ValueError) as exc: raise ValueError("Quantities must be positive whole numbers.") from exc
        if qty <= 0: raise ValueError("Quantities must be positive whole numbers.")
        quantities[item_id]=quantities.get(item_id,0)+qty
    if not quantities: raise ValueError("Select at least one menu item.")
    lines=[]; db=get_db()
    for item_id, qty in quantities.items():
        item=db.execute("SELECT id,name,price,available FROM menu_items WHERE id=?",(item_id,)).fetchone()
        if not item or not item["available"]: raise ValueError("An item is unavailable or no longer exists.")
        price=float(item["price"]); lines.append((item_id,item["name"],price,qty,price*qty))
    return lines

def create_order(user_id, customer_name, selections):
    lines=_lines(selections); total=sum(x[4] for x in lines); db=get_db()
    with db:
        cur=db.execute("INSERT INTO orders (user_id,customer_name,total) VALUES (?,?,?)",(user_id,customer_name,total))
        for item_id,name,price,qty,line_total in lines: db.execute("INSERT INTO order_items (order_id,menu_item_id,item_name,unit_price,quantity,line_total) VALUES (?,?,?,?,?,?)",(cur.lastrowid,item_id,name,price,qty,line_total))
    return cur.lastrowid

def get_orders_for_user(user_id): return get_db().execute("SELECT o.*,COUNT(oi.id) AS item_count FROM orders o LEFT JOIN order_items oi ON oi.order_id=o.id WHERE o.user_id=? GROUP BY o.id ORDER BY o.created_at DESC,o.id DESC",(user_id,)).fetchall()
def get_order_detail(order_id,user_id):
    db=get_db(); order=db.execute("SELECT * FROM orders WHERE id=? AND user_id=?",(order_id,user_id)).fetchone()
    if not order: return None
    return {"order":order,"items":db.execute("SELECT item_name AS name,unit_price,quantity,line_total FROM order_items WHERE order_id=? ORDER BY id",(order_id,)).fetchall()}

def update_order(order_id,user_id,customer_name,selections):
    db=get_db(); order=db.execute("SELECT status FROM orders WHERE id=? AND user_id=?",(order_id,user_id)).fetchone()
    if not order: raise LookupError("Order not found.")
    if order["status"] != "pending": raise ValueError("Only pending orders can be edited.")
    lines=_lines(selections); total=sum(x[4] for x in lines)
    with db:
        db.execute("UPDATE orders SET customer_name=?,total=? WHERE id=?",(customer_name,total,order_id)); db.execute("DELETE FROM order_items WHERE order_id=?",(order_id,))
        for item_id,name,price,qty,line_total in lines: db.execute("INSERT INTO order_items (order_id,menu_item_id,item_name,unit_price,quantity,line_total) VALUES (?,?,?,?,?,?)",(order_id,item_id,name,price,qty,line_total))

def cancel_order(order_id,user_id):
    db=get_db(); cur=db.execute("UPDATE orders SET status='cancelled' WHERE id=? AND user_id=? AND status='pending'",(order_id,user_id))
    if not cur.rowcount: db.rollback(); raise ValueError("Only your pending orders can be cancelled.")
    db.commit()
