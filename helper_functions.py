import numpy as np
import pandas as pd
import geopandas as gpd
import country_converter as coco
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, BasicTicker
from bokeh.palettes import brewer
from bokeh.embed import file_html
from bokeh.resources import CDN
import json


def remove_outliers(dataframe, column_names, low = 5, high = 95):
    """
    Remove rows with the numerical outliers, by using the columns provided in the column_names variable. By default the function will retain data between 5% - 95%.
    
    Arguments:
        dataframe { pandas dataframe } -- the pandas dataframe to perform operation on
        column_names {list} -- the name of the numerical columns to perform the operation on. Needs to be a list.
    
    Keyword Arguments:
        low {int} -- low percentile threshold to retain values from (default: {5})
        high {int} -- high percentile threshold to retain values from (default: {95})
    
    Returns:
        dataframe -- the resulting dataframe with the omitted values for each column
    """ 


    for column_name in column_names:
        vlow,vhigh = np.percentile(dataframe[column_name].values,  q=[low,high])
        out_df = dataframe[(dataframe[column_name] > vlow) & (dataframe[column_name] < vhigh)]

    print("removed {} % of the rows".format(round(100*(dataframe.shape[0]-out_df.shape[0])/dataframe.shape[0]),decimals=4))
    return out_df


def compute_psychometrics(dataframe):
    """
    Compute the psychometrics for:
    (E)Extrovertedness
    (A)Agreeableness
    (C)Conscientiousness
    (N)Neuroticism
    (O)Openness to Experience

    As specified by the online test taking template in : https://openpsychometrics.org/printable/big-five-personality-test.pdf

    
    Arguments:
        dataframe {pandas.DataFrame} -- The pandas dataframe with at least the columns for the 
                                        psychometrics.
    Returns:
        dataframe -- the resulting pandas dataframe with the columns of E,A,C,N,O  scored.

    """
    dataframe['E'] = ( 20 + dataframe['EXT1'] - dataframe['EXT2'] 
                    + dataframe['EXT3'] - dataframe['EXT4']
                    + dataframe['EXT5'] - dataframe['EXT6']
                    + dataframe['EXT7'] - dataframe['EXT8'] 
                    + dataframe['EXT9'] - dataframe['EXT10'])
    
    dataframe['A'] = ( 14 - dataframe['AGR1'] + dataframe['AGR2']
                   -dataframe['AGR3'] + dataframe['AGR4']
                   -dataframe['AGR5'] + dataframe['AGR6']
                   -dataframe['AGR7'] + dataframe['AGR8']
                   +dataframe['AGR9'] + dataframe['AGR10'] )  
    
    dataframe['C'] = ( 14 + dataframe['CSN1'] - dataframe['CSN2']
                   + dataframe['CSN3'] - dataframe['CSN4'] 
                   + dataframe['CSN5'] - dataframe['CSN6']
                   + dataframe['CSN7'] - dataframe['CSN8']
                   + dataframe['CSN9'] + dataframe['CSN10'] )
    
    dataframe['N'] = (38 - dataframe['EST1'] + dataframe['EST2']
                     - dataframe['EST3'] + dataframe['EST4']
                      - dataframe['EST5'] - dataframe['EST6']
                      - dataframe['EST7'] - dataframe['EST8']
                      - dataframe['EST9'] - dataframe['EST10'] )
    
    dataframe['O'] = (8 + dataframe['OPN1'] - dataframe['OPN1']
                     + dataframe['OPN1'] - dataframe['OPN1']
                     + dataframe['OPN1'] - dataframe['OPN1']
                     + dataframe['OPN1'] + dataframe['OPN1']
                     + dataframe['OPN1'] + dataframe['OPN1'])
    return dataframe


def filter_countries(dataframe, minvalues = 100):
    """
    Removes from the dataframe countries that have less completed forms than minvalues.
    It uses the countries column to decide which countries to include.

    Arguments:
        dataframe {pandas.dataframe} -- The pandas dataframe countries column.

    Keyword Arguments:
        minvalues {int} -- minimum number of completed applications from a specific country (default: {100})

    Returns:
        dataframe {pandas.dataframe} -- the dataframe with entries removed for countries with not enough values
    """    

    country_list=dataframe['country'].value_counts()
    country_list=country_list[country_list.values>100]
    country_list=country_list.index.to_list()
    country_list.remove('NONE')
    filtered_country=dataframe[dataframe['country'].isin(country_list)]

    return filtered_country


