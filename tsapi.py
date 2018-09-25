
import os
from flask_restful import Resource, Api, reqparse
from model.history_query import History
from model.datapoints_query import Datapoints
from model.jwt_validation_decorator import AuthError
from model.put_tokens import Tokens
import json
from six.moves.urllib.request import urlopen
from functools import wraps

from flask import Flask, request, jsonify, _request_ctx_stack, abort
from jose import jwt

app = Flask(__name__)

AUTH0_DOMAIN = 'ts-api.auth0.com'
API_AUDIENCE = 'https://github.com/QuietStormToday/tsapi'
ALGORITHMS = ["RS256"]

site_name_to_id = {}
site_name_to_id['WB3090'] = 248
site_name_to_id['XI5016'] = 252
site_name_to_id['XI2004'] = 265
site_name_to_id['XR2099'] = 295
site_name_to_id['XP2690'] = 311
site_name_to_id['AZ2290'] = 329

site_name_to_user_id = {}
site_name_to_user_id['WB3090'] = 'auth0|5b85bfc7ad451875aad65e65'
site_name_to_user_id['XI5016'] = 'auth0|5b85bfc7ad451875aad65e65'
site_name_to_user_id['XI2004'] = 'auth0|5b85bfc7ad451875aad65e65'
site_name_to_user_id['XR2099'] = 'auth0|5b85bfc7ad451875aad65e65'
site_name_to_user_id['XP2690'] = 'auth0|5b85bfc7ad451875aad65e65'
site_name_to_user_id['AZ2290'] = 'auth0|5b85bfc7ad451875aad65e65'

apiUsers = {}
apiUsers['auth0|5b85bfc7ad451875aad65e65'] = 'Hal Wilkinson'
apiUsers['auth0|5baa5750dcd689216002c0a5'] = 'Jack Sprat'


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token

def requires_auth(f):

    #Determines if the Access Token is valid
    @wraps(f)
    def decorated(*args, **kwargs):

        token = get_token_auth_header()
        jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer="https://"+AUTH0_DOMAIN+"/"
                )

                #currentUser = payload['sub']
                #print('**** auth0 user id is: ' + currentUser)

            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    "please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    return decorated


def getUser():

    print( 'getting user...' )

    token = get_token_auth_header()
    jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer="https://"+AUTH0_DOMAIN+"/"
            )

            currentUser = payload['sub']
            print('**** auth0 user id is: ' + currentUser)
            return currentUser

        except:
            print 'oops'
            pass

    return '???'

@app.route("/oauth/token", methods=['POST'])
def getToken():

    un = request.form.get("username")
    pw = request.form.get("password")

    token_query = Tokens(AUTH0_DOMAIN, un, pw)
    data = token_query.putToken()

    json = jsonify(data)
    return json


@app.route("/datapoints")
@requires_auth
def getDatapoints():

    print 'inside getDatapoints route'
    print '...and the user is: ' + apiUsers[getUser()]

    parser = reqparse.RequestParser()
    parser.add_argument('site_name', type=str, help='Cannot parse site_name')
    args = parser.parse_args()
    site_name = args['site_name']

    currentUser = getUser()
    if currentUser == site_name_to_user_id[ site_name ]:

        dp_query = Datapoints(e3os_host, e3os_username, e3os_password)
        data = dp_query.getDatapoints( site_name_to_id[site_name])

        json = jsonify(data)
        return json

    else:
        abort(404)


@app.route("/history")
@requires_auth
def getHistory():

    parser = reqparse.RequestParser()
    parser.add_argument('site_name', type=str, help='Cannot parse site_name')
    parser.add_argument('start_date', type=str, help='Cannot parse start_date')
    parser.add_argument('end_date', type=str, help='Cannot parse end_date')
    parser.add_argument('datapoints', action='split', help='Cannot parse datapoints')
    args = parser.parse_args()

    site_name = args["site_name"]

    currentUser = getUser()
    if currentUser == site_name_to_user_id[ site_name ]:

        start_date = args["start_date"]
        end_date = args["end_date"]
        cds = args["datapoints"]
        datapoints = cds.split(",")

        site_name_to_prefix = {}
        site_name_to_prefix['WB3090']= 'ATT.WB3090.WB3090LP.WB3090LP'
        site_name_to_prefix['XI5016']='ATT.XI5016.XI5016LP.XI5016LP'
        site_name_to_prefix['XI2004']='ATT.XI2004.XI2004LP.X124LP1'
        site_name_to_prefix['XR2099']='ATT.XR2099.XR2099LP1.XR2099'
        site_name_to_prefix['XP2690']='ATT.XP2690.XP2690LP1.XP2690'
        site_name_to_prefix['AZ2290']='ATT.AZ2290.AZ2290LP.AZ2290LP'

        prefix = site_name_to_prefix[ site_name ]

        cache_time = '2018-07-31'

        history_querier = History(e3os_host, e3os_username, e3os_password)

        data = history_querier.get_history(cache_time, start_date, end_date, prefix, datapoints)
        json = jsonify(data)
        return json

    else:
        abort(404)


@app.route("/example")
def getExample():

    prefix = 'ATT.WB3090.WB3090LP.WB3090LP'
    point_names = ["kW Delta"
            "kW/Ton Delta",
            "kWh",
            "kWh Delta",
            "OldkW",
            "OldkW/Ton",
            "OldkWh",
            "ProjkW",
            "ProjkW/Ton",
            "ProjkWh",
            "TonHours"]

    cache_time = '2018-07-31'
    from_time ='2018-03-01'
    to_time = '2018-03-02'

    history_querier = History(e3os_host, e3os_username, e3os_password)

    data = history_querier.get_history(cache_time, from_time, to_time, prefix, point_names)
    json = jsonify(data)
    return json

if __name__ == '__main__':

    e3os_host = os.environ['E3OS_HOST']
    e3os_username = os.environ['E3OS_USER']
    e3os_password = os.environ['E3OS_PASSWORD']

    print(e3os_host)
    print(e3os_username)
    print(e3os_password)

    app.run(port='5002', debug=True)