from utils import *
from copy import deepcopy

language = 'tur'

person_number = {'1;SG', '1;PL', '2;SG', '2;PL', '3;SG', '3;PL'}
nom_prons = {'1;SG': 'ben', '1;PL': 'biz', '2;SG': 'sen', '2;PL': 'siz', '3;SG': 'o', '3;PL': 'onlar'}
acc_prons = {'1;SG': 'beni', '1;PL': 'bizi', '2;SG': 'seni', '2;PL': 'sizi', '3;SG': 'onu', '3;PL': 'onları'}
dat_prons = {'1;SG': 'bana', '1;PL': 'bize', '2;SG': 'sana', '2;PL': 'size', '3;SG': 'ona', '3;PL': 'onlara'}
abl_prons = {'1;SG': 'benden', '1;PL': 'bizden', '2;SG': 'senden', '2;PL': 'sizden', '3;SG': 'ondan', '3;PL': 'onlardan'}
gen_prons = {'1;SG': 'benim', '1;PL': 'bizim', '2;SG': 'senin', '2;PL': 'sizin', '3;SG': 'onun', '3;PL': 'onların'}
loc_prons = {'1;SG': 'bende', '1;PL': 'bizde', '2;SG': 'sende', '2;PL': 'sizde', '3;SG': 'onda', '3;PL': 'onlarda'}
com_prons = {'1;SG': 'benimle', '1;PL': 'bizimle', '2;SG': 'seninle', '2;PL': 'sizinle', '3;SG': 'onunla', '3;PL': 'onlarınla'}
ben_prons = {'1;SG': 'benim için', '1;PL': 'bizim için', '2;SG': 'senin için', '2;PL': 'sizin için', '3;SG': 'onun için', '3;PL': 'onlar için'}
# refnom_prons = {'1;SG': 'kendim', '1;PL': 'kendimiz', '2;SG': 'kendin', '2;PL': 'kendiniz', '3;SG': 'kendi', '3;PL': 'kendileri'}
refacc_prons = {'1;SG': 'kendimi', '1;PL': 'kendimizi', '2;SG': 'kendini', '2;PL': 'kendinizi', '3;SG': 'kendini', '3;PL': 'kendilerini'}
refdat_prons = {'1;SG': 'kendime', '1;PL': 'kendimize', '2;SG': 'kendine', '2;PL': 'kendinize', '3;SG': 'kendine', '3;PL': 'kendilerine'}
refabl_prons = {'1;SG': 'kendimden', '1;PL': 'kendimizden', '2;SG': 'kendinden', '2;PL': 'kendinizden', '3;SG': 'kendinden', '3;PL': 'kendilerinden'}
refgen_prons = {'1;SG': 'kendimin', '1;PL': 'kendimizin', '2;SG': 'kendinin', '2;PL': 'kendinizin', '3;SG': 'kendinin', '3;PL': 'kendilerinin'}
refloc_prons = {'1;SG': 'kendimde', '1;PL': 'kendimizde', '2;SG': 'kendinde', '2;PL': 'kendinizde', '3;SG': 'kendinde', '3;PL': 'kendilerinde'}
refcom_prons = {'1;SG': 'kendimle', '1;PL': 'kendimizle', '2;SG': 'kendinle', '2;PL': 'kendinizle', '3;SG': 'kendiyle', '3;PL': 'kendileriyle'}
refben_prons = {'1;SG': 'kendim için', '1;PL': 'kendimiz için', '2;SG': 'kendin için', '2;PL': 'kendiniz için', '3;SG': 'kendi için', '3;PL': 'kendileri için'}

prepos = {}
pre_prons = {'a': acc_prons, 'd': dat_prons, 'b': abl_prons, 'c': com_prons, 'g': gen_prons, 'l': loc_prons, 'f': ben_prons}
ref_prons = {'a': refacc_prons, 'd': refdat_prons, 'b': refabl_prons, 'c': refcom_prons, 'g': refgen_prons, 'l': refloc_prons, 'f': refben_prons}

