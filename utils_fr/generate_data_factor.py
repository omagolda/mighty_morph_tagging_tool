import os
import json
import re

from tqdm import tqdm

language = 'fr'


person_number = {'1;SG', '1;PL', '2;SG', '2;PL', '3;SG;MASC', '3;SG;FEM',  '3;PL;MASC', '3;PL;FEM'}#,  '3;PL;NEUT','3;SG;NEUT',}


nom_prons = {'1;SG': 'je',#'1;SG;MASC': 'je', '1;SG;FEM': 'je',
             '1;PL': 'nous', '2;SG': 'tu', '2;PL': 'vous', '3;SG;MASC': 'il', '3;SG;FEM': 'elle',  '3;PL;MASC':'ils', '3;PL;FEM': 'elles'}#,  '3;PL;NEUT':'ce', '3;SG;NEUT':'cela'}

acc_prons = {'1;SG': 'me', '1;PL': 'nous', '2;SG': 'te', '2;PL': 'vous', '3;SG;MASC': 'le', '3;SG;FEM': 'la',  "3;PL": "les"}#, "3;PL": "les"} # NB: "3;PL;MASC": "les" and "3;PL;FEM" could be normalized to "3;PL" (but then must handle acc_prons[pn] errors)

dat_prons = {'1;SG': 'me', '1;PL': 'nous', '2;SG': 'te', '2;PL': 'vous', '3;SG;MASC': 'lui', '3;SG;FEM': 'lui', '3;PL': 'leur'}# '3;PL;MASC':'leur', '3;PL;FEM':'leur'}

reflex_prons = {'1;SG': 'me', '1;PL': 'nous', '2;SG': 'te', '2;PL': 'vous', '3;SG': 'se', '3;PL': 'se'}# '3;PL;MASC':'leur', '3;PL;FEM':'leur'}

loc_pron = {'3;SG;NEUT': 'y'}  # --> '3;PL;MASC':'leur', '3;PL;FEM':'leur'}

gen_pron = {'3;SG;NEUT': 'en'}

prepos_prons = {'a': acc_prons, 'd': dat_prons, 'l': loc_pron, "g": gen_pron, "r": reflex_prons, "0": {"None": ""}}

# OTHER ONES: https://pollylingu.al/fr/en/cases : DISJUNCTIF? GENITIF?


# tonique https://parlez-vous-french.com/les-pronoms-toniques-en-francais/
tonique_pronouns = {'1;SG': 'moi', '1;PL':'nous', '2;SG': 'toi', '2;PL': 'vous', '3;SG;MASC': 'lui',
                    '3;SG;FEM': 'elle', '3;PL': 'eux'} #'3;PL;MASC': 'eux', '3;PL;FEM':'elles'}


prepos = {'a': '', 'd': 'à', 'c': 'avec', 'g': 'of', 'b': 'from', 'f': 'for', 'l': 'on', 's': 'at', 't': 'about', 'i': 'in'}


moods = ['IND', 'IMP', "COND"]
tenses = {'PST', 'PRS', 'FUT'}
aspects = {'PFV', 'IPFV'}
# NEG, Q, PASS
have = {'pst': 'had', 'prs': 'have', 'prs3sg': 'has', 'fut': 'will have'}

be = {'v3': 'been', 'fut': 'will be',
      'PST,1,SG': 'was', 'PST,1,PL': 'were', 'PST,2': 'were', 'PST,3,SG': 'was', 'PST,3,PL': 'were',
      'PRS,1,SG': 'am', 'PRS,1,PL': 'are', 'PRS,2': 'are', 'PRS,3,SG': 'is', 'PRS,3,PL': 'are'}

dicts = [nom_prons, acc_prons, reflex_prons, prepos, have, be]
non_lemma_words = set().union(*[set(dicto.values()) for dicto in dicts])
non_lemma_words |= {'will', "don't", 'do', 'be', 'would', 'not', 'did', "didn't", 'does', "doesn't", '?', "I'm", "you're",
                    "we're", "they're", "he's", "she's", "it's", "haven't", "hasn't", "hadn't", "wouldn't", "won't", "wasn't", "weren't",
                    "I've", "you've", "we've", "they've", "I'd", "you'd", "we'd", "they'd", "he'd","she'd", "I'll", "you'll", "we'll",
                    "they'll", "he'll", "she'll", "it'll"}

cases = {'a': 'ACC', 'd': 'DAT', 'l': 'LOC', 'g': 'GEN', #"r": "RFLX"
         }

rev_cases = {v: k for k, v in cases.items()}


auxiliary_dict = {"a": {
                        "IND;PRS": {'1;SG': "ai", '2;SG': 'as', '3;SG': 'a', '1;PL': 'avons',  '2;PL': 'avez',  '3;PL': "ont"},
                        "IND;FUT": {'1;SG': 'aurai','2;SG': 'auras', '3;SG': 'aura', '1;PL': 'aurons',  '2;PL': 'aurez', '3;PL': 'auront'},
                        "IND;PST;IPFV": {'1;SG': 'avais','2;SG': 'avais', '3;SG': 'avait', '1;PL': 'avions',  '2;PL': 'aviez',  '3;PL': 'avaient'},
                        "IND;PST;PFV;LGSPEC1": {'1;SG': 'eus', '2;SG': 'eus', '3;SG': 'eut', '1;PL': 'eûmes',  '2;PL': 'eûtes',  '3;PL': 'eurent'},
                        "COND;PST": {'1;SG': 'aurais', '2;SG': 'aurais', '3;SG': 'aurait', '1;PL': 'aurions',  '2;PL': 'auriez',  '3;PL': 'auraient'},
                        },
                  "e": {"IND;PRS": {'1;SG': "suis", '2;SG': 'es', '3;SG': 'est', '1;PL': 'sommes',  '2;PL': 'êtes',  '3;PL': "sont"},
                        "IND;FUT": {'1;SG': 'serai','2;SG': 'seras', '3;SG': 'sera', '1;PL': 'serons',  '2;PL': 'serez', '3;PL': 'seront'},
                        "IND;PST;IPFV": {'1;SG': 'étais','2;SG': 'étais', '3;SG': 'était', '1;PL': 'étions',  '2;PL': 'étiez',  '3;PL': 'étaient'},
                        "IND;PST;PFV;LGSPEC1": {'1;SG': 'fus', '2;SG': 'fus', '3;SG': 'fut', '1;PL': 'fûmes',  '2;PL': 'fûtes',  '3;PL': 'furent'},
                        "COND;PST": {'1;SG': 'serais', '2;SG': 'serais', '3;SG': 'serait', '1;PL': 'serions',  '2;PL': 'seriez',  '3;PL': 'seraient'}
                        }
}


VERBOSE = 0

TRANSLATE_PRON_FEAT_TO_LEFF = {"1;SG;MASC": 'SG;MASC',
                                "1;SG": 'SG;MASC',
                               "1;SG;FEM": 'SG;FEM',


                               "2;SG": 'SG;MASC',

                               "3;SG;MASC": 'SG;MASC',
                               "3;SG;FEM": 'SG;FEM',

                               "1;PL": 'PL;MASC',
                               "2;PL": 'PL;MASC',

                               "3;PL": 'PL;MASC',

                               "3;PL;MASC": 'PL;MASC',
                               "3;PL;FEM": 'PL;FEM',
                               }


GET_LEFF_PP = {
                                "1;SG": ['SG;MASC', 'SG;FEM'],
                                "2;SG": ['SG;MASC', 'SG;FEM'],

                                "3;SG;MASC": ['SG;MASC'],
                                "3;SG;FEM": ['SG;FEM'],
                                "3;SG": ['SG;MASC', 'SG;FEM'],  # 'se' ?
                                "3;SG;NEUT": ['SG;MASC'],   #"en"
                                "1;PL": ['PL;MASC', 'PL;FEM'],
                                "2;PL": ['PL;MASC', 'PL;FEM'],

                                "3;PL": ['PL;MASC', 'PL;FEM'],
                                "3;PL;MASC": ['PL;MASC'],
                                "3;PL;FEM": ['PL;FEM'],

                               }


