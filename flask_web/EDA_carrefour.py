#!/usr/bin/env python
# coding: utf-8

import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
import json

# # 載入資料


train_df=pd.read_csv("../dataset/商品對照表_-_商品對照表.csv")
#train_df=pd.read_csv("dataset/家樂福數據集.csv")
# Create a dictionary from 'Name' and 'Age' columns
pid_to_name_dict = train_df.set_index('product')['product_name'].to_dict()
name_to_pid_dict = {v:k for k,v in pid_to_name_dict.items()}


def create_product_dict(df):
    pid_to_price_dict = df.set_index('product')[['product_name','sales_price']].to_dict()
    pid_to_product_info={}
    for pid1, name in pid_to_price_dict['product_name'].items():
        for pid2, price in pid_to_price_dict['sales_price'].items():
            if pid1==pid2 :
                pid_to_product_info[pid1]=(name,price)
                #003dc937-e898-4259-870a-4a9afe2eacd6 003dc937-e898-4259-870a-4a9afe2eacd6 絲花極柔化妝棉66片 96
                #print(pid1,pid2, name,price)   
    
    return pid_to_product_info

pid_to_product_info=create_product_dict(train_df)
all_product_names=[v[0] for k,v in  pid_to_product_info.items()]

#train_df.describe()
#train_df.isna().sum()
#Note: 原始 age_group 沒有缺資料, 但這裡存在1筆資料沒有age_group

# train
date = pd.to_datetime(train_df['order_date'])
train_df['month']=date.dt.month
train_df['year']=date.dt.year
train_df['YearMonth'] = date.dt.strftime('%Y-%m')
train_df['day_name']=date.dt.day_name()
train_df['day']=date.dt.day
# add total sales
train_df['total_sales']=train_df['sales_price']*train_df['quantity']
print(len(train_df))

def query_name_by_pid(pid):
    name,price_unit=pid_to_product_info[pid]
    return name,price_unit

# ## 銷售額前K名商品
def get_top_k_product(df,k,by_column='total_sales',plot=False):
    df_group_by_prod=df.groupby('product').sum().reset_index()
    df_group_by_prod=df_group_by_prod[['product','total_sales','quantity']]
    #total sales=PxQ  #joseph ,20231116
    
    df_prod_sales=df_group_by_prod.sort_values(by=by_column,ascending=False)[:k]
    if plot:
        plt.figure(figsize=(6, 4))
        plt.xticks(rotation=45)
        plt.bar(df_prod_sales['product'], df_prod_sales[by_column])
        plt.show()
    result=[]
    for i in range(len(df_prod_sales)):
        pid = df_prod_sales.iloc[i]['product']
        price = df_prod_sales.iloc[i]['total_sales']
        quantity = df_prod_sales.iloc[i]['quantity']
        name,unit_price=query_name_by_pid(pid)
        #print(pid,name,unit_price,price,quantity)
        result.append((pid,name,int(unit_price),int(price),int(quantity)))
           
    return result


# # 整體銷售狀況
def analyze_basic(df):
    total_records=len(df)
    total_transactions=len(df.groupby('id'))
    total_customer=len(df.groupby('customer'))
    #所有發票上的金額 ## same as train_df['sales_price'].sum()
    total_sales=df.groupby('id')['total_sales'].sum().sum()   
    total_products=len(df.groupby('product'))
    
    print('發票數量:',total_transactions)
    print('客戶數量:',total_customer)
    print('平均客戶消費次數:',total_transactions/total_customer)
    print('平均發票金額:',total_sales/total_transactions)
    print('平均每筆發票的商品種類:',total_records/total_transactions)
    print('商品種類:',total_products)


# ## 每個顧客的購買總金額
def ananyze_customer_amount(df,plot=False):
    df_group_by_customer=df.groupby('customer')['total_sales'].agg(['sum']).reset_index()  
    #長條圖: 每個顧客的購買總金額
    if plot:
        df_group_by_customer=df.groupby('customer')['total_sales'].agg(['sum'])
        df_group_by_customer['sum'].plot(kind='bar');
        plt.title("Sales VS. customer")
        plt.xlabel("customer")
        plt.ylabel("Sale")
        plt.show()
        
    return df_group_by_customer


# ## 每筆發票的金額
def ananyze_invoice_amount(df,plot=False):
    df_group_by_id=df.groupby('id')['total_sales'].sum().reset_index()    
    df_group_by_id=df_group_by_id.sort_values(by='total_sales') #ascending=False
    #print(df_group_by_id)
    
    if plot:
        plt.bar(df_group_by_id['id'], df_group_by_id['total_sales'])
        plt.ylabel('Age')
        plt.title('Amount Distribution (Reversed Order)')
        #plt.xticks(rotation=45)
        #plt.tight_layout()
        plt.show()
        
    return df_group_by_id


# ## 查詢某客戶的購買歷史記錄(消費及其金額)
def show_purchase_by_customer(df,cid):
    dataset=df[df['customer']==cid].groupby('id')['total_sales'].agg(['sum']).reset_index()
    total_amounts=dataset['sum'].sum()
    print(f'客戶({cid})消費筆數:{len(dataset)}, 累積消費金額為 {total_amounts}元,平均每次消費{total_amounts/len(dataset)}' )
    return dataset,total_amounts




