import re
from pyswip import Prolog

prolog = Prolog()
prolog.consult("family_kb.pl")

relationships = ["sister", 
                 "brother", 
                 "siblings",
                 "mother",
                 "father",
                 "daughter",
                 "son",
                 "parent",
                 "child",
                 "aunt",
                 "uncle",
                 "cousin",
                 "grandfather",
                 "grandmother",
                 "grandchild",
                 "aunt_or_uncle"]


def handle_sibling_relationship(sentence, names, relationship, gender, excluded, inverse_excluded, print_function):
    # Handle statements (ends with a period)
    if "." in sentence:
        if len(names) == 2:
            sibling1, sibling2 = names[0].lower(), names[1].lower()

            # Validate logical consistency
            if sibling1 != sibling2 and are_related(excluded, inverse_excluded, names[0], names[1]):
                if is_valid_gender(sibling1, gender) or is_valid_gender(sibling1, "genderless") or not person_exists(sibling1, "person"):
                    if not is_existing_relation(relationship, sibling1, sibling2):
                        # Assert sibling relationship in Prolog
                        prolog.assertz(f"{relationship}({sibling1}, {sibling2})")

                        # Update gender if genderless
                        if is_valid_gender(sibling1, "genderless"):
                            update_gender(names[0], gender)
                        else:
                            prolog.assertz(f"{gender}({sibling1})")

                        # Mark as a person
                        prolog.assertz(f"person({sibling1})")
                        print("OK! I learned something.")
                    else:
                        print(f"{names[0]} is already the {relationship} of {names[1]}.")
                else:
                    print("That's impossible!")
            else:
                print("That's impossible!")
            return True
        else:
            return False

    # Handle questions (ends with a question mark)
    elif "?" in sentence:
        names.pop(0)
        if "Who" in sentence:
            sibling_name_match = re.search(rf'{relationship}s of (\w+)', sentence, re.IGNORECASE)
            if sibling_name_match:
                print_function(sibling_name_match.group(1))
                return True
            else:
                return False

        if len(names) == 2:
            sibling1, sibling2 = names[0].lower(), names[1].lower()
            if is_valid_gender(sibling1, "genderless") and is_existing_relation("siblings", sibling1, sibling2):
                print("Not enough information to determine sibling's gender.")
            elif is_existing_relation(relationship, sibling1, sibling2):
                print("Yes!")
            else:
                print("No!")
            return True
        else:
            return False

def handle_parent_relationship(sentence, names, relationship, gender, excluded, inverse_excluded, print_function):
    # Handle statements (ends with a period)
    if "." in sentence:
        if len(names) == 2:
            parent, child = names[0].lower(), names[1].lower()

            # Validate logical consistency
            if parent != child and are_related(excluded, inverse_excluded, names[0], names[1]):
                if is_valid_gender(parent, gender) or is_valid_gender(parent, "genderless") or not person_exists(parent, "person"):
                    if not is_existing_relation(relationship, parent, child):
                        if unique_relationship(relationship, names[1]) == 0 and unique_relationship("parent", names[1]) < 2:
                            # Update gender if genderless
                            if is_valid_gender(parent, "genderless"):
                                update_gender(names[0], gender)

                            # Assert parent relationship in Prolog
                            prolog.assertz(f"{relationship}({parent}, {child})")
                            prolog.assertz(f"{gender}({parent})")
                            prolog.assertz(f"person({parent})")
                            print("OK! I learned something.")
                        else:
                            print("That's impossible!")
                    else:
                        print(f"{names[0]} is already the {relationship} of {names[1]}.")
                else:
                    print("That's impossible!")
            else:
                print("That's impossible!")
            return True
        else:
            return False

    # Handle questions (ends with a question mark)
    elif "?" in sentence:
        names.pop(0)
        if "Who" in sentence:
            parent_name_match = re.search(fr'{relationship} of (\w+)', sentence, re.IGNORECASE)
            if parent_name_match:
                print_function(parent_name_match.group(1))
                return True
            else:
                return False

        if len(names) == 2:
            parent, child = names[0].lower(), names[1].lower()
            if is_valid_gender(parent, "genderless") and is_existing_relation("parent", parent, child):
                print("Not enough information to determine parent's gender.")
            elif is_existing_relation(relationship, parent, child):
                print("Yes!")
            else:
                print("No!")
            return True
        else:
            return False
        
