import os
import requests
from requests.auth import AuthBase
from urllib.parse import quote
from flask_restful import abort

class BitbucketAuth(AuthBase):
  """Authentication for Bitbucket External API"""

  def __init__(self):
    self.bearer_token_url = "https://bitbucket.org/site/oauth2/access_token"
    self.consumer_key = os.getenv('BITBUCKET_CLIENT_ID')
    self.consumer_secret = os.getenv('BITBUCKET_CLIENT_SECRET')
    self.bearer_token = self.get_bearer_token()

  def get_bearer_token(self):
    """Get Bearer token for authentication

    Raises:
        Exception: If unnable to get bearer token

    Returns:
        [str]: Bearer token for request headers.
    """
    response = requests.post(
      self.bearer_token_url, 
      data={'grant_type': 'client_credentials'},
      auth=(self.consumer_key, self.consumer_secret)
      )

    if response.status_code is not 200:
      raise Exception(f"Cannot get a Bearer token (HTTP {response.status_code}): {response.reason}")

    body = response.json()
    return body['access_token']

  def __call__(self, r):
    r.headers['Authorization'] = f"Bearer {self.bearer_token}" 
    return r

class ExternalAPI(object):
  """External API Base Class"""

  def __init__(self, api:str, auth=None):
    """Initialize External API. Must incluse base api url. If no auth is given, no authentication will be done.

      Args:
          api (str): Base api URL
          auth (requests.auth.AuthBase, optional): Auth used for API. Defaults to None.
    """
    self.api = api
    self.auth = auth

  def get(self, endpoint:str):
    """Get an endpoint

    Args:
        endpoint (str): endpoint past base api url

    Returns:
        [requests.Response]: response object
    """
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    response = requests.get(self.api + endpoint, auth=self.auth)
    return response
      
Bitbucket = ExternalAPI('https://api.bitbucket.org/2.0', BitbucketAuth())
Github = ExternalAPI('https://api.github.com')