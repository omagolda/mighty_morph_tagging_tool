import os
import json
import re

language = 'fr'


person_number = {'1;SG', '1;PL', '2;SG', '2;PL', '3;SG;MASC', '3;SG;FEM',  '3;PL;MASC', '3;PL;FEM'}#,  '3;PL;NEUT','3;SG;NEUT',}


nom_prons = {'1;SG': 'je', '1;PL': 'nous', '2;SG': 'tu', '2;PL': 'vous', '3;SG;MASC': 'il', '3;SG;FEM': 'elle',  '3;PL;MASC':'ils', '3;PL;FEM': 'elles'}#,  '3;PL;NEUT':'ce', '3;SG;NEUT':'cela'}

acc_prons = {'1;SG': 'me', '1;PL': 'nous', '2;SG': 'te', '2;PL': 'vous', '3;SG;MASC': 'le', '3;SG;FEM': 'la',  "3;PL;MASC": "les", "3;PL;FEM": "les"} # NB: "3;PL;MASC": "les" and "3;PL;FEM" could be normalized to "3;PL" (but then must handle acc_prons[pn] errors)

dat_prons = {'1;SG': 'me', '1;PL':'nous', '2;SG': 'te', '2;PL': 'vous', '3;SG;MASC': 'lui', '3;SG;FEM': 'lui', '3;PL': 'leur'}# '3;PL;MASC':'leur', '3;PL;FEM':'leur'}


prepos_prons = {'a': acc_prons,'d': dat_prons}

# reflexive_pronouns = {'1;SG': 'me', '1;PL':'nous', '2;SG': 'te', '2;PL': 'vous', '3;SG': 'se', '3;PL': 'se'}# https://francais.lingolia.com/en/grammar/pronouns/reflexive-pronouns#:~:text=The%20French%20reflexive%20pronouns%20are,English%20words%20myself%2C%20yourself%20etc.

# OTHER ONES: https://pollylingu.al/fr/en/cases : DISJUNCTIF? GENITIF?

# Complément du nom??
#gen_prons = {'1;SG': 'meiner', '1;PL': 'unser', '2;SG': 'deiner', '2;PL': 'euer', '3;SG;MASC': 'seiner', '3;SG;FEM': 'ihrer', '3;SG;NEUT': 'seiner', '3;PL': 'ihrer', '2;FRML': 'Ihrer '}

# tonique https://parlez-vous-french.com/les-pronoms-toniques-en-francais/
tonique_pronouns = {'1;SG': 'moi', '1;PL':'nous', '2;SG': 'toi', '2;PL': 'vous', '3;SG;MASC': 'lui', '3;SG;FEM': 'elle',  '3;PL;MASC':'eux', '3;PL;FEM':'elles'}

reflex_prons = {'1,SG': 'myself', '1,PL': 'ourselves', '2,SG': 'yourself', '2,PL': 'yourselves', '3,SG,MACS': 'himself', '3,SG,FEM': 'herself', '3,SG,NEUT': 'itself', '3,PL': 'themselves'}

prepos = {'a': '', 'd': 'à', 'c': 'avec', 'g': 'of', 'b': 'from', 'f': 'for', 'l': 'on', 's': 'at', 't': 'about', 'i': 'in'}

moods = ['IND', 'IMP', "COND"]
tenses = {'PST', 'PRS', 'FUT'}
aspects = {#'SIMP', 'PROG',
           'PFV', 'IPFV'}
# NEG, Q, PASS
have = {'pst': 'had', 'prs': 'have', 'prs3sg': 'has', 'fut': 'will have'}

be = {'v3': 'been', 'fut': 'will be',
      'PST,1,SG': 'was', 'PST,1,PL': 'were', 'PST,2': 'were', 'PST,3,SG': 'was', 'PST,3,PL': 'were',
      'PRS,1,SG': 'am', 'PRS,1,PL': 'are', 'PRS,2': 'are', 'PRS,3,SG': 'is', 'PRS,3,PL': 'are'}

dicts = [nom_prons, acc_prons, reflex_prons, prepos, have, be]
non_lemma_words = set().union(*[set(dicto.values()) for dicto in dicts])
non_lemma_words |= {'will', "don't", 'do', 'be', 'would', 'not', 'did', "didn't", 'does', "doesn't", '?', "I'm", "you're",
                    "we're", "they're", "he's", "she's","it's","haven't","hasn't","hadn't","wouldn't","won't","wasn't","weren't",
                    "I've","you've","we've","they've","I'd","you'd","we'd","they'd","he'd","she'd","I'll","you'll","we'll",
                    "they'll","he'll","she'll","it'll"}

