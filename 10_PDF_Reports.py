
import io
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak
)

from utils.data_processing import load_dataset
from utils.style import apply_custom_style


st.set_page_config(
    page_title="PDF Weather Reports",
    page_icon="📄",
    layout="wide"
)

apply_custom_style()


st.title("📄 PDF Weather Analysis Reports")

st.write(
    "Generate a downloadable PDF report containing "
    "weather statistics, data quality information, and charts."
)

st.divider()

# Load dataset
df = load_dataset()

if df is None or df.empty:
    st.warning(
        "No dataset is available. Open Upload Dataset "
        "and load a CSV file first."
    )
    st.stop()

df = df.copy()
df.columns = df.columns.astype(str).str.strip()

# Find common weather columns
column_map = {
    col.lower().replace(" ", "_"): col
    for col in df.columns
}

temperature_col = next(
    (
        column_map[name]
        for name in ["temperature", "temp", "temperature_c"]
        if name in column_map
    ),
    None
)

humidity_col = next(
    (
        column_map[name]
        for name in ["humidity", "relative_humidity"]
        if name in column_map
    ),
    None
)

rainfall_col = next(
    (
        column_map[name]
        for name in ["rainfall", "rain", "precipitation"]
        if name in column_map
    ),
    None
)

wind_col = next(
    (
        column_map[name]
        for name in ["wind_speed", "windspeed", "wind"]
        if name in column_map
    ),
    None
)

# Convert recognized weather measurements to numeric
weather_cols = [
    col for col in [
        temperature_col,
        humidity_col,
        rainfall_col,
        wind_col
    ]
    if col is not None
]

for col in weather_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Report configuration
st.subheader("⚙️ Report Configuration")

report_title = st.text_input(
    "Report title",
    value="Weather Data Analysis Report"
)

include_data_preview = st.checkbox(
    "Include first 10 dataset records",
    value=True
)

include_chart = st.checkbox(
    "Include temperature chart when available",
    value=True
)

st.write("### Dataset Summary")

c1, c2, c3 = st.columns(3)

c1.metric("Total Records", f"{len(df):,}")
c2.metric("Total Columns", f"{len(df.columns):,}")
c3.metric(
    "Missing Values",
    f"{int(df.isna().sum().sum()):,}"
)

st.divider()


