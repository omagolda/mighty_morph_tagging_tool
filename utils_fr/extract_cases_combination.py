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


def match_accusatif(leff_data, mandatory=False):
    if not mandatory:
        return re.match("<.*Obj:\(?[^,>]*\|?cla\|?[^,>]*\)?.*>", leff_data) is not None
    else:
        return re.match("<.*Obj:[^,>(]*\|?cla\|?[^,>\)]*?.*>", leff_data) is not None

def match_accusatif_cases(leff_data):
    return_ls = []
    if re.match("<.*Obj:\([^,>]*\|?cla\|?[^,>]*\).*>", leff_data) is not None:
        # not mandatory
        return_ls.extend(["a", "0"])
    # if Obj conditional but no cla inside we add 0
    elif re.match("<.*Obj:\([^,>]*.*\|?\|?[^,>]*\).*>", leff_data) is not None:
        return_ls.extend(["0"])
    elif re.match("<.*Obj:[^,>(]*\|?cla\|?[^,>\)]*?.*>", leff_data) is not None:
        return_ls.extend(["a"])
    return return_ls


    #else:
    #    return re.match("<.*Obj:[^,>(]*\|?cla\|?[^,>\)]*?.*>", leff_data) is not None

def match_datif(leff_data, mandatory=False):
    if not mandatory:
        return re.match("<.*Objà:\(?[^,>]*\|?cld\|?[^,>]*\)?.*>", leff_data) is not None
    else:
        return re.match("<.*Objà:[^,>(]*\|?cld\|?[^,>\)]*.*>", leff_data) is not None


def match_datif_cases(leff_data):
    return_ls = []
    if re.match("<.*Objà:\([^,>]*\|?cld\|?[^,>]*\).*>", leff_data) is not None:
        return_ls.extend(["d", "0"])
    elif re.match("<.*Objà:\([^,>]*\|?.*\|?[^,>]*\).*>", leff_data) is not None:
        return_ls.extend(["0"])
    elif re.match("<.*Objà:[^,>(]*\|?cld\|?[^,>\)]*.*>", leff_data) is not None:
        return_ls.extend(["d"])
    return return_ls



def match_genitif(leff_data):
    return re.match("<.*Objde:\(?[^,>]*\|?en\|?[^,>]*\)?.*>", leff_data) is not None or re.match("<.*Dloc:\(?[^,>]*\|?en\|?[^,>]*\)?.*>", leff_data) is not None


def match_genitif_cases(leff_data):
    if re.match("<.*Objde:\([^,>]*\|?en\|?[^,>]*\).*>", leff_data) is not None or re.match("<.*Dloc:\([^,>]*\|?en\|?[^,>]*\).*>", leff_data) is not None:
        return ["g", "0"]
    elif re.match("<.*Objde:[^,>\(]*\|?en\|?[^,>)]*.*>", leff_data) is not None or re.match("<.*Dloc:[^,>\(]*\|?en\|?[^,>)]*.*>", leff_data) is not None:
        return ["g"]
    return []


def match_locatif(leff_data, mandatory=False):
    if not mandatory:
        return re.match("<.*Loc:\(?[^,>]*\|?y\|?[^,>]*\)?.*>", leff_data) is not None or re.match("<.*Objà:\([^,>]*\|?y\|?[^,>]*\).*>", leff_data) is not None
    else:
        return re.match("<.*Loc:[^,>\(]*\|?y\|?[^,>)]*.*>", leff_data) is not None or re.match("<.*Objà:[^,>\(]*\|?y\|?[^,>)]*.*>", leff_data) is not None


def match_locatif_objà(leff_data):
    return re.match("<.*Objà:[^,>\(]*\|?y\|?[^,>)]*.*>", leff_data) is not None



def match_locatif_cases(leff_data):
    if re.match("<.*Loc:\([^,>]*\|?y\|?[^,>]*\).*>", leff_data) is not None or re.match("<.*Objà:\([^,>]*\|?y\|?[^,>]*\).*>", leff_data) is not None:
        return ["l", "0"]
    elif re.match("<.*Loc:[^,>\(]*\|?y\|?[^,>)]*.*>", leff_data) is not None or re.match("<.*Objà:[^,>\(]*\|?y\|?[^,>)]*.*>", leff_data) is not None:
        return ["l"]
    return []


def match_intransitif(leff_data):
    return "Obj" not in leff_data and "Suj" in leff_data


