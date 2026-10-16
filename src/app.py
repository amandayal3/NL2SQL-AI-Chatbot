
import io
from uuid import uuid4

import pandas as pd
import streamlit as st

from orchestration.langgraph_workflow import graph


# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="NL2SQL AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# 2. COLOR THEMES
THEMES = {
    "Light Blue": {
        "background": "#f0f8ff",
        "sidebar": "#dceeff",
        "card": "#ffffff",
        "primary": "#3b82f6",
        "text": "#000000",
        "border": "#cfe4fa",
        "soft": "#e0f2fe",
    },
    "Purple": {
        "background": "#f7f4ff",
        "sidebar": "#ebe4ff",
        "card": "#ffffff",
        "primary": "#8b5cf6",
        "text": "#000000",
        "border": "#ddd0ff",
        "soft": "#f0eaff",
    },
    "Green": {
        "background": "#f1fbf6",
        "sidebar": "#dcf5e7",
        "card": "#ffffff",
        "primary": "#16a34a",
        "text": "#000000",
        "border": "#bfe8d0",
        "soft": "#e4f8eb",
    },
    "Pink": {
        "background": "#fff5fa",
        "sidebar": "#ffe4f0",
        "card": "#ffffff",
        "primary": "#ec4899",
        "text": "#000000",
        "border": "#fbcfe8",
        "soft": "#fce7f3",
    },
    "Orange": {
        "background": "#fff9f1",
        "sidebar": "#ffedd5",
        "card": "#ffffff",
        "primary": "#f97316",
        "text": "#000000",
        "border": "#fed7aa",
        "soft": "#ffedd5",
    },
    "Dark": {
        "background": "#111827",
        "sidebar": "#1f2937",
        "card": "#253247",
        "primary": "#60a5fa",
        "text": "#f3f4f6",
        "border": "#374151",
        "soft": "#334155",
    },
}


# 3. SESSION STATE
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = "Light Blue"


# 4. SIDEBAR
with st.sidebar:

    st.markdown("### 🤖 NL2SQL AI")

    if st.button(
        "＋ New Chat",
        type="primary",
        use_container_width=True
    ):
        st.session_state.thread_id = str(uuid4())
        st.session_state.chat_history = []
        st.rerun()

    st.divider()

    with st.expander("ℹ️ About"):
        st.write("**Database:** Olist E-commerce")
        st.write("**AI Model:** GPT-OSS 120B")
        st.write("**Provider:** Groq")
        st.write("**Framework:** LangGraph")
        st.write("**Database Engine:** SQLite")

    with st.expander("✨ Features"):
        st.write("Natural Language to SQL")
        st.write("AI-Powered Answers")
        st.write("Conversation Memory")
        st.write("SQL Query Viewer")
        st.write("Automatic Charts")
        st.write("CSV and Excel Downloads")

    with st.expander("🎨 Theme"):

        selected_theme = st.selectbox(
            "Choose a color",
            list(THEMES.keys()),
            index=list(THEMES.keys()).index(
                st.session_state.selected_theme
            )
        )

        st.session_state.selected_theme = selected_theme


# 5. APPLY SELECTED THEME
theme = THEMES[st.session_state.selected_theme]

dark_mode = (
    st.session_state.selected_theme == "Dark"
)

input_background = (
    "#253247" if dark_mode else "#ffffff"
)

input_text = (
    "#f3f4f6" if dark_mode else "#000000"
)

