#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 10:59:57 2022

@author: krish
"""

from fastapi import FastAPI
from nowcast_api import nowcast
from pydantic import BaseModel # Pydantic is used for data handling

app = FastAPI()

@app.get("/")
def read_main():
    return 'Nowcast API designed for Federal Aviation Administration'

# Define data shapes that you want to receive using BaseModel
class NowCastParams(BaseModel):
    llcrnrlat: float
    llcrnrlon: float
    urcrnrlat: float
    urcrnrlon: float
    time_utc: str
    catalog_path: str = "C:\\Users\\krish\\Documents\\Northeastern University\\Spring22\\DAMG 7245\\Assignment-3\\SEVIR API\\Working code\\CATALOG.csv"
    data_path: str = "C:\\Users\\krish\\Documents\\Northeastern University\\Spring22\\DAMG 7245\\Assignment-3\\SEVIR API\\Working code\\sevir"
    out_path: str = "C:\\Users\\krish\\Documents\\Northeastern University\\Spring22\\DAMG 7245\\Assignment-3\\SEVIR API\\Working code"
    model_path:str = "C:\\Users\\krish\\Documents\\Northeastern University\\Spring22\\DAMG 7245\\Assignment-3\\SEVIR API\\Working code\\models\\nowcast"
    model_type:str = "gan"

# We need to send JSON data, hence POST method which is our write method
# Endpoint
@app.post("/nowcast/")
def nowcast_predict(params: NowCastParams): # Receive whatever is in the body
    """
    **SEVIR Nowcast API using FastAPI, for Federal Aviation Administration usecase.**
    
    Submitted by - Team 2
    * Aditi Krishna
    * Abhishek Jaiswal
    * Sushrut Mujumdar
    """
    output = nowcast(params.llcrnrlat, params.llcrnrlon, params.urcrnrlat, params.urcrnrlon, params.time_utc, params.model_type, params.catalog_path, params.model_path, params.data_path, params.out_path)
    return {"nowcast_path": output['data'], "gif_path": output['display']}

# Sample json body
'''
{
 "llcrnrlat":37.318363,
 "llcrnrlon":-84.224203, 
 "urcrnrlat":40.087573 ,
 "urcrnrlon":-79.052692,
 "time_utc":"2019-06-02 18:33:00",
 "out_path":"C:\\Users\\krish\\Documents\\Northeastern University\\Spring22\\DAMG 7245\\Assignment-3\\SEVIR API\\Working code\\output",
 "catalog_path":"C:\\Users\\krish\\Documents\\Northeastern University\\Spring22\\DAMG 7245\\Assignment-3\\SEVIR API\\Working code\\CATALOG.csv",
 "data_path":"C:\\Users\\krish\\Documents\\Northeastern University\\Spring22\\DAMG 7245\\Assignment-3\\SEVIR API\\Working code\\sevir",
 "model_path":"C:\\Users\\krish\\Documents\\Northeastern University\\Spring22\\DAMG 7245\\Assignment-3\\SEVIR API\\Working code\\models\\nowcast",
 "model_type":"gan"
}
'''
'''
{
 "llcrnrlat":30.54711887,
 "llcrnrlon":-92.28496258, 
 "urcrnrlat":33.70508203,
 "urcrnrlon":-87.90525535,
 "time_utc":"2019-06-25 21:59:00"
}
'''
'''

'''