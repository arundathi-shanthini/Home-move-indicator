import numpy as np
import pandas as pd
from collections import OrderedDict

import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings('ignore')

from zoopla import Zoopla

zoopla = Zoopla(api_key='gcstpjxbj29s2nzkmr9jnkgg')

import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, plot, iplot

import postcodes_io_api
api  = postcodes_io_api.Api(debug_http=True)

column_list=['listing_id','longitude','latitude','first_published_date','last_published_date','listing_status','property_type']
data=[]
for status in ['sale','rent']:
    page_num=1
    while 1:
        search = zoopla.property_listings({'listing_status': status,'area': 'BN3','include_sold':'1','include_rented':'1',
                                          'order_by':'age','ordering':'descending','page_number':page_num,'page_size':100})
        if(page_num==1):
            nresults=search.result_count
            npages=np.ceil(nresults/100)
        for result in search.listing:
              result_dict=OrderedDict((key,result[key]) for key in column_list)
              result_dict['outcode']='BN3'
              result_dict['postcode']=api.get_nearest_postcodes_for_coordinates(latitude=result.latitude,longitude=result.longitude,limit=1)['result'][0]['postcode']
              data.append(pd.DataFrame(result_dict,index=[0]))
        if(page_num>=npages):
            break
        else:
            page_num+=1
data=pd.concat(data)
col_list=['Listing ID','Longitude','Latitude','First Published Date','Last Published Date','Listing Status','Property Type','Outcode','Postcode']
data.rename(columns=dict(zip(data.columns,col_list)),inplace=True)
data.reset_index(drop=True,inplace=True)

column_list=['listing_id','listing_status']
data2=[]
for status in ['sale','rent']:
    page_num=1
    while 1:
        search = zoopla.property_listings({'listing_status': status,'area': 'BN3',
                                          'order_by':'age','ordering':'descending','page_number':page_num,'page_size':100})
        if(page_num==1):
            nresults=search.result_count
            npages=np.ceil(nresults/100)
        for result in search.listing:
            result_dict=OrderedDict((key,result[key]) for key in column_list)
            data2.append(pd.DataFrame(result_dict,index=[0]))
        if(page_num>=npages):
            break
        else:
            page_num+=1
data2=pd.concat(data2)
col_list=['Listing ID','Listing Status']
data2.rename(columns=dict(zip(data2.columns,col_list)),inplace=True)
data2.reset_index(drop=True,inplace=True)

data.loc[(~data['Listing ID'].isin(data2['Listing ID'])&(data['Listing Status']=='sale')), 'Listing Status'] = 'sold'
data.loc[(~data['Listing ID'].isin(data2['Listing ID'])&(data['Listing Status']=='rent')), 'Listing Status'] = 'rented'

text=[]
for text_dict in data[['Listing ID','First Published Date','Last Published Date', 'Listing Status', 'Property Type', 'Postcode']].to_dict('records'):
    text.append('\n'.join([': '.join(map(str,item)) for item in text_dict.items()]))
data['Description text']=text

split_data=[]
for i in ['sale','rent','sold','rented']:
    split_data.append(data[data['Listing Status']==i])

cm=['#D62728','#1F77B4','#ED9999','#9AC0CD']
legend=['For Sale','For rent','Sold','Rented']

mapbox_access_token = 'pk.eyJ1IjoiYXJ1MjYxMiIsImEiOiJjanMwanVvcHgxZjg2M3luMTk2c2Z1ZnNvIn0.LJrZfEMS-mfe8nIOVqLziA'

plot_data = [
    go.Scattermapbox(
        lon=list(split_data[i]['Longitude']),
        lat=list(split_data[i]['Latitude']),
        mode='markers',
        marker=dict(
            size=9,
            color=cm[i]
        ),
        text=list(split_data[i]['Description text']),
        name=legend[i],
        showlegend=True
    ) for i in range(len(split_data)-1,-1,-1)
]

layout = go.Layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(
            lon=data['Longitude'].sum()/float(len(data['Longitude'])),
            lat=data['Latitude'].sum()/float(len(data['Latitude']))
        ),
        pitch=0,
        zoom=10
    ),
)

fig = dict(data=plot_data, layout=layout)
py.plot(fig, filename='Multiple Mapbox')
