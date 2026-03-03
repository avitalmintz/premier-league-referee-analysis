import altair as alt
import pandas as pd


def chart_slope(slope_data):
    team_click = alt.selection_point(fields=["Team"])

    position_color = alt.Color(
        "PositionChange:Q",
        scale=alt.Scale(scheme="redyellowgreen", domainMid=0),
        legend=alt.Legend(title="Positions Moved\n(+ = up, - = down)"),
    )

    lines = (
        alt.Chart(slope_data)
        .mark_line(strokeWidth=2.5)
        .encode(
            x=alt.X(
                "Season:N",
                title=None,
                axis=alt.Axis(labelAngle=0, labelFontSize=14),
            ),
            y=alt.Y(
                "Position:Q",
                title="League Position (1 = best)",
                scale=alt.Scale(reverse=True, domain=[1, 20]),
                axis=alt.Axis(tickMinStep=1),
            ),
            color=position_color,
            detail="Team:N",
            opacity=alt.condition(team_click, alt.value(1), alt.value(0.3)),
            tooltip=[
                alt.Tooltip("Team:N"),
                alt.Tooltip("Season:N"),
                alt.Tooltip("Position:Q"),
                alt.Tooltip("Points:Q"),
                alt.Tooltip("PositionChange:Q", title="Positions Moved"),
            ],
        )
    )

    dots = (
        alt.Chart(slope_data)
        .mark_circle(size=80)
        .encode(
            x="Season:N",
            y=alt.Y("Position:Q", scale=alt.Scale(reverse=True)),
            color=alt.Color(
                "PositionChange:Q",
                scale=alt.Scale(scheme="redyellowgreen", domainMid=0),
                legend=None,
            ),
            opacity=alt.condition(team_click, alt.value(1), alt.value(0.4)),
            tooltip=[
                alt.Tooltip("Team:N"),
                alt.Tooltip("Season:N"),
                alt.Tooltip("Position:Q"),
                alt.Tooltip("Points:Q"),
                alt.Tooltip("GoalDifference:Q", title="Goal Diff"),
            ],
        )
        .add_params(team_click)
    )

    labels_left = (
        alt.Chart(slope_data[slope_data["Season"] == "2023-24"])
        .mark_text(align="right", dx=-12, fontSize=10)
        .encode(
            x="Season:N",
            y=alt.Y("Position:Q", scale=alt.Scale(reverse=True)),
            text="Team:N",
            opacity=alt.condition(team_click, alt.value(1), alt.value(0.5)),
        )
    )

    labels_right = (
        alt.Chart(slope_data[slope_data["Season"] == "2024-25"])
        .mark_text(align="left", dx=12, fontSize=10)
        .encode(
            x="Season:N",
            y=alt.Y("Position:Q", scale=alt.Scale(reverse=True)),
            text="Team:N",
            opacity=alt.condition(team_click, alt.value(1), alt.value(0.5)),
        )
    )

    return (lines + dots + labels_left + labels_right).properties(
        width=400, height=550
    )


def chart_home_away(home_away_data):
    team_brush = alt.selection_interval()

    diagonal = pd.DataFrame({"HomePoints": [5, 55], "AwayPoints": [5, 55]})
    diag_line = (
        alt.Chart(diagonal)
        .mark_line(strokeDash=[4, 4], color="gray", opacity=0.4)
        .encode(x="HomePoints:Q", y="AwayPoints:Q")
    )

    dots = (
        alt.Chart(home_away_data)
        .mark_circle(size=100)
        .encode(
            x=alt.X(
                "HomePoints:Q",
                title="Points from Home Games",
                scale=alt.Scale(zero=False),
            ),
            y=alt.Y(
                "AwayPoints:Q",
                title="Points from Away Games",
                scale=alt.Scale(zero=False),
            ),
            color=alt.condition(
                team_brush,
                alt.Color(
                    "HomeAdvantage:Q",
                    scale=alt.Scale(scheme="redyellowgreen", domainMid=0),
                    legend=alt.Legend(title="Home Advantage\n(Home - Away Pts)"),
                ),
                alt.value("#d3d3d3"),
            ),
            tooltip=[
                alt.Tooltip("Team:N"),
                alt.Tooltip("Season:N"),
                alt.Tooltip("HomePoints:Q", title="Home Pts"),
                alt.Tooltip("AwayPoints:Q", title="Away Pts"),
                alt.Tooltip("HomeAdvantage:Q", title="Home Advantage"),
            ],
        )
        .add_params(team_brush)
    )

    labels = (
        alt.Chart(home_away_data)
        .mark_text(align="left", dx=8, fontSize=8)
        .encode(
            x=alt.X("HomePoints:Q", scale=alt.Scale(zero=False)),
            y=alt.Y("AwayPoints:Q", scale=alt.Scale(zero=False)),
            text="Team:N",
            opacity=alt.condition(team_brush, alt.value(1), alt.value(0.25)),
        )
    )

    scatter = (diag_line + dots + labels).properties(width=380, height=380)

    bars = (
        alt.Chart(home_away_data)
        .mark_bar()
        .encode(
            y=alt.Y(
                "Team:N",
                title=None,
                sort=alt.EncodingSortField(
                    field="HomeAdvantage", order="descending"
                ),
            ),
            x=alt.X("HomeAdvantage:Q", title="Home Advantage (pts)"),
            color=alt.Color(
                "HomeAdvantage:Q",
                scale=alt.Scale(scheme="redyellowgreen", domainMid=0),
                legend=None,
            ),
            tooltip=[
                alt.Tooltip("Team:N"),
                alt.Tooltip("HomePoints:Q", title="Home Pts"),
                alt.Tooltip("AwayPoints:Q", title="Away Pts"),
                alt.Tooltip("HomeAdvantage:Q", title="Home Advantage"),
            ],
        )
        .transform_filter(team_brush)
        .properties(width=280, height=380)
    )

    return alt.hconcat(scatter, bars).resolve_scale(color="independent")


