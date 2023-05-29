# Import necessary packages
import os
import pickle

from google.auth.transport.requests import Request

from google_auth_oauthlib.flow import InstalledAppFlow
from llama_index import GPTSimpleVectorIndex, download_loader
from llama_index import (
    GPTKeywordTableIndex,
    SimpleDirectoryReader,
    LLMPredictor,
    ServiceContext
)
from langchain.chat_models import ChatOpenAI

def authorize_gdocs():
    google_oauth2_scopes = [
        "https://www.googleapis.com/auth/documents.readonly"
    ]
    cred = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", 'rb') as token:
            cred = pickle.load(token)
    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", google_oauth2_scopes)
            cred = flow.run_local_server(port=0)
        with open("token.pickle", 'wb') as token:
            pickle.dump(cred, token)

# function to authorize or download latest credentials 
authorize_gdocs()

# initialize LlamaIndex google doc reader 
GoogleDocsReader = download_loader('GoogleDocsReader')

# list of google docs we want to index 
gdoc_ids = ['12ihdlVRd4d_nMw4erslep5HbKIRQU0XmpdCJrqytSBE']
# gdoc_ids = ['1EZCXJdWHIkkOmMEre-yNQlOubSbZaGQvoKEy5-Qi9n8']


loader = GoogleDocsReader()

# load gdocs and index them 
documents = loader.load_data(document_ids=gdoc_ids)
llm_predictor = LLMPredictor(llm=ChatOpenAI(model_name='gpt-3.5-turbo'))
service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
index = GPTSimpleVectorIndex.from_documents(documents, service_context=service_context)

text = """Assessment/Measure	No. Questions	Screening	Baseline	Complete Online course	One month after Online course	6 months after Online course	12 months after Online course	2.5 years after Online course
Informed consent	1	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X
Age	1	SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X
MS type diagnosed	2	SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X
MS duration	2	SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X
Do you follow a MS-specific lifestyle program?	2	SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED  X
Do you follow a MS-specific diet	2	SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X
Sex and gender	2	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X
Residential address and country	1	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X
Country of birth	1	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X
Height/weight	2	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X
Comorbidities	2	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X
Marital status	1	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X
Education	1	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X
Employment status	1	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X
Alcohol and smoking	4	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X
Medications	4	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X
Perceived Social Support	12	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X
Lifestyle factors		NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X
Physical activity: IPAQ-SF	7	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X
Meditation: MAQ	3	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X
Sun exposure	4	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X
Diet quality: DHQ	21	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X
Omega-3 intake: dose, frequency	3	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X
Vitamin D intake: dose, frequency	3	SELECTED  X	NOT SELECTED X	NOT SELECTED X	SELECTED  X	SELECTED X	SELECTED X	SELECTED X
Health outcomes		NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X	NOT SELECTED X
HRQOL: MSQOL-54	54	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X	NOT SELECTED X
Disability: PDDS	1	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X	NOT SELECTED X
Anxiety and depression: HADS	14	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X	NOT SELECTED X
Fatigue: FSS	9	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED  X	SELECTED X	SELECTED  X	NOT SELECTED X
Self-efficacy: UWSE-6	6	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	SELECTED X	SELECTED X	NOT SELECTED X
Qualitative interviewing	-7	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X	SELECTED X	NOT SELECTED X	NOT SELECTED X

"""

# prompt = f"Which validated clinical questionnaires appear in this text: "
prompt = f"Which of the questionnaires in the context appear in the following text:{text}?"
# prompt = f"what questionnaires appear in the following text:{text}?"
# prompt = f"what questionnaires appear in the context?"


response = index.query(prompt)
print(response)

# Querying the index
# while True:
#     prompt = input("Type prompt...")
#     response = index.query(prompt)
#     print(response)