def get_ptcp_pst_pn_expansion(case, aux, table_unimorph, table_leff, pron_argument_feat, pron_subject_feat):
    ptcp_pst = table_unimorph["V.PTCP;PST"]
    if aux == "e":
        # we agree the past participle with the 'pronom personel'
        # translate: _pron_feat
        return (
            # participe passé
                [table_leff[aggrement] for aggrement in GET_LEFF_PP[pron_subject_feat]],
            # pronoun list features SUBJET
                [f'{pron_subject_feat[0]};{feature}' for feature in GET_LEFF_PP[pron_subject_feat]],
            # pronoun list features ARGUMENT
                None if pron_argument_feat is None else [f'{pron_argument_feat}' for _ in GET_LEFF_PP[pron_subject_feat]]
                )

    elif aux == "a":
        if case[0] == "a":
            # we agree the past participle with the 'pronom complément'
            # we know that the COD will be before the verb --> the argument needs to agree with the accusatif prono,
            try:
                return (
                    [table_leff[aggrement] for aggrement in GET_LEFF_PP[pron_argument_feat]],
                    [pron_subject_feat for _ in  GET_LEFF_PP[pron_argument_feat]], # subject feat is not expanded cause the agreement will be with the argument
                    None if pron_argument_feat is None else [f'{pron_argument_feat[0]};{feature}' for feature in GET_LEFF_PP[pron_argument_feat]])
            except:
                if ptcp_pst not in ["fallu", "valut"]:
                    # in 'fallut" it is ok because only MASC SG
                    breakpoint()
                    print(f"Warning: could not do the agreement for aux avoir , verb {ptcp_pst}")

                return ([ptcp_pst], [pron_subject_feat], [pron_argument_feat])
        else:

            return ([ptcp_pst], [pron_subject_feat], [pron_argument_feat])
    else:
        raise (Exception("aux not defined"))




def append_declarative_sent(new_table, full_feature, form, subject, case, seed_full_form,_pron_feat=None, pron=None, aux=None):
    # features


    # forms
    if aux is None:
        pron, subject = phonological_constrain_pronons(pron=pron, form=form, type=case, subject=subject)
    else:
        pron, subject = phonological_constrain_pronons(pron=pron, form=aux, type=case, subject=subject)
    if pron.strip() in ["en", "y"] and subject.strip() == "je":
        subject = "j'"

    new_table[full_feature] = f"{seed_full_form}{subject}{pron}{aux+' ' if aux is not None else ''}{form}."


def append_question(new_table, _pron_feat, full_feature, form, subject, case, seed_full_form, pron=None, aux=None):


    full_feature += "Q;"

    # form
    if aux is None:
        # le dites?
        pron, subject = phonological_constrain_pronons(pron=pron, form=form, type=case, subject=subject)
        full_form = f"{seed_full_form}{pron}{form}{get_question_phonological_link(before_subject=form, subject=subject, case=case)}{subject} ?"
    else:
        pron, subject = phonological_constrain_pronons(pron=pron, form=aux, type=case, subject=subject)
        full_form = f"{seed_full_form}{pron}{aux}{get_question_phonological_link(before_subject=aux, subject=subject, case=case)}{subject} {form} ?"

    new_table[full_feature] = full_form


def append_negation(new_table, _pron_feat, full_feature, form, subject, case, seed_full_form,  pron=None, aux=None):

    full_feature += "NEG;"
    # forms

    if aux is None:
        pron, subject = phonological_constrain_pronons(pron=pron, form=form, type=case, subject=subject)
        full_form = f"{seed_full_form}{subject}{get_ne(pron=pron,type=case, form=form)}{pron}{form} pas."
    else:
        pron, subject = phonological_constrain_pronons(pron=pron, form=aux, type=case, subject=subject)
        full_form = f"{seed_full_form}{subject}{get_ne(pron=pron, type=case,form=aux)}{pron}{aux + ' ' if aux is not None else ''}pas {form}."

    new_table[full_feature] = full_form


def append_question_and_negation(new_table, _pron_feat, full_feature, form, subject, case, seed_full_form, pron=None, aux=None):

    # feature
    full_feature += "NEG;Q;"
    # form
    if aux is None:
        pron, subject = phonological_constrain_pronons(pron=pron, form=form, type=case, subject=subject)
        full_form = f"{seed_full_form}{get_ne(pron=pron, type=case, form=form)}{pron}{form}{get_question_phonological_link(before_subject=form, subject=subject, case=case)}{subject}pas ?"
    else:
        pron, subject = phonological_constrain_pronons(pron=pron, form=aux, type=case, subject=subject)
        full_form = f"{seed_full_form}{get_ne(pron=pron, type=case, form=aux)}{pron}{aux}{get_question_phonological_link(before_subject=aux, subject=subject, case=case)}{subject}pas {form} ?"
    new_table[full_feature] = full_form


def append_4_types_of_sentences(new_table, _pron_feat, seed_full_feature, form, subject, case, seed_full_form, pron=None, aux=None):

    full_feature = get_full_feature_single_pronon_case(seed_full_feature=seed_full_feature,case=case, _pron_feat=_pron_feat, pron=pron)

    append_declarative_sent(new_table=new_table, _pron_feat=_pron_feat, full_feature=full_feature, form=form,
                            subject=subject, case=case, seed_full_form=seed_full_form,
                            pron=pron, aux=aux)

    append_negation(new_table=new_table, _pron_feat=_pron_feat, full_feature=full_feature, form=form,
                    subject=subject, case=case, seed_full_form=seed_full_form,
                     pron=pron, aux=aux)

    append_question(new_table=new_table, _pron_feat=_pron_feat, full_feature=full_feature, form=form,
                    subject=subject, case=case, seed_full_form=seed_full_form,
                    pron=pron, aux=aux)
    append_question_and_negation(new_table=new_table, _pron_feat=_pron_feat, full_feature=full_feature,
                                 form=form, subject=subject, case=case, seed_full_form=seed_full_form,
                                 pron=pron, aux=aux)


def append_declarative_sent_bi_pron(new_table, full_feature, form, subject, case, seed_full_form,
                                    _pron_feat_0=None, pron_0=None, _pron_feat_1=None, pron_1=None,
                                    aux=None):
    # features

    assert len(case) == 2

    #full_feature = seed_full_feature + f"{cases[case[0]]}({_pron_feat_0});" + f"{cases[case[1]]}({_pron_feat_1});"

    pron_pairs, tonique_1 = two_pronouns_order_and_phonological_constrains(_pron_feat_0=_pron_feat_0,
                                                                           _pron_feat_1=_pron_feat_1,
                                                                           pron_0=pron_0,
                                                                           pron_1=pron_1, form=aux if aux is not None else form,
                                                                           type=case)
    #if form == "trouvais" and case == "gr" and aux is None:
        #breakpoint()
    if aux is None:
        new_table[full_feature] = f"{seed_full_form}{subject} {pron_pairs}{form}{tonique_1}."
    else:
        new_table[full_feature] = f"{seed_full_form}{subject} {pron_pairs}{aux + ' '}{form}{tonique_1}."