def chart_referee_cards(referee_summary, all_matches):
    ref_click = alt.selection_point(fields=["Referee"])

    bar = (
        alt.Chart(referee_summary)
        .mark_bar()
        .encode(
            y=alt.Y(
                "Referee:N",
                sort=alt.EncodingSortField(
                    field="AvgCardsPerMatch", order="descending"
                ),
                title=None,
            ),
            x=alt.X("AvgCardsPerMatch:Q", title="Avg Cards per Match"),
            color=alt.condition(
                ref_click,
                alt.Color(
                    "AvgCardsPerMatch:Q",
                    scale=alt.Scale(scheme="orangered"),
                    legend=None,
                ),
                alt.value("#d3d3d3"),
            ),
            opacity=alt.condition(ref_click, alt.value(1), alt.value(0.5)),
            tooltip=[
                alt.Tooltip("Referee:N"),
                alt.Tooltip("Season:N"),
                alt.Tooltip("MatchesOfficiated:Q", title="Matches"),
                alt.Tooltip("AvgYellowCards:Q", title="Avg Yellows"),
                alt.Tooltip("AvgRedCards:Q", title="Avg Reds"),
                alt.Tooltip("AvgFouls:Q", title="Avg Fouls"),
            ],
        )
        .add_params(ref_click)
        .properties(width=300, height=450)
    )

    detail = (
        alt.Chart(all_matches)
        .mark_circle()
        .encode(
            x=alt.X("Date:T", title="Match Date"),
            y=alt.Y(
                "TotalYellows:Q",
                title="Yellow Cards in Match",
                axis=alt.Axis(tickMinStep=1),
            ),
            color=alt.Color(
                "TotalFouls:Q",
                scale=alt.Scale(scheme="blues"),
                legend=alt.Legend(title="Total Fouls"),
            ),
            size=alt.Size(
                "TotalFouls:Q", scale=alt.Scale(range=[30, 250]), legend=None
            ),
            tooltip=[
                alt.Tooltip("MatchLabel:N", title="Match"),
                alt.Tooltip("Date:T", format="%b %d, %Y"),
                alt.Tooltip("Referee:N"),
                alt.Tooltip("TotalYellows:Q", title="Yellows"),
                alt.Tooltip("TotalReds:Q", title="Reds"),
                alt.Tooltip("TotalFouls:Q", title="Fouls"),
            ],
        )
        .transform_filter(ref_click)
        .properties(width=400, height=450)
    )

    return alt.hconcat(bar, detail).resolve_scale(color="independent")


def chart_referee_outcomes(ref_outcomes, league_avg_home_win_pct):
    rule_df = pd.DataFrame({"x": [league_avg_home_win_pct]})

    bars = (
        alt.Chart(ref_outcomes)
        .mark_bar()
        .encode(
            y=alt.Y(
                "Referee:N",
                sort=alt.EncodingSortField(
                    field="HomeWinPct", order="descending"
                ),
                title=None,
            ),
            x=alt.X(
                "HomeWinPct:Q",
                title="Home Win Rate",
                axis=alt.Axis(format=".0%"),
            ),
            color=alt.condition(
                alt.datum.HomeWinPct > league_avg_home_win_pct,
                alt.value("#2ca02c"),
                alt.value("#d62728"),
            ),
            tooltip=[
                alt.Tooltip("Referee:N"),
                alt.Tooltip("Matches:Q"),
                alt.Tooltip("HomeWinPct:Q", title="Home Win %", format=".1%"),
                alt.Tooltip("DrawPct:Q", title="Draw %", format=".1%"),
                alt.Tooltip("AwayWinPct:Q", title="Away Win %", format=".1%"),
            ],
        )
    )

    rule = (
        alt.Chart(rule_df)
        .mark_rule(strokeDash=[6, 4], color="black", strokeWidth=2)
        .encode(x="x:Q")
    )

    label = (
        alt.Chart(rule_df)
        .mark_text(align="left", dx=4, dy=-8, fontSize=11, color="black")
        .encode(x="x:Q", text=alt.value(f"League avg: {league_avg_home_win_pct:.1%}"))
    )

    return (bars + rule + label).properties(width=550, height=450)
