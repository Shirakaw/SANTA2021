## **Santa** 2021年度竞赛——**Kaggle**备赛（一）

#### 前述 

最近Kaggle给我推了一个比赛推送，我打开之后大概浏览一遍比赛内容。是有关超置换的问题，我首先想到的是转化为**TSP**商旅问题，我对此产生了很大的兴趣。因为最近想锻炼一下自己的算法和**Coding** 能力。写一篇关于超置换转化为**TSP**问题的分析笔记。

#### 比赛背景

比赛的名称为[**Santa 2021 - The Merry Movie Montage**](https://www.kaggle.com/c/santa-2021/overview/description) 出题的大概意思：在圣诞节北极精灵为了推出他们的产品七部电影。如何安排它们的播放顺序很重要，我们的任务是帮助精灵提供最短的观看时间向他们展现各种电影组合，以便他们尽快获得安排顺序。

#### 赛题目标

我们需要找到三组字符串，字符串中包含七部电影的每个排列顺序。条件约束如下所示

- 每个排列必须至少在一个字符串里
- 没个以🎅🤶开头的排列必须在每组字符串中
- 每个字符串中最多可以有两个 **wildcards** 🌟，它们将匹配排列中的任何符号。包括多个 **wildcards** 的长度为**7**的字符串不会算作排列

在上述约束下，我们的分数为三个字符串中最长字符串的长度。这是最小化问题，因此分数越低越好。

#### 比赛思路

它这道题的特点在于[凉宫春日问题](https://zh.moegirl.org.cn/%E5%87%89%E5%AE%AB%E6%98%A5%E6%97%A5%E9%97%AE%E9%A2%98)，这道题的特点在于一些特殊排列。比如1，2，3的六种排列方式：123，132，213，231，312，321.他们的排列可以组成更长的字符串，并且允许重叠。123和231的排列组合都为1231的子串。在123121321长度为9的字符串中可以找到1，2，3的所有排列组合。在两个字符串中排列，我们可以分为1231213和1321，它的最长长度为7即分数为7在n<5我们可以已知最优的排列方式，在n>=6时，我们需要通过搜索和优化方法进行分析。该问题也加了一个wildcards概念，可以替代任意一个符号。我们假设该问题为**TSP**商旅类型，1231中包含123和231两组子串，123与231的距离为1（一个字符串）。我们可以将这个概念转化为一个点到另一个点的距离问题... 对于求解多项式时间复杂度的算法求得先后次序。主流的方法是采用随机的启发式的搜索算法。对于启发式算法我们还需要筛选最优解。综上分析，我们设计一个**baseline**大方向，选定方法。

- 计算每个电影之间的“距离”：利用**Dijkstra**，**Flord**等算法求出最短路线
- 计算最短的字符串路径：利用启发式算法求每个电影排列的次序

#### **Baseline**设计

关于启发式算法在该问题的优缺点，搜索一些文献如下所示：
![image-20211119223351499](C:\Users\12499\AppData\Roaming\Typora\typora-user-images\image-20211119223351499.png)

很显然在运行计算时间，模拟退火的计算结果更快。所以该设计首先以模拟退火进行模型构建。

1. 根据将最小超置换问题转化为TSP商旅问题，每个字符串之间的距离n(间隔n个字符串)视作每个城市之间的距离即需要一个包含q的字符串，需要在p加入n个字符，我们首先设计一个距离函数：

   ```python
   def distance(p,q):
       N = len(p)
       for n in range(N+1):
           if p[n:] == q[:N-n]:
               return N
   ```

   通过设计该函数可以计算两个字串之间的距离。此时需要注意，逆向的距离不一定相同。

2. 在distance_matrix中已经提供了各字符串之间的距离。我们需要设计一个路径变换函数

   ```python
   def change_path(path,i,j):
       path_new=[]
       for t in path:
           path_new.append(t)
       c = path_new[i]
       path_new[i] = path_new[j]
       path_new[j] = c
       return path_new
   ```

3. 贪心法选择路径

   ```python
   def tanxin(path):
       n = len(path)
       get_new_path = path
       old_len = path_len(path)
       count = 0
       while count < n*n:
           i = random.randint(0, n - 1)
           j = random.randint(0, n - 1)
           path_new = change_path(path, i, j)
           count += 1
           if path_len(path_new) < old_len:
               get_new_path = path_new
               break
   
       if get_new_path == path:
           print('没有找到附近更优解，返回原解')
           return path
       else:
           print('找到该path更优附近解，返回更优附近解：',get_new_path)
           return get_new_path
   ```

4. 爬山法选择路径

   ```python
   def tanxin(path):
       n = len(path)
       get_new_path = path
       old_len = path_len(path)
       count = 0
       while count < n*n:
           i = random.randint(0, n - 1)
           j = random.randint(0, n - 1)
           path_new = change_path(path, i, j)
           count += 1
           if path_len(path_new) < old_len:
               get_new_path = path_new
               break
   
       if get_new_path == path:
           print('没有找到附近更优解，返回原解')
           return path
       else:
           print('找到该path更优附近解，返回更优附近解：',get_new_path)
           return get_new_path
   ```

5. 寻找最优解，当找不到下山方向（路径没有变化时）得到该种方法最优解

   ```python
   def best_path(path):
       nums=0
       while 1:
           path_better=tanxin(path)  
           #这里是用贪心法，改为pashan(path)则为爬山法
           nums+=1
           print(nums)
           if path_better == path:
               dis=path_len(path_better)
               print('----'*50)
               print( '共迭代',nums,'次，搜索到这种方法的最优解')
               print('最优路径：',path_better)
               print('最优距离：',dis)
               break
           else:
               path=path_better
   ```

   

6. 模拟退火法

   ```python
   import math
   #温度变化函数
   def T_update(t,T0):  # t 为推移时间，即每需要更新一次，t+1，表示冷却一次
       T=T0/math.log(1+t)
       return T
   #代入路径长度矩阵
   #得到新路径函数
   def change_path(path, i, j):
       path_new=[]
       for t in path:
           path_new.append(t)
   
       c = path_new[i]
       path_new[i] = path_new[j]
       path_new[j] = c
       return path_new
   # metropolis 准则
   def metropolis(path_old,path_new,T):
       len_new=path_len(path_new)
       len_old=path_len(path_old)
       detE=len_new-len_old
       if detE<=0:
           p=1
       else:
           p=math.pow(math.e,-detE/T)
       return p
   # 退火法函数
   def metropolis(path_old,path_new,T):
       len_new=path_len(path_new)
       len_old=path_len(path_old)
       detE=len_new-len_old
       if detE<=0:
           p=1
       else:
           p=math.pow(math.e,-detE/T)
       return p
   #输入路径矩阵
   
   
   ```

#### 总结

