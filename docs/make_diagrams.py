# makes the two diagrams used in the P3 report
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def box(ax, x, y, w, h, text, color, fs=8.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=color, ec="#33443f", lw=1.1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, linespacing=1.25)


def arrow(ax, x1, y1, x2, y2, label=None, dy=0.12, ha="center"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color="#33443f", lw=1.2))
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + dy, label, fontsize=7, ha=ha, color="#444", style="italic")


# ---------- Figure 1: architecture ----------
fig, ax = plt.subplots(figsize=(10, 5.6))
ax.set_xlim(0, 10); ax.set_ylim(-0.3, 5.6); ax.axis("off")
ax.text(5, 5.4, "Figure 1. HealthAssist system architecture (everything runs on the user's computer)", ha="center", fontsize=10, weight="bold")
ax.add_patch(FancyBboxPatch((0.15, 0.2), 9.7, 4.95, boxstyle="round,pad=0.02,rounding_size=0.1", fc="none", ec="#1d6b5c", lw=1.4, ls="--"))
ax.text(9.75, 4.95, "Local machine", ha="right", fontsize=8, color="#1d6b5c")

box(ax, 0.4, 3.3, 2.1, 1.3, "React front end\nconsent - profile form\nchat - sources - history\ndelete my data", "#cfe8e1")
box(ax, 3.4, 3.3, 3.0, 1.3, "FastAPI back end\n(API routes + pipeline)\nconsent check - input validation", "#fde9c2")
box(ax, 7.3, 3.5, 2.3, 0.9, "Safety filter\n(emergency / diagnosis /\nmedication -> redirect)", "#f6d0d0", 8)
box(ax, 3.4, 1.7, 3.0, 1.0, "Guideline rules (Python)\nsleep - activity - sitting\n(no AI maths)", "#e3dcf5")
box(ax, 7.3, 1.7, 2.3, 1.0, "Retrieval (ChromaDB)\nonly passages above\nrelevance threshold", "#dbe8f7")
box(ax, 7.3, 0.4, 2.3, 0.95, "Knowledge base\nHealth Canada, PHAC, CSEP,\nWHO + source URLs", "#dbe8f7", 8)
box(ax, 3.4, 0.4, 3.0, 0.95, "Ollama local LLM\nLlama 3.1 8B / Gemma 2 9B\n(wording only)", "#fde9c2")
box(ax, 0.4, 1.0, 2.1, 1.7, "SQLite database\nfield-level encryption\nconsent - profile -\nhistory - feedback", "#e8e8e8")

arrow(ax, 2.5, 4.0, 3.4, 4.0, "HTTP/JSON", 0.1)
arrow(ax, 6.4, 4.0, 7.3, 4.0, "1. question")
arrow(ax, 4.9, 3.3, 4.9, 2.7, "2. profile", 0.0, "left")
arrow(ax, 6.4, 3.4, 7.3, 2.5, "3. query", 0.12)
arrow(ax, 8.45, 1.7, 8.45, 1.35, None)
arrow(ax, 7.3, 1.2, 6.4, 1.0, "4. passages", 0.12)
arrow(ax, 4.9, 1.7, 4.9, 1.35, None)
arrow(ax, 3.4, 3.5, 2.5, 2.6, "store / load\n(encrypted)", 0.15)
ax.text(5.0, -0.12, "5. answer + citation check -> back to the interface", ha="center", fontsize=7.5, style="italic", color="#444")
fig.savefig("docs/architecture.png", dpi=200, bbox_inches="tight")

# ---------- Figure 2: question workflow ----------
fig, ax = plt.subplots(figsize=(10, 3.4))
ax.set_xlim(0, 10); ax.set_ylim(0, 3.4); ax.axis("off")
ax.text(5, 3.2, "Figure 2. Question-answering workflow with refusal paths", ha="center", fontsize=10, weight="bold")
box(ax, 0.1, 1.5, 1.1, 0.9, "User\nquestion", "#cfe8e1")
box(ax, 1.6, 1.5, 1.3, 0.9, "Safety\ncheck", "#f6d0d0")
box(ax, 3.3, 1.5, 1.4, 0.9, "Retrieve\npassages", "#dbe8f7")
box(ax, 5.1, 1.5, 1.4, 0.9, "LLM writes\nshort answer\nwith [S1] tags", "#fde9c2", 8)
box(ax, 6.9, 1.5, 1.4, 0.9, "Citation\ncheck", "#e3dcf5")
box(ax, 8.7, 1.5, 1.2, 0.9, "Show answer\n+ sources", "#cfe8e1", 8)
box(ax, 1.4, 0.15, 1.7, 0.75, "Redirect calmly\n(9-1-1, 8-1-1, 9-8-8)", "#f6d0d0", 7.5)
box(ax, 3.35, 0.15, 1.3, 0.75, "Decline:\nnot enough\nsupport", "#f4e3b8", 7.5)
box(ax, 6.9, 0.15, 1.4, 0.75, "Decline:\ninvalid /\nmissing citation", "#f4e3b8", 7.5)
for a, b in [(1.2, 1.6), (2.9, 3.3), (4.7, 5.1), (6.5, 6.9), (8.3, 8.7)]:
    arrow(ax, a, 1.95, b, 1.95)
arrow(ax, 2.25, 1.5, 2.25, 0.9, "unsafe", 0.0, "left")
arrow(ax, 4.0, 1.5, 4.0, 0.9, "too far / none", 0.0, "left")
arrow(ax, 7.6, 1.5, 7.6, 0.9, "fails", 0.0, "left")
ax.text(5.8, 2.6, "profile -> Python rules -> habit notes (sent to the model instead of the raw profile)", fontsize=7.5, ha="center", style="italic", color="#444")
fig.savefig("docs/workflow.png", dpi=200, bbox_inches="tight")
