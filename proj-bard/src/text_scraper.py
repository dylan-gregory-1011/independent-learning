##!/usr/bin/env python
"""
    This file downloads, formats and cleanses Shakespeare data from the Sparknotes No-fear collection
    ...
    Functions
    __________
    api_call(url, headers) -> response: This function moderates all of the api calls
    extractTextFromTable(tbl_row) -> text: Using a table cell, get the proper text from the play
    getNoFearData(play) : Iterate through all of the acts/scenes in an associated play
    applyThemesToPlays() : Taking predefined themes, apply them to the plays and datasets


    The processed data gets dumped into json file as well as a mongodb database for easier querying.  The mongodb commands used to create the 
    collection are below
    create > db.createCollection("collected_works", {storageEngine : {wiredTiger :{configString :'block_compressor=zstd'}}})
    ix > db.collected_works.createIndex({"PLAY":"text","ACT":1, "SCENE":1, "ACTION_NBR": 1}, {sparse: true})

"""
from curses import raw
from pathlib import Path
import requests
import os
import json
import time
import sys
from bs4 import BeautifulSoup
import random
from unidecode import unidecode
from random import randrange
from string import digits
import re
from fuzzywuzzy import fuzz
import pymongo

__author__ = "Dylan Smith"
__copyright__ = "Copyright (C) 2021 Dylan Smith"
__credits__ = ["Dylan Smith"]

__license__ = "Personal Use"
__version__ = "1.0"
__maintainer__ = "Dylan Smith"
__email__ = "-"
__status__ = "Development"

# Constants
PROJ = Path(__file__).resolve().parent.parent.parent
URL_BASE = 'https://www.sparknotes.com/nofear/shakespeare/%s/act-%i-scene-%i/'
PROC_DATA = PROJ.joinpath('data','bard', 'processed')
RAW_DATA = PROJ.joinpath('data','bard', 'raw','no-fear')

# HERNY 5 has prologue, Romeo and Juliet has a prologue # Taming of Shrew has Introduction, # Tempest has an epilogue
# Problem w. Henry 5 Act 3 scene 7
PLAYS = {'antony': 'antony-and-cleopatra',
            'hamlet':'hamlet',
            'macbeth':'macbeth',
            'asyoulikeit':'as-you-like-it',
            'errors':'comedy-of-errors',
            'coriolanus':'coriolanus',
            'henry4pt1':'henry-iv-i',
            'henry4pt2': 'henry-iv-ii',
            'henryv': 'henry-v',
            'juliuscaesar':'julius-ceaser',
            'lear':'king-lear',
            'measure-for-measure': 'measure-for-measure',
            'merchant':'merchant-of-venice',
            'msnd':'a-midsummer-nights-dream',
            'muchado':'much-ado-about-nothing',
            'othello':'othello',
            'richardii':'richard-ii',
            'richardiii':'richard-iii',
            'romeojuliet':'romeo-and-juliet',
            'shrew':'taming-of-the-shrew',
            'tempest':'the-tempest',
            'twelfthnight':'twelfth-night',
            'twogentlemen':'two-gentleman-of-verona',
            'winterstale':'the-winters-tale'}

# URL and String Constants
HEADERS = {'User-agent': 'my-app/0.0.1'}
REGEX = re.compile('[^a-zA-Z]')

# MongoDB Constants
MONGO = pymongo.MongoClient("mongodb://127.0.0.1:27017")['shakespeare']
MONGO.command( "compact", 'collected_works')
WORKS_COL = MONGO['collected_works']

def api_call(url, headers):
    """ 
    The function that calls the api for both the history and fundamental information
    ...
    Parameters
    ----------
    url: The play to download from the source
    headers: API Headers to pass on the request call
    ----------
    Example: api_call(url = '', headers = HEADERS)
    ----------
    Returns: content from an api call
    """
    while True:
        try: #iterate through and if a timeout exception is reached, try again
            api_data = requests.get(url, headers= headers, timeout=(10, 30))
            break
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.ConnectionError:
            pass

    while api_data.status_code != 200:
        if api_data.status_code == 400:
            return 'Bad Call'
        if api_data.status_code == 404:
            print("Error webpage not found")
            return None
        elif api_data.status_code == 429:
            print('RateLimit')
            time.sleep(20)
        
        #recall the api request
        time.sleep(2)

        api_data = requests.get(url, headers= headers, timeout=(10, 30))
    
    return api_data


