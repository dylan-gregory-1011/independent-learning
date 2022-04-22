##!/usr/bin/env python
""" 
 This script takes together the gdp data and formats it into one file
"""
#Imports
import warnings
from pathlib import Path
import pandas as pd
warnings.filterwarnings('ignore')

__author__ = "Dylan Smith"
__copyright__ = "Copyright (C) 2020 Dylan Smith"
__credits__ = ["Dylan Smith"]

__license__ = "Personal Use"
__version__ = "4.0"
__maintainer__ = "Dylan Smith"
__email__ = "-"
__status__ = "Development"

# Constants
PROJ = Path(__file__).resolve().parent.parent.parent.parent
DATA_PATH = PROJ.joinpath('data','politics')
PROC_PATH = DATA_PATH.joinpath('processed')
GDP_PATH = DATA_PATH.joinpath('raw','indicators')
industries = ['All industry total','Accommodation and food services','Trade','Utilities', 'Administrative and support and waste management and remediation services', 'Agriculture, forestry, fishing and hunting', 'All industry total (percent change)', 'Arts, entertainment, and recreation','Construction','Durable goods manufacturing', 'Educational services','Finance and insurance','Government and government enterprises', 'Health care and social assistance','Information', 'Wholesale trade', 'Management of companies and enterprises','Transportation and utilities', 'Manufacturing','Mining, quarrying, and oil and gas extraction', 'Private industries','Professional, scientific, and technical services', 'Real estate and rental and leasing', 'Retail trade','Transportation and warehousing','Nondurable goods manufacturing']

class GDPFormatter(object):

    def __init__(self, data_path):
        '''
        
        '''
        self.raw_data = data_path.joinpath('raw','indicators')
        self.proc_data = data_path.joinpath('processed')

    def gdp_reformat(self, df, typ):
        """ 
        A function that reformats the gdp data to be consumed in the final output.
        ...
        Parameters
        ----------
        df: The dataframe to 
        typ: The type of the file to get extracted
        ...
        Returns
        ----------
         > A DataFrame
        """
        # Replace GeoFIPS with a string, drop unnecessary columns
        df['GeoFIPS'] = df['GeoFIPS'].str.replace('"','').str.strip()
        df['Description'] = df['Description'].str.strip()
        df.rename(columns = {'GeoFIPS': 'FIPS'}, inplace = True)
        df = df[df['FIPS'].astype(int) != 0]
        df.drop(columns = ['TableName','Region','GeoName','IndustryClassification','Unit'],
                inplace = True)

        for yr in range(2002,2019):
            df = df.replace({str(yr): {'(D)': None, '(NA)': None}})
            df[str(yr)] = df[str(yr)].astype('float')

        # Reprocess and format the data.  Pivot the data into different years
        df = pd.melt(df, id_vars = ['FIPS','LineCode','Description'],
                        value_vars = [str(YR) for YR in range(2002,2019)])
        df.rename(columns = {'variable':'YR'}, inplace = True)
        df.replace({'All industry total (percent change)': 'All industry total'},inplace = True)
        df.insert(3,'UNIT',typ)
        
        return df

    def processGDPData(self):
        """ 
        A function that reformats the gdp data to be consumed in the final output.
        """
        df_gdp = pd.read_csv(self.raw_data.joinpath('gdp_usd_all_areas.tsv.gz'),
                    index_col = False,
                    compression = 'gzip',
                    sep='\t',
                    encoding='latin-1')

        df_gdp_chg = pd.read_csv(self.raw_data.joinpath('gdp_change_all_areas.tsv.gz'),
                    index_col = False,
                    compression = 'gzip',
                    sep='\t',
                    encoding='latin-1')

        # Format the gdp data correctly
        df_gdp = self.gdp_reformat(df_gdp, 'USD')
        df_gdp_chg = self.gdp_reformat(df_gdp_chg, 'PCT_CHG')

        # Merge the two files for one output
        df_gdp_out = df_gdp.merge(df_gdp_chg, on = ['FIPS','YR','Description','LineCode'], how = 'left')
        df_gdp_out.drop(columns = ['UNIT_x','UNIT_y','LineCode'], inplace = True)
        df_gdp_out.rename(columns = {'value_y': 'PCT_CHG','value_x':'USD'}, inplace = True)

        # Filter the extraneous industries out of the df
        df_gdp_out['YR'] = df_gdp_out['YR'].astype(int)
        df_gdp_out = df_gdp_out[(df_gdp_out['YR'] % 2 == 0) &
                                (df_gdp_out['Description'].isin(industries))]

        # Get the breakdown of each industry within a county as well as normalize the total county output within the year
        df_gdp_out['PCT_TOTL'] = df_gdp_out.groupby(['FIPS','YR'])['USD'].apply(lambda x: x * 100 / x.max())

        # Normalize each counties total based upon the country + year
        df_gdp_out.loc[df_gdp['Description'] == 'All industry total', 'USD'] = \
        df_gdp_out[df_gdp_out['Description'] == 'All industry total'].groupby('YR')['USD'].apply(lambda x: (x - x.mean()) / x.std())

        # Get the Four year ago USD output from each county and calculate the percent change
        df_gdp_ago = df_gdp_out[['FIPS','Description','YR','USD']]
        df_gdp_ago.rename(columns = {'USD':'FOUR_YR_PCT_CHG'}, inplace = True)
        df_gdp_ago['YR'] = df_gdp_ago['YR'] + 4
        df_gdp_out = df_gdp_out.merge(df_gdp_ago, on = ['FIPS','YR','Description'], how = 'left')
        df_gdp_out['FOUR_YR_PCT_CHG'] = ((df_gdp_out['USD'] - df_gdp_out['FOUR_YR_PCT_CHG'] ) 
                                                        / df_gdp_out['FOUR_YR_PCT_CHG'] * 100)

        # Create the final Feature dataset per year
        df_gdp_final = pd.pivot_table(df_gdp_out, index = ['YR','FIPS'], columns = 'Description')
        df_gdp_final.columns = ['%s_%s' % (ind, val) for (ind, val) in df_gdp_final.columns]
        df_gdp_final.reset_index(inplace = True)
        df_gdp_final.columns = df_gdp_final.columns.str.replace(' ', '_').str.replace(',','').str.lower()

        # Write the data to an outfile
        df_gdp_final.to_csv(self.proc_data.joinpath('gdp.tsv.gz'),
                        compression = 'gzip',
                        mode = 'w',
                        sep='\t',
                        index = False,
                        encoding='utf-8',
                        line_terminator = '\n')
