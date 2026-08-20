import contextlib
import hashlib
import html
import io
import re
from datetime import datetime

import streamlit as st

from pipeline import run_pipeline

# --------------------------------------------------------------------------
# Page setup
# --------------------------------------------------------------------------

st.set_page_config(
    page_title="SIGNAL — Research Wire",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

STAGES = [
    ("01", "SEARCH", "Recon Agent"),
    ("02", "READ", "Verification Agent"),
    ("03", "WRITE", "Draft Chain"),
    ("04", "CRITIQUE", "Review Chain"),
]

STAGE_TRIGGERS = [
    "Search agent is working",
    "Reader Agent is working",
    "Writer chain is working",
    "Critic chain is working",
]

# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
  --ink: #0E1116;
  --ink-2: #161A22;
  --line: #2C3140;
  --paper: #EDE6D6;
  --paper-2: #E3D9C2;
  --text-light: #E7E2D3;
  --text-dim: #8B91A3;
  --text-dark: #211D14;
  --amber: #E3963E;
  --teal: #4FD1C5;
  --red: #C1443D;
}

#MainMenu, footer { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }

.stApp {
  background: radial-gradient(ellipse at top, #141821 0%, var(--ink) 55%);
  color: var(--text-light);
}

section.main > div.block-container {
  max-width: 980px;
  padding-top: 2.2rem;
  padding-bottom: 4rem;
}

* { font-family: 'Source Serif 4', serif; }

/* ---------- masthead ---------- */
.eyebrow {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--amber);
  margin-bottom: 0.5rem;
}
.masthead-title {
  font-family: 'Fraunces', serif;
  font-weight: 700;
  font-size: 3.4rem;
  line-height: 1;
  color: var(--text-light);
  margin: 0 0 0.7rem 0;
  letter-spacing: -0.01em;
}
.masthead-title span { color: var(--amber); }
.masthead-sub {
  color: var(--text-dim);
  font-size: 1.02rem;
  max-width: 640px;
  line-height: 1.55;
  margin-bottom: 2.2rem;
}
.masthead-rule {
  border: none;
  border-top: 1px solid var(--line);
  margin: 0 0 2.2rem 0;
}

/* ---------- input row ---------- */
.dispatch-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-bottom: 0.4rem;
}
div[data-testid="stTextInput"] input {
  background: var(--ink-2) !important;
  border: 1px solid var(--line) !important;
  color: var(--text-light) !important;
  border-radius: 3px !important;
  font-family: 'IBM Plex Mono', monospace !important;
  padding: 0.75rem 0.9rem !important;
}
div[data-testid="stTextInput"] input:focus {
  border-color: var(--amber) !important;
  box-shadow: 0 0 0 1px var(--amber) !important;
}
div[data-testid="stTextInput"] input::placeholder { color: #5b6172 !important; }

.stButton > button {
  background: transparent !important;
  border: 1px solid var(--amber) !important;
  color: var(--amber) !important;
  font-family: 'IBM Plex Mono', monospace !important;
  letter-spacing: 0.1em !important;
  font-size: 0.8rem !important;
  border-radius: 3px !important;
  padding: 0.62rem 1.3rem !important;
  transition: all .18s ease !important;
}
.stButton > button:hover {
  background: var(--amber) !important;
  color: var(--ink) !important;
}
.stButton > button:focus-visible {
  outline: 2px solid var(--teal) !important;
  outline-offset: 2px !important;
}

/* ---------- pipeline track ---------- */
.pipeline-track {
  position: relative;
  display: flex;
  justify-content: space-between;
  margin: 2.6rem 0 2rem 0;
  padding: 0 1rem;
}
.pipeline-track::before {
  content: "";
  position: absolute;
  top: 23px;
  left: 8%;
  right: 8%;
  height: 1px;
  background: var(--line);
  z-index: 0;
}
.track-node {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 24%;
  text-align: center;
}
.track-dot {
  width: 46px; height: 46px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: 'IBM Plex Mono', monospace;
  font-weight: 600; font-size: 0.85rem;
  border: 2px solid var(--line);
  background: var(--ink-2);
  color: var(--text-dim);
  transition: all .35s ease;
}
.track-node.active .track-dot {
  border-color: var(--amber);
  color: var(--amber);
  box-shadow: 0 0 0 rgba(227,150,62,.5);
  animation: pulse 1.5s infinite;
}
.track-node.done .track-dot {
  border-color: var(--teal);
  background: var(--teal);
  color: var(--ink);
}
@keyframes pulse {
  0%   { box-shadow: 0 0 4px rgba(227,150,62,.35); }
  50%  { box-shadow: 0 0 16px rgba(227,150,62,.8); }
  100% { box-shadow: 0 0 4px rgba(227,150,62,.35); }
}
.track-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.68rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-top: 0.55rem;
  color: var(--text-light);
}
.track-node.pending .track-label { color: var(--text-dim); }
.track-sub {
  font-size: 0.68rem;
  color: var(--text-dim);
  margin-top: 1px;
}

