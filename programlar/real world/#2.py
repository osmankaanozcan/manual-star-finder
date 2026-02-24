import day1 as al
import matplotlib.pyplot as plt
#day1 önceki veriler /  verileri sütun haline getirdik
plt.text(-0.6, 2100, '2100', color='black', va='bottom', ha='right', fontweight='bold')
plt.text(-0.6, 950, '950', color='black', va='bottom', ha='left', fontweight='bold')
plt.text(-0.6, 100, '100', color='black', va='bottom', ha='right', fontweight='bold')
plt.axhline(y=2100 , color="black" , alpha=0.5, linestyle="--" )
plt.axhline(y=950 , color="black" , alpha=0.5, linestyle="--"  )
plt.axhline(y=100 , color="black" , alpha=0.5, linestyle="--"  )
plt.bar(al.ozet_tablo.index,al.ozet_tablo.values)
plt.yticks([500 , 1000 , 1500  , 2000 , 2500 ])
plt.title("Kategori bazlı net kar analizi")
plt.xlabel("kategoriler")
plt.ylabel("net kar")

plt.show()