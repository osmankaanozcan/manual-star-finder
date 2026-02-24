from scipy import integrate
import numpy as np
# f = lambda y , x: x + y
# alan , hata = integrate.dblquad(f , 0 , 5,0,2)
# print(alan)




f = lambda z , y ,x: x * y * z
alan , hata = integrate.tplquad(f,0 , 2,lambda x: 0, lambda x: 3,lambda y,x: 0,lambda y,x: 4)
print(alan)