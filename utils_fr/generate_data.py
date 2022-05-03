import os
import json
import re

language = 'fr'


person_number = {'1;SG', '1;PL', '2;SG', '2;PL', '3;SG;MASC', '3;SG;FEM',  '3;PL;MASC', '3;PL;FEM'}#,  '3;PL;NEUT','3;SG;NEUT',}


nom_prons = {'1;SG': 'je',#'1;SG;MASC': 'je', '1;SG;FEM': 'je',
             '1;PL': 'nous', '2;SG': 'tu', '2;PL': 'vous', '3;SG;MASC': 'il', '3;SG;FEM': 'elle',  '3;PL;MASC':'ils', '3;PL;FEM': 'elles'}#,  '3;PL;NEUT':'ce', '3;SG;NEUT':'cela'}

acc_prons = {'1;SG': 'me', '1;PL': 'nous', '2;SG': 'te', '2;PL': 'vous', '3;SG;MASC': 'le', '3;SG;FEM': 'la',  "3;PL": "les"}#, "3;PL": "les"} # NB: "3;PL;MASC": "les" and "3;PL;FEM" could be normalized to "3;PL" (but then must handle acc_prons[pn] errors)

dat_prons = {'1;SG': 'me', '1;PL': 'nous', '2;SG': 'te', '2;PL': 'vous', '3;SG;MASC': 'lui', '3;SG;FEM': 'lui', '3;PL': 'leur'}# '3;PL;MASC':'leur', '3;PL;FEM':'leur'}

reflex_prons = {'1;SG': 'me', '1;PL': 'nous', '2;SG': 'te', '2;PL': 'vous', '3;SG': 'se', '3;PL': 'se'}# '3;PL;MASC':'leur', '3;PL;FEM':'leur'}

loc_pron = {'3;SG;NEUT': 'y'}  # --> '3;PL;MASC':'leur', '3;PL;FEM':'leur'}

gen_pron = {'3;SG;NEUT': 'en'}

prepos_prons = {'a': acc_prons, 'd': dat_prons, 'l': loc_pron, "g": gen_pron, "r": reflex_prons}

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

cases = {'a': 'ACC', 'd': 'DAT', 'l': 'LOC', 'g': 'GEN', "r": "RFLX"
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
            # pronoun subject list
                #[nom_prons[pron_subject_feat] for _ in GET_LEFF_PP[pron_subject_feat]],
            # pronoun list features SUBJET
                [f'{pron_subject_feat[0]};{feature}' for feature in GET_LEFF_PP[pron_subject_feat]],
            # pronoun list ARGUMENT
                #None if pron_argument_feat is None else [f'{pron_argument_feat[0]}:{feature}' for feature in GET_LEFF_PP[pron_argument_feat]],
            # pronoun list features ARGUMENT
                #BUG: ? None if pron_argument_feat is None else [f'{pron_argument_feat[0]};{feature}' for feature in GET_LEFF_PP[pron_argument_feat]] --> the argument is not expanded cause do not impact the pp
                None if pron_argument_feat is None else [f'{pron_argument_feat}' for _ in GET_LEFF_PP[pron_subject_feat]]
                #[f'{pron_argument_feat[0]}:{feature}' for feature in GET_LEFF_PP[pron_argument_feat]]
                )

    elif aux == "a":
        if case[0] == "a":
            # we agree the past participle with the 'pronom complément'
            # we know that the COD will be before the verb --> the argument needs to agree with the accusatif prono,
            try:
                #breakpoint()
                #table['V;NFIN']
                return (
                    [table_leff[aggrement] for aggrement in GET_LEFF_PP[pron_argument_feat]],
                    #BUG?[f'{pron_subject_feat[0]};{feature}' for feature in GET_LEFF_PP[pron_subject_feat]],
                    [pron_subject_feat for _ in  GET_LEFF_PP[pron_argument_feat]], # subject feat is not expanded cause the agreement will be with the argument
                    None if pron_argument_feat is None else [f'{pron_argument_feat[0]};{feature}' for feature in GET_LEFF_PP[pron_argument_feat]]
                )
            except:
                print(f"Warning: could not do the agreement for aux avoir , verb {ptcp_pst}")
                breakpoint()
                return ([ptcp_pst], [pron_subject_feat], [pron_argument_feat])

        else:

            return ([ptcp_pst], [pron_subject_feat], [pron_argument_feat])
    else:
        raise (Exception("aux not defined"))


