from sklearn.preprocessing import RobustScaler
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.neighbors import LocalOutlierFactor
import numpy as np
import pandas as pd
scaler = RobustScaler()
iforest = IsolationForest(n_estimators=100, random_state=42)
ocsvm = OneClassSVM(nu=0.05, kernel='rbf', gamma='scale')
lof = LocalOutlierFactor(n_neighbors=20, novelty=False)
def detect_anomalies(features):
# Scale the features
    features_scaled = scaler.fit_transform(features)

# Fit and predict anomalies with each model
    features['iforest_anomaly'] = iforest.fit_predict(features_scaled)
    features['ocsvm_anomaly'] = ocsvm.fit_predict(features_scaled)
    features['lof_anomaly'] = lof.fit_predict(features_scaled)

# Combine the anomaly predictions using a majority vote
    features['anomaly'] = features[['iforest_anomaly', 'ocsvm_anomaly', 'lof_anomaly']].mode(axis=1)[0]

# In IsolationForest and LocalOutlierFactor, -1 indicates an outlier and 1 indicates an inlier.
# In OneClassSVM, -1 indicates an outlier and 1 indicates an inlier.
# The combined 'anomaly' column will also follow this convention due to the majority vote.