def append_question_sent_bi_pron(new_table, full_feature, form, subject, case, seed_full_form,
                                 _pron_feat_0=None, pron_0=None, _pron_feat_1=None, pron_1=None, aux=None):
    # features

    assert len(case) == 2

    #full_feature = seed_full_feature + f"{cases[case[0]]}({_pron_feat_0});" + f"{cases[case[1]]}({_pron_feat_1});"
    full_feature += "Q;"

    pronon_pairs, tonique_1 = two_pronouns_order_and_phonological_constrains(pron_0=pron_0, pron_1=pron_1,
                                                                             _pron_feat_0=_pron_feat_0,
                                                                             _pron_feat_1=_pron_feat_1,
                                                                             form=aux if aux is not None else form,
                                                                             type=case)
    if aux is None:
        new_table[full_feature] = f"{seed_full_form}{pronon_pairs}{form}{get_question_phonological_link(before_subject=form, subject=subject, case=case)}{subject}{tonique_1} ?"
    else:
        new_table[full_feature] = f"{seed_full_form}{pronon_pairs}{aux}{get_question_phonological_link(before_subject=aux, subject=subject, case=case)}{subject} {form}{tonique_1} ?"


def append_neg_sent_bi_pron(new_table, full_feature, form, subject, case, seed_full_form, _pron_feat_0=None,
                            pron_0=None, _pron_feat_1=None, pron_1=None, aux=None):
    # features
    assert len(case) == 2

    #full_feature = seed_full_feature + f"{cases[case[0]]}({_pron_feat_0});" + f"{cases[case[1]]}({_pron_feat_1});"
    full_feature += "NEG;"

    pronon_pairs, tonique_1 = two_pronouns_order_and_phonological_constrains(pron_0=pron_0, pron_1=pron_1,
                                                                             _pron_feat_0=_pron_feat_0,
                                                                             _pron_feat_1=_pron_feat_1,
                                                                             form=aux if aux is not None else form,
                                                                             type=case)
    if aux is None:
        # NB: here get_ne has not impact for now, just generates 'ne' all the time
        new_table[full_feature] = f"{seed_full_form}{subject} {get_ne(pron=_pron_feat_0,type=case, form=form)}{pronon_pairs}{form} pas{tonique_1}."
    else:
        new_table[full_feature] = f"{seed_full_form}{subject} {get_ne(pron=_pron_feat_0,type=case, form=form)}{pronon_pairs}{aux + ' '}pas {form}{tonique_1}."


def append_question_negation_sent_bi_pron(new_table, full_feature, form, subject, case, seed_full_form,
                                          _pron_feat_0=None, pron_0=None, _pron_feat_1=None, pron_1=None, aux=None):
    # features

    assert len(case) == 2

    #full_feature = seed_full_feature + f"{cases[case[0]]}({_pron_feat_0});" + f"{cases[case[1]]}({_pron_feat_1});"
    full_feature += "NEG;Q;"
    pronon_pairs, tonique_1 = two_pronouns_order_and_phonological_constrains(pron_0=pron_0, pron_1=pron_1,
                                                                  _pron_feat_0=_pron_feat_0,
                                                                  _pron_feat_1=_pron_feat_1,
                                                                  form=aux if aux is not None else form,
                                                                  type=case)

    if aux is None:
        new_table[full_feature] = f"{seed_full_form}{get_ne(pron=_pron_feat_0,type=case, form=form)}{pronon_pairs}{form}{get_question_phonological_link(before_subject=form, subject=subject, case=case)}{subject} pas{tonique_1} ?"
    else:
        new_table[full_feature] = f"{seed_full_form}{get_ne(pron=_pron_feat_0,type=case, form=form)}{pronon_pairs}{aux}{get_question_phonological_link( before_subject=aux, subject=subject, case=case)}{subject} pas {form}{tonique_1} ?"


def get_full_feature_bi_pronon_case(seed_full_feature, case, _pron_feat_0, _pron_feat_1, pn):

    if case[1] != "r":
        return seed_full_feature + f"{cases[case[0]]}({_pron_feat_0});" + f"{cases[case[1]]}({_pron_feat_1});"
    elif case[0] in ["a", "d"] and case[1] == "r":
        # we check the alignement of pronoun this way because acc and dat have the same granularity level
        RFLX = ";RFLX" if pn == _pron_feat_1 and pn.startswith("3") else ""
        return seed_full_feature + f"{cases[case[0]]}({_pron_feat_0}{RFLX});"
    else:
        # the RFLX has been taken care of inside the NOM group
        return seed_full_feature + f"{cases[case[0]]}({_pron_feat_0});"


def get_full_feature_single_pronon_case(seed_full_feature, case, _pron_feat, pron):

    if case in ["a", "d", "l", "g"]:
        assert pron is not None
        full_feature = seed_full_feature + f"{cases[case]}({_pron_feat});"
    elif case in ["0", "r"]:
        full_feature = seed_full_feature
    else:
        raise(Exception(f"case {case} not supported"))

    return full_feature


def append_4_types_of_sentences_two_pron(new_table, seed_full_feature, form, subject, case, seed_full_form,
                                    _pron_feat_0=None, pron_0=None, _pron_feat_1=None, pron_1=None,
                                    aux=None):

    full_feature = get_full_feature_bi_pronon_case(seed_full_feature, case, _pron_feat_0, _pron_feat_1)

    append_declarative_sent_bi_pron(new_table, full_feature, form, subject, case, seed_full_form,
                                    _pron_feat_0=_pron_feat_0, pron_0=pron_0, _pron_feat_1=_pron_feat_1, pron_1=pron_1,
                                    aux=aux)


    append_neg_sent_bi_pron(new_table, full_feature, form, subject, case, seed_full_form,
                                 _pron_feat_0=_pron_feat_0, pron_0=pron_0, _pron_feat_1=_pron_feat_1, pron_1=pron_1,
                                 aux=aux)
    #if 'IND;PRS;NOM(1;SG);' in seed_full_feature:
    #    breakpoint()
    append_question_sent_bi_pron(new_table, full_feature, form, subject, case, seed_full_form,
                                 _pron_feat_0=_pron_feat_0, pron_0=pron_0, _pron_feat_1=_pron_feat_1, pron_1=pron_1,
                                 aux=aux)
    append_question_negation_sent_bi_pron(new_table, full_feature, form, subject, case, seed_full_form,
                                          _pron_feat_0=_pron_feat_0, pron_0=pron_0, _pron_feat_1=_pron_feat_1, pron_1=pron_1,
                                          aux=aux)


def get_question_phonological_link(before_subject, subject, case):
    if case in ["a", "d", "l", "0", "g", "l", "r", "ag", "dg", "al", "ad", "ar", "dr", "lr", "gr"]:
        if re.match("^[aeiouy].*", subject) and re.match(".*[aeiouy]$", before_subject):
            return "-t-"
        else:
            return "-"
    raise(Exception(f"case {case} not supported"))


def get_ne(pron, type, form):
    if type == "l":
        assert pron.strip() == "y", f"pron not 'y' but {pron}"
        return "n'"
    elif type == "g":
        assert pron.strip() == "en", f"pron not 'en' but {pron}"
        return "n'"
    elif type == "0":
        if re.match("^[aeiouyhéêh].*", form):
            return "n'"
        else:
            return "ne "
    else:
        return "ne "


def phonological_constrain_pronons(form, pron=None, subject=None, type="a"):
    if pron is None:
        assert type == "0", f"Case is not intransitif but not pronoun provided {form}"
        assert subject is not None

    if type == "a" or type == "r":
        if re.match("^[aeiouyhéêh].*", form) and re.match('.*[aeiou]$', pron):
            return pron[:-1]+"'", subject+" "
        else:
            return pron+" ", subject+" "
    elif type == "d":
        if re.match('^[aeiouyhéêh].*', form) and re.match('.*[aeiou]$', pron) and pron not in ["lui"]:
            return pron[:-1] + "'", subject+" "
        else:
            return pron+" ", subject+" "
    elif type in ["l", "g"]:
        if type == "g":
            if subject == "je":
                pass#breakpoint()
        if re.match("^[aeiouyhéêh].*", form) and pron in ["je"]:
            return pron[:-1] + "'", subject+" "
        #elif re.match("^[aeiouyhéêh].*", form) and subject in ["je"]:
        #    return pron + " ", subject[:-1] + "'"
        else:
            return pron + " ", subject+" "
    elif type == "0":
        assert pron is None

        if re.match("^[aeiouyhéêh].*", form) and pron in ["je"]:
            return "", subject[:-1] + "'"
        else:
            return "", subject+" "
    else:
        raise(f"Type case not supported {type}")


