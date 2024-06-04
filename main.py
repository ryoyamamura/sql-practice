import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
import os

# 環境変数の取得
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

engine = create_engine('postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(
                        user = db_user,
                        password = db_password,
                        host = db_host,
                        port = "6543",
                        dbname = db_name
    ))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

def get_monthly_sales_data(session, start_date, end_date):
    sql = text("""
        SELECT 
            TO_CHAR(TO_DATE(sales_ymd::text, 'YYYYMMDD'), 'YYYY-MM') AS sales_month, 
            SUM(amount) AS total_sales
        FROM 
            receipt
        WHERE 
            sales_ymd BETWEEN :start_date AND :end_date
        GROUP BY 
            sales_month
        ORDER BY 
            sales_month
    """)
    result = session.execute(sql, {'start_date': start_date, 'end_date': end_date})
    return pd.DataFrame(result.fetchall(), columns=['sales_month', 'total_sales'])


def get_top_stores(session, month):
    start_date = month * 100 + 1
    end_date = month * 100 + 31
    sql = text("""
        SELECT s.store_name, SUM(r.amount) AS total_sales
        FROM receipt r
        LEFT JOIN store s
        ON r.store_cd = s.store_cd
        WHERE r.sales_ymd BETWEEN :start_date AND :end_date
        GROUP BY s.store_name
        ORDER BY total_sales DESC
        LIMIT 10
    """)
    result = session.execute(sql, {'start_date': start_date, 'end_date': end_date})
    return pd.DataFrame(result.fetchall(), columns=['store_name', 'total_sales'])

# Streamlit アプリケーション
st.title("売上分析ダッシュボード")

# 期間ごとの売上データを抽出
start_date = st.sidebar.date_input("開始日", pd.to_datetime("2017-01-01"))
end_date = st.sidebar.date_input("終了日", pd.to_datetime("2019-09-30"))
sales_data = get_monthly_sales_data(session, int(start_date.strftime('%Y%m%d')), int(end_date.strftime('%Y%m%d')))

# DataFrameに変換
sales_df = pd.DataFrame(sales_data, columns=['sales_month', 'total_sales'])

# 最新月の売上合計と昨年比を表示
latest_month = sales_df['sales_month'].max()
latest_month_sales = sales_df[sales_df['sales_month'] == latest_month]['total_sales'].values[0]
previous_year_month = (pd.to_datetime(latest_month) - pd.DateOffset(years=1)).strftime('%Y-%m')
previous_year_sales = sales_df[sales_df['sales_month'] == previous_year_month]['total_sales'].values[0] if previous_year_month in sales_df['sales_month'].values else 0

st.subheader("最新月の売上合計と昨年比")
st.metric("最新月売上", f"{latest_month_sales:,}円", f"{(latest_month_sales - previous_year_sales) / previous_year_sales * 100:.2f}%" if previous_year_sales != 0 else "N/A")

# 月次売上の折れ線グラフを表示
st.subheader("月次売上推移")
fig, ax = plt.subplots()
sales_df.plot(x='sales_month', y='total_sales', ax=ax, marker='o')
ax.set_xlabel("Month")
ax.set_ylabel("Total Sales")
ax.set_title("Monthly Sales Trend")
st.pyplot(fig)

# トップ店舗ランキングを表示
st.subheader("トップ店舗ランキング")
month = int(st.sidebar.text_input("月", "201804"))
top_stores = get_top_stores(session, month)

top_stores_df = pd.DataFrame(top_stores, columns=['store_name', 'total_sales'])
st.table(top_stores_df)

st.write("データの出典：「データサイエンティスト協会スキル定義委員」の「データサイエンス100本ノック（構造化データ加工編）」")

# セッションを閉じる
session.close()
