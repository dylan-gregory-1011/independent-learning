# Project Bard: Next Sentance Prediction with Shakespeare

For the pinnacle of english communication, one needs to look no further than the bard, otherwise known as William Shakespeare.  This project looks to use current language translations of shakespeare's play to create a model that can reply to any delcaration with old english texts.  Deconstructing language into a mathmatical representation so that it can feed a generalizable model requires an understanding of both individual words and the flow of ideas.  Accomplishing this with State of the Art transformers reflects current best practices in the industry and this project will hopefully build on these approaches and improve long-term idea connectivity.

## Process Steps:

1. **Download the Data:** The data for this project was downloaded from [No Fear Shakespeare](https://www.sparknotes.com/shakespeare/) which is a website that displays not only the original text from Shakespeare's plays but the current translations to contemporary english.  For more information on this process, please see the [python scraper](src/shakespeare_download.py) 
2. **Format and Optimize Storage:** With the raw data downloaded, the text was cleansed, tagged with pertinent meta-data and dropped into a processed bucket.


## Research Notes:
- Next Sentance Prediction appears to be a standard binary classification algorithm that distinguishes the original following sentence from a bunc of randomly associated sentances.


### Helpful Links:
- [Example: GFG NSP Using BERT Full Flow](https://www.geeksforgeeks.org/next-sentence-prediction-using-bert/)
- [Example: NSP Using BERT](https://towardsdatascience.com/bert-for-next-sentence-prediction-466b67f8226f)
- [Initial Paper for NSP](https://aclanthology.org/D19-1586.pdf)
- [Beautiful Soup Example](https://programminghistorian.org/en/lessons/intro-to-beautiful-soup)