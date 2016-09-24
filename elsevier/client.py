import requests

from exceptions import ElsevierException
import re


class ElsevierClient(object):
    methods = {
        'search_scopus': '/search/scopus',
        'search_science_direct': '/search/scidir',
        'retrieve_abstract': '/abstract/{id_type}/{id}'
    }

    def __init__(self,
                 api_key,
                 host='http://api.elsevier.com/content'):
        self.api_key = api_key
        self.host = host

    def _request(self, endpoint, params, requestType='GET'):
        response = None
        if self.api_key is not None:
            url = u'{0}{1}'.format(self.host, endpoint)
            params['apiKey'] = self.api_key
            if requestType == 'POST':
                response = requests.post(url, params)
            else:
                response = requests.get(url, params)
        else:
            raise ElsevierException('No API Key.')
        print 'response type: ' + response.headers['content-type']
        return self._parse_response(response)

    def _parse_response(self, response):
        if response.status_code == 200:
            content_type = response.headers['content-type']
            if content_type.startswith('application/json'):
                return response.json()
            else:
                raise ElsevierException('content-type ' +
                    content_type + ' not yet supported') 
        elif response.status_code == 429:
            raise ElsevierException('Quota Exceeded.')
    
    def _api_method(self, endpoint):
        def method(**kwargs):
            endpoint_format_kwargs = re.findall('{([\w_]+)}', endpoint)
            formatted_endpoint = endpoint.format(**kwargs)
            for kwarg in endpoint_format_kwargs:
                kwargs.pop(kwarg, None)
            return self._request(formatted_endpoint, kwargs)
        return method

    def __getattr__(self, name):
        return self._api_method(ElsevierClient.methods[name])

