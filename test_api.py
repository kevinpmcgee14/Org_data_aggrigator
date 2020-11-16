import requests
import pytest

base_url = 'http://127.0.0.1:5000'

class State:
    def __init__(self):
        self.org = 'mailchimp'

@pytest.fixture(scope='session')
def state() -> State:
    state = State()
    return state


def get_github(organization):
    response = requests.get(url=f'{base_url}/github/{organization}/')
    return response


def get_bitbucket(organization):
    response = requests.get(url=f'{base_url}/bitbucket/{organization}/')
    return response


def get_merged(qparams):
    response = requests.get(url=f'{base_url}/merged/{qparams}')
    return response


def test_00_get_github(state: State):
    response = get_github(state.org)
    assert response.status_code == 200

def test_01_get_bitbucket(state: State):
    response = get_bitbucket(state.org)
    assert response.status_code == 200


def test_02_merged(state: State):
    response = get_merged(f'?org={state.org}')
    print(response.reason)
    assert response.status_code == 200
    response = get_merged(f'?github={state.org}&bitbucket={state.org}')
    assert response.status_code == 200