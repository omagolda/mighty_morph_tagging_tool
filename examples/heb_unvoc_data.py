from utils import *
from copy import deepcopy

language = 'heb_unvoc'

person_number = {'2;SG;MASC', '2;SG;FEM', '2;PL;MASC', '2;PL;FEM',
                 '3;SG;MASC', '3;SG;FEM', '3;PL;MASC', '3;PL;FEM'}  # , '3;SG;NEUT'}
present_pns = person_number | {'1;SG;MASC', '1;SG;FEM', '1;PL;MASC', '1;PL;FEM'}
non_present_pns = person_number | {'1;SG', '1;PL'}
imperative_pns = {'2;SG;MASC', '2;SG;FEM', '2;PL;MASC', '2;PL;FEM'}
nom_prons = {'2;SG;MASC': 'אתה', '2;SG;FEM': 'את', '2;PL;MASC': 'אתם', '2;PL;FEM': 'אתן',
             '3;SG;MASC': 'הוא', '3;SG;FEM': 'היא', '3;PL;MASC': 'הם', '3;PL;FEM': 'הן',    # '3;SG;NEUT': 'זה',
             '1;SG;MASC': 'אני', '1;SG;FEM': 'אני', '1;PL;MASC': 'אנחנו', '1;PL;FEM': 'אנחנו',
             '1;SG': 'אני', '1;PL': 'אנחנו'}
et_prons = {'2;SG;MASC': 'אותך', '2;SG;FEM': 'אותך', '2;PL;MASC': 'אתכם', '2;PL;FEM': 'אתכן',
            '3;SG;MASC': 'אותו', '3;SG;FEM': 'אותה', '3;PL;MASC': 'אותם', '3;PL;FEM': 'אותן',  #'3;SG;NEUT': 'את זה',
            '1;SG': 'אותי', '1;PL': 'אותנו'}
le_prons = {'2;SG;MASC': 'לך', '2;SG;FEM': 'לך', '2;PL;MASC': 'לכם', '2;PL;FEM': 'לכן',
            '3;SG;MASC': 'לו', '3;SG;FEM': 'לה', '3;PL;MASC': 'להם', '3;PL;FEM': 'להן',  # '3;SG;NEUT': 'לזה',
            '1;SG': 'לי', '1;PL': 'לנו'}
el_prons = {'2;SG;MASC': 'אליך', '2;SG;FEM': 'אלייך', '2;PL;MASC': 'אליכם', '2;PL;FEM': 'אליכן',
            '3;SG;MASC': 'אליו', '3;SG;FEM': 'אליה', '3;PL;MASC': 'אליהם', '3;PL;FEM': 'אליהן',
            '1;SG': 'אליי', '1;PL': 'אלינו'}
im_prons = {'2;SG;MASC': 'איתך', '2;SG;FEM': 'איתך', '2;PL;MASC': 'אתכם', '2;PL;FEM': 'אתכן',
            '3;SG;MASC': 'איתו', '3;SG;FEM': 'איתה', '3;PL;MASC': 'איתם', '3;PL;FEM': 'איתן',
            '1;SG': 'איתי', '1;PL': 'איתנו'}
be_prons = {'2;SG;MASC': 'בך', '2;SG;FEM': 'בך', '2;PL;MASC': 'בכם', '2;PL;FEM': 'בכן',
            '3;SG;MASC': 'בו', '3;SG;FEM': 'בה', '3;PL;MASC': 'בהם', '3;PL;FEM': 'בהן',
            '1;SG': 'בי', '1;PL': 'בנו'}
me_prons = {'2;SG;MASC': 'ממך', '2;SG;FEM': 'ממך', '2;PL;MASC': 'מכם', '2;PL;FEM': 'מכן',
            '3;SG;MASC': 'ממנו', '3;SG;FEM': 'ממנה', '3;PL;MASC': 'מהם', '3;PL;FEM': 'מהן',
            '1;SG': 'ממני', '1;PL': 'מאיתנו'}
al_prons = {'2;SG;MASC': 'עליך', '2;SG;FEM': 'עלייך', '2;PL;MASC': 'עליכם', '2;PL;FEM': 'עליכן',
            '3;SG;MASC': 'עליו', '3;SG;FEM': 'עליה', '3;PL;MASC': 'עליהם', '3;PL;FEM': 'עליהן',
            '1;SG': 'עליי', '1;PL': 'עלינו'}
