import streamlit as st
from datetime import datetime
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="The Magic Split", layout="centered")

# --- Session State Initialization ---
if "current_module" not in st.session_state:
    st.session_state.current_module = 0
if "current_subproblem" not in st.session_state:
    st.session_state.current_subproblem = 0
if "completed_modules" not in st.session_state:
    st.session_state.completed_modules = set()
if "completed_subproblems" not in st.session_state:
    st.session_state.completed_subproblems = {}
if "student_name" not in st.session_state:
    st.session_state.student_name = ""

# --- Logging Setup ---
DATA_DIR = Path("./.lesson_log")
DATA_DIR.mkdir(exist_ok=True)
LOG_FILE = DATA_DIR / "submissions.txt"

# Google Sheets setup
def get_google_sheet():
    """Connect to Google Sheets if credentials are available."""
    try:
        # Check if running on Streamlit Cloud with secrets
        if "gcp_service_account" in st.secrets:
            credentials = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
            )
            client = gspread.authorize(credentials)
            sheet_url = st.secrets.get("sheet_url", "")
            if sheet_url:
                return client.open_by_url(sheet_url).sheet1
        return None
    except Exception as e:
        st.error(f"Google Sheets connection error: {e}")
        return None

def log_line(name: str, pid: str, answer: str):
    """Log answer to both local file and Google Sheets (if available)."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Always log locally
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{ts}\t{name.strip()}\t{pid}\t{answer.strip()}\n")

    # Try to log to Google Sheets
    try:
        sheet = get_google_sheet()
        if sheet:
            sheet.append_row([ts, name.strip(), pid, answer.strip()])
    except Exception as e:
        # Silently fail - local logging still works
        pass

# --- Problem Definitions ---
MODULES = [
    {
        "id": "logic",
        "title": "Module 1: Logic & Statements",
        "description": "Master statements, negations, converses, and contrapositives with fun examples!",
        "subproblems": [
            {
                "id": "statements",
                "title": "1.1: What Makes a Statement?",
                "problem": """
**🎯 Statement or Not?**

A mathematical statement is a sentence that is either TRUE or FALSE (but not both).

**Analyze this sentence:** "Pikachu is an Electric-type Pokémon."

Can this sentence be clearly identified as true or false?
                """,
                "prompt": "Is this sentence a mathematical statement? Answer 'yes' or 'no' and explain why.",
                "expected_keywords": ["yes", "statement", "true", "false"],
                "hint": "Can you verify this as definitely true or false?"
            },
            {
                "id": "negations",
                "title": "1.2: The Art of Negation",
                "problem": """
**🎯 Write the Opposite**

**Original Statement:** "All Pokémon in Generation 1 are from the Kanto region."

The negation (opposite) of "All X are Y" is "Not all X are Y" or "At least one X is not Y."
                """,
                "prompt": "Write the negation of this statement.",
                "expected_keywords": ["not all", "some", "at least one", "not", "kanto"],
                "hint": "You can write: 'Not all Pokémon in Generation 1...' or 'At least one Pokémon in Generation 1 is not...'"
            },
            {
                "id": "conditionals",
                "title": "1.3: If-Then Statements",
                "problem": """
**🎯 True or False?**

**Statement:** "If a Pokémon is a Charizard, then it is a Fire-type."

Think about what you know about Charizard's type.
                """,
                "prompt": "Is this statement true or false?",
                "expected_keywords": ["true", "fire", "type"],
                "hint": "Charizard is a Fire/Flying type Pokémon."
            },
            {
                "id": "converse",
                "title": "1.4: The Converse Flip",
                "problem": """
**🎯 Write the Converse**

**Original:** "If a Pokémon knows Surf, then it can learn Water-type moves."

The converse switches the if and then parts.
                """,
                "prompt": "Write the converse of this statement.",
                "expected_keywords": ["if", "water", "surf", "learn", "knows"],
                "hint": "Switch the parts: 'If a Pokémon can learn Water-type moves, then...'"
            },
            {
                "id": "contrapositive",
                "title": "1.5: The Contrapositive Challenge",
                "problem": """
**🎯 Write the Contrapositive**

**Original:** "If a Pokémon is Legendary, then it has high base stats."

The contrapositive negates both parts AND switches them:
"If [NOT conclusion], then [NOT hypothesis]."
                """,
                "prompt": "Write the contrapositive of this statement.",
                "expected_keywords": ["if", "not", "legendary", "stats", "does not"],
                "hint": "Start with: 'If a Pokémon does not have high base stats, then...'"
            }
        ]
    },
    {
        "id": "coins",
        "title": "Module 2: The Blindfolded Penny Challenge",
        "description": "Solve an impossible-seeming puzzle using logic and clever strategy!",
        "subproblems": [
            {
                "id": "understand_setup",
                "title": "2.1: The Challenge",
                "problem": """
