# Social Setup

## Flickr

  https://github.com/alexis-mignon/python-flickr-api/wiki/Flickr-API-Keys-and-Authentication
  https://www.flickr.com/services/apps/72157687526251076/

```
docker exec -it duckiehunt python

api_key=''
api_secret=''
filename='/code/duckiehunt/secrets/flickr.auth'

import flickr_api
flickr_api.set_keys(api_key=api_key, api_secret=api_secret)
a = flickr_api.auth.AuthHandler()
perms = 'write'
url = a.get_authorization_url(perms)
print(url)
a.set_verifier('<VERIFIER CODE>')
flickr_api.set_auth_handler(a)
a.save(filename)
```

## Google login

  https://console.cloud.google.com/apis/credentials?project=noble-nation-174502&supportedpurview=project