cases = {'a': 'ACC', 'd': 'DAT', #'c': 'COM',
         #'g': 'GEN'
         }#, 'b': 'ABL', 'f': 'BEN', 'l': 'ON', 's': 'AT', 't': 'CIRC', 'i': 'LOC'}

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


def append_declarative_sent(new_table, _pron_feat, seed_full_feature, form, subject, case, seed_full_form, pron=None, aux=None):
    if case in ["a", "d"]:
        assert pron is not None
        full_feature = seed_full_feature + f"{cases[case]}({_pron_feat})"

    new_table[full_feature] = f"{seed_full_form}{subject} {pron}{aux+' ' if aux is not None else ''}{form}"


def append_question(new_table, _pron_feat, seed_full_feature, form, subject, case, seed_full_form, pron=None, aux=None):
    full_feature = seed_full_feature + f"{cases[case]}({_pron_feat});Q"
    if case in ["a", "d"]:
        assert pron is not None
        if aux is None:
            # le dites?
            full_form = f"{seed_full_form}{pron}{form} {subject}?"
        else:
            full_form = f"{seed_full_form}{pron}{aux} {subject} {form}?"

    new_table[full_feature] = full_form


def append_negation(new_table, _pron_feat, seed_full_feature, form, subject, case, seed_full_form, pron=None, aux=None):
    if case in ["a", "d"]:
        assert pron is not None
        full_form = f"{seed_full_form}{subject} ne {pron}{aux + ' ' if aux is not None else ''}{form} pas"
    full_feature = seed_full_feature + f"{cases[case]}({_pron_feat});NEG"
    new_table[full_feature] = full_form


def append_question_and_negation(new_table, _pron_feat, seed_full_feature, form, subject, case, seed_full_form, pron=None, aux=None):
    if case in ["a", "d"]:
        assert pron is not None
        if aux is None:
            full_form = f"{seed_full_form}ne {pron}{form} {subject} pas?"
        else:
            full_form = f"{seed_full_form}ne {pron}{aux} {subject} pas {form}?"
    full_feature = seed_full_feature + f"{cases[case]}({_pron_feat});NEG;Q"
    new_table[full_feature] = full_form



def append_4_types_of_questions(new_table, _pron_feat, seed_full_feature, form, subject, case, seed_full_form, pron=None, aux=None):
    append_declarative_sent(new_table, _pron_feat, seed_full_feature, form, subject, case, seed_full_form, pron=pron, aux=aux)
    append_question(new_table, _pron_feat, seed_full_feature, form, subject, case, seed_full_form,
                                 pron=pron, aux=aux)
    append_negation(new_table, _pron_feat, seed_full_feature, form, subject, case, seed_full_form,
                                 pron=pron, aux=aux)
    append_question_and_negation(new_table, _pron_feat, seed_full_feature, form, subject, case, seed_full_form,
                                 pron=pron, aux=aux)

def phonological_constrain_pronons(form, pron, type="a"):

    if type == "a":
        if re.match("^[aeiouyhéê].*", form) and re.match(".*[aeiou]$", pron):
            return pron[:-1]+"'"
        else:
            return pron+" "
    elif type == "d":
        if re.match("^[aeiouyhéê].*", form) and re.match(".*[aeiou]$", pron) and pron not in ["lui"]:
            return pron[:-1] + "'"
        else:
            return pron+" "
    elif type == "0":
        if re.match("^[aeiouyhéê].*", form) and pron in ["je"]:
            return pron[:-1] + "'"
        else:
            return pron + " "
    else:
        raise(f"Type case not supported {type}")


def imperatif_pronouns(pron, type="a"):

    if type == "a":
        if pron == "te":
            return "toi"
        elif pron == "me":
            return "moi"
        return pron
    else:
        raise(Exception(f"case {type} not supported "))


