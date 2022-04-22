##!/usr/bin/env python
""" This script takes together polling data along with demographic data and combines them into one file
"""
#Imports
import pandas as pd
import numpy as np
import json
from pathlib import Path
from os import listdir
from os.path import isfile, join
import warnings
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
party_abbrev = {'REP': 'republican', 'DEM': 'democrat', 'IPD':'independent','LIB':'libertarian'}
office = {'house': 'US House','senate': 'US Senate', 'president':'President'}
pollOut = ['year', 'state_po','FIPS', 'office', 'DISTRICT',
           'special', 'candidate', 'party', 'candidatevotes', 'totalvotes']

class VotingDataFormatter(object):

    def __init__(self, data_path):
        '''
        
        '''
        self.mit_raw_data = data_path.joinpath('raw','voting','mit')
        self.cq_raw_data = data_path.joinpath('raw','voting','cq')
        self.demo_path = data_path.joinpath('raw','demographics')
        self.proc_data = data_path.joinpath('processed')
        self.lkup_data = data_path.joinpath('raw','lookup')

    def formatMITPollingData(self):
        '''
        The function that consolidates the data and writes the output to a tsv file
        '''
        print('Formatting House Data')
        df_house = self.formatMITHouse()
        print('Formatting Senate Data')
        df_senate = self.formatMITSenate()
        print('Formatting Historical Presidential Data')
        df_pres = self.formatMITPresident()
        print('Formatting Current Presidential Data')
        df_2020 = self.format2020MITData()

        print('Write the dataset to the processed data')
        df_polling = pd.concat([df_senate, df_house, df_pres, df_2020])
        df_polling.columns = df_polling.columns.str.lower()

        # Write the file
        df_polling.to_csv(self.proc_data.joinpath('mit_voting.tsv.gz'),
                            compression = 'gzip',
                            mode = 'w',
                            sep='\t',
                            index = False,
                            encoding='utf-8',
                            line_terminator = '\n')

    def formatCQVotes(self):
        '''
        The function that formats all of the CQ voting results (From Governers races, House, Senate and Presidential results).  This writes to the processed file directory
        '''
        print('Getting FIPS Codes')
        df_cnty = self.getFIPSLkp()
        
        print('Formatting Gov Data')
        df_gov = self.formatCQVoteData('gov')
        col_out = list(df_gov)
        
        print('Formatting House Data')
        df_hr = self.formatCQVoteData('hr')
        
        print('Formatting Senate Data')
        df_senate = self.formatCQVoteData('sen')
        df_senate = df_senate[col_out]
        
        print('Formatting Historical Presidential Data')
        df_pres = self.formatCQVoteData('pres')
        df_pres = df_pres[col_out]
        df_output = pd.concat([df_senate, df_gov, df_hr, df_pres])

        print('Reformatting the data')
        df_output = df_output.merge(df_cnty, on = ['state','area_join'], how = 'left')
        for cty_fips, aj in [(46102,'SHANNON'),(51005,'CLIFTONFORGE'),(30122,'SOUTHBOSTON'),(35013,'DONAANA'),(46071,'WASHABAUGH'),(46102,'WASHINGTON'),(46077,'KINGSBURG'),(51800,'NANSEMOND'),(13203,'MILTON')]:
            if aj == 'MILTON':
                df_output.loc[(df_output['area_join'] == aj) & (df_output['state'] == 'Georgia'),'fips'] = cty_fips
            else:
                df_output.loc[(df_output['area_join'] == aj) & df_output['fips'].isnull(),'fips'] = cty_fips

        # Drop the column
        df_output.drop(['area_join'], axis = 1, inplace = True)

        # Write the cq voting data to file
        df_output.to_csv(self.proc_data.joinpath('cq_voting.tsv.gz'),
                            compression = 'gzip',
                            mode = 'w',
                            sep='\t',
                            index = False,
                            encoding='utf-8',
                            line_terminator = '\n')


    def formatMITHouse(self):
        """ 
        A function that gets the historical house data and formats it correctly for consolidation with the other data.  
        ...
        Returns
        ---------
         > A DataFrame with MIT Presidential data
        """
        df = pd.read_csv(self.mit_raw_data.joinpath('House','election_results.tsv.gz'),
                        index_col = False,
                        compression = 'gzip',
                        sep='\t',
                        encoding='latin-1')

        # Map the district to the counties
        df_lkup = pd.read_csv(self.lkup_data.joinpath('cd116','National_CD116.txt'),
                        index_col = False,
                        encoding='latin-1',
                        dtype = {'BLOCKID':np.str})
        
        # Format the file and get rid of all files
        df_lkup['BLOCKID'] = df_lkup['BLOCKID'].str[:5]
        df_lkup.drop_duplicates(inplace = True)
        df_lkup['state_fips'] = df_lkup['BLOCKID'].astype(int) // 1000
        df_lkup.rename(columns={'BLOCKID':'FIPS','CD116': 'DISTRICT'}, inplace = True)
        df = df[(df['writein'] == False) & (df['party'] != 'NA')]
        df.rename(columns = {'district':'DISTRICT'}, inplace = True)

        df = df.merge(df_lkup, on = ['state_fips','DISTRICT'], how = 'left')
        return df[pollOut]

    def formatMITSenate(self):
        """ 
        A function that gets the historical senate data and formats it correctly for consolidation with the other data 
        ...
        Returns
        ---------
         > A DataFrame with MIT Senate data
        """
        df = pd.read_csv(self.mit_raw_data.joinpath('Senate','election_results.tsv.gz'),
                        index_col = False,
                        compression = 'gzip',
                        sep = '\t',
                        encoding='latin-1')
        df = df[(df['writein'] == False) & (df['party'] != 'NA')]
        df.rename(columns = {'district':'DISTRICT'}, inplace = True)

        df['state_fips'] = (df['state_fips']*1000).astype(str).str.pad(width = 5, side = 'left', fillchar = '0')
        df.rename(columns = {'state_fips':'FIPS'}, inplace = True)
        return df[pollOut]

    def formatMITPresident(self):
        """ 
        A function that gets the historical presidential data and formats it correctly for consolidation with the other data and returns the dataframe
        ...
        Returns
        ---------
         > A DataFrame with MIT Presidential data
        """
        df = pd.read_csv(self.mit_raw_data.joinpath('President','election_results.tsv.gz'),
                        index_col = False,
                        compression = 'gzip',
                        sep='\t',
                        encoding='latin-1')

        df = df[df['FIPS'].notnull()]
        df['FIPS'] = df['FIPS'].astype(int).astype(str).str.pad(width = 5, side = 'left', fillchar = '0')
        df.insert(4, 'DISTRICT', 0)
        df.insert(5, 'special', False)
        return df[pollOut]

    def format2020MITData(self):
        """ 
        A function that gets the current presidential voting results and formats it correctly for consolidation with the other data
        ...
        Returns
        ---------
         > A DataFrame with 2020 data
        """
        with open(self.mit_raw_data.joinpath('President','2020_results.json')) as f:
            data = json.load(f)
        df_2020 = pd.DataFrame()
        for race in data['data']['races']:
            candidates = {}
            for person in race['candidates']:
                candidates[person['candidate_key']] =  {'name': person['name_display'],
                                    'party': person['party_id']}
            state = race['state_id']
            office = race['office']
            county_data = []
            for county in race['counties']:
                fips, name, total_votes =  county['fips'], county['name'], county['votes']
                for cand, votes in county['results'].items():
                    results = {'FIPS': fips, 'county_name': name, 'totalvotes': total_votes, 'DISTRICT': 'statewide',
                            'office': office, 'candidatevotes': votes,'year' : 2020, 'special': 'False',
                            'state_po': state, 'candidate': candidates[cand]['name'], 'party': candidates[cand]['party']}
                    county_data.append(results)
            df = pd.DataFrame(county_data)
            df_2020 = pd.concat([df_2020, df[pollOut]])

        return df_2020
    
    def formatCQVoteData(self, office):
        """ 
        A function that gets the historical house data and formats it correctly for consolidation with the other data
        ...
        Parameters
        ----------
        office: The office to get the file from
        ...
        Returns
        ----------
          > a dataframe with the correct format for output
        """
        HIST_PATH = self.cq_raw_data.joinpath(office)
        vote_files = [f for f in listdir(HIST_PATH) if isfile(join(HIST_PATH, f))]

        df_out = pd.DataFrame()
        for file in vote_files:
            df = pd.read_csv(HIST_PATH.joinpath(file),
                            index_col = False,
                            encoding='latin-1')
            df.columns = df.columns.str.lower()
            df.replace({r'\|':',', '\r':'\n'}, regex = True, inplace = True)
            df.rename(columns = {'racedate':'raceyear'}, inplace = True)
            df['raceyear'] = df['raceyear'].astype(str).apply(lambda x: x[:4] if len(x) > 4 else x)
            if office == 'hr':
                df['titlenotes'] = ''
                df['othernotes'] = ''

            for column in list(df):
                if 'percent' in column.lower() or 'votes' in column.lower():
                    df[column] = df[column].astype(str).str.replace('Unopposed', '0').astype(float)

            df_out = pd.concat([df_out, df])
        df_out['area_join'] = df_out['area'].str.upper().str.replace(' CITY','').str.replace(' ','')\
                                            .str.replace('.','').str.replace('\'','').str.replace('/WASHABAUGH','')
        return df_out

    def getFIPSLkp(self):
        """ 
        Get the FIPS lookup per zip code.
        """
        df_tmp = pd.read_csv(self.demo_path.joinpath('2018','cc-est2018-alldata.csv.gz'),
                        index_col = False,
                        compression = 'gzip',
                        sep='\t',
                        encoding='latin-1')

        df = df_tmp[['STATE','STNAME','COUNTY', 'CTYNAME']].drop_duplicates()
        df.insert(0, 'fips', (df['STATE']*1000 + df['COUNTY']).astype(str).str.pad(width = 5, side = 'left', fillchar = '0'))
        df['CTYNAME'] = df['CTYNAME'].replace({' County':''}, regex = True)
        df['CTYNAME'] = df['CTYNAME'].str.upper()
        df.rename(columns = {'CTYNAME':'area','STNAME':'state'}, inplace = True)
        df['area_join'] = df['area'].str.upper().str.replace(' CITY','').str.replace(' PARISH','')\
                                    .str.replace(' ','').str.replace('.','').str.replace('\'','').str.replace('/WASHABAUGH','')
        return df[['fips','area_join','state']]