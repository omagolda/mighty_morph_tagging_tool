from utils import *
from copy import deepcopy

language = 'deu'

person_number = {'1;SG', '1;PL', '2;SG', '2;PL', '3;SG;MASC', '3;SG;FEM', '3;SG;NEUT', '3;PL', '2;FRML'}
nom_prons = {'1;SG': 'ich', '1;PL': 'wir', '2;SG': 'du', '2;PL': 'ihr', '3;SG;MASC': 'er', '3;SG;FEM': 'sie', '3;SG;NEUT': 'es', '3;PL': 'sie', '2;FRML': 'Sie'}
acc_prons = {'1;SG': 'mich', '1;PL': 'uns', '2;SG': 'dich', '2;PL': 'euch', '3;SG;MASC': 'ihn', '3;SG;FEM': 'sie', '3;SG;NEUT': 'es', '3;PL': 'sie', '2;FRML': 'Sie'}
dat_prons = {'1;SG': 'mir', '1;PL': 'uns', '2;SG': 'dir', '2;PL': 'euch', '3;SG;MASC': 'ihm', '3;SG;FEM': 'ihr', '3;SG;NEUT': 'ihm', '3;PL': 'ihnen', '2;FRML': 'Ihnen'}
gen_prons = {'1;SG': 'meiner', '1;PL': 'unser', '2;SG': 'deiner', '2;PL': 'euer', '3;SG;MASC': 'seiner', '3;SG;FEM': 'ihrer', '3;SG;NEUT': 'seiner', '3;PL': 'ihrer', '2;FRML': 'Ihrer '}
ref_prons = lambda feats: 'sich' if '3' in feats or 'FRML' in feats else None

prepos = {'c': 'mit', 'b': 'von', 's': 'an', 'l': 'auf', 'z': 'zu', 'f': 'für', 't': 'über', 'j': 'bei', 'u': 'um', 'e': 'aus', 'p': 'durch', 'o': 'vor', 'i': 'in', 'v': 'gegen', 'n': 'in'}
prepos_prons = {'a': acc_prons,'d': dat_prons, 'g': gen_prons,
                'c': dat_prons, 'b': dat_prons, 's': acc_prons, 'l': acc_prons, 'z': dat_prons, 'f': acc_prons,
                't': acc_prons, 'j': dat_prons, 'u': acc_prons, 'e': dat_prons, 'p': acc_prons, 'o': dat_prons,
                'i': dat_prons, 'v': acc_prons, 'n': acc_prons}
cases = {'a': 'ACC','d': 'DAT','g': 'GEN', 'c': 'COM', 'b': 'AT+ABL', 's': 'AT+ESS', 'l': 'ON+ESS', 'z': 'IN+ALL', 'f': 'BEN', 't': 'AT+PER', 'j': 'APUD', 'u': 'CIRC', 'e': 'IN+ABL', 'p': 'IN+PER', 'o': 'ANTE+ESS', 'i': 'IN+ALL', 'v': 'CONTR', 'n': 'IN+ESS'}

haben = {'NFIN': 'haben',
         'PRS;1;SG': 'habe', 'PRS;2;SG': 'hast', 'PRS;3;SG': 'hat', 'PRS;1;PL': 'haben', 'PRS;2;PL': 'habt', 'PRS;3;PL': 'haben',
         'PST;1;SG': 'hatte', 'PST;2;SG': 'hattest', 'PST;3;SG': 'hatte', 'PST;1;PL': 'hatten', 'PST;2;PL': 'hattet', 'PST;3;PL': 'hatten',
         'SBJV;1;SG': 'hätte', 'SBJV;2;SG': 'hättest', 'SBJV;3;SG': 'hätte', 'SBJV;1;PL': 'hätten', 'SBJV;2;PL': 'hättet', 'SBJV;3;PL': 'hätten',
         'QUOT;1;SG': 'habe', 'QUOT;2;SG': 'habest', 'QUOT;3;SG': 'habe', 'QUOT;1;PL': 'haben', 'QUOT;2;PL': 'habet', 'QUOT;3;PL': 'haben'}
sein = {'NFIN': 'sein',
        'PRS;1;SG': 'bin', 'PRS;2;SG': 'bist', 'PRS;3;SG': 'ist', 'PRS;1;PL': 'sind', 'PRS;2;PL': 'seid', 'PRS;3;PL': 'sind',
        'PST;1;SG': 'war', 'PST;2;SG': 'warst', 'PST;3;SG': 'war', 'PST;1;PL': 'waren', 'PST;2;PL': 'wart', 'PST;3;PL': 'waren',
        'SBJV;1;SG': 'wäre', 'SBJV;2;SG': 'wärst', 'SBJV;3;SG': 'wäre', 'SBJV;1;PL': 'wären', 'SBJV;2;PL': 'wärt', 'SBJV;3;PL': 'wären',
        'QUOT;1;SG': 'sei', 'QUOT;2;SG': 'seist', 'QUOT;3;SG': 'sei', 'QUOT;1;PL': 'seien', 'QUOT;2;PL': 'seiet', 'QUOT;3;PL': 'seien'}
