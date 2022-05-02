"""
python utils_fr/preprocess_leff.py --leff_directory ./lefff-3.4/v_new-fixed.ilex --leff_output v_new-fixed_duplicated.ilex
"""
import argparse
import json
import re
from pathlib import Path

def duplicate(lex_dir, output_lex_dir):

    with open(str(lex_dir), encoding="utf-8") as lex:
        with open(str(output_lex_dir), "w", encoding="utf-8") as output_lex:
            lex_alexina = {}
            lex_alexina_2 = {}
            added, skipping, skipping_not_actif, skipping_no_bracket = 0, 0, 0, 0
            for lex_line in lex:
                encoding = "utf-8"
                output_lex.write(lex_line)
                _lex_line = lex_line.strip().split("\t")
                if len(_lex_line) <= 1:
                    continue

                _lex_line = lex_line.strip().split("\t")
                feature_lex_line = _lex_line[2].split(";")

                to_fix = 0
                # check %actif in feature_lex_line[5]
                # être possible in feature_lex_line[4]
                #feature_lex_line[4]
                if "@être_possible" in feature_lex_line[4]:
                    feature_lex_line[4] = feature_lex_line[4].replace("@être_possible", "")
                    feature_lex_line[4] = feature_lex_line[4].replace(",,", ",")
                    # duplicate
                    print("être possible fixed")
                    print(lex_line)
                    _lex_line[2] = ";".join(feature_lex_line)
                    lex_line = "\t".join(_lex_line)+"\n"
                    print(lex_line)

                    to_fix = 1

                    #breakpoint()
                if "(se) Lemma" in feature_lex_line[1] or "(s')Lemma" in feature_lex_line[1]:
                    # replacing '(se)' by 'se' --> this means that (se) lemma should be ignored
                    print("se lemma fixed")
                    print(lex_line)
                    feature_lex_line[1] = feature_lex_line[1].replace(")", "")
                    feature_lex_line[1] = feature_lex_line[1].replace("(", "")
                    _lex_line[2] = ";".join(feature_lex_line)
                    lex_line = "\t".join(_lex_line) + "\n"
                    # duplicate without lemma
                    print(lex_line)
                    to_fix = 1
                    #breakpoint()
                if to_fix:
                    added += 1
                    output_lex.write(lex_line)
    print("added", added)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Extract features from the leff')
    parser.add_argument('--leff_directory', type=str, help='', required=True)
    parser.add_argument('--leff_output', type=str, help='', required=True)

    args = parser.parse_args()
    duplicate(args.leff_directory, args.leff_output)
