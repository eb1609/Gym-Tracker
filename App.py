import streamlit as st
import pandas as pd
from datetime import datetime
import os

WORKOUTS_FILE = "workouts.csv"
EXERCISES_FILE = "exercises.csv"

WORKOUTS_FILE = "workouts.csv"
EXERCISES_FILE = "exercises.csv"


if not os.path.exists(WORKOUTS_FILE):
    pd.DataFrame(
        columns=["date", "notes", "total_volume"]
    ).to_csv(WORKOUTS_FILE, index=False)

if not os.path.exists(EXERCISES_FILE):
    pd.DataFrame(
        columns=[
            "date",
            "muscle_group",
            "exercise",
            "set_number",
            "reps",
            "weight",
            "volume",
            "PR"
        ]
    ).to_csv(EXERCISES_FILE, index=False)



workouts = pd.read_csv(WORKOUTS_FILE)
exercises = pd.read_csv(EXERCISES_FILE)


workouts = pd.read_csv(WORKOUTS_FILE)
exercises = pd.read_csv(EXERCISES_FILE)

st.title("💪 Personal Gym Tracker")

tab_log, tab_analytics, tab_prs = st.tabs(
    ["Log Workout", "Analytics", "PRs"]
)


EXERCISE_LIBRARY = {
    "Abs": {
        "Upper Abs": [
            "Machine Crunch",
            "Decline Crunch",
            "Cable Crunch"
        ],
        "Lower Abs": [
            "Leg Raises",
            "Ab Scissors"
        ],
        "Full Core": [
            "Ab Wheel",
            "Dragon Flag",
            "Bicycle Crunch"
        ],
        "Obliques": [
            "Russian Twists",
            "Torso Twist"
        ]
    },

    "Back": {
        "Lats": [
            "Lat Pulldown",
            "Pull Up",
            "Chin Up",
            "Single Arm Lat Pulldown"
        ],
        "Mid Back": [
            "Barbell Row",
            "Cable Row",
            "Chest-Supported Row",
            "High Row",
            "T-Bar Row",
            "Dumbbell Row"
        ],
        "Traps": [
            "Dumbbell Shrugs",
            "Kelso Shrugs"
        ],
        "Lower Back": [
            "Hyperextensions"
        ],
    },

    "Biceps": {
        "Brachialis": [
            "Hammer Curl"
        ],
        "General": [
            "Bayesian Curl",
            "Bicep Curl",
            "Concentration Curl",
            "Preacher Curl",
            "Seated Incline Curl",
            "Spider Curl"
        ]
    },

    "Chest": {
        "Upper Chest": [
            "Barbell Incline Bench Press",
            "Dumbbell Incline Bench Press",
            "Smith Machine Incline Bench Press"
        ],
        "Mid Chest": [
            "Bench Press",
            "Chest Press",
            "Pec Deck"
        ],
        "Lower Chest": [
            "High to Low Cable Flies"
        ],
        "Chest Fly": [
            "Low to High Cable Flies"
        ]
    },

    "Legs": {
        "Quads": [
            "Barbell Squats",
            "Hack Squat",
            "Pendulum Squat",
            "Leg Press",
            "Leg Extension"
        ],
        "Hamstrings": [
            "Leg Curls",
            "Romanian Deadlift",
            "Stiff Leg Deadlift"
        ],
        "Calves": [
            "Machine Calf Press",
            "Seated Calf Raises",
            "Standing Calf Raises"
        ],
        "Adductors / Abductors": [
            "Hip Adduction Machine",
            "Hip Abduction Machine"
        ]
    },

    "Shoulders": {
        "Front Delts": [
            "Dumbbell Shoulder Press",
            "Machine Shoulder Press"
        ],
        "Side Delts": [
            "Dumbbell Lateral Raises",
            "Cable Lateral Raises",
            "Machine Lateral Raises"
        ],
        "Rear Delts": [
            "Cable Rear Delt Flies",
            "Face Pulls",
            "Machine Rear Delt Flies"
        ]
    },

    "Triceps": {
        "Long Head": [
        "Overhead Dumbbell Extension",
        "Overhead Cable Extension",
        "Skull Crushers"
    ],
    "Lateral Head": [
        "Cable Pushdowns",
        "V-Bar Pushdowns",
        "Close-Grip Bench Press",
        "Dips"
    ]
    }

}


