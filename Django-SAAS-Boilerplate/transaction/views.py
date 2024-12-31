from venv import logger
import stripe
from django.shortcuts import render
from django.conf import settings

from django.views.generic import View
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from payments import get_payment_model, RedirectNeeded

from .models import Plan, Transaction
from .forms import StripeSubscriptionForm

from django.http import JsonResponse
import stripe
from django.conf import settings
import logging


Payment = get_payment_model()
logger = logging.getLogger(__name__)

stripe.api_key = settings.PAYMENT_VARIANTS['stripe'][1]['secret_key']

@login_required
def create_payment(request):
    plan_id = request.POST.get("plan")
    
    if not plan_id:
        logger.error("Plan ID is missing.")
        return JsonResponse({"error": "Plan ID is required."}, status=400)
    
    try:
        plan = Plan.objects.get(id=int(plan_id))
    except (Plan.DoesNotExist, ValueError):
        logger.error(f"Invalid Plan ID: {plan_id}")
        return JsonResponse({"error": "Invalid Plan ID."}, status=404)
    
    amount = plan.price  # price in your plan model
    currency = 'usd'

    # Create payment record in your database
    payment = get_payment_model().objects.create(
        variant='stripe',  # Payment variant for Stripe
        total=amount,
        currency=currency,
        description=plan.description or '',
        billing_email=request.user.email,
        user=request.user,
        plan=plan
    )

    # Prepare the Stripe checkout session data
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': currency,
                'product_data': {
                    'name': plan.name,
                    'description': plan.description or '',
                },
                'unit_amount': plan.get_total_cents(),  # price in cents
            },
            'quantity': 1,
        }],
        mode='subscription',  # You can change to one-time if needed
        success_url=request.build_absolute_uri(payment.get_success_url()),
        cancel_url=request.build_absolute_uri(payment.get_failure_url()),
        client_reference_id=request.user.id,
        customer_email=request.user.email,
        metadata={'customer': request.user.id, 'payment_id': payment.id},
    )

    # Save the transaction ID and redirect to Stripe checkout
    payment.transaction_id = checkout_session.id
    payment.save()

    return JsonResponse({"checkout_url": checkout_session.url})


import logging

logger = logging.getLogger(__name__)

def verify_stripe_connection(request):
    logger.info("verify_stripe_connection endpoint called")
    try:
        account = stripe.Account.retrieve()
        return JsonResponse({
            "status": "success",
            "message": "Stripe is connected successfully!",
            "account_id": account.id,
            "business_name": account.business_profile.get("name", "Not set"),
        })
    except stripe.error.StripeError as e:
        # Log specific Stripe error
        logger.error(f"Stripe error: {e.user_message}")
        return JsonResponse({
            "status": "error",
            "message": f"Stripe error: {e.user_message}",
        }, status=500)
    except Exception as e:
        # Log any other unexpected errors
        logger.error(f"Unexpected error: {e}")
        return JsonResponse({
            "status": "error",
            "message": "An unexpected error occurred. Please try again later."
        }, status=500)


# @login_required
# def payment_details(request, payment_id):
#     payment = get_object_or_404(get_payment_model(), id=payment_id)
    
#     try:
#         form = payment.get_form(data=request.POST or None)
#     except RedirectNeeded as redirect_to:
#         return redirect(str(redirect_to))

#     return TemplateResponse(
#         request,
#         'html/payment/stripe.html',
#         {'form': form, 'payment': payment}
#     )


def pricing(request):

    plans = Plan.objects.all()

    return render(request, "payment/pricing.html", {
        'plans': plans
    })


def payment_success(request):

    return render(request, "html/payment/success.html")


def payment_failed(request):

    return render(request, "html/payment/failure.html")


from django.http import JsonResponse
import stripe
from django.conf import settings
import logging



# import stripe
# from django.conf import settings

# stripe.api_key = settings.PAYMENT_VARIANTS['stripe'][1]['secret_key']

# try:
#     account = stripe.Account.retrieve()
#     print("Connected to Stripe!")
#     print("Account ID:", account.id)
# except stripe.error.StripeError as e:
#     print(f"Stripe error: {e.user_message}")
# except Exception as e:
#     print(f"Unexpected error: {e}")
