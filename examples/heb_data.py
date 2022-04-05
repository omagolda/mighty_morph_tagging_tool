from utils import *
from copy import deepcopy

language = 'heb'

person_number = {'2;SG;MASC', '2;SG;FEM', '2;PL;MASC', '2;PL;FEM',
                 '3;SG;MASC', '3;SG;FEM', '3;PL;MASC', '3;PL;FEM'}  # , '3;SG;NEUT'}
present_pns = person_number | {'1;SG;MASC', '1;SG;FEM', '1;PL;MASC', '1;PL;FEM'}
non_present_pns = person_number | {'1;SG', '1;PL'}
imperative_pns = {'2;SG;MASC', '2;SG;FEM', '2;PL;MASC', '2;PL;FEM'}
nom_prons = {'2;SG;MASC': 'אַתָּה', '2;SG;FEM': 'אַתְּ', '2;PL;MASC': 'אֲתֶּם', '2;PL;FEM': 'אַתֶּן',
             '3;SG;MASC': 'הוּא', '3;SG;FEM': 'הִיא', '3;PL;MASC': 'הֵם', '3;PL;FEM': 'הֵן',    # '3;SG;NEUT': 'זֶה',
             '1;SG;MASC': 'אֲנִי', '1;SG;FEM': 'אֲנִי', '1;PL;MASC': 'אֲנַחְנוּ', '1;PL;FEM': 'אֲנַחְנוּ',
             '1;SG': 'אֲנִי', '1;PL': 'אֲנַחְנוּ'}
et_prons = {'2;SG;MASC': 'אוֹתְךָ', '2;SG;FEM': 'אוֹתָךְ', '2;PL;MASC': 'אֶתְכֶם', '2;PL;FEM': 'אֶתְכֶן',
            '3;SG;MASC': 'אוֹתוֹ', '3;SG;FEM': 'אוֹתָהּ', '3;PL;MASC': 'אוֹתָם', '3;PL;FEM': 'אוֹתָן',  #'3;SG;NEUT': 'אֵת זֶה',
            '1;SG': 'אוֹתִי', '1;PL': 'אוֹתָנוּ'}
le_prons = {'2;SG;MASC': 'לְךָ', '2;SG;FEM': 'לָךְ', '2;PL;MASC': 'לָכֶם', '2;PL;FEM': 'לָכֶן',
            '3;SG;MASC': 'לוֹ', '3;SG;FEM': 'לָהּ', '3;PL;MASC': 'לָהֶם', '3;PL;FEM': 'לָהֶן',  # '3;SG;NEUT': 'לְזֶה',
            '1;SG': 'לִי', '1;PL': 'לָנוּ'}
el_prons = {'2;SG;MASC': 'אֵלֶיךָ', '2;SG;FEM': 'אֵלַיִךְ', '2;PL;MASC': 'אֲלֵיכֶם', '2;PL;FEM': 'אֲלֵיכֶן',
            '3;SG;MASC': 'אֵלָיו', '3;SG;FEM': 'אֵלֶיהָ', '3;PL;MASC': 'אֲלֵיהֶם', '3;PL;FEM': 'אֲלֵיהֶן',
            '1;SG': 'אֵלַי', '1;PL': 'אֵלֵינוּ'}
im_prons = {'2;SG;MASC': 'אִתְּךָ', '2;SG;FEM': 'אִתָּךְ', '2;PL;MASC': 'אִתְּכֶם', '2;PL;FEM': 'אִתְּכֶן',
            '3;SG;MASC': 'אִתּוֹ', '3;SG;FEM': 'אִתָּהּ', '3;PL;MASC': 'אִתָּם', '3;PL;FEM': 'אִתָּן',
            '1;SG': 'אִתִּי', '1;PL': 'אִתָּנוּ'}
be_prons = {'2;SG;MASC': 'בְּךָ', '2;SG;FEM': 'בָּךְ', '2;PL;MASC': 'בָּכֶם', '2;PL;FEM': 'בָּכֶן',
            '3;SG;MASC': 'בּוֹ', '3;SG;FEM': 'בָּהּ', '3;PL;MASC': 'בָּהֶם', '3;PL;FEM': 'בָּהֶן',
            '1;SG': 'בִּי', '1;PL': 'בָּנוּ'}
me_prons = {'2;SG;MASC': 'מִמְּךָ', '2;SG;FEM': 'מִמֵּךְ', '2;PL;MASC': 'מִכֶּם', '2;PL;FEM': 'מִכֶּן',
            '3;SG;MASC': 'מִמֶּנּוֹ', '3;SG;FEM': 'מִמֶּנָּה', '3;PL;MASC': 'מֵהֶם', '3;PL;FEM': 'מֵהֶן',
            '1;SG': 'מִמֶּנִּי', '1;PL': 'מֵאִתָּנוּ'}
