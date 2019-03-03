import numpy as np
import pandas as pd

from collections import OrderedDict

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
        search = zoopla.property_listings({'listing_status': status,'area': 'BN3','page_number':page_num,'page_size':100})
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



text=[]
for text_dict in data[['Listing ID','First Published Date','Last Published Date', 'Listing Status', 'Property Type', 'Postcode']].to_dict('records'):
    text.append('\n'.join([': '.join(map(str,item)) for item in text_dict.items()]))

mapbox_access_token = 'pk.eyJ1IjoiYXJ1MjYxMiIsImEiOiJjanMwanVvcHgxZjg2M3luMTk2c2Z1ZnNvIn0.LJrZfEMS-mfe8nIOVqLziA'

plot_data = [
    go.Scattermapbox(
        lon=list(data['Longitude']),
        lat=list(data['Latitude']),
        mode='markers',
        marker=dict(
            size=9
        ),
        text=text
    )
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