def create_new_table(responses, table, aux_dic):
    nfin = table['V;NFIN']

    ptcp_pst = table["V.PTCP;PST"]

    new_table = {}

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
                                # Imperfect only for first and second person: only keeping present
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

                        aux = aux_dic[_response][0]
                        if len(set(aux_dic[_response]))>1:
                            print(f"Warning: Picking {aux} in {set(aux_dic[_response])} for {nfin} ")

                        # cases
                        if _response not in ["a", "d"]:
                            continue
                        # INTRANSITIF VERBS
                        if _response == "0":

                            if mood == "IMP":

                                full_form = seed_full_form + f"{form}"
                                full_feature = f"{mood};{tense_feature};NOM({pn});"
                                new_table[full_feature] = full_form
                                if VERBOSE:
                                    print(f"{nfin}\t{full_form}\t{full_feature}")

                            else:
                                # SIMPLE
                                seed_full_form = ""
                                full_feature = f"{mood};{tense_feature};NOM({pn});"
                                _pn_writing = phonological_constrain_pronons(pron=nom_prons[pn], form=form,
                                                                             type=_response)
                                full_form = f"{_pn_writing}{form}"
                                new_table[full_feature] = full_form
                                if VERBOSE:
                                    print(f"{nfin}\t{full_form}\t{full_feature}")

                                # COMPOUND
                                if mood == "IND":
                                    if tense == "FUT":
                                        # get FUT --> get future
                                        aux_form = auxiliary_dict[aux]["IND;FUT"][pers]
                                        seed_full_feature = f"IND;FUT;PFV;NOM({pn});"
                                        full_feature = seed_full_feature
                                        _pron_writing_compound = phonological_constrain_pronons(pron=nom_prons[pn],
                                                                                                form=aux_form,
                                                                                                type=_response)
                                        full_form = seed_full_form + f"{_pron_writing_compound}{aux_form} {ptcp_pst}"
                                        new_table[full_feature] = full_form
                                        if VERBOSE:
                                            print(f"{nfin}\t{full_form}\t{full_feature}")

                                    elif tense == "PST":
                                        # present perfect / passé composé --> présent
                                        aux_form = auxiliary_dict[aux]["IND;PRS"][pers]
                                        seed_full_feature = f"IND;PST;NOM({pn});"
                                        full_feature = seed_full_feature
                                        _pron_writing_compound = phonological_constrain_pronons(pron=nom_prons[pn],
                                                                                                form=aux_form,
                                                                                                type=_response)
                                        full_form = seed_full_form + f"{_pron_writing_compound}{aux_form} {ptcp_pst}"
                                        new_table[full_feature] = full_form
                                        if VERBOSE:
                                            print(f"{nfin}\t{full_form}\t{full_feature}")

                                        # past-perfect / plus que parfait --> imparfait
                                        aux_form = auxiliary_dict[aux]["IND;PST;IPFV"][pers]
                                        seed_full_feature = f"IND;PST;PFV;NOM({pn});"
                                        full_feature = seed_full_feature
                                        _pron_writing_compound = phonological_constrain_pronons(pron=nom_prons[pn],
                                                                                                form=aux_form,
                                                                                                type=_response)
                                        full_form = seed_full_form + f"{_pron_writing_compound}{aux_form} {ptcp_pst}"
                                        new_table[full_feature] = full_form
                                        if VERBOSE:
                                            print(f"{nfin}\t{full_form}\t{full_feature}")

                                        # passé antérieur --> passé simple
                                        aux_form = auxiliary_dict[aux]["IND;PST;PFV;LGSPEC1"][pers]
                                        seed_full_feature = f"IND;PST;PFV;LGSPEC1;NOM({pn});"
                                        full_feature = seed_full_feature
                                        _pron_writing_compound = phonological_constrain_pronons(pron=nom_prons[pn],
                                                                                                form=aux_form,
                                                                                                type=_response)
                                        full_form = seed_full_form + f"{_pron_writing_compound}{aux_form} {ptcp_pst}"
                                        new_table[full_feature] = full_form
                                        if VERBOSE:
                                            print(f"{nfin}\t{full_form}\t{full_feature}")
                                elif mood == "COND":
                                    # passé antérieur --> passé simple
                                    if tense == "PST":
                                        aux_form = auxiliary_dict[aux]["COND;PST"][pers]
                                        seed_full_feature = f"COND;PFV;NOM({pn});"

                                        full_feature = seed_full_feature + f"{cases[_response]}({_pron_feat})"
                                        _pron_writing_compound = phonological_constrain_pronons(pron=_pron,
                                                                                                form=aux_form,
                                                                                                type=_response)

                                        full_form = seed_full_form + f"{_pron_writing_compound}{aux_form} {ptcp_pst}"
                                        new_table[full_feature] = full_form
                                        if VERBOSE:
                                            print(f"{nfin}\t{full_form}\t{full_feature}")

                            continue

                        # # TRANSITIF VERBS: handling all datif and accusatif in same way for now

                        for _pron_feat, _pron in prepos_prons[_response].items():

                            seed_full_feature = f"{mood};{tense_feature};NOM({pn});"
                            seed_full_form = ""

                            if (pn == "1;PL" and _pron_feat == "1;SG") or (pn == "2;PL" and _pron_feat == "2;SG") or (
                                    pn == "2;SG" and _pron_feat == "2;PL"):
                                # TODO: double check  (pn == "2;SG" and _pron_feat == "2;PL"): 'tu vous répondrais' not possible ?
                                continue

                            if mood == "IMP":
                                if (pn == "1;PL" and _pron_feat == "2;SG") or (pn == "1;PL" and _pron_feat == "2;PL"):
                                    # TODO: fact check this
                                    continue
                                _pron = imperatif_pronouns(_pron)
                                full_form = seed_full_form + f"{form}-{_pron}"
                                full_feature = seed_full_feature + f"{cases[_response]}({_pron_feat})"
                                new_table[full_feature] = full_form
                                if VERBOSE:
                                    print(f"{nfin}\t{full_form}\t{full_feature}")
                            else:

                                seed_full_form = ""#f"{nom_prons[pn]} "

                                # SIMPLE TENSES
                                _pron_writing = phonological_constrain_pronons(pron=_pron, form=form, type=_response)
                                #full_form = seed_full_form + f"{_pron_writing}{form} "
                                append_4_types_of_questions(new_table, _pron_feat=_pron_feat, seed_full_feature=seed_full_feature, seed_full_form=seed_full_form,
                                                            case=_response, subject=nom_prons[pn], form=form, pron=_pron_writing)
                                #full_feature = seed_full_feature + f"{cases[_response]}({_pron_feat})"
                                #new_table[full_feature] = full_form
                                if VERBOSE:
                                    print(f"{nfin}\t{full_form}\t{full_feature}")

                                # neg
                                # COMPOUND TENSE
                                if mood == "IND":
                                    if tense == "FUT":
                                        # get FUT --> get future
                                        aux_form = auxiliary_dict[aux]["IND;FUT"][pers]
                                        seed_full_feature = f"IND;FUT;PFV;NOM({pn});"
                                        full_feature = seed_full_feature + f"{cases[_response]}({_pron_feat})"
                                        _pron_writing_compound = phonological_constrain_pronons(pron=_pron,
                                                                                                form=aux_form,
                                                                                                type=_response)
                                        append_4_types_of_questions(new_table, _pron_feat=_pron_feat,
                                                                    seed_full_feature=seed_full_feature,
                                                                    seed_full_form=seed_full_form,
                                                                    case=_response, subject=nom_prons[pn], form=form,
                                                                    pron=_pron_writing)
                                        #full_form = seed_full_form + f"{_pron_writing_compound}{aux_form} {ptcp_pst}"
                                        #new_table[full_feature] = full_form
                                        if VERBOSE:
                                            print(f"{nfin}\t{full_form}\t{full_feature}")

                                    elif tense == "PST":
                                        # present perfect / passé composé --> présent
                                        aux_form = auxiliary_dict[aux]["IND;PRS"][pers]
                                        seed_full_feature = f"IND;PST;NOM({pn});"
                                        full_feature = seed_full_feature + f"{cases[_response]}({_pron_feat})"
                                        _pron_writing_compound = phonological_constrain_pronons(pron=_pron,
                                                                                                form=aux_form,
                                                                                                type=_response)
                                        #full_form = seed_full_form + f"{_pron_writing_compound}{aux_form} {ptcp_pst}"
                                        append_4_types_of_questions(new_table, _pron_feat=_pron_feat,
                                                                    seed_full_feature=seed_full_feature,
                                                                    seed_full_form=seed_full_form,
                                                                    case=_response, subject=nom_prons[pn], form=form,
                                                                    pron=_pron_writing)
                                        #new_table[full_feature] = full_form
                                        if VERBOSE:
                                            print(f"{nfin}\t{full_form}\t{full_feature}")

                                        # past-perfect / plus que parfait --> imparfait
                                        aux_form = auxiliary_dict[aux]["IND;PST;IPFV"][pers]
                                        seed_full_feature = f"IND;PST;PFV;NOM({pn});"
                                        #full_feature = seed_full_feature + f"{cases[_response]}({_pron_feat})"
                                        _pron_writing_compound = phonological_constrain_pronons(pron=_pron,
                                                                                                form=aux_form,
                                                                                                type=_response)
                                        #full_form = seed_full_form + f"{_pron_writing_compound}{aux_form} {ptcp_pst}"
                                        append_4_types_of_questions(new_table, _pron_feat=_pron_feat,
                                                                    seed_full_feature=seed_full_feature,
                                                                    seed_full_form=seed_full_form,
                                                                    case=_response, subject=nom_prons[pn], form=form,
                                                                    pron=_pron_writing)
                                        #new_table[full_feature] = full_form
                                        if VERBOSE:
                                            print(f"{nfin}\t{full_form}\t{full_feature}")

                                        # passé antérieur --> passé simple
                                        aux_form = auxiliary_dict[aux]["IND;PST;PFV;LGSPEC1"][pers]
                                        seed_full_feature = f"IND;PST;PFV;LGSPEC1;NOM({pn});"
                                        #full_feature = seed_full_feature + f"{cases[_response]}({_pron_feat})"
                                        _pron_writing_compound = phonological_constrain_pronons(pron=_pron,
                                                                                                form=aux_form,
                                                                                                type=_response)
                                        #full_form = seed_full_form + f"{_pron_writing_compound}{aux_form} {ptcp_pst}"
                                        append_4_types_of_questions(new_table, _pron_feat=_pron_feat,
                                                                    seed_full_feature=seed_full_feature,
                                                                    seed_full_form=seed_full_form,
                                                                    case=_response, subject=nom_prons[pn], form=form,
                                                                    pron=_pron_writing)
                                        #new_table[full_feature] = full_form
                                        if VERBOSE:
                                            print(f"{nfin}\t{full_form}\t{full_feature}")
                                elif mood == "COND":
                                    # passé antérieur --> passé simple
                                    if tense == "PST":
                                        aux_form = auxiliary_dict[aux]["COND;PST"][pers]
                                        seed_full_feature = f"COND;PFV;NOM({pn});"
                                        #full_feature = seed_full_feature + f"{cases[_response]}({_pron_feat})"
                                        _pron_writing_compound = phonological_constrain_pronons(pron=_pron,
                                                                                                form=aux_form,
                                                                                                type=_response)
                                        #full_form = seed_full_form + f"{_pron_writing_compound}{aux_form} {ptcp_pst}"
                                        append_4_types_of_questions(new_table, _pron_feat=_pron_feat,
                                                                    seed_full_feature=seed_full_feature,
                                                                    seed_full_form=seed_full_form,
                                                                    case=_response, subject=nom_prons[pn], form=form,
                                                                    pron=_pron_writing)
                                        #new_table[full_feature] = full_form
                                        if VERBOSE:
                                            print(f"{nfin}\t{full_form}\t{full_feature}")

                            #

    return new_table


