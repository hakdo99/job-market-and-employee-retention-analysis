# *************************************
# Created by: Kukpyo (Andrew) Han  - kha107@sfu.ca
# Created on: March 10, 2022
# Last Updated on: April 1, 2022
# Objective: This python code is intended to consolidate all the job posts obtained from the 4 platforms,
#            remove duplicate job records using Jaccard Similarity (based on job title / company / location),
#            and output a single parquet file.
# Input files (before processing): located under "/preprocessing_parquet"
# Input files (after processing): located under "/preprocessing_parquet/archive"
# Output files : located under "/integrated_parquet"
# *************************************

# pip or conda to install pyarrow
# pip or conda to install fastparquet

import pandas as pd
import numpy as np
import glob
import os
import re
from datetime import datetime


def convert_to_tokens(input_str):
    output_tokens = []
    lowered_str = input_str.lower()
    output_tokens = re.split(r"\W+", lowered_str)

    # Remove empty strings from the list
    filter_object = filter(lambda x: x != "", output_tokens)
    output_tokens = list(filter_object)

    return output_tokens


def calculate_jaccard_similarity(input_list_x, input_list_y):
    # This function is designed to get jaccard similarity score,
    # the number of intersected set of values is to be divided by the number of unionized set of values.
    num_total_union = len(set(input_list_x) | set(input_list_y))
    num_matching_intersection = len(set(input_list_x) & set(input_list_y))
    jaccard_value = num_matching_intersection / num_total_union

    return jaccard_value

# This is a function that will determine if the value is NaN
def isNaN(num):
    return num != num


class SimilarityJoin:
    def __init__(self, dataframe_1, dataframe_2):
        # Performing a deep copy because whatever changes made to the dataframes are \
        # only applicable within the class.
        self.df1 = dataframe_1.copy()
        self.df2 = dataframe_2.copy()

    def preprocess_df(self, df, cols):
        # concatenate the $cols in $df
        df["concatenated"] = df[[cols[0], cols[1], cols[2]]].apply(lambda x: ' '.join(x.dropna()), axis=1)
        # apply the tokenizer to the concatenated string
        df['joinKey'] = df["concatenated"].map(lambda a: convert_to_tokens(a))
        # Return a new DataFrame that adds the "joinKey" column to the input $df
        return df

    def filtering(self, df1, df2):
        # Remove unnecessary fields.
        df1_working_set = df1[['id', 'joinKey']]
        df2_working_set = df2[['id', 'joinKey']]

        # flatten the list of keywords for both dataframes
        df1_joinkey_flattened = pd.DataFrame(
            [(index, value) for (index, values) in df1_working_set['joinKey'].iteritems()
             for value in values
             ], columns=['index', 'joinKey_word']
        ).set_index('index')
        df2_joinkey_flattened = pd.DataFrame(
            [(index, value) for (index, values) in df2_working_set['joinKey'].iteritems()
             for value in values
             ], columns=['index', 'joinKey_word']
        ).set_index('index')
        df1_flattened = df1_working_set.join(df1_joinkey_flattened)
        df2_flattened = df2_working_set.join(df2_joinkey_flattened)

        # Perform inner join of the 2 dataframes
        df_merged = df1_flattened.merge(df2_flattened, left_on='joinKey_word', right_on='joinKey_word')
        df_final = df_merged.drop_duplicates(['id_x', 'id_y'], keep='first').reset_index(drop=True)

        # Rename columns and drop unnecessary fields.
        cand_df = df_final.drop(['joinKey_word'], axis=1).rename(columns={"id_x": "id1", "joinKey_x": "joinKey1",
                                                                          "id_y": "id2", "joinKey_y": "joinKey2"})

        # Return a new DataFrame $cand_df with four columns: 'id1', 'joinKey1', 'id2', 'joinKey2'
        return cand_df

    def verification(self, cand_df, threshold):
        # Calculating Jaccard similarity scores for each pair of word sets.
        cand_df["jaccard"] = cand_df.apply(lambda x: calculate_jaccard_similarity(x['joinKey1'], x['joinKey2']), axis=1)
        # $result_df removes the rows whose jaccard similarity is smaller than $threshold
        result_df = cand_df[cand_df['jaccard'].astype('float') >= threshold]

        # Output: Return a new DataFrame $result_df that represents the ER result.
        #         It has five columns: id1, joinKey1, id2, joinKey2, jaccard
        return result_df


    def jaccard_join(self, cols, threshold):
        new_df1 = self.preprocess_df(self.df1, cols)
        new_df2 = self.preprocess_df(self.df2, cols)
        print("Before filtering: %d pairs in total" % (self.df1.shape[0] * self.df2.shape[0]))

        cand_df = self.filtering(new_df1, new_df2)
        print("After Filtering: %d pairs left" % (cand_df.shape[0]))

        result_df = self.verification(cand_df, threshold)
        print("After Verification: %d similar pairs" % (result_df.shape[0]))

        return result_df