def extractTextFromTable(tbl_row):
    '''
    Takes the row extracted from the page table and extracts the correct speaker, both modern and not for the dataset.
    ...
    Parameters
    ----------
    tbl_row: An beautifulsoup row to be processed.
    ----------
    Example: extractTextFromTable(tbl_row = row)
    ----------
    Returns: Four Strings with the below order
        1. Modern Play Text
        2. Original Play Text
        3. Modern Play Speaker
        4. Original Play Speaker
    '''

    speakers = []
    txt_out = []
    # Check if a title, if so, skip out
    classes = list(set([y for x in [x['class'] for x in tbl_row.find_all('td')] for y in x]))

    if 'noFear__cell--title' in classes or len(classes) == 0:
        return None, None, None, None

    for time_pd in ['modern','original']:
        # Iterate between modern and non-modern text
        cell = tbl_row.find('td', {'class': 'noFear__cell noFear__cell--%s' %  time_pd})
        
        
        # first check if this is a stage value
        txt_vals = cell.find_all('div',{'class': ['noFear__stage noFear__stage--%s' %  time_pd, 
                                                  'noFear__stage noFear__stage--%s noFear__stage--hasLineNumber' %  time_pd]})

        if len(txt_vals) == 0:
            # check if value is speaker, if the speach was interupted there will be no speaker
            speaker = cell.find('p', {'class':'noFear__speaker'})
            if speaker is None:
                speaker = 'INTERRUPTED_SPEACH'
            else:
                speaker = speaker.get_text().strip()

            txt_vals = cell.find_all('div',{'class': ['noFear__line noFear__line--%s' %  time_pd,
                                                  'noFear__line noFear__line--%s noFear__line--hasLineNumber' %  time_pd]})
            
            # Some lines are dropped, get normal lines
            if len(txt_vals) == 0:
                txt_vals = cell.find_all('line')
            
            if len(txt_vals) == 0:
                txt_vals = cell.find('em')
                speaker = 'STAGE_TEXT'
        else:
            speaker = 'STAGE_TEXT'
        
        if txt_vals is None:
            txt = unidecode(cell.get_text())
        else:
            txt = re.sub('[0-9]+', '',unidecode(" ".join([y for x in [x.get_text().split() for x in txt_vals] for y in x])))
    
        txt_out.append(txt)
        speakers.append(speaker)

    return txt_out[0], txt_out[1] , speakers[0], speakers[1]
     

def getNoFearData(play):
    """   
    Function that downloades the No Fear Shakespeare data from sparknotes and formats the data into json
    ...
    Parameters
    ----------
    play: The play to download from the source
    ----------
    Example: getNoFearData(play = 'othello')
    """
    line_nbr, action_nbr = 0 , 0
    play_txt, line_txt = [], {"PLAY":PLAYS[play].upper()}
    LAST_ORIG_SPEAKER, LAST_MOD_SPEAKER = '', ''

    # TODO: Update the download script to capture the change in the 
    for act in range(1,6):
        line_txt['ACT'] = act
        for scene in range(1,25):
            line_txt['SCENE'] = scene
            url = URL_BASE  % (play, act, scene)
            time.sleep(randrange(20))
            
            #format text from Beautiful Soup
            doc_text = api_call(url, HEADERS)
            if doc_text is None:
                break
            
            print('Formatting data for Act %i, Scene %i' % (act, scene))
            soup = BeautifulSoup(doc_text.text, "lxml")
            
            #with open(PROC_DATA.joinpath('test_file.txt'), 'w', encoding='utf-8') as f_out:
            #    f_out.write(soup.prettify())
            #with open(PROC_DATA.joinpath('test_file.txt')) as f:
            #    soup = BeautifulSoup(f.read())
            
            # Extract the tables from the object and define the required classes
            tables = soup.findAll("table")
            for table in tables:
                if table.findParent("table") is None:
                    rows = table.find_all("tr")
                    for row in rows:
                        # Get the speaker from the cell
                        MOD_TXT, ORIG_TXT, MOD_SPEAKER, ORIG_SPEAKER  = extractTextFromTable(tbl_row= row)
                        
                        if ORIG_TXT is None or len(ORIG_TXT) == 0:
                            continue

                        # increment value number
                        action_nbr +=1
                        if ORIG_SPEAKER not in ['INTERRUPTED_SPEACH','STAGE_TEXT']:
                            LAST_ORIG_SPEAKER = ORIG_SPEAKER
                            LAST_MOD_SPEAKER = MOD_SPEAKER
                            

                        if ORIG_SPEAKER != 'STAGE_TEXT':
                            line_nbr +=1
                            line_txt['LINE_NBR'] = line_nbr
                        else:
                            line_txt['LINE_NBR'] = 0
                        
                        if ORIG_SPEAKER == 'INTERRUPTED_SPEACH':
                            ORIG_SPEAKER = LAST_ORIG_SPEAKER
                            MOD_SPEAKER = LAST_MOD_SPEAKER

                        # Define values in the dictionary
                        line_txt['ORIGINAL_TEXT'] = ORIG_TXT
                        line_txt['ORIGINAL_SPEAKER'] = ORIG_SPEAKER
                        line_txt['MODERN_TEXT'] = MOD_TXT
                        line_txt['MODERN_SPEAKER'] = MOD_SPEAKER
                        
                        line_txt['ACTION_NBR'] = action_nbr

                        play_txt.append(line_txt.copy())

    with open(RAW_DATA.joinpath('%s.json' % (PLAYS[play].upper())), 'w') as f:
        json.dump(play_txt, f)

