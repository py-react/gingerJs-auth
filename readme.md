<h1 align="center">Ginger-Auth</h1>

Auth Helper for gingerJs


## Usage
First Import 
```python
from ginger_auth.auth import Google_Provider,Auth,Credentials_Provider,Github_Provider
```

Creeate a settings.py file in the root
```python
GOOGLE_CLIENT_ID = ""
GOOGLE_CLIENT_SECRET = ""

GITHUB_CLIENT_ID = ""
GITHUB_CLIENT_SECRET = ""
```

Then, in your main.py file, add the following lines:
```python
app.config.from_object('settings')

def login(payload):
    print(payload,"payload")
    return payload

with app.app_context():
    auth_options = {
            'providers': [
                Google_Provider(),
                # Github_Provider(),
                # Credentials_Provider(login)
                # ...add more providers here
            ],
            "login_page":"/login",
            "protected_routes":["/dashboard"]
        }
    Auth(auth_options)
```

## Auth Options
### "providers"
#### Google_Provider 
When using Google_Provider, upon successful login, the user object will be accessible in the routes via request.session_user.

#### Github_Provider 
When using Github_Provider, upon successful login, the user object will be accessible in the routes via request.session_user.

#### Credentials_Provider
When using Credentials_Provider, the provided function should return a user object, which will then be accessible in the routes via request.session_user.

### "login_page"
This is the page where the user will be redirected if they are not already logged in and attempt to access restricted routes.

### "protected_routes"
This is a list of routes that will require the user to log in first. Note that specifying "/dashboard" will restrict all nested routes as well.

## Login hook
Create a login hook inside src/libs/useLogin.jsx

```jsx
import {useEffect,useState} from "react"
import useNavigate from 'src/libs/navigate';
import { useSearchParams } from 'react-router-dom';

export const useLogin = ()=>{
    const navigate = useNavigate()
    const [searchParams] = useSearchParams();
    const [nextUrl, setNextUrl] = useState("/")
  
    function sendPostRequest(url,body) {
      var xhr = new XMLHttpRequest();
      xhr.open("POST", url, true);
      xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    
      xhr.onreadystatechange = function () {
          if (xhr.readyState === 4) {
              if (xhr.status === 200) {
                if (xhr.responseURL !== window.location.href) {
                  navigate(xhr.responseURL)
                } else {
                  navigate("/")
                }
              } else {
                  console.error('Error: ' + xhr.status);
              }
          }
      };
    
      var data = JSON.stringify(body);
      xhr.send(data);
    }
    useEffect(()=>{
      setNextUrl(searchParams.get("next_url")||"/")
    },[searchParams])
  
    const loginHook = (loginType,payload)=>{
      if (loginType === "credentials"){
        sendPostRequest("/oAuth/credentials",payload)
      }else{
        const aTag = document.createElement("a")
        if(loginType === "google"){
          aTag.href = `/oAuth/google?next_url=${nextUrl}` 
        }
        if(loginType === "github"){
          aTag.href = `/oAuth/github?next_url=${nextUrl}` 
        }
        aTag.click()
      }
    }
  
   return [loginHook]
  
  }

export default useLogin
```

## Hook Usage
Inside the component
```jsx
import React from "react";
import useLogin from "src/lib/useLogin"

function LoginPage(){
  const [loginUser] = useLogin()

  const onSubmit = ({email,password})=>{
    loginUser("credentials",{email,password})
    // loginUser("google")
    // loginUser("github")
  }

  // LoginPage content
  return (
    <div>
      {/* Login form */}
    </div>
  )
}
```
