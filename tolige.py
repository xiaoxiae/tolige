"""A TOdo LIst GEnerator."""
import os
from dataclasses import dataclass, field
from typing import *
from re import sub


def ask_for_variable(match_object, variables={}):
    """This function is called in a regex sub. Note that it relies on the fact that
    'variables' is not repeatedly instantiated on each method call."""
    variable = match_object.group(1)

    if variable not in variables:
        answer = input(variable.capitalize() + ": ")
        variables[variable] = answer

    return variables[variable]


def ask_for_condition(condition: str):
    """Ask the user for a condition."""
    out = None
    while out not in ("y", "n"):
        out = input(condition.capitalize() + "? [y/n]: ")

    return out == "y"


@dataclass
class Set:
    name: str
    items: List[str] = field(default_factory=list)

    def __getitem__(self, i: int):
        return self.items[i]

    def __setitem__(self, i: int, item: str):
        self.items[i] = item

    def __len__(self):
        return len(self.items)

    def pop(self, i: int):
        return self.items.pop(i)


# the path to the configuration
name = "tolige.config"
base = os.path.dirname(os.path.realpath(__file__))

sets = []
with open(os.path.join(base, name), "r") as f:
    current_set = None

    for line in filter(lambda x: len(x.strip()) != 0, f):
        stripped_line = line.strip()
        # skip comments
        if stripped_line.startswith("#"):
            continue

        # add a line (only right-stripped, since it could be tab-indented)
        elif not line[0].isalpha():
            current_set.items.append(line.rstrip())

        # else add a set
        else:
            if current_set is not None:
                sets.append(current_set)

            current_set = Set(stripped_line)

# add the remaining set
if current_set is not None:
    sets.append(current_set)

# check for empty sets
if len(sets) == 0:
    exit("ERROR: No sets parsed -- add some before running the script.")

# the "*" is for all sets
set_names = ", ".join(list(f"{s.name}: {i}" for i, s in enumerate(sets)) + ["*"])

selected_sets = list(
    filter(
        lambda x: len(x) != 0,
        map(lambda x: x.strip(), input(f"Select sets ({set_names}): ").split(","),),
    )
)

# special * for all sets
if "*" in selected_sets:
    selected_sets = [str(i) for i in range(len(sets))]

print()

# parse each of the sets
k = 0
while k < len(selected_sets):
    s = selected_sets[k]

    # check number
    if not all(c.isdigit() for c in s):
        print(f"WARNING: '{s}' is not an integer, skipping.")
        selected_sets.pop(k)
        continue

    s = int(s)

    # check range
    if not 0 <= s < len(sets):
        print(f"WARNING: {s} is out of range, skipping.")
        selected_sets.pop(k)
        continue

    # parse conditions and variables
    conditions = {}
    variables = {}

    i = 0
    while i < len(sets[s]):
        item = sets[s][i]

        # re-sub the variables
        sets[s][i] = sub(r"{(.+?)}", ask_for_variable, item)

        # check for conditions
        if item.startswith("["):
            # check for incomplete bracket
            if "]" not in item:
                print(f"WARNING: Malformed line '{item}', skipping.")
                sets[s].pop(i)
                continue

            # remove the condition
            c = item[1 : item.index("]")]
            sets[s][i] = item[item.index("]") + 1 :]

            # if the condition has not been met first, ask for it
            if c not in conditions:
                conditions[c] = ask_for_condition(c)

            # include/exclude the condition line depending on the answer
            if not conditions[c]:
                sets[s].pop(i)
                i -= 1

        i += 1
    k += 1

if selected_sets == []:
    exit("ERROR: no sets selected, exiting.")

print()

# write to file
output_path = input("Output file path (defaults to TODO.txt): ")
with open("TODO.txt" if output_path == "" else output_path, "w") as f:
    for s in map(int, selected_sets):
        for line in sets[s]:
            f.write(line + "\n")

        # separate sets by an empty line
        f.write("\n")