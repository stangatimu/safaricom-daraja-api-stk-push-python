from flask import Flask
from flask_restful import Api, Resource, reqparse
import datetime
import requests
from requests.auth import HTTPBasicAuth
import base64
import json


def get_mpesa_token():

    consumer_key = "YOUR_APP_CONSUMER_KEY"
    consumer_secret = "YOUR_APP_CONSUMER_SECRET"
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

    return r.json()['access_token']



app = Flask(__name__)

api = Api(app)

class MakeSTKPush(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('phone',
            type=str,
            required=True,
            help="This fied is required")

    parser.add_argument('amount',
            type=str,
            required=True,
            help="this fied is required")

    def post(self):

        """ make and stk push to daraja API"""

        x = datetime.datetime.now()
        encode_data = b"<Business_shortcode><online_passkey><current timestamp>"
        # timestamp format: 20190317202903 yyyyMMhhmmss  

        passkey  = base64.b64encode(encode_data)

        try:

            access_token = get_mpesa_token()

            api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

            headers = { "Authorization": f"Bearer {access_token}" ,"Content-Type": "application/json" }
            data = MakeSTKPush.parser.parse_args()
            request = {
                "BusinessShortCode": "<business_shortCode>",
                "Password": str(passkey)[2:-1],
                "Timestamp": "<timeStamp>",
                "TransactionType": "CustomerPayBillOnline",
                "Amount": data['amount'],
                "PartyA": data['phone'],
                "PartyB": "<business_shortCode>",
                "PhoneNumber": data['phone'],
                "CallBackURL": "<YOUR_CALLBACK_URL>",
                "AccountReference": "UNIQUE_REFERENCE",
                "TransactionDesc": ""
            }

            response = requests.post(api_url,json=request,headers=headers)

            if response.status_code > 299:
                return{
                    "success": False,
                    "message":"Sorry, something went wrong please try again later."
                },400

            return {
                "data": json.loads(response.text)
            },200

        except:

            return {
                "success":False,
                "message":"Sorry something went wrong please try again."
            },400


api.add_resource(MakeSTKPush,"/stkpush")

if __name__ == "__main__":
    
    app.run(port=5000,debug=True)
        