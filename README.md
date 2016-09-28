# elsevier-sdk-python
Python SDK for the Elsevier API

Install with pip:
```shell
pip install git+https://github.com/latorrefabian/elsevier-sdk-python#egg=elsevier-sdk-python
```

Upgrade with pip:
```shell
pip install --upgrade git+https://github.com/latorrefabian/elsevier-sdk-python#egg=elsevier-sdk-python
```

Basic usage (Note that you should replace API_KEY with your own)
```python
from elsevier.client import ElsevierClient

client = ElsevierClient(API_KEY)
```

Searching on ScienceDirect
```python
search = client.search_science_direct(query='economics')
search = search['search-results']

# print first entry
print search['entry'][0]
```

Retrieve article metadata
```python
article = client.retrieve_article(id_type='pii', id='S0921800916302634', view='META')
article = article['full-text-retrieval-response']
```

Retrieve full text article (Notice that you need the correct credentials and do the request from an authorized IP)
```python
article = client.retrieve_article(id_type='pii', id='S0921800916302634', view='FULL')
article = article['full-text-retrieval-response']
```

Read the API documentation at [http://dev.elsevier.com/api_docs.html]

This repo was forked from <https://github.com/vitorfs/elsevier-sdk-python>
