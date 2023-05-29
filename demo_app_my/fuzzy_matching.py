import rapidfuzz
import pandas as pd

# csv of questionnaires
mapi = pd.read_csv(r"C:\Users\Jakub\Documents\zazu\openai-quickstart-python\demo_app_my\mapi_list_sn_ln.csv")
mapi.iloc[3752][0] = ""

# function for sorting
def key(tup):
    return tup[1]

# clean the answers before trying to match
def answer_cleaning1(my_list):
    templist1 = []
    for answer in my_list:
        if 'None found' not in answer:
            templist1.append(answer)
    return templist1


def answer_cleaning(my_list):
    temp_list1 = []
    temp_list2 = []
    temp_list3 = []
    temp_list4 = []
    for x in my_list:
        if not 'None found' in x:
            # if not x == 'No validated clinical questionnaires were used in this text.':
            temp_list1.append(x)
    for y in temp_list1:
        split = y.split('\n')
        for s in split:
            temp_list2.append(s)
    for z in temp_list2:
        if not 'not a questionnaire' in z:
            temp_list3.append(z)
    for string in temp_list3:
        tokens = string.split()
        # word 'questionnaire' skews answers so remove it
        tokens = [token if token != 'questionnaire' else '' for token in tokens]
        tokens = [token if token != 'Questionnaire' else '' for token in tokens]
        string = ' '.join(tokens)
        temp_list4.append(string)
    print(temp_list4)
    return temp_list4

# my version of the rapidfuzz.process.extract_iter() which allows for change of weights of the processor
# compares the string with all the long names in the csv above
def weighted_iter_long(string):
    matches = []
    choices = mapi.long_name
    cut_off = 0.8

    for choice in choices:
        score = rapidfuzz.distance.Levenshtein.normalized_similarity(string, choice, processor=rapidfuzz.utils.default_process, weights=(0.999999,1,1))
        # remove incomplete answers where '...' occurs
        if score >= cut_off and "..." not in choice:
            matches.append((choice, score))
    
    # sort the list in descending order
    matches = sorted(matches, key=key, reverse=True)
    
    return matches

# same as above but for the short names
# splits the string to compare the individual tokens to the short names
def weighted_iter_short(string):
    matches = []
    tokens = string.split()
    tokens = [token if token != 'questionnaire' else '' for token in tokens]
    choices = mapi.short_name
    cut_off = 0.8
    for token in tokens:
        for choice in choices:
            score = rapidfuzz.distance.Levenshtein.normalized_similarity(token, choice, processor=rapidfuzz.utils.default_process, weights=(1,0.999999,1))
            if score >= cut_off and "..." not in choice:
                matches.append((choice, score))
        
    matches = sorted(matches, key=key, reverse=True)
    
    return matches


# join three algorithms to match long name
# all normalized scores are added together to find the closest match
# cutoffs can be changed to increase or the decrease number of potential answers but only the top answer is outputted 
def long_compound(string, long=True):

    weighted = weighted_iter_long(string)
    ratio = []
    for answer in weighted:
        y = rapidfuzz.fuzz.partial_ratio(string, answer[0])/100
        score = answer[1] + y
        ratio.append((answer[0], score))
    actual = []
    for answer in ratio:
        x = rapidfuzz.distance.Levenshtein.normalized_similarity(string, answer[0], weights=(1,1,1))
        score = answer[1] + x
        actual.append((answer[0], score))
    
    actual = sorted(actual, key=key, reverse=True)
    cutoff = 1.6
    if len(actual) > 1:
        if actual[1][1] >= cutoff:
            actual = actual[0]
        else:
            actual = ()
    elif len(actual) == 1:
        if actual[0][1] >= cutoff:
            actual = actual[0]
        else:
            actual = ()
    else:
        actual = ()
    print(actual,string)
    return actual