def append_declarative_sent(new_table, seed_full_feature, form, subject, case, seed_full_form,_pron_feat=None, pron=None, aux=None):
    # features
    if case in ["a", "d", "l", "g", "r"]:
        assert pron is not None
        full_feature = seed_full_feature + f"{cases[case]}({_pron_feat});"
    elif case == "0":
        full_feature = seed_full_feature
    else:
        raise(Exception(f"case {case} not supported"))

    # forms

    if aux is None:
        pron, subject = phonological_constrain_pronons(pron=pron, form=form, type=case, subject=subject)
    else:
        pron, subject = phonological_constrain_pronons(pron=pron, form=aux, type=case, subject=subject)
    if pron.strip() in ["en", "y"] and subject.strip() == "je":
        subject = "j'"
    new_table[full_feature] = f"{seed_full_form}{subject}{pron}{aux+' ' if aux is not None else ''}{form}."


def append_question(new_table, _pron_feat, seed_full_feature, form, subject, case, seed_full_form, pron=None, aux=None):

    # features
    if case in ["a", "d", "l", "g", "r"]:
        assert pron is not None
        full_feature = seed_full_feature + f"{cases[case]}({_pron_feat});"
    elif case == "0":
        full_feature = seed_full_feature
    else:
        raise(Exception(f"case {case} not supported"))
    full_feature += "Q"

    # form
    if aux is None:
        # le dites?
        pron, subject = phonological_constrain_pronons(pron=pron, form=form, type=case, subject=subject)
        full_form = f"{seed_full_form}{pron}{form}{get_question_phonological_link(before_subject=form, subject=subject, case=case)}{subject} ?"
    else:
        pron, subject = phonological_constrain_pronons(pron=pron, form=aux, type=case, subject=subject)
        full_form = f"{seed_full_form}{pron}{aux}{get_question_phonological_link(before_subject=aux, subject=subject, case=case)}{subject} {form} ?"

    new_table[full_feature] = full_form


def append_negation(new_table,  _pron_feat, seed_full_feature, form, subject, case, seed_full_form,  pron=None, aux=None):

    # feature
    if case in ["a", "d", "l", "g", "r"]:
        assert pron is not None
        full_feature = seed_full_feature + f"{cases[case]}({_pron_feat});"
    elif case == "0":
        full_feature = seed_full_feature
    else:
        raise(Exception(f"case {case} not supported"))
    full_feature += "NEG"
    # forms

    if aux is None:
        pron, subject = phonological_constrain_pronons(pron=pron, form=form, type=case, subject=subject)
        full_form = f"{seed_full_form}{subject}{get_ne(pron=pron,type=case, form=form)}{pron}{form} pas."
    else:
        pron, subject = phonological_constrain_pronons(pron=pron, form=aux, type=case, subject=subject)
        full_form = f"{seed_full_form}{subject}{get_ne(pron=pron, type=case,form=aux)}{pron}{aux + ' ' if aux is not None else ''}pas {form}."

    new_table[full_feature] = full_form


def append_question_and_negation(new_table, _pron_feat, seed_full_feature, form, subject, case, seed_full_form, pron=None, aux=None):
    # feature
    if case in ["a", "d", "l", "g", "r"]:
        assert pron is not None
        full_feature = seed_full_feature + f"{cases[case]}({_pron_feat});"
    elif case == "0":
        full_feature = seed_full_feature
    else:
        raise(Exception(f"case {case} not supported"))
    full_feature += "NEG;Q"
    # form
    if aux is None:
        pron, subject = phonological_constrain_pronons(pron=pron, form=form, type=case, subject=subject)
        full_form = f"{seed_full_form}{get_ne(pron=pron, type=case, form=form)}{pron}{form}{get_question_phonological_link(before_subject=form, subject=subject, case=case)}{subject}pas ?"
    else:
        pron, subject = phonological_constrain_pronons(pron=pron, form=aux, type=case, subject=subject)
        full_form = f"{seed_full_form}{get_ne(pron=pron, type=case, form=aux)}{pron}{aux}{get_question_phonological_link(before_subject=aux, subject=subject, case=case)}{subject}pas {form} ?"
    new_table[full_feature] = full_form