def match_reflexif(leff_data_lemma_field):
    # after deduplicating the lefff and "(se)" changed to "se" this means that we do not want to assign to reflexif (se)Lemma lines so only matching se and s'
    return "se Lemma" in leff_data_lemma_field or "s'Lemma" in leff_data_lemma_field

def match_on(leff_data):
    # after deduplicating the lefff and "(se)" changed to "se" this means that we do not want to assign to reflexif (se)Lemma lines so only matching se and s'
    return re.match("<.*Obl:\(?[^,>]*\|?:sur-sn\|?[^,>]*\)?.*>", leff_data) is not None

def match_sub(leff_data):
    # after deduplicating the lefff and "(se)" changed to "se" this means that we do not want to assign to reflexif (se)Lemma lines so only matching se and s'
    return re.match("<.*Obl:\(?[^,>]*\|?:sous-sn\|?[^,>]*\)?.*>", leff_data) is not None

def match_contr(leff_data):
    # after deduplicating the lefff and "(se)" changed to "se" this means that we do not want to assign to reflexif (se)Lemma lines so only matching se and s'
    return re.match("<.*Obl:\(?[^,>]*\|?:contre-sn\|?[^,>]*\)?.*>", leff_data) is not None

def match_pour(leff_data):
    # after deduplicating the lefff and "(se)" changed to "se" this means that we do not want to assign to reflexif (se)Lemma lines so only matching se and s'
    return re.match("<.*Obl:\(?[^,>]*\|?:pour-sn\|?[^,>]*\)?.*>", leff_data) is not None

def match_par(leff_data):
    # after deduplicating the lefff and "(se)" changed to "se" this means that we do not want to assign to reflexif (se)Lemma lines so only matching se and s'
    return re.match("<.*Obl:\(?[^,>]*\|?:par-sn\|?[^,>]*\)?.*>", leff_data) is not None

