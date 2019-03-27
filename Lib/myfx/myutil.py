import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.fftpack as spfft

def len_na(np_x):
    return len(np_x[np.isnan(np_x)])
