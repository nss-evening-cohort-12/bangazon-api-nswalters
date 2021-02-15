"""Module for generating inexpensive products report"""
import sqlite3
from django.shortcuts import render
from bangazonreports.views import Connection


def list_inexpensive_products(request):
    """Function to build an HTML report of inexpensive products"""
    if request.method == "GET":
        with sqlite3.connect(Connection.db_path) as conn:
            conn.row_factory = sqlite3.Row
            db_cursor = conn.cursor()

            # Query for all products with a price greater than $1000
            db_cursor.execute("""
                SELECT
                    p.name,
                    p.price,
                    p.description,
                    p.quantity,
                    p.created_date,
                    p.location
                FROM
                    bangazonapi_product p
                WHERE
                    p.price < 1000
                ORDER BY
                    p.price ASC
            """)

            dataset = db_cursor.fetchall()

            product_list = []

            for row in dataset:
                product = {}
                product["name"] = row["name"]
                product["price"] = row["price"]
                product["description"] = row["description"]
                product["quantity"] = row["quantity"]
                product["created_date"] = row["created_date"]
                product["location"] = row["location"]

                product_list.append(product)

        template = 'products/list_inexpensive_products.html'
        context = {
            'product_list': product_list
        }

        return render(request, template, context)
