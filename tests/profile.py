import json
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from bangazonapi.models import Customer
from rest_framework.authtoken.models import Token


class ProfileTests(APITestCase):
    def setUp(self) -> None:
        """
        Setup accounts
        """

        new_user1 = User.objects.create_user(
            username='first',
            email='email@email.com',
            password='p@ssW0Rd',
            first_name='firstName',
            last_name='lastName'
        )

        new_user2 = User.objects.create_user(
            username='second',
            email='second@email.com',
            password='p@ssW0Rd',
            first_name='firstName2',
            last_name='lastName2'
        )

        # Customer_id 1 will have user_id 2
        customer = Customer.objects.create(
            phone_number='123123',
            address='asdfas',
            user=new_user2
        )

        customer.save()

        new_token = Token.objects.create(user=new_user2)
        self.new_user2_token = new_token.key

        # Customer_id 2 will have user_id 1
        customer = Customer.objects.create(
            phone_number='99999',
            address='bbbb',
            user=new_user1
        )

        customer.save()

        new_token = Token.objects.create(user=new_user1)
        self.new_user1_token = new_token.key

    def test_get_current_user_profile(self):
        """
        Ensure we get the current user's profile back
        """
        # Verify first customer uses second user's info
        url = "/profile"
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.new_user2_token)
        response = self.client.get(url, None, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["id"], 1)
        self.assertEqual(json_response["user"]["first_name"], "firstName2")

        # Verify second customer uses first user's info
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.new_user1_token)
        response = self.client.get(url, None, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["id"], 2)
        self.assertEqual(json_response["user"]["first_name"], "firstName")
        self.assertEqual(json_response["phone_number"], "99999")

    def test_add_new_favorite_seller(self):
        """
        Ensure we can add a favorite seller
        """
        url = "/profile/favoritesellers"
        data = {
            "seller": 1
        }
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.new_user1_token)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_do_not_add_new_favorite_seller_that_does_not_exist(self):
        """
        Ensure we cannot add a favorite seller that doesn't exist
        """
        url = "/profile/favoritesellers"
        data = {
            "seller": 100
        }
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.new_user1_token)
        response = self.client.post(url, data, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(json_response["message"],
                         "Customer matching query does not exist.")

    def test_get_current_favorite_sellers(self):
        """
        Ensure we can get the favorite sellers
        """

        # Add a favorite seller
        self.test_add_new_favorite_seller()

        # Get our favorite sellers
        url = "/profile/favoritesellers"
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.new_user1_token)
        response = self.client.get(url, None, format='json')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0]["id"], 1)
