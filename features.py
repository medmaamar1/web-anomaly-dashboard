import pandas as pd
def extract_features(data):
    data=data.set_index('time')
    window='5min'
    features=data.groupby(pd.Grouper(freq=window)).agg(
        {
            'hits': ('ip', 'count'),
            'unique_ips': ('ip', 'nunique'),
            'error4xx': ('status', lambda x: (x // 100 == 4).sum()),
            'error5xx': ('status', lambda x: (x // 100 == 5).sum()),
            'avg_size': ('response_size', 'mean'),
            'max_size': ('response_size', 'max'),
            'min_size': ('response_size', 'min'),
        }
    )

    features['err_4xx_pct'] = features['error4xx'] / features['hits']
    features['err_5xx_pct'] = features['error5xx'] / features['hits']

    features = features[['hits','unique_ips','err_4xx_pct','err_5xx_pct','avg_size','max_size','min_size']]