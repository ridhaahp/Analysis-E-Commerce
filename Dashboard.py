import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

#upload local
#all_df = pd.read_csv("submission/Dashboard/all_data.csv")
st.title('Dashboard E-Commerce Data Analysis')
#untuk upload dari github
all_df = pd.read_csv("all_data.csv")
#=======================================================================================
# Create the 'order_purchase_month' column
all_df["order_purchase_date"] = pd.to_datetime(all_df["order_purchase_date"])
all_df["order_purchase_month"] = all_df["order_purchase_date"].dt.strftime("%B")


def create_rfm_df(all_df):
    rfm_df = all_df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "customer_unique_id": "nunique",
        "payment_value": "sum"
    })
    
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df["max_order_timestamp"])  # Convert to datetime
    recent_date = pd.to_datetime(all_df["order_purchase_timestamp"]).max()
    
    rfm_df["recency"] = (recent_date - rfm_df["max_order_timestamp"]).dt.days
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df


# Create the 'rfm_df' DataFrame using the create_rfm_df function
rfm_df = create_rfm_df(all_df)
#=======================================================================================

datetime_columns = ["order_purchase_timestamp"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

#=======================================================================================
# Function to create payment method chart
def create_payment_method_chart():
    plt.figure(figsize=(8, 8))
    pm = sns.countplot(data=all_df, x="payment_type")
    plt.xlabel("Payment Method")
    plt.ylabel("")
    plt.title("Chart of Payment Method")

    for p in pm.patches:
        pm.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 10), textcoords='offset points')

    # Display plot using st.pyplot
    st.pyplot(plt.gcf())

create_payment_method_chart()

def create_monthly_purchase_chart():
    month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(15, 8))

    # Check if the 'order_purchase_month' column is present in the DataFrame
    if 'order_purchase_month' in all_df.columns:
        # Use seaborn to create a countplot
        pm = sns.countplot(data=all_df, x="order_purchase_month", order=month_order, palette="viridis", ax=ax)

        # Set labels and title
        ax.set_xlabel("Month")
        ax.set_ylabel("")
        ax.set_title("Chart of Monthly Purchase")

        # Annotate the count values
        for p in pm.patches:
            pm.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', xytext=(0, 10), textcoords='offset points')

        # Display the plot using st.pyplot
        st.pyplot(plt.gcf())
    else:
        st.write("The 'order_purchase_month' column is not present in the DataFrame.")

# Call the function to create the monthly purchase chart
create_monthly_purchase_chart()

#RFM
st.subheader("RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)
 
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)
 
st.pyplot(fig)
 
st.caption('Copyright (c) Ridha Hasti Putri Des 2023')