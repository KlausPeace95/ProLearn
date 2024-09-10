from decimal import Decimal
import os

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import json

from courses.models import Course
from .models import Payment, PaymentIntent

import stripe



stripe_api_key=os.environ.get("STRIPE_APIKEY")
endpoint_secret=""
stripe.api_key=stripe_api_key

class PaymentHandler(APIView):
    def post(sel, request):
        if request.body:
            body=json.load(request.body)
            if body and len(body):
                course_line_items=[]
                cart_course=[]
                for items in body:
                    try:
                        course=Course.objects.get(course_uuid=item)
                        line_item={
                            "price_data":{
                                "currency":"FCFA",
                                "unit_amount": int(course.price*100),
                                "product_data":{
                                    "name":course.title
                                },
                            },   
                            "quantity":1
                        }

                        course_line_items.append(line_item)
                        cart_course.append(course)

                    except Course.DoesNotExist:
                        return Response(status=status.HTTP_400_BAD_REQUEST)
            
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        checkout_session=stripe.checkout.session.create(
            payment_method=["card"],
            line_items=course_line_items(),
            mode="payment",
            success_url="http://localhost:3000/",
            cancel_url="http://localhost:3000/",
        )

        intent=PaymentIntent.objects.create(
            payment_intent_id=checkout_session.payment_intent,
            checkout_id=checkout_session.id,
            user=request.user
        )

        intent.courses.add(*cart_course)

        return Response({"url":checkout_session.url})


class Webhook(APIView):
    def post(self, request):
        payload=request.body
        sig_header=request.META["HTTP_STRIPE_SIGNATURE"]

        event=None

        try:
            event=stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                endpoint_secret=endpoint_secret
            )

        # except stripe.error.SignatureVerificationError:          # Check whether event is not coming from stripe
        except :                                                   # Make the Error General
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
        if event["type"]=="checkout.session.complete":
            session=event["data"]["object"]
            try:
                intent=PaymentIntent.objects.get(checkout_id=session.id,
                                                 payment_intent_id=session.payment_intent)
            except PaymentIntent.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            Payment.objects.create(
                payment_intent=intent,
                total_amount=Decimal(session.amount_total/100)
            )

            intent.user.paid_course.add(*intent.courses.all())

            return Response(status=200)

            