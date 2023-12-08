import pandas as pd
import math
import time

def main():
     # Reading in and sanitizing the data from the csv file
    pd.options.display.float_format = '{:.2f}'.format
    df_xlsx = pd.read_excel('contactinfo.xlsx', engine='openpyxl')

    # Removing NaN rows at the beginning of the file
    for i in range(len(df_xlsx['Vendor'])):
        value = df_xlsx['Vendor'][i]
        if type(value) == float:
            df_xlsx = df_xlsx.drop([i])
        else:
            continue
            
    # Gathering the necessary columns
    df_csv = df_xlsx[['Address 1','Address 2','City','State','Zip','Phone','Email','URL']]
    df_csv.to_csv("contactinfo.txt", sep='\t', index=False)




if __name__=="__main__": 
    main() 