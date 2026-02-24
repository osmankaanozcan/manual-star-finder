import pandas as pd
import io
# - hatalı verileri düzeltme

raw_data = """Campaign_ID,Category,Ad_Spend,Revenue
1001,Social,500.0,1200.0
1002,Search,-150.0,800.0
1003,Social,600.0,
1004,Display,200.0,300.0
1005,Search,400.0,
1006,Social,550.0,1300.0
1007,Display,-50.0,400.0
1008,Search,450.0,900.0"""

df = pd.read_csv(io.StringIO(raw_data))
df_temiz = df[df["Ad_Spend"] >= 0].copy()
df_temiz["Revenue"] = df_temiz.groupby("Category")["Revenue"].transform(lambda x: x.fillna(x.mean()))
df_temiz["kar"] = (df_temiz["Revenue"] - df_temiz ["Ad_Spend"])
ozet_tablo = df_temiz.groupby("Category")["kar"].sum()

if __name__ == "__main__":
    print("--- orjinali ---")
    print(df)
    print("--- temizlenmiş ---")
    print(df_temiz)
    print("--- istenen son veri ---")
    print(ozet_tablo)