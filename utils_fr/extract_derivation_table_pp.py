"""
Download lefff-3.4.mlex from ...

python utils_fr/extract_derivation_table_pp.py \
    --leff_morph_dir ./lefff-3.4.mlex/lefff-3.4.mlex \
    --output_json_directory ./test.json

 goal extract PP

--> then plug to framework : TEST
--> then handle avoir Participe passé

--> then code
"""

import argparse
import json

feat_translate = {"s": "SG", "p": "PL", "m": "MASC", "f": "FEM"}


def extract_derivation_table(lex_dir, output_dir):
    with open(str(lex_dir), encoding="utf-8") as lex_file:
        lex = {}
        skipping, skipping_not_actif, skipping_no_bracket = 0, 0, 0
        for line in lex_file:

            line = line.strip().split('\t')
            if len(line) < 4:
                continue

            if line[1].startswith("v") and line[3].startswith("K") and line[0] != "_error":

                if line[2] not in lex:
                    lex[line[2]] = {}

                feat = line[3]

                if len(feat) > 2:
                    gender = feat[1]
                    number = feat[2]
                    lex[line[2]][f"{feat_translate[number]};{feat_translate[gender]}"] = line[0]
                elif len(feat) == 2:
                    gender = feat[1]
                    assert gender in ["m", "f"]
                    # number = feat[2]
                    lex[line[2]][f"PL;{feat_translate[gender]}"] = line[0]
                    lex[line[2]][f"SG;{feat_translate[gender]}"] = line[0]
                    print("SAME form for singular and plural", line[0])


    with open(output_dir, "w", encoding="utf-8") as writing:
        json.dump(lex, writing)
        print(f"{output_dir} written")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Extract features from the leff')
    parser.add_argument('--leff_morph_dir', type=str, help='', required=True)
    parser.add_argument('--output_json_directory', type=str, help='', required=True)

    args = parser.parse_args()

    extract_derivation_table(args.leff_morph_dir, args.output_json_directory)

    # to read it:
    #   - given an inf
    #   - given we know we want to do the agreemetn
    #   - given a pronon GENDER,NUMBER --> get the [inf][agreement] --> get the agreemnet DONE:


