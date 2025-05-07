import streamlit as st
from transformers import pipeline
from huggingface_hub import login
import PyPDF2
import docx
import io

# Đăng nhập Hugging Face (lưu token trong Streamlit Secrets)
login(st.secrets["HUGGINGFACE_TOKEN"])

# Dùng mô hình nhẹ hỗ trợ tiếng Nhật
model_name = "izumi-lab/t5-base-japanese-title-generation"
summarizer = pipeline("summarization", model=model_name, tokenizer=model_name)

# Đọc nội dung từ file
def read_file(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return file.read().decode("utf-8")

# Tóm tắt văn bản
def summarize_text(text):
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    summaries = []
    for chunk in chunks:
        result = summarizer(chunk, max_length=64, min_length=10, do_sample=False)
        summaries.append(result[0]['summary_text'])
    return "。".join(summaries)

# Tạo câu hỏi trắc nghiệm đơn giản
def generate_quiz(summary):
    sentences = summary.split("。")
    sentences = [s.strip() for s in sentences if s.strip()]
    questions = []
    max_questions = min(len(sentences), 10)

    for i, sentence in enumerate(sentences[:max_questions]):
        q = f"質問 {i+1}: 「{sentence}」は正しいですか？"
        questions.append({"question": q, "options": ["はい", "いいえ"], "answer": "はい"})
    return questions

def main():
    st.title("📘 クイズメーカー - 日本語の文書から要約とクイズを作成")

    uploaded_file = st.file_uploader("PDF・Word・TXT ファイルをアップロード", type=["pdf", "docx", "txt"])

    if uploaded_file is not None:
        with st.spinner("処理中..."):
            text = read_file(uploaded_file)
            summary = summarize_text(text)
            st.subheader("📝 要約:")
            st.write(summary)

            quiz = generate_quiz(summary)
            st.subheader("🧠 クイズ:")
            for i, q in enumerate(quiz):
                user_answer = st.radio(q["question"], q["options"], key=i)
                if user_answer == q["answer"]:
                    st.success("正解です！")
                else:
                    st.error(f"不正解。正しい答えは: {q['answer']}")

if __name__ == "__main__":
    main()
