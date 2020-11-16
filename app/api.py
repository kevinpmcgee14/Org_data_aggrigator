import requests
import flask
from flask import Flask, request, Response
from flask_restful import Api, Resource, abort
from .external import Bitbucket as bb_api, Github as gh_api
from .helpers import bb_parse_results, gh_parse_results, total_parse_results

app = Flask(__name__)
api = Api(app)

class HealthCheck(Resource):

    def get(self):
        """Endpoint to Health Check API

        Returns:
            [dict]: Positive Health Check
        """
        return {"response": "All Good!"}

api.add_resource(HealthCheck, '/health')

class GitHub(Resource):

    def get(self, organization:str):
        """Endpoint to get GitHub Repo data for an Organization

        Args:
            organization (str): Name of Organization

        Returns:
            [dict]: Final parsed data
        """
        response = gh_api.get(f'/orgs/{organization}/repos')
        final_resp = gh_parse_results(response, organization)
        return final_resp
        
api.add_resource(GitHub, '/github/<organization>/')


class Bitbucket(Resource):

    def get(self, organization):
        """Endpoint to get Bitbucket Repo data for an Organization

        Args:
            organization (str): Name of Organization

        Returns:
            [dict]: Final parsed data
        """
        response = bb_api.get(f'/repositories/{organization}')
        final_resp = bb_parse_results(response, organization)
        return final_resp 
              
api.add_resource(Bitbucket, '/bitbucket/<organization>/')


class Merged(Resource):

    def get(self):
        """Endpoint to get Merged GitHub and Bitbucket data for an Organization.
            Requires either an ?org= parameter (org has same name in both), or ?bitbucket=x&gihub=y parameters (org has different names in both).

        Returns:
            [dict]: Final parsed data
        """
        organization, bb_name, gh_name = request.args.get('org'), request.args.get('bitbucket'), request.args.get('github')
        if organization:
            gh_response = gh_api.get(f'/orgs/{organization}/repos')
            bb_response = bb_api.get(f'/repositories/{organization}')
        elif all([bb_name, gh_name]):
            gh_response = gh_api.get(f'/orgs/{gh_name}/repos')
            bb_response = bb_api.get(f'/repositories/{bb_name}')
        else:
            abort(400, message='Either an ?org= parameter is required, or ?bitbucket=x&gihub=y query parameters are required')
        final_resp = {}
        final_resp['GitHub'] = gh_parse_results(gh_response, organization)
        final_resp['Bitbucket'] = bb_parse_results(bb_response, organization)
        final_resp['Merged Totals'] = total_parse_results(final_resp)
        final_resp = {k: final_resp[k] for k in ["Merged Totals", "GitHub", "Bitbucket"]}
        return final_resp
        
api.add_resource(Merged, '/merged/')