def handle_child_relationship(sentence, names, relationship, gender, excluded, inverse_excluded, print_function):
    # Handle statements (ends with a period)
    if "." in sentence:
        if len(names) == 2:
            child, parent = names[0].lower(), names[1].lower()

            # Validate logical consistency
            if child != parent and are_related(excluded, inverse_excluded, names[0], names[1]):
                if is_valid_gender(child, gender) or is_valid_gender(child, "genderless") or not person_exists(child, "person"):
                    if not is_existing_relation(relationship, child, parent):
                        if (
                            is_existing_relation("child", child, parent) or
                            (unique_relationship("mother", child) == 0 and 
                            unique_relationship("father", child) == 0 and 
                            unique_relationship("parent", child) < 2)
                        ):
                            # Assert child relationship in Prolog
                            prolog.assertz(f"{relationship}({child}, {parent})")
                            prolog.assertz(f"{gender}({child})")
                            prolog.assertz(f"parent({parent}, {child})")
                            prolog.assertz(f"person({child})")
                            print("OK! I learned something.")
                        else:
                            print("That's impossible!")
                    else:
                        print(f"{names[0]} is already a {relationship} of {names[1]}.")
                else:
                    print("That's impossible!")
            else:
                print("That's impossible!")
            return True
        else:
            return False

    # Handle "Who are the [relationship]s of [parent]?" question
    elif f"{relationship}s of" in sentence and "?" in sentence:
        parent_name_match = re.search(fr'{relationship}s of (\w+)', sentence, re.IGNORECASE)
        if parent_name_match:
            print_function(parent_name_match.group(1))
            return True
        else:
            return False

    # Handle yes/no questions about child relationships
    elif "?" in sentence:
        names.pop(0)
        if len(names) == 2:
            child, parent = names[0].lower(), names[1].lower()
            if is_valid_gender(child, "genderless") and is_existing_relation("parent", parent, child):
                print("Not enough information to determine child's gender.")
            elif is_existing_relation(relationship, child, parent):
                print("Yes!")
            else:
                print("No!")
            return True
        else:
            return False


def handle_grandparent_relationship(sentence, names, relationship, gender):
    if "." in sentence:
        if len(names) == 2:
            grandparent, grandchild = names[0].lower(), names[1].lower()
            excluded = [relationship]
            inverse_excluded = ["grandchild"]

            # Validate logical consistency
            if grandparent != grandchild and are_related(excluded, inverse_excluded, names[0], names[1]):
                if is_valid_gender(grandparent, gender) or not person_exists(grandparent, "person"):
                    if not is_existing_relation(relationship, grandparent, grandchild):
                        if unique_relationship(relationship, names[1]) < 2:
                            # Assert grandparent relationship in Prolog
                            prolog.assertz(f"{relationship}({grandparent}, {grandchild})")
                            prolog.assertz(f"{gender}({grandparent})")
                            prolog.assertz(f"person({grandparent})")
                            print("OK! I learned something.")
                        else:
                            print("That's impossible!")
                    else:
                        print(f"{names[0]} is already a {relationship} of {names[1]}.")
                else:
                    print("That's impossible!")
            else:
                print("That's impossible!")
            return True
        else:
            return False

    elif "?" in sentence:
        names.pop(0)
        if len(names) == 2:
            grandparent, grandchild = names[0].lower(), names[1].lower()
            if is_existing_relation(relationship, grandparent, grandchild):
                print("Yes!")
            else:
                print("No!")
            return True
        else:
            return False
        
def handle_aunt_uncle_relationship(sentence, names, relationship, gender, excluded, inverse_excluded):
    # Handle statements (ends with a period)
    if "." in sentence:
        if len(names) == 2:
            relative, niece_nephew = names[0].lower(), names[1].lower()

            # Validate logical consistency
            if relative != niece_nephew and are_related(excluded, inverse_excluded, names[0], names[1]):
                if is_valid_gender(relative, gender) or is_valid_gender(relative, "genderless") or not person_exists(relative, "person"):
                    if unique_relationship(relationship, names[1]) < 2 and not is_existing_relation(relationship, relative, niece_nephew):
                        # Assert aunt/uncle relationship in Prolog
                        prolog.assertz(f"{relationship}({relative}, {niece_nephew})")
                        if gender != "genderless":
                            prolog.assertz(f"{gender}({relative})")
                        prolog.assertz(f"person({relative})")
                        print("OK! I learned something.")
                    else:
                        print(f"{names[0]} is already their {relationship}.")
                else:
                    print("That's impossible!")
            else:
                print("That's impossible!")
            return True
        else:
            return False

    # Handle questions (ends with a question mark)
    elif "?" in sentence:
        names.pop(0)
        if len(names) == 2:
            relative, niece_nephew = names[0].lower(), names[1].lower()
            if is_existing_relation(relationship, relative, niece_nephew):
                print("Yes!")
            else:
                print("No!")
            return True
        else:
            return False

        
