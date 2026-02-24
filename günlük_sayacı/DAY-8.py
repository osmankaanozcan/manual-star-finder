import numpy as np
from scipy import sparse
import matplotlib.pyplot as plt
import time
from scipy.sparse import linalg
import astropy.units as u
import astropy.constants as const

# eye_np = np.eye(5)(birim matris)
# matrix = sparse.csr_matrix(eye_np)
# print(matrix)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# a = ([[1,0,0] , [0,0,2] , [0,5,0]])
#
# sparse = sparse.csr_matrix(a)
# print(sparse)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# rows = np.random.randint(0,1000,1000)
# cols = np.random.randint(0,1000,1000)
# data = np.random.rand(1000)
# coo_mat = sparse.coo_matrix((data, (rows, cols)) , shape=(1000,1000))
# normal = coo_mat.toarray()
# şilk_5_satır = data[0:5]
# print(şilk_5_satır)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# a = sparse.eye(1000).tocsr()
# b = sparse.rand(1000,1000 , density=0.01).tocsr()
# c = a @ b
# yanyana = sparse.hstack([a,b])
# altalta = sparse.vstack([a,b])
# plt.subplot(1,2,1)
# plt.spy(altalta,markersize=1)
# plt.title('alta')
# plt.subplot(1,2,2)
# plt.spy(yanyana,markersize=1)
# plt.title('yanyana')
# plt.show()

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# a = sparse.eye(1000).tocsr() + sparse.rand(1000 , 1000 , density=0.01).tocsr()
# b = np.random.rand(1000)
# start = time.time()
# x = linalg.spsolve(a,b)
# end = time.time()
# hata = np.allclose(a @ x , b)
# print(hata)
# print(f"geçen süre: {end - start}")

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
a = np.sqrt(0.0017) *u.AU
b = a.to(u.km)
print(b)