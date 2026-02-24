import numpy as  np
import matplotlib.pyplot as plt
from scipy import signal

t = np.linspace(0,1,100)
clean_signal = np.sin(2 * np.pi * t * 5)

noise_signal = clean_signal.copy()
noise_signal[::10] += 2
noise_signal[::10] -= 2
clear = signal.savgol_filter(noise_signal, 11, 3)
# bu daha kaba ve üstünkörü  ---   clear = signal.medfilt(noise_signal,5)
plt.plot(t , noise_signal , label = "noise" , alpha = 0.5)
plt.plot(t , clear , label= "temiz ver," , linewidth = 2)
plt.legend()
plt.show()