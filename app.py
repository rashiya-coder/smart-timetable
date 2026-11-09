import random
import math
import pandas as pd
import streamlit as st

# ---------- Settings ----------
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
PERIODS = 6                      # periods per day
SUBJECTS = ["Maths", "AI", "DBMS", "Python", "OS", "Lab"]
PER_WEEK = 5                     # each subject has 5 periods per week
ITERATIONS = 5000


# ---------- Cost function (lower is better, 0 = perfect) ----------
def cost(t):
    c = 0
    for d in range(len(DAYS)):
        day = t[d * PERIODS:(d + 1) * PERIODS]
        for p, s in enumerate(day):
            # Rule 1: same subject more than once in a day -> +10 per extra
            if day[:p].count(s) >= 1:
                c += 10
            # Rule 2: same subject in back-to-back periods -> +5
            if p < PERIODS - 1 and day[p + 1] == s:
                c += 5
            # Rule 3: Maths or AI in the afternoon (periods 4-6) -> +3
            if s in ("Maths", "AI") and p >= 3:
                c += 3
    return c


# ---------- Neighbour move: swap two random slots ----------
def neighbour(t):
    n = t[:]
    a, b = random.sample(range(len(n)), 2)
    n[a], n[b] = n[b], n[a]
    return n


# ---------- Hill Climbing ----------
def hill_climbing(start):
    cur, cur_cost = start[:], cost(start)
    history = [cur_cost]
    for i in range(1, ITERATIONS + 1):
        new = neighbour(cur)
        new_cost = cost(new)
        if new_cost <= cur_cost:          # keep only if not worse
            cur, cur_cost = new, new_cost
        if i % 50 == 0:
            history.append(cur_cost)
    return cur, cur_cost, history


# ---------- Simulated Annealing ----------
def simulated_annealing(start):
    cur, cur_cost = start[:], cost(start)
    best, best_cost = cur[:], cur_cost
    T = 10.0                              # starting temperature
    history = [cur_cost]
    for i in range(1, ITERATIONS + 1):
        new = neighbour(cur)
        new_cost = cost(new)
        delta = new_cost - cur_cost
        # accept better always, worse with probability e^(-delta/T)
        if delta <= 0 or random.random() < math.exp(-delta / T):
            cur, cur_cost = new, new_cost
        if cur_cost < best_cost:
            best, best_cost = cur[:], cur_cost
        T *= 0.999                        # cooling
        if i % 50 == 0:
            history.append(best_cost)
    return best, best_cost, history


# ---------- Helpers ----------
def random_timetable():
    t = SUBJECTS * PER_WEEK
    random.shuffle(t)
    return t


def to_table(t):
    rows = [t[d * PERIODS:(d + 1) * PERIODS] for d in range(len(DAYS))]
    return pd.DataFrame(rows, index=DAYS,
                        columns=[f"P{i}" for i in range(1, PERIODS + 1)])


# ---------- App ----------
st.title("Smart Timetable Optimization")
st.caption("AI concepts: Hill Climbing and Simulated Annealing")

if "start" not in st.session_state:
    st.session_state.start = random_timetable()
    st.session_state.shown = st.session_state.start
    st.session_state.label = "Random starting timetable"
    st.session_state.hc = None
    st.session_state.sa = None

c1, c2, c3 = st.columns(3)

if c1.button("Generate random"):
    st.session_state.start = random_timetable()
    st.session_state.shown = st.session_state.start
    st.session_state.label = "Random starting timetable"
    st.session_state.hc = None
    st.session_state.sa = None

if c2.button("Run Hill Climbing"):
    t, c, h = hill_climbing(st.session_state.start)
    st.session_state.hc = h
    st.session_state.shown = t
    st.session_state.label = "Hill Climbing result"

if c3.button("Run Simulated Annealing"):
    t, c, h = simulated_annealing(st.session_state.start)
    st.session_state.sa = h
    st.session_state.shown = t
    st.session_state.label = "Simulated Annealing result"

st.subheader(st.session_state.label)
st.write("Cost =", cost(st.session_state.shown))
st.table(to_table(st.session_state.shown))

# Cost graph
data = {}
if st.session_state.hc:
    data["Hill Climbing"] = st.session_state.hc
if st.session_state.sa:
    data["Simulated Annealing"] = st.session_state.sa
if data:
    st.subheader("Cost over iterations (lower is better)")
    st.line_chart(pd.DataFrame(data))

with st.expander("Rules and explanation"):
    st.write("**State:** one full timetable (5 days x 6 periods).")
    st.write("**Cost:** same subject twice a day +10, back-to-back +5, "
             "Maths/AI in the afternoon +3. Cost 0 means perfect.")
    st.write("**Neighbour move:** swap two random slots.")
    st.write("**Hill Climbing:** keep a swap only if the cost is not worse. "
             "Can get stuck in a local minimum.")
    st.write("**Simulated Annealing:** also accepts worse swaps with "
             "probability e^(-delta/T); T cools slowly, so it can escape "
             "local minima.")
