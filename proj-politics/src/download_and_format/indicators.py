##!/usr/bin/env python
""" This script takes together polling data along with demographic data and combines them into one file

"""
#Imports
from pathlib import Path
import pandas as pd
from os import listdir
from os.path import isfile, join
import numpy as np
import warnings
warnings.filterwarnings('ignore')

__author__ = "Dylan Smith"
__copyright__ = "Copyright (C) 2020 Dylan Smith"
__credits__ = ["Dylan Smith"]

__license__ = "Personal Use"
__version__ = "1.0"
__maintainer__ = "Dylan Smith"
__email__ = "-"
__status__ = "Development"

# Constants
EMPLOY_SECTOR_REPLACE = {'AGRICULTURAL SERVICES, FORESTRY, AND FISHING':'FORESTRY, FISHING, AND RELATED ACTIVITIES', 'MINING':'MINING, QUARRYING, AND OIL AND GAS EXTRACTION', 'TRANSPORTATION AND PUBLIC UTILITIES':'TRANSPORTATION AND WAREHOUSING', 'FINANCE, INSURANCE, AND REAL ESTATE':'FINANCE AND INSURANCE', 'SERVICES':'OTHER SERVICES (EXCEPT GOVERNMENT AND GOVERNMENT ENTERPRISES)'}


