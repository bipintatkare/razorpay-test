from django.shortcuts import render, redirect
import razorpay
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, 'index.html')


def payment(request):
    try:
        '''
        To make payment, 
        first you have to create a razorpay client to communicate with API
        '''
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))
        if request.method == "POST":

            amount = request.POST.get('payment-amount')

            '''
            Order is the object which razorpay creates to 
            Hold the status of payment for verification becuase
            The payment involves third party integrations also ...

            If you are making payments with INR currency, then you have to 
            Multiply amount with 100. 
            '''
            order = client.order.create(
                dict(amount=int(amount)*100,
                currency="INR",
                payment_capture='0')
            )

            print(f"{request.get_host()=}")
            return render(request, "verify.html", {
                "order_id": order['id'],
                "amount": order['amount'],
                "host_url": request.get_host(),
                "merchant_key": settings.RAZORPAY_KEY,
                "callback_url": "verify/",
                "currency": "INR"
            })

    except Exception as ep:
        print(f"{ep=}")
        return redirect('index')


@csrf_exempt
def paymenthandler(request):
 
    # only accept POST request.
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))
    if request.method == "POST":
        try:
           
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                amount = 20000  # Rs. 200
                try:
 
                    # capture the payemt
                    client.payment.capture(payment_id, amount)
 
                    # render success page on successful caputre of payment
                    return redirect("index")
                except Exception as ep:
                    print(f"{ep=}")
                    # if there is an error while capturing payment.
                    return redirect("index")
            else:
 
                # if signature verification fails.
                print("sign failed")
                return redirect("index")
        except:
 
            # if we don't find the required parameters in POST data
            return HttpResponse("bad")
    else:
       # if other than POST request is made.
        return HttpResponse("bad")