def make_pdf(data, title, include_preview, include_temperature_chart):
    """Build a PDF report in memory and return its bytes."""

    pdf_buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=20,
            leading=25,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#075985"),
            spaceAfter=16
        )
    )

    story = []

    # Title and metadata
    story.append(Paragraph(title, styles["ReportTitle"]))
    story.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
            styles["Normal"]
        )
    )
    story.append(Spacer(1, 18))

    story.append(
        Paragraph("1. Executive Summary", styles["Heading1"])
    )

    story.append(
        Paragraph(
            f"This report summarizes a weather dataset containing "
            f"{len(data)} records and {len(data.columns)} columns. "
            f"It presents available weather statistics, data quality "
            f"information, and a sample of the source records.",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 14))

    # Dataset overview table
    story.append(
        Paragraph("2. Dataset Overview", styles["Heading1"])
    )

    overview = [
        ["Metric", "Value"],
        ["Number of records", str(len(data))],
        ["Number of columns", str(len(data.columns))],
        ["Missing cells", str(int(data.isna().sum().sum()))],
        ["Duplicate rows", str(int(data.duplicated().sum()))]
    ]

    overview_table = Table(
        overview,
        colWidths=[3.0 * inch, 2.2 * inch],
        repeatRows=1
    )

    overview_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#075985")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F0F9FF")),
            ("PADDING", (0, 0), (-1, -1), 7)
        ])
    )

    story.append(overview_table)
    story.append(Spacer(1, 16))

    # Statistical summary
    story.append(
        Paragraph("3. Weather Statistics", styles["Heading1"])
    )

    stats_rows = [["Measurement", "Average", "Minimum", "Maximum"]]

    recognized = [
        ("Temperature", temperature_col),
        ("Humidity", humidity_col),
        ("Rainfall", rainfall_col),
        ("Wind Speed", wind_col)
    ]

    for label, col in recognized:
        if col is None:
            continue

        values = pd.to_numeric(
            data[col],
            errors="coerce"
        ).dropna()

        if values.empty:
            stats_rows.append([label, "N/A", "N/A", "N/A"])
        else:
            stats_rows.append([
                label,
                f"{values.mean():.2f}",
                f"{values.min():.2f}",
                f"{values.max():.2f}"
            ])

    if len(stats_rows) == 1:
        stats_rows.append([
            "No recognized weather measurements",
            "N/A",
            "N/A",
            "N/A"
        ])

    stats_table = Table(
        stats_rows,
        colWidths=[
            1.75 * inch,
            1.25 * inch,
            1.25 * inch,
            1.25 * inch
        ],
        repeatRows=1
    )

    stats_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0E7490")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("FONTSIZE", (0, 0), (-1, -1), 8)
        ])
    )

    story.append(stats_table)
    story.append(Spacer(1, 16))

    # Temperature chart
    if include_temperature_chart and temperature_col:
        chart_values = pd.to_numeric(
            data[temperature_col],
            errors="coerce"
        ).dropna()

        if not chart_values.empty:
            story.append(
                Paragraph("4. Temperature Distribution", styles["Heading1"])
            )

            chart_buffer = io.BytesIO()

            fig, ax = plt.subplots(figsize=(7, 3.5))
            ax.hist(chart_values, bins=min(15, max(5, len(chart_values))))
            ax.set_title("Temperature Distribution")
            ax.set_xlabel(temperature_col)
            ax.set_ylabel("Frequency")
            fig.tight_layout()

            fig.savefig(
                chart_buffer,
                format="png",
                dpi=140,
                bbox_inches="tight"
            )

            plt.close(fig)
            chart_buffer.seek(0)

            story.append(
                Image(
                    chart_buffer,
                    width=6.2 * inch,
                    height=3.1 * inch
                )
            )
            story.append(Spacer(1, 14))

    # Optional dataset preview
    if include_preview:
        story.append(PageBreak())
        story.append(
            Paragraph("5. Dataset Preview", styles["Heading1"])
        )

        preview = data.head(10).copy()
        preview = preview.astype(object).where(
            pd.notna(preview),
            ""
        )

        preview_rows = [
            [str(col)[:22] for col in preview.columns]
        ]

        for _, row in preview.iterrows():
            preview_rows.append([
                str(value)[:25]
                for value in row.tolist()
            ])

        available_width = A4[0] - 80
        col_width = available_width / max(1, len(preview.columns))

        preview_table = Table(
            preview_rows,
            colWidths=[col_width] * len(preview.columns),
            repeatRows=1
        )

        preview_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#075985")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 4)
            ])
        )

        story.append(preview_table)

    # Footer on each page
    def add_footer(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(
            40,
            25,
            "Weather Data Analysis System"
        )
        canvas.drawRightString(
            A4[0] - 40,
            25,
            f"Page {document.page}"
        )
        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=add_footer,
        onLaterPages=add_footer
    )

    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()


# Generate report
if st.button("📄 Generate PDF Report", type="primary"):
    try:
        pdf_bytes = make_pdf(
            df,
            report_title,
            include_data_preview,
            include_chart
        )

        st.session_state["weather_pdf_report"] = pdf_bytes
        st.success("PDF report generated successfully!")

    except Exception as error:
        st.error(f"Could not generate the PDF report: {error}")


# Download generated report
if "weather_pdf_report" in st.session_state:
    st.download_button(
        label="⬇️ Download PDF Report",
        data=st.session_state["weather_pdf_report"],
        file_name="weather_analysis_report.pdf",
        mime="application/pdf"
    )
