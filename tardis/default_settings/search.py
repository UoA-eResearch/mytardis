'''
Settings for search
'''

SINGLE_SEARCH_ENABLED = True
'''
To enable search:

SINGLE_SEARCH_ENABLED = True
INSTALLED_APPS += ('django_elasticsearch_dsl', 'tardis.app.search')
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': os.environ.get('ELASTICSEARCH_URL', 'http://localhost:9200')
    }
}
ELASTICSEARCH_DSL_INDEX_SETTINGS = {
    'number_of_shards': 1
}
'''

RESULTS_PER_PAGE = 10000
'''
Limits the maximum number of search results for each model (Project, Experiment, Dataset and DataFile).
The default value of 10,000 means that a query could potentially return 40,000 results in total,
i.e. 10,000 projects, 10,000 experiments, 10,000 datasets and 10,000 datafiles.
'''
MIN_CUTOFF_SCORE = 0.0
'''
Filters results based on this value.
The default value of 0.0 means that nothing will be excluded from search results.
Set it to any number greater than 0.0 to filter out results.
'''
