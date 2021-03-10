from wsp import *
from oxford import *

if __name__ == '__main__':
    dog = WSG('plane')
    definitions = get_all_coarse_defs('plane')
    data = WSPComparer.group_by_closest_definition(dog, definitions)
    for definition in data:
        print(f"OXFORD_DEFINITION: '{definition}'")
        for wsp in data[definition]:
            print(f"{wsp.name}->'{wsp.definition}'")
        print("\n")
