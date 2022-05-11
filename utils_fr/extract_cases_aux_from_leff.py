"""

- Download Leff from almanach.inria.fr
- unzip in a lefff-3.4 folder
- Run:

python utils_fr/extract_cases_aux_from_leff.py \
    --leff_directory ./lefff-3.4/v_new-fixed_duplicated.ilex \
    --output_json_directory ./leff-extract/cases.json

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
    # after deduplicating the lefff and "(se)" changed to "se" this means that we do not want to assign to reflexif (se)Lemma lines so only matching se and s'
    return "se Lemma" in leff_data_lemma_field or "s'Lemma" in leff_data_lemma_field


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
                # %actif_impersonnel
                skipping += 1
                skipping_not_actif += 1
                continue

            if "%actif_impersonnel" in feature_lex_line[5]:
                PREFIX = "I"
            else:
                PREFIX = "P"

            if "@être" in feature_lex_line[4]:
                lex_alexina[lex_line[0]]["aux"].append(f"{PREFIX}e")
            else:
                lex_alexina[lex_line[0]]["aux"].append(f"{PREFIX}a")

            if not match_reflexif(feature_lex_line[1]):

                if match_accusatif(feature_lex_line[3]):
                    # cla --> accusatif
                    CODE = f"{PREFIX}a"
                    lex_alexina[lex_line[0]]["cases"].append(CODE)
                    if CODE not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][CODE] = []
                    lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))

                #if re.match("<.*Objà:\(?[^,>]*\|?cld\|?[^,>]*\)?.*>", feature_lex_line[3]) is not None:
                if match_datif(feature_lex_line[3]):
                    # cld --> datif
                    CODE = f"{PREFIX}d"
                    lex_alexina[lex_line[0]]["cases"].append(CODE)
                    if CODE not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][CODE] = []
                    lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))

                #if re.match("<.*Objde:\(?[^,>]*\|?en\|?[^,>]*\)?.*>", feature_lex_line[3]) is not None or re.match("<.*Dloc:\(?[^,>]*\|?en\|?[^,>]*\)?.*>", feature_lex_line[3]) is not None:
                if match_genitif(feature_lex_line[3]):
                    # en --> genitif
                    CODE = f"{PREFIX}g"
                    lex_alexina[lex_line[0]]["cases"].append(CODE)
                    if CODE not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][CODE] = []
                    lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))

                #if re.match("<.*Loc:\(?[^,>]*\|?y\|?[^,>]*\)?.*>", feature_lex_line[3]) is not None or re.match("<.*Objà:\(?[^,>]*\|?y\|?[^,>]*\)?.*>", feature_lex_line[3]) is not None:
                if match_locatif(feature_lex_line[3]):
                    # y --> locatif
                    CODE = f"{PREFIX}l"
                    lex_alexina[lex_line[0]]["cases"].append(CODE)
                    if CODE not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][CODE] = []
                    print(f"{lex_line[0]} locatif with aux {get_aux(feature_lex=feature_lex_line[4])}")
                    lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))

                #if "Obj" not in feature_lex_line[3] and "Suj" in feature_lex_line[3]:
                if match_intransitif(feature_lex_line[3]):
                    # intransitif
                    CODE = f"{PREFIX}0"
                    lex_alexina[lex_line[0]]["cases"].append(CODE)
                    if CODE not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][CODE] = []
                    lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))
                # if parenthesis we just ignore the feature --> and rely on the other features
                #if "se Lemma" in feature_lex_line[1] or "s'Lemma" in feature_lex_line[1] or "(se) Lemma" in feature_lex_line[1] or "(s')Lemma" in feature_lex_line[1]:


                #COMBINATIONS:
                # ad
                if match_datif(leff_data=feature_lex_line[3]) and match_accusatif(leff_data=feature_lex_line[3]):
                    CODE = f"{PREFIX}ad"
                    lex_alexina[lex_line[0]]["cases"].append(CODE)
                    if CODE not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][CODE] = []
                    # always être for reflexive verbs
                    lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))

                if match_accusatif(leff_data=feature_lex_line[3]) and match_genitif(leff_data=feature_lex_line[3]):
                    CODE = f"{PREFIX}ag"
                    lex_alexina[lex_line[0]]["cases"].append(CODE)
                    if CODE not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][CODE] = []
                    # always être for reflexive verbs
                    lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))

                if match_accusatif(leff_data=feature_lex_line[3]) and match_locatif(leff_data=feature_lex_line[3]):
                    CODE = f"{PREFIX}al"
                    lex_alexina[lex_line[0]]["cases"].append(CODE)
                    if CODE not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][CODE] = []
                    # always être for reflexive verbs
                    lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))

                if match_datif(leff_data=feature_lex_line[3]) and match_locatif(leff_data=feature_lex_line[3]):
                    CODE = f"{PREFIX}dg"
                    lex_alexina[lex_line[0]]["cases"].append(CODE)
                    if CODE not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][CODE] = []
                    # always être for reflexive verbs
                    lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))

            else:
                # reflexif case
                if match_genitif(leff_data=feature_lex_line[3]):
                    CODE = f"{PREFIX}gr"
                    lex_alexina[lex_line[0]]["cases"].append(CODE)
                    if CODE not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][CODE] = []
                    # always être for reflexive verbs
                    lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))

                if match_locatif(leff_data=feature_lex_line[3]):
                    CODE = f"{PREFIX}lr"
                    lex_alexina[lex_line[0]]["cases"].append(CODE)
                    if CODE not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][CODE] = []
                    # always être for reflexive verbs
                    lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))
                if match_datif(leff_data=feature_lex_line[3]):
                    CODE = f"{PREFIX}dr"
                    lex_alexina[lex_line[0]]["cases"].append(CODE)
                    if CODE not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][CODE] = []
                    # always être for reflexive verbs
                    lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))
                if match_accusatif(leff_data=feature_lex_line[3]):
                    CODE = f"{PREFIX}ar"
                    lex_alexina[lex_line[0]]["cases"].append(CODE)
                    if CODE not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][CODE] = []
                    # always être for reflexive verbs
                    lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))

                if not (match_datif(leff_data=feature_lex_line[3]) or match_accusatif(leff_data=feature_lex_line[3]) or match_genitif(leff_data=feature_lex_line[3]) or match_locatif(leff_data=feature_lex_line[3]) ):
                    CODE = f"{PREFIX}r"
                    lex_alexina[lex_line[0]]["cases"].append(CODE)
                    if "r" not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][CODE] = []
                    # always être for reflexive verbs
                    lex_alexina_2[lex_line[0]][CODE].append("e")

        print(f"{len(lex_alexina)} verbs found in alexina skipped {skipping} lines, {skipping_no_bracket} no brackets, "
              f"{skipping_not_actif} not actif")

        check_no_cases_found(lex_alexina)

        if output_dir is not None:
            with open(output_dir, "w", encoding="utf-8") as writing:
                #json.dump(lex_alexina, writing)
                json.dump(lex_alexina_2, writing, indent=4, sort_keys=True)
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


