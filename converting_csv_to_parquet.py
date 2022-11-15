#*************************************
# Created by: Rovenna Chu (ytc17@sfu.ca)
# Purpose: this is for converting csv files (previously crawled) to parquet files
# This program will read all csv files in a directory and convert all files in the directory to parquet files - output files will also be in the same directory
# usage: python3 converting_csv_to_parquet.py folder_name
#*************************************

import sys
import os
import glob

from schema import columns
import pandas as pd


try:
    script_folder = os.path.dirname(__file__)
except NameError:
    script_folder = "."
directory = f"{script_folder}data"
extension = 'csv'
 
if __name__ == '__main__':
    
    if len(sys.argv) == 2:
        directory = f"{script_folder}"+sys.argv[1]

    print('start conversion...')

    os.chdir(directory)
    csv_list = glob.glob('*.{}'.format(extension))
    
    #print(*csv_list, sep = "\n")
    for file in csv_list:
        s = "{}/{}".format(directory, file)
        
        print("./"+s)
        print()
        
        df = pd.read_csv("./"+s)

        tmp = file.split(".", 1)
        df.to_parquet(directory+'/' + tmp[0] + ".parquet")
    