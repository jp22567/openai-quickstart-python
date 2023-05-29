import numpy as np
from rapidfuzz import fuzz, process 
from sklearn.metrics import f1_score

choices = ['apple', 'banana', 'cherry', 'date']

validation_set = [
    ('banana','banana', True),
    ('aple','apple', True),
    ('dae','date',True),
    ('ornge', 'orange', False),
]

threshold_vals = np.arange(50,101,1)
f1_scores = []

for threshold in threshold_vals:
    y_true = []
    y_pred = []

    for query, true_match, is_match in validation_set:
        bestmatch = process.extractOne(query, choices, scorer=fuzz.ratio)
        y_true.append(is_match)
        y_pred.append(bestmatch[1] >= threshold)

    f1 = f1_score(y_true, y_pred)
    f1_scores.append(f1)

best_threshold = threshold_vals[np.argmax(f1_scores)]
print(f1_scores)
print(y_pred, y_true)