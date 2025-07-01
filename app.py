
import streamlit as st
import google.generativeai as genai
import pypdf
import io

def extract_text_from_pdf(pdf_file):
    """アップロードされたPDFファイルからテキストを抽出する"""
    try:
        pdf_reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"PDFの読み込み中にエラーが発生しました: {e}")
        return None

def summarize_text(api_key, model_name, text):
    """Gemini APIを使用してテキストを要約する"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        以下の英語の学術論文を読み、指定された項目に従って情報を抽出・要約してください。

        【指示】
        1.  まず、論文の本文から「タイトル」と「著者」を正確に抽出してください。
        2.  次に、以下の項目について日本語で要約してください。
            - 「背景・目的」
            - 「方法」
            - 「結果・考察」
            - 「主張の限界・残された課題」
        3.  「参考文献」は原文のまま抽出し、各文献を改行で区切ってリスト形式にしてください。
        4.  出力は全体としてマークダウン形式で、各セクションのタイトル（「タイトル」「著者」「背景・目的」など）のみを `###` を使って記述し、本文は平文で出力してください（太字などの装飾は不要です）。

        【出力フォーマット】
        ### タイトル
        ここに抽出したタイトルを記述

        ### 著者
        ここに抽出した著者リストを記述

        ### 背景・目的
        ここに内容を記述

        ### 方法
        ここに内容を記述

        ### 結果・考察
        ここに内容を記述

        ### 主張の限界・残された課題
        ここに内容を記述

        ### 参考文献
        - 文献1
        - 文献2
        - ...

        ---

        【論文本文】
        {text}
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini APIとの通信中にエラーが発生しました: {e}")
        return None

# --- Streamlit App UI ---

st.title("英語論文要約アプリ")

# サイドバーでAPIキーとモデルを設定
st.sidebar.header("設定")
# Streamlit Community CloudのSecretsからAPIキーを取得
api_key = st.secrets.get("GEMINI_API_KEY")

# APIキーが設定されていない場合のメッセージ
if not api_key:
    st.sidebar.error("アプリをデプロイする管理者に連絡して、Gemini APIキーを設定してもらってください。")
    st.stop()
model_name = st.sidebar.selectbox(
    "使用するモデルを選択",
    ("gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-flash") 
)

# ファイルアップローダー
uploaded_file = st.file_uploader("英語の論文(PDF)をアップロードしてください", type="pdf")

# 実行ボタン
if st.button("要約を実行"):
    if api_key and uploaded_file:
        with st.spinner("論文を読み込んでいます..."):
            file_bytes = io.BytesIO(uploaded_file.getvalue())
            paper_text = extract_text_from_pdf(file_bytes)
        
        if paper_text:
            with st.spinner(f"{model_name} が論文を要約しています..."):
                summary = summarize_text(api_key, model_name, paper_text)
            
            if summary:
                st.subheader("要約結果")
                st.markdown(summary)

    elif not api_key:
        st.warning("サイドバーでGemini APIキーを入力してください。")
    else:
        st.warning("論文のPDFファイルをアップロードしてください。")