haya = {'2;SG;MASC': 'היית', '2;SG;FEM': 'היית', '2;PL;MASC': 'הייתם', '2;PL;FEM': 'הייתן',
            '3;SG;MASC': 'היה', '3;SG;FEM': 'היתה', '3;PL;MASC': 'היו', '3;PL;FEM': 'היו',
            '1;SG;MASC': 'הייתי', '1;PL;MASC': 'היינו', '1;SG;FEM': 'הייתי', '1;PL;FEM': 'היינו'}
reflex = {'2;SG;MASC': 'עצמך', '2;SG;FEM': 'עצמך', '2;PL;MASC': 'עצמכם', '2;PL;FEM': 'עצמכן',
          '3;SG;MASC': 'עצמו', '3;SG;FEM': 'עצמה', '3;PL;MASC': 'עצמם', '3;PL;FEM': 'עצמן',
          '1;SG': 'עצמי', '1;PL': 'עצמנו'}
reflex_prepos = {'t': 'את ', 'l': 'ל', 'e': 'אל ', 'i': 'עם ', 'b': 'ב', 'm': 'מ', 'a': 'על '}
prepos = {'t': et_prons, 'l': le_prons, 'e': el_prons, 'i': im_prons, 'b': be_prons, 'm': me_prons, 'a': al_prons}
cases = {'t': 'ACC', 'l': 'DAT', 'e': 'ALL', 'i': 'COM', 'b': 'LOC', 'm': 'ABL', 'a': 'ON'}
cases_to_correct = {'a': 'ACC', 'd': 'DAT', 'c': 'COM', 'i': 'INE', 'b': 'ABL', 'l': 'LOC'}

dicts = [nom_prons, et_prons, le_prons, el_prons, im_prons, be_prons, me_prons, al_prons, haya, reflex]
non_lemma_words = set().union(*[set(dicto.values()) for dicto in dicts])
non_lemma_words |= {p + x for p in reflex_prepos.values() for x in reflex.values()} | {'לא', 'אל', 'על', 'את', 'עם'}


class Feats:
    def __init__(self):
        self.person = ''
        self.number = ''
        self.mood = ''
        self.tense = ''
        self.gender = ''


def unpack_feats(feats):
    result = Feats()
    for feat in feats:
        if feat in {'1', '2', '3'}:
            result.person = feat
        elif feat in {'SG', 'PL'}:
            result.number = feat
        elif feat in {'PST', 'PRS', 'FUT', 'IMP'}:
            result.tense = feat
        elif feat in {'MASC', 'FEM'}:
            result.gender = feat
        else:
            print('unhandled feature:', feat)
            raise NotImplementedError
    if result.tense == 'IMP':
        result.mood = 'IMP'
        result.tense = ''
    else:
        result.mood = 'IND'
    return result