pred_suffixes = {'1;SG': '(y)Im', '1;PL': '(y)Iz', '2;SG': 'sIn', '2;PL': 'sInIz', '3;SG': '', '3;PL': ''}
verb_suffixes = {'1;SG': 'm', '1;PL': 'k', '2;SG': 'n', '2;PL': 'nIz', '3;SG': '', '3;PL': ''}
imperative_suffixes = {'2;SG': '', '2;PL': '(y)In', '2;PL;LGSPEC2': '(y)InIz'}

cases = {'a': 'ACC', 'd': 'DAT', 'b': 'ABL', 'c': 'COM', 'g': 'GEN', 'l': 'LOC', 'f': 'BEN'}


tams = {'IND;PRS;HAB':          ['',                    ''],
        'IND;PRS;PROG':         ['Iyor',                ''],
        'IND;PST':              ['DI',                  ''],
        'IND;PST;HAB':          ['',                    '(y)DI'],
        'IND;PST;PROG':         ['Iyor',                '(y)dI'],
        'IND;PST;PERF':         ['DI',                  '(y)dI'],
        'IND;PST;PRSP':         ['(y)EcEk',             '(y)DI'],
        'IND;PST;HAB;PROG':     ['Iyor olur',           '(y)DI'],
        'IND;PST;PRSP;PROG':    ['Iyor olacak',         '(y)DI'],
        'IND;FUT':              ['(y)EcEk',             ''],
        'IND;FUT;PROG':         ['Iyor olacak',         ''],
        'IND;FUT;PRSP':         ['(y)EcEk olacak',      ''],
        'INFR;PRS;PROG':        ['Iyor',                '(y)mIş'],
        'INFR;PRS;HAB':         ['',                    '(y)mIş'],
        'INFR;PST':             ['mIş',                 ''],
        'INFR;PST;PERF':        ['mIş',                 '(y)DI'],
        'INFR;PST;PRSP':        ['mIş olacak',          '(y)DI'],
        'INFR;FUT':             ['(y)EcEk',             '(y)mIş'],
        'INFR;FUT;PERF':        ['mIş olacak',          ''],
        'INFR;FUT;HAB':         [' olacak',             '(y)mIş'],
        'INFR;FUT;PROG':        ['Iyor olacak',         '(y)mIş'],
        'INFR;FUT;PRSP':        ['(y)EcEk olacak',      '(y)mIş'],
        'INFR;LGSPEC1;PST':     ['mIş',                 '(y)mIş'],
        'NEC;PRS':              ['mElI',                ''],
        'NEC;PRS;PROG':         ['Iyor olmalı',         ''],
        'NEC;PST':              ['mElI',                '(y)DI'],
        'NEC;PST;PROG':         ['Iyor olmalı',         '(y)DI'],
        'NEC;INFR;PST':         ['mElI',                '(y)mIş'],
        'NEC;INFR;PRS;PROG':    ['Iyor olmalı',         '(y)mIş'],
        'IMP':                  ['',                    '']}
compound_negation = {'olacak': 'olmayacak', 'olmalı': 'olmamalı', 'olur': 'olmaz'}



vowels = set('iıeaöoüu')
voiceless = set('çfhksştpqx')
voiced = set('bcdgğjlmnrvyzw')
I = {'i': 'i', 'ı': 'ı', 'e': 'i', 'a': 'ı', 'ö': 'ü', 'o': 'u', 'ü': 'ü', 'u': 'u'}
E = {'i': 'e', 'ı': 'a', 'e': 'e', 'a': 'a', 'ö': 'e', 'o': 'a', 'ü': 'e', 'u': 'a'}

def replace_at(string, index, new_char):
    return string[:index] + new_char + string[index+1:]

def last_populated(lst):
    idx = -1
    while not lst[idx]:
        idx -= 1
    return lst[idx]

