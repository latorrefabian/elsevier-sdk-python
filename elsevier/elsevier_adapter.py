from elsevier.client import ElsevierClient
import pdb
from config import api_key as key
from .models import Article as ArticleEntry
from elsevier.exceptions import ElsevierException

max_results = 5950
client = ElsevierClient(key)


class Mapper(object):
    def __init__(self, attr_list, raw_data):
        self.raw_data = raw_data
        for attr, path in attr_list.items():
            attr_path = list(path)
            attribute = raw_data
            while len(attr_path) > 0:
                try:
                    attribute = attribute[attr_path.pop(0)]
                except KeyError:
                    attribute = None
                    break
            self.__setattr__(attr, attribute)


class Search(Mapper):
    attr_list = {
        'search_terms': ['opensearch:Query', '@searchTerms'],
        'count': ['opensearch:itemsPerPage'],
        'total_results': ['opensearch:totalResults'],
        'start': ['opensearch:startIndex']
        }

    def __init__(self, **kwargs):
        raw_data = client.search_science_direct(**kwargs)['search-results']
        super(Search, self).__init__(Search.attr_list, raw_data)
        self.arguments = kwargs
        if list(raw_data['entry'][0].keys())[1] != 'error':
            self.entry = [SearchEntry(x) for x in raw_data['entry']]
        else:
            raise ElsevierException('error during search')


    def __iter__(self):
        return iter(self.entry)


    def download(self, **kwargs):
        if int(self.total_results) > max_results:
            raise ElsevierException('Too many results to download')
        for entry in self.entry:
            entry.download(**kwargs)


class Article(Mapper):
    attr_list = {
        'url': ['coredata', 'prism:url'],
        'title': ['coredata', 'dc:title'],
        'authors': ['coredata', 'dc:creator'],
        'abstract': ['coredata', 'dc:description'],
        'keywords': ['coredata', 'dcterms:subject'],
        'full_text': ['originalText', 'xocs:doc'],
        }

    def __init__(self, **kwargs):
        raw_data = client.retrieve_article(**kwargs)
        raw_data = raw_data['full-text-retrieval-response']
        super(Article, self).__init__(Article.attr_list, raw_data)
        if self.abstract:
            if self.abstract.startswith('Abstract'):
                self.abstract = self.abstract[8: ]
                self.english = True
            elif self.abstract.startswith('Summary'):
                self.abstract = self.abstract[7: ]
                self.english = True
            else:
                print(self.abstract)
                self.abstract = ''
                self.english = False
        else:
            self.english = False
        url_components = self.url.split('/')
        self.uid = url_components[-1]
        self.id_type = url_components[-2]

    def download(self, **kwargs):
        if self.english:
            entry = ArticleEntry(uid=self.uid, id_type=self.id_type,
                title=self.title, abstract=self.abstract,
                full_text=self.full_text, keywords=self.keywords)
            entry.download(**kwargs)
        else:
            print('nonenglish article')

class SearchEntry(Mapper):
    attr_list = {
        'title': ['dc:title'],
        'url': ['prism:url'],
        'creator': ['dc:creator'],
        'teaser': ['prism:teaser']
        }

    def __init__(self, raw_data):
        super(SearchEntry, self).__init__(SearchEntry.attr_list, raw_data)
        url_components = self.url.split('/')
        self.uid = url_components[-1]
        self.id_type = url_components[-2]

    def get(self, view='META_ABS'):
        return Article(id_type=self.id_type, id=self.uid, view=view)

    def download(self, view, **kwargs):
        try:
            self.get(view=view).download(**kwargs)
        except Exception as e:
            print(e.args)