class HebManager(Manager):
    def create_new_table(self, res, old_table):
        new_table = {}
        for old_feats, old_form in old_table.items():
            if old_feats in {'V.MSDR', 'V;NFIN'}:
                continue
            old_feats = old_feats.split(';')[1:]
            feats_dict = unpack_feats(old_feats)

            person_number_gender = ';'.join([feats_dict.person, feats_dict.number, feats_dict.gender])
            person_number_gender = person_number_gender.replace(';;', ';').strip(';')

            mood_tense = ';'.join([feats_dict.mood, feats_dict.tense]).strip(';')

            if mood_tense == 'IMP':
                forms = {mood_tense + f';n({person_number_gender})': (person_number_gender, old_form)}
            elif person_number_gender == '3;PL':
                forms = {mood_tense + f';n({person_number_gender};MASC)': (f'{person_number_gender};MASC', nom_prons[person_number_gender + ';MASC'] + ' ' + old_form),
                         mood_tense + f';n({person_number_gender};FEM)': (f'{person_number_gender};FEM', nom_prons[person_number_gender + ';FEM'] + ' ' + old_form)}
                forms = {k+';NEG':(v[0],' '.join([v[1].split()[0]] + ['לא'] + v[1].split()[1:])) for k,v in forms.items()}
            elif mood_tense == 'IND;PRS':
                forms = {mood_tense + f';n(1;{person_number_gender})': (f'1;{person_number_gender}', nom_prons['1;' + person_number_gender] + ' ' + old_form),
                         mood_tense + f';n(2;{person_number_gender})': (f'2;{person_number_gender}', nom_prons['2;' + person_number_gender] + ' ' + old_form),
                         mood_tense + f';n(3;{person_number_gender})': (f'3;{person_number_gender}', nom_prons['3;' + person_number_gender] + ' ' + old_form),
                         'COND' + f';n(1;{person_number_gender})': (f'1;{person_number_gender}', nom_prons['1;' + person_number_gender] + ' ' + haya[f'1;{person_number_gender}'] + ' ' + old_form),
                         'COND' + f';n(2;{person_number_gender})': (f'2;{person_number_gender}', nom_prons['2;' + person_number_gender] + ' ' + haya[f'2;{person_number_gender}'] + ' ' + old_form),
                         'COND' + f';n(3;{person_number_gender})': (f'3;{person_number_gender}', nom_prons['3;' + person_number_gender] + ' ' + haya[f'3;{person_number_gender}'] + ' ' + old_form)}
                forms = {k+';NEG':(v[0],' '.join([v[1].split()[0]] + ['לא'] + v[1].split()[1:])) for k,v in forms.items()}
            elif '3;SG' in person_number_gender or '3;PL' in person_number_gender:
                forms = {mood_tense + f';n({person_number_gender})': (person_number_gender, nom_prons[person_number_gender] + ' ' + old_form),
                         mood_tense + f';n({person_number_gender});NEG': (person_number_gender, f'{nom_prons[person_number_gender]} לא ' + old_form)}
            elif 'FUT' in mood_tense and '2' in person_number_gender:
                forms = {mood_tense + f';n({person_number_gender})': (person_number_gender, old_form),
                         mood_tense + f';n({person_number_gender});NEG': (person_number_gender, 'לא ' + old_form),
                         'IMP' + f';n({person_number_gender});NEG': (person_number_gender, 'אל ' + old_form)}
            else:
                forms = {mood_tense + f';n({person_number_gender})': (person_number_gender, old_form),
                         mood_tense + f';n({person_number_gender});NEG': (person_number_gender, 'לא ' + old_form)}

            for feats, (nom_feats, form) in forms.items():
                if res == '0' or res == 'r':
                    if res == 'r' and 'PL' not in feats:
                        continue
                    new_table[feats] = form
                elif len(res) == 1:
                    pre_prons = prepos[res]
                    for pre_feats, pre_pron in pre_prons.items():
                        if pre_feats in nom_feats and not ('3' in pre_feats and '3' in nom_feats):
                            new_table[feats + f';{cases[res]}({pre_feats};RFLX)'] = form + ' ' + reflex_prepos[res] + reflex[pre_feats]
                            continue
                        new_table[feats + f';{cases[res]}({pre_feats})'] = form + ' ' + pre_pron
                        if pre_feats in nom_feats:
                            # if it's 3rd person add a reflexive form in addition to a non-reflexive one
                            new_table[feats + f';{cases[res]}({pre_feats};RFLX)'] = form + ' ' + reflex_prepos[res] + reflex[pre_feats]
                else:
                    temp_table = {feats: form}
                    for argu in res:
                        pre_prons = prepos[argu]
                        new_temp = {}
                        for pre_feats, pre_pron in pre_prons.items():
                            for k, v in temp_table.items():
                                if pre_feats in k and '3' not in pre_feats:
                                    if 'RFLX' in k:
                                        continue
                                    else:
                                        new_temp[k + f';{cases[argu]}({pre_feats};RFLX)'] = v + ' ' + reflex_prepos[argu] + reflex[pre_feats]
                                        continue
                                new_temp[k + f';{cases[argu]}({pre_feats})'] = v + ' ' + pre_pron
                                if pre_feats in k and 'RFLX' not in k:
                                    new_temp[k + f';{cases[argu]}({pre_feats};RFLX)'] = v + ' ' + reflex_prepos[argu] + reflex[pre_feats]
                        temp_table = deepcopy(new_temp)
                    new_table.update(temp_table)

        new_table.update({k+';Q':v+'?' for k,v in new_table.items() if 'IMP' not in k})

        new_table = {correct_args(k): v for k, v in new_table.items()}

        return new_table


if __name__ == '__main__':
    excluded_lemmas = {'יכול','היה','נהיה'}
    forced_lemmas = {}

    possible_responses = {'0','r','t','l','e','i','b','m','a','lt','te','ti','tm','ta','tb','la','em','am','ia','ea','tme'}

    manager = HebManager(language, possible_responses, excluded_lemmas)
    manager.main()
    manager.write_data()
