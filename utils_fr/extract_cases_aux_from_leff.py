"""

- Download Leff from almanach.inria.fr
- unzip in a lefff-3.4 folder
- Run:

python utils_fr/extract_cases_aux_from_leff.py
    --leff_directory ./lefff-3.4/v_new.ilex
    --output_json_directory leff_features.json

"""

import argparse
import json
import re
from pathlib import Path



def check_no_cases_found(lex_alexina):
    count_empty_cases = 0
    count__ = 0
    for v in lex_alexina:
        if len(lex_alexina[v]["cases"]) == 0:
            count_empty_cases += 1
    print(f"{count_empty_cases} / {len(lex_alexina)} verbs have no cases")


    # print(f"{count__} / {len(lex_alexina)} verbs have ___ ")


def get_aux(feature_lex):
    if "@être" in feature_lex:
        return "e"
    else:
        return "a"


def match_accusatif(leff_data):
    return re.match("<.*Obj:\(?[^,>]*\|?cla\|?[^,>]*\)?.*>", leff_data) is not None


def match_datif(leff_data):
    return re.match("<.*Objà:\(?[^,>]*\|?cld\|?[^,>]*\)?.*>", leff_data) is not None


def match_genitif(leff_data):
    return re.match("<.*Objde:\(?[^,>]*\|?en\|?[^,>]*\)?.*>", leff_data) is not None or re.match("<.*Dloc:\(?[^,>]*\|?en\|?[^,>]*\)?.*>", leff_data) is not None


def match_locatif(leff_data):
    return re.match("<.*Loc:\(?[^,>]*\|?y\|?[^,>]*\)?.*>", leff_data) is not None or re.match("<.*Objà:\(?[^,>]*\|?y\|?[^,>]*\)?.*>", leff_data) is not None


def match_intransitif(leff_data):
    return "Obj" not in leff_data and "Suj" in leff_data


def match_reflexif(leff_data_lemma_field):
    return "se Lemma" in leff_data_lemma_field or "s'Lemma" in leff_data_lemma_field or "(se) Lemma" in leff_data_lemma_field or "(s')Lemma" in leff_data_lemma_field