**🎭 The Blindfolded Penny Puzzle**

You're blindfolded at a table with 16 pennies scattered on it. You can't see which are heads or tails, but you can feel and count them.

**What you know:**
- Total pennies: 16
- Heads-up pennies: 12 (someone tells you this)
- Tails-up pennies: 4

**Your goal:** Divide the pennies into two separate piles so that both piles have the SAME number of heads.

**You can:** Move pennies around, flip any penny over.
                """,
                "prompt": "Is this challenge possible? Answer 'yes' or 'no' and explain your reasoning.",
                "expected_keywords": ["yes", "possible", "flip", "move"],
                "hint": "Think about whether you can manipulate the coins to achieve equal heads in both piles.",
                "image": "2-1a.png"
            },
            {
                "id": "first_attempt",
                "title": "2.2: A Simple Strategy?",
                "problem": """
**🤔 Strategy Attempt**

You might think: "I'll just put 8 pennies in each pile randomly!"

**Example random split:**
- Pile A: 8 pennies (maybe 6 heads, 2 tails)
- Pile B: 8 pennies (maybe 6 heads, 2 tails)

**Problem:** The heads aren't equal! And since you're blindfolded, you can't tell which pennies are heads to fix this.
                """,
                "prompt": "Why doesn't random splitting work for this challenge?",
                "expected_keywords": ["random", "blindfolded", "can't see", "don't know"],
                "hint": "You can't see which pennies are heads, so you can't control the distribution."
            },
            {
                "id": "key_insight",
                "title": "2.3: The Key Insight",
                "problem": """
**💡 The Breakthrough**

Here's the clever solution:

1. Separate any 12 pennies into Pile A
2. Put the remaining 4 pennies in Pile B
3. **Flip over all pennies in Pile A**

**Why 12 pennies in Pile A?** Because there are 12 total heads on the table!
                """,
                "prompt": "After following these steps, how many heads will be in each pile?",
                "expected_keywords": ["equal", "same", "head", "pile", "both"],
                "hint": "Think about what happens when you flip all the pennies in Pile A."
            },
            {
                "id": "verify_solution",
                "title": "2.4: Why It Works",
                "problem": """
**🔍 The Logic**

Let's say Pile A (12 coins) originally had H heads and (12-H) tails.

**After flipping all coins in Pile A:**
- Original heads become tails: H → 0
- Original tails become heads: (12-H) → (12-H)
- **Total heads in Pile A:** 12-H

**Pile B has the remaining heads:** 12-H heads (since total heads = 12)

**Result:** Both piles have exactly (12-H) heads!
                """,
                "prompt": "Will this strategy work no matter how the 12 heads are distributed initially?",
                "expected_keywords": ["yes", "always", "works", "any"],
                "hint": "The math works regardless of which specific coins are heads initially."
            },
            {
                "id": "general_solution",
                "title": "2.5: The Universal Strategy",
                "problem": """
**🌟 The General Solution**

This works for any number of pennies and heads!

**Strategy:** If there are H total heads:
1. Put exactly H pennies in Pile A
2. Put remaining pennies in Pile B  
3. Flip all pennies in Pile A

**Result:** Both piles will have equal heads!

**Example:** 20 pennies, 7 heads total
- Pile A: 7 pennies → flip all → ends with (7-x) heads
- Pile B: 13 pennies → keeps x heads
- Both have the same number!

**Our case:** 16 pennies, 12 heads total
- Pile A: 12 pennies → flip all → ends with (12-x) heads
- Pile B: 4 pennies → keeps x heads
- Both have the same number!
                """,
                "prompt": "Why does putting exactly H pennies in Pile A (where H = total heads) guarantee success?",
                "expected_keywords": ["flip", "equal", "head", "pile", "same"],
                "hint": "Flipping creates a 'complement' that matches the remaining heads."
            }
        ]
    },
    {
        "id": "logic_remix",
        "title": "Module 3: Logic Remix",
        "description": "Apply logic rules to the coin trick!",
        "subproblems": [
            {
                "id": "original_statement",
                "title": "3.1: The Original Claim",
                "problem": """
**🔄 Logic Time!**

From the coin trick, we discovered this statement:
**"If you flip H coins from the all-tails pile, then both piles have equal heads."**

**Your Task:** Write the CONVERSE and CONTRAPOSITIVE of this statement.

