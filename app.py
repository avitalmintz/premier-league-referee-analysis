import streamlit as st
from data_utils import (
    load_and_combine,
    compute_standings,
    compute_slope_data,
    compute_home_away,
    compute_referee_summary,
    compute_referee_outcomes,
)
from charts import (
    chart_slope,
    chart_home_away,
    chart_referee_cards,
    chart_referee_outcomes,
)

st.set_page_config(page_title="The Effects of the Referee on Match Outcomes", layout="wide")

# ---------- load data ----------
all_matches = load_and_combine()
standings = compute_standings(all_matches)
slope_data = compute_slope_data(standings)
home_away_data = compute_home_away(all_matches)

# ---------- header ----------
st.title("The Effects of the Referee on Match Outcomes")
st.subheader("A Data Visualization Project at referee tendencies and match outcomes in the Premier League")

# ---------- dataset intro ----------
st.markdown(
    """
**About the Data**

This analysis draws on match-level data from
[football-data.co.uk](https://www.football-data.co.uk/englandm.php) covering
every Premier League fixture in the 2023–24 and 2024–25 seasons — 760 matches
in total. Each record includes full-time and half-time scores, the match
referee, and detailed statistics for both teams: shots, shots on target, fouls,
yellow cards, red cards, and corners. The dataset captures 20 teams and over
30 referees per season, giving us enough depth to explore patterns in both
team performance and officiating behavior.
"""
)

season = st.selectbox("Filter by season", ["Both", "2023-24", "2024-25"])

if season != "Both":
    matches_filtered = all_matches[all_matches["Season"] == season]
    ha_filtered = home_away_data[home_away_data["Season"] == season]
else:
    matches_filtered = all_matches
    ha_filtered = home_away_data

ref_summary = compute_referee_summary(matches_filtered)
ref_outcomes = compute_referee_outcomes(matches_filtered)

league_home_wins = (matches_filtered["FTR"] == "H").sum()
league_avg_hwp = league_home_wins / len(matches_filtered)

# ========================================================
# SECTION 1: Setting the Table
# ========================================================
st.divider()
st.header("The Premier League Standings")

st.write(
    """
Manchester City won the 2023-24 Premier League with 91 points. The following season,
Liverpool took the title and City fell to fourth. Some teams made big jumps (Nottingham
Forest went from 17th to 5th), while others were relegated or promoted between seasons.

The slope chart below shows how every team that played both seasons moved in the
standings. Green lines mean a team improved, red lines mean they dropped. Click on
any team to isolate it.
"""
)

st.altair_chart(chart_slope(slope_data), use_container_width=True)
st.caption(
    "Click a team to highlight it. Only the 17 teams present in both seasons are shown."
)

st.write(
    """
But league tables only show final results. They don't say anything about what
happened during the match itself, or about the person in the middle making calls
the whole time: the referee.
"""
)

# ========================================================
# SECTION 2: The Impact of Home Advantage on Match Outcomes
# ========================================================
st.divider()
st.header("The Impact of Home Advantage on Match Outcomes")

total = len(matches_filtered)
home_wins = (matches_filtered["FTR"] == "H").sum()
draws = (matches_filtered["FTR"] == "D").sum()
away_wins = (matches_filtered["FTR"] == "A").sum()

col1, col2, col3 = st.columns(3)
col1.metric("Home Wins", f"{home_wins} ({home_wins/total*100:.1f}%)")
col2.metric("Draws", f"{draws} ({draws/total*100:.1f}%)")
col3.metric("Away Wins", f"{away_wins} ({away_wins/total*100:.1f}%)")

st.write(
    f"""
Across {'both seasons combined' if season == 'Both' else 'the ' + season + ' season'},
home teams won {home_wins/total*100:.1f}% of matches compared to {away_wins/total*100:.1f}%
for away teams. That's about a 10 percentage point difference in win probability just from
playing at home.

Some teams benefit more than others. In the scatter plot below, each dot is one team.
The dashed diagonal is where a team would be if they earned the same points home and
away. Most sit below it, meaning they do better at home. You can drag across a group
of dots to rank them by home advantage in the bar chart on the right.
"""
)

st.altair_chart(chart_home_away(ha_filtered), use_container_width=True)
st.caption("Drag to select teams in the scatter. The bar chart shows their home advantage.")

st.write(
    """
Home advantage is well-documented in football and usually attributed to things like
crowd support and travel fatigue. But there's another factor worth looking at: the
referee.
"""
)

# ========================================================
# SECTION 3: The Impact of the Referee on Card Counts
# ========================================================
st.divider()
st.header("The Impact of the Referee on Card Counts")

