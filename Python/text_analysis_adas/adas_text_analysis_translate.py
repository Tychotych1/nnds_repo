# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 13:15:46 2019

@author: svvdb
"""

#%% Import libraries
import os
import pandas as pd
from pattern.en import sentiment, tag
from pattern.en import parse, pprint
#from pattern.en import attributive, predicative
from pattern.en import conjugate, lemma, lexeme
from pattern.en import parsetree
from pattern.en import wordnet
from pattern.en import ADJECTIVE, NOUN
from google.cloud import translate
from google.oauth2 import service_account
import html

#%% Set credentials and create translate object
path = "C:/Users/svvdb/OneDrive/Documents/Github/nnds_datascience/Python/text_analysis_adas/"
credentials = service_account.Credentials.from_service_account_file(path + "api_key.json")
translate_client = translate.Client(credentials = credentials)

#%% Set directory and load data
os.chdir(path)
df = pd.read_excel("Voorbeeldzinnen.xlsx", encoding = 'utf8')

#%% Iterate through rows
### Pattern is outdated. In python 3.7 RuntimeError: generator raised StopIteration. 
### Op de een of andere manier werkt het wel na elke RuntimeError een keer opnieuw te runnen. 
### Werkt in python 3.6 wel goed.

for index, row in df.iterrows():
        
    text = df.at[index, 'Melding']
    
    ######################### Translate #########################
    translation = translate_client.translate(text, target_language='en')
    text_eng = html.unescape(translation['translatedText'])

    df.at[index, 'Melding_engels'] = text_eng
    
    ######################### Sentiment analysis #########################
    sent, subj = sentiment(text_eng)
    
    df.at[index, 'Sentiment'] = sent
    df.at[index, 'Subjectivity'] = subj
    
    if sent > 0.1:        
        berichtgeving = 'Positief'    
    elif sent < -0.1: 
        berichtgeving = 'Negatief'        
    else:        
        berichtgeving = 'Neutraal'
    
    df.at[index, 'Berichtgeving'] = berichtgeving
    
    if subj > 0.25:
        vorm = 'Mening'
    else:
        vorm = 'Feit'
        
    df.at[index, 'Vorm'] = vorm
    
    ######################### Part-of-speech tagging #########################
    text_tagged = tag(text_eng)
    noun_list = []
    
    for word_pos in text_tagged:        
        pos = word_pos[1]
        
        if pos in ['VBD', 'VBN']:                
            tijd = 'Verleden'            
            break            
        else:                
            tijd = 'Heden'
    
    df.at[index, 'Tijd'] = tijd
    
    i = 0
    for word_pos in text_tagged:      
        pos = word_pos[1]
        
        if pos in ['NN', 'NNS', 'NNP', 'NNPS']:
            i += 1
            noun = word_pos[0]
            df.at[index, 'ZNW_{}'.format(i)] = noun
          
    ######################### Zinsdelen #########################
    s = parsetree(text_eng, relations = True, lemmata = True)
    
    i = 0
    for sentence in s:
        
        for chunk in sentence.chunks:
            
            if chunk.type == 'NP' and len(chunk.words) > 1:
                                
                chunk_nounphrase = ''                                
                for word in chunk.words:
                    
                    if str(word).lower() not in ['the', 'a', 'an']:
                                                
                        if chunk_nounphrase == '':
                            chunk_word = word.string
                            chunk_nounphrase = chunk_word
                        else:
                            chunk_word = word.string
                            chunk_nounphrase = chunk_nounphrase + ' ' + chunk_word
                    
                if ' ' in chunk_nounphrase:
                    i += 1
                    df.at[index, 'Zinsdeel_{}'.format(i)] = chunk_nounphrase
                    
#%% Synsets and Synonyms
def synonymFinder(Word, Word_type = NOUN):
    
    synset = wordnet.synsets(Word, pos=Word_type)
    synset_list = []
    gloss_list = []
    
    for i in range(0, len(synset), 1):
        
        for j in range(0, len(synset[i].synonyms), 1):            
            synset_list.append(synset[i].synonyms[j])
            gloss_list.append(synset[i].gloss)
        
    df_synonyms = pd.DataFrame({'Synoniem': synset_list, 'Definitie': gloss_list})
    
    return df_synonyms

Word = "Condition"
Word_type = NOUN #NOUN, VERB, ADJECTIVE, ADVERB

df_synonyms = synonymFinder(Word, Word_type)