class IndicatorDataFormatter(object):

    def __init__(self, data_path):
        '''
        An object that formats the indicator data and stores processed data into the correct format
        ...
        Parameters
        ----------
        data_path: The path where all of the formatted political data is located.
        '''
        self.raw_indi_path = data_path.joinpath('raw','indicators')
        self.raw_employ_path = data_path.joinpath('raw','employment')
        self.proc_data = data_path.joinpath('processed')

    def formatCultureData(self):
        """ 
        A function that formats the different cultural regions and ouputs the data for consumption and writes to an output table
        """
        df_culture = pd.read_csv(self.raw_indi_path.joinpath('regions.csv'),
                            index_col = False,
                            encoding='latin-1',
                            dtype = {'FIPS':np.str})

        df_county = pd.read_csv(self.raw_indi_path.joinpath('Rural_Atlas_Update22','County Classifications.tsv.gz'),
                        index_col = False,
                        compression = 'gzip',
                        sep='\t')
        
        # Format the County file
        df_county.rename({'ï»¿FIPStxt':"FIPS"}, axis = 'columns', inplace = True)
        df_county['FIPS'] = df_county['FIPS'].astype(str).str.pad(width = 5, side = 'left', fillchar = '0')

        # Format the Rural Urban Continuum
        df_county = df_county[['FIPS'] + ['%s%s' % (col, yr) for yr in [2003,2013] for col in ['RuralUrbanContinuumCode','UrbanInfluenceCode','Metro','Nonmetro','Micropolitan']]]
        df_county.columns = df_county.columns.str.replace("2003", "2000s").str.replace('2013','2010s')

        df_culture = df_county.merge(df_culture, on = 'FIPS', how = 'left')
        df_culture.loc[df_culture['REGION'].isnull(),'REGION'] = 12
        df_culture.loc[df_culture['DESCRIPTION'].isnull(),'DESCRIPTION'] = 'HI & AK'

        df_cult_out = pd.DataFrame()
        for yr in [2000, 2010]:
            df_tmp = df_culture[['FIPS','State','REGION','DESCRIPTION']]
            df_tmp['year_join'] = yr
            for col in ['RuralUrbanContinuumCode','UrbanInfluenceCode','Metro','Nonmetro','Micropolitan']:
                df_tmp[col] = df_culture[col + str(yr) + 's']
            df_cult_out = pd.concat([df_cult_out, df_tmp])

        # Rename the column names
        df_cult_out.columns = df_cult_out.columns.str.lower()
        df_cult_out.to_csv(self.proc_data.joinpath('culture.tsv.gz'),
                            sep = '\t',
                            encoding = 'utf-8',
                            compression = 'gzip',
                            index = False)

    def outputCleanEmploymentValues(self, df_emp):
        """ 
        A function that outputs each of the employment datasets for merging into later datasets
        ...
        Parameters
        ----------
        df_emp: The dataframe with the prior employment data
        """
        df_emp.rename(columns = {'GeoFIPS':'FIPS'}, inplace = True)
        df_emp.drop(columns = ['GeoName','Region','TableName','IndustryClassification','Unit','LineCode'], inplace = True)
        df_emp = df_emp[~df_emp['FIPS'].str.replace("\"",'').apply(pd.to_numeric, errors='coerce').isna()]
        df_emp['FIPS'] = df_emp['FIPS'].str.replace('\"','').str.strip()
        df_emp['Description'] = df_emp['Description'].str.strip().str.upper()
        return df_emp

    def formatEmploymentData(self):
        """
        A function that formats the employment data based on the files added to the raw directory
        """
        # Format all the history files and write them to the output
        df_empHist = pd.read_csv(self.raw_employ_path.joinpath('CAEMP25S__ALL_AREAS_1969_2000.csv'),
                        index_col = False,
                        encoding = 'latin-1',
                        dtype = {'LineCode':np.str})

        # Format all the history files and write them to the output
        df_empCurr = pd.read_csv(self.raw_employ_path.joinpath('CAEMP25N__ALL_AREAS_2001_2018.csv'),
                        index_col = False,
                        encoding = 'latin-1',
                        dtype = {'LineCode':np.str})

        df_income = pd.read_csv(self.raw_indi_path.joinpath('Rural_Atlas_Update22', 'Income.tsv.gz'),
                    index_col = False,
                    compression = 'gzip',
                    sep='\t')
        # Read Files necessary for Unemployment Analysis
        df_unemp = pd.read_excel(self.raw_indi_path.joinpath('Unemployment.xls'),
                        index_col = False)

        df_empHist = self.outputCleanEmploymentValues(df_emp = df_empHist)
        df_empHist['Description'] = df_empHist['Description'].replace(EMPLOY_SECTOR_REPLACE)
        df_empCurr = self.outputCleanEmploymentValues( df_emp = df_empCurr)

        df_employment = df_empCurr.merge(df_empHist, how = 'left', on = ['FIPS','Description'])
        # Reverse Pivot the years into rows and take care of formatting issues for the below pivot
        df_employment = pd.melt(df_employment, id_vars = ['FIPS','Description'])
        df_employment.rename(columns = {'variable':'YR'}, inplace = True)
        df_employment['value'] = df_employment['value'].str.replace('\(NA\)','').str.replace('\(D\)','')
        df_employment['value'] = df_employment['value'].apply(lambda x: float(x) if x != '' else np.nan)

        # Pivot the table to get years as the rows and employment as the column values
        df_employment = df_employment.pivot(index = ['FIPS','YR'], columns = 'Description')
        df_employment.reset_index(inplace = True)
        df_employment.columns = ['FIPS','YR'] + [y for (x,y) in df_employment.columns[2:]]
        df_employment['YR'] = df_employment['YR'].astype(int)

        # Get percentage of employment for each county for each year
        for sector in list(df_employment)[2:]:
            if sector == 'TOTAL EMPLOYMENT (NUMBER OF JOBS)':
                continue
            df_employment[sector] = df_employment[sector].astype(float) / df_employment['TOTAL EMPLOYMENT (NUMBER OF JOBS)'].astype(float)

        # Select the desired columns the income values and rename to reflect the current status
        df_income.rename({'ï»¿FIPS':"FIPS"}, axis = 'columns', inplace = True)
        df_income = df_income[['FIPS','State','MedHHInc','PerCapitaInc','PovertyUnder18Pct','PovertyAllAgesPct',
                                'Deep_Pov_All', 'Deep_Pov_Children' ]]
        df_income.columns = ['FIPS','State'] + ['Curr_%s' % col for col in df_income.columns[2:]]
        df_income['FIPS'] = df_income['FIPS'].astype(str).str.pad(width = 5, side = 'left', fillchar = '0')

        # Reverse Pivot the years into rows and take care of formatting issues for the below pivot
        df_unemp = df_unemp[['FIPS','State'] + ['Unemployment_rate_%s' % yr for yr in range(2007,2019)]]
        df_unemp = pd.melt(df_unemp, id_vars = ['FIPS','State'])
        df_unemp.rename(columns = {'value': 'Unemployment_Rate', 'variable':'YR'}, inplace = True)
        df_unemp['YR'] = df_unemp['YR'].str.replace('Unemployment_rate_','').astype(int)
        df_unemp['FIPS'] = df_unemp['FIPS'].astype(str).str.pad(width = 5, side = 'left', fillchar = '0')

        # Format the dataframes and merge them to form one output
        df_employ = df_unemp.merge(df_income, on = ['FIPS','State'], how = 'left').\
                            merge(df_employment, on = ['FIPS','YR'], how = 'left')
        # rename columns
        df_employ.columns = df_employ.columns.str.replace(' ', '_').str.replace(',','').str.replace('(','')\
                                            .str.replace(')','').str.replace('/','').str.lower()

        # Write to a file
        df_employ.to_csv(self.proc_data.joinpath('employment.tsv.gz'),
                            sep = '\t',
                            encoding = 'utf-8',
                            compression = 'gzip',
                            index = False)

    def formatEducationData(self):
        """ 
        A function that formats and returns the education data in an output format
        """
        df_edu = pd.read_excel(self.raw_indi_path.joinpath('Education.xls'),
                    index_col = False)

        # Format and select the appropriate columns
        df_edu = df_edu[['FIPS','State'] + [col for col in df_edu.columns if 'percent' in col.lower() or 'PCT_' in col]]
        df_edu = df_edu[['FIPS','State'] + [col for col in df_edu.columns if 'percent' in col.lower() or 'PCT_' in col]]
        df_edu.columns = df_edu.columns.str.replace('Percent of adults with less than a high school diploma, ', 'PCT_LESS_HS_')\
                            .str.replace('Percent of adults with a high school diploma only, ','PCT_HS_')\
                            .str.replace('Percent of adults completing some college \(1-3 years\),', 'PCT_SOME_BA_')\
                            .str.replace('Percent of adults completing four years of college or higher, ', 'PCT_EQ_MORE_BA_')\
                            .str.replace("Percent of adults completing some college or associate's degree, ", 'PCT_SOME_BA_')\
                            .str.replace("Percent of adults with a bachelor's degree or higher,", 'PCT_EQ_MORE_BA_')\
                            .str.replace("13_17", '2010').str.replace(' ','')

        # Pivot the formatting to the year level
        df_edu_out = pd.DataFrame()
        for yr in ['1970', '1980', '1990', '2000', '2010']:
            df_yrs = df_edu[['FIPS','State']]
            df_yrs["year"] = int(yr)
            for edu_lvl in ['PCT_LESS_HS_%s','PCT_HS_%s','PCT_SOME_BA_%s','PCT_EQ_MORE_BA_%s']:
                df_yrs[edu_lvl.replace('_%s','')] = df_edu[edu_lvl % yr]
            df_edu_out = pd.concat([df_edu_out, df_yrs])
        
        # Rename the column names
        df_edu_out.columns = df_edu_out.columns.str.lower()
        
        # Write the file out
        df_edu_out.to_csv(self.proc_data.joinpath('education.tsv.gz'),
                            sep = '\t',
                            encoding = 'utf-8',
                            compression = 'gzip',
                            index = False)
