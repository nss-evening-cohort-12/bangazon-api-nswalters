import json
import datetime
from rest_framework import status
from rest_framework.test import APITestCase
from bangazonapi.models import Product


class ProductTests(APITestCase):
    def setUp(self) -> None:
        """
        Create a new account and create sample category
        """
        # Creates primary user
        url = "/register"
        data = {"username": "steve", "password": "Admin8*", "email": "steve@stevebrownlee.com",
                "address": "100 Infinity Way", "phone_number": "555-1212", "first_name": "Steve", "last_name": "Brownlee"}
        response = self.client.post(url, data, format='json')
        json_response = json.loads(response.content)
        self.token = json_response["token"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create secondary user
        url = "/register"
        data = {"username": "secondary", "password": "Admin8*", "email": "secondary@stevebrownlee.com",
                "address": "100 Infinity Way", "phone_number": "555-1212", "first_name": "Steve", "last_name": "Brownlee"}
        response = self.client.post(url, data, format='json')
        json_response = json.loads(response.content)
        self.token_secondary = json_response["token"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = "/productcategories"
        data = {"name": "Sporting Goods"}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        response = self.client.post(url, data, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["name"], "Sporting Goods")

        # Create a PaymentType
        url = "/paymenttypes"
        data = {
            "merchant_name": "American Express",
            "account_number": "111-1111-1111",
            "expiration_date": "2024-12-31",
            "create_date": datetime.date.today()
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url, data, format='json')
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_product(self):
        """
        Ensure we can create a new product.
        """
        url = "/products"
        data = {
            "name": "Kite",
            "price": 14.99,
            "quantity": 60,
            "description": "It flies high",
            "category_id": 1,
            "location": "Pittsburgh"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url, data, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["name"], "Kite")
        self.assertEqual(json_response["price"], 14.99)
        self.assertEqual(json_response["quantity"], 60)
        self.assertEqual(json_response["description"], "It flies high")
        self.assertEqual(json_response["location"], "Pittsburgh")

    def test_update_product(self):
        """
        Ensure we can update a product.
        """
        self.test_create_product()

        url = "/products/1"
        data = {
            "name": "Kite",
            "price": 24.99,
            "quantity": 40,
            "description": "It flies very high",
            "category_id": 1,
            "created_date": datetime.date.today(),
            "location": "Pittsburgh"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(url, data, format='json')
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["name"], "Kite")
        self.assertEqual(json_response["price"], 24.99)
        self.assertEqual(json_response["quantity"], 40)
        self.assertEqual(json_response["description"], "It flies very high")
        self.assertEqual(json_response["location"], "Pittsburgh")

    def test_get_all_products(self):
        """
        Ensure we can get a collection of products.
        """
        self.test_create_product()
        self.test_create_product()
        self.test_create_product()

        url = "/products"

        response = self.client.get(url, None, format='json')
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 3)

    def test_products_number_sold_query_param(self):
        """
        Ensure we can filter products based on the number sold
        """

        # Create some products to add
        self.test_create_product()
        self.test_create_product()

        # Add products to order

        # Add three of the same item which -SHOULD- be returned in the
        # 'number_sold=3' query
        for i in range(3):
            url = "/cart"
            data = {"product_id": 1}
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
            response = self.client.post(url, data, format='json')

            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Add two different items which -SHOULD NOT- be returned in the
        # 'number_sold=3' query
        for i in range(2):
            url = "/cart"
            data = {"product_id": 2}
            self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
            response = self.client.post(url, data, format='json')

            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Add payment_type to order
        url = "/orders/1"
        data = {"payment_type": 1}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Now we have sold items, verify we can filter those items properly
        # We are looking to get only the products that have sold >= 3 items
        url = "/products?number_sold=3"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(url, None, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0]["id"], 1)

    def test_products_min_price_query_param(self):
        """
        Ensure we can filter products based on a given minimum price
        """

        # Create a product
        self.test_create_product()

        # Request products >= 15 dollars (should return no results)
        url = "/products?min_price=15"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(url, None, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 0)

        # Request products >= 14 dollars (should return 1 result)
        url = "/products?min_price=14"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(url, None, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0]["id"], 1)

        # Request products using decimal query param
        url = "/products?min_price=14.99"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(url, None, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0]["id"], 1)

    def test_validate_create_product_over_maximum_price(self):
        """
        Verify that we cannot have a product over the maximum allowed price
        """
        # Attempt to create a product with a price > the max
        max_price = float(Product._meta.get_field(
            'price').validators[1].limit_value)

        url = "/products"
        data = {
            "name": "Kite",
            "price": max_price + 1,
            "quantity": 60,
            "description": "It flies high",
            "category_id": 1,
            "location": "Pittsburgh"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url, data, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json_response["message"]["price"][0][0],
                         "Ensure this value is less than or equal to " + str(max_price) + ".")

    def test_validate_update_product_over_maximum_price(self):
        """
        Verify that we cannot have a product over the maximum allowed price
        """
        # Create a base product
        self.test_create_product()

        # Get the current configured max_price from the MaxValueValidator
        # on the 'price' field of the 'Product' model
        max_price = float(Product._meta.get_field(
            'price').validators[1].limit_value)

        # Attempt to update a product and set the price > max_price
        url = "/products/1"
        data = {
            "name": "Kite",
            "price": max_price + 1,
            "quantity": 40,
            "description": "It flies very high",
            "category_id": 1,
            "created_date": datetime.date.today(),
            "location": "Pittsburgh"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.put(url, data, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json_response["message"]["price"][0][0],
                         "Ensure this value is less than or equal to " + str(max_price) + ".")

    def test_validate_create_product_under_minimum_price(self):
        """
        Verify that we cannot have a product under the minimum allowed price
        """
        # Attempt to create a product with a price < the min
        min_price = float(Product._meta.get_field(
            'price').validators[0].limit_value)

        url = "/products"
        data = {
            "name": "Kite",
            "price": min_price - 1,
            "quantity": 60,
            "description": "It flies high",
            "category_id": 1,
            "location": "Pittsburgh"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url, data, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json_response["message"]["price"][0][0],
                         "Ensure this value is greater than or equal to " + str(min_price) + ".")

    def test_validate_update_product_under_minimum_price(self):
        """
        Verify that we cannot have a product under the minimum allowed price
        """
        # Create a base product
        self.test_create_product()

        # Get the current configured max_price from the MaxValueValidator
        # on the 'price' field of the 'Product' model
        min_price = float(Product._meta.get_field(
            'price').validators[0].limit_value)

        # Attempt to update a product and set the price < min_price
        url = "/products/1"
        data = {
            "name": "Kite",
            "price": min_price - 1,
            "quantity": 40,
            "description": "It flies very high",
            "category_id": 1,
            "created_date": datetime.date.today(),
            "location": "Pittsburgh"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.put(url, data, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json_response["message"]["price"][0][0],
                         "Ensure this value is greater than or equal to " + str(min_price) + ".")

    def test_products_location_query_param(self):
        """
        Ensure we can filter products by their location
        """

        # Create initial product
        self.test_create_product()

        # Attempt to get our product based on the location
        url = "/products?location=Pittsburgh"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(url, None, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0]["name"], "Kite")
        self.assertEqual(json_response[0]["price"], 14.99)
        self.assertEqual(json_response[0]["quantity"], 60)
        self.assertEqual(json_response[0]["description"], "It flies high")
        self.assertEqual(json_response[0]["location"], "Pittsburgh")

        # Attempt to get a product by location that doesn't exist
        url = "/products?location=Philadelphia"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(url, None, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 0)

    def test_like_product(self):
        """
        Ensure that we can like a product
        """

        # create initial product
        self.test_create_product()

        # Like the product
        url = "/products/1/like"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url, None, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify product was liked
        url = "/products/liked"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(url, None, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0]["id"], 1)

    def test_not_like_product_twice(self):
        """
        Ensure that we cannot like a product more than once
        """

        # create initial product
        self.test_like_product()

        # Attempt to like the product again
        url = "/products/1/like"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url, None, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json_response["message"],
                         "You have already liked that product.")

    def test_unlike_product(self):
        """
        Ensure we can unlike a product
        """

        # Like our product
        self.test_like_product()

        # Verify product was unliked
        url = "/products/1/like"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.delete(url, None, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unlike_product_does_not_exist(self):
        """
        Ensure we cannot unlike a product that doesn't exist and handle it gracefully
        """

        # Attempt to unlike a product that doesn't exist
        url = "/products/12312312/like"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.delete(url, None, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product(self):
        """
        Ensure we can delete a product
        """

        # Create a couple test products
        self.test_create_product()
        self.test_create_product()

        # Attempt to delete the second product
        url = "/products/2"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.delete(url, None, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify product was "deleted" (it's soft-deleted, but still won't
        # show in the GET request)
        url = "/products"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(url, None, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0]["id"], 1)

    def test_rate_product(self):
        """
        Ensure we can rate a product
        """

        # Create test product
        self.test_create_product()

        # Attempt to rate the product with primary user
        url = "/products/1/rate"
        data = {
            "rating": 5
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # With the primary user:
        # Get product and validate rating exists and is set properly
        # as well as that 'can_be_rated' is set to false
        url = "/products/1"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(url, None, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["id"], 1)
        self.assertEqual(json_response["average_rating"], 5.0)
        self.assertEqual(json_response["can_be_rated"], False)

        # Rate the product with the secondary user
        url = "/products/1/rate"
        data = {
            "rating": 1
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token_secondary)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # With the secondary user:
        # Get product and validate rating exists and is set properly
        # as well as that 'can_be_rated' is set to false
        url = "/products/1"
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token_secondary)
        response = self.client.get(url, None, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["id"], 1)
        self.assertEqual(json_response["average_rating"], 3.0)
        self.assertEqual(json_response["can_be_rated"], False)

    def test_duplicate_ratings_not_allowed(self):
        """
        Ensure a user cannot rate a product more than once
        """

        # Create initial ratings
        self.test_rate_product()

        # Test rating our product again
        url = "/products/1/rate"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url, None, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(json_response["message"],
                         "You've already rated this product.")
