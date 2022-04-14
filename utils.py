import os
import pickle
from abc import abstractmethod
import re
from copy import deepcopy

unimorph_dir = 'unimorph'
vocab_dir = 'fasttext'

def read_mightymorph(path):
    data = {}
    with open(path, encoding='utf8') as f:
        for line in f:
            line = line.strip()
            parts = line.split('\t')
            if len(parts) != 3:
                continue
            lemma, form, feats = parts
            if lemma not in data:
                data[lemma] = {}
            # if feats not in data[lemma]:
            #     data[lemma][feats] = set()
            # data[lemma][feats].add(form)
            data[lemma][feats] = form

    return data


# def dump_done(language, done_lemmas, new_data):
#     with open(f'{language}_done_lemmas.pkl', 'wb') as f:
#         pickle.dump((done_lemmas, new_data), f)


class Manager:
    def __init__(self, language, possible_responses,excluded_lemmas):
        self.language = language
        self.save_path = f'{self.language}_done_lemmas.pkl'
        self.possible_responses = possible_responses
        self.possible_responses |= {res + '+' for res in self.possible_responses}
        self.possible_responses |= {'-', 'p'}
        self.excluded_lemmas = excluded_lemmas

        self.data = self.read_unimorph()
        self.done_lemmas, self.new_data, self.replies = self.load_done()
        print("Initialize freq_sort")
        self.sorted_lemmas = self.freq_sort()

        self.repair = False

    def main(self, conds=set(), forced_lemmas=set(), repair=False):
        lemmas_to_do = set(self.data.keys()) - self.done_lemmas
        if self.sorted_lemmas:
            sorted_set = set(self.sorted_lemmas)
            lemmas_to_do = {lemma for lemma in lemmas_to_do if lemma in sorted_set}
            lemmas_to_do = sorted(lemmas_to_do, key=lambda lemma: self.sorted_lemmas.index(lemma))
            # lemmas_to_do = {lemma for lemma in lemmas_to_do if lemma.split()[0] in sorted_set}
            # lemmas_to_do = sorted(lemmas_to_do, key=lambda lemma: self.sorted_lemmas.index(lemma.split()[0]))
        else:
            lemmas_to_do = list(lemmas_to_do)

        lemmas_to_do = list(forced_lemmas) + lemmas_to_do

        if repair:
            lemmas_to_do = self.replies.keys()
            self.temp_replies = deepcopy(self.replies)
            self.repair = True
        else:
            self.repair = False
        for i, lemma in enumerate(lemmas_to_do):
            if lemma in self.done_lemmas | self.excluded_lemmas and lemma not in forced_lemmas:
                continue
            if conds and lemma in self.data:
                if any([cond(self.data[lemma]) for cond in conds]):
                    continue
            if (i + 1) % 20 == 0:
                self.dump_done()

            if repair:
                if lemma not in self.temp_replies:
                    continue
                response = self.temp_replies[lemma][0]
                if len(self.temp_replies[lemma]) > 1 and not response.endswith('+'):
                    response += '+'
                self.temp_replies[lemma] = self.temp_replies[lemma][1:]
            else:
                response = None
                while response not in self.possible_responses:
                    response = input(f"what's the transitivity of {lemma}? [p to pass, - to skip, s to save]")
                    #breakpoint()
                    if response == 's':
                        self.dump_done()
                        response = None

            if response == '-':
                continue
            if response == 'p':
                self.done_lemmas.add(lemma)
                continue
            # if self.new_data.get(lemma, None):
            #     self.new_data[lemma].update(self.lang_func(lemma, response))
            # else:
            if not repair:
                if lemma not in self.replies:
                    self.replies[lemma] = []
                self.replies[lemma].append(response)
            self.new_data[lemma] = self.lang_func(lemma, response)
            self.done_lemmas.add(lemma)
        self.dump_done()
        if repair:
            print('data repaired!')
            print('to write the new data use Manager.write_data()')

    def load_done(self):
        if os.path.isfile(self.save_path):
            with open(self.save_path, 'rb') as f:
                things = pickle.load(f)
                if len(things)==2:
                    things.append([])
        else:
            done_lemmas = set()
            new_data = {}
            replies = {}
            things = [done_lemmas, new_data, replies]
        return things

    def read_unimorph(self, pos='V', exclude_doublets=True):
        path = os.path.join(unimorph_dir, f'{self.language}.txt')
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

    def dump_done(self):
        with open(self.save_path, 'wb') as f:
            pickle.dump((self.done_lemmas, self.new_data, self.replies), f)
        print('data saved!')

    def lang_func(self, lemma: str, response):
        try:
            old_table = self.data[lemma]
            if self.language == 'tur' and 'V;NFIN' not in old_table:
                old_table['V;NFIN'] = lemma
        except KeyError:
            if self.language == 'tur':
                aorist = input(f"what is the aorist of {lemma}?")
                old_table = {'V;IND;PRS;HAB;3;SG;POS;DECL': aorist, 'V;NFIN': lemma}
            else:
                raise KeyError(f'{lemma} does not exist in UniMorph')
        new_table = {}

        if response.endswith('+'):
            response = [response[:-1], '+']
        else:
            response = [response]

        for res in response:
            if res == '+':
                if self.repair:
                    response = self.temp_replies[lemma][0]
                    if len(self.temp_replies[lemma]) > 1 and not response.endswith('+'):
                        response += '+'
                    self.temp_replies[lemma] = self.temp_replies[lemma][1:]
                else:
                    response = None
                    while response not in self.possible_responses:
                        if response:
                            print('illegal response!')
                        response = input(f"any other arguments for {lemma}? [p to pass]")
                if response in {'-', 'p'}:
                    break
                else:
                    self.replies[lemma].append(response)
                    new_table.update(self.lang_func(lemma, response))
            else:
                new_table.update(self.create_new_table(res, old_table))
        return new_table

    @abstractmethod
    def create_new_table(self, res, old_table):
        pass

    def write_data(self):
        with open(os.path.join('mighty_morph', f'{self.language}'), 'w', encoding='utf8') as f:
            for lemma in sorted(self.new_data.keys()):
                for feats, form in self.new_data[lemma].items():
                    line = '\t'.join([lemma, form, feats])+'\n'
                    line = line.replace('??','?')
                    f.write(line)

    def freq_sort(self):
        path = os.path.join(vocab_dir, self.language + '.txt')

        if not os.path.isfile(path):
            print(f"Warning: Reading frequency list empty")
            return []
        print(f"Reading frequency list from {path}")
        with open(path, encoding='utf8') as f:
            return [line.strip() for line in f.readlines()]


def read_unimorph(path, pos='V', exclude_doublets=True):
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


def prepare_freq_list(lang2, lang3):
    if lang2 == 'ru':
        alphabet =  set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    else:
        alphabet = set('abcdefghijklmnopqrstuvwxyzäöüß')
    ft_path = os.path.join(vocab_dir, f'cc.{lang2}.300.vec')
    freq_path = os.path.join(vocab_dir, f'{lang3}.txt')
    with open(ft_path, encoding='utf8') as ft, open(freq_path, 'w', encoding='utf8') as freq:
        _ = ft.readline()
        for line in ft:
            word = line.split()[0]
            if all([c in alphabet for c in word]):
                freq.write(word + '\n')


def correct_args(string):
    args = re.findall('\(.+?\)', string)
    new_args = [arg.replace(';',',') for arg in args]
    for i in range(len(args)):
        string = string.replace(args[i], new_args[i])
    return string