def reduce_duplicate_jobposts(prim_df, sec_df, dup_pairs):

    # Reduced_df is intended to hold a single record after the merger of two duplicate records
    reduced_records = []

    # Iterate over each pair and combine them into one record.
    for dup_pair in dup_pairs:
        prim_row = prim_df[prim_df["id"] == dup_pair[0]]
        sec_row = sec_df[sec_df["id"] == dup_pair[1]]

        # If either of the rows does not exist, it means they were removed during the previous loop.
        both_exist = (not prim_row.empty) and (not sec_row.empty)

        # Reduce the records only if both records exist.
        if both_exist:
            reduced_rec = {}
            # Aggregate information from both sources to have more complete information about the role.
            for (colname, colval) in prim_row.iteritems():
                if isNaN(colval.values[0]):
                    if isNaN(sec_row[colname].values[0]):
                        reduced_rec[colname] = np.nan
                    else:
                        reduced_rec[colname] = sec_row[colname].values[0]
                else:
                    reduced_rec[colname] = colval.values[0]

            # Add the aggregated information into the "reduced_records" set
            reduced_records.append(reduced_rec)

        # drop the job post from both dataframes.
        prim_df.drop(prim_df[prim_df["id"] == dup_pair[0]].index, inplace=True)
        sec_df.drop(sec_df[sec_df["id"] == dup_pair[1]].index, inplace=True)

    # Reduced_df is intended to hold a single record after the merger of two duplicate records
    reduced_df = pd.DataFrame(reduced_records, columns=prim_df.columns)

    # Combine all the three dataframes (prim_df + sec_df + reduced_df) into output_df
    output_df = pd.concat([prim_df, sec_df, reduced_df], ignore_index=True)

    return output_df



if __name__ == "__main__":

    INPUT_PATH = r'preprocessing_parquet/'
    CSV_PATH = r'preprocessing_parquet/archive_csv/'
    OUTPUT_PATH = r'integrated_parquet/'
    all_files = glob.glob(INPUT_PATH + "*.parquet")
    # This timestamp will be used to generate a unique identification number for job posts.
    TIMESTAMP = datetime.today().strftime("%Y%m%d%H")
    # The following column names will be used for the removal of duplicate records. (Excluding "id")
    col_names = ['job_title', 'job_type', 'job_exp', 'company', 'industries',
                 'location', 'source', 'search_kw', 'expected_salary', 'post_date',
                 'job_function', 'remote', 'job_summary', 'description']

    # li is used to hold dataframes taken from the preprocessing_parquet folder.
    li = []
    # li_processed is used to hold processed dataframes.
    li_processed = []

    print('============================== Read in the parquet files ===================================')

    for filename in all_files:
        # df = pd.read_csv(filename, index_col=None, header=0)
        df = pd.read_parquet(filename, columns=None)

        # Extract the file name from the full path.
        filename_tmp1 = filename.split("\\")
        # Extract the file name without the extension
        filename_tmp2 = filename_tmp1[1].split(".")
        df.to_csv(CSV_PATH + filename_tmp2[0] + '.csv')
        li.append(df)

    print('============================== Read in the parquet files (completed) ===================================')

    print('============================== Perform Preprocessing ===================================')
    # Perform pre-processing on respective dataframes before running the jaccard similarity
    for idx, df in enumerate(li):

        print(all_files[idx])
        print(f'Number of Records before drop_duplicates(): {df.shape[0]}')
        # Remove duplicate records. (When there are exactly same job posts within each dataset)
        df = df.drop_duplicates(col_names, keep='first').reset_index(drop=True)
        print(f'Number of Records after drop_duplicates(): {df.shape[0]}')

        # Replace the empty string to NaN
        df = df.replace(r'^\s*$', np.NaN, regex=True)
        # Restore the city name "Montreal"
        #df["location"] = df["location"].apply(lambda a: str(a).replace('Montr??al', 'Montreal'))

        # If the id field is empty, assign a unique identification number
        if df["id"].isnull().all():
            df = df.reset_index()
            df['id'] = df['index'].apply(lambda a: TIMESTAMP + "_" + str(idx) + "_" + str(a))
            df = df.drop(columns=['index'])

        if np.issubdtype(df["post_date"].dtype, np.datetime64):
            df["post_date"] = df["post_date"].apply(lambda a: a.strftime("%Y-%m-%d"))

        li_processed.append(df)

    print('============================== Perform Preprocessing (completed) ===================================')

    print('============================== Perform Jaccard Similarity ===================================')
    # Initialize the base dataframe with the first dataframe.
    df_base = li_processed[0].copy()
    cols_for_comparison = ["job_title", "company", "location"]

    for idx in range(1, len(li_processed)):

        df_comparing = li_processed[idx].copy()

        er = SimilarityJoin(df_base, df_comparing)
        # Running it over a number of datasets, threshold 0.8 was most optimal to effectively identify
        # duplicate records.
        duplicate_df = er.jaccard_join(cols_for_comparison, 0.8)

        # Get a list of pairs identified as duplicate and combine them into a single row.
        duplicate_pairs = duplicate_df[['id1', 'id2']].values.tolist()
        print(f"Duplicate Pairs Identified for Iteration {idx}: ", duplicate_pairs)

        df_base = reduce_duplicate_jobposts(df_base, df_comparing, duplicate_pairs)

    result_df = df_base

    print('============================== Perform Jaccard Similarity (completed) ===================================')

    # Save the integrated dataframe into parquet.
    result_df.to_csv(OUTPUT_PATH + "integrated_" + TIMESTAMP + ".csv")
    result_df.to_parquet(OUTPUT_PATH + "integrated_" + TIMESTAMP + ".parquet")
    print('The parquet file containing the integrated dataset has been successfully saved.')

    print('============================== Move the processed files to archive ===================================')

    # Move the processed parquet files to archive folder.
    for filename in all_files:
        # Extract the file name from the full path.
        filename_tmp1 = filename.split("\\")
        # Source file path
        source = filename
        # destination file path
        dest = INPUT_PATH + "archive/" + filename_tmp1[1]

        try:
            os.rename(source, dest)
            print(f"{filename_tmp1[1]} : Source path renamed to destination path successfully.")
        # For permission related errors
        except PermissionError:
            print("Operation not permitted.")
        # For other errors
        except OSError as error:
            print(error)

    print('============================== Move the processed files to archive (completed) ====================='
          '=============')
