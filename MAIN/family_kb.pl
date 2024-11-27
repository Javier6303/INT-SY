% Declare dynamic predicates to allow updates at runtime
:- dynamic parent/2.
:- dynamic male/1.
:- dynamic female/1.
:- dynamic person/1.
:- dynamic siblings/2.
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
:- dynamic relatives/2.
:- dynamic genderless/1.

% Rules for family relationships

% Father/mother depend only on explicit facts
father(X, Y) :- male(X), parent(X, Y).
mother(X, Y) :- female(X), parent(X, Y).

% Child relationships
child(X, Y) :- parent(Y, X).
child(X, Y) :- father(Y, X).
child(X, Y) :- mother(Y, X).
child(X, Y) :- daughter(X, Y).
child(X, Y) :- son(X, Y).
son(X, Y) :- male(X), parent(Y, X).
daughter(X, Y) :- female(X), parent(Y, X).

% Sibling relationships
% Siblings Rule

siblings(X, Y) :- (sister(X, Y); brother(X, Y); sister(Y, X); brother(Y, X)), X \= Y.
siblings(X, Y) :- (parent(Z, X); father(Z, X); mother(Z, X); brother(Z,X), sister(Z,X)), (parent(Z, Y); father(Z, Y); mother(Z, Y); brother(Z,Y); sister(Z,Y)), X \= Y.

brother(X, Y) :-
    male(X),
    (father(Z, X); mother(Z, X); parent(Z, X)),
    (father(Z, Y); mother(Z, Y); parent(Z, Y)),
    X \= Y.

sister(X, Y) :-
    female(X),
    (father(Z, X); mother(Z, X); parent(Z, X)),
    (father(Z, Y); mother(Z, Y); parent(Z, Y)),
    X \= Y.

% Grandparent relationships
grandparent(X, Y) :-
    parent(X, Z),
    parent(Z, Y),
    X \= Y.

grandfather(X, Y) :- male(X), father(X, Z), (parent(Z, Y); mother(Z, Y); father(Z, Y)).
grandmother(X, Y) :- female(X), mother(X, Z), (parent(Z, Y); mother(Z, Y); father(Z, Y)).

% Grandchild relationships
grandchild(X, Y) :- child(X, Z), grandparent(Y, Z).

% Uncle and Aunt relationships
uncle(X, Y) :- male(X), brother(X, Z), (parent(Z, Y); mother(Z, Y); father(Z, Y)).
uncle(X, Y) :- brother(X, Z), child(Y, Z).

aunt(X, Y) :- female(X), sister(X, Z), (parent(Z, Y); mother(Z, Y); father(Z, Y)).
aunt(X, Y) :- sister(X, Z), child(Y, Z).

% Combined Aunt or Uncle
aunt_or_uncle(X, Y) :- siblings(X, Z), (parent(Z, Y); father(Z, Y); mother(Z, Y)).

% Cousins
cousin(X, Y) :-
    parent(PX, X),
    parent(PY, Y),
    sibling(PX, PY),
    X \= Y.

% Relatives
relative(X, Y) :-
    parent(X, Y);
    child(X, Y);
    sibling(X, Y);
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

% Helpers to dynamically add facts
learn_fact(Fact) :-
    \+ contradiction,
    assert(Fact). % Add a fact dynamically if it's logically valid.
