# Player Agency and Choice-Based Narrative Design

In game design, player agency is the feeling that the player's actions
have meaningful consequences in the game world. One of the most
effective ways to build agency is through choice-based narrative
mechanics. Instead of a linear story, players are presented with
branching dialogue trees and critical decisions that alter the state of
the game world or the relationships between characters.

Implementing these mechanics requires robust data structures to track
player decisions over time. A common approach is using state machines or
global variables to remember past choices. When designing these systems,
maintaining scene continuity is vital; if a player betrays a character in
chapter one, the game's logic must accurately reflect that tension in
later dialogue fragments to keep the narrative immersive.