al_prons = {'2;SG;MASC': 'עָלֶיךָ', '2;SG;FEM': 'עָלַיִךְ', '2;PL;MASC': 'עֲלֵיכֶם', '2;PL;FEM': 'עֲלֵיכֶן',
            '3;SG;MASC': 'עָלָיו', '3;SG;FEM': 'עָלֶיהָ', '3;PL;MASC': 'עֲלֵיהֶם', '3;PL;FEM': 'עֲלֵיהֶן',
            '1;SG': 'עָלַי', '1;PL': 'עָלֵינוּ'}
haya = {'2;SG;MASC': 'הָיִיתָ', '2;SG;FEM': 'הָיִית', '2;PL;MASC': 'הֱיִיתֶם', '2;PL;FEM': 'הֱיִיתֶן',
        '3;SG;MASC': 'הָיָה', '3;SG;FEM': 'הָיְתָה', '3;PL;MASC': 'הָיוּ', '3;PL;FEM': 'הָיוּ',
        '1;SG;MASC': 'הָיִיתִי', '1;PL;MASC': 'הָיִינוּ', '1;SG;FEM': 'הָיִיתִי', '1;PL;FEM': 'הָיִינוּ'}
reflex = {'2;SG;MASC': 'עַצְמְךָ', '2;SG;FEM': 'עַצְמֵךְ', '2;PL;MASC': 'עַצְמְכֶם', '2;PL;FEM': 'עַצְמְכֶן',
          '3;SG;MASC': 'עַצְמוֹ', '3;SG;FEM': 'עַצְמָהּ', '3;PL;MASC': 'עַצְמָם', '3;PL;FEM': 'עַצְמָן',
          '1;SG': 'עַצְמִי', '1;PL': 'עַצְמֵנוּ'}
reflex_prepos = {'t': 'אֶת ', 'l': 'לְ', 'e': 'אֶל ', 'i': 'עִם ', 'b': 'בְּ', 'm': 'מֵ', 'a': 'עַל '}
prepos = {'t': et_prons, 'l': le_prons, 'e': el_prons, 'i': im_prons, 'b': be_prons, 'm': me_prons, 'a': al_prons}
cases = {'t': 'ACC', 'l': 'DAT', 'e': 'ALL', 'i': 'COM', 'b': 'LOC', 'm': 'ABL', 'a': 'ON'}

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
                forms = {k+';NEG':(v[0],' '.join([v[1].split()[0]] + ['לֹא'] + v[1].split()[1:])) for k,v in forms.items()}
            elif mood_tense == 'IND;PRS':
                forms = {mood_tense + f';n(1;{person_number_gender})': (f'1;{person_number_gender}', nom_prons['1;' + person_number_gender] + ' ' + old_form),
                         mood_tense + f';n(2;{person_number_gender})': (f'2;{person_number_gender}', nom_prons['2;' + person_number_gender] + ' ' + old_form),
                         mood_tense + f';n(3;{person_number_gender})': (f'3;{person_number_gender}', nom_prons['3;' + person_number_gender] + ' ' + old_form),
                         'COND' + f';n(1;{person_number_gender})': (f'1;{person_number_gender}', nom_prons['1;' + person_number_gender] + ' ' + haya[f'1;{person_number_gender}'] + ' ' + old_form),
                         'COND' + f';n(2;{person_number_gender})': (f'2;{person_number_gender}', nom_prons['2;' + person_number_gender] + ' ' + haya[f'2;{person_number_gender}'] + ' ' + old_form),
                         'COND' + f';n(3;{person_number_gender})': (f'3;{person_number_gender}', nom_prons['3;' + person_number_gender] + ' ' + haya[f'3;{person_number_gender}'] + ' ' + old_form)}
                forms = {k+';NEG':(v[0],' '.join([v[1].split()[0]] + ['לֹא'] + v[1].split()[1:])) for k,v in forms.items()}
            elif '3;SG' in person_number_gender or '3;PL' in person_number_gender:
                forms = {mood_tense + f';n({person_number_gender})': (person_number_gender, nom_prons[person_number_gender] + ' ' + old_form),
                         mood_tense + f';n({person_number_gender});NEG': (person_number_gender, f'{nom_prons[person_number_gender]} לֹא ' + old_form)}
            elif 'FUT' in mood_tense and '2' in person_number_gender:
                forms = {mood_tense + f';n({person_number_gender})': (person_number_gender, old_form),
                         mood_tense + f';n({person_number_gender});NEG': (person_number_gender, 'לֹא ' + old_form),
                         'IMP' + f';n({person_number_gender});NEG': (person_number_gender, 'אַל ' + old_form)}
            else:
                forms = {mood_tense + f';n({person_number_gender})': (person_number_gender, old_form),
                         mood_tense + f';n({person_number_gender});NEG': (person_number_gender, 'לֹא ' + old_form)}

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
    excluded_lemmas = {'יָכֹל','הָיָה','נִהְיָה'}
    possible_responses = {'0','r','t','l','e','i','b','m','a','lt','te','ti','tm','ta','tb','la','em','am','ia','ea','tme'}

    manager = HebManager(language, possible_responses, excluded_lemmas)
    manager.main()
    manager.write_data()
