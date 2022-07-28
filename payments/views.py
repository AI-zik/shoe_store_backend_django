from decimal import Decimal
import stripe
import json
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from payments.serializers import ProductCheckoutSerializer, ProductListSerializer
from shoes.models import AvailableShoeSize, CartItem
from users.models import User
from .models import Purchase, Transaction

stripe.api_key = settings.STRIPE_SECRET_KEY



class CreatePaymentIntentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):

        if request.data.get("product_source") == 1:
            products = []
            cart_items = CartItem.objects.filter(user = request.user)

            if len(cart_items) > 0:

                # adding product data from cart to serializer if cart is not empty
                for item in cart_items:
                    products.append({
                        "id" : item.id,
                        "quantity" : item.quantity
                    })
            
                request.data["products"] = products
            else:
                
                # clearing the products key if the cart is empty
                request.data.pop("products", None)

        serializer = ProductCheckoutSerializer(data = request.data)
        if serializer.is_valid():

            data = serializer.data
            amount = 0

            #calculating the total price of the products
            for item in data["products"]:
                
                # getting the total amount of each product
                product_amount = (item["price"] - (item["price"] * item["discount"])) * item["quantity"]
                amount+= int(product_amount * 100)

                # converting the prices and discounts to serializable JSON types
                item["price"] = str(item['price'])
                item["discount"] = str(item["discount"])

            # creating the payment intent
            try:
                intent = stripe.PaymentIntent.create(
                    amount = amount,
                    currency = 'usd',
                    automatic_payment_methods = {
                        "enabled" : True
                    },

                    # adding the products to the payment intent
                    # along with the ID of the user making the intent
                    metadata = {
                        "user_id" : request.user.id,
                        "products" : f"""{json.dumps(data["products"])}""",
                        "product_source" : data["product_source"]
                    },

                    # the stripe customer ID of the user
                    customer = request.user.stripe_customer_id
                )
                return Response({ "client_secret" : intent["client_secret"] }, status = status.HTTP_201_CREATED)
        
            except Exception as e:
                return Response({"error" : str(e)}, status = status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateCheckoutSessionView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        line_items = []
        products = []

        if request.data.get("product_source") == 1:
            cart_items = CartItem.objects.filter(user = request.user)
            if len(cart_items) > 0:
                for item in cart_items:
                    products.append({
                        "id" : item.id,
                        "quantity" : item.quantity
                    })
                request.data["products"] = products
            else:
                request.data.pop("products", None)

        serializer = ProductCheckoutSerializer(data = request.data)
        if serializer.is_valid():
            data = serializer.data
            for item in data["products"]:

                # getting the unit amount of each product
                unit_amount = int(item["price"] - (item["price"] * item["discount"])) * 100
                
                # converting the price to whole number integers
                item["price"] = str(item["price"])


                # appending to the line items
                line_items.append({
                    "price_data" : {
                        "currency" : "usd",
                        "product_data" : {
                            "name" : item["name"]
                        },
                        "unit_amount" : unit_amount
                    },
                    "quantity" : item["quantity"]
                })
                
                # converting the discount to string
                item["discount"] = str(item["discount"])

            session = stripe.checkout.Session.create(
                line_items = line_items,
                mode = "payment",
                success_url = "https://google.com",
                cancel_url = "https://google.com",
                customer = request.user.stripe_customer_id,
                payment_intent_data = {
                    "metadata" : {
                        "user_id" : request.user.id,
                        "products" : json.dumps(data["products"]),
                        "product_source" : data["product_source"]
                    }
                }
                
            )
            return Response({"url" : session.url}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class StripeWebhookView(APIView):

    def post(self, request, format = None):
        event = None

        # getting the raw request body
        payload = request.body

        endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

        # checking the signature header
        signature_header = request.headers.get('Stripe-Signature')

        try:
            event = stripe.Webhook.construct_event(payload, signature_header, endpoint_secret)
        except stripe.error.SignatureVerificationError as e:
            print(e)
            return Response("Webhook signature verifiation failed", status=status.HTTP_400_BAD_REQUEST)

        if event and event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            amount = payment_intent["amount"]
            user_id = payment_intent["metadata"].get("user_id")
            user = User.objects.get(id = user_id)
            product_source = int(payment_intent["metadata"].get("product_source"))
            print(product_source)

            # creating a transaction record in the database
            transaction = Transaction(payment_intent_id = payment_intent["id"], user = user)
            transaction.save()


            # getting the product data
            products = json.loads(payment_intent["metadata"].get("products"))
            
            for item in products:

                # converting the price of product back to decimal
                item["price"] = Decimal(item["price"])

                # converting the discount back to decimal
                item["discount"] = Decimal(item["discount"])

                # reducing the quantities of each product
                product = AvailableShoeSize.objects.get(id = item["id"])
                product.quantity -= item["quantity"]
                product.save()
                
                if product_source == 1:

                    # deleting the cart items since the purchase is done
                    cart_item = CartItem.objects.get(id = item["id"], user = user)
                    print(cart_item)
                    cart_item.delete()

                # reducing each item in each user's cart in the database
                # where the quantity is greater than available stock.
                cart_items = CartItem.objects.filter(shoe__id = item["id"], quantity__gt = product.quantity)
                for item in cart_items:
                    item.quantity = product.quantity
                    item.save()


                # entering each item purchased in the database
                purchase = Purchase(
                    quantity = item["quantity"],
                    shoe = AvailableShoeSize.objects.get(id = item["id"]),
                    price = item["price"],
                    discount = item["discount"],
                    transaction = transaction
                )

                purchase.save()



        elif event['type'] == 'payment_method.attached':
            payment_method = event['data']['object']  # contains a stripe.PaymentMethod
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)

        else:
            # Unexpected event type
            print('Unhandled event type {}'.format(event['type']))

        return Response()