# Sentence process for assertion and query
def process(sentence):
    # Extract sentence
    names = re.findall(r'\b[A-Z][a-z]*\b', sentence)

    if "siblings" in sentence:
        # Handle statements (ends with a period)
        if "." in sentence:
            if len(names) == 2:
                person1, person2 = names[0].lower(), names[1].lower()
                excluded = ["siblings", "brother", "sister"]
                inverse_excluded = ["siblings", "brother", "sister"]

                # Validate logical consistency
                if person1 != person2 and are_related(excluded, inverse_excluded, names[0], names[1]):
                    if not is_existing_relation("siblings", names[0], names[1]):
                        # Assert sibling relationship in Prolog
                        prolog.assertz(f"siblings({person1}, {person2})")
                        prolog.assertz(f"siblings({person2}, {person1})")

                        # Add genderless facts if genders are undefined
                        if not (is_valid_gender(person1, "male") or is_valid_gender(person1, "female")):
                            prolog.assertz(f"genderless({person1})")
                        if not (is_valid_gender(person2, "male") or is_valid_gender(person2, "female")):
                            prolog.assertz(f"genderless({person2})")

                        print("OK! I learned something.")
                    else:
                        print(f"{names[0]} and {names[1]} are already siblings.")
                else:
                    print("That's impossible!")
                return True
            else:
                return False

        # Handle questions (ends with a question mark)
        elif "?" in sentence:
            names.pop(0)
            if "Who" in sentence:
                sibling_name_match = re.search(r'siblings of (\w+)', sentence, re.IGNORECASE)
                if sibling_name_match:
                    print_siblings(sibling_name_match.group(1))
                    return True
                else:
                    return False

            if len(names) == 2:
                person1, person2 = names[0].lower(), names[1].lower()
                if is_existing_relation("siblings", person1, person2):
                    print("Yes!")
                else:
                    print("No!")
                return True
            else:
                return False

    
    # Check for "sister" relationships
    if "sister" in sentence:
        return handle_sibling_relationship(
            sentence, names, 
            "sister", "female", 
            ["siblings", "sister"], 
            ["siblings", "brother", "sister"], 
            print_sisters
        )

    # Check for "brother" relationship
    elif "brother" in sentence:
        return handle_sibling_relationship(
            sentence, names, 
            "brother", "male", 
            ["siblings", "brother"], 
            ["siblings", "brother", "sister"], 
            print_brothers
        )

    # Check for "grandmother" relationship
    elif "grandmother" in sentence:
        return handle_grandparent_relationship(sentence, names, "grandmother", "female")

    # Check for "grandfather" relationship
    elif "grandfather" in sentence:
        return handle_grandparent_relationship(sentence, names, "grandfather", "male")

    # Check for "mother" relationships
    elif "mother" in sentence:
        return handle_parent_relationship(
            sentence, 
            names, 
            "mother", 
            "female", 
            ["parent", "mother"], 
            ["child", "daughter", "son"], 
            print_mother
        )

    # Check for "father" relationships
    elif "father" in sentence:
        return handle_parent_relationship(
            sentence, 
            names, 
            "father", 
            "male", 
            ["parent", "father"], 
            ["child", "daughter", "son"], 
            print_father
        )
    
    # Check for parents relationship
    elif "parents" in sentence:
        # Handle statements (ends with a period)
        if "." in sentence:
            if len(names) == 3:
                parent1, parent2, child = names[0].lower(), names[1].lower(), names[2].lower()
                excluded = ["parent", "mother", "father"]
                inverse_excluded = ["child", "son", "daughter"]

                # Validate logical consistency
                if len(names) == len(set(names)) and are_related(excluded, inverse_excluded, names[0], names[1]):
                    if not (is_existing_relation("parent", parent1, child) or is_existing_relation("parent", parent2, child)):
                        if all(unique_relationship(rel, names[2]) == 0 for rel in ["parent", "father", "mother"]):
                            # Assert parent relationships in Prolog
                            prolog.assertz(f"parent({parent1}, {child})")
                            prolog.assertz(f"parent({parent2}, {child})")
                            prolog.assertz(f"person({parent1})")
                            prolog.assertz(f"person({parent2})")
                            print("OK! I learned something.")

                            # Add genderless facts if genders are undefined
                            for parent in [parent1, parent2]:
                                if not (is_valid_gender(parent, "male") or is_valid_gender(parent, "female")):
                                    prolog.assertz(f"genderless({parent})")
                        else:
                            print("That's impossible!")
                    else:
                        print(f"{names[0]} and {names[1]} are already parents of {names[2]}.")
                else:
                    print("That's impossible!")
                return True
            else:
                return False

        # Handle questions (ends with a question mark)
        elif "?" in sentence:
            names.pop(0)
            if "Who" in sentence:
                child_name_match = re.search(r'parents of (\w+)', sentence, re.IGNORECASE)
                if child_name_match:
                    print_parents(child_name_match.group(1))
                    return True
                else:
                    return False

            if len(names) == 3:
                parent1, parent2, child = names[0].lower(), names[1].lower(), names[2].lower()
                if is_existing_relation("parent", parent1, child) and is_existing_relation("parent", parent2, child):
                    print("Yes!")
                else:
                    print("No!")
                return True
            else:
                return False

        
    # check for daughter relationships
    elif "daughter" in sentence:
        return handle_child_relationship(
            sentence, 
            names, 
            "daughter", 
            "female", 
            ["child", "daughter"], 
            ["parent", "mother", "father"], 
            print_daughters_of_parent
        )

    # check for son relationships
    elif "son" in sentence:
        return handle_child_relationship(
            sentence, 
            names, 
            "son", 
            "male", 
            ["child", "son"], 
            ["parent", "mother", "father"], 
            print_sons_of_parent
        )

    elif "children" in sentence:
    # Handle statements (ends with a period)
        if "." in sentence:
            excluded = ["child", "daughter", "son"]
            inverse_excluded = ["parent", "mother", "father"]
            learned, related, unique = False, False, True

            if len(names) == len(set(names)):  # Ensure no duplicate names
                for n in range(len(names) - 1):
                    if not are_related(excluded, inverse_excluded, names[n], names[-1]):
                        related = True
                        break
                    if not is_existing_relation("parent", names[-1], names[n]):
                        if (
                            unique_relationship("mother", names[n]) < 2 and
                            unique_relationship("father", names[n]) < 2 and
                            unique_relationship("parent", names[n]) < 2
                        ):
                            # Assert parent-child relationships
                            prolog.assertz(f"parent({names[-1].lower()}, {names[n].lower()})")
                            prolog.assertz(f"person({names[n].lower()})")
                            if not is_valid_gender(names[n], "male") and not is_valid_gender(names[n], "female"):
                                prolog.assertz(f"genderless({names[n].lower()})")
                            
                            # Ensure parent existence
                            if not person_exists(names[-1], "person"):
                                prolog.assertz(f"person({names[-1].lower()})")
                                if not is_valid_gender(names[-1], "male") and not is_valid_gender(names[-1], "female"):
                                    prolog.assertz(f"genderless({names[-1].lower()})")
                            
                            learned = True
                        else:
                            unique = False
                            break

                if learned:
                    print("OK! I learned something.")
                elif related or not unique:
                    print("That's impossible!")
                elif not learned:
                    print(f"They are already children of {names[-1]}.")

            return True

        # Handle "Who are the children of [parent]?" question
        elif "children of" in sentence and "?" in sentence:
            if "Are" in sentence:
                names.pop(0)  # Remove "Are"
                all_children = all(
                    is_existing_relation("parent", names[-1], names[n]) or 
                    is_existing_relation("child", names[n], names[-1]) 
                    for n in range(len(names) - 1)
                )
                print("Yes!" if all_children else "No!")
            else:
                parent_name_match = re.search(r'children of (\w+)', sentence, re.IGNORECASE)
                if parent_name_match:
                    print_children_of_parent(parent_name_match.group(1))
                else:
                    return False
            return True

    # Check for "child" relationship
    elif "child" in sentence:
        # Handle statements (ends with a period)
        if "." in sentence:
            if len(names) == 2:
                child, parent = names[0].lower(), names[1].lower()
                excluded = ["child", "daughter", "son"]
                inverse_excluded = ["parent", "mother", "father"]

                # Validate logical consistency
                if child != parent and are_related(excluded, inverse_excluded, names[0], names[1]):
                    if not is_existing_relation("parent", parent, child):
                        if (
                            is_existing_relation("child", child, parent) or
                            (unique_relationship("mother", child) == 0 and 
                            unique_relationship("father", child) == 0 and 
                            unique_relationship("parent", child) < 2)
                        ):
                            # Assert parent-child relationship
                            prolog.assertz(f"parent({parent}, {child})")
                            prolog.assertz(f"person({child})")
                            if not is_valid_gender(child, "male") and not is_valid_gender(child, "female"):
                                prolog.assertz(f"genderless({child})")
                            
                            # Ensure parent existence
                            if not person_exists(parent, "person"):
                                prolog.assertz(f"person({parent})")
                                if not is_valid_gender(parent, "male") and not is_valid_gender(parent, "female"):
                                    prolog.assertz(f"genderless({parent})")

                            print("OK! I learned something.")
                        else:
                            print("That's impossible!")
                    else:
                        print(f"{names[0]} is already a child of {names[1]}.")
                else:
                    print("That's impossible!")
                return True
            else:
                return False

        # Handle yes/no questions about child relationships
        elif "?" in sentence:
            names.pop(0)
            if len(names) == 2:
                child, parent = names[0].lower(), names[1].lower()
                if is_existing_relation("parent", parent, child) or is_existing_relation("child", child, parent):
                    print("Yes!")
                else:
                    print("No!")
                return True
            return False
        
    # Check for aunt relationships
    elif "aunt" in sentence:
        return handle_aunt_uncle_relationship(
            sentence, 
            names, 
            "aunt", 
            "female", 
            ["aunt"], 
            []
        )

    # Check for uncle relationships
    elif "uncle" in sentence:
        return handle_aunt_uncle_relationship(
            sentence, 
            names, 
            "uncle", 
            "male", 
            ["uncle"], 
            []
        )
    
    # Check for cousin relationships
    elif "cousin" in sentence:
        # Handle statements (ends with a period)
        if "." in sentence:
            if len(names) == 2:
                cousin1, cousin2 = names[0].lower(), names[1].lower()
                excluded = ["cousin"]
                inverse_excluded = []

                # Validate logical consistency
                if cousin1 != cousin2 and are_related(excluded, inverse_excluded, names[0], names[1]):
                    if not is_existing_relation("cousin", cousin1, cousin2):
                        # Assert cousin relationship in Prolog
                        prolog.assertz(f"cousin({cousin1}, {cousin2})")
                        print("OK! I learned something.")
                    else:
                        print("They are already cousins.")
                else:
                    print("That's impossible!")
                return True
            else:
                return False

        # Handle questions (ends with a question mark)
        elif "?" in sentence:
            names.pop(0)
            if len(names) == 2:
                cousin1, cousin2 = names[0].lower(), names[1].lower()
                if is_existing_relation("cousin", cousin1, cousin2):
                    print("Yes!")
                else:
                    print("No!")
                return True
            else:
                return False

        
    # check for relatives relationships
    elif "relatives" in sentence:
        # Handle statements (ends with a period)
        if "." in sentence:
            if len(names) == 2:
                relative1, relative2 = names[0].lower(), names[1].lower()

                # Validate logical consistency
                if relative1 != relative2:
                    if not is_existing_relation("relatives", relative1, relative2):
                        # Assert relatives relationship in Prolog
                        prolog.assertz(f"relatives({relative1}, {relative2})")
                        print("OK! I learned something.")
                    else:
                        print("They are already relatives.")
                else:
                    print("That's impossible!")
                return True
            else:
                return False

        # Handle yes/no questions about relatives
        elif "?" in sentence:
            names.pop(0)
            if len(names) == 2:
                relative1, relative2 = names[0].lower(), names[1].lower()
                if is_existing_relation("relatives", relative1, relative2) or is_existing_relation("relatives", relative2, relative1):
                    print("Yes!")
                else:
                    print("No!")
                return True
            else:
                return False
            
    try:
        # Example return
        if not sentence:
            return "Invalid input given."
        # Add logic to process the input
        return "Processed successfully!"
    except Exception as e:
        return f"Error: {str(e)}"

