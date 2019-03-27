import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def estimated_rate(pastRate, nowRate, coef=1):
    y = nowRate-pastRate
    return nowRate + y*coef

def isCross(sig_past, sig_now, ref_past, ref_now):
    if sig_past <= ref_past and sig_now > ref_now:
        return 1
    elif sig_past >= ref_past and sig_now < ref_now:
        return -1
    return 0

def cross_loc(sig, i, loc):
    return isCross(sig[i-1],sig[i], loc, loc)

def cross_zero(sig, i):
    return cross_loc(sig, i, 0)

def cross_line(sig, i, ref):
    return isCross(sig[i-1], sig[i], ref[i-1], ref[i])

def cross_line_estimated(sig, i, coef, ref):
    est = estimated_rate(sig[i-1], sig[i], coef)
    return isCross(sig[i-1], est, ref[i-1], ref[i])

def cross_line_estimated2(sig, i, coef_s, ref, j, coef_r):
    est_sig = estimated_rate(sig[i-1], sig[i], coef_s)
    est_ref = estimated_rate(ref[j-1], ref[j], coef_r)
    return isCross(sig[i-1], est_sig, ref[i-1], est_ref)

def cross_loc_estimated(sig, i, coef, loc):
    est = estimated_rate(sig[i-1], sig[i], coef)
    return isCross(sig[i-1], est, loc, loc)

def direction_line(sig, i):
    if sig[i-1] < sig[i]:
        return 1
    elif sig[i-1] > sig[i]:
        return -1
    return 0

def or_(list_):
    for l_ in list_:
        if l_ == True:
            return True
    return False

def and_(list_):
    for l_ in list_:
        if l_ == False:
            return False
    return True
