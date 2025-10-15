import math
from functools import lru_cache
from datetime import datetime

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ------------------------------
# APP META / THEME
# ------------------------------
st.set_page_config(
    page_title="Dragon Tail → Golden Ratio → Fibonacci",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#0b84f3"
ACCENT = "#ff9f1c"
GOOD = "#2ecc71"
WARN = "#e74c3c"

# ------------------------------
# GOOGLE SHEETS SETUP
# ------------------------------
worksheet = None
try:
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = None

    # Load credentials from Streamlit secrets
    if "gcp_service_account" in st.secrets:
        credentials_dict = {
            "type": st.secrets["gcp_service_account"]["type"],
            "project_id": st.secrets["gcp_service_account"]["project_id"],
            "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
            "private_key": st.secrets["gcp_service_account"]["private_key"],
            "client_email": st.secrets["gcp_service_account"]["client_email"],
            "client_id": st.secrets["gcp_service_account"]["client_id"],
            "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
            "token_uri": st.secrets["gcp_service_account"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"],
            "universe_domain": st.secrets["gcp_service_account"]["universe_domain"]
        }
        creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)

        # Extract sheet ID from URL
        sheet_url = st.secrets.get("sheet_url", "")
        if "/d/" in sheet_url:
            SHEET_ID = sheet_url.split("/d/")[1].split("/")[0]
        else:
            st.warning("Sheet URL format not recognized. Logging may not work.")
            SHEET_ID = None

        if SHEET_ID:
            gc = gspread.authorize(creds)
            worksheet = gc.open_by_key(SHEET_ID).sheet1

            # Initialize header row if sheet is empty
            if worksheet.row_count == 0 or not worksheet.row_values(1):
                worksheet.append_row(["Timestamp", "Student", "Section", "Interaction Type", "Details", "Correctness"])
except Exception as e:
    st.warning(f"Google Sheets logging unavailable: {e}")
    worksheet = None

# ------------------------------
# HELPERS
# ------------------------------

@lru_cache(None)
def fib(n: int) -> int:
    if n <= 0:
        return 0
    if n in (1, 2):
        return 1
    return fib(n - 1) + fib(n - 2)


def convergent_phi(n: int) -> float:
    """
    nth convergent of 1 + 1/(1 + 1/(1 + ...)) with n layers.
    C1 = 1, C2 = 2/1, C3 = 3/2, ... = F_{n+1}/F_n
    """
    if n <= 1:
        return 1.0
    return fib(n + 1) / fib(n)


def continued_fraction_value(depth: int) -> float:
    """Compute finite value of 1 + 1/(1 + 1/(...)) of given depth via fold-back."""
    x = 1.0
    for _ in range(depth - 1):
        x = 1.0 + 1.0 / x
    return x


def phi() -> float:
    return (1 + math.sqrt(5)) / 2


def fmt(x: float, digits: int = 6) -> str:
    return f"{x:.{digits}f}"


def log_interaction(student_name: str, section: str, interaction_type: str, details: str, is_correct: bool = None):
    """
    Logs student interactions to Google Sheets.

    Args:
        student_name: Name of the student (Soren, Ayushi, or Both)
        section: Which section of the app (Part A, Part B, etc.)
        interaction_type: Type of interaction (quiz_answer, section_change, slider_change, etc.)
        details: Additional details about the interaction
        is_correct: For quiz answers, whether the answer was correct (True/False/None)
    """
    if worksheet is None:
        return False

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        correctness = "N/A" if is_correct is None else ("Correct" if is_correct else "Incorrect")
        row = [timestamp, student_name, section, interaction_type, details, correctness]
        worksheet.append_row(row)
        return True
    except Exception as e:
        st.warning(f"Error logging to Google Sheets: {e}")
        return False


def check_both_students_completed(section: str, question_identifier: str) -> dict:
    """
    Checks if both Soren and Ayushi have answered a specific question correctly.

    Args:
        section: The section name (e.g., "Part A — Dragon Tail Fraction")
        question_identifier: Unique identifier for the question (e.g., "Question: 'If x = 1 + 1/x'")

    Returns:
        dict with keys:
            - 'both_completed': bool
            - 'soren_completed': bool
            - 'ayushi_completed': bool
    """
    if worksheet is None:
        return {'both_completed': False, 'soren_completed': False, 'ayushi_completed': False}

    try:
        # Get all records from the sheet
        all_records = worksheet.get_all_records()

        soren_completed = False
        ayushi_completed = False

        # Check for correct answers from each student
        for record in all_records:
            if (record.get('Section') == section and
                record.get('Interaction Type') == 'quiz_answer' and
                question_identifier in record.get('Details', '') and
                record.get('Correctness') == 'Correct'):

                if record.get('Student') == 'Soren':
                    soren_completed = True
                elif record.get('Student') == 'Ayushi':
                    ayushi_completed = True

        return {
            'both_completed': soren_completed and ayushi_completed,
            'soren_completed': soren_completed,
            'ayushi_completed': ayushi_completed
        }
    except Exception as e:
        st.warning(f"Error checking completion status: {e}")
        return {'both_completed': False, 'soren_completed': False, 'ayushi_completed': False}


# ------------------------------
# STUDENT AUTHENTICATION
# ------------------------------
if "student" not in st.session_state:
    st.session_state.student = None

if st.session_state.student is None:
    col_img, col_text = st.columns([1, 2])

    with col_img:
        try:
            st.image("dragon.png", width=300)
        except:
            st.markdown("## 🐉")

    with col_text:
        st.markdown("## Welcome to Dragon Tail Math!")
        st.write("Please select your name to begin:")

        student_choice = st.selectbox("I am:", ["-- Select --", "Soren", "Ayushi"], key="student_select")
        if st.button("Start Learning", type="primary", disabled=(student_choice == "-- Select --")):
            if student_choice != "-- Select --":
                st.session_state.student = student_choice
                log_interaction(student_choice, "Login", "student_login", f"{student_choice} logged in")
                st.rerun()

    st.stop()

student = st.session_state.student

# ------------------------------
# SIDEBAR: LESSON NAV + ROLE
# ------------------------------
st.sidebar.title("Lesson Navigator")
st.sidebar.markdown(f"**Logged in as:** {student}")

# Track previous section for logging
if "prev_section" not in st.session_state:
    st.session_state.prev_section = None

section = st.sidebar.radio(
    "Jump to section",
    [
        "Part A — Dragon Tail Fraction",
        "Part C — Mini Puzzles",
        "Part D — The Bus Problem",
        "About / How to Use",
    ],
)

# Log section changes
if st.session_state.prev_section != section:
    log_interaction(student, section, "section_change", f"Navigated to {section}")
    st.session_state.prev_section = section

st.sidebar.caption(
    "Explore each section, answer questions, and watch the patterns unfold!"
)

# Progress Overview
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Progress Overview")

# Check completion for key checkpoints
part_a_status = check_both_students_completed(
    "Part A — Dragon Tail Fraction",
    "Q3: 'Which answer makes sense?'"
)
puzzle1_status = check_both_students_completed(
    "Part C — Mini Puzzles",
    "Puzzle 1a: First result"
)
puzzle2_status = check_both_students_completed(
    "Part C — Mini Puzzles",
    "Puzzle 2: Next fraction"
)

# Display progress indicators
if part_a_status['both_completed']:
    st.sidebar.success("✅ Part A Complete")
else:
    st.sidebar.warning("⏳ Part A In Progress")

if puzzle1_status['both_completed']:
    st.sidebar.success("✅ Puzzle 1 Complete")
else:
    st.sidebar.info("🔒 Puzzle 1")

if puzzle2_status['both_completed']:
    st.sidebar.success("✅ Puzzle 2 Complete")
else:
    st.sidebar.info("🔒 Puzzle 2")

# Logout button
st.sidebar.markdown("---")
if st.sidebar.button("Logout"):
    st.session_state.student = None
    st.rerun()

# ------------------------------
# HEADER
# ------------------------------
st.markdown(
    f"""
    <div style='padding:0.6rem 0 0.2rem 0'>
      <h1 style='margin-bottom:0'>🐉 Dragon Tail → Golden Ratio → Fibonacci</h1>
      <p style='color:#666;margin-top:4px'>Self-similarity (x = 1 + 1/x) • Convergents • Fibonacci Ratios • Error propagation</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Utility to render a clean card
from contextlib import contextmanager

@contextmanager
def card(title: str = ""):
    st.markdown(
        f"<div style='border:1px solid #eaeaea;border-radius:16px;padding:16px 18px;margin:8px 0;background:#fff'>",
        unsafe_allow_html=True,
    )
    if title:
        st.markdown(f"<h3 style='margin-top:2px'>{title}</h3>", unsafe_allow_html=True)
    yield
    st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------
# ------------------------------
# PART A — Dragon Tail Fraction
# ------------------------------
if section == "Part A — Dragon Tail Fraction":

    # 0) Cold Open
    with card("The Dragon's Infinite Tail"):
        col_img, col_frac = st.columns([1, 1])
        with col_img:
            try:
                st.image("dragon.png", use_container_width=True)
            except:
                st.markdown("### 🐉")
        with col_frac:
            st.markdown("<div style='padding: 30px 0; text-align: center;'>", unsafe_allow_html=True)
            st.latex(r"\Large x = 1 + \cfrac{1}{1 + \cfrac{1}{1 + \cfrac{1}{1 + \cdots}}}")
            st.markdown("</div>", unsafe_allow_html=True)
            st.caption("This pattern repeats forever. Let's use that!")

    # 1) See the Self-Copy
    with card("Step 1: The Pattern Copies Itself"):
        st.write("Look closely at the tail (everything after the first '1 + ...'):")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**The whole thing:**")
            st.latex(r"x = 1 + \cfrac{1}{\boxed{\text{tail}}}")
        with col2:
            st.markdown("**The tail:**")
            st.latex(r"\text{tail} = 1 + \cfrac{1}{1 + \cfrac{1}{1 + \cdots}}")

        st.info("💡 The tail looks exactly like the whole! So if we call the whole thing **x**, the tail must also equal **x**.")
        st.latex(r"x = 1 + \frac{1}{x}")

    # 2) Baby Algebra Ladder
    with card("Step 2: Solve Step-by-Step (Balance Trick)"):
        st.write("Let's solve x = 1 + 1/x using tiny steps:")

        st.markdown("**Step 1:** Subtract 1 from both sides")
        st.latex(r"x - 1 = \frac{1}{x}")
        st.caption("Balance!")

        st.markdown("**Step 2:** Multiply both sides by x")
        st.latex(r"x(x - 1) = 1")
        st.caption("Head × tail = 1")

        st.markdown("**Step 3:** Expand")
        st.latex(r"x^2 - x = 1")

        st.markdown("**Step 4:** Add ¼ to both sides (the balance-square trick!)")
        st.latex(r"x^2 - x + \frac{1}{4} = 1 + \frac{1}{4}")
        st.caption("Same on both sides keeps balance")

        st.markdown("**Step 5:** The left side is now a perfect square")
        st.latex(r"\left(x - \frac{1}{2}\right)^2 = \frac{5}{4}")

        st.markdown("**Step 6:** Take square roots")
        st.latex(r"x - \frac{1}{2} = \pm \frac{\sqrt{5}}{2}")

        st.markdown("**Step 7:** Add ½ back")
        st.latex(r"x = \frac{1}{2} \pm \frac{\sqrt{5}}{2}")

        st.markdown("**Step 8:** Choose the sensible answer")
        st.write("The dragon-tail is clearly positive and bigger than 1, so we pick the **plus**:")
        st.latex(r"x = \frac{1 + \sqrt{5}}{2} \approx 1.618")
        st.success("This is the **Golden Ratio** φ (phi)!")

    # 3) Reality Check
    with card("Step 3: Reality Check"):
        st.write("Let's verify our answer works:")
        phi_val = phi()
        check_val = 1 + 1/phi_val
        st.latex(r"1 + \frac{1}{1.618...} \approx " + fmt(check_val))
        st.success("✓ It gives the same number! Our equation is consistent.")

    # 4) Alternate Path: Iteration
    with card("Alternate Path: Watch It Converge"):
        st.write("Start with any number and keep applying the rule: x → 1 + 1/x")

        n_iterations = st.slider("How many steps?", 1, 15, 8, key="iterations")

        x_vals = [1.0]  # Start with 1
        for i in range(n_iterations):
            x_vals.append(1 + 1/x_vals[-1])

        # Show table
        df_iter = pd.DataFrame({
            "Step": range(len(x_vals)),
            "Value": x_vals,
            "Distance from φ": [abs(x - phi()) for x in x_vals]
        })
        st.dataframe(df_iter.style.format({"Value": "{:.6f}", "Distance from φ": "{:.6f}"}))

        st.caption("Notice how it wiggles but settles near 1.618... These fractions are connected to Fibonacci numbers!")

    # 5) Check-in Questions
    with card("Check Your Understanding"):
        st.markdown("### Question 1")
        q1 = st.radio(
            f"{student}: From x = 1 + 1/x, what is x − 1?",
            ["1/x", "x²", "x + 1", "1 - x"],
            index=None,
            key="q1"
        )

        if "part_a_q1" not in st.session_state:
            st.session_state.part_a_q1 = None

        if q1 is not None and st.session_state.part_a_q1 != q1:
            is_correct_q1 = (q1 == "1/x")
            log_interaction(student, "Part A — Dragon Tail Fraction", "quiz_answer",
                           f"Q1: 'From x = 1 + 1/x, what is x − 1?' Answer: {q1}", is_correct_q1)
            st.session_state.part_a_q1 = q1

        if q1 is not None:
            if q1 == "1/x":
                st.success("✅ Correct!")
            else:
                st.error("❌ Try again: subtract 1 from both sides.")

        st.markdown("### Question 2")
        q2 = st.radio(
            f"{student}: If x − 1 = 1/x, what is x(x − 1)?",
            ["0", "1", "x", "x²"],
            index=None,
            key="q2"
        )

        if "part_a_q2" not in st.session_state:
            st.session_state.part_a_q2 = None

        if q2 is not None and st.session_state.part_a_q2 != q2:
            is_correct_q2 = (q2 == "1")
            log_interaction(student, "Part A — Dragon Tail Fraction", "quiz_answer",
                           f"Q2: 'If x − 1 = 1/x, what is x(x − 1)?' Answer: {q2}", is_correct_q2)
            st.session_state.part_a_q2 = q2

        if q2 is not None:
            if q2 == "1":
                st.success("✅ Correct! x times (1/x) equals 1.")
            else:
                st.error("❌ Hint: multiply both sides by x.")

        st.markdown("### Question 3")
        q3 = st.radio(
            f"{student}: The dragon-tail is clearly bigger than 1. Which answer makes sense?",
            ["(1 − √5)/2 (negative)", "(1 + √5)/2 (positive, ≈ 1.618)"],
            index=None,
            key="q3"
        )

        if "part_a_q3" not in st.session_state:
            st.session_state.part_a_q3 = None

        if q3 is not None and st.session_state.part_a_q3 != q3:
            is_correct_q3 = (q3 == "(1 + √5)/2 (positive, ≈ 1.618)")
            log_interaction(student, "Part A — Dragon Tail Fraction", "quiz_answer",
                           f"Q3: 'Which answer makes sense?' Answer: {q3}", is_correct_q3)
            st.session_state.part_a_q3 = q3

        if q3 is not None:
            if q3 == "(1 + √5)/2 (positive, ≈ 1.618)":
                st.success("✅ Exactly! The positive one fits the picture.")
            else:
                st.error("❌ The negative value doesn't match our pattern which builds with positive pieces.")

        # Check if all three questions answered correctly
        all_correct = (
            st.session_state.part_a_q1 == "1/x" and
            st.session_state.part_a_q2 == "1" and
            st.session_state.part_a_q3 == "(1 + √5)/2 (positive, ≈ 1.618)"
        )

        if all_correct:
            st.balloons()

        # Progress check
        completion_status = check_both_students_completed(
            "Part A — Dragon Tail Fraction",
            "Q3: 'Which answer makes sense?'"
        )

        st.markdown("---")
        st.markdown("**Progress Check:**")
        col_s, col_a = st.columns(2)
        with col_s:
            if completion_status['soren_completed']:
                st.success("✅ Soren completed")
            else:
                st.info("⏳ Soren not yet completed")
        with col_a:
            if completion_status['ayushi_completed']:
                st.success("✅ Ayushi completed")
            else:
                st.info("⏳ Ayushi not yet completed")

    # Gate: Only show takeaway if both students completed
    completion_status = check_both_students_completed(
        "Part A — Dragon Tail Fraction",
        "Q3: 'Which answer makes sense?'"
    )

    if completion_status['both_completed']:
        with card("🎯 Takeaway"):
            st.markdown("**Self-copy ⇒ x = 1 + 1/x ⇒ balance-square trick ⇒ x = (1 + √5)/2**")
            st.latex(r"\varphi = \frac{1 + \sqrt{5}}{2} \approx 1.618")
            st.success("You've discovered the Golden Ratio!")
    else:
        with card("🔒 Final Takeaway Locked"):
            st.info("**Both students need to answer all three questions correctly!**")
            if student == "Soren" and not completion_status['soren_completed']:
                st.warning("⏳ Soren, complete all questions above.")
            elif student == "Ayushi" and not completion_status['ayushi_completed']:
                st.warning("⏳ Ayushi, complete all questions above.")
            elif student == "Soren" and completion_status['soren_completed']:
                st.success("✅ Great job! Waiting for Ayushi...")
            elif student == "Ayushi" and completion_status['ayushi_completed']:
                st.success("✅ Great job! Waiting for Soren...")

            if st.button("🔄 Refresh", key="check_progress_a"):
                st.rerun()

# ------------------------------
# PART C — Mini Puzzles
# ------------------------------
elif section == "Part C — Mini Puzzles":
    with card("Puzzle 1: Build the Pattern"):
        st.write("We're going to build a pattern step by step!")
        st.write("**Starting value:** 2/1 (which is the same as 2)")
        st.write("**The rule:** Take your number and do this → 1 + 1/□")
        st.write("**Example:** If we have 2, then 1 + 1/2 = 3/2")
        st.markdown("---")

        # Track previous answers
        if "p1a_prev" not in st.session_state:
            st.session_state.p1a_prev = None
        if "p1b_prev" not in st.session_state:
            st.session_state.p1b_prev = None

        st.write("**Your turn!**")
        a1 = st.text_input("Apply the rule ONCE to 2/1. What do you get?", key="p1a")
        a2 = st.text_input("Now apply the rule to your answer above. What do you get?", key="p1b")

        sol1, sol2 = "3/2", "5/3"

        if a1 and st.session_state.p1a_prev != a1:
            is_correct = a1.replace(" ","") in {"3/2","1.5","1+1/2"}
            log_interaction(student, "Part C — Mini Puzzles", "quiz_answer",
                           f"Puzzle 1a: First result = {a1}", is_correct)
            st.session_state.p1a_prev = a1

        if a2 and st.session_state.p1b_prev != a2:
            is_correct = a2.replace(" ","") in {"5/3","1.666666","1+2/3"}
            log_interaction(student, "Part C — Mini Puzzles", "quiz_answer",
                           f"Puzzle 1b: Second result = {a2}", is_correct)
            st.session_state.p1b_prev = a2

        if a1:
            st.markdown("✅" if a1.replace(" ","") in {"3/2","1.5","1+1/2"} else "❌ try 1 + 1/2")
        if a2:
            st.markdown("✅" if a2.replace(" ","") in {"5/3","1.666666","1+2/3"} else "❌ next is 1 + 1/(3/2)")

    # Check completion status for puzzle 1
    puzzle1_status = check_both_students_completed(
        "Part C — Mini Puzzles",
        "Puzzle 1a: First result"
    )

    # Show progress for Puzzle 1
    st.markdown("---")
    st.markdown("**Puzzle 1 Progress:**")
    col_s, col_a = st.columns(2)
    with col_s:
        if puzzle1_status['soren_completed']:
            st.success("✅ Soren completed")
        else:
            st.info("⏳ Soren not yet completed")
    with col_a:
        if puzzle1_status['ayushi_completed']:
            st.success("✅ Ayushi completed")
        else:
            st.info("⏳ Ayushi not yet completed")

    # Gate Puzzle 2
    if puzzle1_status['both_completed']:
        with card("Puzzle 2: What Comes Next?"):
            st.write("Given the fractions 8/5 and 13/8, what's the next fraction in the pattern?")

            # Track previous answer
            if "p2_prev" not in st.session_state:
                st.session_state.p2_prev = None

            a = st.text_input("Your fraction", key="p2")

            if a and st.session_state.p2_prev != a:
                is_correct = a.replace(" ","") in {"21/13"}
                log_interaction(student, "Part C — Mini Puzzles", "quiz_answer",
                               f"Puzzle 2: Next fraction = {a}", is_correct)
                st.session_state.p2_prev = a

            if a:
                st.markdown("✅" if a.replace(" ","") in {"21/13"} else "❌ Hint: add top-to-top and bottom-to-bottom.")
    else:
        with card("🔒 Next Puzzle Locked"):
            st.info("**Both students need to complete Puzzle 1 first!**")
            if st.button("🔄 Refresh", key="check_progress_c1"):
                st.rerun()

    # Check completion status for puzzle 2
    puzzle2_status = check_both_students_completed(
        "Part C — Mini Puzzles",
        "Puzzle 2: Next fraction"
    )

    # Gate: Golden Ratio Discovery
    if puzzle1_status['both_completed'] and puzzle2_status['both_completed']:
        with card("The Golden Rectangle"):
            col_img, col_text = st.columns([1, 1])
            with col_img:
                try:
                    st.image("golden_rectangle.png", use_container_width=True)
                except:
                    st.warning("Golden rectangle image not found")
            with col_text:
                st.write("This is the **Golden Rectangle** - its sides have a ratio of 1:1.618 (the Golden Ratio!).")
                st.write("If you cut a square from it, what's left is another golden rectangle. You can do this forever!")
                st.write("The spiral connects the corners, creating the famous **Golden Spiral**.")

        with card("The Golden Ratio in Nature"):
            st.write("The Golden Ratio (φ ≈ 1.618) shows up everywhere in nature!")

            st.markdown("**Where can you find it?**")
            st.markdown("🌻 **Sunflowers** - The spirals in the center follow Fibonacci numbers")
            st.markdown("🐚 **Seashells** - Many shells grow in a spiral using the Golden Ratio")
            st.markdown("🌀 **Hurricanes** - The spiral shape follows this same pattern")
            st.markdown("🌲 **Pine cones** - Count the spirals - they're Fibonacci numbers!")
            st.markdown("🍍 **Pineapples** - The segments spiral in Fibonacci patterns")

            st.info("💡 Why does nature use this ratio? Because it's the most efficient way to pack things into a spiral - nothing overlaps and nothing is wasted!")

        with card("Challenge: List the Fibonacci Numbers!"):
            st.write("**How many Fibonacci numbers can you list from memory?**")
            st.write("Start with: 1, 1, 2, 3, 5, 8...")
            st.write("Enter your sequence below (separate numbers with commas)")

            # Track previous submission
            if "fib_list_prev" not in st.session_state:
                st.session_state.fib_list_prev = None

            fib_input = st.text_area("Your Fibonacci sequence:", key="fib_sequence", height=100)

            if st.button("Submit My List", key="submit_fib"):
                if fib_input:
                    # Parse the input
                    try:
                        numbers = [int(x.strip()) for x in fib_input.split(",") if x.strip()]

                        # Check if they're valid Fibonacci numbers in order
                        correct_count = 0
                        for i, num in enumerate(numbers):
                            if num == fib(i + 1):
                                correct_count += 1
                            else:
                                break

                        # Log the result
                        if st.session_state.fib_list_prev != fib_input:
                            log_interaction(student, "Part C — Mini Puzzles", "fibonacci_challenge",
                                          f"Listed {correct_count} correct Fibonacci numbers", True)
                            st.session_state.fib_list_prev = fib_input

                        if correct_count == len(numbers):
                            st.success(f"✅ Perfect! You listed {correct_count} Fibonacci numbers correctly!")
                        else:
                            st.warning(f"You got {correct_count} correct before making a mistake. Keep trying!")
                    except:
                        st.error("Please enter numbers separated by commas, like: 1, 1, 2, 3, 5, 8")

            # Show comparison
            st.markdown("---")
            st.markdown("**Scoreboard:**")

            # Get both students' best counts
            try:
                if worksheet is not None:
                    all_records = worksheet.get_all_records()
                    soren_best = 0
                    ayushi_best = 0

                    for record in all_records:
                        if (record.get('Section') == 'Part C — Mini Puzzles' and
                            record.get('Interaction Type') == 'fibonacci_challenge'):
                            details = record.get('Details', '')
                            # Extract number from "Listed X correct Fibonacci numbers"
                            if 'Listed' in details:
                                try:
                                    count = int(details.split('Listed ')[1].split(' ')[0])
                                    if record.get('Student') == 'Soren':
                                        soren_best = max(soren_best, count)
                                    elif record.get('Student') == 'Ayushi':
                                        ayushi_best = max(ayushi_best, count)
                                except:
                                    pass

                    col_s, col_a = st.columns(2)
                    with col_s:
                        st.metric("Soren's Best", f"{soren_best} numbers")
                    with col_a:
                        st.metric("Ayushi's Best", f"{ayushi_best} numbers")
            except:
                pass
    else:
        with card("🔒 More Content Locked"):
            st.info("**Complete Puzzles 1 and 2 to unlock more!**")
            if st.button("🔄 Refresh", key="check_progress_c2"):
                st.rerun()

# ------------------------------
# PART D — The Bus Problem
# ------------------------------
elif section == "Part D — The Bus Problem":
    with card("The Bus Problem"):
        st.write("On a long bus ride, 17 math teachers created a sequence of numbers:")
        st.markdown("""
        - The **1st teacher** said: **2**
        - The **2nd teacher** said: **8**
        - Every teacher after that said the **sum of the two previous terms**

        For example:
        - The 3rd teacher said: 2 + 8 = **10**
        - The 4th teacher said: 8 + 10 = **18**
        """)

        st.info("🚌 After everyone finished, the **7th teacher** realized they made a mistake! Their number should have been **one more** than what they said.")

        st.markdown("**Question:** How much larger should the **17th teacher's** number have been?")

    with card("Your Answer"):
        st.write("**Work together to figure it out!** Calculate the sequences and track how the error spreads.")

        if "bus_answer" not in st.session_state:
            st.session_state.bus_answer = None

        answer = st.number_input("Enter your answer:", min_value=0, step=1, key="bus_input")

        if st.button("Check Answer", key="check_bus"):
            # Calculate correct answer
            correct_seq = [2, 8]
            for i in range(2, 17):
                correct_seq.append(correct_seq[-1] + correct_seq[-2])

            wrong_seq = [2, 8]
            for i in range(2, 17):
                if i == 6:
                    wrong_seq.append(correct_seq[i] - 1)
                else:
                    wrong_seq.append(wrong_seq[-1] + wrong_seq[-2])

            correct_answer = correct_seq[16] - wrong_seq[16]

            if answer == correct_answer:
                st.success(f"✅ Correct! The answer is {correct_answer}!")
                st.balloons()
                if st.session_state.bus_answer != answer:
                    log_interaction(student, "Part D — The Bus Problem", "quiz_answer",
                                  f"Bus Problem answer: {answer}", True)
                    st.session_state.bus_answer = answer
            else:
                st.error("❌ Not quite. Keep working through the sequence - both of you should build the sequence step by step!")
                if st.session_state.bus_answer != answer:
                    log_interaction(student, "Part D — The Bus Problem", "quiz_answer",
                                  f"Bus Problem answer: {answer}", False)
                    st.session_state.bus_answer = answer

# ------------------------------
# ABOUT
# ------------------------------
else:
    st.markdown(
        """
        ## How to Use This App

        **Learning Path:**
        1. **Part A**: Build the dragon's tail pattern and discover how it leads to the Golden Ratio (φ)
        2. **Part C**: Solve puzzles to deepen your understanding
        3. **Part D**: Solve the famous Bus Problem - track how errors spread through sequences

        **Working Together:**
        - Both students must complete each section before moving forward
        - Check the Progress Overview in the sidebar to see your progress
        - Use the Refresh button if you're waiting for your partner

        **Tips:**
        - Take your time with each question
        - Try different values with the sliders to see what happens
        - All your work is saved automatically!
        """
    )
