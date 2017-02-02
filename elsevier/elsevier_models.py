from elsevier.client import ElsevierException
import warnings

# There is a maximum number of results returned by the server
max_results = 5950

class ScienceDirectSearch(object):
    """An iterable that stores the parameters for a ScienceDirect
    Search. Returns the data for each article in the search results.
    """
    def __init__(self, client, **kwargs):
        self.client = client
        self.params = kwargs
        self.page = client.search_science_direct(**kwargs)['search-results']
        self.total_results = int(self.page['opensearch:totalResults'])
        self.page_length = int(self.page['opensearch:itemsPerPage'])
        self.start = self.page['opensearch:startIndex']
        if self.total_results > max_results:
            warnings.warn('Too many results, only ' + str(max_results) +
                    ' will be returned')
        if list(self.page['entry'][0].keys())[1] == 'error':
            raise ElsevierException('error retrieving search results')

    def __iter__(self):
        """Iterates over the result pages and entries."""
        self.index = 0
        while True:
            try:
                yield SearchEntry(self.page['entry'][self.index])
                self.index += 1
            except IndexError:
                try:
                    self.params['start'] += self.page_length
                except KeyError:
                    self.params['start'] = self.page_length
                try:
                    self.page = self.client.search_science_direct(**self.params)
                    self.page = self.page['search-results']
                    self.index = 0
                except ElsevierException as e:
                    self.params['start'] = 0
                    self.page = self.client.search_science_direct(**self.params)
                    self.page = self.page['search-results']
                    break


class SearchEntry(object):
    """Stores the id and id_type of an article."""
    def __init__(self, data):
        url_components = data['prism:url'].split('/')
        self.id = url_components[-1]
        self.id_type = url_components[-2]
        self.data = data

    def download(self, client, view='META_ABS'):
        """Retrieves a view of the article

        :param client: ElsevierClient
        :param view: name of the particular view that will be retrieved
            for example 'META_ABS' or 'FULL'.
        """
        result = client.retrieve_article(
                id=self.id, id_type=self.id_type, view=view)
        return Article(result['full-text-retrieval-response'])


class Article(object):
    """Stores the data of an article."""
    def __init__(self, data):
        self.data = data
