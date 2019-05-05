import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from scipy.stats import binom

def doubleDist(param, count, N):
  coef = math.factorial(N)/(math.factorial(count)*math.factorial(N-count))
  return np.power(param, count)*np.power(1-param, N-count)*coef

def normal(x, sgm, mu):
  coef = 1.0/np.sqrt(2*np.pi*sgm*sgm)
  return np.exp(-np.power(x-mu, 2.0)/(2*sgm*sgm))

def main():
  N = 1000
  theta = 0.35
  data = [1 if x >= theta else 0 for x in np.random.normal(size=N)]
  theta_series = np.linspace(0.0, 1.0, 100)

  y = data.count(1)
  likelihood = binom.pmf(y, N, theta_series)#doubleDist(theta_series, y, N)
  prior = normal(theta_series, 0.1, 0.5)

  posterior = likelihood*prior
  posterior /= sum(posterior)

  plt.plot(theta_series, likelihood, color='b')
  plt.plot(theta_series, prior, color='g')
  plt.plot(theta_series, posterior, color='r')
  plt.axvline(theta, ymax=0.3, color='black')
  plt.title('N={}, y={}'.format(N, y))
  plt.show()


if __name__ == "__main__":
    main()