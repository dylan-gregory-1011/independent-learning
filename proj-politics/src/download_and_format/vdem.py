##!/usr/bin/env python
""" This script takes the V-Dem Democratic measurements and formats the data for analysis

"""
#Imports
import pandas as pd
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
RENAME_COLS = {'v2paenname':'party',
               'country_name':'country_name',
               'year':'year',
               'v2xpa_illiberal':'illiberalism',
               'v2xpa_popul':'populism',
              'v2pagovsup':'government_support',
              'v2paanteli': 'anti_elitism',
              'v2papeople': 'people_centrism',
              'v2paopresp': 'political_opponents_respect',
              'v2paplur': 'political_pluralism',
              'v2paminor':'observes_minority_rights',
              'v2paviol': 'rejection_of_political_violence',
              'v2paimmig': 'supports_immigration',
              'v2palgbt': 'lgbt_social_equality',
              'v2paculsup': 'opposes_cultural_superiority',
              'v2parelig': 'invokes_religious_principles',
              'v2pagender': 'gender_equality_representation',
              'v2pawomlab':'working_women',
              'v2pariglef': 'economic_right_leaning_scale',
              'v2pawelf': 'suppors_welfare',
              'v2paclient': 'clientelism',
               'v2pasalie_0':'importance_anti_elitism',
               'v2pasalie_1':'importance_people_centrism',
               'v2pasalie_2':'importance_political_pluralism',
               'v2pasalie_3':'importance_observes_minority_rights',
               'v2pasalie_4':'importance_supports_immigration',
               'v2pasalie_5':'importance_lgbt_social_equality',
               'v2pasalie_6':'importance_opposes_cultural_superiority',
               'v2pasalie_7':'importance_invokes_religious_principles',
               'v2pasalie_8':'importance_gender_equality_representation',
               'v2pasalie_9':'importance_suppors_welfare',
               'v2pasalie_10':'importance_economic_issues',
               'v2pasalie_11':'importance_clientelism',
               'v2pasalie_12':'importance_envirnomental_protection',
               'v2pasalie_13':'importance_farmers_issues',
              'v2pasalie_14':'importance_leader',
              'v2pasalie_15':'importance_anti_corruption',
              'v2pasalie_16':'importance_intimidation',
              'v2pagroup_0':'main_support_not_observable',
              'v2pagroup_1':'main_support_aristocracy',
              'v2pagroup_2':'main_support_agrarian_elites',
              'v2pagroup_3':'main_support_business_elites',
              'v2pagroup_4':'main_support_military',
              'v2pagroup_5':'main_support_racial',
              'v2pagroup_6':'main_support_religious',
              'v2pagroup_7':'main_support_local_elites',
              'v2pagroup_8':'main_support_working_class_urban',
              'v2pagroup_9':'main_support_middle_class_urban',
              'v2pagroup_10':'main_support_working_class_rural',
              'v2pagroup_11':'main_support_middle_class_rural',
              'v2pagroup_12':'main_support_separatists',
              'v2pagroup_13':'main_support_woman',
              'v2paactcom':'local_organizational_strength',
              'v2pasoctie':'affiliate_organizations',
              'v2padisa':'internal_cohesion',
              'v2paind':'leader_personalization_of_party',
              'ep_antielite_salience':'importance_anti_establishment_rhetoric',
              'ep_corrupt_salience':'importance_reducing_political_corruption',
              'ep_members_vs_leadership':'leader_controls_party_policy',
              'ep_people_vs_elite':'people_over_elite_decisions',
              'ep_type_populism':'populism_type',
              'ep_type_populist_values':'populist_values_type',
              'ep_v8_popul_rhetoric':'favors_populist_rhetoric',
              'ep_v9_popul_saliency':'importance_populism',
              'ep_galtan':'authoritarian_position',
              'ep_galtan_salience':'importance_libertarian',
              'ep_v6_lib_cons':'social_conservative_values',
               'ep_v7_lib_cons_saliency':'importance_social_values'}

ORDINAL_REPLACE = {'populism_type': {1: 'strongly_pluralist', 
                                     2:'moderately_pluralist',
                                     3:'moderately_populist', 
                                     4:'strongly_populist'},
                   'populist_values_type':{1: 'pluralist_liberal', 
                                          2: 'pluralist_conservative',
                                          3: 'populist_liberal', 
                                          4: 'populist_conservative'}}

class VDemFormatter(object):

    def __init__(self, data_path):
        """
        An object that ingests different V Dem data and outputs it to the proper format
        ...
        Parameters
        ----------
        data_path: The datapath for the project
        
        """
        self.raw_data = data_path.joinpath('raw','v-dem')
        self.proc_data = data_path.joinpath('processed')

    def formatPartyData(self):
        '''
        The function that reformats the v-dem party data into a compressed tsv
        '''
         # Get the Presidential Polling data
        df_parties = pd.read_csv(self.raw_data.joinpath('V-Dem-CPD-Party-V1.csv'),
                            index_col = False,
                            encoding='utf-8')

        # Select the columns to use and rename them based upon the english definitions
        df_pol_out = df_parties[list(RENAME_COLS.keys())]
        df_pol_out = df_pol_out.rename(RENAME_COLS, axis = 1)

        # Replace the Ordinal Values
        for key in ORDINAL_REPLACE.keys():
            df_pol_out[key].replace(to_replace = ORDINAL_REPLACE[key], inplace = True)

        # Replace the Pipe Delimited values
        #df_pol_out['party_name_short'] = df_pol_out['party_name_short'].str.replace("|",'')
        df_pol_out['party'] = df_pol_out['party'].apply(lambda x: x.split(' ')[0].lower())
        
        # Write the file to a compressed tsv
        df_pol_out.to_csv(self.proc_data.joinpath('vdem_party.tsv.gz'),
                            sep = '\t',
                            encoding = 'utf-8',
                            compression = 'gzip',
                            index = False)
