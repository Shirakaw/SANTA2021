import numpy as np 
import time
import pandas as pd
import xlrd
# step1 由permutation中可知一共5040组排序方式
data_file = pd.read_csv(r'C:\Users\12499\OneDrive\santa-2021\distance_matrix.csv') # Excel文件存储位置
data_file.drop(columns=["Permutation"])
data_file.drop([1])


def distance(p, q):
  n = len(p)
  for i in range(n + 1):
    if p[i:] == q[:n - i]:
      return n