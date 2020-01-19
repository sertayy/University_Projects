% sertay akpinar
% 2016400075
% compiling:  yes
% complete:  yes
:- [pokemon_data].

%Created and designed by Sertay Akpınar, 20.04.19.


% find pokemon evolution(+PokemonLevel, +Pokemon, -EvolvedPokemon)
% Evolves the pokemon if it reaches the required level
find_pokemon_evolution(PokemonLevel, Pokemon, EvolvedPokemon):-  
pokemon_evolution(Pokemon, Evolved, MinRequiredLevel),
PokemonLevel >= MinRequiredLevel -> find_pokemon_evolution(PokemonLevel, Evolved, EvolvedPokemon);
EvolvedPokemon=Pokemon.



%Evolves the pokemons features according to its pokemon level 
% pokemon level stats(+PokemonLevel, ?Pokemon, -PokemonHp, -PokemonAttack,-PokemonDefense)
pokemon_level_stats(PokemonLevel, Pokemon, PokemonHp, PokemonAttack, PokemonDefense):-
pokemon_stats(Pokemon, Types, HealthPoint, Attack, Defense),
PokemonHp is PokemonLevel*2+HealthPoint, PokemonAttack is PokemonLevel+Attack, PokemonDefense is PokemonLevel+Defense.



%this is a helper predicate for iterating the defender types, and multipliers, used in single_type_multiplier
recursive_lists([H | T],[Head | Tail], Multiplier, DefenderType, AttackerType):-
(DefenderType = Head, Multiplier = H; 
	recursive_lists(T,Tail,Multiplier,DefenderType, AttackerType)).



%Finds the AttackerType, DefenderType or the Multiplier of these two
% single_type_multiplier(?AttackerType, ?DefenderType, ?Multiplier)
single_type_multiplier(AttackerType, DefenderType, Multiplier):-
type_chart_attack(AttackerType, L), 
pokemon_types(List),
recursive_lists(L, List, Multiplier, DefenderType, AttackerType).



%used to find double-type advantage/disadvantage multiplier
% type_multiplier(?AttackerType, +DefenderTypeList, ?Multiplier)
type_multiplier(_, [] , 1.0).
type_multiplier(AttackerType, [H|T] , Multiplier):-
single_type_multiplier(AttackerType, H, M1),
type_multiplier(AttackerType, T, M2),
Multiplier is M1*M2.



%used to find type multiplier between two Pokemons or different attacker/defender Pokemon that achieves a given multiplier
%pokemon type multiplier(?AttackerPokemon, ?DefenderPokemon, ?Multiplier)
pokemon_type_multiplier(AttackerPokemon, DefenderPokemon, Multiplier):-
pokemon_stats(AttackerPokemon, [H|T], HealthPoint, Attack, Defense),
pokemon_stats(DefenderPokemon, [H1|T1], Health, Attack1, Defense1),
predicate([H|T],[H1|T1],Multiplier).


%helper predicate used in type_multiplier, gives the maximum multiplier
predicate([H|T],[H1|T1],Multiplier):-
type_multiplier(H,[H1|T1],M1),  (T = [T2|_] -> (type_multiplier(T2,[H1|T1],M2),
Multiplier is max(M1,M2)); Multiplier is M1). 



%pokemon attack(+AttackerPokemon, +AttackerPokemonLevel, +DefenderPokemon,+DefenderPokemonLevel, -Damage)
pokemon_attack(AttackerPokemon, AttackerPokemonLevel, DefenderPokemon,DefenderPokemonLevel, Damage):-

pokemon_type_multiplier(AttackerPokemon,DefenderPokemon,Multiplier),
pokemon_level_stats(AttackerPokemonLevel, AttackerPokemon, HealthAttack, Attack, Defense),
pokemon_level_stats(DefenderPokemonLevel,DefenderPokemon,HealthDefend,AttackD,DefenseD),
Damage is (0.5 * AttackerPokemonLevel*(Attack/DefenseD)*Multiplier)+1.



%simulates a fight between two Pokemon then finds health points of each Pokemon at the end of the fight and the number of rounds.
%pokemon fight(+Pokemon1, +Pokemon1Level, +Pokemon2, +Pokemon2Level, -Pokemon1Hp, -Pokemon2Hp, -Rounds):-
pokemon_fight(Pokemon1, Pokemon1Level, Pokemon2, Pokemon2Level, Pokemon1Hp, Pokemon2Hp, Rounds):-

%calculates the damage points of each pokemons
pokemon_attack(Pokemon1, Pokemon1Level, Pokemon2,Pokemon2Level, Damage1),
pokemon_attack(Pokemon2,Pokemon2Level, Pokemon1, Pokemon1Level, Damage2),

