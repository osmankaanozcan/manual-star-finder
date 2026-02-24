# import pandas as pd
#
# data = {"yildiz_id" : [1,2,3,] , "parlaklik": [15 , 123 ,None ] , "uzaklik" : [5e6 , 1e4 , None] }
# df = pd.DataFrame(data)
# df_temiz = df.dropna(subset=["parlaklik"])
#
# print(df_temiz.describe())

#£££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££££
import pandas as pd
import numpy as np

data = {
    'yildiz_id': [101, 102, 103, 104, 105, 106],
    'parlaklik': [12.5, 13.1, None, 12.8, 999.0, 13.0],
    'sicaklik': [5500, 6000, 5800, None, 5900, -99]     }
df = pd.DataFrame(data)
df.loc[df["parlaklik"] > 100 , "parlaklik"] = np.nan
df.loc[df["sicaklik"] < 0 , "sicaklik"] = np.nan
df["durum"]= df.isnull().any(axis=1).map({True: "*" , False:  "well"})
print(df)
sıkıntılılar= df[df.isnull().any(axis=1)]
print(sıkıntılılar)

eksikler = df[df["durum"] == "*"]
print("---")
print(len(eksikler))


