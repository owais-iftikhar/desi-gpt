from flask import Flask, render_template, request
import os
import csv

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

app = Flask(__name__)

llm = ChatGroq(
    api_key=groq_api_key,
    model="llama3-70b-8192"
)

template = """
Tum aik smart programming assistant ho jo Pakistan ke students ki help karta hai.

📌 Jawab do hamesha do parts mein:
1️⃣ Pehle Roman Urdu mein, taake woh samajh sakein jinko Urdu script nahi aati.
2️⃣ Phir neeche same answer English mein do (lekin heading na do, bas likh do).

📌 Jawab:
- Hamesha friendly aur easy hona chahiye.
- Step-by-step samjhao, simple examples ke saath.
- Java ka code sirf tab do jab zaroori ho — code ko box ke andar do.
- Agar koi tumse tumhara naam poochay, to kehna: "Mera naam Desi GPT hai."

Har concept ko beginner ke liye explain karo — assume user bilkul naya hai.

Sawal: {question}
"""

prompt = PromptTemplate.from_template(template)
chain = prompt | llm | StrOutputParser()

@app.route("/", methods=["GET", "POST"])
def index():
    reply = ""
    if request.method == "POST":
        try:
            question = request.form.get("question", "")
            print("🟡 Question:", question)

            reply = chain.invoke({"question": question})
            # Save Q&A to CSV
            with open("chat_log.csv", "a", newline='', encoding="utf-8") as csvfile:
                   writer = csv.writer(csvfile)
                   writer.writerow([question, reply])

            
            print("✅ Reply:", reply)

            reply = reply.replace("**Roman Urdu**", "<b>Roman Urdu:</b>")
            reply = reply.replace("**English**", "<br><b>English:</b>")
            reply = reply.replace("```java", "<pre><code>").replace("```", "</code></pre>")
        except Exception as e:
            print("❌ Error:", str(e))
            reply = f"❌ Error: {e}"

    return render_template("index.html", reply=reply)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
