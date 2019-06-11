from flask import Flask
from flask_restful import Api, Resource, reqparse
import datetime
import requests
from requests.auth import HTTPBasicAuth
import base64
import json

# get Oauth token from M-pesa [function]
def get_mpesa_token():

    consumer_key = "YOUR_APP_CONSUMER_KEY"
    consumer_secret = "YOUR_APP_CONSUMER_SECRET"
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    # make a get request using python requests liblary
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    # return access_token from response
    return r.json()['access_token']


# initialize a flask app
app = Flask(__name__)

# intialize a flask-restful api
api = Api(app)

class MakeSTKPush(Resource):

    # get 'phone' and 'amount' from request body
    parser = reqparse.RequestParser()
    parser.add_argument('phone',
            type=str,
            required=True,
            help="This fied is required")

    parser.add_argument('amount',
            type=str,
            required=True,
            help="this fied is required")

    # make stkPush method
    def post(self):

        """ make and stk push to daraja API"""

        encode_data = b"<Business_shortcode><online_passkey><current timestamp>" 

        # encode business_shortcode, online_passkey and current_time (yyyyMMhhmmss) to base64
        passkey  = base64.b64encode(encode_data)

        # make stk push
        try:

            # get access_token
            access_token = get_mpesa_token()

            # stk_push request url
            api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

            # put access_token in request headers
            headers = { "Authorization": f"Bearer {access_token}" ,"Content-Type": "application/json" }

            # get phone and amount
            data = MakeSTKPush.parser.parse_args()

            # define request body
            request = {
                "BusinessShortCode": "<business_shortCode>",
                "Password": str(passkey)[2:-1],
                "Timestamp": "<timeStamp>", # timestamp format: 20190317202903 yyyyMMhhmmss 
                "TransactionType": "CustomerPayBillOnline",
                "Amount": data['amount'],
                "PartyA": data['phone'],
                "PartyB": "<business_shortCode>",
                "PhoneNumber": data['phone'],
                "CallBackURL": "<YOUR_CALLBACK_URL>",
                "AccountReference": "UNIQUE_REFERENCE",
                "TransactionDesc": ""
            }

            # make request and catch response
            response = requests.post(api_url,json=request,headers=headers)

            # check response code for errors and return response
            if response.status_code > 299:
                return{
                    "success": False,
                    "message":"Sorry, something went wrong please try again later."
                },400

            # if success return response
            return {
                "data": json.loads(response.text)
            },200

        except:
            # catch error and return respones

            return {
                "success":False,
                "message":"Sorry something went wrong please try again."
            },400


# stk push path [POST request to {baseURL}/stkpush]
api.add_resource(MakeSTKPush,"/stkpush")

if __name__ == "__main__":
    
    app.run(port=5000,debug=True)
        