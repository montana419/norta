import base64
import io
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")  # Force headless backend to prevent GUI thread crashes during tests


def _fig_to_base64(fig) -> str:
    """Converts a Matplotlib figure to a base64 string and cleans up memory."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=140)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return img_str


# --- 1. Employee List Table ---
def generate_employee_list_image(employees_list, client_name: str = "Default Client") -> str | None:
    """Generates a tabular image visualizing the employee directory scoped by client."""
    if not employees_list:
        return None

    # Convert the list of dicts to a clean DataFrame
    df = pd.DataFrame(employees_list)

    # Reorder/Rename columns for public display
    required_cols = ["id", "name", "role", "salary"]
    display_cols = [col for col in required_cols if col in df.columns]
    df = df[display_cols]

    col_mappings = {
        "id": "ID",
        "name": "Employee Name",
        "role": "Role",
        "salary": "Annual Salary ($)",
    }
    df.columns = [col_mappings.get(c, c) for c in df.columns]

    # Format salary column if present
    if "Annual Salary ($)" in df.columns:
        df["Annual Salary ($)"] = df["Annual Salary ($)"].apply(
            lambda x: f"${x:,.2f}" if isinstance(x, (int, float)) else str(x)
        )

    # Set up figure size dynamically based on row count
    fig, ax = plt.subplots(figsize=(10, max(len(df) * 0.5 + 1.5, 2.5)))
    ax.axis("off")

    # Create the table
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="left",
        loc="center",
        colColours=["#f0f0f0"] * len(df.columns),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.9)

    plt.title(f"Atlas Corporate Directory — [{client_name}]", fontsize=14, fontweight="bold", pad=20)
    return _fig_to_base64(fig)


# --- 2. Dynamic Salary Invoice ---
def generate_invoice_image(payout_data: dict) -> str | None:
    """Generates a visually structured invoice image for a salary payment with client scoping."""
    if not payout_data:
        return None

    client_name = payout_data.get("client_name", "Default Client")

    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.axis("off")

    # Styles
    header_style = {"family": "sans-serif", "weight": "bold", "size": 18}
    client_style = {"family": "sans-serif", "weight": "bold", "size": 12, "color": "#0288d1"}
    key_style = {"family": "sans-serif", "weight": "normal", "size": 12, "color": "#555555"}
    value_style = {"family": "sans-serif", "weight": "bold", "size": 14, "color": "black"}

    # Header
    y = 0.95
    ax.text(0.05, y, "SALARY INVOICE / REMITTANCE", fontdict=header_style, ha="left")
    y -= 0.06
    ax.text(0.05, y, f"CLIENT: {client_name.upper()}", fontdict=client_style, ha="left")
    ax.axhline(y - 0.03, xmin=0.05, xmax=0.95, color="#d0d0d0", linewidth=1)

    # Core details
    y -= 0.15
    line_height = 0.09
    total_due = float(payout_data.get("salary", 0.0))

    details = [
        ("Employee:", payout_data.get("employee_name", "N/A")),
        ("Role:", payout_data.get("role", "N/A")),
        ("Payment Date (UTC):", payout_data.get("timestamp", "N/A")),
        ("Status:", "PAID / EXECUTED"),
    ]

    for key, val in details:
        ax.text(0.1, y, key, fontdict=key_style, ha="left")
        ax.text(0.9, y, val, fontdict=value_style, ha="right")
        y -= line_height

    # Separator & Total
    y -= 0.03
    ax.axhline(y, xmin=0.05, xmax=0.95, color="black", linewidth=2)
    y -= 0.12
    ax.text(0.1, y, "TOTAL DISBURSED", fontdict={"weight": "bold", "size": 13}, ha="left")
    ax.text(0.9, y, f"${total_due:,.2f}", fontdict={"weight": "bold", "size": 18, "color": "#2e7d32"}, ha="right")

    # Footer
    y -= 0.10
    ax.text(0.5, y, f"Thank you for your contribution to {client_name}.", fontdict={"style": "italic", "color": "gray"}, ha="center")

    return _fig_to_base64(fig)


# --- 3. Financial Health Summary Charts ---
def generate_treasury_charts(transactions_list, client_name: str = "Default Client") -> str | None:
    """Generates dual charts for income, expenses, and net treasury positioning for a client."""
    if not transactions_list:
        return None

    income = sum(t["amount"] for t in transactions_list if t.get("trans_type") == "INCOME")
    expenses = sum(t["amount"] for t in transactions_list if t.get("trans_type") == "EXPENSE")
    net_treasury = income - expenses

    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    plt.suptitle(f"Atlas Corporate Financial Position — [{client_name}]", fontsize=16, fontweight="bold", y=1.03)

    # --- Chart 1: Flow Distribution Pie Chart ---
    labels = ["Income", "Expenses"]
    sizes = [income, expenses]
    colors = ["#81c784", "#e57373"]  # Soft Green, Soft Red

    if income == 0 and expenses == 0:
        axs[0].text(0.5, 0.5, "No Financial Flow Data Logged.", ha="center", va="center", color="gray")
        axs[0].axis("off")
    else:
        axs[0].pie(
            sizes,
            explode=(0.05, 0),
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            shadow=True,
            startangle=140,
        )
        axs[0].axis("equal")
        axs[0].set_title(f"Flow Split (Total: ${income + expenses:,.2f})")

    # --- Chart 2: Net Treasury Positioning Bar Chart ---
    labels_bar = ["Total Income", "Total Expenses", "Net Treasury"]
    values_bar = [income, expenses, net_treasury]
    colors_bar = ["#388e3c", "#d32f2f", "#1976d2"]  # Strong Green, Strong Red, Strong Blue

    y_pos = np.arange(len(labels_bar))
    axs[1].bar(y_pos, values_bar, color=colors_bar, alpha=0.9, edgecolor="black")

    for i, v in enumerate(values_bar):
        axs[1].text(i, v, f"${v:,.2f}", ha="center", va="bottom" if v >= 0 else "top", fontweight="bold")

    axs[1].set_xticks(y_pos)
    axs[1].set_xticklabels(labels_bar)
    axs[1].set_ylabel("Disbursed Amount ($)")
    axs[1].set_title("Financial Position Summary")
    axs[1].grid(axis="y", linestyle="--", alpha=0.5)

    return _fig_to_base64(fig)


# --- 4. Task List Table ---
def generate_task_list_image(tasks_list, client_name: str = "Default Client") -> str | None:
    """Generates a tabular image visualizing the task inbox scoped by client."""
    if not tasks_list:
        return None

    df = pd.DataFrame(tasks_list)

    cols_to_show = ["id", "title", "priority", "status", "created_at"]
    display_cols = [col for col in cols_to_show if col in df.columns]
    df = df[display_cols]

    col_mappings = {
        "id": "ID",
        "title": "Task Title",
        "priority": "Priority",
        "status": "Status",
        "created_at": "Date Added (UTC)",
    }
    df.columns = [col_mappings.get(c, c) for c in df.columns]

    if "Task Title" in df.columns:
        df["Task Title"] = df["Task Title"].apply(lambda x: str(x)[:40] + "..." if len(str(x)) > 40 else str(x))

    fig, ax = plt.subplots(figsize=(12, max(len(df) * 0.45 + 1.5, 2.5)))
    ax.axis("off")

    colors_map = {"High": "#ffe0e0", "Medium": "#fff5e0", "Low": "#e0ffe0"}
    row_colors = [colors_map.get(row.get("Priority"), "white") for _, row in df.iterrows()]

    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        cellLoc="left",
        loc="center",
        colColours=["#e8e8e8"] * len(df.columns),
        rowColours=row_colors,
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.3, 1.7)

    plt.title(f"Active Task List — [{client_name}]", fontsize=14, fontweight="bold", pad=20)
    return _fig_to_base64(fig)