def two_pronouns_order_and_phonological_constrains(form, _pron_feat_0=None, _pron_feat_1=None, pron_0=None, pron_1=None, type="ad", mood=None):
    tonique_1 = ""

    if type == "ad":
        # pron_1 is datif
        # pron_0 is accusatif
        if _pron_feat_0 is None:
            breakpoint()
        if _pron_feat_0[0] in ['1', '2']:
            # here we want to add à moi/toi/eux... tonique pronouns
            tonique_1 = ' à ' + tonique_pronouns[_pron_feat_1]

            if re.match(".*[aeiou]$", pron_0) and re.match("^[aeiouyhéêh].*", form):
                return pron_0[:-1] + "'", tonique_1
            else:
                return pron_0+" ", tonique_1

        first = pron_0
        second = pron_1

        if pron_1 in ["me", "te", "nous", "vous"] and pron_0 in ["les", "le", "la"]:
            #first = "I-"+pron_1
            first =  pron_1
            #second = "D-"+pron_0
            second = pron_0

            if re.match(".*[aeiou]$", second) and re.match("^[aeiouyhéêh].*", form):
                return first+" "+second[:-1]+"'", tonique_1
        return first+" "+second+" ", tonique_1
    else:
        assert pron_1 is not None
        if type in ["dr", "ar"]:
            breakpoint()
        if type in ["al", "ag"]:#, "lr", "gr"]:

            if pron_0 in ["toi", "moi"] and pron_1 in ["en", "y"]:
                return pron_0[:-2] + "'" + pron_1 + " ", tonique_1
            if re.match(".*[aeiou]$", pron_0) and re.match("^[aeiouyhéêh].*", pron_1):
                return pron_0[:-1] + "'" + pron_1 + " ", tonique_1
            return pron_0 + " " + pron_1 + " ", tonique_1
        elif type in ["lr", "gr"]:
            if pron_1 in ["toi", "moi"] and pron_0 in ["en", "y"]:
                return pron_1[:-2] + "'" + pron_0 + " ", tonique_1
            if re.match(".*[aeiou]$", pron_1) and re.match("^[aeiouyhéêh].*", pron_0):
                return pron_1[:-1] + "'" + pron_0 + " ", tonique_1
            return pron_1 + " " + pron_0 + " ", tonique_1
        elif type in ["dg"]:
            if pron_0 in ["toi", "moi"] and pron_1 in ["en", "y"]:
                # might be able to factorize with if pron_0 in ["toi", "moi"] and pron_1 in ["en", "y"]: above
                return pron_0[:-2] + "'" + pron_1 + " ", tonique_1
            if re.match(".*[aeiou]$", pron_0) and re.match("^[aeiouyhéêh].*", pron_1) and pron_0 not in ["lui"]:
                return pron_0[:-1] + "'" + pron_1 + " ", tonique_1
            return pron_0 + " " + pron_1 + " ", tonique_1

        else:
            return pron_0 + " " + pron_1 + " ", tonique_1


def imperatif_pronouns(pron, type="a"):

    if type == "a" or type == "r" or type == "d":
        if pron == "te":
            return "toi"
        elif pron == "me":
            return "moi"
        return pron
    elif type in ["l", "g"]:
        #assert pron == "y"
        return pron
    elif type == "d":
        return pron
    else:
        raise(Exception(f"case {type} not supported "))


def get_order_pronon_imp_decl(_pron_imperatif_0, _pron_imperatif_1):
    # TODO
    return f"{_pron_imperatif_0} {_pron_imperatif_1}"


def only_impersonel_verb(responses):
    for r in responses:
        if not r.startswith("I"):
            return False
    return True


POS_INDEX_TO_CODE_ARG = ["a", "d", "l", "g", "o1", "o1"]


def get_arg_dic_ls(_response, index_response) -> list[dict]:
    if _response[index_response].startswith("(") and _response[0].endswith(")"):
        assert _response[index_response][1] == POS_INDEX_TO_CODE_ARG[index_response]
        arg_dic_ls = [prepos_prons[_response[index_response][1]], prepos_prons['0']]
    else:
        assert len(_response[0]) == 1 and _response[index_response][1] == POS_INDEX_TO_CODE_ARG[index_response]
        arg_dic_ls = [prepos_prons[_response[index_response][1]]]
    return arg_dic_ls


def get_order_pronon(_pron_0, _pron_1):
    # TODO
    # me/te/le/nous/vous/le/les
    #je te:COI le:COD dis
    # je le:COD lui:COI dis
    # je vous:COI le/les  dis / je le dis à vous,
    # je vous:COI le/les  dis
    if _pron_1 == "y":
        first_pron = _pron_0
        second_pron = _pron_1

    #phonological_constrain_pronons(pron=pron_0, form=form, type=case, subject=subject)
    #je m'y trouve
    # tu t'y trouve
    # M'y trouve ty
    # Ne m'y trouve tu pas
    return f"{_pron_0} {_pron_1} "


