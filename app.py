import os
from functools import wraps
from pathlib import Path
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from auth import create_user, get_user_by_email, validate_registration, verify_user_password
from database import add_menu_item,cancel_order,create_order,delete_menu_item,get_all_menu_items,get_categories,get_menu_item,get_order_detail,get_orders_for_user,init_app as init_database_app,init_db,search_menu_items,update_menu_item,update_order

def login_required(view):
 @wraps(view)
 def wrapped(*args,**kwargs):
  if "user_id" not in session:return redirect(url_for("login",next=request.path))
  return view(*args,**kwargs)
 return wrapped
def price(value):
 try:
  value=float(value)
  return value if value>=0 else None
 except ValueError:return None
def form_selections():return [{"menu_item_id":k[4:],"quantity":v} for k,v in request.form.items() if k.startswith("qty_") and v.strip()]

def create_app(test_config=None):
 app=Flask(__name__,instance_relative_config=True); app.config.from_mapping(SECRET_KEY=os.environ.get("SECRET_KEY","dev-only-change-this"),DATABASE=os.path.join(app.instance_path,"cafe.sqlite"))
 if test_config:app.config.update(test_config)
 Path(app.instance_path).mkdir(parents=True,exist_ok=True);init_database_app(app)
 with app.app_context():init_db()
 @app.route("/")
 @login_required
 def home():return render_template("index.html")
 @app.route("/menu")
 @login_required
 def menu():
  q=request.args.get("q","").strip();cat=request.args.get("category","");avail=request.args.get("availability","")
  return render_template("menu.html",items=search_menu_items(q,cat,avail) if q else get_all_menu_items(cat,avail),query=q,categories=get_categories(),selected_category=cat,availability=avail)
 def menu_form(item=None):
  if request.method=="POST":
   name=request.form.get("name","").strip();desc=request.form.get("description","").strip();cat=request.form.get("category","").strip();cost=price(request.form.get("price","").strip());available=int(request.form.get("available")=="on")
   if not name or not cat or cost is None:flash("Name, category, and a non-negative price are required.","error")
   else:
    try:
     if item:update_menu_item(item["id"],name,desc,cat,cost,available);flash("Menu item updated.","success")
     else:add_menu_item(name,desc,cat,cost,available);flash("Menu item added.","success")
     return redirect(url_for("menu"))
    except ValueError as e:flash(str(e),"error")
  return render_template("menu_edit.html" if item else "menu_add.html",item=item)
 @app.route("/menu/add",methods=["GET","POST"])
 @login_required
 def menu_add():return menu_form()
 @app.route("/menu/edit/<int:item_id>",methods=["GET","POST"])
 @login_required
 def menu_edit(item_id):
  item=get_menu_item(item_id)
  if not item:abort(404)
  return menu_form(item)
 @app.post("/menu/delete/<int:item_id>")
 @login_required
 def menu_delete(item_id):
  try:delete_menu_item(item_id);flash("Menu item deleted.","success")
  except ValueError as e:flash(str(e),"error")
  return redirect(url_for("menu"))
 @app.route("/register",methods=["GET","POST"])
 def register():
  if request.method=="POST":
   name=request.form.get("full_name","").strip();email=request.form.get("email","").strip();password=request.form.get("password","");confirm=request.form.get("confirm","");error=validate_registration(name,email,password,confirm)
   if error:flash(error,"error")
   elif create_user(name,email,password):flash("Registration successful. Please log in.","success");return redirect(url_for("login"))
   else:flash("Email already registered.","error")
  return render_template("register.html")
 @app.route("/login",methods=["GET","POST"])
 def login():
  if request.method=="POST":
   email=request.form.get("email","").strip()
   if verify_user_password(email,request.form.get("password","") ):
    user=get_user_by_email(email);session.clear();session["user_id"]=user["id"];session["user_name"]=user["full_name"];n=request.args.get("next","");return redirect(n if n.startswith("/") and not n.startswith("//") else url_for("home"))
   flash("Invalid email or password.","error")
  return render_template("login.html")
 @app.post("/logout")
 @login_required
 def logout():session.clear();flash("Logged out.","success");return redirect(url_for("login"))
 @app.route("/order/create",methods=["GET","POST"])
 @login_required
 def order_create():
  items=get_all_menu_items(availability="1")
  if request.method=="POST":
   customer=request.form.get("customer_name","").strip()
   if not customer:flash("Customer name is required.","error")
   else:
    try:oid=create_order(session["user_id"],customer,form_selections());flash("Order placed.","success");return redirect(url_for("order_detail",order_id=oid))
    except ValueError as e:flash(str(e),"error")
  return render_template("order_create.html",items=items,order=None,quantities={})
 @app.route("/order/<int:order_id>")
 @login_required
 def order_detail(order_id):
  detail=get_order_detail(order_id,session["user_id"])
  if not detail:abort(404)
  return render_template("order_detail.html",**detail)
 @app.route("/order/<int:order_id>/edit",methods=["GET","POST"])
 @login_required
 def order_edit(order_id):
  detail=get_order_detail(order_id,session["user_id"])
  if not detail:abort(404)
  if detail["order"]["status"]!="pending":flash("Only pending orders can be edited.","error");return redirect(url_for("order_detail",order_id=order_id))
  if request.method=="POST":
   customer=request.form.get("customer_name","").strip()
   try:
    if not customer:raise ValueError("Customer name is required.")
    update_order(order_id,session["user_id"],customer,form_selections());flash("Order updated.","success");return redirect(url_for("order_detail",order_id=order_id))
   except (ValueError,LookupError) as e:flash(str(e),"error")
  quantities={row["name"]:row["quantity"] for row in detail["items"]}
  return render_template("order_create.html",items=get_all_menu_items(availability="1"),order=detail["order"],quantities=quantities)
 @app.post("/order/<int:order_id>/cancel")
 @login_required
 def order_cancel(order_id):
  try:cancel_order(order_id,session["user_id"]);flash("Order cancelled.","success")
  except ValueError as e:flash(str(e),"error")
  return redirect(url_for("order_detail",order_id=order_id))
 @app.route("/orders")
 @login_required
 def order_history():return render_template("order_history.html",orders=get_orders_for_user(session["user_id"]))
 return app
app=create_app()
if __name__=="__main__":app.run(debug=True)
