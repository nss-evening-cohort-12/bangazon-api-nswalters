"""Module for generating favorited sellers report"""
import sqlite3
from django.shortcuts import render
from bangazonreports.views import Connection


def list_favorited_sellers(request):
    """Function to build an HTML report for favorited sellers by customer"""
    if request.method == "GET":
        with sqlite3.connect(Connection.db_path) as conn:
            conn.row_factory = sqlite3.Row
            db_cursor = conn.cursor()

            # Query for all customers and their favorite sellers
            db_cursor.execute("""
            SELECT
            	buyer_user.first_name as user,
	            seller_user.first_name as favorited_seller
            FROM
	            bangazonapi_favorite as fav
            JOIN
	            bangazonapi_customer as seller_cust
	            ON
		            seller_cust.id = fav.seller_id
            JOIN
	            auth_user as seller_user
	            ON
		            seller_user.id = seller_cust.user_id
            JOIN
	            bangazonapi_customer as buyer_cust
	            ON
		            buyer_cust.id = fav.customer_id
            JOIN
	            auth_user as buyer_user
	            ON
		            buyer_user.id = buyer_cust.user_id
            """)

            dataset = db_cursor.fetchall()

            favorite_sellers = {}

            for row in dataset:

                customer = row["user"]

                # If the 'buyer' is already a key in our dictionary
                if customer in favorite_sellers:
                    favorite_sellers[customer].append(row["favorited_seller"])

                # Otherwise, we add that buyer as a key
                else:
                    favorite_sellers[customer] = [row["favorited_seller"]]

            print(favorite_sellers)

            template = 'favorites/favoritedsellers.html'
            context = {
                'favorited_sellers': favorite_sellers
            }

            return render(request, template, context)