def freq_sort(vocab_dir, language = "fr"):
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
    for i, lemma in enumerate(lemmas_to_do):

        try:

            responses = features[lemma].keys()
            _pp = pp[lemma]
        except:
            print(f"Missing lemma {lemma} so skipping it")
            continue
        if i > 600:
            break
        #if len(responses) == 0:
        #    responses.append("0")
        _new_table = create_new_table(responses, table[lemma], aux_dic=features[lemma])
        new_table[lemma] = _new_table
        lemmas_done.append(lemma)
        print(f"{i} {lemma} done")
    write_data(lemmas_done, new_table)
    breakpoint()

    # PB with leff pluging:

    # - with falloir and valoir

    # - validate use of auxilliary and cases
        #- shouldn't I match auxilliary with case --> dire: dire___tell_oneself is not accusatif it is
        #- e.g. : initier, rapporter, référer, garer, planter, promener: both être et avoir for accusatif

    #TODO:
    # 0 --> cannot be the default one!
    # - genitif / locatif to handle
    #    - aller: was not match with l (y) : ["e"]
    #    - genitif: j'en ai parlé: great , j'en suis venus great,   j'en ai su: vraiment (savoir)  ?
    # do L and D
    # add avoir + être accord
    # combination ad, + combination with l and d: for checking + questions
    # # send to Benoît
    # Add question/negations --> phonological constrains or maybe it is ok, - to handle 't'

        # writing

    # j'en ai pris, j'en ai trouvé
    # what order to go through it ?
    # then: given properties of the leff: aux+transitivity



