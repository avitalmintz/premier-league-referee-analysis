import streamlit as st
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@st.cache_data
def load_and_combine():
    s1 = pd.read_csv(os.path.join(DATA_DIR, "PL-season-2324.csv"))
    s2 = pd.read_csv(os.path.join(DATA_DIR, "PL-season-2425.csv"))
    s1["Season"] = "2023-24"
    s2["Season"] = "2024-25"

    df = pd.concat([s1, s2], ignore_index=True)
    df["Referee"] = df["Referee"].str.strip()
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%y")

    df["TotalGoals"] = df["FTHG"] + df["FTAG"]
    df["GoalDifference"] = df["FTHG"] - df["FTAG"]
    df["TotalYellows"] = df["HY"] + df["AY"]
    df["TotalReds"] = df["HR"] + df["AR"]
    df["TotalFouls"] = df["HF"] + df["AF"]
    df["MatchLabel"] = (
        df["HomeTeam"]
        + " "
        + df["FTHG"].astype(str)
        + "-"
        + df["FTAG"].astype(str)
        + " "
        + df["AwayTeam"]
    )
    df = df.sort_values(["Season", "Date"]).reset_index(drop=True)
    df["Matchweek"] = df.groupby("Season").cumcount() // 10 + 1
    return df


@st.cache_data
def compute_standings(all_matches):
    home = all_matches[["HomeTeam", "FTHG", "FTAG", "FTR", "Season"]].copy()
    home.columns = ["Team", "GoalsFor", "GoalsAgainst", "Result", "Season"]
    home["Points"] = home["Result"].map({"H": 3, "D": 1, "A": 0})
    home["Win"] = (home["Result"] == "H").astype(int)
    home["Draw"] = (home["Result"] == "D").astype(int)
    home["Loss"] = (home["Result"] == "A").astype(int)

    away = all_matches[["AwayTeam", "FTAG", "FTHG", "FTR", "Season"]].copy()
    away.columns = ["Team", "GoalsFor", "GoalsAgainst", "Result", "Season"]
    away["Points"] = away["Result"].map({"A": 3, "D": 1, "H": 0})
    away["Win"] = (away["Result"] == "A").astype(int)
    away["Draw"] = (away["Result"] == "D").astype(int)
    away["Loss"] = (away["Result"] == "H").astype(int)

    every = pd.concat([home, away], ignore_index=True)
    standings = (
        every.groupby(["Team", "Season"])
        .agg(
            Points=("Points", "sum"),
            Wins=("Win", "sum"),
            Draws=("Draw", "sum"),
            Losses=("Loss", "sum"),
            GoalsFor=("GoalsFor", "sum"),
            GoalsAgainst=("GoalsAgainst", "sum"),
        )
        .reset_index()
    )
    standings["GoalDifference"] = standings["GoalsFor"] - standings["GoalsAgainst"]
    standings = standings.sort_values(
        ["Season", "Points", "GoalDifference", "GoalsFor"],
        ascending=[True, False, False, False],
    ).reset_index(drop=True)
    standings["Position"] = standings.groupby("Season").cumcount() + 1
    return standings


@st.cache_data
def compute_slope_data(standings):
    teams_2324 = set(standings[standings["Season"] == "2023-24"]["Team"])
    teams_2425 = set(standings[standings["Season"] == "2024-25"]["Team"])
    both = teams_2324 & teams_2425

    slope = standings[standings["Team"].isin(both)].copy()
    pos_2324 = slope[slope["Season"] == "2023-24"].set_index("Team")["Position"]
    pos_2425 = slope[slope["Season"] == "2024-25"].set_index("Team")["Position"]
    change = (pos_2324 - pos_2425).reset_index()
    change.columns = ["Team", "PositionChange"]
    slope = slope.merge(change, on="Team")
    return slope


@st.cache_data
def compute_home_away(all_matches):
    home = all_matches[["HomeTeam", "FTHG", "FTAG", "FTR", "Season"]].copy()
    home.columns = ["Team", "GoalsFor", "GoalsAgainst", "Result", "Season"]
    home["Points"] = home["Result"].map({"H": 3, "D": 1, "A": 0})
    home["Win"] = (home["Result"] == "H").astype(int)

    away = all_matches[["AwayTeam", "FTAG", "FTHG", "FTR", "Season"]].copy()
    away.columns = ["Team", "GoalsFor", "GoalsAgainst", "Result", "Season"]
    away["Points"] = away["Result"].map({"A": 3, "D": 1, "H": 0})
    away["Win"] = (away["Result"] == "A").astype(int)

    hp = (
        home.groupby(["Team", "Season"])
        .agg(
            HomePoints=("Points", "sum"),
            HomeWins=("Win", "sum"),
            HomeGoalsFor=("GoalsFor", "sum"),
            HomeGoalsAgainst=("GoalsAgainst", "sum"),
        )
        .reset_index()
    )
    hp["HomeGD"] = hp["HomeGoalsFor"] - hp["HomeGoalsAgainst"]

    ap = (
        away.groupby(["Team", "Season"])
        .agg(
            AwayPoints=("Points", "sum"),
            AwayWins=("Win", "sum"),
            AwayGoalsFor=("GoalsFor", "sum"),
            AwayGoalsAgainst=("GoalsAgainst", "sum"),
        )
        .reset_index()
    )
    ap["AwayGD"] = ap["AwayGoalsFor"] - ap["AwayGoalsAgainst"]

    merged = hp.merge(ap, on=["Team", "Season"])
    merged["HomeAdvantage"] = merged["HomePoints"] - merged["AwayPoints"]
    return merged


@st.cache_data
def compute_referee_summary(all_matches):
    ref = (
        all_matches.groupby(["Referee", "Season"])
        .agg(
            MatchesOfficiated=("Date", "count"),
            AvgFouls=("TotalFouls", "mean"),
            AvgYellowCards=("TotalYellows", "mean"),
            AvgRedCards=("TotalReds", "mean"),
            TotalYellows=("TotalYellows", "sum"),
            TotalReds=("TotalReds", "sum"),
        )
        .reset_index()
    )
    ref["AvgFouls"] = ref["AvgFouls"].round(2)
    ref["AvgYellowCards"] = ref["AvgYellowCards"].round(2)
    ref["AvgRedCards"] = ref["AvgRedCards"].round(2)
    ref["AvgCardsPerMatch"] = (ref["AvgYellowCards"] + ref["AvgRedCards"]).round(2)
    return ref


@st.cache_data
def compute_referee_outcomes(all_matches, min_matches=15):
    ref = (
        all_matches.groupby("Referee")
        .agg(
            Matches=("Date", "count"),
            HomeWins=("FTR", lambda x: (x == "H").sum()),
            Draws=("FTR", lambda x: (x == "D").sum()),
            AwayWins=("FTR", lambda x: (x == "A").sum()),
        )
        .reset_index()
    )
    ref["HomeWinPct"] = (ref["HomeWins"] / ref["Matches"]).round(3)
    ref["DrawPct"] = (ref["Draws"] / ref["Matches"]).round(3)
    ref["AwayWinPct"] = (ref["AwayWins"] / ref["Matches"]).round(3)
    ref = ref[ref["Matches"] >= min_matches].copy()
    return ref
