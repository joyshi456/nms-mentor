Lesson: “The Magic Split — Coins, Logic, and a Dash of Chess” (35–40 min)
Goals (very plain)

Say a statement clearly (something that’s true or false).

Know converse / inverse / contrapositive as “remixed statements.”

Do the coin magic: make two piles with the same number of heads while blindfolded—and explain why it works.

Spot a chess invariant (knight changes color every move).

Flow

Warm-up (5 min): Statement or not?
Show 4 short sentences; kids label each: “statement / not a statement”.

“Flip exactly H coins and the piles will match in heads.” (statement)

“Split the coins!” (not a statement)

“Both piles have heads.” (ambiguous → refine)

Penny trick (10–12 min):

Setup: “There are N coins, exactly H are heads.”

Claim (theorem): If you take any H coins and flip all of them, then both piles end with the same number of heads.

Kids try small numbers with real coins (e.g., N=6, H=2).

Explain (8–10 min):

Guide them to: “Let the H coins you grabbed have x heads. Then they had H−x tails. After flipping, that pile now has H−x heads. The other pile already had H−x heads (because total heads was H). So they match.”

Connect to last week: turn this into a clear statement. Then make its converse and contrapositive:

Statement S: If you flip any H chosen coins, then the two piles end with the same number of heads.

Converse: If the two piles end with the same number of heads, then you flipped exactly H coins. (⚠️ not necessarily true)

Contrapositive: If the two piles do not end with the same number of heads, then you did not flip exactly H coins. (logically equivalent to S)

Mini-chess closer (5–8 min):

Knight-color invariant: A knight always lands on the opposite color.

Kid claim: “If a knight starts on a dark square and makes an odd number of moves, it ends on a light square.” (Converse/contrapositive practice.)

Exit tickets (2–3 min):

One sentence why the coin trick works.

Label S / Converse / Contrapositive for the coin claim.

Knight color one-liner.

Streamlit demo (simple, intuitive logging to TXT)

Prompts your two students will see:

S1 – Statement Check: Is this a statement? (You can edit the text inline.)

P – Penny Claim: State the coin trick in one sentence.

L – Remix: Write the converse and contrapositive of your coin claim.

E – Explain: Why does flipping H coins make the piles match? (kid proof)

C – Chess Mini: Knight color claim—true or false, and why?

Logging: each submission appends to ./.lesson_log/submissions.txt
YYYY-MM-DD HH:MM:SS<TAB>Name<TAB>PromptID<TAB>Answer