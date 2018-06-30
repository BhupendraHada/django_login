from __future__ import unicode_literals

from random import randint
import requests

from publishers.otp import OTPPublisher


def get_random_key():
    return randint(1000, 9999)


def call_publisher(routing_key, contact_number, key):
    data = {
        'contact_number': contact_number,
        'key': key
    }
    #publisher = OTPPublisher(routing_key=routing_key)
    message_url = "http://enterprise.smsgupshup.com/GatewayAPI/rest?method=SendMessage&send_to=" + str(contact_number) + "&msg=" + "Hi, Your verification OTP is " + str(key) + "&msg_type=text&userid=2000145635&auth_scheme=plain&password=g8aaTK7So&v=1.1&format=text"
    response = requests.get(message_url)
    #publisher.publish(data)