def country_averages(dataframe):
    """
    Makes a GeoPandas DataFrame, with the geographical/geometric information for each country represented
    in the dataframe variable. The output dataframe countains the average psychometric scores for each 
    country. Scores of 0 represent countries with no entries. Writes the dataframe to 'country_averages.csv'
    in the local directory.
    
    Arguments:
        dataframe {pandas.dataframe} -- DataFrame with psychometric values, and countries for each entry.
    
    Returns:
        {geopandas.dataframe} -- The GeoPandas DataFrame with the psychometric averages for each country,
        the geometric shape of country on a map, and country labels.
                                 
    """    
    Edf=dataframe.groupby(by='country').mean()['E']
    Adf=dataframe.groupby(by='country').mean()['A']
    Cdf=dataframe.groupby(by='country').mean()['C']
    Ndf=dataframe.groupby(by='country').mean()['N']
    Odf=dataframe.groupby(by='country').mean()['O']

    shapefile = 'ne_110_admin_0_countries/ne_110m_admin_0_countries.shp'
    gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
    gdf.columns=['country','country_code' , 'geometry']
    gdf.drop(gdf[gdf['country'] =='Antarctica'].index)
    gdf['country_code']=coco.convert(gdf['country_code'].to_list(), to= 'ISO2')
    # merge the gdf with the group by for countries
    merged=gdf.merge(Edf, left_on='country_code', right_on='country', how='outer')
    merged=merged.merge(Adf, left_on='country_code', right_on='country',how='outer')
    merged=merged.merge(Cdf, left_on='country_code', right_on='country',how='outer')
    merged=merged.merge(Ndf, left_on='country_code', right_on='country',how='outer')
    merged=merged.merge(Odf, left_on='country_code', right_on='country',how='outer')
    merged.dropna(subset=['country'], inplace=True)
    merged['E'].fillna(-100, inplace= True)
    merged['A'].fillna(-100, inplace= True)
    merged['C'].fillna(-100, inplace= True)
    merged['N'].fillna(-100, inplace= True)
    merged['O'].fillna(-100, inplace= True)

    #merged.to_csv('country_averages.csv')

    return merged

def plot_map(dataframe, column):

    merged_json=json.loads(dataframe.to_json())
    
    json_data=json.dumps(merged_json)
    geosource = GeoJSONDataSource(geojson= json_data)
    
    palette= brewer['RdYlBu'][10]
    
    vals=dataframe[dataframe[column]>-50][column].values
    #vals=vals - np.mean(vals)
    vmin=np.round(np.min(vals), decimals = 1)
    r= np.max(vals) - np.min(vals)
    color_mapper = LinearColorMapper (palette= palette, low = vmin-5,
                                    high= vmin + r)
    tick_labels= {'no values': str(np.round((vmin-5),decimals=1)),
                '0': str(np.round(vmin,decimals=1)),
                '10': str(np.round((vmin + 0.1 * r),decimals=1)),
                '20': str(np.round((vmin + 0.2 * r),decimals=1)),
                '30': str(np.round((vmin + 0.3 * r),decimals=1)),
                '40': str(np.round((vmin + 0.4 * r),decimals=1)),
                '50': str(np.round((vmin + 0.5 * r),decimals=1)),
                '60': str(np.round((vmin + 0.6 * r),decimals=1)),
                '70': str(np.round((vmin + 0.7 * r),decimals=1)),
                '80': str(np.round((vmin + 0.8 * r),decimals=1)),
                '90': str(np.round((vmin + 0.9 * r),decimals=1)),
                '100': str(np.round((vmin + r),decimals=1))
                }
    color_bar = ColorBar(color_mapper= color_mapper, 
                        label_standoff=10, width = 500, height = 20,
                        border_line_color = None, location = (0,0), 
                        orientation='horizontal', major_label_overrides= tick_labels)
    #figure
    TOOLTIPS = [
    ("country", "@country"),
    (column, "@"+column),
    ]

    p = figure(title = ' Average Extrovertedness of each country, NOTE: countries  with value -100 do not enough values', 
            plot_height = 600 , plot_width = 950, tooltips = TOOLTIPS)
    p.xgrid.grid_line_color= None
    p.ygrid.grid_line_color = None
    p.xaxis.visible=False
    p.yaxis.visible=False
    #add patch renders to figure
    
    p.patches('xs','ys', source = geosource, fill_color = {'field': column, 'transform' : color_mapper},
            line_color = 'black', line_width = 0.25 , fill_alpha = 0.8)
    
    p.add_layout(color_bar, 'below')
    #html = file_html(p, CDN, "my plot")
    output_notebook()
    show(p)
    print("Top 10 countries in the psychometric")
    print(dataframe[['country',column]].sort_values(by=column, ascending=False).head(10))