def create_new_table(responses, table, aux_dic, ptcp_pst_table):

    nfin = table['V;NFIN']
    new_table = {}

    #for _response in responses:
    #    aux_dic[_response] = list(set(aux_dic[_response]))

    for mood in moods:
        for tense in tenses:
            for i, aspect in enumerate(aspects):

                if tense != "PST" and i > 0:
                    # only going through the tensexmood one (cause aspect do not impact present and future)
                    continue
                for pn in person_number:
                    #

                    ## UNIMORPH MATCH
                    pers = ";".join(pn.split(";")[:2])
                    unimorph_match = f"V;{mood};{tense};{pers}"

                    if only_impersonel_verb(responses) and pers != "3;SG":
                        # we dont look for the form if it is impersonel and not 'il'
                        continue
                    try:
                        if mood == "IMP":
                            if pers not in ["2;SG", "1;PL", "2;PL"] or tense != "PRS":
                                # IMPERATIF  only for first and second person: only keeping present
                                continue
                            unimorph_match = f"V;POS;{mood};{pers}"
                            form = table[unimorph_match]
                            # print(f"IMP form {form} working for {unimorph_match}")

                        elif mood == "IND" and tense == "PST":  # and aspect == "PVF":
                            unimorph_match += f";{aspect}"
                            form = table[unimorph_match]
                            # print(f"PAST IND: form {form} working for {unimorph_match}")
                        elif mood == "COND":
                            if tense != "PRS":
                                # only
                                continue
                            unimorph_match = f"V;{mood};{pers}"
                            form = table[unimorph_match]

                        else:
                            form = table[unimorph_match]

                        # sabity check Participe passé
                    except Exception as e:
                        print(f"Warning: form {nfin} : {unimorph_match} not found in unimorph so skipping it {e}")
                        continue

                    try:
                        table["V.PTCP;PST"]
                    except Exception as e:
                        print(f"Warning: form {nfin} : 'V.PTCP;PST' not found in unimorph so skipping it {e}")
                        continue

                    ## END UNIMORPH MATCH

                    ## TENSE NAME
                    if tense == "PST":
                        if aspect == "PFV":
                            tense_feature = f'{tense}:LGSPEC1'
                        elif aspect == "IPFV":
                            tense_feature = f'{tense};IPFV'
                    else:
                        tense_feature = tense

                    for _response in responses:
                        impersonel_verb = _response[0] == "I"
                        original_feat = _response

                        #SKIP pn != il for impersonel
                        if impersonel_verb:
                            if pn != "3;SG;MASC":
                                continue
                            if VERBOSE:
                                print(f"{nfin} is impersonel")
                        # skip if it is not "il"  and not IND

                        _response = _response[1:]

                        for i, aux in enumerate(aux_dic[original_feat]):
                            # suppose you have (a)d(l)(g)(obl1)(obl2)
                            # (a),d,(l),(g),(obl1),(obl2) -->

                            # ad , dl a , ao1o2, 0  --> and + obl

                            # cannot generate adlg --> l and g are marked in the same one

                            acc_dic_ls = get_arg_dic_ls(_response, index_response=0)
                            for acc_dic in acc_dic_ls:
                                for _pron_feat_acc, _pron_acc in acc_dic.items():

                                    dat_dic_ls = get_arg_dic_ls(_response, index_response=1)
                                    for dat_dic in dat_dic_ls:
                                        for _pron_feat_dat, _pron_dat in dat_dic.items():

                                            loc_dic_ls = get_arg_dic_ls(_response, index_response=2)
                                            for loc_dic in loc_dic_ls:
                                                for _pron_feat_loc, _pron_loc in loc_dic.items():

                                                    gen_dic_ls = get_arg_dic_ls(_response, index_response=3)
                                                    for gen_dic in gen_dic_ls:
                                                        for _pron_feat_gen, _pron_gen in loc_dic.items():

                                                            pass

                                                            full_feature = f"{mood};{tense_feature};NOM({pn});"

                                                            append_4_types_of_sentences(new_table, _pron_feat=None,
                                                                                        seed_full_feature=full_feature,
                                                                                        seed_full_form=seed_full_form,
                                                                                        case=_response,
                                                                                        subject=nom_prons[pn],
                                                                                        form=form, pron=None, aux=None)

                                                            # GENERATE: for all should handle NONE and not NONE
                                                            # then make sure order is right
                                                            # if feature 0 --> _pron_feat_acc is None and _pron_acc is ''
                                                            #--> move to next one
                                                            # if feature a --> need to generate it



                            # ar

                            if _response not in ["a", "d", "l", "g", "0", "r", "ad",
                                                 "al", "ag", "dg", "lr", "gr", "ar", "dr"]:
                                print("Skipping ", _response)
                                raise("Not supported")

                                #raise(Exception(f"{_response} not supported "))

                            # INTRANSITIF VERBS
                            if _response == "0":
                                seed_full_form = ""
                                if mood == "IMP":
                                    full_form = seed_full_form + f"{form} !"
                                    full_feature = f"{mood};{tense_feature};NOM({pn});"
                                    new_table[full_feature] = full_form

                                    full_form = seed_full_form + f"{get_ne(None, _response, form)}{form} pas !"
                                    full_feature = f"{mood};{tense_feature};NOM({pn});NEG;"
                                    new_table[full_feature] = full_form
                                    if VERBOSE:
                                        print(f"-- {nfin}\t{full_form}\t{full_feature}")

                                else:
                                    # SIMPLE

                                    full_feature = f"{mood};{tense_feature};NOM({pn});"

                                    append_4_types_of_sentences(new_table, _pron_feat=None,
                                                                seed_full_feature=full_feature,
                                                                seed_full_form=seed_full_form,
                                                                case=_response, subject=nom_prons[pn],
                                                                form=form, pron=None, aux=None)

                                ptcp_pst_ls, pn_ls, _ = get_ptcp_pst_pn_expansion(_response, aux, table, ptcp_pst_table, None, pn)

                                for pn_feat_subject, ptcp_pst in zip(pn_ls, ptcp_pst_ls):

                                    # COMPOUND
                                    if mood == "IND":
                                        if tense == "FUT":
                                            # get FUT --> get future
                                            aux_form = auxiliary_dict[aux]["IND;FUT"][pers]
                                            #seed_full_feature = f"{AUX}IND;FUT;PFV;NOM({pn_feat_subject});"
                                            seed_full_feature = f"IND;FUT;PFV;NOM({pn_feat_subject});"

                                            append_4_types_of_sentences(new_table, _pron_feat=None,
                                                                        seed_full_feature=seed_full_feature,
                                                                        seed_full_form=seed_full_form,
                                                                        case=_response, subject=nom_prons[pn],
                                                                        form=ptcp_pst, pron=None, aux=aux_form)
                                            if VERBOSE:
                                                print(f"{nfin}\t{full_form}\t{full_feature}")

                                        elif tense == "PST":
                                            # present perfect / passé composé --> présent
                                            aux_form = auxiliary_dict[aux]["IND;PRS"][pers]
                                            #seed_full_feature = f"{AUX}IND;PST;NOM({pn_feat_subject});"
                                            seed_full_feature = f"IND;PST;NOM({pn_feat_subject});"
                                            append_4_types_of_sentences(new_table, _pron_feat=None,
                                                                        seed_full_feature=seed_full_feature,
                                                                        seed_full_form=seed_full_form,
                                                                        case=_response, subject=nom_prons[pn],
                                                                        form=ptcp_pst, pron=None, aux=aux_form)
                                            if VERBOSE:
                                                print(f"{nfin}\t{full_form}\t{full_feature}")

                                            # past-perfect / plus que parfait --> imparfait
                                            aux_form = auxiliary_dict[aux]["IND;PST;IPFV"][pers]
                                            #seed_full_feature = f"{AUX}IND;PST;PFV;NOM({pn_feat_subject});"
                                            seed_full_feature = f"IND;PST;PFV;NOM({pn_feat_subject});"
                                            append_4_types_of_sentences(new_table, _pron_feat=None,
                                                                        seed_full_feature=seed_full_feature,
                                                                        seed_full_form=seed_full_form,
                                                                        case=_response, subject=nom_prons[pn],
                                                                        form=ptcp_pst, pron=None, aux=aux_form)
                                            if VERBOSE:
                                                print(f"{nfin}\t{full_form}\t{full_feature}")

                                            # passé antérieur --> passé simple
                                            aux_form = auxiliary_dict[aux]["IND;PST;PFV;LGSPEC1"][pers]
                                            #seed_full_feature = f"{AUX}IND;PST;PFV;LGSPEC1;NOM({pn_feat_subject});"
                                            seed_full_feature = f"IND;PST;PFV;LGSPEC1;NOM({pn_feat_subject});"
                                            append_4_types_of_sentences(new_table, _pron_feat=None,
                                                                        seed_full_feature=seed_full_feature,
                                                                        seed_full_form=seed_full_form,
                                                                        case=_response, subject=nom_prons[pn],
                                                                        form=ptcp_pst, pron=None, aux=aux_form)

                                            if VERBOSE:
                                                print(f"{nfin}\t{full_form}\t{full_feature}")
                                    elif mood == "COND":
                                        # passé antérieur --> passé simple
                                        if tense == "PST":
                                            aux_form = auxiliary_dict[aux]["COND;PST"][pers]
                                            #seed_full_feature = f"{AUX}COND;PFV;NOM({pn_feat_subject});"
                                            seed_full_feature = f"COND;PFV;NOM({pn_feat_subject});"
                                            #??full_feature = seed_full_feature #+ f"{cases[_response]}({_pron_feat})"
                                            append_4_types_of_sentences(new_table, _pron_feat=None,
                                                                        seed_full_feature=seed_full_feature,
                                                                        seed_full_form=seed_full_form,
                                                                        case=_response, subject=nom_prons[pn],
                                                                        form=ptcp_pst, pron=None, aux=aux_form)
                                            if VERBOSE:
                                                print(f"{nfin}\t{full_form}\t{full_feature}")

                                continue

                            elif len(_response) == 2:
                                for _pron_feat_0, _pron_0 in prepos_prons[_response[0]].items():
                                    for _pron_feat_1, _pron_1 in prepos_prons[_response[1]].items():

                                        # accordé ptcp_pst
                                        # if r is here it will always be in first position
                                        if _response == "ad":
                                            if _pron_feat_0[0] in ['1', '2'] and ";".join(_pron_feat_0.split(";")[:1]) == ";".join(_pron_feat_1.split(";")[:1]):
                                                # skipping me me, te te..., me nous, nous me...
                                                continue
                                        # r should always be second
                                        if _response[1] == "r" and ";".join(_pron_feat_1.split(";")[:2]) != ";".join(pn.split(";")[:2]):
                                            # in reflexive cases: only "je me..., tu te... "
                                            continue

                                        if _response[1] != "r":
                                            seed_full_feature = f"{mood};{tense_feature};NOM({pn});"
                                        else:
                                            if _response[0] in ["a", "d"]:
                                                # in this case thr RFLX feature is taken care of in the ACC/DAT
                                                seed_full_feature = f"{mood};{tense_feature};NOM({pn});"
                                            elif  ";".join(_pron_feat_1.split(";")[:2]) != ";".join(pn.split(";")[:2]):
                                                # pronouns not aligned so not reflexif
                                                seed_full_feature = f"{mood};{tense_feature};NOM({pn});"
                                            else:
                                                # reflexif
                                                seed_full_feature = f"{mood};{tense_feature};NOM({pn};RFLX);"
                                        seed_full_form = ""

                                        # SIMPLE TENSES
                                        if mood == "IMP":
                                            if (pn == "1;PL" and _pron_feat_0 == "2;SG") or (pn == "1;PL" and _pron_feat_0 == "2;PL"):
                                                continue
                                            # IMPERATIF AFFIRMATIF
                                            _pron_imperatif_0 = imperatif_pronouns(_pron_0, type=_response[0])
                                            _pron_imperatif_1 = imperatif_pronouns(_pron_1, type=_response[1])
                                            _pron_imperatif, tonique_1 = two_pronouns_order_and_phonological_constrains(_pron_feat_0=_pron_feat_0, _pron_feat_1=_pron_feat_1, pron_0=_pron_imperatif_0, pron_1=_pron_imperatif_1, form=form, type=_response, mood=mood)

                                            full_form = seed_full_form + f"{form}-{_pron_imperatif}{tonique_1}!"
                                            full_feature = get_full_feature_bi_pronon_case(seed_full_feature, _response, _pron_feat_0, _pron_feat_1, pn)
                                            #full_feature = seed_full_feature + f"{cases[_response[0]]}({_pron_feat_0});" + f"{cases[_response[1]]}({_pron_feat_1});"
                                            new_table[full_feature] = full_form

                                            # IMPERATIF NEGATIVE
                                            full_feature += "NEG;"

                                            # For negation : no "moi" "toi"
                                            _pron_imperatif, tonique_1 = two_pronouns_order_and_phonological_constrains(_pron_feat_0=_pron_feat_0, _pron_feat_1=_pron_feat_1, pron_0=_pron_0, pron_1=_pron_1, form=form,type=_response, mood=mood)
                                            full_form = seed_full_form + f"{get_ne(_pron_0, type=_response,form=form)}{_pron_imperatif} {form} pas{tonique_1} !"
                                            new_table[full_feature] = full_form

                                            if VERBOSE:
                                                print(f"{nfin}\t{full_form}\t{full_feature}")

                                        else:

                                            seed_full_form = ""
                                            # SIMPLE TENSES

                                            append_4_types_of_sentences_two_pron(new_table, seed_full_feature, form,
                                                                                 nom_prons[pn],
                                                                                 _response, seed_full_form,
                                                                                 _pron_feat_0=_pron_feat_0,
                                                                                 pron_0=_pron_0,
                                                                                 _pron_feat_1=_pron_feat_1,
                                                                                 pron_1=_pron_1,
                                                                                 aux=None)


                                            if VERBOSE:
                                                print(f"{nfin}\t{full_form}\t{full_feature}")


                                        # COUMPOUND TENSES (GENDER EXPANSION BASED ON PP)
                                        # accusatif would only be in position 0 so the agreement is done
                                        ptcp_pst_ls, pn_ls, pn_feat_argument_0_ls = get_ptcp_pst_pn_expansion(_response, aux, table, ptcp_pst_table, _pron_feat_0, pn)

                                        for pn_feat_subject, pn_feat_arg_0, ptcp_pst in zip(pn_ls, pn_feat_argument_0_ls, ptcp_pst_ls):
                                            seed_full_form = ""

                                            if (pn == "1;PL" and _pron_feat_0 == "1;SG") or (pn == "2;PL" and _pron_feat_0 == "2;SG") or (pn == "2;SG" and _pron_feat_0 == "2;PL"):
                                                continue
                                            RFLX = ""
                                            if mood == "IND":
                                                if tense == "FUT":
                                                    # get FUT --> get future
                                                    aux_form = auxiliary_dict[aux]["IND;FUT"][pers]

                                                    seed_full_feature = f"IND;FUT;PFV;NOM({pn_feat_subject});"

                                                    append_4_types_of_sentences_two_pron(new_table, seed_full_feature,
                                                                                    ptcp_pst, nom_prons[pn],
                                                                                    _response, seed_full_form,
                                                                                    _pron_feat_0=pn_feat_arg_0,
                                                                                    pron_0=_pron_0,
                                                                                    _pron_feat_1=_pron_feat_1,
                                                                                    pron_1=_pron_1,
                                                                                    aux=aux_form)


                                                    if VERBOSE:
                                                        print(f"{nfin}\t{full_form}\t{full_feature}")

                                                elif tense == "PST":
                                                    # present perfect / passé composé --> présent
                                                    aux_form = auxiliary_dict[aux]["IND;PRS"][pers]

                                                    seed_full_feature = f"IND;PST;NOM({pn_feat_subject});"

                                                    append_4_types_of_sentences_two_pron(new_table, seed_full_feature,
                                                                                    ptcp_pst, nom_prons[pn],
                                                                                    _response, seed_full_form,
                                                                                    _pron_feat_0=pn_feat_arg_0,
                                                                                    pron_0=_pron_0,
                                                                                    _pron_feat_1=_pron_feat_1,
                                                                                    pron_1=_pron_1,
                                                                                    aux=aux_form)

                                                    if VERBOSE:
                                                        print(f"{nfin}\t{full_form}\t{full_feature}")

                                                    # past-perfect / plus que parfait --> imparfait
                                                    aux_form = auxiliary_dict[aux]["IND;PST;IPFV"][pers]

                                                    seed_full_feature = f"IND;PST;PFV;NOM({pn_feat_subject});"

                                                    append_4_types_of_sentences_two_pron(new_table, seed_full_feature,
                                                                                    ptcp_pst, nom_prons[pn],
                                                                                    _response, seed_full_form,
                                                                                    _pron_feat_0=pn_feat_arg_0,
                                                                                    pron_0=_pron_0,
                                                                                    _pron_feat_1=_pron_feat_1,
                                                                                    pron_1=_pron_1,
                                                                                    aux=aux_form)

                                                    if VERBOSE:
                                                        print(f"{nfin}\t{full_form}\t{full_feature}")

                                                    # passé antérieur --> passé simple
                                                    aux_form = auxiliary_dict[aux]["IND;PST;PFV;LGSPEC1"][pers]
                                                    #seed_full_feature = f"{AUX}IND;PST;PFV;LGSPEC1;NOM({pn_feat_subject});"
                                                    seed_full_feature = f"IND;PST;PFV;LGSPEC1;NOM({pn_feat_subject});"

                                                    append_4_types_of_sentences_two_pron(new_table, seed_full_feature,
                                                                                    ptcp_pst, nom_prons[pn],
                                                                                    _response, seed_full_form,
                                                                                    _pron_feat_0=pn_feat_arg_0,
                                                                                    pron_0=_pron_0,
                                                                                    _pron_feat_1=_pron_feat_1,
                                                                                    pron_1=_pron_1,
                                                                                    aux=aux_form)

                                                    if VERBOSE:
                                                        print(f"{nfin}\t{full_form}\t{full_feature}")
                                            elif mood == "COND":
                                                # passé antérieur --> passé simple
                                                if tense == "PST":
                                                    aux_form = auxiliary_dict[aux]["COND;PST"][pers]

                                                    seed_full_feature = f"COND;PFV;NOM({pn_feat_subject});"

                                                    append_4_types_of_sentences_two_pron(new_table, seed_full_feature,
                                                                                    ptcp_pst, nom_prons[pn],
                                                                                    _response, seed_full_form,
                                                                                    _pron_feat_0=pn_feat_arg_0,
                                                                                    pron_0=_pron_0,
                                                                                    _pron_feat_1=_pron_feat_1,
                                                                                    pron_1=_pron_1,
                                                                                    aux=aux_form)

                                                    if VERBOSE:
                                                        print(f"{nfin}\t{full_form}\t{full_feature}")
                            elif len(_response) == 1 and _response != "0":
                                for _pron_feat, _pron in prepos_prons[_response].items():

                                    # accordé ptcp_pst
                                    if _response[0] == "r" and ";".join(_pron_feat.split(";")[:2]) != ";".join(pn.split(";")[:2]):
                                        # in reflexive cases: only "je me..., tu te... "
                                        continue

                                    RFLX = ";RFLX" if _response[0] == "r" else ""
                                    seed_full_feature = f"{mood};{tense_feature};NOM({pn}{RFLX});"
                                    seed_full_form = ""

                                    if mood == "IMP":

                                        if (pn == "1;PL" and _pron_feat == "2;SG") or \
                                                (pn == "1;PL" and _pron_feat == "2;PL"):
                                            # TODO: fact check this
                                            continue
                                        _pron_imperatif = imperatif_pronouns(_pron, type=_response)
                                        full_form = seed_full_form + f"{form}-{_pron_imperatif} !"
                                        #full_feature = seed_full_feature + f"{cases[_response]}({_pron_feat});"
                                        full_feature = get_full_feature_single_pronon_case(seed_full_feature, _response, _pron_feat, _pron)
                                        new_table[full_feature] = full_form
                                        full_feature += "NEG;"

                                        full_form = seed_full_form + f"{get_ne(_pron, type=_response, form=form)}{phonological_constrain_pronons(form=form, pron=_pron, subject='', type=_response)[0]}{form} pas !"
                                        new_table[full_feature] = full_form

                                        if VERBOSE:
                                            print(f"{nfin}\t{full_form}\t{full_feature}")

                                    else:
                                        seed_full_form = ""
                                        # SIMPLE TENSES
                                        append_4_types_of_sentences(new_table, _pron_feat=_pron_feat,
                                                                    seed_full_feature=seed_full_feature,
                                                                    seed_full_form=seed_full_form,
                                                                    case=_response, subject=nom_prons[pn],
                                                                    form=form, pron=_pron)

                                        if VERBOSE:
                                            print(f"{nfin}\t{full_form}\t{full_feature}")

                                    ptcp_pst_ls, pn_ls, pn_feat_argument_ls = get_ptcp_pst_pn_expansion(_response, aux, table, ptcp_pst_table, _pron_feat, pn)

                                    for pn_feat_subject, pn_feat_arg, ptcp_pst in zip(pn_ls, pn_feat_argument_ls, ptcp_pst_ls):
                                        seed_full_form = ""

                                        if (pn == "1;PL" and _pron_feat == "1;SG") or (pn == "2;PL" and _pron_feat == "2;SG") or (
                                                pn == "2;SG" and _pron_feat == "2;PL"):
                                            # TODO: double check  (pn == "2;SG" and _pron_feat == "2;PL"): 'tu vous répondrais' not possible ?
                                            continue
                                        # neg
                                        # COMPOUND TENSE
                                        if mood == "IND":
                                            if tense == "FUT":
                                                # get FUT --> get future
                                                aux_form = auxiliary_dict[aux]["IND;FUT"][pers]
                                                #seed_full_feature = f"{AUX}IND;FUT;PFV;NOM({pn_feat_subject});"
                                                seed_full_feature = f"IND;FUT;PFV;NOM({pn_feat_subject}{RFLX});"
                                                #full_feature = seed_full_feature + f"{cases[_response]}({pn_feat_arg})"

                                                append_4_types_of_sentences(new_table, _pron_feat=pn_feat_arg,
                                                                            seed_full_feature=seed_full_feature,
                                                                            seed_full_form=seed_full_form,
                                                                            aux=aux_form,
                                                                            case=_response, subject=nom_prons[pn], form=ptcp_pst,
                                                                            pron=_pron)

                                                if VERBOSE:
                                                    print(f"{nfin}\t{full_form}\t{full_feature}")

                                            elif tense == "PST":
                                                # present perfect / passé composé --> présent
                                                aux_form = auxiliary_dict[aux]["IND;PRS"][pers]
                                                #seed_full_feature = f"{AUX}IND;PST;NOM({pn_feat_subject});"
                                                seed_full_feature = f"IND;PST;NOM({pn_feat_subject}{RFLX});"
                                                #full_feature = seed_full_feature + f"{cases[_response]}({_pron_feat})"

                                                append_4_types_of_sentences(new_table, _pron_feat=pn_feat_arg,
                                                                            seed_full_feature=seed_full_feature,
                                                                            seed_full_form=seed_full_form,
                                                                            aux=aux_form,
                                                                            case=_response, subject=nom_prons[pn], form=ptcp_pst,
                                                                            pron=_pron)

                                                if VERBOSE:
                                                    print(f"{nfin}\t{full_form}\t{full_feature}")

                                                # past-perfect / plus que parfait --> imparfait
                                                aux_form = auxiliary_dict[aux]["IND;PST;IPFV"][pers]
                                                #seed_full_feature = f"{AUX}IND;PST;PFV;NOM({pn_feat_subject});"
                                                seed_full_feature = f"IND;PST;PFV;NOM({pn_feat_subject}{RFLX});"

                                                append_4_types_of_sentences(new_table, _pron_feat=pn_feat_arg,
                                                                            seed_full_feature=seed_full_feature,
                                                                            seed_full_form=seed_full_form,
                                                                            case=_response, subject=nom_prons[pn], form=ptcp_pst,
                                                                            aux=aux_form,
                                                                            pron=_pron)

                                                if VERBOSE:
                                                    print(f"{nfin}\t{full_form}\t{full_feature}")

                                                # passé antérieur --> passé simple
                                                aux_form = auxiliary_dict[aux]["IND;PST;PFV;LGSPEC1"][pers]
                                                #seed_full_feature = f"{AUX}IND;PST;PFV;LGSPEC1;NOM({pn_feat_subject});"
                                                seed_full_feature = f"IND;PST;PFV;LGSPEC1;NOM({pn_feat_subject}{RFLX});"

                                                append_4_types_of_sentences(new_table, _pron_feat=pn_feat_arg,
                                                                            seed_full_feature=seed_full_feature,
                                                                            seed_full_form=seed_full_form,
                                                                            aux=aux_form,
                                                                            case=_response, subject=nom_prons[pn], form=ptcp_pst,
                                                                            pron=_pron)

                                                if VERBOSE:
                                                    print(f"{nfin}\t{full_form}\t{full_feature}")
                                        elif mood == "COND":
                                            # passé antérieur --> passé simple
                                            if tense == "PST":
                                                aux_form = auxiliary_dict[aux]["COND;PST"][pers]
                                                #seed_full_feature = f"{AUX}COND;PFV;NOM({pn_feat_subject});"
                                                seed_full_feature = f"COND;PFV;NOM({pn_feat_subject}{RFLX});"

                                                append_4_types_of_sentences(new_table, _pron_feat=pn_feat_arg,
                                                                            seed_full_feature=seed_full_feature,
                                                                            seed_full_form=seed_full_form,
                                                                            aux=aux_form,
                                                                            case=_response, subject=nom_prons[pn], form=ptcp_pst,
                                                                            pron=_pron)

                                                if VERBOSE:
                                                    print(f"{nfin}\t{full_form}\t{full_feature}")

    return new_table
