
import csv
import pandas as pd
import numpy as np
import time
import os

def hms(seconds):
    h = seconds // 3600
    m = seconds % 3600 // 60
    s = seconds % 3600 % 60
    return '{:02d}:{:02d}:{:02d}'.format(h, m, s)


def print_progress_bar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    if iteration == total: 
        print()

def join_csv_files():
    file_name = "OUTPUT_Article_Topics_IDs_" + str(time.time())[:10] + ".csv"

    df1 = pd.read_csv("_output/clavis_topics.csv")
    df2 = pd.read_csv("_output/klangoo_topics.csv")

    df3 = df1.merge(df2, on=["id"], how='outer')
    df3.to_csv("_output/{}".format(file_name),index=False)

def get_list():
    file_names = os.listdir('_input/')
    return file_names

def remove_output_files():
    print("Removing unneeded files in output folder...")
    file_names = os.listdir('_output/')
    for file in file_names:
        if "OUTPUT" not in file:
            os.remove('_output/'+file)
    print('Removed successfully!')