# ## 查詢發票的交易明細
def show_invoice(df,tid,show_detail=True):
    data=df[df['id']==tid][['product_name','sales_price','quantity','total_sales']].reset_index()
    amount=data['total_sales'].sum()
    counts=len(data)
    if show_detail:
        print(f'發票號碼:{tid} 消費總金額: {amount} 元, 共 {counts} 樣商品，明細如下:')
        print(f'    {"品項":30},{"數量":3},{"金額":5}')
        for i in range(len(data)):
            item = data.iloc[i]['product_name']
            q = data.iloc[i]['quantity']
            price=data.iloc[i]['sales_price']
            print(f'{i+1}:{item:<30}{q:3}{price:>5}')
    
    return amount,counts,data



# # 每月總銷售額
def analyze_revenue(df):
    sales_per_month=train_df.groupby('YearMonth')['total_sales'].agg(['sum']).reset_index()
    plt.figure(figsize=(8, 6))
    sns.barplot(data=sales_per_month,x='YearMonth',y='sum')
    plt.title('Sales VS YearMonth')
    plt.ylabel('Sales')
    plt.xlabel("Year")
    plt.xticks(rotation=45)
    plt.show()


# ## 每月各分店的銷售額

def analyze_store_amount(df):
    print('共有店家:',len (df.groupby('store')))
    sales_per_month_store=df.groupby(['YearMonth','store'])['total_sales'].agg(['sum']).reset_index()
    sales_per_month_store
    plt.figure(figsize=(10, 6))
    plt.xticks(rotation=45)
    sns.barplot(x='YearMonth', y='sum', data=sales_per_month_store, hue='store')
    

# ## 分店每月銷售狀況

def analyze_store_sales(df,store_id,plot=False):
    sales_per_month_store=df.groupby(['YearMonth','store'])['total_sales'].agg(['sum']).reset_index()
    data=sales_per_month_store[sales_per_month_store['store']==store_id]
    data=data[['YearMonth','sum']]
    # Create a DataFrame with all months (including missing ones) and fill missing values with 0
    all_months = pd.date_range(start='2020-05', end='2022-01', freq='M')
    df_m = pd.DataFrame({'YearMonth': all_months})
    df_m['YearMonth']= df_m['YearMonth'].dt.to_period('M').apply(str)    
    df_data = pd.merge(df_m,data, on=['YearMonth'], how='left').fillna(0)
    if plot:
        plt.figure(figsize=(10, 6))
        plt.xticks(rotation=45)
        sns.barplot(x='YearMonth', y='sum', data=df_data)
        
    return df_data


## Recommanded system 
from difflib import SequenceMatcher
#content-based : only use product name as a factor

def top_k_recommnd_item(p_name,k=5):
    recommand_list={}
    for name in all_product_names:
        similarity = SequenceMatcher(None,name,p_name).ratio()
        recommand_list[name]=similarity
        #print(f"{name}({name_to_pid_dict[name]})和{com_prod}相似度為{similarity}")
    
    recommand_sorted=sorted(recommand_list.items(), key=lambda item: item[1], reverse=True)[:k]
    
    return [(item[0],item[1])  for item in recommand_sorted]


   
if __name__=="__main__":


    analyze_basic(train_df)
    
    #print(pid_to_name_dict['003dc937-e898-4259-870a-4a9afe2eacd6'])
    #print(name_to_pid_dict['絲花極柔化妝棉66片'])

    print(pid_to_product_info['003dc937-e898-4259-870a-4a9afe2eacd6'])
    
    # # ## 銷售額前K名的商品
    k=3
    print(f'----------銷售額前 {k}名的商品-----------------')
    top_K_prod=get_top_k_product(train_df,k,'total_sales')
    
   
    for i in top_K_prod: print(i)
    
    # # ## 銷售量前K名的商品
    print(f'----------銷售量前 {k}名的商品----------------')
    top_K_prod=get_top_k_product(train_df,k,'quantity')
    for i in top_K_prod: print(i)
    
    
    #dataset=analyze_store_sales(train_df,'51cbbfb9-85a5-4032-8f03-7b1c43d08e49')
    #print(dataset)
    #dataset=analyze_store_sales(train_df,'39653f7d-f888-4f53-9cfe-d9143f7e03e0')
    print('-----------查詢發票明細-------------')
    #amount,n_records,data=show_invoice(train_df,'65f9657e-a473-46be-bf6c-ebbc508297a9',show_detail=False)
    amount,n_records,data=show_invoice(train_df,'a70c6a3c-d8b8-4280-b85f-56eeb9621006',show_detail=True)
    print(data)
    
    
    print('-----------查詢客戶交易記錄-------------')
    
    customer_id='00113cb1-293b-4c73-8844-4ca901c819ab'
    dataset,total_amounts=show_purchase_by_customer(train_df,customer_id)
    print(dataset)
    # dataset,total_amounts=show_purchase_by_customer(train_df,'003c1701-7951-41f7-8e3e-7c102daa28a0')
    # print(dataset)
    
    print('-----------推廌商品-------------')
    com_prod = "光泉茉莉茶園紅茶蘋果-250ml" #"特上檸檬紅茶"
    print(top_k_recommnd_item(com_prod,10))
    
    