def append_4_types_of_sentences(new_table, _pron_feat, seed_full_feature, form, subject, case, seed_full_form, pron=None, aux=None):
    append_declarative_sent(new_table=new_table, _pron_feat=_pron_feat, seed_full_feature=seed_full_feature, form=form,
                            subject=subject, case=case, seed_full_form=seed_full_form,
                            pron=pron, aux=aux)
    append_question(new_table=new_table, _pron_feat=_pron_feat, seed_full_feature=seed_full_feature, form=form,
                    subject=subject, case=case, seed_full_form=seed_full_form,
                    pron=pron, aux=aux)
    append_negation(new_table=new_table, _pron_feat=_pron_feat, seed_full_feature=seed_full_feature, form=form,
                    subject=subject, case=case, seed_full_form=seed_full_form,
                     pron=pron, aux=aux)
    append_question_and_negation(new_table=new_table, _pron_feat=_pron_feat, seed_full_feature=seed_full_feature,
                                 form=form, subject=subject, case=case, seed_full_form=seed_full_form,
                                 pron=pron, aux=aux)


def append_declarative_sent_bi_pron(new_table, seed_full_feature, form, subject, case, seed_full_form,
                                    _pron_feat_0=None, pron_0=None, _pron_feat_1=None, pron_1=None,
                                    aux=None):
    # features

    assert len(case) == 2

    full_feature = seed_full_feature + f"{cases[case[0]]}({_pron_feat_0});"+ f"{cases[case[1]]}({_pron_feat_1});"

    pron_pairs, tonique_1 = two_pronouns_order_and_phonological_constrains(_pron_feat_0=_pron_feat_0,
                                                                           _pron_feat_1=_pron_feat_1,
                                                                           pron_0=pron_0,
                                                                           pron_1=pron_1, form=aux if aux is not None else form,
                                                                           type=case)

    if aux is None:
        new_table[full_feature] = f"{seed_full_form}{subject} {pron_pairs}{form}{tonique_1}."
    else:
        new_table[full_feature] = f"{seed_full_form}{subject} {pron_pairs}{aux + ' '}{form}{tonique_1}."


def append_question_sent_bi_pron(new_table, seed_full_feature, form, subject, case, seed_full_form,
                                 _pron_feat_0=None, pron_0=None, _pron_feat_1=None, pron_1=None, aux=None):
    # features

    assert len(case) == 2

    full_feature = seed_full_feature + f"{cases[case[0]]}({_pron_feat_0});" + f"{cases[case[1]]}({_pron_feat_1});"
    full_feature += "Q"

    pronon_pairs, tonique_1 = two_pronouns_order_and_phonological_constrains(pron_0=pron_0, pron_1=pron_1,
                                                                             _pron_feat_0=_pron_feat_0,
                                                                             _pron_feat_1=_pron_feat_1,
                                                                             form=aux if aux is not None else form,
                                                                             type=case)
    if aux is None:
        new_table[full_feature] = f"{seed_full_form}{pronon_pairs}{form}{get_question_phonological_link(before_subject=form, subject=subject, case=case)}{subject}{tonique_1} ?"
    else:
        new_table[full_feature] = f"{seed_full_form}{pronon_pairs}{aux}{get_question_phonological_link(before_subject=aux, subject=subject, case=case)}{subject} {form}{tonique_1} ?"


def append_neg_sent_bi_pron(new_table, seed_full_feature, form, subject, case, seed_full_form, _pron_feat_0=None,
                            pron_0=None, _pron_feat_1=None, pron_1=None, aux=None):
    # features
    assert len(case) == 2

    full_feature = seed_full_feature + f"{cases[case[0]]}({_pron_feat_0});" + f"{cases[case[1]]}({_pron_feat_1});"
    full_feature += "NEG"

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


def append_question_negation_sent_bi_pron(new_table, seed_full_feature, form, subject, case, seed_full_form,
                                          _pron_feat_0=None, pron_0=None, _pron_feat_1=None, pron_1=None, aux=None):
    # features

    assert len(case) == 2

    full_feature = seed_full_feature + f"{cases[case[0]]}({_pron_feat_0});" + f"{cases[case[1]]}({_pron_feat_1});"
    full_feature += "NEG;Q"
    pronon_pairs, tonique_1 = two_pronouns_order_and_phonological_constrains(pron_0=pron_0, pron_1=pron_1,
                                                                  _pron_feat_0=_pron_feat_0,
                                                                  _pron_feat_1=_pron_feat_1,
                                                                  form=aux if aux is not None else form,
                                                                  type=case)

    if aux is None:
        new_table[full_feature] = f"{seed_full_form}{get_ne(pron=_pron_feat_0,type=case, form=form)}{pronon_pairs}{form}{get_question_phonological_link(before_subject=form, subject=subject, case=case)}{subject} pas{tonique_1} ?"
    else:
        new_table[full_feature] = f"{seed_full_form}{get_ne(pron=_pron_feat_0,type=case, form=form)}{pronon_pairs}{aux}{get_question_phonological_link( before_subject=aux, subject=subject, case=case)}{subject} pas {form}{tonique_1} ?"


