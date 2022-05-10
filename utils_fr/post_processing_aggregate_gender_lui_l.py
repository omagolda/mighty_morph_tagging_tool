

import os
import re

import numpy as np
from tqdm import tqdm
from pathlib import Path


def aggregate_gender_mark(dir, output_dir, add_readme=False):
    # handling DATIF lui and l' ACC FEM/MASC
    n_total = sum(1 for _ in open(dir, encoding="utf-8"))
    mighty_morph = {}

    with open(dir, encoding="utf-8") as f:
        for line in tqdm(f, total=n_total, desc="reading mightymorph"):
            line = line.strip().split("\t")
            lemma = line[0]
            form = line[1]
            form = re.sub('\\s+', ' ', form)
            features = line[2]
            if lemma not in mighty_morph:
                mighty_morph[lemma] = {}
            if form not in mighty_morph[lemma]:
                mighty_morph[lemma][form] = []
            mighty_morph[lemma][form].append(features)

    n_form_per_lemma = []
    n_line = 0

    with open(output_dir, "w", encoding="utf-8") as write:
        for lemma in tqdm(mighty_morph, "writing mightymorph/aggregating lui, l' "):
            n_form_per_lemma.append(len(mighty_morph[lemma]))
            for form in mighty_morph[lemma]:
                # remove multiple space

                # aggregate 'l' and 'lui'
                features = mighty_morph[lemma][form]
                assert 0 < len(features)

                if len(features) == 2:
                    # aggregate gender lui
                    filter_re = '^.*DAT\(3;SG;MASC\);.*|^.*DAT\(3;SG;FEM\);.*$'
                    if 'lui' in form and not 'à lui' and re.match(filter_re, features[0]) and re.match(filter_re, features[1]):
                        pattern = 'DAT\(3;SG(;MASC)\);|DAT\(3;SG(;FEM)\);'
                        new = re.sub(pattern, 'DAT(3;SG);', features[0])
                        assert new == re.sub(pattern, 'DAT(3;SG);', features[1])

                    filter_re_ACC = '^.*ACC\(3;SG;MASC\);.*|^.*ACC\(3;SG;FEM\);.*$'
                    if "l'" in form and re.match(filter_re_ACC, features[0]) and re.match(filter_re_ACC, features[1]):
                        pattern = 'ACC\(3;SG(;MASC)\);|ACC\(3;SG(;FEM)\);'
                        new = re.sub(pattern, 'ACC(3;SG);', features[0])
                        assert new == re.sub(pattern, 'ACC(3;SG);', features[1])

                        features = [new]

                for feature in features:
                    n_line += 1
                    write.write(f'{lemma}\t{form}\t{feature}\n')

    if add_readme:
        #
        log = "# French Mighty Morph based on the lefff and unimorph \n\n"
        log += f"{len(mighty_morph)} lemmas \n"
        log += f"{np.mean(n_form_per_lemma):0.1f} form/lemmas in avg {np.min(n_form_per_lemma)}/{np.max(n_form_per_lemma)} min/max form per lemmas \n"
        log += f"{n_line} observations in total \n"
        with open(output_dir.parent/"readme_fr_final.txt", 'w') as readme:
            readme.write(log)
            print(output_dir.parent/"readme_fr_final.txt", " readme written")
        print(log)


if __name__ == "__main__":

    path = Path('/Users/bemuller/Documents/Work/INRIA/dev/mighty_morph_tagging_tool')
    aggregate_gender_mark(path/'mighty_morph'/'fr-w_leff.txt', path/'mighty_morph'/'fr-w_leff.txt', add_readme=True)