def applyThemesToPlays():
    """ 
    Function that goes through the downloaded Shakespeare plays and applies the themes downloaded from the internet
    to the json data.
    ...
    Parameters
    ----------
    None
    ----------
    Example: applyThemesToPlays()
    """
    # Download both the shakespeare plays and the themes.
    with open(PROC_DATA.joinpath('themes.json'), 'r', encoding="utf-8") as f:
        themes = json.load(f)

    # Get a list of all the plays in the file
    play_texts = [x for x in RAW_DATA.glob('**/*') if x.is_file()]

    # Iterate over the different plays and read each from the raw directory
    for play_path in play_texts:
        # Get the play name from the file
        play_nm = play_path.name.split('.')[0]
        print('Formatting the data for the play %s' % play_nm)  
        # Read the play text
        with open(RAW_DATA.joinpath('%s.json' % play_nm), 'r') as f:
            play_text = json.load(f)
        
        if play_nm in themes.keys():
            # Iterate over all the different themes
            for theme in themes[play_nm].keys():
    
                # Go through all the different quotes in the plays
                for quote in themes[play_nm][theme]:
                    quotes_base = ''.join([i for i in quote if i.isalpha()])
                    len_quote = len(quote.split(' '))
                    found = False

                    # go through each row in the play
                    for row in play_text:
                        # With the quote stripped try to match the quote with the associated value
                        row_stripped = ''.join([i for i in row['ORIGINAL_TEXT'].lower() if i.isalpha()])
                        if quote.lower() in row['ORIGINAL_TEXT'].lower() or quotes_base.lower() in row_stripped:
                            if "THEME" in row.keys():
                                row['THEME'].append(theme)
                            else:
                                row['THEME'] = [theme]
                                found = True
                                break
                    
                    if found:
                        continue

                    # if the quote isn't found above, go through the play again and use fuzzy matching to get the most likely match from the plays
                    max_match = 0
                    for row in play_text:
                        len_line = len(row['ORIGINAL_TEXT'].split(' '))
                        if len_quote > 1.1 * len_line:
                            continue
                        for i in range(0,len_line - len_quote):
                            quote_check = ' '.join(row['ORIGINAL_TEXT'].split(' ')[i: i + len_quote])
                            if fuzz.ratio(quote_check, quote) > max_match:
                                max_match = fuzz.ratio(quote_check, quote)
                                line_found = row['LINE_NBR']
                    
                    # Go through all of the plays and associate the theme with the line number in the play
                    for row in play_text:
                        if row['LINE_NBR'] == line_found:
                            if "THEME" in row.keys():
                                row['THEME'].append(theme)
                            else:
                                row['THEME'] = [theme]

        # Write to a cleansed json file
        with open(PROC_DATA.joinpath('no-fear',"%s.json" % play_nm), 'w') as f:
            json.dump(play_text, f)
    
        # Delete the object if it exists in the dataframe
        WORKS_COL.delete_many({'PLAY' : {'$eq': play_nm}})
        WORKS_COL.insert_many(play_text)

def main():
    # Specify whether we are downloading the text data or applying the themes
    process = sys.argv[1]
    if process not in ['download','cleanse_themes','download_and_cleanse']:
        print("Please input a valid runtime option (download, cleanse_themes or download_and_cleanse)")
        return 

    if process in ['download','download_and_cleanse']:
        for play in PLAYS.keys():
            if play in ['antony','hamlet', 'macbeth']:
                continue
            
            print('Downloading the data for Play %s' % play)
            getNoFearData(play)

    if process == 'cleanse_themes':
        applyThemesToPlays()

if __name__ == '__main__':
    main()
    