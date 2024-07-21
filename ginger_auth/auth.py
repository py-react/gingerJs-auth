from authlib.integrations.starlette_client import OAuth
from fastapi import Request,FastAPI
from fastapi.routing import APIRoute
from starlette.status import HTTP_403_FORBIDDEN
from fastapi.responses import RedirectResponse
from starlette.config import Config
from starlette.middleware.base import BaseHTTPMiddleware
from gingerjs.create_app.routes.flask.middleware import match_static_to_dynamic



def Create_Auth_middleware_Class(auth_options):

    class AuthMiddleware(BaseHTTPMiddleware):
        def __init__(self, app: FastAPI):
            super().__init__(app)

        async def dispatch(self, request, call_next):
            protected_routes = auth_options.get('protected_routes', [])
            login_page = auth_options.get('login_page', '/login')
            # Check if the request path needs authentication
            if any(match_static_to_dynamic(request.url.path,route) for route in protected_routes):
                if "user" not in  request.session:
                    request.session['next_url'] = str(request.url.path)
                    return RedirectResponse(f"{login_page}?next_url={str(request.url.path)}")

            response = await call_next(request)
            return response
    return AuthMiddleware


def Google_Provider():
    # Configure the Google provider
    def func(oauth):
        if "google" not in oauth._clients:
            oauth.register(
                name='google',
                server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
                client_kwargs={
                    'scope': 'openid email profile',
                    'prompt': 'select_account',  # force to select account
                }
            )
    return  {"type":"google","func":func}

def Github_Provider():
    def func(oauth):
        # Configure the Google provider
        if "github" not in oauth._clients:
            oauth.register(
                name='github',
                api_base_url='https://api.github.com/',
                client_kwargs={
                    'scope': 'user:openid,email,profile'
                },
                access_token_url = 'https://github.com/login/oauth/access_token',
                authorize_url='https://github.com/login/oauth/authorize',
                userinfo_endpoint= 'https://api.github.com/user',
            )
    return  {"type":"github","func":func}

def Credentials_Provider(paasedFunc):
    def func(*args, **kwargs):
        return paasedFunc(*args, **kwargs)
    return {"type":"credentials","func":func}

def Auth(auth_options,app):
    if not auth_options:
        raise ValueError("No Auth Option Provided")
    config = Config(".env")
    oauth = OAuth(config)
    if not auth_options["providers"]:
        raise ValueError("providers not provided in auth_options")
    
    for provider in auth_options["providers"]:
        if provider['type'] != "credentials":
            provider["func"](oauth)

    
    async def login(request:Request,name,next_url):
        if next_url:
            request.session['next_url'] = next_url
        if name == "credentials":
            data = await request.json()
            user = None
            for credFlow in auth_options["providers"]:
                if credFlow["type"] == name:
                    user = credFlow['func'](data)
            
            request.session['user'] = user
            request.session_user = request.session['user']
            return RedirectResponse(request.session['next_url'])
            
        client = oauth.create_client(name)
        if not client:
            raise HTTP_403_FORBIDDEN(404)
        # Get the host (domain) and port
        host = request.url.hostname
        port = request.url.port
        
        # Get the protocol (http or https)
        protocol = request.url.scheme
        redirect_uri = f"{protocol}://{host}:{port}/auth/{name}"
        return await client.authorize_redirect(request,redirect_uri)

    async def auth(request:Request,name):
        if(name != "credentials"):
            client = oauth.create_client(name)
            if not client:
                raise HTTP_403_FORBIDDEN(404)

            token = await client.authorize_access_token(request)
            user = token.get('userinfo')
            if not user:
                user = client.userinfo()
            request.session['user'] = user
        request.session_user = request.session['user']
        return RedirectResponse(request.session['next_url'])

    def logout(request:Request):
        request.session.pop('user', None)
        return RedirectResponse('/')
    
    app.add_middleware(Create_Auth_middleware_Class(auth_options))
    oAuthRoute =APIRoute(
        path= "/oAuth/{name}",
        endpoint=login,
        methods=['GET',"POST"],
        name="oAuth",
    )
    app.router.routes.append(oAuthRoute)
    authRoute =APIRoute(
        path= "/auth/{name}",
        endpoint=auth,
        methods=['GET',"POST"],
        name="auth",
    )
    app.router.routes.append(authRoute)
    logoutRoute =APIRoute(
        path= "/logout",
        endpoint=logout,
        methods=['GET',"POST"],
        name="logout",
    )
    app.router.routes.append(logoutRoute)
    
    return oauth