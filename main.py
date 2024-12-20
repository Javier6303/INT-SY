import re
from pyswip import Prolog

prolog = Prolog()
prolog.consult("relationship.pl")

RELATIONSHIPS = {
    "siblings": {},
    "sister": {"gender": "female"},
    "brother": {"gender": "male"},
    "mother": {"gender": "female"},
    "father": {"gender": "male"},
    "parent": {},
    "child": {},
    "daughter": {"gender": "female"},
    "son": {"gender": "male"},
    "grandmother": {"gender": "female"},
    "grandfather": {"gender": "male"},
    "aunt": {"gender": "female"},
    "uncle": {"gender": "male"},
    "cousin": {},
    "grandchild": {},
    "relative": {}
}

def execute_query(query):
    """Run a Prolog query and return results."""
    try:
        return list(prolog.query(query))
    except Exception as e:
        print(f"Error: {e}")
        return []

def is_existing_relation(relation, name1, name2=None):
    """Check if a specific relationship exists."""
    name1, name2 = name1.lower(), (name2.lower() if name2 else None)
    query = f"{relation}({name1}, {name2})" if name2 else f"{relation}({name1})"
    return bool(execute_query(query))


def get_all_parents(child):
    """Retrieve all parents of a given child."""
    query = f"parent(X, {child.lower()})"
    results = execute_query(query)
    return [result["X"] for result in results]

def detect_cycle(name1, name2):
    """
    Detect if adding a parent-child relationship would create a cycle.
    """
    def dfs(current, target, visited):
        if current == target:
            return True  # Cycle detected
        if current in visited:
            return False
        visited.add(current)
        parents = get_all_parents(current)
        for parent in parents:
            if dfs(parent, target, visited):
                return True
        return False

    # Check if there is a path from name2 to name1
    return dfs(name2.lower(), name1.lower(), set())

def get_gender(name):
    """Determine the gender of a person based on Prolog facts."""
    if is_existing_relation("male", name):
        return "male"
    if is_existing_relation("female", name):
        return "female"
    return None

def check_gender(name, gender):
    """Validate if the specified gender matches the person's gender."""
    current_gender = get_gender(name)
    if current_gender and current_gender != gender:
        return False 
    return True

def assert_relationship(relation, name1, name2, gender=None):
    """Assert a specific relationship."""
    name1, name2 = name1.lower(), name2.lower()

    if name1 == name2:
        raise ValueError(f"That's impossible! A person cannot be their own {relation}.")

    # Check for circular relationships (e.g., in parent-child cases)
    if relation in ["father", "mother", "parent"]:
        if detect_cycle(name1, name2):
            raise ValueError(f"That's impossible! Adding {relation} between {name1} and {name2} would create a circular ancestry.")

    # Check if the relationship already exists
    if is_existing_relation(relation, name1, name2):
        raise ValueError(f"{name1.capitalize()} is already the {relation} of {name2.capitalize()}.")

    # Check gender consistency
    if gender:
        if not check_gender(name1, gender):
            raise ValueError(f"That's impossible! {name1.capitalize()} is not {gender}.")

    # Add the relationship
    if relation in ["father", "mother", "parent"]:
        result = execute_query(f"safe_add_parent({name1}, {name2})")
        if not result:
            raise ValueError(f"That's impossible! Adding {relation} between {name1} and {name2} would create a cycle.")
    elif relation in ["siblings", "sister", "brother"]:
        # Use siblings_direct to prevent recursion issues
        prolog.assertz(f"siblings_direct({name1.lower()}, {name2.lower()})")
    else:
        prolog.assertz(f"{relation}({name1}, {name2})")

    # Add gender if applicable
    if gender:
        prolog.assertz(f"{gender}({name1})")

    print("OK! I learned something.")

def reload_prolog():
    """Reload the Prolog knowledge base."""
    try:
        prolog.consult("relationship.pl")
        print("Prolog knowledge base reloaded.")
    except Exception as e:
        print(f"Failed to reload Prolog file: {e}")