# same as above but for short names
def short_compound(string):
    tokens = string.split()
    weighted = weighted_iter_short(string)
    ratio = []
    for answer in weighted:
        for token in tokens:
            y = rapidfuzz.fuzz.partial_ratio(token, answer[0])/100
            score = answer[1] + y
            ratio.append((answer[0], score))
    actual = []
    for answer in ratio:
        for token in tokens:
            x = rapidfuzz.distance.Levenshtein.normalized_similarity(string, answer[0], weights=(1,1,1))
            score = answer[1] + x
            actual.append((answer[0], score))

    actual = list(filter(None, actual))
    actual = list(dict.fromkeys(actual))
    actual = sorted(actual, key=key, reverse=True)
    
    cutoff = 2.6
    if len(actual) > 1:
        if actual[1][1] >= cutoff:
            actual = actual[0]
        else:
            actual = ()
    elif len(actual) == 1:
        if actual[0][1] >= cutoff:
            actual = actual[0]
        else:
            actual = ()
    else:
        actual = ()
    print(actual,string)
    return actual


# join the short + long name functions, taking the best score 
# s stands for short name and l for long name
def joint(string):
    short = short_compound(string)
    long  = long_compound(string)
    # print(string, short , long)
    best = (long, 'l')
    if short and not long:
        best = (short,'s')
    if short and long:
        if short[1] > long[1]:
            best = (short,'s')
    if best[0]:
        best = best[0][0], best[1]
    return best

# cleans the questionnaires and matches long and short names, outputting a dictionary
def questionnaire_output(my_list):
    new = list(filter(None, my_list))
    almost = {}
    short = []
    long = []
    for q in new:
        if q[1] == 's':
            short.append(q[0])
        else:
            long.append(q[0])
    short = list(filter(None, short))
    long = list(filter(None, long))
    for q in short:
        idx = mapi.index[mapi['short_name'] == q]
        if mapi.iloc[idx[0]][0] not in almost:
            almost[mapi.iloc[idx[0]][0]] = mapi.iloc[idx[0]][1]

    for q in long:
        idx = mapi.index[mapi['long_name'] == q]
        if mapi.iloc[idx[0]][0] not in almost:
            almost[mapi.iloc[idx[0]][0]] = mapi.iloc[idx[0]][1]


    return almost

def fuzzy_matching(answers):
    cleaned_answers1 = answer_cleaning1(answers)
    cleaned_answers = answer_cleaning(cleaned_answers1)
    cleaned_answers = answer_cleaning(cleaned_answers)
    questionnaires = []
    for answer in cleaned_answers:
        questionnaires.append(joint(answer))
    return questionnaire_output(questionnaires)


