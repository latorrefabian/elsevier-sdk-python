import pdb
api_key = '787e618968bd6064264d80f811623b48'

from elsevier.client import ElsevierClient
from elsevier.elsevier_models import ScienceDirectSearch

query = 'tak(Crime)'
subj = 'environscigen'

client = ElsevierClient(api_key)

search = ScienceDirectSearch(client=client, query=query, subj=subj)
articles = [x.id for x in search]
pdb.set_trace()
