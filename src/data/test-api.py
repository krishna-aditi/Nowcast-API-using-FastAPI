# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 18:15:57 2022

@author: krish
"""

from nowcast_main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_model_run():
    response = client.post("/nowcast/", json = {"llcrnrlat":37.318363,"llcrnrlon":-84.224203,"urcrnrlat":40.087573, "urcrnrlon":-79.052692, "time_utc":"2019-06-02 18:33:00"})
    assert response.status_code == 200