def append_4_types_of_sentences_two_pron(new_table, seed_full_feature, form, subject, case, seed_full_form,
                                    _pron_feat_0=None, pron_0=None, _pron_feat_1=None, pron_1=None,
                                    aux=None):
    append_declarative_sent_bi_pron(new_table, seed_full_feature, form, subject, case, seed_full_form,
                                    _pron_feat_0=_pron_feat_0, pron_0=pron_0, _pron_feat_1=_pron_feat_1, pron_1=pron_1,
                                    aux=aux)
    append_question_sent_bi_pron(new_table, seed_full_feature, form, subject, case, seed_full_form,
                                    _pron_feat_0=_pron_feat_0, pron_0=pron_0, _pron_feat_1=_pron_feat_1, pron_1=pron_1,
                                    aux=aux)
    append_neg_sent_bi_pron(new_table, seed_full_feature, form, subject, case, seed_full_form,
                                 _pron_feat_0=_pron_feat_0, pron_0=pron_0, _pron_feat_1=_pron_feat_1, pron_1=pron_1,
                                 aux=aux)
    append_question_negation_sent_bi_pron(new_table, seed_full_feature, form, subject, case, seed_full_form,
                                          _pron_feat_0=_pron_feat_0, pron_0=pron_0, _pron_feat_1=_pron_feat_1, pron_1=pron_1,
                                          aux=aux)