# HELPER functions
# Function to check if a relationship exists between two names
def is_existing_relation(relation, name1, name2):
    return bool(list(prolog.query(f"{relation}({name1.lower()}, {name2.lower()})")))

def unique_relationship(relationship, name):
    result = list(prolog.query(f"findall(X, {relationship}(X, {name.lower()}), Relationship), length(Relationship, Length)"))
    return result[0]["Length"] if result else 0

def are_related(excluded, inverse_excluded, name1, name2):
    relations_copy = [r for r in relationships if r not in excluded]
    relations_inverse = [r for r in relationships if r not in inverse_excluded]

    return not any(
        is_existing_relation(rel, name1, name2) for rel in relations_copy
    ) and not any(
        is_existing_relation(rel, name2, name1) for rel in relations_inverse
    )

# function to check if a given name has a specified gender and relationship
def is_valid_gender(name, gender):
    try:
        return bool(list(prolog.query(f"{gender.lower()}({name.lower()})")))
    except Exception as e:
        print(f"Error: {e}")
        return False
    
# function to checking
def person_exists(name, rs):
    try:
        return bool(list(prolog.query(f"{rs.lower()}({name.lower()})")))
    except Exception as e:
        print(f"Error: {e}")
        return False

# Helper function to query Prolog and format results
def print_relationship(query, relationship, subject_name, result_label):
    results = list(prolog.query(query))
    if results:
        result_names = set([result[relationship].capitalize() for result in results])
        if len(result_names) == 1:
            print(f"The {result_label} of {subject_name} is {', '.join(result_names)}.")
        else:
            print(f"The {result_label} of {subject_name} are: {', '.join(result_names)}.")
    else:
        print(f"{subject_name} has no known {result_label.lower()}.")