werden = {'PRS;1;SG': 'werde', 'PRS;2;SG': 'wirst', 'PRS;3;SG': 'wird', 'PRS;1;PL': 'werden', 'PRS;2;PL': 'werdet', 'PRS;3;PL': 'werden',
          'PST;1;SG': 'wurde', 'PST;2;SG': 'wurdest', 'PST;3;SG': 'wurde', 'PST;1;PL': 'wurden', 'PST;2;PL': 'wurdet', 'PST;3;PL': 'wurden',
          'SBJV;1;SG': 'würde', 'SBJV;2;SG': 'würdest', 'SBJV;3;SG': 'würde', 'SBJV;1;PL': 'würden', 'SBJV;2;PL': 'würdet', 'SBJV;3;PL': 'würden',
          'QUOT;1;SG': 'werde', 'QUOT;2;SG': 'werdest', 'QUOT;3;SG': 'werde', 'QUOT;1;PL': 'werden', 'QUOT;2;PL': 'werdet', 'QUOT;3;PL': 'werden'}

# mtas = {'IND;PRS', 'IND;PST', 'IND;PST;LGSPEC1', 'IND;PST;PRF', 'IND;FUT', 'IND;FUT;PRF', 'IMP', 'SBJV', 'SBJV;LGSPEC1',
#         'SBJV;PRF', 'SBJV;PRF;LGSPEC2', 'QUOT;PRS', 'QUOT;PST', 'QUOT;FUT', 'QUOT;FUT;PRF'}

dicts = [nom_prons, acc_prons, dat_prons, gen_prons, prepos, haben, sein, werden]
non_lemma_words = set().union(*[set(dicto.values()) for dicto in dicts]) | {'sich', 'nicht', '?'}


def include_gender(inflection_table):
    temp = {}
    for feats, form in inflection_table.items():
        if '3;SG' in feats:
            temp[feats + ';FEM'] = form
            temp[feats + ';MASC'] = form
            temp[feats + ';NEUT'] = form
        elif '3;PL' in feats:
            temp[feats] = form
            temp[feats.replace('3','2').replace('PL','FRML')] = form
        else:
            temp[feats] = form
    return temp


haben = include_gender(haben)
sein = include_gender(sein)
werden = include_gender(werden)


def simple_forms(old_table, new_mta, old_mta):
    return {new_mta + ';NOM(' + pn + ')': nom_prons[pn] + ' ' + old_table[old_mta + ';' + pn] for pn in person_number}


def compound_forms(main_mta, aux_table, aux_mta, ending):
    return {main_mta + ';NOM(' + pn + ')': [nom_prons[pn] + ' ' + aux_table[aux_mta + ';' + pn], ending] for pn in person_number}


def clean_reflexive(feats):
    if 'RFLX' not in feats:
        return feats
    feats = feats.replace('1;SG;RFLX', '1;SG')
    feats = feats.replace('1;PL;RFLX', '1;PL')
    feats = feats.replace('2;SG;RFLX', '2;SG')
    feats = feats.replace('2;PL;RFLX', '2;PL')
    return feats


