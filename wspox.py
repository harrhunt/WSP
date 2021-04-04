from wsp import *
from oxford import *
from nltk.corpus import wordnet as wn

if __name__ == '__main__':
    trumpet = WSG('trumpet')
    trumpeting = WSG('trumpeting')
    trumpet_synset = wn.synsets('trumpet')
    trumpeting_synset = wn.synsets('trumpeting')
    print(trumpet_synset)
    print(trumpeting_synset)
    definitions = get_all_coarse_defs('trumpet')
    data = WSPComparer.group_by_closest_definition(trumpet, definitions)
    for definition in data:
        print(f"OXFORD_DEFINITION: '{definition}'")
        for wsp in data[definition]:
            print(f"{wsp.name}->'{wsp.definition}'")
        print("\n")
    definitions = get_all_coarse_defs('trumpeting')
    data = WSPComparer.group_by_closest_definition(trumpeting, definitions)
    for definition in data:
        print(f"OXFORD_DEFINITION: '{definition}'")
        for wsp in data[definition]:
            print(f"{wsp.name}->'{wsp.definition}'")
        print("\n")
