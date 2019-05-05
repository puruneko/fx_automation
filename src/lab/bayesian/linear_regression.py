# https://www.iwanttobeacat.com/entry/2018/02/17/170542
# https://qiita.com/ysdyt/items/05a884354741bd9ca82b
# ベイズ線形回帰の解は、重み係数wnをn=0から順番にベイズ更新した時の事後分布の、各wnに対する最大確率と一致する！

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.special import gamma

def main():
  X = np.array([0.02, 0.12, 0.19, 0.27, 0.42, 0.51, 0.64, 0.84, 0.88, 0.99])
  t = np.array([0.05, 0.87, 0.94, 0.92, 0.54, -0.11, -0.78, -0.79, -0.89, -0.04])
  est_xLen = 0.1

  # 定数項＋ガウス基底(12次元) 
  def phi(x):
      s = 0.1 # ガウス基底の「幅」
      #return np.array([x**i for i in range(10)])
      return np.append(1, np.exp(-(x - np.arange(0, 1 + s, s)) ** 2 / (2 * s * s)))
  # 正規分布の確率密度関数
  def normal_dist_pdf(x, mean, var): 
      return np.exp(-(x-mean) ** 2 / (2 * var)) / np.sqrt(2 * np.pi * var)
  # 2次形式( x^T A x を計算)
  def quad_form(A, x):
      return np.dot(x, np.dot(A, x))

  PHI = np.array([phi(x) for x in X])
  xlist = np.arange(0, 1 + est_xLen, 0.01)
  # 線形回帰
  w = np.linalg.solve(np.dot(PHI.T, PHI), np.dot(PHI.T, t))
  ylist1 = [np.dot(w, phi(x)) for x in xlist]
  # ベイズ線形回帰
  alpha = 0.1 # 事前分布の分散の逆数（w=0という前提をどれだけ強く信じるか）
  beta = 9.0  # 尤度の分散の逆数（どれだけ観測値からの広がりを制限するか）
  Sigma_N = np.linalg.inv(alpha * np.identity(PHI.shape[1]) + beta * np.dot(PHI.T, PHI))
  mu_N = beta * np.dot(Sigma_N, np.dot(PHI.T, t))
  ylist2 = [np.dot(mu_N, phi(x)) for x in xlist]
  # ベイズ線形回帰の事後分布
  tlist = np.arange(-1.5, 1.5, 0.01)
  z = np.array([normal_dist_pdf(tlist, np.dot(mu_N, phi(x)),
          1 / beta + quad_form(Sigma_N, phi(x))) for x in xlist]).T


  plt.contourf(xlist, tlist, z, 5, cmap=plt.cm.binary)
  plt.plot(xlist, ylist1, label='linear')
  plt.plot(xlist, ylist2, label='bayes')
  plt.plot(X, t, 'o')
  plt.legend()
  plt.show()

