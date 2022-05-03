
import os
from tqdm import tqdm


def prepare_freq_list(vocab_dir, lang="fr"):
    print("Warning: alphabet defined based on French")
    alphabet = set('abcdefghijklmnopqrstuvwxyzàäöôüùûüßéèêëïç')
    ft_path = os.path.join(vocab_dir, f'cc.{lang}.300.vec')
    freq_path = os.path.join(vocab_dir, f'{lang}.txt')
    with open(ft_path, encoding='utf8') as ft, open(freq_path, 'w', encoding='utf8') as freq:
        _ = ft.readline()
        for line in tqdm(ft):
            word = line.split()[0]
            word = word.lower()
            if all([c in alphabet for c in word]):
                freq.write(word + '\n')
            else:
                pass
                #print(f"skipping {word}")


if __name__ == "__main__":

    prepare_freq_list("/Users/bemuller/Documents/Work/INRIA/dev/mighty_morph_tagging_tool/fasttext")#, "/Users/bemuller/Documents/Work/INRIA/dev/mighty_morph_tagging_tool/fasttext")

