##!/usr/bin/env python3

""" 

    This script downloads campaign finance data from the FECs website.
    Notes: The committee master data has mixed datatypes
"""

#Imports
import pandas as pd
import numpy as np
import os
import zipfile
import os.path
import urllib.request
import shutil
import pyarrow as pa
import pyarrow.parquet as pq

__author__ = "Dylan Smith"
__copyright__ = "Copyright (C) 2019 Dylan Smith"
__credits__ = ["Dylan Smith"]

__license__ = "Personal Use"
__version__ = "1.0"
__maintainer__ = "Dylan Smith"
__email__ = "-"
__status__ = "Development"

#constants
HEADER_RENAMES = {
    "CANDIDATE_MASTER": {"CAND_ID": "candidate_identification",
                        "CAND_NAME":"candidate_name",
                        'CAND_PTY_AFFILIATION':"party_affiliation",
                        'CAND_ELECTION_YR':"year_of_election",
                        'CAND_OFFICE_ST':"candidate_state",
                        'CAND_OFFICE':"candidate_office",
                        'CAND_OFFICE_DISTRICT':"candidate_district",
                        'CAND_ICI':"incumbent_challenger_status",
                        'CAND_STATUS':"candidate_status",
                        'CAND_PCC':"principal_campaign_committee_id",
                        'CAND_ST1':"mailing_address_1",
                        'CAND_ST2':"mailing_address_2",
                        'CAND_CITY':"mailing_address_city",
                        'CAND_ST':"mailing_address_state",
                        'CAND_ZIP':"mailing_address_zip"},
    "CANDIDATE_COMMITTEE":{"CAND_ID":"candidate_identification",
                        "CAND_ELECTION_YR":"candidate_election_year",
                        "FEC_ELECTION_YR":"fec_election_year",
                        "CMTE_ID":"committee_identification",
                        "CMTE_TP":"committee_type",
                        "CMTE_DSGN":"committee_designation",
                        "LINKAGE_ID":"linkage_identification"},
    "COMMITTEE_MASTER":{"CMTE_ID":"committee_identification",
                        "CMTE_NM":"committee_name",
                        "TRES_NM":"treasurers_name",
                        "CMTE_ST1":"mailing_address_st1",
                        "CMTE_ST2":"mailing_address_st2",
                        "CMTE_CITY":"mailing_address_city",
                        "CMTE_ST":"mailing_address_state",
                        "CMTE_ZIP":"mailing_address_zip",
                        "CMTE_DSGN":"committee_designation",
                        "CMTE_TP":"committee_type",
                        "CMTE_PTY_AFFILIATION":"committee_party",
                        "CMTE_FILING_FREQ":"filing_frequency",
                        "ORG_TP":"interest_group_category",
                        "CONNECTED_ORG_NM":"connected_organization_name",
                        "CAND_ID":"candidate_identification"},
    "INDIVIDUAL_SUMMARY":{"CMTE_ID":"filer_identification_number",
                        "AMNDT_IND":"ammendment_indicator",
                        "RPT_TP":"report_type",
                        "TRANSACTION_PGI":"primary_general_indicator",
                        "IMAGE_NUM":"image_number",
                        "TRANSACTION_TP":"transaction_type",
                        "ENTITY_TP":"entity_typ",
                        "NAME":"contributor_name",
                        "CITY":"contributor_city",
                        "STATE":"contributor_state",
                        "ZIP_CODE":"contributor_zip",
                        "EMPLOYER":"contributor_employer",
                        "OCCUPATION":"contributor_occupation",
                        "TRANSACTION_DT":"transaction_date",
                        "TRANSACTION_AMT":"transaction_amount",
                        "OTHER_ID":"other_identification_number",
                        "TRAN_ID":"transaction_id",
                        "FILE_NUM":"file_number",
                        "MEMO_CD":"memo_code",
                        "MEMO_TEXT":"memo_text",
                        "SUB_ID":"fec_record_number"},
    "CONTRIBUTION_COMMITTEE_CANDIDATE": {"CMTE_ID":"filer_identification_number",
                                "AMNDT_IND":"amendment_indicator",
                                "RPT_TP":"report_type",
                                "TRANSACTION_PGI":"primary_general_indicator",
                                "IMAGE_NUM":"image_number",
                                "TRANSACTION_TP":"transaction_type",
                                "ENTITY_TP":"entity_type",
                                "NAME":"contributor_name",
                                "CITY":"contributor_city",
                                "STATE":"contributor_state",
                                "ZIP_CODE":"contributor_zip",
                                "EMPLOYER":"contributor_employer",
                                "OCCUPATION":"contributor_occupation",
                                "TRANSACTION_DT":"transaction_date",
                                "TRANSACTION_AMT":"transaction_amount",
                                "OTHER_ID":"other_identification_number",
                                "CAND_ID":"candidate_identification",
                                "TRAN_ID":"transaction_id",
                                "FILE_NUM":"file_number",
                                "MEMO_CD":"memo_code",
                                "MEMO_TEXT":"memo_text",
                                "SUB_ID":"fec_record_number"}
                                }
LINKS = {"CANDIDATE_COMMITTEE":"ccl",
        "CANDIDATE_MASTER":"cn",
        "CONTRIBUTION_COMMITTEE_CANDIDATE":"pas2",
        "COMMITTEE_MASTER":"cm",
        "INDIVIDUAL_SUMMARY":"indiv"}

