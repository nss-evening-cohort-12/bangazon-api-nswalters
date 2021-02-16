"""Module for generating completed orders report"""
import sqlite3
from django.shortcuts import render
from bangazonreports.views import Connection


def list_incomplete_orders(request):
    """Function to build an HTML report for completed orders"""
    if request.method == "GET":
        with sqlite3.connect(Connection.db_path) as conn:
            conn.row_factory = sqlite3.Row
            db_cursor = conn.cursor()

            # Query for all orders that are completed
            db_cursor.execute("""
                SELECT
	                b_op.order_id,
	                user.first_name || ' ' || user.last_name as customer_name,
	                sum(b_prod.price) as total_cost
                FROM 
                    bangazonapi_order b_ord
                JOIN 
                    bangazonapi_customer b_cust
                ON
                    b_ord.customer_id = b_cust.id
                JOIN
                    auth_user user
                ON
                    b_cust.user_id = user.id
                JOIN
                    bangazonapi_orderproduct b_op
                ON
                    b_ord.id = b_op.order_id
                JOIN
                    bangazonapi_product b_prod
                ON
                    b_op.product_id = b_prod.id
                WHERE
                    b_ord.payment_type_id
                        IS NULL
                GROUP BY
                    order_id
            """)

            dataset = db_cursor.fetchall()

            incomplete_orders = []

            for row in dataset:
                order = {}
                order["order_id"] = row["order_id"]
                order["customer_name"] = row["customer_name"]
                order["total_cost"] = row["total_cost"]

                incomplete_orders.append(order)

        template = 'products/incomplete_orders.html'
        context = {
            'order_list': incomplete_orders
        }

        return render(request, template, context)
