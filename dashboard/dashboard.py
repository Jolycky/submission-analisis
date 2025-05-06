import streamlit as st
import pandas as pd
import plotly.express as px

# --- Config halaman ---
st.set_page_config(page_title="📊 E-Commerce Dashboard", layout="wide")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv", parse_dates=["order_purchase_timestamp"])
    df['month'] = df['order_purchase_timestamp'].dt.to_period('M').dt.to_timestamp()
    df['year'] = df['order_purchase_timestamp'].dt.year
    df['month_name'] = df['order_purchase_timestamp'].dt.strftime('%B')
    return df

df = load_data()

# --- Sidebar Filter ---
st.sidebar.title("📊 Filter Dashboard")
st.sidebar.markdown("Gunakan filter di bawah untuk mengeksplorasi data.")

# Filter Tahun
all_years = df['year'].sort_values().unique()
selected_years = st.sidebar.multiselect("Pilih Tahun", options=all_years, default=all_years[-1:])

# Filter Bulan
all_months = df['month_name'].unique().tolist()
selected_months = st.sidebar.multiselect("Pilih Bulan", options=all_months, default=all_months)

# Filter Total Penjualan
min_sales, max_sales = int(df['total_sales'].min()), int(df['total_sales'].max())
sales_range = st.sidebar.slider("Range Total Penjualan", min_value=min_sales, max_value=max_sales, value=(min_sales, max_sales))

# --- Apply Filters ---
df_filtered = df[
    (df['year'].isin(selected_years)) &
    (df['month_name'].isin(selected_months)) &
    (df['total_sales'].between(sales_range[0], sales_range[1]))
]

# --- Title ---
st.markdown("<h1 style='text-align: center;'>📈 E-Commerce Public Dataset</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- Ringkasan Data ---
total_sales = int(df_filtered['total_sales'].sum())
total_orders = df_filtered['order_id'].nunique()
unique_categories = df_filtered['product_category_name_english'].nunique()

st.markdown("### 🔍 Ringkasan Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div style="background-color: #e8f4fd; 
                    padding: 18px; 
                    border-radius: 12px; 
                    box-shadow: 2px 2px 10px rgba(0,0,0,0.05); 
                    text-align: center;">
            <div style="font-size: 28px;">💰</div>
            <div style="font-size: 16px; color: #1b74e4; font-weight: 600;">Total Penjualan</div>
            <div style="font-size: 22px; color: #333333; font-weight: bold;">R$ {:,}</div>
        </div>
        """.format(total_sales), unsafe_allow_html=True)

with col2:
    st.markdown(
        """
        <div style="background-color: #e6fff7; 
                    padding: 18px; 
                    border-radius: 12px; 
                    box-shadow: 2px 2px 10px rgba(0,0,0,0.05); 
                    text-align: center;">
            <div style="font-size: 28px;">🧾</div>
            <div style="font-size: 16px; color: #00a884; font-weight: 600;">Jumlah Transaksi</div>
            <div style="font-size: 22px; color: #333333; font-weight: bold;">{:,}</div>
        </div>
        """.format(total_orders), unsafe_allow_html=True)

with col3:
    st.markdown(
        """
        <div style="background-color: #fff3e6; 
                    padding: 18px; 
                    border-radius: 12px; 
                    box-shadow: 2px 2px 10px rgba(0,0,0,0.05); 
                    text-align: center;">
            <div style="font-size: 28px;">📦</div>
            <div style="font-size: 16px; color: #ff8c00; font-weight: 600;">Kategori Produk</div>
            <div style="font-size: 22px; color: #333333; font-weight: bold;">{:,}</div>
        </div>
        """.format(unique_categories), unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- Visualisasi 1: Tren Penjualan Bulanan ---
st.subheader("📆 Tren Penjualan Bulanan")
monthly_sales = df_filtered.groupby('month')['total_sales'].sum().reset_index()

fig1 = px.line(monthly_sales, x='month', y='total_sales', markers=True,
               title=f"Tren Penjualan Bulanan")
fig1.update_layout(xaxis_title='Bulan', yaxis_title='Total Penjualan', template='plotly_white')
st.plotly_chart(fig1, use_container_width=True)

# --- Visualisasi 2: Top 10 Kategori Produk ---
st.subheader("🏆 Top 10 Kategori Produk Berdasarkan Total Penjualan")

top_10 = (df_filtered.groupby('product_category_name_english')['total_sales']
          .sum().sort_values(ascending=False).head(10).reset_index())

fig2 = px.bar(top_10, x='total_sales', y='product_category_name_english',
              orientation='h', color='total_sales', color_continuous_scale='viridis',
              title="Top 10 Kategori Produk")
fig2.update_layout(xaxis_title='Total Penjualan', yaxis_title='Kategori Produk',
                   yaxis=dict(autorange='reversed'), template='plotly_white')
st.plotly_chart(fig2, use_container_width=True)