class FECBulkDownloader(object):

    def __init__(self, proj_data):
        '''
        An object that downloads data from the FEC and stores it in a parquet dataframe for later analysis
        ...
        Parameters
        ----------
        proj_data: The Directory that stores all politics data
        '''
        self.raw_data = proj_data.joinpath('raw','campaign-finance')
        self.proc_data = proj_data.joinpath('processed','campaign-finance')

    def downloadAndFormatFECBulkData(self,data_typ, yr, download_data = True):
        """ 
        A Function that downloads the bulk-data from the FEC campaign-finance dataset and stores it in a parquet file in the correct directory.
        ...
        Parameters
        ----------
        data_typ: The source of the data to download
        yr: The associated Year we want to download
        download_data = True
        """
        url_abbrev = LINKS[data_typ]
        if yr <= 50:
            cent = 20
        else:
            cent = 19
        
        # Zero-pad the string to ensure the correct URL
        yr = str(yr).rjust(2, '0')

        file = '%s-%i%s' % (url_abbrev, cent, yr)
        URL = "https://www.fec.gov/files/bulk-downloads/%i%s/%s%s.zip"  % (cent, yr, url_abbrev, yr)
        NEW_DIR_NM = data_typ.replace('_','-').lower()
        FILE_PATH = self.raw_data.joinpath(NEW_DIR_NM,'%s.txt.gz' % file)
        COL_NAMES = list(HEADER_RENAMES[data_typ.upper()].keys())
        TMP_PATH = self.raw_data.joinpath('tmp.zip')

        # If a download is required, download the data
        if download_data:
            if data_typ != 'INDIVIDUAL_SUMMARY':
                chunks = pd.read_csv(URL, sep = '|', chunksize = 100000, names = COL_NAMES, encoding = 'latin_1', compression = 'zip')
                mode, header = 'w', True
                for df in chunks:
                    df.to_csv(FILE_PATH,
                            sep = '|',
                            header = header,
                            encoding = 'utf-8',
                            compression = 'gzip',
                            mode = mode,
                            index = False)
                    header, mode = False, 'a'
            else:
                with urllib.request.urlopen(URL) as response, open(TMP_PATH, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)

                # Write the temp file into the a dataframe
                with zipfile.ZipFile(TMP_PATH) as z:
                    with z.open('itcont.txt') as zfile:
                        chunks = pd.read_csv(zfile,
                                        sep = '|',
                                        names = COL_NAMES,
                                        encoding = 'latin_1',
                                        chunksize = 200000,
                                        on_bad_lines='skip')

                        mode, header = 'w', True
                        for df in chunks:
                            df.to_csv(FILE_PATH,
                                    sep = '|',
                                    header = header,
                                    encoding = 'utf-8',
                                    compression = 'gzip',
                                    mode = mode,
                                    index = False)
                            header, mode = False, 'a'
                    os.unlink(TMP_PATH)

        chunks = pd.read_csv(FILE_PATH,
                            sep = '|',
                            compression = 'gzip',
                            encoding = 'utf-8',
                            chunksize = 200000)

        if 'TRANSACTION_DT' in COL_NAMES:
            # Delete partiion if exists
            parquet = True
            shutil.rmtree(str(self.proc_data.joinpath('%s' % NEW_DIR_NM,'file_nm=%s' % file)), ignore_errors=True)
        else:
            parquet = False

        for df in chunks:
            df['file_nm'] = file
            df = df.replace(to_replace= r'[^0-9a-zA-Z]+', value= '-', regex=True)
            df.rename(columns = HEADER_RENAMES[data_typ], inplace = True)

            if parquet:
                df['orig_transaction_date'] = df['transaction_date'].copy()
                df['transaction_date'] = df['transaction_date'].astype(dtype = int, errors='ignore')
                df['transaction_date'] = df['transaction_date'].fillna(12311901)

                # Format the Zip Codes succesfully
                df['contributor_zip'] = df['contributor_zip'].apply(lambda x: str(x)[:5] + '-' + str(x)[5:] if len(str(x)) == 9 else str(x))
                df['transaction_date'] = pd.to_datetime(df['transaction_date'], format = '%m%d%Y',errors='coerce')
                # Set values for year
                df['transaction_year'] = df['transaction_date'].dt.year
                df['transaction_year'] = df['transaction_year'].replace(np.nan, 1901)
                df['transaction_year'] = df['transaction_year'].astype('int')

                # Set values for month
                df['transaction_month'] = df['transaction_date'].dt.month
                df['transaction_month'] = df['transaction_month'].replace(np.nan, 12)
                df['transaction_month'] = df['transaction_month'].astype('int')
                # Convert the data to a string
                for col in list(df):
                    df[col] = df[col].astype('str')

                df['transaction_amount'] = df['transaction_amount'].str.replace('[a-zA-Z]', '0', regex = True)
                df['transaction_amount'] = df['transaction_amount'].astype('float')

                print('Writing table to parquet')
                table = pa.Table.from_pandas(df, preserve_index=False)
                pq.write_to_dataset(table, root_path = str(self.proc_data.joinpath('%s' % NEW_DIR_NM)),
                            partition_cols = ['file_nm','transaction_year', 'transaction_month'], compression = 'GZIP')
            else:
                # Read the file if it exists
                file_nm = self.proc_data.joinpath('%s.tsv.gz' % data_typ.lower())
                if os.path.exists(file_nm):
                    df_init = pd.read_csv(file_nm,
                            compression = 'gzip',
                            sep = '\t',
                            index_col = False,
                            encoding = 'utf-8',
                            lineterminator = '\n')
                    
                    # Concatenate the two dataframes and drop the duplicates
                    df = pd.concat([df_init, df])
                    df = df.drop_duplicates(keep = "first").reset_index(drop= True)        

                # Write the dataframe to the file
                df.to_csv(file_nm,
                        compression = 'gzip',
                        mode = 'w',
                        sep='\t',
                        index = False,
                        encoding='utf-8',
                        line_terminator = '\n')