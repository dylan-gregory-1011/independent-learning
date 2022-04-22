##!/usr/bin/env python
"""
 Campaign Finance Downloader
"""

#Imports
from pathlib import Path
import pandas as pd
import sys
from download_and_format import FECBulkDownloader, IndicatorDataFormatter, DemographicDataFormatter, GDPFormatter, VotingDataFormatter, VDemFormatter

__author__ = "Dylan Smith"
__copyright__ = "Copyright (C) 2019 Dylan Smith"
__credits__ = ["Dylan Smith"]

__license__ = "Personal Use"
__version__ = "1.0"
__maintainer__ = "Dylan Smith"
__email__ = "-"
__status__ = "Development"

#constants
PROJ = Path(__file__).resolve().parent.parent.parent
DATA_PATH = PROJ.joinpath('data','politics')

def downloadCampaignFinanceData(full_load = False):
    '''
    To download campaign finance data from the FEC, either update the current election cycle or download all files
    ...
    Parameters
    ----------
    full_load: Whether to download all files or just update the current files
    '''
    # Instantiate FEC Downloader
    fec_downloader = FECBulkDownloader(proj_data= DATA_PATH)
    for dataset in ['CANDIDATE_MASTER','CANDIDATE_COMMITTEE','COMMITTEE_MASTER','CONTRIBUTION_COMMITTEE_CANDIDATE','INDIVIDUAL_SUMMARY']:
        if full_load:
            # Get data for 1970 to 1998
            for yr in range(80, 99, 2):
                # Pass datasets that don't have data in this time frame
                if dataset in ['CANDIDATE_COMMITTEE']:
                    break
                elif dataset == 'CONTRIBUTION_COMMITTEE_CANDIDATE' and yr < 82:
                    continue

                print('Downloading %s data for the cycle %i' % (dataset, yr))
                fec_downloader.downloadAndFormatFECBulkData(dataset, yr)

            # Get data for 2000 to 2022
            for yr in range(0, 23, 2):
                print('Downloading %s data for the cycle %i' % (dataset, yr))
                fec_downloader.downloadAndFormatFECBulkData(dataset, yr, download_data= True)
            break
        else:
            # get data for the current cycle
            fec_downloader.downloadAndFormatFECBulkData(dataset, 22)

def formatIndicatorAndEmploymentData():
    '''
    A function that formats the indicator data (Employment, Culture, and Education)
    '''
    indicator_formater = IndicatorDataFormatter(data_path= DATA_PATH)
    print('Formatting Culture Data')
    indicator_formater.formatCultureData()
    print('Finished formatting Culture Data, now formatting Employment Data')
    indicator_formater.formatEmploymentData()
    print('Finished formatting employment data, now formatting education data')
    indicator_formater.formatEducationData()
    print('Finished formatting education data and all other indicator files')

def formatDemographicData():
    """
    A function that formats the demographic data from the US Census Bureau.
    """
    print('Formatting Demographic Data from the US Census Bureau')
    demo_formatter = DemographicDataFormatter(data_path= DATA_PATH)
    demo_formatter.consolidateDemographicData()
    print('Demographic data has been formatted')

def formatGDPData():
    """
    Format the GDP data output
    """
    print('Formatting GDP Data')
    gdp_formatter = GDPFormatter(data_path= DATA_PATH)
    gdp_formatter.processGDPData()
    print('Demographic data has been formatted')

def formatVotingData():
    '''
    Format the MIT and CQ Voting Data
    '''
    voting_formatter = VotingDataFormatter(data_path= DATA_PATH)
    print('Formatting MIT Data')
    voting_formatter.formatMITPollingData()
    print('Formatted MIT data.  Moving to format CQ data')
    voting_formatter.formatCQVotes()
    print('Finished formatting voting data')

def formatVDEMData():
    '''
    
    '''
    print('Format VDEM Data')
    vdem_formatter = VDemFormatter(data_path= DATA_PATH)
    vdem_formatter.formatPartyData()
    print('Finished Formatting VDem Data')