def process_assertion(sentence):
    """Process assertion sentences dynamically."""
    try:
        
        # Pattern: "<Name1> and <Name2> are siblings."
        match = re.match(r"([A-Z][a-z]*) and ([A-Z][a-z]*) are siblings\.", sentence)
        if match:
            name1, name2 = match.groups()
            assert_relationship("siblings", name1, name2)
            assert_relationship("siblings", name2, name1)
            return True

        # Pattern: "<Name1> is a sister of <Name2>."
        match = re.match(r"([A-Z][a-z]*) is a sister of ([A-Z][a-z]*)\.", sentence)
        if match:
            name1, name2 = match.groups()
            assert_relationship("sister", name1, name2, "female")
            return True

        # Pattern: "<Name1> is a brother of <Name2>."
        match = re.match(r"([A-Z][a-z]*) is a brother of ([A-Z][a-z]*)\.", sentence)
        if match:
            name1, name2 = match.groups()
            assert_relationship("brother", name1, name2, "male")
            return True

        # Pattern: "<Name1> is the mother of <Name2>."
        match = re.match(r"([A-Z][a-z]*) is the mother of ([A-Z][a-z]*)\.", sentence)
        if match:
            name1, name2 = match.groups()
            assert_relationship("mother", name1, name2, "female")
            return True

        # Pattern: "<Name1> is the father of <Name2>."
        match = re.match(r"([A-Z][a-z]*) is the father of ([A-Z][a-z]*)\.", sentence)
        if match:
            name1, name2 = match.groups()
            assert_relationship("father", name1, name2, "male")
            return True
        
        # Pattern: "<Name1> is a grandmother of <Name2>."
        match = re.match(r"([A-Z][a-z]*) is a grandmother of ([A-Z][a-z]*)\.", sentence)
        if match:
            name1, name2 = match.groups()
            assert_relationship("grandmother", name1, name2)
            return True
        
        # Pattern: "<Name1> is a grandfather of <Name2>."
        match = re.match(r"([A-Z][a-z]*) is a grandfather of ([A-Z][a-z]*)\.", sentence)
        if match:
            name1, name2 = match.groups()
            assert_relationship("grandfather", name1, name2)
            return True
        
        # Pattern: "<Name1> is a child of <Name2>."
        match = re.match(r"([A-Z][a-z]*) is a child of ([A-Z][a-z]*)\.", sentence)
        if match:
            name1, name2 = match.groups()
            assert_relationship("child", name1, name2)
            return True

        # Pattern: "<Name1> is a daughter of <Name2>."
        match = re.match(r"([A-Z][a-z]*) is a daughter of ([A-Z][a-z]*)\.", sentence)
        if match:
            name1, name2 = match.groups()
            assert_relationship("daughter", name1, name2, "female")
            return True

        # Pattern: "<Name1> is a son of <Name2>."
        match = re.match(r"([A-Z][a-z]*) is a son of ([A-Z][a-z]*)\.", sentence)
        if match:
            name1, name2 = match.groups()
            assert_relationship("son", name1, name2, "male")
            return True

        # Pattern: "<Name1> is an uncle of <Name2>."
        match = re.match(r"([A-Z][a-z]*) is an uncle of ([A-Z][a-z]*)\.", sentence)
        if match:
            name1, name2 = match.groups()
            assert_relationship("uncle", name1, name2, "male")
            return True

        # Pattern: "<Name1> is an aunt of <Name2>."
        match = re.match(r"([A-Z][a-z]*) is an aunt of ([A-Z][a-z]*)\.", sentence)
        if match:
            name1, name2 = match.groups()
            assert_relationship("aunt", name1, name2, "female")
            return True

        # Pattern: "<Name1> and <Name2> are the parents of <Name3>."
        match = re.match(r"Are ([A-Z][a-z]*) and ([A-Z][a-z]*) the parents of ([A-Z][a-z]*)\.", sentence)
        if match:
            name1, name2, child = match.groups()
            assert_relationship("parent", name1, child)
            assert_relationship("parent", name2, child)
            return True

        # Pattern: "<Name1>, <Name2>, and <Name3> are children of <Name4>."
        match = re.match(r"Are ([A-Z][a-z]*), ([A-Z][a-z]*), and ([A-Z][a-z]*) are children of ([A-Z][a-z]*)\.", sentence)
        if match:
            child1, child2, child3, parent = match.groups()
            assert_relationship("parent", parent, child1)
            assert_relationship("parent", parent, child2)
            assert_relationship("parent", parent, child3)
            return True

    except ValueError as e:
        print(e)
        return True 

    return False