# in it: 'IMP;PRS;NOM(1;PL);LOC(3;SG;NEUT);NEG': "n'y allons pas!"


def freq_sort(vocab_dir, language="fr"):
    path = os.path.join(vocab_dir, language + '.txt')

    if not os.path.isfile(path):
        print(f"Warning: Reading frequency list empty")
        return []
    print(f"Reading frequency list from {path}")
    with open(path, encoding='utf8') as f:
        return [line.strip() for line in f.readlines()]


def read_unimorph(unimorph_dir, pos='V', language="fr", exclude_doublets=True):
    path = os.path.join(unimorph_dir, f'{language}.txt')
    data = {}
    with open(path, encoding='utf8') as f:
        for line in f:
            line = line.strip()
            parts = line.split('\t')
            if len(parts) != 3:
                continue
            lemma, form, feats = parts
            if not feats.startswith(pos):
                continue
            if lemma not in data:
                data[lemma] = {}
            if feats not in data[lemma]:
                data[lemma][feats] = set()
            data[lemma][feats].add(form)

    if exclude_doublets:
        data = {lemma: {feats: form.pop() for feats, form in datum.items() if len(form) == 1} for lemma, datum in
                data.items()}
    else:
        lens = {k: {kk: len(vv) for kk, vv in d.items()} for k, d in data.items()}
        flat_lens = [l for d in lens.values() for l in d.values() if l > 1]
        max_len = {k: max(d.values()) for k, d in lens.items()}
        print(f'for {os.path.basename(path)}:\n'
              f'{len([v for v in max_len.values() if v > 1])} lemmas have double forms.\n'
              f'all in all {len(flat_lens)} double forms')
    return data