def main():
    answers = ['None found', '- DTR-QOL, Diabetes Therapy-Related Quality of Life Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', 'None found', 
'- DTR-QOL, DTR-QOL Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', '- DTSQ, Diabetes Treatment Satisfaction Questionnaire\n- DTR-QOL, Diabetes Therapy-Related QOL', '- DTR-QOL, Diabetes Therapy-Related QOL Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', '- DTR-QOL, Diabetes Therapy-Related Quality of Life', 'None found', '- DTR-QOL, Diabetes Therapy-Related Quality of Life Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', '- DTR-QOL, DTR-QOL Questionnaire\n- DTSQ, DTSQ Questionnaire', 'None found', 'None found', 'None found', 'None found', 'None found', 'None found', 'DTR-QOL, Development and Psychometric Validation of the Diabetes Therapy-Related QOL Questionnaire\nDTSQ, Diabetes Treatment Satisfaction Questionnaire', '- DTR-QOL, Diabetes Therapy-Related Quality of Life Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', 'None found', '- DTR-QOL, Diabetes Treatment-Related Quality of Life Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', '- DTSQ, Diabetes Treatment Satisfaction Questionnaire\n- DTR-QOL, Diabetes Therapy-Related QOL', '- DTR-QOL, Diabetes Therapy-Related Quality of Life Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', '- DTR-QOL, Diabetes Treatment-Related Quality of Life', 'None found', 'None found.', '- DTR-QOL, Diabetes Therapy-Related QOL Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', '- DTR-QOL Questionnaire\n- DTSQ', 'None found', 
'None found', 'None found', '- DTR-QOL, Diabetes Therapy-Related Quality of Life Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', 'None found', '- DTR-QOL, Diabetes Therapy-Related Quality of Life\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire']
    answers = ['None found', '- EQ-5D-5L, European Quality of Life 5-Dimensions health questionnaire\n- EQ-5D-Y, EQ-5D Youth\n- FAIM, Food Allergy Independent Measure\n- FAQL-PB, Food Allergy Quality of Life - Parental Burden\n- FAQLQ, Food Allergy Quality of Life Questionnaire\n- HADS, Hospital Anxiety and Depression Scale\n- TSQM-9, Treatment Satisfaction Questionnaire for Medication', '- FAQLQ-PF, Food Allergy Quality of Life Questionnaire - Parent Form\n- FAQLQ-PFT, Food Allergy Quality of Life Questionnaire - Parent Form for Teens\n- FAIM, Food Allergy Independent Measure\n- FAQLQ-CF, Food Allergy Quality of Life Questionnaire - Child Form\n- FAIM-CF, Food Allergy Independent Measure - Child Form\n- FAQLQ-TF, Food Allergy Quality of Life Questionnaire - Teen Form\n- FAIM-TF, Food Allergy Independent Measure - Teen Form\n- TNSS, Total Nasal Symptom Score\n- SCORAD, Scoring Atopic Dermatitis\n- ACT, Asthma Control Test', '- FAQL-PB Questionnaire\n- HADS Questionnaire\n- EQ-5D Questionnaires\n- TSQM-9 Questionnaire\n- Exit Questionnaire\n- PEESS v2.0 Questionnaire\n- TNSS Questionnaires\n- SCORAD Index', '- ACT, Asthma Control Test\n- C-ACT, Childhood Asthma Control Test\n- EQ-5D, European Quality of Life 5-Dimensions health questionnaire\n- EQ-5D-5L, EQ-5D 5-Levels\n- EQ-5D-Y, EQ-5D Youth\n- FAIM, Food Allergy Independent Measure\n- FAIM-CF, FAIM - child form\n- FAIM-PF, FAIM - parent form\n- FAIM-PFT, FAIM - parent form teenager\n- FAIM-TF, FAIM - teenager form\n- FAQL-PB, Food Allergy Quality of Life - Parental Burden\n- FAQLQ, Food Allergy Quality of Life Questionnaire\n- FAQLQ-CF, FAQLQ - child form\n- FAQLQ-PF, FAQLQ - parent form\n- FAQLQ-PFT, FAQLQ - parent form teenager\n- FAQLQ-TF, FAQLQ - teenager form\n- HADS, Hospital Anxiety and Depression Scale\n- PEESS v2.0, Pediatric Eosinophilic Esophagitis Symptom Scores version 2.0\n- TNSS, Total Nasal Symptom Score\n- TSQM-9, Treatment Satisfaction Questionnaire for Medication', 'None found', 'None found', 'None found', 'None found', '- EQ-5D-5L, European Quality of Life 5-Dimensions 5-Levels health questionnaire\n- EQ-5D-Y, EQ-5D Youth', 'None found', '- EQ-5D, European Quality of Life 5-Dimensions health questionnaire\n- FAQLQ, Food Allergy Quality of Life Questionnaire\n- FAIM, Food Allergy Independent Measure', '- PEESS v2.0, Pediatric Eosinophilic Esophagitis Symptom Scores version 2.0', 'None found', 'None found', 'None found', 'None found', 'None found', 'None found', '- PEESS v2.0, Pediatric Eosinophilic Esophagitis Symptom Score v2.0\n- EQ-5D, European Quality of Life 5-Dimension Questionnaire', '- FAQLQ-PF, Food Allergy Quality of Life Questionnaire - Parent Form\n- FAQLQ-PFT, Food Allergy Quality of Life Questionnaire - Parent Form Teenager\n- FAQLQ-CF, Food Allergy Quality of Life Questionnaire - Child Form\n- FAQLQ-TF, Food Allergy Quality of Life Questionnaire - Teenager Form\n- FAIM-PF, Food Allergy Independent Measure - Parent Form\n- FAIM-PFT, Food Allergy Independent Measure - Parent Form Teenager\n- FAIM-CF, Food Allergy Independent Measure - Child Form\n- FAIM-TF, Food Allergy Independent Measure - Teenager Form\n- FAQL-PB, Food Allergy Quality of Life - Parental Burden\n- HADS, Hospital Anxiety and Depression Scale\n- EQ-5D, European Quality of Life 5-Dimension Questionnaire\n- TSQM-9, Treatment Satisfaction Questionnaire for Medication', '- EQ-5D-5L, European Quality of Life 5-Dimensions health questionnaire 5-Levels\n- EQ-5D-Y, European Quality of Life 5-Dimensions health questionnaire Youth\n- FAQL-PB, Food Allergy Quality of Life - Parental Burden\n- HADS, Hospital Anxiety and Depression Scale\n- FAQLQ-PF, Food Allergy Quality of Life Questionnaire - Parent Form\n- FAQLQ-PFT, Food Allergy Quality of Life Questionnaire - Parent Form Teenager\n- FAQLQ-CF, Food Allergy Quality of Life Questionnaire - Child Form\n- FAQLQ-TF, Food Allergy Quality of Life Questionnaire - Teenager Form\n- FAIM-PF, Food Allergy Independent Measure - Parent Form\n- FAIM-PFT, Food Allergy Independent Measure - Parent Form Teenager\n- FAIM-CF, Food Allergy Independent Measure - Child Form\n- FAIM-TF, Food Allergy Independent Measure - Teenager Form\n- TSQM-9, Treatment Satisfaction Questionnaire for Medication', '- TSQM-9, Treatment Satisfaction Questionnaire for Medication-9\n- ACT, Asthma Control Test\n- C-ACT, Childhood Asthma Control Test', '- TNSS, Total Nasal Symptom Score\n- SCORAD, Scoring Atopic Dermatitis Index\n- PEESS v2.0, Pediatric Eosinophilic Esophagitis Symptom Score version 2.0', '- FAQLQ-PF, Food Allergy Quality of Life Questionnaire - Parent Form\n- FAQLQ-PFT, Food Allergy Quality of Life Questionnaire - Parent Form for Teens\n- FAQLQ-CF, Food Allergy Quality of Life Questionnaire - Child Form\n- FAQLQ-TF, Food Allergy Quality of Life Questionnaire - Teen Form\n- FAIM-PF, Food Allergy Independent Measure - Parent Form\n- FAIM-PFT, Food Allergy Independent Measure - Parent Form for Teens\n- FAIM-CF, Food Allergy Independent Measure - Child Form\n- FAIM-TF, Food Allergy Independent Measure - Teen Form\n- EQ-5D, European Quality of Life 5-Dimension Questionnaire\n- FAQL-PB, Food Allergy Quality of Life - Parental Burden\n- HADS, Hospital Anxiety and Depression Scale\n- TSQM-9, Treatment Satisfaction Questionnaire for Medication-Version 9', 'None found', 'None found', 'None found', '- SCORAD, Severity Scoring of Atopic Dermatitis\n- Food Allergy Quality of Life Questionnaire for Children\n- Food Allergy Quality of Life Questionnaire for Adolescents\n- Childhood Asthma Control Test\n- Pediatric Eosinophilic Esophagitis Symptom Scores (PEESS v2.0)\n- Food Allergy Quality of Life - Parental Burden Questionnaire\n- Asthma Control Test\n- Food Allergy Independent Measure (FAIM)\n- EQ-5D-5L, European Quality of Life 5-Dimension Questionnaire\n- EQ-5D-Y, European Quality of Life Youth Questionnaire\n- Hospital Anxiety and Depression Scale', 'None found', 'None found', 'None found', 'None found', '- EQ-5D\n- FAQL-PB\n- HADS\n- FAQLQ, FAIM', '- EQ-5D, European Quality of Life 5-Dimensions health questionnaire\n- EQ-5D-5L, EQ-5D 5-Levels\n- EQ-5D-Y, EQ-5D Youth\n- FAIM, Food Allergy Independent Measure\n- FAIM-CF, FAIM - child form\n- FAIM-PF, FAIM - parent form\n- FAIM-PFT, FAIM - parent form teenager\n- FAIM-TF, FAIM - teenager form\n- FAQL-PB, Food Allergy Quality of Life - Parental Burden\n- FAQLQ, Food Allergy Quality of Life Questionnaire\n- FAQLQ-CF, FAQLQ - child form\n- FAQLQ-PF, FAQLQ - parent form\n- FAQLQ-PFT, FAQLQ - parent form teenager\n- FAQLQ-TF, FAQLQ - teenager form\n- HADS, Hospital Anxiety and Depression Scale\n- PEESS v2.0, Pediatric Eosinophilic Esophagitis Symptom Scores version 2.0\n- SCORAD, scoring atopic dermatitis\n- TNSS, Total Nasal Symptom Score\n- TSQM-9, Treatment Satisfaction Questionnaire for Medication-9\n- ACT, Asthma Control Test\n- C-ACT, Childhood Asthma Control Test', '- EQ-5D-5L, European Quality of Life 5-Dimensions health questionnaire\n- EQ-5D-Y, EQ-5D Youth\n- FAIM, Food Allergy Independent Measure\n- FAIM-CF, FAIM - child form\n- FAIM-PF, FAIM - parent form\n- FAIM-PFT, FAIM - parent form teenager\n- FAIM-TF, FAIM - teenager form\n- FAQL-PB, Food Allergy Quality of Life - Parental Burden\n- FAQLQ, Food Allergy Quality of Life Questionnaire\n- FAQLQ-CF, FAQLQ - child form\n- FAQLQ-PF, FAQLQ - parent form\n- FAQLQ-PFT, FAQLQ - parent form teenager\n- FAQLQ-TF, FAQLQ - teenager form\n- PEESS v2.0, Pediatric Eosinophilic Esophagitis Symptom Scores version 2.0', '- EQ-5D, European Quality of Life 5-Dimensions health questionnaire\n- EQ-5D-5L, EQ-5D 5-Levels\n- EQ-5D-Y, EQ-5D Youth\n- FAIM, Food Allergy Independent Measure\n- FAIM-CF, FAIM - child form\n- FAIM-PF, FAIM - parent form\n- FAIM-PFT, FAIM - parent form teenager\n- FAIM-TF, FAIM - teenager form\n- FAQL-PB, Food Allergy Quality of Life - Parental Burden\n- FAQLQ, Food Allergy Quality of Life Questionnaire\n- FAQLQ-CF, FAQLQ - child form\n- FAQLQ-PF, FAQLQ - parent form\n- FAQLQ-PFT, FAQLQ - parent form teenager\n- FAQLQ-TF, FAQLQ - teenager form\n- HADS, Hospital Anxiety and Depression Scale', '- PEESS v2.0, Pediatric Eosinophilic Esophagitis Symptom Scores version 2.0']
    answers = ['None found', 'None found', '- FACT-P, Functional Assessment of Cancer Therapy-Prostate\n- FACT/GOG-NTX, Functional Assessment of Cancer Therapy/Gynecologic Oncology Group-Neurotoxicity\n- PROMIS Fatigue, Patient-Reported Outcomes Measurement Information System Fatigue', 'None found', 'None found', 'None found', 'None found', '- FACT P, Functional Assessment of Cancer Therapy - Prostate\n- FACT/GOG-NTX, Functional Assessment of Cancer Therapy/Gynecologic Oncology Group - Neurotoxicity\n- PROMIS Fatigue, Patient-Reported Outcomes Measurement Information System Fatigue', '- FACT-P-TOI\n- FACT/GOG-NTX\n- PROMIS Fatigue', 'None found', 'None found', '- FACT-P, Functional Assessment of Cancer Therapy - Prostate', '- FACT/GOG-NTX, FACT/GOG-NTX (Version 4)\n- PROMIS Fatigue, Fatigue - Short Form 7a\n- ECOG PERFORMANCE STATUS, ECOG/KPS Conversion Table\n- Overall Treatment Utility Form, OTU', 'None found']  
    answers = ['- FACT-G, Version 4\n- EQ-5D-5L, Questionnaire', 'None found', 'None found', '- EQ-5D-5L, EuroQol group descriptive questionnaire system\n- FACT-G, Functional Assessment of Cancer Therapy-General', '- EQ-5D-5L, European Quality of Life 5-Dimension Questionnaire\n- FACT-G, Functional Assessment of Cancer Therapy-General', 'None found', 'None found', 'None found', 'None found', 'None found', 'None found', 'None found', 'None found', 'None found', 'None found', '- EQ-5D, Patient reported quality of life (QOL) using EQ-5D\n- FACT-G, Patient reported quality of life (QOL) using FACT-G', 'None found', 'None found', 'None found', 'None found', 'None found', 'None found', 'None found', 'None found', 'None found', '- FACT-G, Functional Assessment of Cancer Therapy-General\n- EQ-5D-5L, Health Questionnaire', '- EQ-5D-5L, EuroQol 5-Dimension 5-Level Questionnaire\n- FACT-G, Functional Assessment of Cancer Therapy - General']
    answers = ['None found', '- DTR-QOL, Diabetes Therapy-related QOL Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', 'None found', '- DTR-QOL, Diabetes Therapy-Related QOL Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', '- DTSQ, Diabetes Treatment Satisfaction Questionnaire\n- DTR-QOL, Diabetes Therapy-Related QOL', '- DTR-QOL, Diabetes Therapy-Related Quality of Life Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', '- DTR-QOL, Diabetes Treatment-Related Quality of Life', 'None found', '- DTR-QOL, Diabetes Therapy-Related QOL Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', '- DTR-QOL, Diabetes Therapy-Related QOL\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', 'None found', 'None found.', 'None found', 'None found', 'None found', 'None found', '- DTR-QOL, Diabetes Therapy-Related QOL\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', '- DTR-QOL, DTR-QOL Questionnaire\n- DTSQ, DTSQ', 'None found', '- DTR-QOL, Diabetes Therapy-Related Quality of Life Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', '- DTSQ, Diabetes Treatment Satisfaction Questionnaire\n- DTR-QOL, Diabetes Therapy-Related QOL', '- DTR-QOL, Diabetes Treatment-Related Quality of Life Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', '- DTR-QOL, Diabetes Treatment-Related Quality of Life', 'None found', 'None found', '- DTR-QOL, Diabetes Therapy-Related Quality of Life Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', '- DTR-QOL Questionnaire\n- DTSQ', 'None found', 'None found', 'None found', '- DTR-QOL, Diabetes Therapy-Related Quality of Life\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire', 'None found', '- DTR-QOL, Diabetes Therapy-Related QOL Questionnaire\n- DTSQ, Diabetes Treatment Satisfaction Questionnaire']
    answers = ['None found.', '- DLQI, Dermatology Life Quality Index\n- EQ-5D, European Quality of Life 5-Dimension Questionnaire\n- Itch Numeric Rating Scale (NRS)\n- Skin Discomfort/Pain Visual Analog Scale (VAS)\n- Body Surface Area (BSA)\n- Psoriasis Area and Severity Index (PASI)\n- Patient Benefit Index (PBI)\n- Work Productivity and Activity Impairment Questionnaire: Psoriasis (WPAI: PSO)', '- DLQI, Dermatology Life Quality Index\n- EQ-5D, The European Quality of Life 5-Dimension Questionnaire', 'None found.', 'None found.', '- DLQI, Dermatology Life Quality Index\n- EQ-5D, European Quality of Life 5-Dimension Questionnaire\n- WPAI: PSO, Work Productivity and Activity Impairment Questionnaire for Psoriasis\n- Itch NRS, Itch Numeric Rating Scale\n- Skin Discomfort/Pain VAS, Visual Analog Scale for skin discomfort/pain\n- BSA, Body Surface Area affected by psoriasis\n- PBI, Patient Benefit Index\n- PASI, Psoriasis Area Severity Index\n- modified sPGA-G, Modified Static Physician Global Assessment-Genitalia\n- PPPGA, Palmoplantar Psoriasis Physician Global Assessment', 'DLQI, Dermatology Life Quality Index', 'None found.', 'None found.', 'DLQI, Dermatology Life Quality Index', '- Patient Benefit Index (PBI)\n- Patient Needs Questionnaire (PNQ)\n- Patient Benefit Questionnaire (PBQ)\n- European Quality of Life 5-Dimension Questionnaire (EQ-5D)\n- Work Productivity and Activity Impairment Questionnaire: Psoriasis (WPAI: PSO)', 'None found.', 'None found.', 'None found.', 'None found.', 'None found.', 'None found.', 'None found.', 'None found.', 'None found.', '- DLQI, Dermatology Life Quality Index\n- EQ-5D, European Quality of Life 5-Dimension Questionnaire', '- DLQI, Dermatology Life Quality Index\n- sPGA, Static Physicians Global Assessment\n- ScPGA, Scalp Physician Global Assessment\n- NAPSI, Nail Psoriasis Severity Index', 'None found.', '- EQ-5D, European Quality of Life 5-Dimension Questionnaire\n- PNQ, Patient Needs Questionnaire\n- PBQ, Patient Benefit Questionnaire', '- European Quality of Life 5-Dimension Questionnaire (EQ-5D)\n- Work Productivity and Activity Impairment Questionnaire: Psoriasis (WPAI: PSO)\n- Waist Circumference Measurement & Body Mass Index', 'None found.', 'None found.', 'None found.', 'None found.', 'None found.']
    
    print(fuzzy_matching(answers))

main()