def process_query(sentence):
    """Handle query sentences."""
    # Pattern: "Are <Name1> and <Name2> siblings?"
    match = re.match(r"Are ([A-Z][a-z]*) and ([A-Z][a-z]*) siblings\?", sentence)
    if match:
        name1, name2 = match.groups()
        exists = is_existing_relation("siblings", name1, name2)
        print("Yes!" if exists else "No!")
        return True

    # Pattern: "Is <Name1> a sister of <Name2>?"
    match = re.match(r"Is ([A-Z][a-z]*) a sister of ([A-Z][a-z]*)\?", sentence)
    if match:
        name1, name2 = match.groups()
        exists = is_existing_relation("sister", name1, name2)
        print("Yes!" if exists else "No!")
        return True

    # Pattern: "Is <Name1> a brother of <Name2>?"
    match = re.match(r"Is ([A-Z][a-z]*) a brother of ([A-Z][a-z]*)\?", sentence)
    if match:
        name1, name2 = match.groups()
        exists = is_existing_relation("brother", name1, name2)
        print("Yes!" if exists else "No!")
        return True

    # Pattern: "Is <Name1> the mother of <Name2>?"
    match = re.match(r"Is ([A-Z][a-z]*) the mother of ([A-Z][a-z]*)\?", sentence)
    if match:
        name1, name2 = match.groups()
        exists = is_existing_relation("mother", name1, name2)
        print("Yes!" if exists else "No!")
        return True

    # Pattern: "Is <Name1> the father of <Name2>?"
    match = re.match(r"Is ([A-Z][a-z]*) the father of ([A-Z][a-z]*)\?", sentence)
    if match:
        name1, name2 = match.groups()
        exists = is_existing_relation("father", name1, name2)
        print("Yes!" if exists else "No!")
        return True

    # Pattern: "Are <Name1> and <Name2> the parents of <Name3>?"
    match = re.match(r"Are ([A-Z][a-z]*) and ([A-Z][a-z]*) the parents of ([A-Z][a-z]*)\?", sentence)
    if match:
        parent1, parent2, child = match.groups()
        exists1 = is_existing_relation("parent", parent1, child)
        exists2 = is_existing_relation("parent", parent2, child)
        print("Yes!" if exists1 and exists2 else "No!")
        return True
    
    # Pattern: "Is <Name1> a grandmother of <Name2>?"
    match = re.match(r"Is ([A-Z][a-z]*) a grandmother of ([A-Z][a-z]*)\?", sentence)
    if match:
        name1, name2 = match.groups()
        exists = is_existing_relation("grandmother", name1, name2)
        print("Yes!" if exists else "No!")
        return True

    # Pattern: "Is <Name1> a daughter of <Name2>?"
    match = re.match(r"Is ([A-Z][a-z]*) a daughter of ([A-Z][a-z]*)\?", sentence)
    if match:
        name1, name2 = match.groups()
        exists = is_existing_relation("daughter", name1, name2)
        print("Yes!" if exists else "No!")
        return True

    # Pattern: "Is <Name1> a son of <Name2>?"
    match = re.match(r"Is ([A-Z][a-z]*) a son of ([A-Z][a-z]*)\?", sentence)
    if match:
        name1, name2 = match.groups()
        exists = is_existing_relation("son", name1, name2)
        print("Yes!" if exists else "No!")
        return True

    # Pattern: "Is <Name1> a child of <Name2>?"
    match = re.match(r"Is ([A-Z][a-z]*) a child of ([A-Z][a-z]*)\?", sentence)
    if match:
        name1, name2 = match.groups()
        exists = is_existing_relation("child", name1, name2)
        print("Yes!" if exists else "No!")
        return True

    # Pattern: "Are <Name1>, <Name2>, and <Name3> children of <Name4>?"
    match = re.match(r"Are ([A-Z][a-z]*), ([A-Z][a-z]*), and ([A-Z][a-z]*) children of ([A-Z][a-z]*)\?", sentence)
    if match:
        child1, child2, child3, parent = match.groups()
        exists1 = is_existing_relation("parent", parent, child1)
        exists2 = is_existing_relation("parent", parent, child2)
        exists3 = is_existing_relation("parent", parent, child3)
        print("Yes!" if exists1 and exists2 and exists3 else "No!")
        return True

    # Pattern: "Is <Name1> an uncle of <Name2>?"
    match = re.match(r"Is ([A-Z][a-z]*) an uncle of ([A-Z][a-z]*)\?", sentence)
    if match:
        name1, name2 = match.groups()
        exists = is_existing_relation("uncle", name1, name2)
        print("Yes!" if exists else "No!")
        return True
    
    #whowhowhowho

    # Pattern: "Is <Name1> a grandfather of <Name2>?"
    match = re.match(r"Is ([A-Z][a-z]*) a grandfather of ([A-Z][a-z]*)\?", sentence)
    if match:
        name1, name2 = match.groups()
        exists = is_existing_relation("grandfather", name1, name2)
        print("Yes!" if exists else "No!")
        return True
    
    #whowhowho

    # Pattern: "Is <Name1> an aunt of <Name2>?"
    match = re.match(r"Is ([A-Z][a-z]*) an aunt of ([A-Z][a-z]*)\?", sentence)
    if match:
        name1, name2 = match.groups()
        exists = is_existing_relation("aunt", name1, name2)
        print("Yes!" if exists else "No!")
        return True

    # Pattern: "Are <Name1> and <Name2> relatives?"
    match = re.match(r"Are ([A-Z][a-z]*) and ([A-Z][a-z]*) relatives\?", sentence)
    if match:
        name1, name2 = match.groups()
        exists = is_existing_relation("relative", name1, name2)
        print("Yes!" if exists else "No!")
        return True
    
    # If no pattern matched
    return False


def process_sentence(sentence):
    """Process both assertions and queries."""
    if process_assertion(sentence):
        return True
    if process_query(sentence):
        return True
    return False

if __name__ == "__main__":
    reload_prolog()
    print("Enter a prompt below.")
    while (sentence := input("\n> ").strip()) != "quit":
        if not process_sentence(sentence):
            print("Invalid input given.")

