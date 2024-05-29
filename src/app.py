import os
from flask import Flask, abort, flash, jsonify, redirect, render_template, request, url_for, session
from flask_mysqldb import MySQL
from flask_wtf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from models.modelUsers import ModelUsers
from models.modelProducts import ModelProducts
from models.modelCart import ModelCart
from models.entities.users import User
from models.entities.products import Product
from config import config
from werkzeug.utils import secure_filename
app = Flask(__name__)
db = MySQL(app)
login_manager_app = LoginManager(app)

app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

csrf = CSRFProtect(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@login_manager_app.user_loader
def load_user(id):
    return ModelUsers.get_by_id(db, id)


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
    # Verificar si el usuario está autenticado y es un administrador
        if not current_user.is_authenticated or current_user.usertype != 1:
            abort(403) # Acceso prohibido
        return func(*args, **kwargs)
    return decorated_view

@app.route('/')
def root():
    return redirect("login")

@app.route('/home')
@login_required
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User(0, request.form['username'], request.form['password'], 0)
        logged_user = ModelUsers.login(db, user)
        print("Logged User:", logged_user)  # Debug print
        if logged_user is not None:
            login_user(logged_user)
            return redirect(url_for("admin"))
        else:
            flash('Acceso rechazado.', 'danger')
            return render_template("auth/login.html")
    else:
        return render_template("auth/login.html")

    
@app.route('/admin')
@login_required
def admin():
    return render_template("admin.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/catalogue')
@login_required
def catalogue():
    products = ModelProducts.get_all_products(db)
    return render_template('catalogue.html', products=products)

# @app.route('/product/<int:id>')
# @login_required
# def product_detail(id):
#     product = ModelProducts.get_product_by_id(db, id)
#     if product:
#         return render_template('product_detail.html', product=product)
#     else:
#         flash('Product not found')
#         return redirect(url_for('home'))

@app.route('/addProduct', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.usertype != 1:
        flash('Access denied')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        file = request.files['image']
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            new_product = Product(None, name, description, price, filename)
            ModelProducts.add_product(db, new_product)
            flash('Producto registrado exitosamente.', 'success')
            return redirect(url_for('catalogue'))
    
    return render_template('catalogue')

@app.route('/getProduct/<int:id>', methods=['GET'])
@login_required
def get_product(id):
    if current_user.usertype != 1:
        return jsonify({'error': 'Access denied'}), 403

    product = ModelProducts.get_product_by_id(db, id)
    if product:
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'image': product.image
        }
        print("THIS IS THE PRODUCT DATAAAAAA")
        print(product_data)

        return jsonify(product_data)
    else:
        return jsonify({'error': 'Product not found'}), 404


@app.route('/editProduct', methods=['POST'])
@login_required
def edit_product():
    if current_user.usertype != 1:
        flash('Access denied')
        return redirect(url_for('home'))

    product_id = request.form['productId']
    print(f"Received productId: {product_id}")

    name = request.form['name']
    print(f"Received name: {name}")

    description = request.form['description']
    print(f"Received description: {description}")

    price = request.form['price']
    print(f"Received price: {price}")

    file = request.files['image']
    print(f"Received file: {file.filename if file else 'No file uploaded'}")

    product = ModelProducts.get_product_by_id(db, product_id)

    if product:
        product.name = name
        product.description = description
        product.price = price

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            product.image = filename

        ModelProducts.update_product(db, product)
        flash('Producto actualizado exitosamente', 'success')
    else:
        flash('Error, el producto no fue encontrado.', 'danger')

    return redirect(url_for('catalogue'))

@app.route('/deleteProduct', methods=['POST'])
@login_required
def delete_product():
    id = request.form['id']
    if current_user.usertype != 1:
        flash('Access denied', 'danger')
        return redirect(url_for('home'))

    try:
        ModelProducts.delete_product(db, id)
        flash('Product deleted successfully', 'success')
    except Exception as ex:
        print(f"Error deleting product: {ex}")
        flash('An error occurred while deleting the product', 'danger')

    return redirect(url_for('catalogue'))

# app.py
@app.route('/addToCart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = ModelProducts.get_product_by_id(db, product_id)
    if product:
        ModelCart.add_to_cart(product)
        return jsonify({'success': True, 'message': 'Product added to cart'})
    else:
        return jsonify({'success': False, 'message': 'Product not found'}), 404

@app.route('/cart')
@login_required
def view_cart():
    cart = ModelCart.get_cart()
    print("THIS IS THE CAAAART")
    print(cart)
    return render_template('cart.html', cart=cart)

@app.route('/removeFromCart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    ModelCart.remove_from_cart(product_id)
    flash('Articulo eliminado de su carrito.', 'success')
    return redirect(url_for('view_cart'))

@app.route('/clearCart', methods=['POST'])
@login_required
def clear_cart():
    ModelCart.clear_cart()
    flash('Su carrito ha sido vaciado.', 'success')
    return redirect(url_for('view_cart'))

@app.route('/users')
@login_required
@admin_required
def list_users():
    users = ModelUsers.get_all_users(db)
    return render_template('users.html', users=users)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        usertype = request.form['usertype']
        user = User(0, username, password, usertype, fullname)
        ModelUsers.add_user(db, user)
        flash('Usuario agregado exitosamente.', 'success')
        return redirect(url_for('list_users'))

    return render_template('users.html')

@app.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    user = ModelUsers.get_by_id(db, id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.fullname = request.form['fullname']
        user.usertype = request.form['usertype']
        ModelUsers.update_user(db, user)
        flash('Usuario actualizado exitosamente.', 'success')
        return redirect(url_for('list_users'))
    
    return render_template('users/edit.html', user=user)

@app.route('/users/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    ModelUsers.delete_user(db, id)
    flash('Usuario eliminado exitosamente.', 'success')
    return redirect(url_for('list_users'))


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        query = request.form['query']
        products = ModelProducts.search_products(db, query)
        return render_template('search_results.html', products=products, query=query)
    return render_template('search.html')



if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()
    
    