def get_question_phonological_link(before_subject, subject, case):
    if case in ["a", "d", "l", "0", "g", "l", "r", "ag", "dg", "al", "ad", "rl", "rg"]:
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
        if type in ["al", "ag", "rl", "rg"]:
            if pron_0 in ["toi", "moi"] and pron_1 in ["en", "y"]:
                return pron_0[:-2] + "'" + pron_1 + " ", tonique_1
            if re.match(".*[aeiou]$", pron_0) and re.match("^[aeiouyhéêh].*", pron_1):
                return pron_0[:-1] + "'" + pron_1 + " ", tonique_1
        elif type in ["dg"]:
            if pron_0 in ["toi", "moi"] and pron_1 in ["en", "y"]:
                # might be able to factorize with if pron_0 in ["toi", "moi"] and pron_1 in ["en", "y"]: above
                return pron_0[:-2] + "'" + pron_1 + " ", tonique_1
            if re.match(".*[aeiou]$", pron_0) and re.match("^[aeiouyhéêh].*", pron_1) and pron_0 not in ["lui"]:
                return pron_0[:-1] + "'" + pron_1 + " ", tonique_1

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

    for _response in responses:
        aux_dic[_response] = list(set(aux_dic[_response]))
        if len(aux_dic[_response]) > 1:
            print(f"Warning: two aux for verb {nfin}")

    # if len(set(aux_dic[_response])) > 1:
    # print(f"Warning: Several {aux} in {set(aux_dic[_response])} for {nfin} cas {_response}")
    for mood in moods:
        for tense in tenses:
            # TODO: if else no IMPERATIVE : no future
            for i, aspect in enumerate(aspects):
                # TODO: ifelse
                if tense != "PST" and i > 0:
                    # only going through the tensexmood one (cause aspect do not impact present and future)
                    continue
                for pn in person_number:
                    #
                    pers = ";".join(pn.split(";")[:2])
                    unimorph_match = f"V;{mood};{tense};{pers}"

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
                    except:
                        print(f"{unimorph_match} not found in unimoprh {table}")
                        continue

                        # print(f"form {form} working for {unimorph_match}")

                    # Type of clause: affirmative, interrogative, negative, negative interrogative

                    # affirmative
                    if tense == "PST":
                        if aspect == "PFV":
                            tense_feature = f'{tense}:LGSPEC1'
                        elif aspect == "IPFV":
                            tense_feature = f'{tense};IPFV'
                    else:
                        tense_feature = tense

                    for _response in responses:
                        aux_dic[_response] = list(set(aux_dic[_response]))
                        for i, aux in enumerate(aux_dic[_response]):
                            AUX = aux+";"
                            #if len(set(aux_dic[_response])) > 1:
                                #print(f"Warning: Several {aux} in {set(aux_dic[_response])} for {nfin} cas {_response}")

                            # cases
                            if _response not in ["a", "d", "l", "g", "0", "r", "ad", "al", "ag", "dg", "rl", "rg"]:
                                print("Skipping ", _response)
                                continue

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

                                    full_feature = f"{AUX}{mood};{tense_feature};NOM({pn});"

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
                                            seed_full_feature = f"{AUX}IND;FUT;PFV;NOM({pn_feat_subject});"

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
                                            seed_full_feature = f"{AUX}IND;PST;NOM({pn_feat_subject});"
                                            append_4_types_of_sentences(new_table, _pron_feat=None,
                                                                        seed_full_feature=seed_full_feature,
                                                                        seed_full_form=seed_full_form,
                                                                        case=_response, subject=nom_prons[pn],
                                                                        form=ptcp_pst, pron=None, aux=aux_form)
                                            if VERBOSE:
                                                print(f"{nfin}\t{full_form}\t{full_feature}")

                                            # past-perfect / plus que parfait --> imparfait
                                            aux_form = auxiliary_dict[aux]["IND;PST;IPFV"][pers]
                                            seed_full_feature = f"{AUX}IND;PST;PFV;NOM({pn_feat_subject});"
                                            append_4_types_of_sentences(new_table, _pron_feat=None,
                                                                        seed_full_feature=seed_full_feature,
                                                                        seed_full_form=seed_full_form,
                                                                        case=_response, subject=nom_prons[pn],
                                                                        form=ptcp_pst, pron=None, aux=aux_form)
                                            if VERBOSE:
                                                print(f"{nfin}\t{full_form}\t{full_feature}")

                                            # passé antérieur --> passé simple
                                            aux_form = auxiliary_dict[aux]["IND;PST;PFV;LGSPEC1"][pers]
                                            seed_full_feature = f"{AUX}IND;PST;PFV;LGSPEC1;NOM({pn_feat_subject});"
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
                                            seed_full_feature = f"{AUX}COND;PFV;NOM({pn_feat_subject});"
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
                                        if _response[0] == "r" and ";".join(_pron_feat_0.split(";")[:2]) != ";".join(pn.split(";")[:2]):
                                            # in reflexive cases: only "je me..., tu te... "
                                            continue

                                        seed_full_feature = f"{mood};{tense_feature};NOM({pn});"
                                        seed_full_form = ""

                                        # SIMPLE TENSES
                                        if mood == "IMP":
                                            if (pn == "1;PL" and _pron_feat_0 == "2;SG") or (pn == "1;PL" and _pron_feat_0 == "2;PL"):
                                                continue

                                            _pron_imperatif_0 = imperatif_pronouns(_pron_0, type=_response[0])
                                            _pron_imperatif_1 = imperatif_pronouns(_pron_1, type=_response[1])
                                            _pron_imperatif, tonique_1 = two_pronouns_order_and_phonological_constrains(_pron_feat_0=_pron_feat_0, _pron_feat_1=_pron_feat_1, pron_0=_pron_imperatif_0, pron_1=_pron_imperatif_1, form=form, type=_response, mood=mood)

                                            #full_form = seed_full_form + f"{form}-{get_order_pronon_imp_decl( _pron_imperatif_0, _pron_imperatif_1)} !"
                                            full_form = seed_full_form + f"{form}-{_pron_imperatif}{tonique_1}!"
                                            full_feature = seed_full_feature + f"{cases[_response[0]]}({_pron_feat_0});" + f"{cases[_response[1]]}({_pron_feat_1});"
                                            new_table[full_feature] = full_form
                                            full_feature = seed_full_feature + f"{cases[_response[0]]}({_pron_feat_0});" + f"{cases[_response[1]]}({_pron_feat_1});NEG;"
                                            #full_form = seed_full_form + f"{get_ne(_pron_0, type=_response, form=form)}{get_order_pronon(_pron_0, _pron_1)} {form} pas !"
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
                                        #if _response[0] == "a":
                                        #    breakpoint()
                                        for pn_feat_subject, pn_feat_arg_0, ptcp_pst in zip(pn_ls, pn_feat_argument_0_ls, ptcp_pst_ls):
                                            seed_full_form = ""

                                            if (pn == "1;PL" and _pron_feat_0 == "1;SG") or (pn == "2;PL" and _pron_feat_0 == "2;SG") or (pn == "2;SG" and _pron_feat_0 == "2;PL"):
                                                continue

                                            if mood == "IND":
                                                if tense == "FUT":
                                                    # get FUT --> get future
                                                    aux_form = auxiliary_dict[aux]["IND;FUT"][pers]
                                                    seed_full_feature = f"{AUX}IND;FUT;PFV;NOM({pn_feat_subject});"

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
                                                    seed_full_feature = f"{AUX}IND;PST;NOM({pn_feat_subject});"

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
                                                    seed_full_feature = f"{AUX}IND;PST;PFV;NOM({pn_feat_subject});"

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
                                                    seed_full_feature = f"{AUX}IND;PST;PFV;LGSPEC1;NOM({pn_feat_subject});"

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
                                                    seed_full_feature = f"{AUX}COND;PFV;NOM({pn_feat_subject});"

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
                                    if _response == "r" and ";".join(_pron_feat.split(";")[:2]) != ";".join(pn.split(";")[:2]):
                                        # in reflexive cases: only "je me..., tu te... "
                                        continue
                                    seed_full_feature = f"{mood};{tense_feature};NOM({pn});"
                                    seed_full_form = ""

                                    if mood == "IMP":

                                        if (pn == "1;PL" and _pron_feat == "2;SG") or \
                                                (pn == "1;PL" and _pron_feat == "2;PL"):
                                            # TODO: fact check this
                                            continue
                                        _pron_imperatif = imperatif_pronouns(_pron, type=_response)
                                        full_form = seed_full_form + f"{form}-{_pron_imperatif} !"
                                        full_feature = seed_full_feature + f"{cases[_response]}({_pron_feat});"
                                        new_table[full_feature] = full_form
                                        full_feature = seed_full_feature + f"{cases[_response]}({_pron_feat});NEG;"

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
                                                seed_full_feature = f"{AUX}IND;FUT;PFV;NOM({pn_feat_subject});"
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
                                                seed_full_feature = f"{AUX}IND;PST;NOM({pn_feat_subject});"
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
                                                seed_full_feature = f"{AUX}IND;PST;PFV;NOM({pn_feat_subject});"

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
                                                seed_full_feature = f"{AUX}IND;PST;PFV;LGSPEC1;NOM({pn_feat_subject});"

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
                                                seed_full_feature = f"{AUX}COND;PFV;NOM({pn_feat_subject});"

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


