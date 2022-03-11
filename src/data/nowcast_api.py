#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 10:59:57 2022

@author: krish
"""

import os
from nowcast_helper import get_nowcast_data, run_model, save_gif, save_h5
import dateutil.parser

# Use the following for testing nowcast(llcrnrlat=37.318363, llcrnrlon=-84.224203, urcrnrlat=40.087573 , urcrnrlon=-79.052692, time_utc='2019-06-02 18:33:00', path='C:\\Users\\krish\\Documents\\Northeastern University\\Spring22\\DAMG 7245\\Assignment-3\\SEVIR API\\Working code\\')
def nowcast(llcrnrlat, llcrnrlon, urcrnrlat, urcrnrlon, time_utc, model_type, catalog_path, model_path, data_path, out_path):
    
    # Parse time
    user_time = dateutil.parser.parse(time_utc)
    
    # Data cannot be older than 2019 June 1st (As per paper)
    if user_time.year < 2019 and user_time.month < 6:
        raise Exception('Request date is too old!')
    
    # Filter to get data
    data = get_nowcast_data(llcrnrlat = llcrnrlat, llcrnrlon = llcrnrlon, urcrnrlat = urcrnrlat, urcrnrlon = urcrnrlon, time_utc = time_utc, catalog_path = catalog_path, data_path = data_path)
    
    # Run model
    output = run_model(data,model_path,scale=True,model_type=model_type)
    
    # Output as h5/GIF
    display_path = save_gif(data = output,file_name =os.path.join(out_path,f'nowcast_display_{llcrnrlat}_{llcrnrlon}.gif'), time_utc=time_utc)
    output_path = save_h5(output,os.path.join(out_path,f'nowcast_output_{llcrnrlat}_{llcrnrlon}.h5'))
    
    # Return path for output
    return {'data': output_path, 'display':display_path}