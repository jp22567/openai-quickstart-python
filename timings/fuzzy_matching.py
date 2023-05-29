import rapidfuzz
import pandas as pd
# need to run nltk.download() when using for the first time
# this opens a window, in the download path just make it C:/(nltk_data) or whatever this is called
# this makes it so you dont have to set an environmental variable
import nltk 

mapi = pd.read_csv(r"C:\Users\Jakub\Documents\zazu\openai-quickstart-python\timings\mapi_list_sn_ln.csv")
mapi.iloc[3752][0] = ""


# function for sorting
def key(tup):
    return tup[1]

def convertTuple(tup):
    # initialize an empty string
    str = ''
    for item in tup:
        str = str + " " + item
    return str

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
        if not 'None found' in x and len(x) < 1001:
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
        skews = ('life','Life','of','questionnaire','questionnaires','Questionnaire','Questionnaires', '-')
        tokens = [token if token not in skews else '' for token in tokens]
        string = ' '.join(tokens)
        string = string.replace(',','').strip()
        temp_list4.append(string)
    # print(temp_list4)
    return temp_list4

# my version of the rapidfuzz.process.extract_iter() which allows for change of weights of the processor
# compares the string with all the long names in the csv above
def weighted_iter_long(string, weight_cut_off=0.8):
    matches = []
    choices = mapi.long_name

    for choice in choices:
        score = rapidfuzz.distance.Levenshtein.normalized_similarity(string, choice, processor=rapidfuzz.utils.default_process, weights=(1,1,1))
        # remove incomplete answers where '...' occurs
        if score >= weight_cut_off and "..." not in choice:
            matches.append((choice, score))
    
    # sort the list in descending order
    matches = sorted(matches, key=key, reverse=True)
    # print('matches', matches)
    
    return matches

# same as above but for the short names
# splits the string to compare the individual tokens to the short names
def weighted_iter_short(string, weight_cut_off=0.8):
    matches = []
    tokens = string.split()
    nltk_tokens = nltk.word_tokenize(string)
    trigrams = list(nltk.ngrams(nltk_tokens,3))
    trigrams = [convertTuple(tup).strip() for tup in trigrams]
    
    bigrams = list(nltk.bigrams(nltk_tokens))
    bigrams = [convertTuple(tup).strip() for tup in bigrams]
    # print('bigrams',bigrams)
    tokens = [token if token != 'questionnaire' else '' for token in tokens]
    choices = mapi.short_name
    for token in tokens:
        for choice in choices:
            score = rapidfuzz.distance.Levenshtein.normalized_similarity(token, choice, processor=rapidfuzz.utils.default_process, weights=(1,1,1))
            if score >= weight_cut_off and "..." not in choice:
                matches.append((choice, score))
    for token in bigrams:
        for choice in choices:
            score = rapidfuzz.distance.Levenshtein.normalized_similarity(token, choice, processor=rapidfuzz.utils.default_process, weights=(1,1,1))
            if score >= weight_cut_off and "..." not in choice:
                matches.append((choice, score))
    for token in trigrams:
        for choice in choices:
            score = rapidfuzz.distance.Levenshtein.normalized_similarity(token, choice, processor=rapidfuzz.utils.default_process, weights=(1,1,1))
            if score >= weight_cut_off and "..." not in choice:
                matches.append((choice, score))    
        
    matches = sorted(matches, key=key, reverse=True)
    # print('matches', matches)
    
    return matches


# join three algorithms to match long name
# all normalized scores are added together to find the closest match
# cutoffs can be changed to increase or the decrease number of potential answers but only the top answer is outputted 
def long_compound(string, weight_cut_off=0.8):

    weighted = weighted_iter_long(string, weight_cut_off=0.8)
    ratio = []
    for answer in weighted:
        y = rapidfuzz.fuzz.partial_ratio(string, answer[0],processor=rapidfuzz.utils.default_process)/100
        score = answer[1] + y
        ratio.append((answer[0], score))
    actual = []
    for answer in ratio:
        x = rapidfuzz.distance.Levenshtein.normalized_similarity(string, answer[0],processor=rapidfuzz.utils.default_process, weights=(1,0.999999,1))
        score = answer[1] + x
        actual.append((answer[0], score))
    
    actual = sorted(actual, key=key, reverse=True)
    # print('long', actual, string)
    cutoff = 2
    if len(actual) > 1:
        if actual[0][1] >= cutoff:
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
    # print(actual,string)
    return actual

# same as above but for short names
def short_compound(string,weight_cut_off=0.8):
    tokens = string.split()
    weighted = weighted_iter_short(string,weight_cut_off)
    # print('w', weighted)
    ratio = []
    for answer in weighted:
        for token in tokens:
            y = rapidfuzz.fuzz.partial_ratio(token, answer[0],processor=rapidfuzz.utils.default_process)/100
            score = answer[1] + y
            ratio.append((answer[0], score))
    # print('ratio',ratio)
    actual = []
    for answer in ratio:
        for token in tokens:
            x = rapidfuzz.distance.Levenshtein.normalized_similarity(string, answer[0], weights=(1,0.999999,1),processor=rapidfuzz.utils.default_process)
            score = answer[1] + x
            actual.append((answer[0], score))
    actual = list(filter(None, actual))
    actual = list(dict.fromkeys(actual))
    actual = sorted(actual, key=key, reverse=True)
    # print('actual',actual)
    
    cutoff = 2.4
    if len(actual) > 1:
        if actual[0][1] >= cutoff:
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
    # print('short', actual,string)
    return actual


# join the short + long name functions, taking the best score 
# s stands for short name and l for long name
def joint(string, weight_cut_off=0.8):
    short = short_compound(string, weight_cut_off=0.8)
    long  = long_compound(string, weight_cut_off=0.8)
    print(string, short , long)
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

def fuzzy_matching(answers, weight_cut_off=0.8):
    cleaned_answers1 = answer_cleaning1(answers)
    cleaned_answers = answer_cleaning(cleaned_answers1)
    cleaned_answers = answer_cleaning(cleaned_answers)
    questionnaires = []
    for answer in cleaned_answers:
        questionnaires.append(joint(answer, weight_cut_off=0.8))
    return questionnaire_output(questionnaires)