def consolidateVotingDemographicAndIndicatorData():
    '''
    
    '''
    print('Getting Culture Data')
    df_vote = pd.read_csv(DATA_PATH.joinpath('processed','mit_voting.tsv.gz'),
                        compression = 'gzip',
                        sep = '\t',
                        index_col = False,
                        encoding = 'utf-8',
                        lineterminator = '\n')
    print(df_vote.columns)
    df_cult = pd.read_csv(DATA_PATH.joinpath('processed','culture.tsv.gz'),
                        compression = 'gzip',
                        sep = '\t',
                        index_col = False,
                        encoding = 'utf-8',
                        lineterminator = '\n')

    df_gdp = pd.read_csv(DATA_PATH.joinpath('processed','gdp.tsv.gz'),
                        compression = 'gzip',
                        sep = '\t',
                        index_col = False,
                        encoding = 'utf-8',
                        lineterminator = '\n')

    df_employ = pd.read_csv(DATA_PATH.joinpath('processed','employment.tsv.gz'),
                        compression = 'gzip',
                        sep = '\t',
                        index_col = False,
                        encoding = 'utf-8',
                        lineterminator = '\n')

    df_demo = pd.read_csv(DATA_PATH.joinpath('processed','demographics.tsv.gz'),
                        compression = 'gzip',
                        sep = '\t',
                        index_col = False,
                        encoding = 'utf-8',
                        lineterminator = '\n')

    df_edu = pd.read_csv(DATA_PATH.joinpath('processed','education.tsv.gz'),
                        compression = 'gzip',
                        sep = '\t',
                        index_col = False,
                        encoding = 'utf-8',
                        lineterminator = '\n')
    
    df_vdem = pd.read_csv(DATA_PATH.joinpath('processed','vdem_party.tsv.gz'),
                        compression = 'gzip',
                        sep = '\t',
                        index_col = False,
                        encoding = 'utf-8',
                        lineterminator = '\n')

    df_vote['year_join'] = df_vote['year'].astype('int') // 10 * 10
    df_vote['year_join'] = df_vote['year_join'].replace(2020, 2010)
    # Bring together the dataframes and filter out AK & HI
    df_agg = df_vote[(~df_vote['state_po'].isin(['AK','HI'])) & (df_vote['year'] >= 2000)]\
                    .merge(df_cult, on = ['fips','year_join'], how = 'left')
    df_agg.drop('state', inplace = True, axis = 1)
    
    print('Format GDP Data')
    df_gdp.rename({'yr':'year'}, axis = 1, inplace = True)
    df_agg = df_agg.merge(df_gdp, on = ['fips','year'], how = 'left')

    print('Getting Employment Data')
    df_employ.rename({'yr':'year'}, axis = 1, inplace = True)
    df_employ.drop(columns = 'state', inplace = True)
    df_agg = df_agg.merge(df_employ, on = ['fips','year'], how = 'left')

    print('Getting Demographic Data')
    df_agg = df_agg.merge(df_demo, on = ['fips','year'], how = 'left')
    
    print('Getting Education Data')
    df_edu.rename({'year':'year_join'}, axis = 1, inplace = True)
    df_agg = df_agg.merge(df_edu, on = ['fips','year_join'], how = 'left')
    df_agg.drop('year_join', inplace = True, axis = 1)

    # Get the Education Data
    df_vdem = df_vdem[df_vdem['country_name'] == 'United States of America']
    df_agg = df_agg.merge(df_vdem, on = ['party','year'], how = 'left')
    df_agg = df_agg.groupby('fips').apply(lambda x: x.ffill().bfill())

    # Get rid of null values and convert the year to an integer
    df_agg = df_agg[~df_agg['year'].isnull()]
    df_agg['year'] = df_agg['year'].astype('int')

    print('Writing data to the consolidated file output')
    df_agg.to_csv(DATA_PATH.joinpath('processed','voting_demographic.tsv.gz'),
                compression = 'gzip',
                mode = 'a',
                sep='\t',
                index = False,
                encoding='utf-8',
                line_terminator = '\n')

def main(download_to_run= None):
    if download_to_run == 'demographic':
        formatDemographicData()
    elif download_to_run == 'indicator':
        formatIndicatorAndEmploymentData()
    elif download_to_run == 'voting':
        formatVotingData()
    elif download_to_run == 'campaign':
        downloadCampaignFinanceData()
    elif download_to_run == 'vdem':
        formatVDEMData()
    elif download_to_run == 'consolidate_data':
        consolidateVotingDemographicAndIndicatorData()
    elif download_to_run == 'campaign-full':
        downloadCampaignFinanceData(full_load = True)
    elif download_to_run == 'gdp':
        formatGDPData()

if __name__ == '__main__':
    #import the process to run
    main(download_to_run = sys.argv[1])