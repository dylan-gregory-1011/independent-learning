##!/usr/bin/env python
""" 

    This script takes together polling data along with demographic data and combines them into one file


"""
#Imports
import pandas as pd
from os import listdir
from os.path import isfile, join
import numpy as np
import warnings
warnings.filterwarnings('ignore')

__author__ = "Dylan Smith"
__copyright__ = "Copyright (C) 2018 Dylan Smith"
__credits__ = ["Dylan Smith"]

__license__ = "Personal Use"
__version__ = "4.0"
__maintainer__ = "Dylan Smith"
__email__ = "-"
__status__ = "Development"

# Constants
CENSUS_FIELDS = {'Asian Alone': 'AA','American Indian Alaska': 'IA',
                 'White Alone':'WA','Black Alone':'BA',
                "Native Hawaiian Pacific": 'NA','Two Or More Races':
                 'TOM',"Hispanic": 'H'}
AGE_CODES = {1:"0_to_4",2:"5_to_9",3:"10_to_14",4:"15_to_19",5:"20_to_24",
          6:"25_to_29",7:"30_to_34",8:"35_to_39",9:"40_to_44",10:"45_to_49",
          11:"50_to_54",12:"55_to_59",13:"60_to_64",14:"65_to_69",15:"70_to_74",
          16:"75_to_79",17:"80_to_84", 18:"85_to_Older", 0:'Total_Population'}

class DemographicDataFormatter(object):

    def __init__(self, data_path):
        '''
        The object that formats demographic data from the US Census bureau into a zip code based dataset
        ...
        Parameters
        ----------
        data_path: The path with the political data stored.
        '''
        self.raw_demo_data = data_path.joinpath('raw','demographics')
        self.proc_data = data_path.joinpath('processed')

    def formatDemographicData(self, df, yr):
        '''
        A function that formats all of the demographic data downloaded from the US Census bureau.
        ...
        Parameters
        ----------
        df: A dataframe downloaded from the data
        yr: The year the data is from
        '''
        # Reformat a few of the fields to match the geographic needs and reformat the Year column.
        df.replace({'X':np.nan}, inplace = True)
        df = df.apply(pd.to_numeric, errors='ignore')
        pd.to_numeric(df['WA_MALE'])
        df.insert(0, 'FIPS', (df['STATE']*1000 + df['COUNTY']).astype(str).str.pad(width = 5, side = 'left', fillchar = '0'))
        df['AGEGRP'] = df['AGEGRP'].replace(AGE_CODES)
        df['YEAR'] = df['YEAR'].apply(lambda x: x + (yr - 3))
        df = df[(df['YEAR'] >= yr) & (~df['AGEGRP'].isin(['0_to_4','5_to_9','10_to_14'])) & (df['YEAR'] % 2 == 0)]

        # Get the total population to decompose each group into a percent
        df_out = df[['YEAR','FIPS','TOT_POP']][df['AGEGRP'] == 'Total_Population']
        df_out.rename(columns = {'TOT_POP':'TOT_POP_CNTY'},inplace = True)
        df = df.merge(df_out, on = ['FIPS', 'YEAR'], how = 'left')
        df['TOT_POP_CNTY'] = df['TOT_POP_CNTY'].astype(float)

        # Get state aggregations
        df_state = df[df.columns.difference(['FIPS'])].groupby(['STATE','AGEGRP','YEAR','STNAME']).sum()
        df_state['CTYNAME'] = 'State Level'
        df_state.reset_index(inplace = True)
        df_state.insert(0, 'FIPS', (df_state['STATE']*1000).astype(str).str.pad(width = 5, side = 'left', fillchar = '0'))
        df = pd.concat([df, df_state[list(df)]])

        # Get Demographics as a percentage of age
        out_cols = ['TOT_MALE','TOT_FEMALE']
        df['TOT_MALE'] = round(df['TOT_MALE'] / df['TOT_POP_CNTY'] * 100, 8)
        df['TOT_FEMALE'] = round(df['TOT_FEMALE'] / df['TOT_POP_CNTY'] * 100, 8)

        # Iterate through all of the census columns
        for key, value in CENSUS_FIELDS.items():
            for gender in ['MALE','FEMALE']:
                demo = '%s_%s' % (value, gender)
                df[demo] = df[demo].astype(float)
                df['H_%s' % gender] = df['H_%s' % gender].astype(float)

                if value == 'WA':
                    df[demo] = round((df[demo] - df['H_%s' % gender]) / df['TOT_POP_CNTY'] * 100, 8)
                else:
                    df[demo] = round(df[demo] / df['TOT_POP_CNTY'] * 100, 8)

                out_cols.append(demo)

        return df[['YEAR','FIPS', 'CTYNAME', 'AGEGRP','STATE'] + out_cols]

    def consolidateDemographicData(self):
        """
        The function that iterates through the files and aggregates the demographic information into one file

        """
        # Format all the history files and write them to the output
        HIST_DEMO_PATH = self.raw_demo_data.joinpath('2009')
        demofiles = [f for f in listdir(HIST_DEMO_PATH) if isfile(join(HIST_DEMO_PATH, f))]

        df_out = pd.DataFrame()
        for file_name in demofiles:
            df_tmp = pd.read_csv(HIST_DEMO_PATH.joinpath(file_name),
                        encoding='latin-1')
            df_format = self.formatDemographicData(df_tmp, 2000)
            df_out = pd.concat([df_out, df_format])

        #download the dataframes for the age fields and the census fields
        df_tmp = pd.read_csv(self.raw_demo_data.joinpath('2018','cc-est2018-alldata.csv.gz'),
                        index_col = False,
                        compression = 'gzip',
                        sep='\t',
                        encoding='latin-1')

        # Format the data and add it to the temp path
        df_format = self.formatDemographicData(df_tmp, 2010)
        df_demo = pd.concat([df_out, df_format])

        # Format the Age Groups appropriately
        for grp in list(df_demo)[5:]:
            df_demo.loc[df_demo['AGEGRP'] == '15_to_19', grp] = df_demo[df_demo['AGEGRP'] == '15_to_19'][grp].astype(float) * 2 / 5

        # Aggregate the ages into different groups and filter out people who are too young to vote.  Also filter odd numbered years
        df_demo['AGEGRP'].replace({'15_to_19':'18_to_29', '20_to_24': '18_to_29', '25_to_29':'18_to_29',
                                '30_to_34':'30_to_49', '35_to_39': '30_to_49', '40_to_44': '30_to_49' , '45_to_49': '30_to_49',
                                '50_to_54': '50_to_64', '55_to_59': '50_to_64' , '60_to_64': '50_to_64', '80_to_84': '65+',
                                '65_to_69': '65+', '70_to_74': '65+' , '75_to_79': '65+', '75_to_79': '65+', '85_to_Older': '65+'},
                                inplace = True)
        df_demo = df_demo.groupby(['YEAR','FIPS','AGEGRP'], as_index=False).sum()

        # Create the final Feature dataset per year
        df_demo = pd.pivot_table(df_demo, index = ['YEAR','FIPS', 'STATE'], columns = 'AGEGRP')
        df_demo.columns = ['%s_%s' % (demo, age) for (demo, age) in df_demo.columns]
        df_demo.reset_index(inplace = True)
        df_demo.columns = df_demo.columns.str.replace('+', '_plus').str.lower()
        
        # Write the demographic data to a file
        df_demo.to_csv(self.proc_data.joinpath('demographics.tsv.gz'),
                        compression = 'gzip',
                        mode = 'w',
                        sep='\t',
                        index = False,
                        encoding='utf-8',
                        line_terminator = '\n')