st.markdown(
    f"""
    <style>

    /* Main background */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {{
        background-color: {theme["background"]} !important;
        color: {theme["text"]};
    }}

    /* Top toolbar */
    [data-testid="stHeader"] {{
        background-color: {theme["background"]} !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"] {{
        background-color: {theme["sidebar"]} !important;
    }}

    /* Bottom chat area */
    [data-testid="stBottom"],
    [data-testid="stBottomBlockContainer"] {{
        background-color: {theme["background"]} !important;
    }}

    /* Chat input */
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div {{
        background-color: {input_background} !important;
        border-radius: 14px !important;
        border-color: {theme["border"]} !important;
    }}

    [data-testid="stChatInput"] textarea {{
        background-color: transparent !important;
        color: {input_text} !important;
    }}

    [data-testid="stChatInput"] textarea::placeholder {{
        color: #94a3b8 !important;
    }}

    /* Headings */
    h1, h2, h3 {{
        color: {theme["text"]} !important;
    }}

    /* Chat messages */
    [data-testid="stChatMessage"] {{
        background-color: {theme["card"]} !important;
        border: 1px solid {theme["border"]};
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
    }}

    [data-testid="stChatMessage"] p {{
        color: {theme["text"]} !important;
    }}

    /* Expanders */
    [data-testid="stExpander"] {{
        background-color: {theme["card"]};
        border: 1px solid {theme["border"]};
        border-radius: 10px;
    }}

    /* Buttons */
    .stButton > button[kind="primary"] {{
        background-color: {theme["primary"]} !important;
        color: white !important;
        border: none;
        border-radius: 10px;
    }}

    .stButton > button {{
        border-radius: 10px;
    }}

    /* Metric cards */
    [data-testid="stMetric"] {{
        background-color: {theme["soft"]};
        padding: 15px;
        border-radius: 12px;
    }}

    /* Main layout */
    .block-container {{
        max-width: 1050px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }}

    footer {{
        visibility: hidden;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# 6. MAIN PAGE
st.title("NL2SQL AI")

st.caption(
    "Ask questions about your e-commerce data."
)


# 7. CONVERT SQL RESULTS TO DATAFRAME
def get_dataframe(result):

    rows = result.get("rows") or []
    columns = result.get("columns") or []

    if not rows:
        return pd.DataFrame(columns=columns)

    return pd.DataFrame(
        rows,
        columns=columns
    )


# 8. AUTOMATIC CHART
def show_chart(df):

    if df.empty:
        return

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    # Single numeric value
    if len(df) == 1 and len(df.columns) == 1:

        value = df.iloc[0, 0]

        if pd.api.types.is_numeric_dtype(
            df.iloc[:, 0]
        ):

            if isinstance(value, (float, int)):
                display_value = f"{value:,.2f}" if isinstance(
                    value, float
                ) else f"{value:,}"
            else:
                display_value = str(value)

            st.metric(
                label=str(
                    df.columns[0]
                ).replace("_", " ").title(),
                value=display_value
            )

        else:
            st.info(
                "No suitable chart for this result."
            )

        return

    # Remove numeric ID columns
    numeric_columns = [
        col for col in numeric_columns
        if not str(col).lower().endswith("_id")
    ]

    category_columns = [
        col for col in df.columns
        if col not in numeric_columns
    ]

    if not numeric_columns or not category_columns:

        st.info(
            "No suitable chart for these results."
        )
        return

    x_column = category_columns[0]
    y_column = numeric_columns[0]

    chart_df = df[
        [x_column, y_column]
    ].head(30).copy()

    if chart_df[x_column].isna().all():

        st.info(
            "No suitable chart labels were found."
        )
        return

    time_keywords = [
        "month",
        "year",
        "date",
        "day",
        "time"
    ]

    is_time_series = any(
        word in str(x_column).lower()
        for word in time_keywords
    )

    try:

        if is_time_series:

            chart_df = chart_df.sort_values(
                x_column
            )

            st.line_chart(
                chart_df,
                x=x_column,
                y=y_column,
                color=theme["primary"],
                use_container_width=True
            )

        else:

            st.bar_chart(
                chart_df,
                x=x_column,
                y=y_column,
                color=theme["primary"],
                use_container_width=True
            )

    except Exception as error:

        st.info(
            "Unable to display this chart."
        )

        st.caption(str(error))


# 9. DOWNLOAD CSV AND EXCEL
def show_downloads(df, message_id):

    if df.empty:
        return

    csv_data = df.to_csv(
        index=False
    ).encode("utf-8-sig")

    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Results"
        )

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            "📄 CSV",
            data=csv_data,
            file_name="query_results.csv",
            mime="text/csv",
            key=f"csv_{message_id}",
            use_container_width=True
        )

    with col2:

        st.download_button(
            "📊 Excel",
            data=excel_buffer.getvalue(),
            file_name="query_results.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            key=f"excel_{message_id}",
            use_container_width=True
        )


# 10. DISPLAY ASSISTANT RESPONSE
def display_assistant_message(message, message_id):

    # AI answer
    st.markdown(message["content"])

    # NEW FEATURE: SHOW GENERATED SQL QUERY
    sql_query = message.get(
        "sql_query",
        ""
    )

    if sql_query:

        with st.expander("💻 View SQL Query"):

            st.code(
                sql_query,
                language="sql"
            )

    # Results DataFrame
    df = message.get("dataframe")

    if not isinstance(df, pd.DataFrame):
        return

    if df.empty:
        return

    # Show results table
    with st.expander("📋 View Results"):

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    # Chart and download buttons
    col1, col2 = st.columns(2)

    with col1:

        with st.popover(
            "📊 Chart",
            use_container_width=True
        ):

            show_chart(df)

    with col2:

        with st.popover(
            "⬇️ Download",
            use_container_width=True
        ):

            show_downloads(
                df,
                message_id
            )


# 11. DISPLAY PREVIOUS CHAT MESSAGES
for index, message in enumerate(
    st.session_state.chat_history
):

    with st.chat_message(
        message["role"]
    ):

        if message["role"] == "assistant":

            display_assistant_message(
                message,
                index
            )

        else:

            st.markdown(
                message["content"]
            )


# 12. USER INPUT
question = st.chat_input(
    "Ask a question about your data..."
)

if question:

    # Save user question
    st.session_state.chat_history.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):

        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner(
            "Analyzing your question..."
        ):

            try:

                config = {
                    "configurable": {
                        "thread_id": (
                            st.session_state.thread_id
                        )
                    }
                }

                # Execute LangGraph workflow
                result = graph.invoke(
                    {
                        "question": question,
                        "intent": "",
                        "answer": "",
                        "resolved_question": "",
                        "sql_query": "",
                        "rows": [],
                        "columns": []
                    },
                    config=config
                )

                # Get AI answer
                answer = result.get(
                    "answer",
                    "No answer generated."
                )

                # NEW: Get generated SQL query
                sql_query = result.get(
                    "sql_query",
                    ""
                )

                # Get database results
                df = get_dataframe(result)

            except Exception as error:

                answer = (
                    "Sorry, something went wrong."
                )

                sql_query = ""
                df = pd.DataFrame()

                st.error(str(error))

        # Save assistant response
        assistant_message = {
            "role": "assistant",
            "content": answer,
            "sql_query": sql_query,
            "dataframe": df
        }

        display_assistant_message(
            assistant_message,
            len(st.session_state.chat_history)
        )

    st.session_state.chat_history.append(
        assistant_message
    )