%Calculates the health point according to their levels
pokemon_level_stats(Pokemon1Level, Pokemon1, P1Hp, _, _),
pokemon_level_stats(Pokemon2Level,Pokemon2,P2Hp,_,_),
pokemon_fight_2(P1Hp, P2Hp, Rounds, Damage1, Damage2, Pokemon1Hp, Pokemon2Hp).


%helper predicate used in pokemon_fight
pokemon_fight_2(P1Hp, P2Hp, Rounds, Damage1, Damage2, Don1, Don2):-

%calculates the new health point after one attack
NPokemon2Hp is P2Hp - Damage1,  
NPokemon1Hp is P1Hp - Damage2,

%fight is not over so keep figthing recursively, calculates the Rounds recursively
((NPokemon1Hp > 0 , NPokemon2Hp > 0) -> 
(pokemon_fight_2(NPokemon1Hp, NPokemon2Hp, NRounds, Damage1, Damage2, Don1, Don2),
Rounds is NRounds + 1);

%Initialize the rounds and equalize the last health points
(Rounds is 1, Don1 = NPokemon1Hp, Don2 = NPokemon2Hp)).



%simulates a tournament between two Pokemon trainers then finds the winner Pokemon trainer of each fight
%pokemon tournament(+PokemonTrainer1, +PokemonTrainer2, -WinnerTrainerList)
pokemon_tournament(PokemonTrainer1, PokemonTrainer2, WinnerTrainerList):-
	
	pokemon_trainer(PokemonTrainer1, PokemonList1, PokemonLevel1),
	pokemon_trainer(PokemonTrainer2, PokemonList2, PokemonLevel2),
	pokemon_tournament_2(PokemonTrainer1, PokemonList1, PokemonLevel1, PokemonTrainer2, PokemonList2, PokemonLevel2, WinnerTrainerList),!.

pokemon_tournament_2(_, [], [], _, [], [], []).	


%helper predicate used in pokemon_tournament
pokemon_tournament_2(PokemonTrainer1, [Head1|Tail1], [HeadLevel1|TailLevel1], PokemonTrainer2, [Head2|Tail2], [HeadLevel2|TailLevel2], [Head|List]):-
	
	%finds the evolved version of each pokemon
	find_pokemon_evolution(HeadLevel1, Head1, EvolvedPokemon1),
	find_pokemon_evolution(HeadLevel2, Head2, EvolvedPokemon2),
	
	%continues the fights by recalling pokemon_tournament_2 and updates the lists in parameters
	pokemon_fight(EvolvedPokemon1, HeadLevel1, EvolvedPokemon2, HeadLevel2, Pokemon1Hp, Pokemon2Hp, _),
	(Pokemon1Hp >= Pokemon2Hp -> 
		(Head = PokemonTrainer1, 
			pokemon_tournament_2(PokemonTrainer1, Tail1, TailLevel1, PokemonTrainer2, Tail2, TailLevel2, List));
		(Head = PokemonTrainer2, 
			pokemon_tournament_2(PokemonTrainer1, Tail1, TailLevel1, PokemonTrainer2, Tail2, TailLevel2, List))).



%a shortcut to access all pokemons
pokemon_members(List) :-
	findall(Pokemon, pokemon_stats(Pokemon, _, _, _ ,_), List).


%finds the best Pokemon against the given EnemyPokemon where the both Pokemon’s levels are LevelCap
%best pokemon(+EnemyPokemon, +LevelCap, -RemainingHP, -BestPokemon)
best_pokemon(EnemyPokemon, LevelCap, RemainingHp, BestPokemon) :-

	pokemon_members(PokemonList),		%-9999999999 represents a very small number that no RemainingHps can reach, like we equalize this number to the remaining Hp before the fights
	best_pokemon_2(EnemyPokemon, LevelCap, PokemonList, -9999999999, _, BestPokemon, RemainingHp).

best_pokemon_2(_, _, [], RemainHP, BestPoke, BestPoke, RemainHP).

best_pokemon_2(EnemyPokemon, LevelCap,[HeadPokemon|TailPokemon], RemainHP, BestPoke, BestPokemon, RemainingHp) :-
	pokemon_fight(EnemyPokemon, LevelCap, HeadPokemon, LevelCap, _, HeadPokemonHP, _),
	
	%If the RemainingHp is greater than or equal to next pokemon’s hp, remaining hp and best pokemon dont change.
	(RemainHP >= HeadPokemonHP  ->
		best_pokemon_2(EnemyPokemon, LevelCap, TailPokemon, RemainHP, BestPoke, BestPokemon, RemainingHp); 
		%else remaining hp is the next pokemon’s hp, and best pokemon is the next pokemon
		best_pokemon_2(EnemyPokemon, LevelCap, TailPokemon, HeadPokemonHP, HeadPokemon, BestPokemon, RemainingHp)).



