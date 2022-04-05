from utils import *
from typing import Dict, List
import pickle
from copy import deepcopy

language = 'eng'
unimorph_path = 'unimorph/eng.txt'
mighymorph_path = 'mighty_eng.txt'

person_number = {'1,SG', '1,PL', '2', '3,SG,MACS', '3,SG,FEM', '3,SG,NEUT', '3,PL'}
nom_prons = {'1,SG': 'I', '1,PL': 'we', '2': 'you', '3,SG,MACS': 'he', '3,SG,FEM': 'she', '3,SG,NEUT': 'it', '3,PL': 'they'}
acc_prons = {'1,SG': 'me', '1,PL': 'us', '2': 'you', '3,SG,MACS': 'him', '3,SG,FEM': 'her', '3,SG,NEUT': 'it', '3,PL': 'them'}
reflex_prons = {'1,SG': 'myself', '1,PL': 'ourselves', '2,SG': 'yourself', '2,PL': 'yourselves', '3,SG,MACS': 'himself', '3,SG,FEM': 'herself', '3,SG,NEUT': 'itself', '3,PL': 'themselves'}
# dat_prons = {k: 'to ' + v for k,v in acc_prons.items()}
# del dat_prons['3;SG;NEUT']
prepos = {'a': '', 'd': 'to', 'c': 'with', 'g': 'of', 'b': 'from', 'f': 'for', 'l': 'on', 's': 'at', 't': 'about', 'i': 'in'}

moods = ['IND', 'IMP']
tenses = {'PST', 'PRS', 'FUT', 'COND'}
aspects = {'SIMP', 'PROG', 'PERF', 'PROG;PERF'}
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

cases = {'a': 'ACC', 'd': 'DAT', 'c': 'COM', 'g': 'GEN', 'b': 'ABL', 'f': 'BEN', 'l': 'ON', 's': 'AT', 't': 'CIRC', 'i': 'LOC'}
rev_cases = {v: k for k, v in cases.items()}


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


