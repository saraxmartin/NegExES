import copy

def BIO_tagging(y):
  y_bio = copy.deepcopy(y)
  for t in range(len(y)):
    for i in range(len(y[t])):
      if y[t][i]=='NEG':
        if y[t][i-1]!='NEG':
          y_bio[t][i] = 'B_NEG'
        elif y[t][i-1]=='NEG':
          y_bio[t][i] = 'I_NEG'

      elif y[t][i]=='UNC':
        if y[t][i-1]!='UNC':
          y_bio[t][i] = 'B_UNC'
        elif y[t][i-1]=='UNC':
          y_bio[t][i] = 'I_UNC'

      elif y[t][i]=='NSCO':
        if y[t][i-1]!='NSCO':
          y_bio[t][i] = 'B_NSCO'
        elif y[t][i-1]=='NSCO':
          y_bio[t][i] = 'I_NSCO'

      elif y[t][i]=='USCO':
        if y[t][i-1]!='USCO':
          y_bio[t][i] = 'B_USCO'
        elif y[t][i-1]=='USCO':
          y_bio[t][i] = 'I_USCO'

  return y_bio

def BIESO_tagging(y):
  y_bio = copy.deepcopy(y)
  for t in range(len(y)):
    for i in range(len(y[t])):
      if y[t][i]=='NEG':
        if y[t][i-1]!='NEG' and y[t][i+1]!='NEG':
          y_bio[t][i] = 'S_NEG'
        elif y[t][i-1]!='NEG' and y[t][i+1]=='NEG':
          y_bio[t][i] = 'B_NEG'
        elif y[t][i+1] != 'NEG':
          y_bio[t][i] = 'E_NEG'
        elif y[t][i-1]=='NEG' and y[t][i+1]=='NEG':
          y_bio[t][i] = 'I_NEG'

      elif y[t][i]=='UNC':
        if y[t][i-1]!='UNC' and y[t][i+1]!='UNC':
          y_bio[t][i] = 'S_UNC'
        elif y[t][i-1]!='UNC' and y[t][i+1]=='UNC':
          y_bio[t][i] = 'B_UNC'
        elif y[t][i+1] != 'UNC':
          y_bio[t][i] = 'E_UNC'
        elif y[t][i-1]=='UNC' and y[t][i+1]=='UNC':
          y_bio[t][i] = 'I_UNC'

      elif y[t][i]=='NSCO':
        if y[t][i-1]!='NSCO' and y[t][i+1]!='NSCO':
          y_bio[t][i] = 'S_NSCO'
        elif y[t][i-1]!='NSCO' and y[t][i+1]=='NSCO':
          y_bio[t][i] = 'B_NSCO'
        elif y[t][i+1] != 'NSCO':
          y_bio[t][i] = 'E_NSCO'
        elif y[t][i-1]=='NSCO' and y[t][i+1]=='NSCO':
          y_bio[t][i] = 'I_NSCO'

      elif y[t][i]=='USCO':
        if y[t][i-1]!='USCO' and y[t][i+1]!='USCO':
          y_bio[t][i] = 'S_USCO'
        if y[t][i-1]!='USCO' and y[t][i+1]=='USCO':
          y_bio[t][i] = 'B_USCO'
        elif y[t][i+1] != 'USCO':
          y_bio[t][i] = 'E_USCO'
        elif y[t][i-1]=='USCO' and y[t][i+1]=='USCO':
          y_bio[t][i] = 'I_USCO'

  return y_bio
