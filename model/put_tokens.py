#import httplib, urllib
import requests
import json

class Tokens:

    def __init__(self, auth0_domain, username, password):
        self.auth0_domain = auth0_domain
        self.username = username
        self.password = password
        self.grantType = "password"
        self.audience = "https://github.com/QuietStormToday/tsapi"
        self.clientId = 'CmQ35yD5uXnChds6xExcmJjfAo2YGsG8'
        self.clientSecret = '6kj8DUcfeXw7fFOELuqEN_pCAXFcEksEhkEFbmzg7QKaqCF0v__wQ4IOeiWQyJ5i'

    def putToken(self):
        url = 'https://' + self.auth0_domain + '/oauth/token'

        payload = {
            "grant_type": self.grantType,
            "username": self.username,
            "password": self.password,
            "audience": self.audience,
            #"scope": "SCOPE",
            "client_id": self.clientId,
            "client_secret": self.clientSecret
        }
        response = requests.post(url, data=payload)
        json_data = json.loads(response.text)

        return json_data



