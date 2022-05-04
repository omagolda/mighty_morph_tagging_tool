
from tqdm import tqdm
import os
import re

from pathlib import Path


def sanity_check_mighty_morph(file='fr-w_leff.txt', dir=""):
    dir = os.path.join(dir, 'mighty_morph', file)

    mighty_morph_lemma_feat = {}
    mighty_morph_lemma_feat_no_aux = {}

    mighty_morph_lemma_form = {}

    n_total = sum(1 for _ in open(dir, encoding="utf-8"))
    # aggregate
    with open(dir, encoding="utf-8") as f:
        for line in tqdm(f, total=n_total):
            line = line.strip().split("\t")
            lemma = line[0]
            form = line[1]
            features = line[2]

            lemma_feat = f"{lemma}|{features}"
            if features.startswith("a;") or features.startswith("e;"):
                lemma_feat_no_aux = f"{lemma}|{features[2:]}"
            else:
                lemma_feat_no_aux = lemma_feat

            lemma_form = f"{lemma}|{form}"

            if lemma_feat not in mighty_morph_lemma_feat:
                mighty_morph_lemma_feat[lemma_feat] = []
            if lemma_feat_no_aux not in mighty_morph_lemma_feat_no_aux:
                mighty_morph_lemma_feat_no_aux[lemma_feat_no_aux] = []

            if lemma_form not in mighty_morph_lemma_form:
                mighty_morph_lemma_form[lemma_form] = []

            mighty_morph_lemma_feat[lemma_feat].append(form)
            mighty_morph_lemma_feat_no_aux[lemma_feat_no_aux].append(form)

            mighty_morph_lemma_form[lemma_form].append(features)

    # check
    n_doublon = 0

    for lemma_feat_no_aux in tqdm(mighty_morph_lemma_feat_no_aux):
        try:
            assert len(mighty_morph_lemma_feat_no_aux[lemma_feat_no_aux]) == 1, \
                f"Doublon: (lemma, feature) not in injection with form {lemma_feat_no_aux} {mighty_morph_lemma_feat_no_aux[lemma_feat_no_aux]}"
        except Exception as e:
            n_doublon += 1
            #print(e)
    if n_doublon == 0:
        print("AUX MATTERS: There is a unique form for each (lemma, feature without e/a)")
    else:
        print(f"There is no bijeciton {n_doublon}/{len(mighty_morph_lemma_feat_no_aux)} doublons")

    for lemma_feat in tqdm(mighty_morph_lemma_feat):
        assert len(mighty_morph_lemma_feat[lemma_feat]) == 1, "doublon: (lemma, feature) not in injection with form "
            #print("Doublon one lemma-feature --> is associated to two forms: ", lemma_feat,"-->", mighty_morph_lemma_feat[lemma_feat])
    print("There is a unique form for each (lemma, feature)")

    #  print("Doublon one lemma-feature --> is associated to two forms: ", lemma_feat,"-->", mighty_morph_lemma_feat[lemma_feat])
    n_doublon = 0
    for lemma_form in tqdm(mighty_morph_lemma_form):
        if len(mighty_morph_lemma_form[lemma_form]) > 1:
            print("Doublon one lemma-form --> is associated to two features: ", lemma_form,"-->", mighty_morph_lemma_form[lemma_form])

    if n_doublon == 0:
        print("There is a unique feature for each (lemma, form)")




if __name__ == "__main__":
    #sanity_check_mighty_morph(dir="/Users/bemuller/Documents/Work/INRIA/dev/mighty_morph_tagging_tool")
    path = Path('/Users/bemuller/Documents/Work/INRIA/dev/mighty_morph_tagging_tool')
    aggregate_gender_mark(path/'mighty_morph'/'fr-w_leff.txt', path/'mighty_morph'/'fr-w_leff_final.txt')