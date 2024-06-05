import pandas as pd
import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer
# import matplotlib.pyplot as plt
# from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

import os
from dotenv import load_dotenv

# .envファイルの内容を読み込む
load_dotenv()

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


st.set_page_config(
    page_title="SQL × Pygwalker でデータ可視化",
    layout="wide"
)

# サイドバーにアプリの使い方を記載
st.sidebar.title("How to Use")
st.sidebar.write("""
1. SQL クエリをテキストボックスに入力してください.
2. 「SQL クエリ実行」ボタンを押してクエリを実行できます。
3. クエリ結果が下に表示されます。
4. 「PygWalker で可視化」ボタンを押すとクエリ結果をもとにした PygWalker のエディタ画面が開きます。
5. データベースの ER 図は「ER 図を見る」ボタンで表示できます。
""")

# データベースにクエリを発行し、返り値として DataFrame を取り出す関数を定義
def extract_data(query: str, connection=engine.connect()) -> pd.DataFrame:
  # SQL 文の定義
  query = text(query)

  # SQL 文の実行
  df_sql = pd.read_sql(sql=query, con=connection)
  return df_sql

# SQL入力フォーム
sql_query = st.text_area("SQL クエリをここに書いてください", height=150)
submit_button = st.button("SQL クエリ実行")

# クエリ実行と結果表示
if submit_button:
    if sql_query.strip() == "":
        st.error("SQL クエリが空の状態です")
    else:
        try:
            with engine.connect() as connection:
                result = extract_data(sql_query, connection)
                st.dataframe(result)
        except SQLAlchemyError as e:
            st.error(f"SQL エラー: {e}")

show_pygwalker_button = st.button("PygWalker で可視化")

if show_pygwalker_button:
    if sql_query.strip() == "":
        st.error("SQL クエリが空の状態です")
    else:
        try:
            with engine.connect() as connection:
                result = extract_data(sql_query, connection)
                pyg_app = StreamlitRenderer(result)
                pyg_app.explorer()                
        except SQLAlchemyError as e:
            st.error(f"SQL エラー: {e}")

# ER図のトグル表示
show_er_diagram = st.checkbox("ER 図を見る")
if show_er_diagram:
    st.image("100knocks_ER.png", caption="ER 図", use_column_width=True)

st.write("データの出典：「データサイエンティスト協会スキル定義委員」の「データサイエンス100本ノック（構造化データ加工編）」")