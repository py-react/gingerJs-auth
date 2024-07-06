from authlib.integrations.flask_client import OAuth
from flask import request,abort,url_for,session,redirect,current_app


def Google_Provider():
    # Configure the Google provider
    def func(oauth):
        if "google" not in oauth._clients:
            oauth.register(
                name='google',
                server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
                client_kwargs={
                    'scope': 'openid email profile'
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

def Auth(auth_options):
    app = current_app
    if not auth_options:
        raise ValueError("No Auth Option Provided")
    
    oauth = OAuth(app)
    if not auth_options["providers"]:
        raise ValueError("providers not provided in auth_options")
    
    for provider in auth_options["providers"]:
        if provider['type'] != "credentials":
            provider["func"](oauth)

    
    def login(name):
        if request.args.get("next_url"):
            session['next_url'] = request.args.get("next_url")
        if name == "credentials":
            data = request.get_json()
            user = None
            for credFlow in auth_options["providers"]:
                if credFlow["type"] == name:
                    user = credFlow['func'](data)
                    break
            
            session['user'] = user
            request.session_user = session['user']
            return redirect(session['next_url'])
            
        client = oauth.create_client(name)
        if not client:
            abort(404)
        redirect_uri = url_for('auth', name=name, _external=True)
        
        return client.authorize_redirect(redirect_uri)

    def auth(name):
        if(name != "credentials"):
            client = oauth.create_client(name)
            if not client:
                abort(404)

            token = client.authorize_access_token()
            user = token.get('userinfo')
            if not user:
                user = client.userinfo()
            session['user'] = user
        request.session_user = session['user']
        return redirect(session['next_url'])

    def logout():
        session.pop('user', None)
        return redirect('/')
    
    def authMiddleware():
        user = session.get('user')
        if "protected_routes" in auth_options:
            for route in auth_options['protected_routes']:
                # TODO: better match logic
                if not user and request.path.startswith(route):
                    session['next_url'] = request.base_url
                    if "login_page" in  auth_options:
                        return redirect(auth_options["login_page"]+"?next_url="+request.base_url)
                    return redirect(f"/login?next_url={request.base_url}")
                
    app.before_request(authMiddleware)
    app.add_url_rule("/oAuth/<name>",view_func=login,methods=['GET',"POST"])
    app.add_url_rule("/auth/<name>",view_func=auth)
    app.add_url_rule("/logout",view_func=logout)
    return oauth