def write_data(lemma_done: list, new_table: dict, language="fr"):
    with open(os.path.join('mighty_morph', f'{language}-w_leff.txt'), 'w', encoding='utf8') as f:
        for lemma in lemma_done:
            for feats, form in new_table[lemma].items():
                line = '\t'.join([lemma, form, feats])+'\n'
                line = line.replace('??', '?')
                f.write(line)
    print(os.path.join('mighty_morph', f'{language}-w_leff.txt'), " written")


if __name__ == '__main__':
    unimorph_dir = 'unimorph'

    new_table = {}
    # get unimorph
    table = read_unimorph("unimorph")
    # get order
    sorted_lemmas = freq_sort("fasttext")
    # sort unimorph lemmas
    sorted_set = set(sorted_lemmas)
    lemmas_to_do = {lemma for lemma in table.keys() if lemma in sorted_set}
    lemmas_to_do = sorted(lemmas_to_do, key=lambda lemma: sorted_lemmas.index(lemma))

    # load leff properties and PP derivation table
    with open("/Users/bemuller/Documents/Work/INRIA/dev/mighty_morph_tagging_tool/leff-extract/cases.json") as read:
        features = json.load(read)
    with open("/Users/bemuller/Documents/Work/INRIA/dev/mighty_morph_tagging_tool/leff-extract/derivation_pp.json") as read:
        pp = json.load(read)


    # get property
    lemmas_done = []
    new_table = {}
    skipping = []
    for i, lemma in enumerate(lemmas_to_do):
        if lemma in ["falloir", "valoir"]:
            log = f"Skipping {lemma} because 'aux' matching pb in unimorph or empty leff table"
            print(log)
            skipping.append(log)
            continue
        try:
            responses = features[lemma].keys()
            _pp = pp[lemma]
        except:

            log= f"Missing lemma {lemma} in leff cases or leff auxilliary"
            print(log)
            skipping.append(log)
            continue
        if i > 600:
            break
        #if len(responses) == 0:
        #    responses.append("0")
        _new_table = create_new_table(responses, table[lemma], aux_dic=features[lemma], ptcp_pst_table=_pp)
        new_table[lemma] = _new_table
        lemmas_done.append(lemma)
        print(f"{i} {lemma} done")
    write_data(lemmas_done, new_table)
    print(f"Skipped {skipping} out of {len(lemmas_done)}")
    print(lemmas_done)




    