def print_children_of_parent(parent_name):
    query = f"child(Child, {parent_name.lower()})"
    print_relationship(query, "Child", parent_name, "children")

def print_daughters_of_parent(parent_name):
    query = f"daughter(Daughter, {parent_name.lower()})"
    print_relationship(query, "Daughter", parent_name, "daughters")

def print_sons_of_parent(parent_name):
    query = f"son(Son, {parent_name.lower()})"
    print_relationship(query, "Son", parent_name, "sons")

def print_siblings(sibling_name):
    query = f"siblings(Sibling, {sibling_name.lower()})"
    print_relationship(query, "Sibling", sibling_name, "siblings")

def print_sisters(sibling_name):
    query = f"sister(Sister, {sibling_name.lower()})"
    print_relationship(query, "Sister", sibling_name, "sisters")

def print_brothers(sibling_name):
    query = f"brother(Brother, {sibling_name.lower()})"
    print_relationship(query, "Brother", sibling_name, "brothers")

def print_mother(child_name):
    query = f"mother(Mother, {child_name.lower()})"
    print_relationship(query, "Mother", child_name, "mother")

def print_father(child_name):
    query = f"father(Father, {child_name.lower()})"
    print_relationship(query, "Father", child_name, "father")

def print_parents(child_name):
    parent_query = f"parent(Parent, {child_name.lower()})"
    parents = list(prolog.query(parent_query))
    if parents:
        parent_names = {parent["Parent"].capitalize() for parent in parents}
        if len(parent_names) == 1:
            print(f"The parent of {child_name} is {', '.join(parent_names)}.")
        else:
            print(f"The parents of {child_name} are: {', '.join(parent_names)}.")
    else:
        print(f"{child_name} has no known parents.")

def update_gender(individual, new_gender):
    query = f"retract(genderless({individual.lower()})), assertz({new_gender}({individual.lower()}))."
    list(prolog.query(query))

if __name__ == "__main__":
    print("Enter a prompt below.")
    sentence = " "
    while sentence.lower() != "quit":
        sentence = input("\n> ")
        # Process the input sentence, handle invalid input
        if not process(sentence) and sentence.lower() != "quit":
            print("Invalid input given.")
