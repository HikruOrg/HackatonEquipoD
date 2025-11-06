import pandas as pd
import plotly.express as px
from pathlib import Path

def save_excel(df, path="outputs/top3_by_user.xlsx"):
    # Ensure outputs directory exists
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_excel(path, index=False)
    print(f"✅ Excel saved to {path}")

def save_html(df, path="outputs/index.html", invert_axes: bool = True):
    """Save interactive HTML dashboard.

    Args:
        df: DataFrame with columns ['user','category','score']
        path: Output HTML path
        invert_axes: If True, show users on x-axis and categories as color groups.
                      If False, keep original layout (categories on x-axis).
    """
    # Ensure outputs directory exists
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if invert_axes:
        fig = px.bar(
            df,
            x="user",
            y="score",
            color="category",
            barmode="group",
            title="Top Categories by User (Inverted Axes)",
        )
    else:
        fig = px.bar(
            df,
            x="category",
            y="score",
            color="user",
            barmode="group",
            title="Top 3 Categories per User",
        )

    fig.update_layout(xaxis_title="User" if invert_axes else "Category",
                      yaxis_title="Score",
                      legend_title_text="Category" if invert_axes else "User")
    fig.write_html(path)
    print(f"✅ Dashboard saved to {path} (invert_axes={invert_axes})")