def extract_features_from_leff(lex_dir: Path, output_dir:str =None):
    with open(str(lex_dir), encoding="utf-8") as lex:
        lex_alexina = {}
        lex_alexina_2 = {}
        skipping, skipping_not_actif, skipping_no_bracket = 0, 0, 0
        for line in lex:
            # breakpoint()
            lex_line = line.strip().split("\t")
            if len(lex_line) <= 1:
                continue
            feature_lex_line = lex_line[2].split(";")
            try:
                assert feature_lex_line[3].startswith("<") and feature_lex_line[3].endswith(">"), f"{lex_line[2]} and {feature_lex_line[3]}"
            except:
                print("Skipping cause did not found <..>", lex_line)
                skipping += 1
                skipping_no_bracket += 1
                continue

            # verb
            lex_line[0] = lex_line[0].split("___")[0]

            if lex_line[0] not in lex_alexina:
                lex_alexina_2[lex_line[0]] = {}
                lex_alexina[lex_line[0]] = {}
                lex_alexina[lex_line[0]]["cases"] = []
                lex_alexina[lex_line[0]]["aux"] = []

            if "%actif" not in feature_lex_line[5]:
                print(f"Skipping {lex_line[0]} because not %actif ")
                skipping += 1
                skipping_not_actif += 1
                continue

            if "@être" in feature_lex_line[4]:
                lex_alexina[lex_line[0]]["aux"].append("e")
            else:
                lex_alexina[lex_line[0]]["aux"].append("a")
            if "HAND_CHECKING" == lex_line[0]:
                breakpoint()

            #if re.match("<.*Obj:\(?[^,>]*\|?cla\|?[^,>]*\)?.*>", feature_lex_line[3]) is not None:
            if match_accusatif(feature_lex_line[3]):
                # cla --> accusatif
                lex_alexina[lex_line[0]]["cases"].append("a")
                if "a" not in lex_alexina_2[lex_line[0]]:
                    lex_alexina_2[lex_line[0]]["a"] = []
                lex_alexina_2[lex_line[0]]["a"].append(get_aux(feature_lex=feature_lex_line[4]))

            #if re.match("<.*Objà:\(?[^,>]*\|?cld\|?[^,>]*\)?.*>", feature_lex_line[3]) is not None:
            if match_datif(feature_lex_line[3]):
                # cld --> datif
                lex_alexina[lex_line[0]]["cases"].append("d")
                if "d" not in lex_alexina_2[lex_line[0]]:
                    lex_alexina_2[lex_line[0]]["d"] = []
                lex_alexina_2[lex_line[0]]["d"].append(get_aux(feature_lex=feature_lex_line[4]))

            #if re.match("<.*Objde:\(?[^,>]*\|?en\|?[^,>]*\)?.*>", feature_lex_line[3]) is not None or re.match("<.*Dloc:\(?[^,>]*\|?en\|?[^,>]*\)?.*>", feature_lex_line[3]) is not None:
            if match_genitif(feature_lex_line[3]):
                # en --> genitif
                lex_alexina[lex_line[0]]["cases"].append("g")
                if "g" not in lex_alexina_2[lex_line[0]]:
                    lex_alexina_2[lex_line[0]]["g"] = []
                lex_alexina_2[lex_line[0]]["g"].append(get_aux(feature_lex=feature_lex_line[4]))

            #if re.match("<.*Loc:\(?[^,>]*\|?y\|?[^,>]*\)?.*>", feature_lex_line[3]) is not None or re.match("<.*Objà:\(?[^,>]*\|?y\|?[^,>]*\)?.*>", feature_lex_line[3]) is not None:
            if match_locatif(feature_lex_line[3]):
                # y --> locatif
                lex_alexina[lex_line[0]]["cases"].append("l")
                if "l" not in lex_alexina_2[lex_line[0]]:
                    lex_alexina_2[lex_line[0]]["l"] = []
                print(f"{lex_line[0]} locatif with aux {get_aux(feature_lex=feature_lex_line[4])}")
                lex_alexina_2[lex_line[0]]["l"].append(get_aux(feature_lex=feature_lex_line[4]))

            #if "Obj" not in feature_lex_line[3] and "Suj" in feature_lex_line[3]:
            if match_intransitif(feature_lex_line[3]):
                # intransitif
                lex_alexina[lex_line[0]]["cases"].append("0")
                if "0" not in lex_alexina_2[lex_line[0]]:
                    lex_alexina_2[lex_line[0]]["0"] = []
                lex_alexina_2[lex_line[0]]["0"].append(get_aux(feature_lex=feature_lex_line[4]))
            # if parenthesis we just ignore the feature --> and rely on the other features
            #if "se Lemma" in feature_lex_line[1] or "s'Lemma" in feature_lex_line[1] or "(se) Lemma" in feature_lex_line[1] or "(s')Lemma" in feature_lex_line[1]:
            if match_reflexif(feature_lex_line[1]):
                # intransitif
                lex_alexina[lex_line[0]]["cases"].append("r")
                if "r" not in lex_alexina_2[lex_line[0]]:
                    lex_alexina_2[lex_line[0]]["r"] = []
                # always être for reflexive verbs
                lex_alexina_2[lex_line[0]]["r"].append("e")


            #COMBINATIONS:
            # ad
            if match_datif(leff_data=feature_lex_line[3]) and match_accusatif(leff_data=feature_lex_line[3]):
                CODE = "ad"
                lex_alexina[lex_line[0]]["cases"].append(CODE)
                if CODE not in lex_alexina_2[lex_line[0]]:
                    lex_alexina_2[lex_line[0]][CODE] = []
                # always être for reflexive verbs
                lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))

            if match_accusatif(leff_data=feature_lex_line[3]) and match_genitif(leff_data=feature_lex_line[3]):
                CODE = "ag"
                lex_alexina[lex_line[0]]["cases"].append(CODE)
                if CODE not in lex_alexina_2[lex_line[0]]:
                    lex_alexina_2[lex_line[0]][CODE] = []
                # always être for reflexive verbs
                lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))

            if match_accusatif(leff_data=feature_lex_line[3]) and match_locatif(leff_data=feature_lex_line[3]):
                CODE = "al"
                lex_alexina[lex_line[0]]["cases"].append(CODE)
                if CODE not in lex_alexina_2[lex_line[0]]:
                    lex_alexina_2[lex_line[0]][CODE] = []
                # always être for reflexive verbs
                lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))

            if match_datif(leff_data=feature_lex_line[3]) and match_locatif(leff_data=feature_lex_line[3]):
                CODE = "dg"
                lex_alexina[lex_line[0]]["cases"].append(CODE)
                if CODE not in lex_alexina_2[lex_line[0]]:
                    lex_alexina_2[lex_line[0]][CODE] = []
                # always être for reflexive verbs
                lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))

            if match_reflexif(feature_lex_line[1]) and match_genitif(leff_data=feature_lex_line[3]):
                CODE = "rg"
                lex_alexina[lex_line[0]]["cases"].append(CODE)
                if CODE not in lex_alexina_2[lex_line[0]]:
                    lex_alexina_2[lex_line[0]][CODE] = []
                # always être for reflexive verbs
                lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))

            if match_reflexif(feature_lex_line[1]) and match_locatif(leff_data=feature_lex_line[3]):
                CODE = "rl"
                lex_alexina[lex_line[0]]["cases"].append(CODE)
                if CODE not in lex_alexina_2[lex_line[0]]:
                    lex_alexina_2[lex_line[0]][CODE] = []
                # always être for reflexive verbs
                lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))


        print(f"{len(lex_alexina)} verbs found in alexina skipped {skipping} lines, {skipping_no_bracket} no brackets, "
              f"{skipping_not_actif} not actif")

        check_no_cases_found(lex_alexina)

        if output_dir is not None:
            with open(output_dir, "w", encoding="utf-8") as writing:
                #json.dump(lex_alexina, writing)
                json.dump(lex_alexina_2, writing)
                print(f"{output_dir} written")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Extract features from the leff')
    parser.add_argument('--leff_directory', type=str, help='', required=True)
    parser.add_argument('--output_json_directory', type=str, help='', required=True)

    args = parser.parse_args()

    extract_features_from_leff(args.leff_directory, args.output_json_directory)


    # 1- WRITE BIG JSON with auxilliary
    # READ from fr_data.py for Accusatif and Datif --> test
    # 2- get the participe passé conjugauson for each verb --> can add it to this dict
    # replace in compounds tense for être and in some cases for avoir
    # 3-
    # Other: neutral cases, reflexivity
    #   breakpoint()


    # notes: # se seréfl : plusieurs cas à gérer  --> soit datif soit accusatif
    #             # verbe impersonel
    #             # MAKE SURE that %actif is at the end
    #             # voler : deux entrée --> je vol
    #             # lex_line[2] = ""