def compound_tam(tam_suffs):
    return len(tam_suffs[0].split()) > 1 or tam_suffs[0].strip() != tam_suffs[0]

def negate_compound(suffix):
    for pos, neg in compound_negation.items():
        suffix = suffix.replace(pos, neg)
    return suffix

def iron_vowels(new_form):
    for j, char in enumerate(new_form):
        if char.lower() != char:
            if char == 'I':
                char = I[last_vowel]
            elif char == 'E':
                char = E[last_vowel]
            else:
                if j != 0:
                    raise NotImplementedError
            new_form = replace_at(new_form, j, char)
        if char in vowels:
            last_vowel = char
    return new_form


class TurManager(Manager):
    # def __init__(self, language, possible_responses,excluded_lemmas):
    #     # self.old_responses = self.get_old_responses()
    #     super().__init__(language, possible_responses,excluded_lemmas)

    def create_new_table(self, response, old_table):
        base, aorist = old_table['V;NFIN'][:-3], old_table['V;IND;PRS;HAB;3;SG;POS;DECL']

        new_table = {}

        if base[-1] in vowels:
            weak_base = aorist[:-1]
        else:
            weak_base = aorist[:-2]  # to deal with etmek-eder, gitmek-gider etc.

        for tam in tams:
            forms = {}
            if 'HAB' in tam and tam != 'IND;PST;HAB;PROG':
                forms[''] = [aorist] + tams[tam]
                forms['NEG'] = [base, 'mEz'] + tams[tam]
            # elif not tams[tam][0] or tams[tam][0][0] in vowels | {'E','I'} or tams[tam][0].startswith('(y)'):
            elif not tams[tam][0] or tams[tam][0][0] in vowels | {'E','I'} or tams[tam][0].startswith('(y)'):
                forms[''] = [weak_base] + tams[tam]
                forms['NEG'] = [base, 'mE'] + tams[tam]
            else:
                forms[''] = [base] + tams[tam]
                forms['NEG'] = [base, 'mE'] + tams[tam]

            if compound_tam(tams[tam]):
                if 'HAB' in tam and tam != 'IND;PST;HAB;PROG':
                    forms['NEG'] = [aorist, negate_compound(tams[tam][0])] + tams[tam][1:]
                else:
                    if tams[tam][0][0] in vowels | {'E','I'} or tams[tam][0].startswith('(y)'):
                        forms['NEG'] = [weak_base, negate_compound(tams[tam][0])] + tams[tam][1:]
                    else:
                        forms['NEG'] = [base, negate_compound(tams[tam][0])] + tams[tam][1:]

            if tam != 'IMP':
                forms['Q'] = deepcopy(forms[''])
                forms['Q'].insert(-1, ' mI')
                forms['NEG;Q'] = deepcopy(forms['NEG'])
                forms['NEG;Q'].insert(-1, ' mI')

            for sent_type, form in forms.items():
                pl3 = -1 if 'Q' not in sent_type else -2
                if last_populated(form).endswith(('dI','DI')) or \
                        (last_populated(form)==' mI' and last_populated(form[:form.index(' mI')]).endswith(('dI','DI'))):
                    prons_suffixes = verb_suffixes
                elif tam == 'IMP':
                    prons_suffixes = imperative_suffixes
                else:
                    prons_suffixes = pred_suffixes
                for pn in prons_suffixes:
                    new_form = deepcopy(form)
                    if tam == 'IMP' and pn == '2;SG':
                        new_form[0] = base

                    if pn == '3;PL':
                        new_form.insert(pl3, 'lEr')
                    if last_populated(form) == ' mI' and prons_suffixes == verb_suffixes:
                        new_form.insert(form.index(' mI'), prons_suffixes[pn])
                    else:
                        new_form.append(prons_suffixes[pn])

                    new_form = [suf for suf in new_form if suf]
                    if 'NEG' in sent_type and 'HAB' in tam and '1' in pn and new_form[2] in {'(y)Im', '(y)Iz'}:
                        assert new_form[1].endswith('z')
                        new_form[1] = new_form[1][:-1]
                        if new_form[2].endswith('m'):
                            new_form[2] = 'm'

                    for i, suffix in enumerate(new_form):
                        if i < len(new_form) - 1 and new_form[i + 1].startswith('Iyor') and suffix[-1] in vowels | {'E','I'}:
                            if i == 0 and all([c not in vowels for c in suffix[:-1]]):
                                # shouldn't be happening
                                # the only examples I managed to find where komak (to fuck) and yumak (to wash, regional)
                                # both are probably not in unimorph
                                new_form[i + 1] = 'yor'
                            else:
                                suffix = suffix[:-1]
                        if suffix.startswith('(y)'):
                            if new_form[i - 1][-1] in vowels | {'E', 'I'}:
                                suffix = suffix.replace('(y)', 'y')
                            else:
                                suffix = suffix.replace('(y)', '')
                        if 'D' in suffix:
                            if suffix.startswith('y') or new_form[i - 1][-1] in voiced | vowels | {'E', 'I'}:
                                suffix = suffix.replace('D', 'd')
                            else:
                                suffix = suffix.replace('D', 't')
                        # should not occur for the base (i=0) nor for the last morpheme
                        if suffix.endswith('k') and i!=0 and i!=len(new_form)-1:
                            if new_form[i + 1][0] in vowels | {'E', 'I'} or \
                                    (new_form[i + 1].startswith('(y)') and new_form[i + 1][3] in vowels | {'E', 'I'}):
                                suffix = suffix[:-1] + 'ğ'
                        new_form[i] = suffix
                    if base in {'ye', 'de'} and new_form[0].endswith('e') and len(new_form) > 1 and new_form[1].startswith('y'):
                        new_form[0] = new_form[0][:-1] + 'i'

                    new_form = ''.join(new_form)
                    new_form = iron_vowels(new_form)

                    feats = tam + ';NOM(' + pn + ');' + sent_type
                    feats = feats.strip(';')

                    if response.startswith('r') and 'PL' not in feats:
                        continue
                    if response == '0' or response == 'r':
                        new_table[feats] = new_form
                    else:
                        temp_forms = {feats: [new_form]}
                        for argu in response:
                            if argu == 'r':
                                continue
                            new_temp_forms = {}
                            arg_prons = pre_prons[argu]
                            ref_arg_prons = ref_prons[argu]
                            for arg_feats, arg in arg_prons.items():
                                for k, v in temp_forms.items():
                                    if arg_feats in k and '3' not in arg_feats:
                                        if 'RFLX' not in k:
                                            new_temp_forms[k + f';{cases[argu]}({arg_feats};RFLX)'] = v + [ref_arg_prons[arg_feats]]
                                        continue
                                    new_temp_forms[k + f';{cases[argu]}({arg_feats})'] = v + [arg]
                                    if arg_feats in k and 'RFLX' not in k:
                                        new_temp_forms[k + f';{cases[argu]}({arg_feats};RFLX)'] = v + [ref_arg_prons[arg_feats]]
                            temp_forms = deepcopy(new_temp_forms)
                        temp_forms = {k: ' '.join(v[1:] + [v[0]]) for k, v in temp_forms.items()}
                        new_table.update(temp_forms)

        new_table = {k: v + '?' if 'Q' in k else v for k, v in new_table.items()}

        new_table = {correct_args(k): v for k, v in new_table.items()}

        return new_table


if __name__ == '__main__':
    possible_responses = {'0', 'r', 'a', 'd', 'b', 'c', 'g', 'l', 'f', 'ad', 'ab', 'ac', 'af', 'adb', 'bd'}
    excluded_lemmas = {'imek', 'olmak'}

    manager = TurManager(language, possible_responses, excluded_lemmas)
    manager.main()
    manager.write_data()

