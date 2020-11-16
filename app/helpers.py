import requests 
import time
import asyncio
import aiohttp
from flask_restful import abort

def validate_response(response: requests.Response, org_name: str, site=''):
    """Validate Response object before parsing data

    Args:
        response (requests.Response): the response returned from external APIs
        org_name (str): The name of the organization.
        site (str, optional): The name of the external API. Defaults to ''.
    """
    if response.status_code == 200:
        return
    elif response.status_code == 404:
        abort(404, message=f'The organization {org_name} does not exist on {site}')
    else:
        abort(response.status_code, message=response.reason)

def drop_null(ls: list):
    """Remove null values from final response, if present

    Args:
        ls (list): values in final response object

    Returns:
        [list]: final response object with null values removed
    """
    try:
        ls.remove(None)
    except ValueError:
        pass
    return ls

async def bb_parse_repo(repo: dict):
    """Parse a Repos data. 
    Asynchronous calls to are made Bitbucket Watchers and Forks reference urls to speed up parsing.

    Args:
        repo (dict): A repo within an Orgnaization's workspace

    Returns:
        [dict]: Parsed repo data for final response
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(repo['links']['watchers']['href']) as response:
            resp = await response.json()
            watchers = resp['size']
        async with session.get(repo['links']['forks']['href']) as response:
            resp = await response.json()
            forks = resp['size']
        rep = {
            'watchers': watchers,
            'forks': forks,
            'name': repo['name'],
            'language': repo['language'],
            'topic': repo['description']
        }
        return rep

async def bb_parse_all_repos(repos: list):
    """Asynchronous call to parse all Repos. 
    This is done to run reference urls for Watchers and Forks concurrently to speed up calls.

    Args:
        repos (list): List of repositories(dicts) to parse

    Returns:
        [list]: list of parsed repository dicts for final response
    """
    try:
        ret = await asyncio.gather(*[bb_parse_repo(repo) for repo in repos])
    except:
        time.sleep(2)
        ret = await asyncio.gather(*[bb_parse_repo(repo) for repo in repos])
    return ret

def bb_parse_results(response: requests.Response, org_name: str):
    """Main Bitbucket parsing function. Takes advantage of asynchronous calls to speed up parsing.

    Args:
        response (requests.Response): response object from Bitbucket External API
        org_name (str): Name of the organization

    Returns:
        [dict]: Final Response object, including repo level and org level data.
    """
    validate_response(response, org_name, site='Bitbucket')
    results = response.json()
    final_resp = {}
    final_resp['repos'] = asyncio.run(bb_parse_all_repos(results['values']))
    final_resp['repo_count'] = len(final_resp['repos'])
    final_resp['languages'] = drop_null(list(set([repo['language'] for repo in final_resp['repos']])))
    final_resp['fork_count'] = sum([repo['forks'] for repo in final_resp['repos']])
    final_resp['watcher_count'] = sum([repo['watchers'] for repo in final_resp['repos']])
    return final_resp

def gh_parse_results(response: requests.Response, org_name:str):
    """Main GitHub parsing function.

    Args:
        response (requests.Response): response object from GitHub External API
        org_name (str): Name of the organization

    Returns:
        [dict]: Final Response object, including repo level and org level data.
    """
    validate_response(response, org_name, site='Github')
    results = response.json()
    final_resp = {}
    final_resp['repos'] = []
    for repo in results:
        rep = {
            'watchers': repo['watchers_count'],
            'forks': repo['forks_count'],
            'name': repo['name'],
            'language': repo['language'],
            'topic': repo['description']
        }
        final_resp['repos'].append(rep)
    final_resp['repo_count'] = len(final_resp['repos'])
    final_resp['languages'] = drop_null(list(set([repo['language'] for repo in final_resp['repos']])))
    final_resp['fork_count'] = sum([repo['forks'] for repo in final_resp['repos']])
    final_resp['watcher_count'] = sum([repo['watchers'] for repo in final_resp['repos']])
    return final_resp

def total_parse_results(final_resp: list):
    """Combine Bitbucket and GitHub Data

    Args:
        final_resp (list): list of GitHub and Bitbucket parsed data, including repo level and org level data.

    Returns:
        [dict]: Total aggregated data.
    """
    total_resp = {
        "total_repos": final_resp["GitHub"]["repo_count"] + final_resp["Bitbucket"]["repo_count"],
        "languages": final_resp["GitHub"]["languages"] + final_resp["Bitbucket"]["languages"],
        "total_forks": final_resp["GitHub"]["fork_count"] + final_resp["Bitbucket"]["fork_count"],
        "total_watchers": final_resp["GitHub"]["watcher_count"] + final_resp["Bitbucket"]["watcher_count"]
    }
    return total_resp