# find top/bottom refs in filtered data
ref_agg = (
    matches_filtered.groupby("Referee")
    .agg(
        Matches=("Date", "count"),
        AvgCards=("TotalYellows", "mean"),
    )
    .reset_index()
)
ref_agg["AvgCards"] = (
    ref_agg["AvgCards"]
    + matches_filtered.groupby("Referee")["TotalReds"].mean().values
)
ref_agg["AvgCards"] = ref_agg["AvgCards"].round(2)
regulars = ref_agg[ref_agg["Matches"] >= 15].sort_values("AvgCards", ascending=False)

if len(regulars) >= 2:
    top_ref = regulars.iloc[0]
    bot_ref = regulars.iloc[-1]
    most_used = ref_agg.sort_values("Matches", ascending=False).iloc[0]

    c1, c2, c3 = st.columns(3)
    c1.metric("Most Active Referee", most_used["Referee"], f"{most_used['Matches']:.0f} matches")
    c2.metric("Highest Card Rate", top_ref["Referee"], f"{top_ref['AvgCards']:.2f} per match")
    c3.metric("Lowest Card Rate", bot_ref["Referee"], f"{bot_ref['AvgCards']:.2f} per match")

st.write(
    """
Different referees hand out cards at very different rates. Across both seasons,
32 referees officiated Premier League matches, but a core group handled most of the
games. Among those regulars, the gap between the strictest and most lenient is over
a full card per match on average. That adds up over a season.

Click on a referee in the bar chart below to see how their card counts look on a
match-by-match basis.
"""
)

st.altair_chart(
    chart_referee_cards(ref_summary, matches_filtered), use_container_width=True
)
st.caption("Click a referee to see their match-level detail on the right.")

avg_home_yellows = matches_filtered["HY"].mean()
avg_away_yellows = matches_filtered["AY"].mean()

st.write(
    f"""
It's also worth noting that away teams get more yellow cards than home teams on
average: {avg_away_yellows:.2f} per match versus {avg_home_yellows:.2f} for home
sides. That could be because away teams tend to play more aggressively, or because
referees are a bit more lenient toward the home side. Either way, it's a consistent
pattern.
"""
)

# ========================================================
# SECTION 4: Does the Whistle Pick Sides?
# ========================================================
st.divider()
st.header("The Impact of the Referee on Home Win Probability")

st.write(
    f"""
Referees have different discipline styles, and away teams tend to get carded more.
Does any of that actually relate to the home win probability?

The chart below compares each referee's home win rate to the league average of
{league_avg_hwp*100:.1f}%. Green bars are above average (more home wins), red bars
are below. Only referees with 15 or more matches are included to avoid small sample
size issues.
"""
)

st.altair_chart(
    chart_referee_outcomes(ref_outcomes, league_avg_hwp), use_container_width=True
)
st.caption(
    f"Dashed line = league average home win rate ({league_avg_hwp:.1%}). "
    "Only referees with 15+ matches shown."
)

# highlight specific referees
if len(ref_outcomes) > 0:
    top_hw = ref_outcomes.sort_values("HomeWinPct", ascending=False).iloc[0]
    bot_hw = ref_outcomes.sort_values("HomeWinPct", ascending=True).iloc[0]

    st.write(
        f"""
There's a pretty wide range. {top_hw['Referee']} has a {top_hw['HomeWinPct']*100:.1f}%
home win rate across {top_hw['Matches']:.0f} matches, while {bot_hw['Referee']} is at
{bot_hw['HomeWinPct']*100:.1f}% across {bot_hw['Matches']:.0f} matches. That's a
{(top_hw['HomeWinPct'] - bot_hw['HomeWinPct'])*100:.1f} percentage point difference.

This doesn't mean referees are deciding who wins. Referee assignments aren't random;
the PGMOL assigns officials based on team conflicts and experience, so a referee with
a high home win rate might just be getting assigned to matches where the home team was
already favored. It's a correlation, not proof of anything.

Still, the variation is large enough to be interesting. The data shows that match
conditions look noticeably different depending on who the referee is, even if we
can't say exactly why from this dataset alone.
"""
    )

# ========================================================
# SECTION 5: More to Explore
# ========================================================
st.divider()
st.header("More to Explore")

st.write(
    """
A few caveats on all of this.

Card counts don't tell you whether the cards were deserved. A referee assigned to
rougher matches will naturally have higher averages even if every call was correct.

Sample sizes are also limited. The busiest referees have around 50-60 matches in
this dataset. That's enough to see patterns but not enough to make strong claims
about any one person.

This analysis doesn't prove referees cause teams to win or lose. But it does show
that different referees are associated with different kinds of matches and different
outcome distributions. That's worth knowing, even if the reasons behind it need
more data to fully explain.
"""
)

st.divider()
st.markdown(
    "**Data source:** [football-data.co.uk](https://www.football-data.co.uk/englandm.php) "
    "| Premier League seasons 2023-24 and 2024-25"
)
st.markdown("**Built with** Streamlit and Altair")
