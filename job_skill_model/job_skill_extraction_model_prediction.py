#*************************************
# Created by: Rovenna Chu (ytc17@sfu.ca)
# Job Skill Extraction for all Job Market Data in Project
# Purpose: this is for extracting job skills from job posts crawled across all job market platforms (LinkedIn, Workoplis, Indeed and Glassdoor)
# This program will read all job posts data from MongoDB and extract the job skills from each job posts
# The resulting skills extracted will be attached to the original job posts / separate table containing only job title - skill pairs
#- Input: Parquet file with all job posts consolidated in single batch crawl
#- Output: All job posts with corresponding skills extracted into Mongodb
# usage: python3 job_skill_extraction_model_prediction.py model/job_skill_extraction_bert.h5
#*************************************

# Prerequisite
#1. For model build
#pip install contractions
#pip install bert-for-tf2
#pip install tqdm
#pip install tensorflow_hub
#pip install --upgrade tensorflow

#2. For pre-processing and tokenization
#pip install -U pip setuptools wheel
#pip install -U spacy
#python -m spacy download en_core_web_lg

import sys
import os
import glob

import pandas as pd
import numpy as np

# Import model related classes and functions
from job_skill_extraction_model import PaddingInputExample
from job_skill_extraction_model import InputExample
from job_skill_extraction_model import create_tokenizer_from_hub_module
from job_skill_extraction_model import convert_single_example
from job_skill_extraction_model import convert_examples_to_features
from job_skill_extraction_model import convert_text_to_examples
from job_skill_extraction_model import BertModel
#from job_skill_extraction_model import PreprocessingBertData
from job_skill_extraction_model import NetworkModel

from job_skill_extraction_data_processing import *

# Configuration for reading the job posts
colab_used = False

if colab_used:
    from google.colab import drive
    drive.mount('/content/drive')

input_path_colab = "/content/drive/MyDrive/SFU/CMPT733/project/"
input_path_lab = ""

INPUT_PATH = input_path_colab if colab_used else input_path_lab

# get current directory
cur_path = os.getcwd()
# obtain the upper directory
PARENT_PATH = os.path.abspath(os.path.join(cur_path, os.pardir)) + "\\"

INPUT_FILE_FOLDER = "postprocessing_parquet\\archive\\"
all_files = glob.glob(PARENT_PATH + INPUT_FILE_FOLDER + "*.parquet")
# input_file = "Indeed_Manufacturing Director_Canada_2022032809.parquet"

# Set the default input model.
INPUT_MODEL = "model\\job_skill_extraction_bert.h5"

DESTINATION_FOLDER = "job_skill_prediction\\"

threshold = 0.5     #previous is 0.5

if __name__ == '__main__':
    
    # Get model name
    if len(sys.argv) == 2:
        INPUT_MODEL = str(sys.argv[1])

    # Read job posts
    print('============================== Read in the parquet files ===================================')

    df = pd.DataFrame()

    for filename in all_files:
        cur_df = pd.read_parquet(filename, columns=None)
        df = pd.concat([df, cur_df], ignore_index=True)

    print('============================== Read in the parquet files (completed) ===================================')

    # Pre-processing
    source_df = data_preparation_preprocessing(df)

    # Extract tokens
    extract_exps = [extract_noun_phrase, extract_adp, extract_adp_2, extract_adp_conj, extract_verb_maybeadj_noun]
    df_ents = extract_df(source_df, *extract_exps, n_max=source_df.shape[0], label_list=EXP_TERMS)
    df_ents_valid = df_ents[(~df_ents.text.str.lower().str.contains(experience_qualifier_pattern)) & # Not a qualifier
                         ~df_ents.text.isin(stopwords)]

    input_df = df_ents_valid[["text", "label", "job_title"]]

    # Post-processing
    input_df = data_preparation_postprocessing(input_df)

    # Group text - just in case of any duplication in entries
    consolidated_df = input_df[["text", "job_title"]].drop_duplicates()

    input_text = consolidated_df.to_numpy()[:, np.newaxis]

    # Instantiate tokenizer
    tokenizer = create_tokenizer_from_hub_module()

    # Convert data to InputExample format
    input_examples = convert_text_to_examples(input_text, np.zeros((len(input_text),1)))

    # Convert to features
    (input_ids, input_masks, segment_ids, labels 
    ) = convert_examples_to_features(tokenizer,
                                     input_examples,
                                     max_seq_length = 18)
                                     
    # Build and Load Model
    model = None

    bert_model_obj = BertModel()

    model = NetworkModel()
    model.bert_model(bert_model_obj, bert_model_obj.max_len)

    # Load existing model
    model.load_weights(INPUT_PATH+INPUT_MODEL)  # Load the selected input model.
    
    # Extract job skills
    save_preds = model.get_model().predict([input_ids, input_masks, segment_ids] )


    predictions = pd.DataFrame(dict(list(zip(consolidated_df["text"].to_numpy(), save_preds))))

    # Convert to desired format for saving
    consolidated_df['prediction_prob'] = save_preds
    consolidated_df['predicted_skill'] = (consolidated_df['prediction_prob'] >= threshold).astype('int8')
    
    # Export to destination for storage
    # consolidated_df.to_csv(DESTINATION_FOLDER + "results_job_title_predicted_skills_{}.csv".format(pd.datetime.now().strftime("%Y-%m-%d %H%M%S")))
    consolidated_df.to_parquet(DESTINATION_FOLDER + "job_title_predicted_skills_{}.parquet".format(
        pd.datetime.now().strftime("%Y-%m-%d %H%M%S")))
    