def write_data(lemma_done: list, new_table: dict, dir_data, language="fr"):
    with open(dir_data, 'w', encoding='utf8') as f:
        for lemma in lemma_done:
            for feats, form in new_table[lemma].items():
                line = '\t'.join([lemma, form, feats])+'\n'
                line = line.replace('??', '?')
                f.write(line)
    print(dir_data, " written")


if __name__ == '__main__':
    unimorph_dir = 'unimorph'

    new_table = {}
    # get unimorph
    table = read_unimorph("unimorph") # 19938 uniq lemma in unimporh in French
    # get order
    sorted_lemmas = freq_sort("fasttext")

    # sort unimorph lemmas
    sorted_set = set(sorted_lemmas)
    lemmas_to_do = {lemma for lemma in table.keys() if lemma in sorted_set}
    lemmas_to_do = sorted(lemmas_to_do, key=lambda lemma: sorted_lemmas.index(lemma))


    # load leff properties and PP derivation table
    with open("/Users/bemuller/Documents/Work/INRIA/dev/mighty_morph_tagging_tool/leff-extract/cases.json") as read:
        features = json.load(read)

    #for v in features:
        #if len(features[v]) == 1:

            #if "r" in list(features[v].keys())[0]:
                #print("features[v][0]", v, features[v])
            #    breakpoint()
    #breakpoint()
    with open("/Users/bemuller/Documents/Work/INRIA/dev/mighty_morph_tagging_tool/leff-extract/derivation_pp.json") as read:
        pp = json.load(read)

    # get property
    lemmas_done = []
    new_table = {}
    skipping = []
    MAX_LEMMAS, count_two_aux_verb = 500, 0
    lemmas_to_do = lemmas_to_do[:MAX_LEMMAS]
        # fixing accent problem
    for lemma in tqdm(lemmas_to_do, total=len(lemmas_to_do)):
        lemma_leff = lemma
        if lemma in ["connaitre", "reconnaitre", "diner", "apparaitre",  "paraitre", "entrainer", "abimer", "déboiter", "repaitre"]:
            lemma_leff = lemma.replace("i", "î")
        elif lemma == "arreter":
            lemma_leff = "arrêter"
        elif lemma == "designer":
            lemma_leff = "désigner"
        elif lemma == "rafraichir":
            lemma_leff = "rafraîchir"
        elif lemma == "disparaitre":
            lemma_leff = "disparaître"
        elif lemma == "pecher":
            lemma_leff = "pêcher"
        elif lemma == "representer":
            lemma_leff = "représenter"
        elif lemma == "desirer":
            lemma_leff = "désirer"
        elif lemma == "referer":
            lemma_leff = "référer"
        elif lemma == "detester":
            lemma_leff = "détester"
        elif lemma == "resigner":
            lemma_leff = "résigner"
        elif lemma == "penetrer":
            lemma_leff = "pénétrer"
        elif lemma == "alterer":
            lemma_leff = "altérer"

        elif lemma in ["jeuner", "murir", "envouter"]:
            lemma_leff = lemma.replace("u", "û")

        #if lemma in ["falloir", "valoir", "béer"]:
        if lemma in ["béer"]:
            log = f"Skipping {lemma} because pp table empty in "
            # actually because there are both actif_impersonnel --> so should be fixed after this
            print(log)
            skipping.append(lemma)
            continue
        try:
            responses = features[lemma_leff].keys()
            _pp = pp[lemma_leff]
        except:
            log = ""
            if lemma not in features:
                log = f"Missing lemma {lemma} in lefff cases \n"
            if lemma not in pp:
                log += f"Missing lemma {lemma} in aux table \n"
            print(log)
            skipping.append(lemma)
            continue

        lemma_has_two_aux = False
        for _response in responses:
            features[lemma_leff][_response] = list(set(features[lemma_leff][_response]))
            if len(features[lemma_leff][_response]) > 1:
                assert len(features[lemma_leff][_response]) == 2
                lemma_has_two_aux = True

        if lemma_has_two_aux:
            print("TWO AUX LEMMA")
            feature_dic_etre = {case: ls_aux for case, ls_aux in features[lemma_leff].items() if "e" in ls_aux}
            feature_dic_etre = {case: ["e"] for case in feature_dic_etre}

            _new_table = create_new_table(feature_dic_etre.keys(), table[lemma], aux_dic=feature_dic_etre, ptcp_pst_table=_pp)
            new_table[f'être {lemma}'] = _new_table
            lemmas_done.append(f'être {lemma}')

            feature_dic_avoir = {case: ls_aux for case, ls_aux in features[lemma_leff].items() if "a" in ls_aux}
            feature_dic_avoir = {case: ["a"] for case in feature_dic_avoir}

            _new_table = create_new_table(feature_dic_avoir.keys(), table[lemma], aux_dic=feature_dic_avoir, ptcp_pst_table=_pp)
            new_table[f'avoir {lemma}'] = _new_table
            lemmas_done.append(f'avoir {lemma}')
            count_two_aux_verb += 1

        else:
            _new_table = create_new_table(responses, table[lemma], aux_dic=features[lemma_leff], ptcp_pst_table=_pp)
            new_table[lemma] = _new_table
            lemmas_done.append(lemma)
        if VERBOSE:
            print(f"{i} {lemma} done ({count_two_aux_verb} two aux verbs)")
    write_data(lemmas_done, new_table, os.path.join('mighty_morph', f'{language}-w_leff-TEST.txt'))
    print(f"Skipped {skipping} : {len(lemmas_done)-len(skipping)}/{len(lemmas_done)} lemma derived at the clause-level, {100-len(skipping)/len(lemmas_done)*100:0.2f}% coverage rate ")


