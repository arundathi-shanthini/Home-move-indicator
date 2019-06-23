import numpy as np
import pandas as pd

from collections import OrderedDict

import logging,sys
logging.disable(sys.maxsize)

import contextlib

from zoopla import Zoopla
zoopla = Zoopla(api_key='gcstpjxbj29s2nzkmr9jnkgg') # Alternative API key: gc8uhcvhxyfqwhj2bnt4nrpv

import postcodes_io_api
api  = postcodes_io_api.Api(debug_http=True)

def execute_api_call(area_list,include_old='1'):
    # If include_old=='1' then col_list must include the entire list of the required columns
    if include_old=='1':
        col_list=['Listing ID','Longitude','Latitude','First Published Date','Last Published Date','Listing Status',
                  'Property Type','Outcode','Postcode']
    else:
        col_list=['Listing ID','Listing Status']

    # Define column list for the dataframe
    column_list=['listing_id','longitude','latitude','first_published_date','last_published_date',
                 'listing_status','property_type']
    # Initialise the list that is to store the data
    result_df=[]
    for area in area_list:
        for status in ['sale','rent']:
            # Define initial value of page_num for first iteration of the while loop
            page_num=1
            while 1:
                with contextlib.redirect_stdout(None):
                    # Perform API call
                    search = zoopla.property_listings({'listing_status': status,'area': area,'include_sold':include_old,
                                                       'include_rented':include_old,'order_by':'age','ordering':'descending',
                                                       'page_number':page_num,'page_size':100})

                # If this the first iteration of the loop calculate the number of pages
                if(page_num==1):
                    nresults=search.result_count
                    npages=np.ceil(nresults/100)
                # Create an ordered dictionary for every result in the listing returned
                for result in search.listing:
                    result_dict=OrderedDict((key,result[key]) for key in column_list)
                    result_dict['outcode']=area

                    with contextlib.redirect_stdout(None):
                        # Match the coordinates to the nearest postcode
                        result_dict['postcode']=api.get_nearest_postcodes_for_coordinates(latitude=result.latitude,
                                                         longitude=result.longitude,limit=1)['result'][0]['postcode']
                    # Convert dictionary into a Dataframe and append it to the list
                    result_df.append(pd.DataFrame(result_dict,index=[0]))
                # Check if results of all pages have been requested, if true break else update value of page_num
                if(page_num>=npages):
                    break
                else:
                    page_num+=1
        print('Finished request for area outcode: {}/{} ({:1.2f}% done)'.format(area_list.index(area)+1,len(area_list),
                                                                    (area_list.index(area)+1)/float(len(area_list))*100))

    # Convert list of dataframes into a single list
    result_df=pd.concat(result_df)
    # Rename the columns
    result_df.rename(columns=dict(zip(result_df.columns,col_list)),inplace=True)
    # Reset the index
    result_df.reset_index(drop=True,inplace=True)
    return result_df

def get_data_for_home_move_predictor(area_list):
    print("Executing API call with all records:" )
    # Perform API call for the area outcode list passed
    data=execute_api_call(area_list,include_old='1')
    print("Executing API call without old records:" )
    # Perform API call for the area outcode list passed without including old records
    data_without_old=execute_api_call(area_list,include_old='0')
    # Change status of rows that in data but not in data_without_old
    data.loc[(~data['Listing ID'].isin(data_without_old['Listing ID'])&(data['Listing Status']=='sale')),
             'Listing Status'] = 'sold'
    data.loc[(~data['Listing ID'].isin(data_without_old['Listing ID'])&(data['Listing Status']=='rent')),
             'Listing Status'] = 'rented'

    # Add column Description text to be displayed as hover text
    text=[]
    text_list_keys=['Listing ID','First Published Date','Last Published Date', 'Listing Status',
                                                                      'Property Type', 'Postcode']
    for text_dict in data[text_list_keys].to_dict('records'):
        text.append('<br>'.join([': '.join(map(str,item)) for item in text_dict.items()]))
    data['Description text']=text

    # Split dataframe into a dataframe list based on their listing status
    split_data=[]
    for i in ['sale','rent','sold','rented']:
        split_data.append(data[data['Listing Status']==i])
    return split_data