**Reminder:**
- **Converse:** Switch the if and then parts
- **Contrapositive:** Negate both parts and switch them
                """,
                "prompt": "Write the converse and contrapositive of the coin statement.",
                "expected_keywords": ["if", "then", "equal", "head", "flip"],
                "hint": "Converse: 'If both piles have equal heads, then...' Contrapositive: 'If piles don't have equal heads, then...'"
            }
        ]
    },
    {
        "id": "proofs",
        "title": "Module 4: Proof Power",
        "description": "Explain mathematical reasoning clearly!",
        "subproblems": [
            {
                "id": "kid_explanation",
                "title": "4.1: Kid-Friendly Proof",
                "problem": """
**👨‍🏫 Teaching Challenge!**

Imagine explaining the coin trick to a 5th grader who loves magic tricks but doesn't know algebra.

**Your Mission:** Explain WHY the coin trick works using simple, clear language.

**Requirements:**
- Use 2-3 sentences
- No fancy math terms
- Focus on what happens step by step
                """,
                "prompt": "Explain why the coin trick works in 2-3 simple sentences for a 5th grader.",
                "expected_keywords": ["because", "flip", "heads", "same", "equal", "always"],
                "hint": "Think about counting: if you add the same number of heads to the second pile..."
            }
        ]
    },
    {
        "id": "chess",
        "title": "Module 5: Chess Logic",
        "description": "Discover mathematical patterns in chess!",
        "subproblems": [
            {
                "id": "knight_insight",
                "title": "5.1: The Knight's Secret",
                "problem": """
**♞ Chess Puzzle Time!**

**Key Insight:** A chess knight moves in an L-shape and ALWAYS changes the color of its square.
- If a knight is on a white square, its next move lands on a black square
- If a knight is on a black square, its next move lands on a white square

**Your Challenge:** Use this insight to prove that it's IMPOSSIBLE for a knight to return to its starting square in an odd number of moves.

