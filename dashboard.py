import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

#Daily order

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

#sum order

def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name").payment_installments.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df

#rfm

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

#Open data

all_data_df = pd.read_csv("https://raw.githubusercontent.com/IzzaMooN/proyek_akhir/main/all_dataset.csv")

#membuat kolom

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_data_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_data_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_data_df[column] = pd.to_datetime(all_data_df[column])

######################################################################

#membuat filter

min_date = all_data_df["order_purchase_timestamp"].min()
max_date = all_data_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

#Save

main_df = all_data_df[(all_data_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_data_df["order_purchase_timestamp"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
rfm_df = create_rfm_df(main_df)

#Visualisasi 1

st.header('Izz Collection Dashboard :sparkles:')

#Visualisasi 2

st.subheader("Best & Worst Performing Product")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="payment_installments", y="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="payment_installments", y="product_category_name", data=sum_order_items_df.sort_values(by="payment_installments", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)

#visualisasi 3

st.subheader("Last Transaction")
 
col1 = st.columns(1)
 
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax)
ax.set_ylabel(None)
ax.set_xlabel("customer_id", fontsize=30)
ax.set_title("By Recency (days)", loc="center", fontsize=50)
ax.tick_params(axis='y', labelsize=30)
ax.tick_params(axis='x', labelsize=35)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
 
st.pyplot(fig)
 
st.caption('Copyright (c) Izz 2023')