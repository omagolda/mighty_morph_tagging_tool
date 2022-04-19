import sys
sys.path.insert(0,".")

from utils import *
from typing import Dict, List
import pickle
from copy import deepcopy

import json

language = 'fr'


person_number = {'1;SG', '1;PL', '2;SG', '2;PL', '3;SG;MASC', '3;SG;FEM',  '3;PL;MASC', '3;PL;FEM'}#,  '3;PL;NEUT','3;SG;NEUT',}


nom_prons = {'1;SG': 'je', '1;PL': 'nous', '2;SG': 'tu', '2;PL': 'vous', '3;SG;MASC': 'il', '3;SG;FEM': 'elle',  '3;PL;MASC':'ils', '3;PL;FEM': 'elles'}#,  '3;PL;NEUT':'ce', '3;SG;NEUT':'cela'}

acc_prons = {'1;SG': 'me', '1;PL': 'nous', '2;SG': 'te', '2;PL': 'vous', '3;SG;MASC': 'le', '3;SG;FEM': 'la',  "3;PL;MASC": "les", "3;PL;FEM": "les"} # NB: "3;PL;MASC": "les" and "3;PL;FEM" could be normalized to "3;PL" (but then must handle acc_prons[pn] errors)

dat_prons = {'1;SG': 'me', '1;PL':'nous', '2;SG': 'te', '2;PL': 'vous', '3;SG;MASC': 'lui', '3;SG;FEM': 'lui', '3;PL': 'leur'}# '3;PL;MASC':'leur', '3;PL;FEM':'leur'}

loc_pron = {'3;SG;NEUT': 'y'}# '3;PL;MASC':'leur', '3;PL;FEM':'leur'}

gen_pron = {'3;SG;NEUT': 'en'}

prepos_prons = {'a': acc_prons, 'd': dat_prons, 'l': loc_pron, "g": gen_pron}

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


VERBOSE = 1


def join_and_shorten(form: List[str], neg=False, qneg=False):
    form = ' '.join(form)
    form = form.replace('I am ',"I'm ").replace('you are ',"you're ").replace('we are ',"we're ").replace('they are ',"they're ").replace('he is ',"he's ").replace('she is ',"she's ").replace('it is ',"it's ")
    if neg:
        form = form.replace('have not ',"haven't ").replace('has not ',"hasn't ").replace('had not ',"hadn't ").replace('would not ',"wouldn't ").replace('will not ',"won't ").replace('was not ',"wasn't ").replace('were not ',"weren't ")
    form = form.replace('I have ',"I've ").replace('you have ',"you've ").replace('we have ',"we've ").replace('they have ',"they've ").replace('he has ',"he's ").replace('she has ',"she's ").replace('it has ',"it's ")
    form = form.replace('I had ',"I'd ").replace('you had ',"you'd ").replace('we had ',"we'd ").replace('they had ',"they'd ").replace('he had ',"he'd ").replace('she had ',"she'd ") #.replace('it had ',"it'd ")
    form = form.replace('I would ',"I'd ").replace('you would ',"you'd ").replace('we would ',"we'd ").replace('they would ',"they'd ").replace('he would ',"he'd ").replace('she would ',"she'd ") #.replace('it would ',"it'd ")
    form = form.replace('I will ',"I'll ").replace('you will ',"you'll ").replace('we will ',"we'll ").replace('they will ',"they'll ").replace('he will ',"he'll ").replace('she will ',"she'll ").replace('it will ',"it'll ")

    form = form.split()
    if qneg and not form[0].endswith("n't"):
        if form[0] != 'am':
            form[0] = form[0].replace('have', "haven't").replace('has', "hasn't").replace('had',"hadn't")\
                             .replace('would', "wouldn't").replace('will', "won't").replace('was', "wasn't")\
                             .replace('were',"weren't").replace('is',"isn't").replace('are',"aren't")
            assert form[0].endswith("n't")
            assert form[2] == 'not'
            del form[2]
    form = ' '.join(form)
    return form


def reflexive_forms(k, v, argu, arg_feats):
    temp = {}
    if arg_feats == '2':
        arg_feats = ['2,SG', '2,PL']
    else:
        arg_feats = [arg_feats]

    for af in arg_feats:
        key = k.replace('2', af)
        key = key + f';{cases[argu]}({af},RFLX)'
        value = (v + ' ' + prepos[argu] + ' ' + reflex_prons[af]).replace('  ', ' ')
        temp[key] = value

    return temp

import re


def phonological_constrain_pronons(form, pron, type="a"):

    if type == "a":
        if re.match("^[aeiouyhé].*", form) and re.match(".*[aeiou]$", pron):
            return pron[:-1]+"'"
        else:
            return pron+" "
    elif type == "d":
        if re.match("^[aeiouyhé].*", form) and re.match(".*[aeiou]$", pron) and pron not in ["lui"]:
            return pron[:-1] + "'"
        else:
            return pron+" "
    elif type == "0":
        if re.match("^[aeiouyhé].*", form) and pron in ["je"]:
            return pron[:-1] + "'"
        else:
            return pron+" "
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


class FrManager(Manager):
    def create_new_table(self, response, table):

        nfin = table['V;NFIN']

        ptcp_pst = table["V.PTCP;PST"]

        new_table = {}

        aux = None
        while aux not in {'e', 'a'}:
            aux = input(f"what is the auxiliary or {nfin}? [a for avoir, e for être (if several just do +)]")
            if aux == "e":
                print("WARNING: agreement with PARTICIPE PASSE not IMPLEMENTED")

        for mood in moods:
            for tense in tenses:
                # TODO: if else no IMPERATIVE : no future
                for i, aspect in enumerate(aspects):
                    # TODO: ifelse
                    if tense != "PST" and i>0:
                        # only going through the tensexmood one (cause aspect do not impact present and future)
                        continue
                    for pn in person_number:
                        #
                        pers = ";".join(pn.split(";")[:2])
                        unimorph_match = f"V;{mood};{tense};{pers}"

                        if mood == "IMP":

                            if pers not in ["2;SG", "1;PL", "2;PL"] or tense != "PRS":
                                # Imperfect only for first and second person: only keeping present
                                continue
                            unimorph_match = f"V;POS;{mood};{pers}"
                            form = table[unimorph_match]
                            #print(f"IMP form {form} working for {unimorph_match}")

                        elif mood == "IND" and tense == "PST":# and aspect == "PVF":
                            unimorph_match += f";{aspect}"
                            form = table[unimorph_match]
                            #print(f"PAST IND: form {form} working for {unimorph_match}")
                        elif mood == "COND":
                            if tense != "PRS":
                                # only
                                continue
                            unimorph_match = f"V;{mood};{pers}"
                            form = table[unimorph_match]

                        else:
                            form = table[unimorph_match]
                            #print(f"form {form} working for {unimorph_match}")

                        # Type of clause: affirmative, interrogative, negative, negative interrogative

                        # affirmative
                        if tense == "PST":
                            if aspect == "PFV":
                                tense_feature = f'{tense}:LGSPEC1'
                            elif aspect == "IPFV":
                                tense_feature = f'{tense};IPFV'
                        else:
                            tense_feature = tense

                        for _response in response:
                            # cases

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
                                            _pron_writing_compound = phonological_constrain_pronons(pron=nom_prons[pn], form=aux_form, type=_response)
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

                                if (pn == "1;PL" and _pron_feat == "1;SG") or (pn == "2;PL" and _pron_feat == "2;SG") or (pn == "2;SG" and _pron_feat == "2;PL"):
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

                                    seed_full_form += f"{nom_prons[pn]} "

                                    # SIMPLE TENSES
                                    _pron_writing = phonological_constrain_pronons(pron=_pron, form=form, type=_response)
                                    full_form = seed_full_form + f"{_pron_writing}{form} "

                                    full_feature = seed_full_feature + f"{cases[_response]}({_pron_feat})"
                                    new_table[full_feature] = full_form
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
                                            _pron_writing_compound = phonological_constrain_pronons(pron=_pron, form=aux_form, type=_response)
                                            full_form = seed_full_form + f"{_pron_writing_compound}{aux_form} {ptcp_pst}"
                                            new_table[full_feature] = full_form
                                            if VERBOSE:
                                                print(f"{nfin}\t{full_form}\t{full_feature}")

                                        elif tense == "PST":
                                            # present perfect / passé composé --> présent
                                            aux_form = auxiliary_dict[aux]["IND;PRS"][pers]
                                            seed_full_feature = f"IND;PST;NOM({pn});"
                                            full_feature = seed_full_feature + f"{cases[_response]}({_pron_feat})"
                                            _pron_writing_compound = phonological_constrain_pronons(pron=_pron, form=aux_form, type=_response)
                                            full_form = seed_full_form + f"{_pron_writing_compound}{aux_form} {ptcp_pst}"
                                            new_table[full_feature] = full_form
                                            if VERBOSE:
                                                print(f"{nfin}\t{full_form}\t{full_feature}")

                                            # past-perfect / plus que parfait --> imparfait
                                            aux_form = auxiliary_dict[aux]["IND;PST;IPFV"][pers]
                                            seed_full_feature = f"IND;PST;PFV;NOM({pn});"
                                            full_feature = seed_full_feature + f"{cases[_response]}({_pron_feat})"
                                            _pron_writing_compound = phonological_constrain_pronons(pron=_pron, form=aux_form, type=_response)
                                            full_form = seed_full_form + f"{_pron_writing_compound}{aux_form} {ptcp_pst}"
                                            new_table[full_feature] = full_form
                                            if VERBOSE:
                                                print(f"{nfin}\t{full_form}\t{full_feature}")

                                            # passé antérieur --> passé simple
                                            aux_form = auxiliary_dict[aux]["IND;PST;PFV;LGSPEC1"][pers]
                                            seed_full_feature = f"IND;PST;PFV;LGSPEC1;NOM({pn});"
                                            full_feature = seed_full_feature + f"{cases[_response]}({_pron_feat})"
                                            _pron_writing_compound = phonological_constrain_pronons(pron=_pron, form=aux_form, type=_response)
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
                                            _pron_writing_compound = phonological_constrain_pronons(pron=_pron, form=aux_form, type=_response)

                                            full_form = seed_full_form + f"{_pron_writing_compound}{aux_form} {ptcp_pst}"
                                            new_table[full_feature] = full_form
                                            if VERBOSE:
                                                print(f"{nfin}\t{full_form}\t{full_feature}")


                                # TODO: create Q/N/QN : in a factorized and maintaable way
                                # can we automate more:
                                # TODO: create ad combination
                                #
                                # Other type of argumetns
                                # --> send table + what you have done
                                # --> Q? how do you handle intransitive?
                                # --> Q? remaining reflexive ? : what else?
                                #

        return new_table


if __name__ == '__main__':
    possible_responses = {'0', #'r',
                          'a', 'd'}#, 'c', 'g', 'b', 'f', 'l', 's', 't', 'i', 'ad', 'ac', 'ag', 'ab', 'af', 'al',
                          #'as', 'at', 'ai', 'abd'}
    conds = [lambda table: len(table)<5]
    excluded_lemmas = {'have', 'be', 'will', 'do'}

    manager = FrManager(language, possible_responses, excluded_lemmas)
    manager.main(conds) #, forced_lemmas=manager.old_responses.keys())
    manager.write_data()