**Think about:** If a knight starts on white and makes 1 move, where is it? What about 3 moves? 5 moves?
                """,
                "prompt": "Explain why a knight cannot return to its starting square in an odd number of moves.",
                "expected_keywords": ["odd", "color", "change", "opposite", "different"],
                "hint": "After an odd number of moves, the knight is on the opposite color from where it started."
            }
        ]
    }
]

# --- Answer Validation ---
def check_answer(module_idx, subproblem_idx, answer):
    if not answer.strip():
        return False, "Please provide an answer."

    answer_lower = answer.lower()
    module = MODULES[module_idx]
    subproblem = module["subproblems"][subproblem_idx]

    # Check if answer contains expected keywords
    keyword_count = sum(1 for keyword in subproblem["expected_keywords"] if keyword in answer_lower)

    # More flexible validation - at least 1 keyword and answer is substantial (>10 chars)
    if keyword_count >= 1 and len(answer.strip()) > 10:
        return True, "Great work! You can proceed to the next problem."
    else:
        return False, f"Try again! Hint: {subproblem['hint']}"

# --- Helper Functions ---
def get_total_subproblems():
    return sum(len(module["subproblems"]) for module in MODULES)

def get_completed_subproblems():
    total = 0
    for module_idx in range(len(MODULES)):
        if module_idx in st.session_state.completed_subproblems:
            total += len(st.session_state.completed_subproblems[module_idx])
    return total

def is_current_subproblem_available():
    # TESTING MODE: All modules unlocked
    return True

# --- Main App ---
st.title("🎯 The Magic Split")
st.caption("Master logic through puzzles: statements → coins → logic → proofs → chess")

# Student name input (appears once)
if not st.session_state.student_name:
    st.subheader("Welcome!")
    name_input = st.text_input("Enter your name to begin:")
    if st.button("Start Learning") and name_input.strip():
        st.session_state.student_name = name_input.strip()
        st.rerun()
    st.stop()

# Progress indicator
st.subheader(f"Welcome back, {st.session_state.student_name}!")
completed_subs = get_completed_subproblems()
total_subs = get_total_subproblems()
progress = completed_subs / total_subs if total_subs > 0 else 0
st.progress(progress)
st.write(f"Progress: {completed_subs}/{total_subs} problems completed")

# Current module and subproblem
current_module = MODULES[st.session_state.current_module]
current_subproblem = current_module["subproblems"][st.session_state.current_subproblem]

# Module header
st.markdown(f"## {current_module['title']}")
st.write(current_module['description'])

# Subproblem display
st.markdown(f"### {current_subproblem['title']}")

# Display image if it exists
if "image" in current_subproblem:
    try:
        st.image(current_subproblem["image"], use_column_width=True)
    except:
        st.write(f"*Image: {current_subproblem['image']}*")

st.markdown(current_subproblem['problem'])

# Check if current subproblem is available
if not is_current_subproblem_available():
    st.warning("🔒 Complete the previous problem to unlock this one!")
    st.stop()

# Answer input
st.markdown("### Your Solution")
answer = st.text_area(current_subproblem['prompt'], height=120, 
                     key=f"answer_{current_module['id']}_{current_subproblem['id']}")

# Navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    # Previous button
    can_go_prev = st.session_state.current_module > 0 or st.session_state.current_subproblem > 0
    if can_go_prev and st.button("← Previous"):
        if st.session_state.current_subproblem > 0:
            st.session_state.current_subproblem -= 1
        else:
            st.session_state.current_module -= 1
            st.session_state.current_subproblem = len(MODULES[st.session_state.current_module]["subproblems"]) - 1
        st.rerun()

with col2:
    if st.button("Submit Answer"):
        is_correct, message = check_answer(st.session_state.current_module, 
                                         st.session_state.current_subproblem, answer)
        
        if is_correct:
            # Log the correct answer
            log_line(st.session_state.student_name, 
                    f"{current_module['id']}_{current_subproblem['id']}", answer)
            
            # Mark subproblem as completed
            module_idx = st.session_state.current_module
            if module_idx not in st.session_state.completed_subproblems:
                st.session_state.completed_subproblems[module_idx] = set()
            st.session_state.completed_subproblems[module_idx].add(st.session_state.current_subproblem)
            
            # Check if module is completed
            if len(st.session_state.completed_subproblems[module_idx]) == len(current_module["subproblems"]):
                st.session_state.completed_modules.add(module_idx)
            
            st.success(message)
            st.balloons()
            
            # Auto-advance to next subproblem/module
            if st.session_state.current_subproblem < len(current_module["subproblems"]) - 1:
                # Next subproblem in same module
                st.session_state.current_subproblem += 1
                st.rerun()
            elif st.session_state.current_module < len(MODULES) - 1:
                # Next module
                st.session_state.current_module += 1
                st.session_state.current_subproblem = 0
                st.rerun()
            else:
                st.success("🎉 Congratulations! You've completed all problems!")
        else:
            st.error(message)

with col3:
    # Next button (only if current subproblem is completed)
    module_idx = st.session_state.current_module
    subproblem_idx = st.session_state.current_subproblem
    is_completed = (module_idx in st.session_state.completed_subproblems and 
                   subproblem_idx in st.session_state.completed_subproblems[module_idx])
    
    can_go_next = (st.session_state.current_subproblem < len(current_module["subproblems"]) - 1 or 
                   st.session_state.current_module < len(MODULES) - 1)
    
    if is_completed and can_go_next and st.button("Next →"):
        if st.session_state.current_subproblem < len(current_module["subproblems"]) - 1:
            st.session_state.current_subproblem += 1
        else:
            st.session_state.current_module += 1
            st.session_state.current_subproblem = 0
        st.rerun()

# Module overview with subproblem navigation
st.markdown("### Module Overview")
for module_idx, module in enumerate(MODULES):
    with st.expander(f"{module['title']} ({len(module['subproblems'])} problems)", 
                     expanded=(module_idx == st.session_state.current_module)):
        
        cols = st.columns(min(len(module["subproblems"]), 5))
        for sub_idx, subproblem in enumerate(module["subproblems"]):
            with cols[sub_idx % 5]:
                # Determine status
                is_current = (module_idx == st.session_state.current_module and 
                             sub_idx == st.session_state.current_subproblem)
                is_completed = (module_idx in st.session_state.completed_subproblems and 
                               sub_idx in st.session_state.completed_subproblems[module_idx])
                
                if is_completed:
                    status = "✅"
                elif is_current:
                    status = "📍"
                else:
                    status = "⭕"
                
                button_text = f"{status} {sub_idx + 1}.{sub_idx + 1}"

                # TESTING MODE: All problems available
                if st.button(button_text, key=f"nav_{module_idx}_{sub_idx}"):
                    st.session_state.current_module = module_idx
                    st.session_state.current_subproblem = sub_idx
                    st.rerun()

# Teacher tools (collapsed by default)
with st.expander("🎓 Teacher Tools"):
    if st.button("Reset Student Progress"):
        st.session_state.current_module = 0
        st.session_state.current_subproblem = 0
        st.session_state.completed_modules = set()
        st.session_state.completed_subproblems = {}
        st.rerun()
    
    if st.checkbox("Show Submissions Log"):
        txt = LOG_FILE.read_text(encoding="utf-8") if LOG_FILE.exists() else ""
        st.code(txt or "(no submissions yet)", language="text")
        if LOG_FILE.exists():
            st.download_button("Download submissions.txt",
                               data=txt.encode("utf-8"),
                               file_name="submissions.txt",
                               mime="text/plain")