def main2():
  est_xLen = 0.1
  comment = '''
  X = np.array([0.02, 0.12, 0.19, 0.27, 0.42, 0.51, 0.64, 0.84, 0.88, 0.99])
  xlist = np.arange(0, 1 + est_xLen, 0.01)
  t = np.array([0.05, 0.87, 0.94, 0.92, 0.54, -0.11, -0.78, -0.79, -0.89, -0.04])
  tlist = np.arange(-1.5, 1.5, 0.01)
  '''
  N = 32
  pips = 0.0001
  filename = r'C:\Users\Ryutaro\Dropbox\prog\git\github\fx_automation\resources\DAT_ASCII_EURUSD_M1_2006.csv'
  data = pd.read_csv(filename, sep=';', names=['date', 'open', 'high', 'low', 'close', 'volume'])
  close = data['close'][1000:1000+N].as_matrix()
  avg = np.average(close)
  t = close - avg
  tlist = np.arange(min(t), max(t), pips)
  X = np.arange(0, N, 1)
  width = np.average([X[i]-X[i-1] for i in range(1,len(X))])
  xlist = np.arange(min(X), max(X) + width, width)

  alpha_s = 1.0
  beta_s  = 2.0
  M_kai = 5
  nu_phi = 4
  var = np.var(t)
  nu = abs(2*var/(var-1))
  print(var, '  ', nu)

  # 定数項＋ガウス基底(12次元) 
  def phi_normal(x):
    s = width # ガウス基底の「幅」
    return np.exp(-(x - np.arange(0, N, s)) ** 2 / (2 * s * s))
  # kai分布線形和
  def phi_kai2(x):
    return np.array([x**(i*M_kai/(N)) for i in range(N)])
  # t分布線形和
  def phi_t(x):
    s = width # 幅
    shift = np.arange(0, N, s)
    return np.power(1.0+np.power((shift-x),2.0)/nu_phi, -0.5*(nu_phi+1.0))
  # 正規分布の確率密度関数
  def normal_dist_pdf(x, mean, var):
    return np.exp(-(x-mean) ** 2 / (2 * var)) / np.sqrt(2 * np.pi * var)
  # t分布の確率密度関数
  def t_dist_pdf(x, nu, mean):
    coef = gamma(0.5*(nu+1))/(np.sqrt(nu*np.pi)*gamma(nu*0.5))
    return np.power(1+np.power((x-mean),2.0)/nu, -0.5*(nu+1)) * coef

  phi_func = phi_t
  PHI = np.array([phi_func(x) for x in X])
  # 線形回帰
  w = np.linalg.solve(np.dot(PHI.T, PHI), np.dot(PHI.T, t))
  ylist1 = [np.dot(w, phi_func(x)) for x in xlist]
  # ベイズ線形回帰
  alpha = np.array([alpha_s for i in range(N)]) # 事前分布の分散の逆数（w=0という前提をどれだけ強く信じるか）
  beta  = np.array([beta_s for i in range(N)]) # 尤度の分散の逆数（どれだけ観測値からの広がりを制限するか）
  Sigma_N = np.linalg.inv(alpha * np.identity(PHI.shape[1]) + beta * np.dot(PHI.T, PHI))
  mu_N = beta * np.dot(Sigma_N, np.dot(PHI.T, t))
  ylist2 = [np.dot(mu_N, phi_func(x)) for x in xlist]
  # 閾値曲線
  var = np.var(t[[(True if t[i] > ylist2[i] else False) for i in range(len(t))]])
  nu = abs(2*var/(var-1))
  upper = ylist2 + np.sqrt(nu)*0.16
  var = np.var(t[[(True if t[i] > ylist2[i] else False) for i in range(len(t))]])
  nu = abs(2*var/(var-1))
  lower = ylist2 - np.sqrt(nu)*0.16
  # ベイズ線形回帰の事後分布
  z = np.array([t_dist_pdf(tlist, nu, np.dot(mu_N, phi_func(x))) for x in xlist]).T

  # ガウス基底の場合
  PHI_n = np.array([phi_normal(x) for x in X])
  Sigma_N = np.linalg.inv(alpha * np.identity(PHI_n.shape[1]) + beta * np.dot(PHI_n.T, PHI_n))
  mu_N = beta * np.dot(Sigma_N, np.dot(PHI_n.T, t))
  ylist3 = [np.dot(mu_N, phi_normal(x)) for x in xlist]
  # 指数基底の場合
  PHI_k = np.array([phi_kai2(x) for x in X])
  Sigma_N = np.linalg.inv(alpha * np.identity(PHI_k.shape[1]) + beta * np.dot(PHI_k.T, PHI_k))
  mu_N = beta * np.dot(Sigma_N, np.dot(PHI_k.T, t))
  ylist4 = [np.dot(mu_N, phi_kai2(x)) for x in xlist]

  fig = plt.figure(figsize=(9, 9))
  ax1 = fig.add_subplot(2, 1, 1)
  for i in range(len(PHI)):
    ax1.plot(np.arange(0, len(PHI[i]), 1), PHI[i])
  ax2 = fig.add_subplot(2, 1, 2)
  ax2.contourf(xlist, tlist, z, 5, cmap=plt.cm.binary)
  #ax2.plot(xlist, ylist1, label='linear')
  ax2.plot(xlist, ylist2, label='bayes_t')
  ax2.plot(xlist, upper, label='bayes_t_upper')
  ax2.plot(xlist, lower, label='bayes_t_lower')
  ax2.plot(xlist, ylist3, label='bayes_normal')
  ax2.plot(xlist, ylist4, label='bayes_kai2')
  ax2.plot(X, t, 'o', label='value')
  ax2.set_ylim(min(tlist), max(tlist))
  ax2.legend()
  plt.show()

if __name__ == '__main__':
  main2()