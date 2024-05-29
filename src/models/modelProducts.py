from .entities.products import Product

class ModelProducts:
    @classmethod
    def get_all_products(self, db):
        try:
            cursor = db.connection.cursor()
            cursor.execute("SELECT * FROM products")
            rows = cursor.fetchall()
            products = []
            for row in rows:
                product = Product(row[0], row[1], row[2], row[3], row[4])
                products.append(product)
            return products
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_product_by_id(self, db, id):
        try:
            cursor = db.connection.cursor()
            cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
            row = cursor.fetchone()
            if row:
                return Product(row[0], row[1], row[2], row[3], row[4])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def add_product(self, db, product):
        try:
            cursor = db.connection.cursor()
            cursor.execute("INSERT INTO products (prodName, descript, price, image) VALUES (%s, %s, %s, %s)",
                           (product.name, product.description, product.price, product.image))
            db.connection.commit()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def update_product(self, db, product):
        try:
            cursor = db.connection.cursor()
            cursor.execute("UPDATE products SET prodName=%s, descript=%s, price=%s, image=%s WHERE id=%s",
                           (product.name, product.description, product.price, product.image, product.id))
            db.connection.commit()
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def delete_product(self, db, id):
        try:
            cursor = db.connection.cursor()
            cursor.execute("DELETE FROM products WHERE id=%s", (id,))
            db.connection.commit()
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def search_products(cls, db, query):
        try:
            cursor = db.connection.cursor()
            search_query = f"%{query}%"
            cursor.execute("SELECT * FROM products WHERE prodName LIKE %s OR descript LIKE %s", (search_query, search_query))
            rows = cursor.fetchall()
            products = []
            for row in rows:
                products.append(Product(row[0], row[1], row[2], row[3], row[4]))
            return products
        except Exception as ex:
            raise Exception(ex)
