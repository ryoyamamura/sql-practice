import pandas as pd
import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
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


st.set_page_config(
    page_title="SQL × PyGwalker でデータ可視化",
    layout="wide",
    page_icon=":shopping_trolley:"
)

st.write('''
# :shopping_trolley: スーパーの購買データ分析 :receipt:
:bar_chart: **SQL** と **PyGWalker** を使って分析してみましょう :bulb:   
:mag: データベースの ER 図はページ下部の「ER 図を見る」ボタンで表示できます 
''')

# サイドバーにアプリの使い方を記載
st.sidebar.title("How to Use")
st.sidebar.write("""                 
1. SQL クエリをテキストボックスに入力してください.
2. 「SQL クエリ実行」ボタンを押してクエリを実行できます。
3. クエリ結果が下に表示されます。
4. 「PyGWalker で可視化」ボタンを押すとクエリ結果をもとにした PyGWalker のエディタ画面が開きます。  

※ PyGWalker の使い方は[PyGWalker 公式ドキュメント](https://docs.kanaries.net/ja/graphic-walker/data-viz/create-data-viz)をご覧ください。
""")

# データベースにクエリを発行し、返り値として DataFrame を取り出す関数を定義
def extract_data(query: str, connection) -> pd.DataFrame:
  # SQL 文の定義
  query = text(query)

  # SQL 文の実行
  df_sql = pd.read_sql(sql=query, con=connection)
  return df_sql

# エラーの際に SQL クエリを保存する関数を定義
def log_error(query: str, error_message: str) -> None:
    log_query = """
    INSERT INTO error_logs (query, error_message)
    VALUES (:query, :error_message)
    """
    with engine.connect() as connection:
        with connection.begin():
            connection.execute(text(log_query), {'query': query, 'error_message': error_message})

# SQL入力フォーム
sql_query = st.text_area("SQL クエリをここに書いてください", height=150)

# ボタンの状態を保持するセッションステートを初期化
if 'submit_button' not in st.session_state:
    st.session_state['submit_button'] = False

if 'show_pygwalker_button' not in st.session_state:
    st.session_state['show_pygwalker_button'] = False

# クエリ実行と結果表示
if st.button("SQL クエリ実行"):
    st.session_state['submit_button'] = True

if st.session_state['submit_button']:
    if sql_query.strip() == "":
        st.error("SQL クエリが空の状態です")
    else:
        try:
            with engine.connect() as connection:
                result = extract_data(sql_query, connection)
                st.dataframe(result)
            if st.button("PyGWalker で可視化"):
                st.session_state['show_pygwalker_button'] = True            
            if st.session_state['show_pygwalker_button']:
                pyg_app = StreamlitRenderer(result)
                pyg_app.explorer()
            # クエリ実行と結果表示
        except SQLAlchemyError as e:
            st.error(f"SQL エラー: {e}")
            error_message = str(e)
            log_error(sql_query, error_message)

# ER図のトグル表示
show_er_diagram = st.checkbox("ER 図を見る")
if show_er_diagram:
    st.image("100knocks_ER.png", caption="ER 図", use_column_width=True)

st.write("データの出典 :「データサイエンティスト協会スキル定義委員」の「[データサイエンス100本ノック（構造化データ加工編）](https://github.com/The-Japan-DataScientist-Society/100knocks-preprocess)」を使用しています")
