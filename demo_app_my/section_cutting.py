from PyPDF2 import PdfReader, PdfWriter
import pandas as pd
import csv
import os
import fitz
from re import search


# function for finding "relevant" pages where the questionnaires could occur.
def page_finder(protocol):
    # list of potential keywords to find relevant sections
    potential_sections = [
    "objective",
    "study endpoints",
    "event",
    "assessments",
    "activities",
    "abbreviations",
    "endpoint",
    "evaluation",
    "measure",
    "design",
    "synopsis",
    "questionnaire",
    "outcome",
    "patient reported",
    "definitions",
    "flow chart",
    "visits",
    "schedule",
    ]
    # table of contents
    # input_pdf = PdfReader(open(protocol, 'rb'))
    try:
        pdf = fitz.open(protocol)
        toc = pdf.get_toc()
        # header = page number
        section_titles = {}
        for item in toc:
            section_titles[item[1]] = item[2]
        # page numbers to extract
        page_nos = []
        for title in section_titles.keys():
            for potential in potential_sections:
                if search(potential, title.lower()):
                    page_nos.append(section_titles[title])
        page_nos = list(dict.fromkeys(page_nos))
        page_nos2 = page_nos.copy()
        for page in page_nos:
            page_nos2.append(page + 1)
        page_nos2 = list(dict.fromkeys(page_nos2))
        # try:
        #     if page_nos2[-1] >= len(input_pdf.pages):
        #         page_nos2.remove(page_nos2[-1])
        # except:
        #     print(protocol, "finder")
        return page_nos2
    except:
        print(protocol)


# take page numbers from page_finder and cut those pages out making a new pdf at the specified path
def pdf_writer(inpath,  outpath, page_nos):
    input_pdf = PdfReader(open(inpath,'rb'))
    output_pdf = PdfWriter()
    for i in page_nos:
        page = input_pdf.pages[i]
        output_pdf.add_page(page)
    with open(outpath, 'wb') as f:
        output_pdf.write(f)
        # ok_count += 1

        print("ok")


page_nos = page_finder(r"C:\Users\Jakub\Documents\zazu\openai-quickstart-python\demo_app\clinical_trial_rank_0005.pdf")

pdf_writer(r"C:\Users\Jakub\Documents\zazu\openai-quickstart-python\demo_app\clinical_trial_rank_0005.pdf", r"C:\Users\Jakub\Documents\zazu\openai-quickstart-python\demo_app\clinical_trial_rank_5.pdf", page_nos)