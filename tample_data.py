from utils import *
from copy import deepcopy

# 3 letters language code
language = ''

# a set of all possible person_number_gender combinations. e.g. '1;SG', '2;PL;NEUT' etc.
person_number_gender = {'', ''}
# dicts with all personal pronouns keys are person_number_gender combinations
# add dicts according to the number of cases in the language
nom_prons = {}
acc_prons = {}
# for reflexive pronouns sometimes it's better to have more pronoun dicts, and sometimes it's better to partly define
# them here and partly in the script

# mapping the letters to case features (just a shortcut to make annotation process easier)
# e.g. {'a': 'ACC', 'b': 'ABL', 'c': 'COM'}
cases = {}
# defining adprepositions to be used with every case. only if this case is expressed with an adposition
# for example: {'b': 'from', 'c': 'with'}
prepos = {}
# mapping prepositions to cases to be used with them. also keyed by letters
# for example: {'a': acc_prons, 'b': acc_prons, 'c': dat_prons}
pre_prons = {}

# here you can define some auxiliary tables and anything that will make it easier down the line.
# for example in english I defined have={'pst': 'had', 'prs': 'have', 'prs3sg': 'has', 'fut': 'will have'}


class LangManager(Manager):
    def create_new_table(self, res, old_table):
        '''
        :param res: a combination of letters representing arguments. e.g. 'a', 'rb', '0'
        :param old_table: a unimorph table {feats: form}
        :return: new_table: a mightymorph table {feats: form}
        '''
        # here is my suggestion for a structure. it works well for languages without polypersonal agreement.
        # start by going over the forms in the forms in the unimorph table and use them to create a mini table with all
        # periphrastic and non-periphrastic constructions and add the nominative pronoun if needed (i.e. if no pro-drop)
        # according to the features
        mini_table = {}
        for old_feats, old_form in old_table.items():
            # I'd recommend skipping participles and infinitives here

            # add nominative pronoun to old_form and layer the correct features in a 'NOM(1,SG,MASC)' pattern
            new_feats = ''
            new_form = ''
            mini_table[new_feats] = new_form
            # don't forget to add here the negative and interrogative forms, in case the they have a different structure
            # already in this stage
            if True: # if this form is needed in a periphrastic construction build it here
                new_feats = ''
                new_form = ''
                mini_table[new_feats] = new_form

        # now it's time to build periphrastic constructions with participles, using the auxiliaries you hopefully
        # defined above
        pass

        # now add the other arguments
        new_table = {}
        for feats, form in mini_table.items():

            # if the verb is intransitive or reciprocal no need for more arguments
            if res == '0' or res == 'r':
                if res == 'r' and 'PL' not in feats:
                    continue
                new_table[feats] = [form]

            else:
                # we're going to manipulate the forms so we're saving a copy
                temp = {feats: form}
                for argument in res:
                    new_temp = {}

                    # get everything you need from the dicts defined in the beginning of the file
                    case = cases[argument]
                    arg_prons = pre_prons[argument]
                    preposition = prepos.get(argument, '')
                    # go over all possible features for this argument and add them to the existing forms
                    for arg_feats, arg in arg_prons.items():
                        for feats, form in temp.items():
                            # add the pronoun to the form and the relevant features to feats
                            # for example:
                            feats = feats + f';{case}({arg_feats})'
                            form = form + f' {preposition} {arg}'
                            # this is definitely not complete!
                            # don't forget to treat reflexive pronouns properly
                            # also make sure that no illegal combinations of pronouns are added. e.g. 'I eat me' should
                            # not be generated but 'I eat myself', or if a formal 2nd person is produced, then don't use
                            # a non-formal pronoun somewhere else, etc.

                            new_temp[feats] = form
                    temp = deepcopy(new_temp)
                new_table.update(temp)

        # if the negative and interrogative were not added in the nominative phase, it may be a good idea to add them now
        pass

        return new_table


if __name__ == '__main__':
    # enumerate lemmas to be ignored. copulas, auxiliaries etc.
    excluded_lemmas: set = {}
    # an optional list of functions that take unimorph tables and return True/False to disqualify some lemmas
    # if any condition returns True the lemma will be disqualified
    # can used, for example for filtering partial tables in unimorph
    conds: set = {}
    # a list of lemmas to be dealt with first. optional
    forced_lemmas: set = {}
    # enumerate all possible argument combinations. I'd suggest adding '0' for intransitive and 'r' for reciprocal
    # don't use 'p' as it is designated for 'pass'
    possible_responses: set = {'', ''}
    # all responses can be added a '+' to say that there are more argument combinations possible
    # for example, the english verb 'stop' can be either transitive or intransitive.
    # so the correct response should be '0+' and then 'a' (for accusative)

    manager = LangManager(language, possible_responses, excluded_lemmas)
    manager.main(conds, forced_lemmas)
    manager.write_data()