class EngManager(Manager):
    def create_new_table(self, response, table):
        nfin = table['V;NFIN']
        past = table['V;PST']
        v3 = table['V;V.PTCP;PST']
        ing = table['V;V.PTCP;PRS']
        sg3 = table['V;3;SG;PRS']

        new_table = {}

        # for mood in moods:
        #     if mood == 'IMP':
        pn = '2'
        if response == '0' or response == 'r':
            new_table['IMP;NOM(2)'] = nfin
            new_table['IMP;NOM(2);NEG'] = "don't " + nfin
        else:
            forms = {
                'IMP;NOM(2)': nfin,
                'IMP;NOM(2);NEG': "don't " + nfin
            }
            for argu in response:
                new_forms = {}
                for arg_feats, arg in acc_prons.items():
                    for k, v in forms.items():
                        if arg_feats in k and '3' not in arg_feats:
                            if 'RFLX' not in k:
                                new_forms.update(reflexive_forms(k, v, argu, arg_feats))
                            continue

                        key = (k + f';{cases[argu]}({arg_feats})')
                        value = (v + ' ' + prepos[argu] + ' ' + arg).replace('  ', ' ')
                        new_forms[key] = value
                        if arg_feats in k and 'RFLX' not in k:
                            new_forms.update(reflexive_forms(k, v, argu, arg_feats))
                            # key = k + f';{cases[argu]}({arg_feats},RFLX)'
                            # value = (v + ' ' + prepos[argu] + ' ' + reflex_prons[arg_feats]).replace('  ', ' ')
                            # new_forms[key] = value
                forms = deepcopy(new_forms)
            new_table.update(new_forms)

        # if mood == 'IND':
        for aspect in aspects:
            for tense in tenses:
                for pn in person_number:
                    form = [nfin]

                    # aspect
                    if 'PROG' in aspect:
                        form = ['be', ing]
                    if 'PERF' in aspect:
                        if form[0] == 'be':
                            form = ['have', 'been', ing]
                        else:
                            form = ['have', v3]

                    # tense
                    if tense == 'FUT':
                        form = ['will'] + form
                    elif tense == 'COND':
                        form = ['would'] + form
                    elif tense == 'PST':
                        if form[0]=='be':
                            form[0] = 'be.PST'
                        elif form[0]=='have':
                            form[0] = have['pst']
                        else:
                            assert form == [nfin]
                            form = [past]
                    elif tense == 'PRS':
                        form[0] += '.PRS'

                    # person-number
                    if '.' in form[0]:
                        if form[0].split('.')[0]=='be':
                            key = tense + ',' + pn
                            # delete gender
                            if len(key.split(',')) == 4:
                                key = ','.join(key.split(',')[:-1])
                            form[0] = be[key]
                        elif form[0].split('.')[0]=='have':
                            if '3,SG' in pn:
                                form[0] = have['prs3sg']
                            else:
                                form[0] = 'have'
                        else:
                            assert form[0].split('.')[0] == nfin
                            if '3,SG' in pn:
                                form[0] = sg3
                            else:
                                form[0] = nfin
                    form = [nom_prons[pn]] + form

                    feats = ';'.join(['IND', tense, aspect, 'NOM('+pn+')'])
                    feats = feats.replace(';SIMP;', ';')
                    feats = feats.replace('IND;COND', 'COND')

                    if form[1] not in table.values():
                        q_form = [form[1], form[0]] + form[2:]
                        neg_form = form[:2] + ['not'] + form[2:]
                        q_neg_form = [neg_form[1], neg_form[0]] + neg_form[2:]
                    elif form[1] == past:
                        q_form = ['did'] + [form[0]] + [nfin]
                        neg_form = [form[0], "didn't", nfin]
                        q_neg_form = ["didn't", form[0], nfin]
                    else:
                        assert tense == 'PRS' and aspect == 'SIMP'
                        if '3,SG' in pn:
                            do = 'does'
                        else:
                            do = 'do'
                        q_form = [do] + [form[0]] + [nfin]
                        neg_form = [form[0], do+"n't", nfin]
                        q_neg_form = [do+"n't", form[0], nfin]

                    form = join_and_shorten(form)
                    q_form = join_and_shorten(q_form)
                    neg_form = join_and_shorten(neg_form, neg=True)
                    q_neg_form = join_and_shorten(q_neg_form, qneg=True)

                    if response == '0' or response == 'r':
                        if response == 'r' and 'PL' not in feats:
                            continue
                        new_table[feats] = form
                        new_table[feats + ';NEG'] = neg_form
                        new_table[feats + ';Q'] = q_form + '?'
                        new_table[feats + ';NEG;Q'] = q_neg_form + '?'

                    else:
                        forms = {
                            feats: form,
                            feats + ';NEG': neg_form,
                            feats + ';Q': q_form,
                            feats + ';NEG;Q': q_neg_form
                        }
                        for argu in response:
                            new_forms = {}
                            for arg_feats, arg in acc_prons.items():
                                for k, v in forms.items():
                                    if arg_feats in k and '3' not in arg_feats:
                                        if 'RFLX' not in k:
                                            new_forms.update(reflexive_forms(k, v, argu, arg_feats))
                                        continue
                                    key = k + f';{cases[argu]}({arg_feats})'
                                    value = (v + ' ' + prepos[argu] + ' ' + arg).replace('  ', ' ')
                                    new_forms[key] = value
                                    if arg_feats in k and 'RFLX' not in k:
                                        new_forms.update(reflexive_forms(k, v, argu, arg_feats))
                            forms = deepcopy(new_forms)
                        new_table.update(new_forms)
        new_table = {k: v+'?' if 'Q' in k else v for k, v in new_table.items()}

        return new_table


if __name__ == '__main__':
    possible_responses = {'0', 'r', 'a', 'd', 'c', 'g', 'b', 'f', 'l', 's', 't', 'i', 'ad', 'ac', 'ag', 'ab', 'af', 'al',
                          'as', 'at', 'ai', 'abd'}
    conds = [lambda table: len(table)<5]
    excluded_lemmas = {'have', 'be', 'will', 'do'}

    manager = EngManager(language, possible_responses, excluded_lemmas)
    manager.main(conds) #, forced_lemmas=manager.old_responses.keys())
    manager.write_data()
