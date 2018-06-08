import pandas as pd

df = pd.DataFrame(data=[[1,2,3],[4,5,6],[7,8,9]], index=['a', 'b', 'c'], columns=['d', 'e', 'f'])

print(df.loc['a'])
print(df['d'])