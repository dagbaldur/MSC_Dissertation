from os import listdir
from os.path import isfile, join
import pandas as pd

crackpath = "C:/Users/memoc/pool_cracks"
noncrackpath = "C:/Users/memoc/pool_noncracks"

getCracks = ['gs://gcu-dissertation/Model DS/Lake/'+f for f in listdir(crackpath) if isfile(join(crackpath, f))]
getNonCracks = ['gs://gcu-dissertation/Model DS/Lake/'+f for f in listdir(noncrackpath) if isfile(join(noncrackpath, f))]

cr = pd.DataFrame(data=getCracks,columns=['file'])
nc = pd.DataFrame(data=getNonCracks,columns=['file'])


cr['label'] = 'crack'
nc['label'] = 'no_crack'

final = pd.DataFrame.append(cr,nc)

final.to_csv(index=False)
