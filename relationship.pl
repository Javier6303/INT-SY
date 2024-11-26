% Declare dynamic predicates to allow updates at runtime
:- dynamic parent/2.
:- dynamic male/1.
:- dynamic female/1.
:- dynamic person/1.
:- dynamic sibling/2.
:- dynamic brother/2.
:- dynamic sister/2.
:- dynamic father/2.
:- dynamic mother/2.
:- dynamic grandparent/2.
:- dynamic grandfather/2.
:- dynamic grandmother/2.
:- dynamic child/2.
:- dynamic son/2.
:- dynamic daughter/2.
:- dynamic uncle/2.
:- dynamic aunt/2.
:- dynamic aunt_or_uncle/2.
:- dynamic cousin/2.
:- dynamic grandchild/2.
:- dynamic relative/2.
:- dynamic genderless/1.
:- dynamic safe_add_parent/2.

% Rules for family relationships

% Father/mother depend only on explicit facts
father(X, Y) :- male(X), parent(X, Y).
mother(X, Y) :- female(X), parent(X, Y).

% Child relationships
child(X, Y) :- parent(Y, X).
son(X, Y) :- male(X), parent(Y, X).
daughter(X, Y) :- female(X), parent(Y, X).

% Sibling relationships
siblings(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y.
brother(X, Y) :- male(X), siblings(X, Y).
sister(X, Y) :- female(X), siblings(X, Y).

% Grandparent relationships
grandparent(X, Y) :- parent(X, Z), parent(Z, Y).
grandfather(X, Y) :- male(X), grandparent(X, Y).
grandmother(X, Y) :- female(X), grandparent(X, Y).

% Uncle and Aunt relationships
uncle(X, Y) :- male(X), siblings(X, Z), parent(Z, Y).
aunt(X, Y) :- female(X), siblings(X, Z), parent(Z, Y).

% Combined Aunt or Uncle
aunt_or_uncle(X, Y) :- siblings(X, Z), parent(Z, Y).

% Cousins
cousin(X, Y) :-
    parent(PX, X),
    parent(PY, Y),
    siblings(PX, PY),
    X \= Y.

% Relatives
relative(X, Y) :-
    parent(X, Y);
    child(X, Y);
    siblings(X, Y);
    grandparent(X, Y);
    grandchild(X, Y);
    uncle(X, Y);
    aunt(X, Y);
    cousin(X, Y);
    aunt_or_uncle(X, Y);
    father(X, Y);
    mother(X, Y);
    brother(X, Y);
    sister(X, Y);
    son(X, Y);
    daughter(X, Y).

% Logical Constraints
contradiction :- male(X), female(X). % A person cannot be both male and female.
contradiction :- parent(X, X). % A person cannot be their own parent.

% Cycle Detection
has_cycle(X, Y) :-
    parent(Y, X). % Direct cycle: Y is already a parent of X
has_cycle(X, Y) :-
    parent(Z, X),
    has_cycle(Z, Y). % Indirect cycle: Transitive parent relationship

% Add a parent-child relationship only if it does not create a cycle
safe_add_parent(X, Y) :-
    \+ has_cycle(X, Y), % Ensure no cycle exists
    assertz(parent(X, Y)).

% Helpers to dynamically add facts
learn_fact(Fact) :-
    \+ contradiction,
    assert(Fact). % Add a fact dynamically if it's logically valid.
