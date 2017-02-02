import requests
import xmltodict
from .exceptions import ElsevierException
import re


class ElsevierClient(object):

    methods = {'search_scopus': '/search/scopus',
        'search_science_direct': '/search/scidir',
        'retrieve_abstract': '/abstract/{id_type}/{id}',
        'retrieve_object_refs': '/object/{id_type}/{id}',
        'retrieve_object': '/object/{id_type}/{id}/ref/{ref}',
        'retrieve_image': '/object/{id_type}/{id}/ref/{ref}/{img_type}',
        'retrieve_article': '/article/{id_type}/{id}'
        }

    def __init__(self, api_key, host='http://api.elsevier.com/content'):
        self.api_key = api_key
        self.host = host

    def _request(self, endpoint, params, requestType='GET'):
        response = None
        if self.api_key is not None:
            url = '{0}{1}'.format(self.host, endpoint)
            params['apiKey'] = self.api_key
            if requestType == 'POST':
                response = requests.post(url, params)
            else:
                response = requests.get(url, params)
        else:
            raise ElsevierException('No API Key.')
        return self._parse_response(response)

    def _parse_response(self, response):
        content_type = response.headers['content-type'].split(';')[0]
        if response.status_code == 200:
            if content_type == 'application/json':
                return response.json()
            elif content_type == 'text/xml':
                return xmltodict.parse(response.content)
            else:
                raise ElsevierException(
                    'content type ' + content_type + ' not yet supported.')

        elif response.status_code == 429:
            raise ElsevierException('Quota Exceeded.')

        elif response.status_code == 403:
            if content_type == 'text/xml':
                parsed_error = xmltodict.parse(response.content)
                parsed_error = parsed_error['service-error']['status']
                raise ElsevierException(parsed_error['statusCode'] + ': ' +
                                        parsed_error['statusText'])
        else:
            raise ElsevierException('Response code: ' + str(response.status_code))

    def _api_method(self, endpoint):
        """Given and endpoint, creates a function that takes as named parameters
        the variables inside curly braces '{variable_name}'. Such named paramenters
        are used to format such URL. The function makes a call to such URL with extra
        parameters given by the user.
        """
        def method(**kwargs):
            endpoint_format_kwargs = re.findall('{([\w_]+)}', endpoint)
            formatted_endpoint = endpoint.format(**kwargs)
            for kwarg in endpoint_format_kwargs:
                kwargs.pop(kwarg, None) # remove keyword arguments used
            return self._request(formatted_endpoint, kwargs)
        return method

    def __getattr__(self, name):
        return self._api_method(ElsevierClient.methods[name])