/* ---------- console ---------- */
.console-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.7rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin: 0.4rem 0 0.5rem 0;
  display: flex; align-items: center; gap: 0.5rem;
}
.console-label .dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--amber);
  box-shadow: 0 0 8px var(--amber);
}
.console-box {
  background: #07090C;
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 1rem 1.2rem;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.76rem;
  line-height: 1.6;
  color: var(--amber);
  max-height: 320px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

/* ---------- appendix (raw findings) ---------- */
.appendix-box {
  background: var(--ink-2);
  border: 1px solid var(--line);
  border-left: 3px solid var(--text-dim);
  border-radius: 4px;
  padding: 1.1rem 1.3rem;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.8rem;
  line-height: 1.65;
  color: var(--text-light);
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 420px;
  overflow-y: auto;
}
div[data-testid="stExpander"] {
  background: transparent;
  border: 1px solid var(--line);
  border-radius: 4px;
}
div[data-testid="stExpander"] summary {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  color: var(--text-light);
}

/* ---------- dossier paper ---------- */
.dossier-wrap { margin-top: 2.6rem; }
.dossier-paper {
  background: var(--paper);
  color: var(--text-dark);
  border-radius: 2px;
  padding: 2.6rem 3rem 2.8rem 3rem;
  box-shadow: 0 18px 50px rgba(0,0,0,.5);
  position: relative;
}
.dossier-topline {
  display: flex; justify-content: space-between; align-items: flex-start;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.68rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #6b6350;
  border-bottom: 1px solid var(--paper-2);
  padding-bottom: 0.9rem;
  margin-bottom: 1.4rem;
}
.dossier-stamp {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.68rem;
  letter-spacing: 0.14em;
  color: var(--red);
  border: 1.5px solid var(--red);
  padding: 0.15rem 0.55rem;
  border-radius: 2px;
  transform: rotate(-3deg);
  display: inline-block;
}
.dossier-title {
  font-family: 'Fraunces', serif;
  font-weight: 700;
  font-size: 2.1rem;
  line-height: 1.15;
  margin: 0 0 1.6rem 0;
  color: var(--text-dark);
}
.dossier-body { font-size: 1.02rem; line-height: 1.75; color: #2b2618; }
.dossier-body p { margin: 0 0 1rem 0; }
.dossier-body h3 { font-family: 'Fraunces', serif; font-size: 1.25rem; margin: 1.4rem 0 0.6rem 0; }
.dossier-body h4 { font-family: 'Fraunces', serif; font-size: 1.08rem; margin: 1.2rem 0 0.5rem 0; }
.dossier-body ul { margin: 0 0 1rem 1.2rem; padding: 0; }
.dossier-body li { margin-bottom: 0.4rem; }

.memo {
  margin-top: 1.6rem;
  background: #FBEEE9;
  border-left: 4px solid var(--red);
  padding: 1.1rem 1.4rem;
  border-radius: 2px;
}
.memo-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.68rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--red);
  margin-bottom: 0.5rem;
}
.memo-body { color: #3a2420; font-size: 0.94rem; line-height: 1.65; }
.memo-body p { margin: 0 0 0.8rem 0; }

@media (max-width: 640px) {
  .masthead-title { font-size: 2.2rem; }
  .pipeline-track { flex-wrap: wrap; row-gap: 1.4rem; }
  .pipeline-track::before { display: none; }
  .track-node { width: 48%; }
  .dossier-paper { padding: 1.8rem 1.6rem; }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def to_text(x) -> str:
    """Coerce chain/agent output (which may be an LLM message object) to plain text."""
    if x is None:
        return ""
    if hasattr(x, "content"):
        return str(x.content)
    return str(x)


def inline_fmt(s: str) -> str:
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s


def md_to_html(text: str) -> str:
    """Very small markdown -> HTML converter, just enough for LLM-style output."""
    text = (text or "").strip()
    if not text:
        return "<p><em>No content returned.</em></p>"
    lines = text.split("\n")
    parts, para, in_list = [], [], False

    def flush_para():
        if para:
            parts.append("<p>" + " ".join(para) + "</p>")
            para.clear()

    for raw in lines:
        line = raw.strip()
        if not line:
            flush_para()
            if in_list:
                parts.append("</ul>")
                in_list = False
            continue
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            flush_para()
            if in_list:
                parts.append("</ul>")
                in_list = False
            level = min(len(m.group(1)) + 2, 4)
            parts.append(f"<h{level}>{inline_fmt(html.escape(m.group(2)))}</h{level}>")
            continue
        m2 = re.match(r"^[-*]\s+(.*)", line)
        if m2:
            flush_para()
            if not in_list:
                parts.append("<ul>")
                in_list = True
            parts.append(f"<li>{inline_fmt(html.escape(m2.group(1)))}</li>")
            continue
        if in_list:
            parts.append("</ul>")
            in_list = False
        para.append(inline_fmt(html.escape(line)))
    flush_para()
    if in_list:
        parts.append("</ul>")
    return "\n".join(parts)


def render_track(states) -> str:
    nodes = ""
    for i, (num, label, sub) in enumerate(STAGES):
        state = states[i]
        cls = "pending"
        mark = num
        if state == 1:
            cls = "active"
        elif state == 2:
            cls = "done"
            mark = "&#10003;"
        nodes += (
            f'<div class="track-node {cls}">'
            f'<div class="track-dot">{mark}</div>'
            f'<div class="track-label">{label}</div>'
            f'<div class="track-sub">{sub}</div>'
            f"</div>"
        )
    return f'<div class="pipeline-track">{nodes}</div>'


def render_console(tail_text: str) -> str:
    return f'<div class="console-box">{html.escape(tail_text)}</div>'


class WireWriter(io.TextIOBase):
    """Captures pipeline.py's stdout, mirrors it into a live console panel,
    and advances the pipeline track when it recognizes a stage header."""

    def __init__(self, console_ph, track_ph):
        self.console_ph = console_ph
        self.track_ph = track_ph
        self.lines = []
        self.states = [0, 0, 0, 0]

    def write(self, s):
        if not s:
            return 0
        self.lines.append(s)
        for idx, trigger in enumerate(STAGE_TRIGGERS):
            if trigger in s:
                for j in range(idx):
                    self.states[j] = 2
                self.states[idx] = 1
                self.track_ph.markdown(render_track(self.states), unsafe_allow_html=True)
        tail = "".join(self.lines[-500:])
        self.console_ph.markdown(render_console(tail), unsafe_allow_html=True)
        return len(s)

    def flush(self):
        pass

    def finish(self):
        self.states = [2, 2, 2, 2]
        self.track_ph.markdown(render_track(self.states), unsafe_allow_html=True)

    def full_log(self):
        return "".join(self.lines)


def dossier_id(topic: str) -> str:
    h = hashlib.sha1(topic.encode("utf-8")).hexdigest()[:6].upper()
    return f"{datetime.now().strftime('%Y%m%d')}-{h}"


# --------------------------------------------------------------------------
# Session state
# --------------------------------------------------------------------------

if "result" not in st.session_state:
    st.session_state.result = None
if "result_topic" not in st.session_state:
    st.session_state.result_topic = ""
if "log_text" not in st.session_state:
    st.session_state.log_text = ""

# --------------------------------------------------------------------------
# Masthead
# --------------------------------------------------------------------------

st.markdown('<div class="eyebrow">Automated Research Wire</div>', unsafe_allow_html=True)
st.markdown('<h1 class="masthead-title">SIGNAL<span>.</span></h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="masthead-sub">Four agents, one desk. A recon agent searches the open web, '
    "a verification agent reads and cross-checks the sources, a draft chain writes the "
    "briefing, and a review chain checks its work — all wired into a single pipeline.</div>",
    unsafe_allow_html=True,
)
st.markdown('<hr class="masthead-rule" />', unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Dispatch form
# --------------------------------------------------------------------------

st.markdown('<div class="dispatch-label">Dispatch a topic</div>', unsafe_allow_html=True)
in_col, btn_col = st.columns([5, 1], vertical_alignment="bottom")
with in_col:
    topic = st.text_input(
        "topic",
        placeholder="e.g. the economics of desalination in the Gulf states",
        label_visibility="collapsed",
        key="topic_input",
    )
with btn_col:
    go = st.button("▶ TRANSMIT", use_container_width=True)

# --------------------------------------------------------------------------
# Run pipeline
# --------------------------------------------------------------------------

if go:
    if not topic or not topic.strip():
        st.warning("Enter a topic before transmitting.")
    else:
        track_ph = st.empty()
        st.markdown('<div class="console-label"><span class="dot"></span>Live wire feed</div>', unsafe_allow_html=True)
        console_ph = st.empty()

        track_ph.markdown(render_track([0, 0, 0, 0]), unsafe_allow_html=True)
        console_ph.markdown(render_console("waiting for signal…"), unsafe_allow_html=True)

        writer = WireWriter(console_ph, track_ph)
        try:
            with contextlib.redirect_stdout(writer):
                result = run_pipeline(topic.strip())
            writer.finish()
            st.session_state.result = result
            st.session_state.result_topic = topic.strip()
            st.session_state.log_text = writer.full_log()
        except Exception as exc:
            st.error(f"Transmission failed: {exc}")
            st.exception(exc)

# --------------------------------------------------------------------------
# Dossier output
# --------------------------------------------------------------------------

if st.session_state.result:
    result = st.session_state.result
    topic_done = st.session_state.result_topic
    report_text = to_text(result.get("report"))
    feedback_text = to_text(result.get("feedback"))
    search_text = to_text(result.get("search_results"))
    reader_text = to_text(result.get("reader_results"))

    st.markdown('<div class="dossier-wrap">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="dossier-paper">
            <div class="dossier-topline">
                <span>File No. {dossier_id(topic_done)} &nbsp;·&nbsp; Compiled {datetime.now().strftime('%d %b %Y, %H:%M')}</span>
                <span class="dossier-stamp">Reviewed</span>
            </div>
            <div class="dossier-title">{html.escape(topic_done)}</div>
            <div class="dossier-body">{md_to_html(report_text)}</div>
            <div class="memo">
                <div class="memo-label">Critic&rsquo;s margin notes</div>
                <div class="memo-body">{md_to_html(feedback_text)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    dl_col, reset_col = st.columns([1, 1])
    with dl_col:
        export = f"# {topic_done}\n\n{report_text}\n\n---\n\n## Critic's Notes\n\n{feedback_text}\n"
        st.download_button(
            "⤓ Export briefing (.md)",
            data=export,
            file_name=f"signal-{dossier_id(topic_done)}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with reset_col:
        if st.button("↺ New transmission", use_container_width=True):
            st.session_state.result = None
            st.session_state.result_topic = ""
            st.session_state.log_text = ""
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Appendix A — Raw search wire"):
        st.markdown(f'<div class="appendix-box">{html.escape(search_text)}</div>', unsafe_allow_html=True)
    with st.expander("Appendix B — Field reader notes"):
        st.markdown(f'<div class="appendix-box">{html.escape(reader_text)}</div>', unsafe_allow_html=True)