class DeuManager(Manager):
    def create_new_table(self, res, old_table):
        lemma = old_table['V;NFIN']
        aux = None
        while aux not in {'s', 'h'}:
            aux = input(f"what is the auxiliary or {lemma}? [s for sein, h for haben]")
        aux = 'sein' if aux == 's' else 'haben'

        old_table = include_gender(old_table)

        aux_table = haben if aux=='haben' else sein

        trennbar = len(old_table['V;IND;PRS;1;PL'].split()) > 1
        if trennbar:
            ending = old_table['V;IND;PRS;1;PL'].split()[1]
            old_table = {feats[2:]: form.split()[0] for feats, form in old_table.items()}
        else:
            old_table = {feats[2:]: form for feats, form in old_table.items()}
            ending = ''

        # 'IMP'
        forms = {'IMP;NOM(2;SG)': old_table['IMP;2;SG'], 'IMP;NOM(2;PL)': old_table['IMP;2;PL'],
                 'IMP;NOM(1;PL)': old_table['IND;PRS;1;PL'] + ' wir', 'IMP;NOM(2;FRML)': old_table['IND;PRS;1;PL'] + ' Sie'}
        # 'IND;PRS'
        forms.update(simple_forms(old_table, 'IND;PRS', 'IND;PRS'))
        # 'IND;PST;LGSPEC1'
        forms.update(simple_forms(old_table, 'IND;PST;LGSPEC1', 'IND;PST'))
        # 'SBJV;LGSPEC1'
        forms.update(simple_forms(old_table, 'SBJV;LGSPEC1', 'SBJV;PST'))
        # 'QUOT;PRS'
        forms.update(simple_forms(old_table, 'QUOT;PRS', 'SBJV;PRS'))

        forms = {feats: [form, ending] for feats, form in forms.items()}

        # 'IND;PST'
        forms.update(compound_forms('IND;PST', aux_table, 'PRS', old_table['PTCP;PST']))
        # IND;PST;PRF
        forms.update(compound_forms('IND;PST;PRF', aux_table, 'PST', old_table['PTCP;PST']))
        # 'IND;FUT'
        forms.update(compound_forms('IND;FUT', werden, 'PRS', old_table['NFIN']))
        # 'IND;FUT;PRF'
        forms.update(compound_forms('IND;FUT;PRF', werden, 'PRS', old_table['PTCP;PST'] + ' ' + aux_table['NFIN']))
        # 'SBJV'
        forms.update(compound_forms('SBJV', werden, 'SBJV', old_table['NFIN']))
        # 'SBJV;PRF'
        forms.update(compound_forms('SBJV;PRF', aux_table, 'SBJV', old_table['PTCP;PST']))
        # 'SBJV;PRF;LGSPEC2'
        # forms.update(compound_forms('SBJV;PRF;LGSPEC2', werden, 'SBJV', old_table['PTCP;PST'] + ' ' + aux_table['NFIN']))
        # 'QUOT;PST'
        forms.update(compound_forms('QUOT;PST', aux_table, 'QUOT', old_table['PTCP;PST']))
        # 'QUOT;FUT'
        forms.update(compound_forms('QUOT;FUT', werden, 'QUOT', old_table['NFIN']))
        # 'QUOT;FUT;PRF'
        forms.update(compound_forms('QUOT;FUT;PRF', werden, 'QUOT', old_table['PTCP;PST'] + ' ' + aux_table['NFIN']))

        new_table = {}
        for feats, (form, end) in forms.items():
            nom_feats = feats[feats.index('(')+1:feats.index(')')]
            if res == '0' or res == 'r':
                if res == 'r' and 'PL' not in feats:
                    continue
                new_table[feats] = [form, end]
            elif res.startswith('x'):
                # xa for reflexive accusative, xd for reflexive dative
                if res[:2] == 'xa':
                    arg_prons = acc_prons
                    case = 'a'
                elif res[:2] == 'xd':
                    arg_prons = dat_prons
                    case = 'd'
                else:
                    raise ValueError
                pron = ref_prons(nom_feats)
                if not pron:
                    pron = arg_prons[nom_feats]
                form += ' ' + pron
                feats += f';{cases[case]}({nom_feats};RFLX)'
                temp_res = res[2:]
            else:
                temp_res = res
            if res not in {'0', 'r'}:
                temp_forms = {feats: [form, end]}
                for argu in temp_res:
                    new_temp_forms = {}
                    arg_prons = prepos_prons[argu]
                    preposition = prepos.get(argu, '')
                    for arg_feats, arg in arg_prons.items():
                        for k, v in temp_forms.items():
                            if ('2;SG' in arg_feats and '2;FRML' in k) or ('2;SG' in k and '2;FRML' in arg_feats):
                                continue
                            if arg_feats in k and '3' not in arg_feats:
                                if 'RFLX' not in k:
                                    key = k + f';{cases[argu]}({arg_feats};RFLX)'
                                    arg = arg if not ref_prons(arg_feats) else ref_prons(arg_feats)
                                else:
                                    continue
                            else:
                                key = k + f';{cases[argu]}({arg_feats})'
                            to_add = (preposition + ' ' + arg).strip()
                            new_temp_forms[key] = v[:-1] + [to_add] + [v[-1]]
                            if arg_feats in k and 'RFLX' not in k and '3' in arg_feats:
                                key = k + f';{cases[argu]}({arg_feats};RFLX)'
                                to_add = (preposition + ' ' + ref_prons(arg_feats)).strip()
                                new_temp_forms[key] = v[:-1] + [to_add] + [v[-1]]
                    temp_forms = deepcopy(new_temp_forms)
                new_table.update(temp_forms)

        final_table = {}
        for feats, form in new_table.items():
            form = form[0].split() + form[1:]
            feats = clean_reflexive(feats)
            final_table[feats] = ' '.join(form).strip()
            if 'IMP;' not in feats:
                final_table[feats+';Q'] = ' '.join([form[1], form[0]] + form[2:]).strip() + '?'
            form.insert(-1, 'nicht')
            final_table[feats+';NEG'] = ' '.join(form).strip()
            if 'IMP;' not in feats:
                final_table[feats + ';NEG;Q'] = ' '.join([form[1], form[0]] + form[2:]).strip() + '?'

        final_table = {correct_args(k): v for k, v in final_table.items()}

        return final_table


if __name__ == '__main__':
    excluded_lemmas = {'sein', 'werden'}
    # possible_responses = {'0','r','a','d','c','b','s','l','f','t','n','ad','ac','ab','as','al','af','at','an'}
    possible_responses = {'0','r','a','d','g','ad','ag','ct'} | set(prepos.keys()) | {'a' + char for char in prepos.keys()} | {'d' + char for char in prepos.keys()}
    possible_responses |= {'x' + res for res in possible_responses if res[0] in {'a','d'}}
    possible_responses |= {'xda', 'xanf', 'xajt'}
    conds = [lambda table: len(table)<29]

    manager = DeuManager(language, possible_responses, excluded_lemmas)
    manager.main(conds)
    manager.write_data()
