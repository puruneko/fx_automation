
    point = padding*counter
    raised_point = point-margin_point
    a = float(raised_point) * 0.5
    b = float(raised_point) * 0.25
    for j in range(raised_point):
      result.append((sgnl[itr_start]-sgnl[i]) * (0.5 + 0.5*np.cos(np.pi*(float(j)-2.0*b+a)/(2.0*a))) + sgnl[i])
    for j in range(margin_point):
      result.append(