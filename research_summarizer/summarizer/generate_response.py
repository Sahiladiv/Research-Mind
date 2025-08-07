from langchain.prompts import ChatPromptTemplate
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI 

PROMPT_TEMPLATE = """
Answer the question based on the following context:

{context}

--------

Answer the question based on the following query:

{question}
"""

def generate_response_using_llm(question, context, openai_api_key, request):
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context, question=question)
    print("MODEL USED:",request.session['selected_lm'])
    model_to_be_used = request.session['selected_lm']
    llm = ChatOpenAI(model_name=model_to_be_used)
    response = llm.predict(prompt)
    
    return response