EXERCISE_TO_MUSCLE = {}

for body_part, subgroups in EXERCISE_LIBRARY.items():
    for sub_muscle, exercise_list in subgroups.items():
        for ex in exercise_list:
            EXERCISE_TO_MUSCLE[ex] = {
                "body_part": body_part,
                "sub_muscle": sub_muscle
            }

exercises["body_part"] = exercises["exercise"].map(
    lambda x: EXERCISE_TO_MUSCLE.get(x, {}).get("body_part", "Other")
)

exercises["sub_muscle"] = exercises["exercise"].map(
    lambda x: EXERCISE_TO_MUSCLE.get(x, {}).get("sub_muscle", "Other")
)

exercises["date"] = pd.to_datetime(
    exercises["date"],
    format="mixed",
    errors="coerce"
)

exercises["week"] = exercises["date"].dt.to_period("W").astype(str)

weekly_volume = (
    exercises
    .groupby(["week", "body_part", "sub_muscle"])["volume"]
    .sum()
    .reset_index()
)



with tab_log:
    st.header("Log New Exercise")

    workout_date = st.date_input(
        "Workout Date", datetime.today()
    )

    notes = st.text_area("Workout Notes")

    st.subheader("Exercise")

    muscle_group = st.selectbox(
        "Muscle Group",
        list(EXERCISE_LIBRARY.keys())
    )

    exercise_options = []
    for subgroup in EXERCISE_LIBRARY[muscle_group].values():
        exercise_options.extend(subgroup)

    exercise_name = st.selectbox(
        "Exercise",
        exercise_options
    )
    st.subheader("Sets")

    num_sets = st.number_input(
        "Number of Sets",
        min_value=1,
        value=3,
        step=1
    )

    set_data = []

    for i in range(num_sets):
        st.markdown(f"**Set {i+1}**")

        reps = st.number_input(
            f"Reps (Set {i+1})",
            min_value=1,
            value=8,
            key=f"reps_{i}"
        )

        weight = st.number_input(
            f"Weight (Set {i+1})",
            min_value=0.0,
            value=20.0,
            step=1.0,
            key=f"weight_{i}"
        )

        volume = reps * weight

        set_data.append({
            "set_number": i + 1,
            "reps": reps,
            "weight": weight,
            "volume": volume
        })

    if st.button("Add Exercise"):
        workout_date = pd.to_datetime(workout_date)

        if exercise_name == "":
            st.error("Please enter an exercise name")
            st.stop()

        previous_max = exercises[
            exercises["exercise"] == exercise_name
        ]["weight"].max()

        session_max = max(s["weight"] for s in set_data)
        is_pr = pd.isna(previous_max) or session_max > previous_max

        new_rows = []

        for s in set_data:
            new_rows.append([
                workout_date.strftime("%Y-%m-%d"),
                muscle_group,
                exercise_name,
                s["set_number"],
                s["reps"],
                s["weight"],
                s["volume"],
                is_pr and s["weight"] == session_max
            ])

        new_df = pd.DataFrame(
            new_rows,
            columns=[
                "date",
                "muscle_group",
                "exercise",
                "set_number",
                "reps",
                "weight",
                "volume",
                "PR"
            ]
        )

        exercises = pd.concat([exercises, new_df], ignore_index=True)
        exercises.to_csv(EXERCISES_FILE, index=False)

        st.success(
            f"Logged {exercise_name} ({num_sets} sets) on {workout_date.date()}"
        )

with tab_prs:
    st.subheader("Personal Records ")

    if exercises.empty:
        st.info("No exercises logged yet.")
        st.stop()



    max_weight_prs = (
        exercises
        .loc[exercises.groupby("exercise")["weight"].idxmax()]
        .sort_values("weight", ascending=False)
    )
    st.dataframe(
        max_weight_prs[
            ["exercise", "weight", "reps", "date"]
        ],
        use_container_width=True
    )

