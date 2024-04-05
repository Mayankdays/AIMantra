from dotenv import load_dotenv
load_dotenv()
import os

from pdf_linker import get_pdf_link

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.6, google_api_key=GOOGLE_API_KEY)

import warnings
from pathlib import Path as p

import urllib
import warnings
from pathlib import Path as p
from pprint import pprint

from langchain_core.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from langchain_community.document_loaders import PyPDFLoader

warnings.filterwarnings("ignore")

data_folder = p.cwd() / "data"
p(data_folder).mkdir(parents=True, exist_ok=True)


def pdf_catcher(input):
    pdf_url = get_pdf_link(input)
    pdf_file = str(p(data_folder, pdf_url.split("/")[-1]))
    return pdf_file

def ai(messages, chapter):
    user_input = chapter[0]

    link = get_pdf_link(user_input)
    pdf = pdf_catcher(user_input)

    urllib.request.urlretrieve(link, pdf)

    pdf_loader = PyPDFLoader(pdf)
    pages = pdf_loader.load_and_split()

    prompt_template = """Answer the question as precise as possible using the provided context. If the answer is
                        not contained in the context, say "answer not available in context". If asked for a formula,
                        give the formula in LaTeX format, while rest of the text in Markdown format. \n\n
                        Context: \n {context}\n
                        Question: \n {question} \n
                        Answer:
                    """

    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    stuff_chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    
    question = messages[-1]  # only one message for Q&A model

    stuff_answer = stuff_chain(
        {
            "input_documents": pages, 
            "question": question
        }, 
        return_only_outputs=True
    )
    return stuff_answer