def match_with(leff_data):
    # after deduplicating the lefff and "(se)" changed to "se" this means that we do not want to assign to reflexif (se)Lemma lines so only matching se and s'
    return re.match("<.*Obl:\(?[^,>]*\|?:with-sn\|?[^,>]*\)?.*>", leff_data) is not None



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

            #if not match_reflexif(feature_lex_line[1]):
            if True:
                CODE = f"{PREFIX}"

                # intransitif feature
                if match_intransitif(feature_lex_line[3]):
                    CODE += "0"
                    if CODE not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][CODE] = []
                    lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))

                    continue

                PREF = f"{PREFIX}"
                comb_to_make = []
                for match_code, match_func in zip([#  "0",
                                                   "a",
                                                   "d", "l", "g"],
                                                  [#  match_intransitif,
                                                   match_accusatif_cases, match_datif_cases,
                                                   match_locatif_cases, match_genitif_cases]):
                    #breakpoint()
                    comb_to_make.append(match_func(feature_lex_line[3]))
                # for reflexive only mandatory or not used
                comb_to_make.append(["r"] if match_reflexif(feature_lex_line[1]) else ["0"])
                if match_reflexif(feature_lex_line[1]):
                    breakpoint()



                try:
                    assert len([e for ls in comb_to_make for e in ls]), comb_to_make
                except:
                    # MISSING FACULTATIF ARGUMENT that should have generatif ["0"] but not that many Objde:() and othre
                    pass # breakpoint()

                count_non_null = 0
                count_mandatory_field = 0
                #comb_to_make = [['a'], [], [], ['g', '0']]
                objà_has_two_value = False
                for ls in comb_to_make:
                    if len(ls) > 0:
                        count_non_null += 1
                    if len(ls) > 0 and "0" not in ls:
                        count_mandatory_field += 1
                try:
                    assert 0 <= count_mandatory_field <= 2, f'{count_mandatory_field} {comb_to_make} {lex_line}'
                except Exception as e:
                    if not count_mandatory_field == 3:
                        raise(Exception(e))
                    if comb_to_make[1][0] == "d" and comb_to_make[2][0] == "l" and match_locatif_objà(feature_lex_line[3]):
                        objà_has_two_value = True
                        print("objà_has_two_value ")

                    else:
                        raise(Exception(e))

                # comb_to_make = [['a', '0'], ["d", "0"], ["g"], []]
                mandatory_ls = []
                for ipos, case in enumerate(comb_to_make):
                    if len(case) == 1 and case[0] != '0':
                        # mandatory
                        mandatory_ls.append(case[0])
                if objà_has_two_value:
                    print(f"\n\nOriginal combinations {comb_to_make}, {objà_has_two_value} objà_has_two_value")

                comb_to_make = [ls if len(ls) != 0 else ["0"] for ls in comb_to_make]
                #print("Appending 0 for no field", comb_to_make)
                #print("MANDATORY FIELD", mandatory_ls)
                ls_code = []

                for acc in comb_to_make[0]:
                    for dat in comb_to_make[1]:
                        for loc in comb_to_make[2]:
                            for gen in comb_to_make[3]:
                                for ref in comb_to_make[4]:
                                    possible_val = [acc, dat, loc, gen, ref]
                                    possible_val_no_0 = [val for val in possible_val if val != '0']

                                    # SPLITTING EVERYTHING in 3

                                    # 1- taking all pairs of non-null arguments, we make sure that all the mandatory ones are always in the list added that dl is not added if they come from Objà
                                    # adding all pairs (including mandatory ones)

                                    for i1, val_1 in enumerate(possible_val_no_0):
                                        for val_2 in possible_val_no_0[i1+1:]:
                                            if len(mandatory_ls) and not ((val_1 in mandatory_ls or val_2 in mandatory_ls)) or val_1+val_2 in ls_code:
                                                # we skip it because we don't have the mandatory ones
                                                continue
                                            if objà_has_two_value and val_1 == "d" and val_2 == "l":
                                                print("--------------------", val_1, val_2)

                                                continue
                                            ls_code.append(f'{val_1}{val_2}')

                                    #2- IF THERE is only 1 mandatory one: we make sure it is added to the list alone
                                    # mandatory ones adding: single one add
                                    if len(mandatory_ls) == 1:
                                        for i1, val_1 in enumerate(mandatory_ls):
                                            if val_1 in ls_code:
                                                continue
                                            ls_code.append(val_1)

                                    # 3- IF NO ARG is MANDATORY we can now add all the single ones by themselves
                                    # non mandatory ones single
                                    if len(mandatory_ls) == 0:
                                        for i1, val_1 in enumerate(possible_val_no_0):
                                            if val_1 in ls_code:
                                                continue
                                            ls_code.append(val_1)


                                # adding pairs
                                #for i1, val_1 in enumerate(mandatory_ls):
                                #    for val_2 in mandatory_ls[i1+1:]:
                                ##        val = val_1+val_2 if val_1 != val_2 else val_1
                                #        if val in ls_code or (objà_has_two_value and val_1 == "d" and val_2 == "l"):
                                            # we skip it because we don't have the mandatory ones
                                #            continue
                                #        ls_code.append(val)

                                # single ones

                if len(mandatory_ls) == 0:
                    ls_code.append("0")

                for code in ls_code:
                    if code in ["dl", "lg"]:
                        assert not objà_has_two_value, "should not have happened"
                        # for lg; not sure what
                        if not objà_has_two_value:
                            print("skipping this sort of dl for now (could intagrate it later)")
                            continue

                    code = PREF+code

                    if code not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][code] = []
                    # always être for reflexive verbs
                    lex_alexina_2[lex_line[0]][code].append(get_aux(feature_lex=feature_lex_line[4]))
                    #TODO NEED ALSO 1 val case
                    #TODO: need 0 val case


                print("Final:", ls_code)
                ##if match_reflexif(feature_lex_line[1]):
                #    print(comb_to_make, lex_line)
                #    breakpoint()

                #breakpoint()





                #CODE += f"{match_code}"



                    
                    

            elif False:
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
                    try:
                        assert not (match_accusatif(leff_data=feature_lex_line[3], mandatory=True) and match_datif(leff_data=feature_lex_line[3], mandatory=True)), f"should not have se lemma with both {feature_lex_line} {lex_line}"
                    except Exception as e:
                        print(e)
                        #raise(e)
                    CODE = f"{PREFIX}dr"
                    lex_alexina[lex_line[0]]["cases"].append(CODE)
                    if CODE not in lex_alexina_2[lex_line[0]]:
                        lex_alexina_2[lex_line[0]][CODE] = []
                    # always être for reflexive verbs
                    lex_alexina_2[lex_line[0]][CODE].append(get_aux(feature_lex=feature_lex_line[4]))
                if match_accusatif(leff_data=feature_lex_line[3]):
                    try:
                        assert not (match_datif(leff_data=feature_lex_line[3], mandatory=True) and match_accusatif(leff_data=feature_lex_line[3], mandatory=True)), f"should not have se lemma with both {feature_lex_line} {lex_line}"
                    except Exception as e:
                        print(e)
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