with tab_analytics:
    st.subheader("📅 Weekly Volume by Sub-Muscle")

    selected_week = st.selectbox(
        "Select Week",
        sorted(exercises["week"].dropna().unique(), reverse=True)
    )

    week_data = weekly_volume[
        weekly_volume["week"] == selected_week
    ]

    st.dataframe(
        week_data.sort_values("volume", ascending=False)
    )

    daily_volume = (
        exercises
        .groupby("date")["volume"]
        .sum()
        .reset_index()
    )

    daily_volume["date"] = pd.to_datetime(daily_volume["date"])
    daily_volume["week"] = daily_volume["date"].dt.isocalendar().week
    daily_volume["weekday"] = daily_volume["date"].dt.weekday

    heatmap_data = daily_volume.pivot_table(
    index="weekday",
    columns="week",
    values="volume",
    aggfunc="sum"
    ).fillna(0)


    heatmap_data = heatmap_data.sort_index()

    st.subheader("🔥 Workout Consistency")
    st.write("Darker squares = more training volume")

    st.dataframe(
        heatmap_data,
        height=250
    )
    st.subheader("🟩 Training Consistency (2026)")

    start_date = pd.Timestamp("2026-01-01")
    end_date = pd.Timestamp("2026-12-31")


    calendar_df = (
        exercises
        .groupby("date")["volume"]
        .sum()
        .reset_index()
    )

    calendar_df["date"] = pd.to_datetime(calendar_df["date"])
    calendar_df = calendar_df[
        (calendar_df["date"] >= start_date) &
        (calendar_df["date"] <= end_date)
    ]

    all_days = pd.DataFrame({
        "date": pd.date_range(start_date, end_date, freq="D")
    })

    calendar_df = all_days.merge(
        calendar_df, on="date", how="left"
    ).fillna(0)

    calendar_df["dow"] = calendar_df["date"].dt.weekday
    calendar_df["week"] = (
        calendar_df["date"]
        - pd.to_timedelta(calendar_df["dow"], unit="D")
    )

    weekly_order = calendar_df["week"].drop_duplicates().sort_values()

    max_vol = calendar_df["volume"].max()

    def color_scale(v):
        if v == 0:
            return "#ebedf0"
        elif v < max_vol * 0.25:
            return "#9be9a8"
        elif v < max_vol * 0.5:
            return "#40c463"
        elif v < max_vol * 0.75:
            return "#30a14e"
        else:
            return "#216e39"

    calendar_df["color"] = calendar_df["volume"].apply(color_scale)

    html = """
    <style>
    .calendar {
        display: grid;
        grid-template-columns: repeat(""" + str(len(weekly_order)) + """, 14px);
        gap: 3px;
    }
    .cell {
        width: 14px;
        height: 14px;
        border-radius: 3px;
    }
    </style>
    <div class="calendar">
    """

    for dow in range(7):
        for wk in weekly_order:
            cell = calendar_df[
                (calendar_df["week"] == wk) &
                (calendar_df["dow"] == dow)
            ]
            color = cell["color"].iloc[0] if not cell.empty else "#ebedf0"
            html += f'<div class="cell" style="background:{color}"></div>'

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)
    st.subheader("📅 Select Day")
    selected_date = st.date_input(
    "Workout date",
    value=pd.to_datetime("2026-01-01"),
    min_value=pd.to_datetime("2026-01-01"),
    max_value=pd.to_datetime("2026-12-31")
)
    st.subheader("📖 Workout History")
day_log = exercises[exercises["date"].dt.date == selected_date]

if day_log.empty:
    st.info("No workout logged on this day.")
else:
    st.dataframe(
        day_log[["exercise", "set_number", "reps", "weight", "volume", "body_part"]],
        use_container_width=True
    )
    st.metric("Total Volume", int(day_log["volume"].sum()))