%best pokemon team(+OpponentTrainer, -PokemonTeam)
best_pokemon_team(OpponentTrainer, PokemonTeam):-

	%finds the pokemon List and their levels
	pokemon_trainer(OpponentTrainer, PokemonList,PokemonLevels),
	best_pokemon_team_2(PokemonList, PokemonLevels, PokemonTeam).


%helper predicate used in best_pokemon_team, iterating all the elements of the lists recursively
	best_pokemon_team_2([HeadPokemon|TailPokemon], [HeadLevel|TailLevel], [HeadTeam|TailTeam]):-

	
	find_pokemon_evolution(HeadLevel, HeadPokemon, EvolvedHeadPokemon), %evolves the pokemon if it is possible   
	best_pokemon(EvolvedHeadPokemon, HeadLevel, _, HeadTeam),			%find the best pokemon against the enemy pokemon add it to the Pokemon Team
	best_pokemon_team_2(TailPokemon, TailLevel, TailTeam).				

best_pokemon_team_2([], [], []).



%finds the best Pokemon Team against the given OpponentTrainer where the levels of each Pokemon of our best Pokemon
%pokemon types(+TypeList, +InitialPokemonList, -PokemonList)
pokemon_types(TypeList, InitialPokemonList, PokemonList):-

findall(Pokemon, (member(Pokemon, InitialPokemonList), pokemon_types_2(TypeList, Pokemon)), PokemonList).

pokemon_types_2([H|TypeListTail], Pokemon):-

pokemon_stats(Pokemon, PokemonTypeList, _, _, _),
((member(H, PokemonTypeList),!); pokemon_types_2(TypeListTail, Pokemon)).



%generates a Pokemon team based on liked and disliked types and some criteria
%generate pokemon team(+LikedTypes, +DislikedTypes, +Criterion, +Count, -PokemonTeam)
generate_pokemon_team(LikedTypes, DislikedTypes, Criterion, Count, PokemonTeam):-

pokemon_members(PokemonList),
pokemon_types(LikedTypes, PokemonList, LikedPokemons), %finds pokemons that have at least one liked type (A)
pokemon_types(DislikedTypes, PokemonList, DislikedPokemons), %%finds pokemons that have at least one disliked type (B)

findall(Pokemon,(member(Pokemon, LikedPokemons),(\+member(Pokemon, DislikedPokemons))), DesiredPokemonList), %finds the pokemons that have liked types but dont have disliked types (A-B)

(Criterion=h -> 
getH(DesiredPokemonList, PairedFeature); 
(Criterion=a -> getA(DesiredPokemonList, PairedFeature);
getD(DesiredPokemonList, PairedFeature))),

sort(0, >=, PairedFeature, PairedFeatureSorted), %sorts the Pokemons with its feature in a descending order
generate_pokemon_team_2(PairedFeatureSorted, PokemonTemp, PokemonTeam1), %PokemonTeam1 is the all pokemons with its features in a descending order according to the criterion

length(PokemonTeam, Count),  %Equalizes the length of the PokemonTeam list
append(PokemonTeam, _, PokemonTeam1).  %gives the first count elements of the PokemonTeam1


generate_pokemon_team_2([], [], []).

%helper recursive method used in generate_pokemon_team
generate_pokemon_team_2([PokemonTeamSortedH|PokemonTeamSortedT], [PokemonTempH|PokemonTempT], [PokemonTeamH|PokemonTeamT]):-

[_,PokemonTempH] = PokemonTeamSortedH,  %equalize the pokemon
pokemon_stats(PokemonTempH, _, HP, A, D), %finds the equalized pokemon’s features
PokemonTeamH = [PokemonTempH, HP, A, D],   % and equalize the pokemon with its features to a new list
generate_pokemon_team_2(PokemonTeamSortedT, PokemonTeamTempT, PokemonTeamT).


getA([], []).
getD([], []).
getH([], []).

%pairs the pokemon with its attack value
getA([HPokemon|TPokemon], [AttackH|AttackT]):-
pokemon_stats(HPokemon, _, _, A, _),
AttackH = [A,HPokemon],
getA(TPokemon, AttackT).

%pairs the pokemon with its defense point
getD([HPokemon|TPokemon], [DefenseH|DefenseT]):-
pokemon_stats(HPokemon, _, _, _, D),
DefenseH = [D, HPokemon],
getD(TPokemon, DefenseT).

%pairs the pokemon with its health point
getH([HPokemon|TPokemon], [HealthH|HealthT]):-
pokemon_stats(HPokemon, _, HP, _, _),
HealthH = [HP,HPokemon],
getH(TPokemon, HealthT).






