#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 10:59:57 2022

@author: krish
"""
import tensorflow as tf
import numpy as np
import datetime
import os
import h5py
from nowcast_utils import SEVIRSequence
import dateutil.parser
import matplotlib as mpl
mpl.use("TkAgg")
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (10,10)

############################################################################## 
# make_nowcast_dataset file class and function copied here
# Use make_nowcast_generator file functions for filtering

class NowcastGenerator(SEVIRSequence):
    """
    Generator that loads full VIL sequences, and spilts each
    event into three training samples, each 12 frames long.

    Event Frames:  [-----------------------------------------------]
                   [----13-----][---12----]
                               [----13----][----12----]
                                          [-----13----][----12----]
    """
    # Splitting into sequence
    def __getitem__(self, idx):
        """

        """
        X,_ = super(NowcastGenerator, self).__getitem__(idx)  # N,L,W,49
        x1,x2,x3 = X[0][:,:,:,:13],X[0][:,:,:,12:25],X[0][:,:,:,24:37]
        y1,y2,y3 = X[0][:,:,:,13:25],X[0][:,:,:,25:37],X[0][:,:,:,37:49]
        Xnew = np.concatenate((x1,x2,x3),axis=0)
        Ynew = np.concatenate((y1,y2,y3),axis=0)
        return [Xnew],[Ynew]
 
# lat/lon as additional parameters used for filtering

def get_nowcast_test_generator(sevir_catalog,
                           sevir_location,
                           llcrnrlat, llcrnrlon, urcrnrlat, urcrnrlon, time_utc,
                           batch_size=8,
                           start_date=datetime.datetime(2019,6,1),
                           end_date=None):
    #time_utc = '2012-03-01T10:00:00Z'
    filt = lambda c:  np.logical_and(c.pct_missing==0, np.logical_and(np.logical_and(round(c.llcrnrlat, 3) == round(llcrnrlat, 3), round(c.llcrnrlon, 3) == round(llcrnrlon, 3)), np.logical_and(round(c.urcrnrlat, 3) == round(urcrnrlat, 3), round(c.urcrnrlon, 3) == round(urcrnrlon, 3))))
    user_time = dateutil.parser.parse(time_utc)
    datetime_filt = lambda t: np.logical_and(t.dt.hour <= user_time.hour, t.dt.hour >= user_time.hour - 1)
    return NowcastGenerator(catalog = sevir_catalog,
                            sevir_data_home = sevir_location,
                            x_img_types = ['vil'],
                            y_img_types = ['vil'],
                            batch_size = batch_size,
                            start_date = start_date,
                            end_date = end_date,
                            catalog_filter = filt,
                            datetime_filter = datetime_filt)

############################################################################## 
# Defining our own data generator with the help of make_nowcast_dataset 
# Functions to filter the catalog and reading data in desired format

def get_nowcast_data(llcrnrlat, llcrnrlon, urcrnrlat, urcrnrlon, time_utc,catalog_path, data_path):
    tst_generator = get_nowcast_test_generator(sevir_catalog = catalog_path,
                                               sevir_location = data_path,
                                               llcrnrlat = llcrnrlat, llcrnrlon = llcrnrlon,
                                               urcrnrlat = urcrnrlat, urcrnrlon = urcrnrlon, 
                                               time_utc = time_utc)
    # tst_generator returns a SEVIRSequence class
    X, Y = tst_generator.__getitem__(0)
    # Array of 13 images input
    return np.array(X)

##############################################################################
# Display VIL images through matplotlib

# get_cmap function from src.display.display
# vil_cmap function from src.display.display

def get_cmap(type, encoded=True):
   
    if type.lower() == 'vil':
        cmap, norm = vil_cmap(encoded)
        vmin, vmax = None, None
    else:
        cmap, norm = 'jet', None
        vmin, vmax = (-7000, 2000) if encoded else (-70, 20)

    return cmap, norm, vmin, vmax


def vil_cmap(encoded = True):
    cols=[   [0,0,0],
              [0.30196078431372547, 0.30196078431372547, 0.30196078431372547],
              [0.1568627450980392,  0.7450980392156863,  0.1568627450980392],
              [0.09803921568627451, 0.5882352941176471,  0.09803921568627451],
              [0.0392156862745098,  0.4117647058823529,  0.0392156862745098],
              [0.0392156862745098,  0.29411764705882354, 0.0392156862745098],
              [0.9607843137254902,  0.9607843137254902,  0.0],
              [0.9294117647058824,  0.6745098039215687,  0.0],
              [0.9411764705882353,  0.43137254901960786, 0.0],
              [0.6274509803921569,  0.0, 0.0],
              [0.9058823529411765,  0.0, 1.0]]
    lev = [0.0, 16.0, 31.0, 59.0, 74.0, 100.0, 133.0, 160.0, 181.0, 219.0, 255.0]
    #TODO:  encoded=False
    nil = cols.pop(0)
    under = cols[0]
    over = cols.pop()
    cmap = mpl.colors.ListedColormap(cols)
    cmap.set_bad(nil)
    cmap.set_under(under)
    cmap.set_over(over)
    norm = mpl.colors.BoundaryNorm(lev, cmap.N)
    return cmap, norm
       
##############################################################################
# Create multiple temporary images of VIL and save as GIF, then delete temp files

def save_gif(data, file_name, time_utc):
    count = 0
    # From visualize_result function in AnalyzeNowcast notebook
    cmap_dict = lambda s: {'cmap':get_cmap(s,encoded=True)[0],
                            'norm':get_cmap(s,encoded=True)[1],
                            'vmin':get_cmap(s,encoded=True)[2],
                            'vmax':get_cmap(s,encoded=True)[3]}
    filenames = []
    for pred in data:
        for i in range(pred.shape[-1]):
            plt.imshow(pred[:,:,i],**cmap_dict('vil'))
            # plt.imshow(pred[:,:,i],cmap="gist_heat")
#            plt.colorbar(c)
            plt.axis('off')
            plt.title(f'Nowcast prediction at time {time_utc}+{(count+1)*5}minutes')
            plt.savefig(f"Pred_{time_utc.replace(':','')}_{count}.png", bbox_inches='tight')
            plt.close()
            filenames.append(f"Pred_{time_utc.replace(':','')}_{count}.png")
            count+=1
    # Saving files as GIF (https://stackoverflow.com/questions/41228209/making-gif-from-images-using-imageio-in-python)
    import imageio
    images = []
    for filename in filenames:
        images.append(imageio.imread(filename))
        os.remove(filename)
    imageio.mimsave(file_name, images)
    return file_name



##############################################################################
# Saving the model's output as h5

def save_h5(data, file_name):
    hf = h5py.File(file_name, 'w')
    hf.create_dataset('nowcast_predict', data = data)
    hf.close()
    return file_name

##############################################################################
# Initializing and running the model
# Link to download pre-trained model (https://www.dropbox.com/s/9y3m4axfc3ox9i7/gan_generator.h5?dl=0Downloading%20mse_and_style.h5)

def run_model(data, model_path, scale=False, model_type='gan'):
    MEAN=33.44
    SCALE=47.54
    data = (data.astype(np.float32)-MEAN)/SCALE
    norm = {'scale':47.54, 'shift':33.44}
    # Model type
    if model_type == 'gan':
        file = os.path.join(model_path, 'gan_generator.h5')
        model = tf.keras.models.load_model(file, compile=False, custom_objects = {"tf": tf})
    elif model_type == 'mse':    
        file  = os.path.join(model_path, 'mse_model.h5')
        model = tf.keras.models.load_model(file, compile=False, custom_objects = {"tf": tf})
    elif model_type == 'style':    
        file = os.path.join(model_path, 'style_model.h5')
        model = tf.keras.models.load_model(file, compile=False, custom_objects = {"tf": tf})
    elif model_type in ['mse+style', 'style+mse']:    
        file = os.path.join(model_path, 'mse_and_style.h5')
        model = tf.keras.models.load_model(file, compile=False, custom_objects = {"tf": tf})
    else:
        raise Exception('Did not find the specified model for nowcast!')
    
    # Output
    output = model.predict(data[0])
    if isinstance(output,(list,)):
        output=output[0]
    if scale:
        output = output*norm['scale'] + norm['shift']
    return output

