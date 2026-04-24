"""Build the PowerPoint and Keynote variants of the thesis presentation.

Emits two `.pptx` files from a single slide-content specification:
  - thesis_prezi_powerpoint.pptx  (Calibri, survives PowerPoint render natively)
  - thesis_prezi_keynote.pptx     (Helvetica Neue, survives Keynote import natively)

Both files share the same Keynote-native aesthetic: off-white (#FAFAFA)
background, navy slate text, blue/red accents, minimal chrome.

Usage:
    python presentations/build_decks.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

BG_COLOR = RGBColor(0xFA, 0xFA, 0xFA)
TEXT_COLOR = RGBColor(0x2D, 0x37, 0x48)       # DarkSteel navy
ACCENT_BLUE = RGBColor(0x31, 0x82, 0xCE)
ACCENT_RED = RGBColor(0xC5, 0x30, 0x30)
MUTED_GREY = RGBColor(0xA0, 0xAE, 0xC0)
LIGHT_SHADE = RGBColor(0xED, 0xF2, 0xF7)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

# Layout geometry
TITLE_BAR_H = Inches(0.9)
BODY_LEFT = Inches(0.6)
BODY_TOP = Inches(1.2)
BODY_W = Inches(12.1)
BODY_H = Inches(5.9)

FIGURES_DIR = Path(__file__).parent.parent / "results" / "figures"

# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------


def set_background(slide, color: RGBColor) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_text(
    slide,
    text: str,
    left,
    top,
    width,
    height,
    *,
    font: str,
    size: int = 14,
    bold: bool = False,
    italic: bool = False,
    color: RGBColor = TEXT_COLOR,
    align: PP_ALIGN = PP_ALIGN.LEFT,
    anchor: MSO_ANCHOR = MSO_ANCHOR.TOP,
):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return tb


def add_bullets(
    slide,
    items: list,
    left,
    top,
    width,
    height,
    *,
    font: str,
    size: int = 16,
    color: RGBColor = TEXT_COLOR,
    spacing: float = 1.25,
):
    """Render a bulleted list. Each item is str or (prefix_bold, rest)."""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    for idx, item in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.level = 0
        p.line_spacing = spacing
        run_bullet = p.add_run()
        run_bullet.text = "\u2022  "
        run_bullet.font.name = font
        run_bullet.font.size = Pt(size)
        run_bullet.font.color.rgb = ACCENT_BLUE
        if isinstance(item, tuple):
            head, tail = item
            rb = p.add_run()
            rb.text = head
            rb.font.name = font
            rb.font.size = Pt(size)
            rb.font.bold = True
            rb.font.color.rgb = color
            rt = p.add_run()
            rt.text = tail
            rt.font.name = font
            rt.font.size = Pt(size)
            rt.font.color.rgb = color
        else:
            rt = p.add_run()
            rt.text = item
            rt.font.name = font
            rt.font.size = Pt(size)
            rt.font.color.rgb = color
    return tb


def add_title_bar(slide, title: str, font: str) -> None:
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, TITLE_BAR_H)
    bar.fill.solid()
    bar.fill.fore_color.rgb = TEXT_COLOR
    bar.line.fill.background()
    add_text(
        slide,
        title,
        Inches(0.5),
        Inches(0.18),
        Inches(12.3),
        Inches(0.55),
        font=font,
        size=24,
        bold=True,
        color=RGBColor(0xFF, 0xFF, 0xFF),
        anchor=MSO_ANCHOR.MIDDLE,
    )


def add_card(slide, left, top, width, height, fill: RGBColor = LIGHT_SHADE):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def add_footer(slide, font: str, text: str = "Tuboly \u00b7 Knowledge Wall \u00b7 TDK 2026") -> None:
    add_text(
        slide,
        text,
        Inches(0.5),
        Inches(7.1),
        Inches(8),
        Inches(0.3),
        font=font,
        size=10,
        color=MUTED_GREY,
    )


# ---------------------------------------------------------------------------
# Slide builders
# ---------------------------------------------------------------------------


def slide_title(prs, font: str, subtitle_font_size: int = 18) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    # huge accent bar on the left
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.25), SLIDE_H)
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT_RED
    bar.line.fill.background()
    add_text(
        slide,
        "Do LLMs Shape the Diffusion of New Software?",
        Inches(0.9),
        Inches(2.0),
        Inches(12.0),
        Inches(1.6),
        font=font,
        size=40,
        bold=True,
        color=TEXT_COLOR,
    )
    add_text(
        slide,
        "Training cutoffs and adoption dynamics in the Python ecosystem.",
        Inches(0.9),
        Inches(3.6),
        Inches(12.0),
        Inches(0.8),
        font=font,
        size=subtitle_font_size + 4,
        color=MUTED_GREY,
    )
    add_text(
        slide,
        "Roland Tuboly  \u00b7  MSc Social Data Science",
        Inches(0.9),
        Inches(5.9),
        Inches(10),
        Inches(0.4),
        font=font,
        size=16,
        bold=True,
        color=TEXT_COLOR,
    )
    add_text(
        slide,
        "TDK Presentation  \u00b7  May 2026",
        Inches(0.9),
        Inches(6.35),
        Inches(10),
        Inches(0.4),
        font=font,
        size=14,
        color=MUTED_GREY,
    )


def slide_motivation(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "Why software diffusion, and why now?", font)

    # Left column
    add_card(slide, Inches(0.6), Inches(1.3), Inches(7.2), Inches(2.2))
    add_text(
        slide,
        "The measurable object",
        Inches(0.85),
        Inches(1.45),
        Inches(6.8),
        Inches(0.4),
        font=font,
        size=16,
        bold=True,
        color=TEXT_COLOR,
    )
    add_text(
        slide,
        "Software libraries are a clean unit of technological diffusion: "
        "released on a specific date, downloaded at a measurable rate, "
        "used in public code.",
        Inches(0.85),
        Inches(1.9),
        Inches(6.8),
        Inches(1.4),
        font=font,
        size=14,
        color=TEXT_COLOR,
    )

    add_card(slide, Inches(0.6), Inches(3.7), Inches(7.2), Inches(3.3))
    add_text(
        slide,
        "Why it matters",
        Inches(0.85),
        Inches(3.85),
        Inches(6.8),
        Inches(0.4),
        font=font,
        size=16,
        bold=True,
        color=TEXT_COLOR,
    )
    add_bullets(
        slide,
        [
            ("Productivity vs. variety", " \u2014 Doshi & Hauser (2024): individual gains can narrow collective variety."),
            ("Knowledge frontier", " \u2014 Acemoglu (2024); Evans; Daniotti et al. on scientific search."),
            ("Gatekeeping", " \u2014 Wachs on platforms steering adoption."),
        ],
        Inches(0.85),
        Inches(4.3),
        Inches(6.8),
        Inches(2.5),
        font=font,
        size=14,
    )

    # Right column: research question
    add_card(slide, Inches(8.1), Inches(1.3), Inches(4.7), Inches(5.7), fill=RGBColor(0xFE, 0xE2, 0xE2))
    add_text(
        slide,
        "Research question",
        Inches(8.35),
        Inches(1.55),
        Inches(4.3),
        Inches(0.5),
        font=font,
        size=18,
        bold=True,
        color=ACCENT_RED,
    )
    add_text(
        slide,
        "Do Python libraries released after an LLM's training cutoff diffuse "
        "more slowly than otherwise-identical libraries released before the cutoff?",
        Inches(8.35),
        Inches(2.2),
        Inches(4.3),
        Inches(4.5),
        font=font,
        size=18,
        italic=True,
        color=TEXT_COLOR,
    )

    add_footer(slide, font)


def slide_method(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "Method at a glance", font)

    # Option A
    add_card(slide, Inches(0.6), Inches(1.3), Inches(6.0), Inches(5.4))
    add_text(
        slide, "Option A \u2014 Single-year RDD",
        Inches(0.85), Inches(1.5), Inches(5.6), Inches(0.5),
        font=font, size=18, bold=True, color=TEXT_COLOR,
    )
    add_text(
        slide,
        "Compare libraries released just before vs. just after Sept 2021, within a narrow bandwidth.",
        Inches(0.85), Inches(2.1), Inches(5.6), Inches(1.5),
        font=font, size=14, color=TEXT_COLOR,
    )
    add_text(
        slide,
        "Problem:  the jump we see is a mix of the LLM effect and raw calendar seasonality "
        "(September releases differ from August releases every year).",
        Inches(0.85), Inches(4.0), Inches(5.6), Inches(2.4),
        font=font, size=14, color=ACCENT_RED, bold=False,
    )

    # Option B (primary)
    add_card(slide, Inches(6.9), Inches(1.3), Inches(6.0), Inches(5.4), fill=RGBColor(0xDB, 0xEA, 0xFE))
    add_text(
        slide, "Option B \u2014 Diff-in-RDD (primary)",
        Inches(7.15), Inches(1.5), Inches(5.6), Inches(0.5),
        font=font, size=18, bold=True, color=ACCENT_BLUE,
    )
    add_text(
        slide,
        "Stack 2018\u20132020 placebo cohorts at the same calendar position. "
        "Subtract the placebo jump from the 2021 jump.",
        Inches(7.15), Inches(2.1), Inches(5.6), Inches(1.8),
        font=font, size=14, color=TEXT_COLOR,
    )
    add_text(
        slide,
        "Payoff:  seasonality is differenced out; the residual is the LLM-specific treatment effect.",
        Inches(7.15), Inches(4.0), Inches(5.6), Inches(2.4),
        font=font, size=14, color=ACCENT_BLUE, bold=True,
    )

    add_text(
        slide, "Both estimators are reported. The Diff-in-RDD is the primary specification.",
        Inches(0.6), Inches(6.85), Inches(12.1), Inches(0.3),
        font=font, size=12, italic=True, color=MUTED_GREY, align=PP_ALIGN.CENTER,
    )


def slide_data(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "Data and unit of analysis", font)

    # Left column: sources + panel
    add_card(slide, Inches(0.6), Inches(1.3), Inches(7.0), Inches(2.7))
    add_text(slide, "Sources", Inches(0.85), Inches(1.5), Inches(6.6), Inches(0.4),
             font=font, size=16, bold=True, color=TEXT_COLOR)
    add_bullets(
        slide,
        [
            ("PyPI:", " weekly downloads for every registered package."),
            ("GitHub:", " code-import counts (linked sample)."),
        ],
        Inches(0.85), Inches(2.0), Inches(6.6), Inches(2.0),
        font=font, size=14,
    )

    add_card(slide, Inches(0.6), Inches(4.2), Inches(7.0), Inches(2.7))
    add_text(slide, "Panel", Inches(0.85), Inches(4.4), Inches(6.6), Inches(0.4),
             font=font, size=16, bold=True, color=TEXT_COLOR)
    add_text(
        slide,
        "Library-week, from first release through January 2026.",
        Inches(0.85), Inches(4.95), Inches(6.6), Inches(1.5),
        font=font, size=14, color=TEXT_COLOR,
    )

    # Right column: scale numbers
    add_card(slide, Inches(7.9), Inches(1.3), Inches(4.9), Inches(5.6), fill=RGBColor(0xDB, 0xEA, 0xFE))
    add_text(slide, "Scale", Inches(8.15), Inches(1.5), Inches(4.5), Inches(0.4),
             font=font, size=16, bold=True, color=ACCENT_BLUE)
    big_stats = [
        ("527,361", "PyPI packages"),
        ("28,243",  "linked to GitHub"),
        ("88,001",  "Diff-in-RDD (Broad tier)"),
        ("Sept '21", "training-data cutoff"),
    ]
    y = 2.0
    for number, label in big_stats:
        add_text(slide, number, Inches(8.15), Inches(y), Inches(4.5), Inches(0.7),
                 font=font, size=32, bold=True, color=ACCENT_BLUE)
        add_text(slide, label, Inches(8.15), Inches(y + 0.72), Inches(4.5), Inches(0.4),
                 font=font, size=13, color=TEXT_COLOR)
        y += 1.25

    add_footer(slide, font)


def slide_timeline(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "Design timeline", font)

    axis_top = Inches(3.7)
    axis_left = Inches(1.0)
    axis_right = Inches(12.3)

    # main axis line
    line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, axis_left, axis_top, axis_right, axis_top)
    line.line.width = Pt(2.5)
    line.line.color.rgb = TEXT_COLOR

    # helper: position along axis given 0..1 fraction
    def x_at(frac: float):
        return Emu(int(axis_left + (axis_right - axis_left) * frac))

    # placebo band
    pb_left = x_at(0.02)
    pb_right = x_at(0.48)
    band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, pb_left, Inches(3.05), pb_right - pb_left, Inches(0.55))
    band.fill.solid()
    band.fill.fore_color.rgb = RGBColor(0xDB, 0xEA, 0xFE)
    band.line.fill.background()
    add_text(slide, "2018\u20132020 placebo cohorts",
             pb_left, Inches(3.17), pb_right - pb_left, Inches(0.35),
             font=font, size=11, color=ACCENT_BLUE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # post-AI band
    pa_left = x_at(0.70)
    pa_right = x_at(1.0)
    pa = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, pa_left, Inches(3.05), pa_right - pa_left, Inches(0.55))
    pa.fill.solid()
    pa.fill.fore_color.rgb = RGBColor(0xDB, 0xEA, 0xFE)
    pa.line.fill.background()
    add_text(slide, "Post-AI observation window",
             pa_left, Inches(3.17), pa_right - pa_left, Inches(0.35),
             font=font, size=11, color=ACCENT_BLUE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # donut
    donut_left = x_at(0.52)
    donut_right = x_at(0.58)
    donut = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, donut_left, Inches(2.9), donut_right - donut_left, Inches(0.8))
    donut.fill.solid()
    donut.fill.fore_color.rgb = RGBColor(0xFE, 0xE2, 0xE2)
    donut.line.fill.background()
    add_text(slide, "9-week\ndonut",
             Emu(int(donut_left - Inches(0.2))), Inches(2.1),
             Inches(1.1), Inches(0.7),
             font=font, size=10, bold=True, color=ACCENT_RED, align=PP_ALIGN.CENTER)

    # cutoff marker
    cut_x = x_at(0.55)
    cutoff = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, cut_x, Inches(2.1), cut_x, Inches(4.4))
    cutoff.line.width = Pt(3)
    cutoff.line.color.rgb = ACCENT_RED
    add_text(slide, "Sept 2021 cutoff",
             Emu(int(cut_x - Inches(1.1))), Inches(1.65),
             Inches(2.2), Inches(0.4),
             font=font, size=13, bold=True, color=ACCENT_RED, align=PP_ALIGN.CENTER)

    # chatgpt marker (dashed)
    gpt_x = x_at(0.70)
    chat = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, gpt_x, Inches(2.1), gpt_x, Inches(4.4))
    chat.line.width = Pt(2.5)
    chat.line.color.rgb = ACCENT_BLUE
    chat.line.dash_style = 7  # dash
    add_text(slide, "ChatGPT release\nNov 2022",
             Emu(int(gpt_x - Inches(1.2))), Inches(1.5),
             Inches(2.4), Inches(0.6),
             font=font, size=13, bold=True, color=ACCENT_BLUE, align=PP_ALIGN.CENTER)

    # latency brace (drawn as line + label beneath)
    brace = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, cut_x, Inches(4.6), gpt_x, Inches(4.6))
    brace.line.width = Pt(1.5)
    brace.line.color.rgb = TEXT_COLOR
    add_text(slide, "14-month latency",
             cut_x, Inches(4.75), Emu(int(gpt_x - cut_x)), Inches(0.3),
             font=font, size=11, italic=True, color=TEXT_COLOR, align=PP_ALIGN.CENTER)

    # axis tick labels
    ticks = [(0.02, "Jan 2018"), (0.20, "2019"), (0.38, "2020"),
             (0.55, "Sept 2021"), (0.70, "Nov 2022"), (1.0, "Jan 2026")]
    for frac, lbl in ticks:
        tx = x_at(frac)
        tick = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, tx, Inches(3.65), tx, Inches(3.78))
        tick.line.width = Pt(1.5)
        tick.line.color.rgb = TEXT_COLOR
        bold = lbl in {"Sept 2021", "Nov 2022"}
        add_text(slide, lbl,
                 Emu(int(tx - Inches(0.8))), Inches(3.85),
                 Inches(1.6), Inches(0.35),
                 font=font, size=11, bold=bold, color=TEXT_COLOR, align=PP_ALIGN.CENTER)

    # footer explanation
    add_text(
        slide,
        "The September 2021 cutoff is an invisible property of training data; libraries released "
        "a week before or after look identical to a developer in 2021. No one could have "
        "anticipated ChatGPT, released 14 months later.",
        Inches(1.0), Inches(5.8), Inches(11.3), Inches(1.2),
        font=font, size=14, italic=True, color=TEXT_COLOR, align=PP_ALIGN.CENTER,
    )


def slide_identification(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "Identification", font)
    add_bullets(
        slide,
        [
            ("As-if random assignment:",
             " the exact week of release relative to an invisible training cutoff is exogenous to the library itself (McCrary density test: p = 0.43)."),
            ("RDD specifics:",
             " bandwidth h = 13 weeks; local-linear regression with triangular kernel; 9-week donut excludes the Aug\u2013Sept 2021 window of ambiguous training inclusion."),
            ("Inference:",
             " cluster-robust standard errors at the year-by-week level (~72 clusters); bias-corrected CIs via rdrobust."),
            ("Diff-in-RDD:",
             " 2021 discontinuity minus the mean placebo discontinuity (2018\u20132020) isolates the LLM-specific effect from calendar seasonality."),
        ],
        BODY_LEFT, Inches(1.4), BODY_W, BODY_H,
        font=font, size=17, spacing=1.4,
    )
    add_footer(slide, font)


def slide_validity(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "Validity diagnostics", font)
    add_bullets(
        slide,
        [
            ("No manipulation:",
             " McCrary density smooth across the cutoff (p = 0.43) \u2014 developers cannot time their release to an unannounced boundary."),
            ("Covariate balance, pre-AI:",
             " post-cutoff libraries actually start ahead on pre-ChatGPT downloads (a seasonal headwind for our hypothesis) \u2014 so the post-AI suppression is a conservative estimate."),
            ("Placebo years:",
             " 2018\u20132020 cohorts show no discontinuity at the same calendar position, ruling out seasonality as the driver."),
        ],
        BODY_LEFT, Inches(1.5), BODY_W, BODY_H,
        font=font, size=18, spacing=1.5,
    )
    add_footer(slide, font)


def slide_headline(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)

    add_text(
        slide,
        "Post-cutoff libraries have",
        Inches(0.6), Inches(1.5), Inches(12.1), Inches(0.8),
        font=font, size=26, color=TEXT_COLOR, align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        "+430%",
        Inches(0.6), Inches(2.4), Inches(12.1), Inches(2.8),
        font=font, size=140, bold=True, color=ACCENT_RED, align=PP_ALIGN.CENTER,
        anchor=MSO_ANCHOR.MIDDLE,
    )
    add_text(
        slide,
        "fewer weekly downloads by January 2026.",
        Inches(0.6), Inches(5.3), Inches(12.1), Inches(0.8),
        font=font, size=26, color=TEXT_COLOR, align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        "Ratio of pre-cutoff to post-cutoff downloads (Jan 2026).  "
        "Diff-in-RDD: p = 0.001 (Broad), p = 0.002 (Successful), baseline-adjusted, cluster-robust SE.",
        Inches(1.5), Inches(6.5), Inches(10.3), Inches(0.8),
        font=font, size=12, italic=True, color=MUTED_GREY, align=PP_ALIGN.CENTER,
    )


def slide_activation(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "Activation dynamics", font)

    add_bullets(
        slide,
        [
            ("Dormant:", " gap flat at ~28% seasonal baseline before Nov 2022."),
            ("Activation:", " discontinuity emerges only after ChatGPT's mass adoption."),
            ("Trajectory:", " +136% at 12 months, +287% at 24 months, +430% by Jan 2026."),
            ("Shaded band:", " 95% bootstrap confidence interval."),
        ],
        Inches(0.6), Inches(1.5), Inches(5.0), Inches(5.5),
        font=font, size=15, spacing=1.4,
    )

    fig_path = FIGURES_DIR / "normalized_diffusion_gap_pypi.png"
    if fig_path.exists():
        slide.shapes.add_picture(
            str(fig_path),
            Inches(5.9), Inches(1.4),
            width=Inches(7.0),
        )
    add_footer(slide, font)


def slide_mechanism(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "Mechanism: GitHub imports", font)

    add_card(slide, Inches(0.6), Inches(1.3), Inches(6.0), Inches(5.6))
    add_text(slide, "Directional evidence",
             Inches(0.85), Inches(1.5), Inches(5.6), Inches(0.5),
             font=font, size=16, bold=True, color=TEXT_COLOR)
    add_bullets(
        slide,
        [
            ("Matched subsample,", " N = 6,582 in the Diff-in-RDD."),
            ("All-time imports:", " +2.12 log-point jump (baseline-adjusted, p = 0.022) \u2014 post-cutoff libraries accumulate MORE GitHub imports, opposite sign to PyPI."),
        ],
        Inches(0.85), Inches(2.1), Inches(5.6), Inches(4.5),
        font=font, size=14, spacing=1.4,
    )

    add_card(slide, Inches(6.9), Inches(1.3), Inches(6.0), Inches(5.6), fill=RGBColor(0xDB, 0xEA, 0xFE))
    add_text(slide, "Interpretation",
             Inches(7.15), Inches(1.5), Inches(5.6), Inches(0.5),
             font=font, size=16, bold=True, color=ACCENT_BLUE)
    add_bullets(
        slide,
        [
            ("Flow vs. stock:", " PyPI downloads are a flow; GitHub imports are a stock of existing code."),
            ("Displacement:", " new libraries displace old ones in flow, but existing repos keep their old imports."),
            ("LLM steering:", " the LLM pushes the FIRST try, not every line of legacy code."),
        ],
        Inches(7.15), Inches(2.1), Inches(5.6), Inches(4.5),
        font=font, size=14, spacing=1.4,
    )
    add_footer(slide, font)


def slide_moderation(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "Moderation & scope", font)
    add_bullets(
        slide,
        [
            ("AI-exposure heterogeneity:",
             " directional but non-significant (p = 0.18) \u2014 suggests a broad, systemic effect rather than a subset-specific channel."),
            ("Ecosystem:",
             " Python only. Rust, JS, R may show different magnitudes."),
            ("One cutoff:",
             " effects estimated around September 2021; newer-model cutoffs would require separate estimation."),
            ("SUTVA:",
             " the gap reflects direct suppression plus substitution toward established tools \u2014 both are part of the LLM effect."),
        ],
        BODY_LEFT, Inches(1.5), BODY_W, BODY_H,
        font=font, size=17, spacing=1.4,
    )
    add_footer(slide, font)


def slide_implications(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "Implications", font)

    add_card(slide, Inches(0.6), Inches(1.4), Inches(12.1), Inches(1.5),
             fill=RGBColor(0xFE, 0xE2, 0xE2))
    add_text(slide, "The Knowledge Wall",
             Inches(0.85), Inches(1.55), Inches(11.6), Inches(0.5),
             font=font, size=18, bold=True, color=ACCENT_RED)
    add_text(slide,
             "Training-data cutoffs act as a functional barrier for newly released software tools.",
             Inches(0.85), Inches(2.05), Inches(11.6), Inches(0.8),
             font=font, size=15, color=TEXT_COLOR)

    add_bullets(
        slide,
        [
            ("Durable advantage:",
             " tools embedded in LLM weights gain persistent visibility."),
            ("Spillovers:",
             " same logic plausibly applies to research papers, blog posts, documentation."),
            ("Policy:",
             " raises questions about how AI systems update their internal knowledge and what the costs are of being \u2018outside the wall\u2019."),
        ],
        BODY_LEFT, Inches(3.3), BODY_W, Inches(3.6),
        font=font, size=16, spacing=1.4,
    )
    add_footer(slide, font)


def slide_limitations(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "Limitations", font)
    add_bullets(
        slide,
        [
            "We observe outcomes (downloads, imports), not LLM usage directly.",
            "AI systems are evolving \u2014 web search and retrieval may erode the wall over time.",
            "One language, one cutoff, one year of treatment \u2014 external validity is local.",
            "Running variable is release date; metadata errors could attenuate estimates.",
        ],
        BODY_LEFT, Inches(1.6), BODY_W, BODY_H,
        font=font, size=18, spacing=1.6,
    )
    add_footer(slide, font)


def slide_conclusion(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "Conclusion", font)

    add_card(slide, Inches(0.6), Inches(1.4), Inches(12.1), Inches(2.2),
             fill=RGBColor(0xFE, 0xE2, 0xE2))
    add_text(
        slide,
        "A +430% diffusion gap by January 2026, activated only after ChatGPT,\n"
        "with no placebo discontinuities \u2014 a clean quasi-experiment\n"
        "for collective narrowing in the age of LLMs.",
        Inches(0.85), Inches(1.55), Inches(11.6), Inches(2.0),
        font=font, size=20, bold=True, color=ACCENT_RED,
        align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
    )
    add_bullets(
        slide,
        [
            "LLMs steer adoption toward tools already in training data.",
            "Libraries released post-cutoff face persistent disadvantages.",
            "The Knowledge Wall is real, measurable, and widening.",
        ],
        BODY_LEFT, Inches(4.1), BODY_W, Inches(3.0),
        font=font, size=18, spacing=1.5,
    )


def slide_thanks(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, TEXT_COLOR)

    add_text(slide, "Thank you.",
             Inches(0.5), Inches(0.8), Inches(12.3), Inches(1.5),
             font=font, size=60, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF),
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, "Questions?",
             Inches(0.5), Inches(2.3), Inches(12.3), Inches(0.8),
             font=font, size=28, color=MUTED_GREY,
             align=PP_ALIGN.CENTER)

    # mini-timeline
    t_top = Inches(4.2)
    t_left = Inches(1.5)
    t_right = Inches(11.8)
    line = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, t_left, t_top, t_right, t_top)
    line.line.width = Pt(1.5)
    line.line.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    def at(frac):
        return Emu(int(t_left + (t_right - t_left) * frac))

    cut_x = at(0.55)
    gpt_x = at(0.70)
    cm = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, cut_x, Inches(3.95), cut_x, Inches(4.45))
    cm.line.width = Pt(2); cm.line.color.rgb = ACCENT_RED
    gm = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, gpt_x, Inches(3.95), gpt_x, Inches(4.45))
    gm.line.width = Pt(2); gm.line.color.rgb = ACCENT_BLUE

    ticks = [(0.0, "2018"), (0.55, "Sept '21"), (0.70, "Nov '22"), (1.0, "Jan '26")]
    for frac, lbl in ticks:
        x = at(frac)
        add_text(slide, lbl,
                 Emu(int(x - Inches(0.8))), Inches(4.55),
                 Inches(1.6), Inches(0.3),
                 font=font, size=11, color=RGBColor(0xFF, 0xFF, 0xFF),
                 align=PP_ALIGN.CENTER)

    add_text(slide, "+430%",
             Inches(0.5), Inches(5.5), Inches(12.3), Inches(1.3),
             font=font, size=80, bold=True, color=ACCENT_RED,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, "diffusion gap by Jan 2026.",
             Inches(0.5), Inches(6.75), Inches(12.3), Inches(0.5),
             font=font, size=20, color=RGBColor(0xFF, 0xFF, 0xFF),
             align=PP_ALIGN.CENTER)


# ----- Appendix ------------------------------------------------------------


def slide_appendix_divider(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, TEXT_COLOR)
    add_text(slide, "Appendix",
             Inches(0.5), Inches(3.0), Inches(12.3), Inches(1.5),
             font=font, size=72, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF),
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def add_table(slide, rows: list, left, top, width, height, *, font: str, header_color=TEXT_COLOR,
              header_fg=RGBColor(0xFF, 0xFF, 0xFF), body_size=13, header_size=14):
    n_rows = len(rows)
    n_cols = len(rows[0])
    tbl = slide.shapes.add_table(n_rows, n_cols, left, top, width, height).table
    for r_idx, row in enumerate(rows):
        for c_idx, cell_text in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.margin_left = Emu(60000)
            cell.margin_right = Emu(60000)
            cell.margin_top = Emu(30000)
            cell.margin_bottom = Emu(30000)
            if r_idx == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = header_color
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = BG_COLOR if r_idx % 2 == 1 else LIGHT_SHADE
            tf = cell.text_frame
            tf.word_wrap = True
            tf.paragraphs[0].text = ""
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if c_idx == 0 else PP_ALIGN.RIGHT
            run = p.add_run()
            run.text = str(cell_text)
            run.font.name = font
            run.font.size = Pt(header_size if r_idx == 0 else body_size)
            run.font.bold = (r_idx == 0)
            run.font.color.rgb = header_fg if r_idx == 0 else TEXT_COLOR
    return tbl


def slide_a1(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "A1.  Summary statistics", font)

    rows = [
        ["Horizon", "Pre-cutoff mean", "Post-cutoff mean", "\u0394%"],
        ["ChatGPT + 6 months",  "1,467",  "630",   "+133%"],
        ["ChatGPT + 12 months", "2,559",  "1,085", "+136%"],
        ["ChatGPT + 24 months", "8,218",  "2,124", "+287%"],
        ["January 2026",        "18,085", "3,410", "+430%"],
        ["Post-ChatGPT average", "6,538",  "1,703", "+284%"],
    ]
    add_table(slide, rows, Inches(1.4), Inches(1.5), Inches(10.5), Inches(3.8), font=font)

    add_text(
        slide,
        "Weekly PyPI downloads, mean across libraries in each cohort.  "
        "Pre-cutoff: libraries released Jan\u2013Aug 2021.  "
        "Post-cutoff: Oct 2021\u2013.",
        Inches(1.4), Inches(5.7), Inches(10.5), Inches(1.2),
        font=font, size=12, italic=True, color=MUTED_GREY,
    )
    add_footer(slide, font)


def slide_a2(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "A2.  Diff-in-RDD estimates (PyPI)", font)

    rows = [
        ["Panel", "Tier", "Excess jump", "SE", "p", "N"],
        ["Pre-ChatGPT baseline",     "Successful", "-3.72",  "1.67", "0.026", "75,313"],
        ["Post-ChatGPT, adjusted",   "Broad",      "-7.29",  "2.20", "0.001", "88,001"],
        ["Post-ChatGPT, adjusted",   "Successful", "-7.29",  "2.39", "0.002", "75,313"],
        ["Post-ChatGPT, adjusted",   "Superstar",  "-0.25",  "0.35", "0.473", "57,931"],
        ["Post-ChatGPT, unadjusted", "Broad",      "-9.14",  "4.42", "0.039", "88,001"],
        ["Post-ChatGPT, unadjusted", "Successful", "-12.79", "4.83", "0.008", "75,313"],
    ]
    add_table(slide, rows, Inches(0.8), Inches(1.4), Inches(11.8), Inches(4.2), font=font)
    add_text(
        slide,
        "Log-scale estimates: discontinuity in log(1 + downloads) at the cutoff, differenced against "
        "2018\u20132020 placebos.  Baseline adjustment = ANCOVA on log pre-ChatGPT downloads.",
        Inches(0.8), Inches(5.9), Inches(11.8), Inches(1.2),
        font=font, size=12, italic=True, color=MUTED_GREY,
    )
    add_footer(slide, font)


def slide_a3(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "A3.  Bandwidth sensitivity", font)
    fig = FIGURES_DIR / "sensitivity_diff_in_rdd_bandwidth.png"
    if fig.exists():
        slide.shapes.add_picture(str(fig),
                                 Inches(2.5), Inches(1.3),
                                 width=Inches(8.3))
    add_text(
        slide,
        "Point estimate and 95% CI across bandwidth choices h \u2208 {10, 13, 18, 26, 39, 52} weeks.  "
        "Sign and significance stable.",
        Inches(1.0), Inches(6.5), Inches(11.3), Inches(0.7),
        font=font, size=12, italic=True, color=MUTED_GREY, align=PP_ALIGN.CENTER,
    )
    add_footer(slide, font)


def slide_a4(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "A4.  Density test and placebo years", font)

    d_fig = FIGURES_DIR / "density_dist_to_cutoff.png"
    if d_fig.exists():
        slide.shapes.add_picture(str(d_fig), Inches(0.6), Inches(1.3), width=Inches(6.0))
    add_text(slide, "McCrary density, p = 0.43.",
             Inches(0.6), Inches(6.2), Inches(6.0), Inches(0.4),
             font=font, size=12, italic=True, color=MUTED_GREY, align=PP_ALIGN.CENTER)

    p_fig = FIGURES_DIR / "stacked_rdd_comparison.png"
    if p_fig.exists():
        slide.shapes.add_picture(str(p_fig), Inches(6.8), Inches(1.3), width=Inches(6.0))
    add_text(slide, "2018\u20132020 placebo coefficients vs. 2021.  Only 2021 is significant.",
             Inches(6.8), Inches(6.2), Inches(6.0), Inches(0.4),
             font=font, size=12, italic=True, color=MUTED_GREY, align=PP_ALIGN.CENTER)

    add_footer(slide, font)


def slide_a5(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "A5.  GitHub mechanism results", font)

    rows = [
        ["Tier", "Outcome", "Excess jump", "SE", "p"],
        ["Broad",      "All-time imports", "+2.12", "0.92", "0.022"],
        ["Broad",      "Post-AI imports",  "+1.87", "1.05", "0.075"],
        ["Successful", "All-time imports", "+2.29", "0.96", "0.017"],
        ["Successful", "Post-AI imports",  "+2.09", "1.15", "0.069"],
    ]
    add_table(slide, rows, Inches(1.5), Inches(1.5), Inches(10.3), Inches(3.0), font=font)
    add_text(
        slide,
        "Baseline-adjusted Diff-in-RDD on log(1 + GitHub imports), N = 6,582 (Broad).  "
        "Positive sign: post-cutoff libraries accumulate MORE imports \u2014 consistent with stock-vs-flow interpretation.",
        Inches(1.5), Inches(5.0), Inches(10.3), Inches(1.5),
        font=font, size=12, italic=True, color=MUTED_GREY,
    )
    add_footer(slide, font)


def slide_a6(prs, font: str) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, BG_COLOR)
    add_title_bar(slide, "A6.  Reviewer comments placeholder", font)

    add_card(slide, Inches(1.0), Inches(1.5), Inches(11.3), Inches(5.3))
    add_text(slide, "Notes for discussion",
             Inches(1.3), Inches(1.75), Inches(10.7), Inches(0.6),
             font=font, size=18, bold=True, color=TEXT_COLOR)
    for i in range(5):
        y = 2.6 + i * 0.65
        add_text(slide, "\u2022  ",
                 Inches(1.3), Inches(y), Inches(0.3), Inches(0.4),
                 font=font, size=16, color=ACCENT_BLUE)
        add_text(slide, " " if i > 0 else "[to be populated during Q\u0026A]",
                 Inches(1.6), Inches(y), Inches(9.5), Inches(0.4),
                 font=font, size=14, italic=(i == 0), color=MUTED_GREY if i == 0 else TEXT_COLOR)


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


SLIDE_BUILDERS: list[Callable] = [
    slide_title,
    slide_motivation,
    slide_method,
    slide_data,
    slide_timeline,
    slide_identification,
    slide_validity,
    slide_headline,
    slide_activation,
    slide_mechanism,
    slide_moderation,
    slide_implications,
    slide_limitations,
    slide_conclusion,
    slide_thanks,
    slide_appendix_divider,
    slide_a1,
    slide_a2,
    slide_a3,
    slide_a4,
    slide_a5,
    slide_a6,
]


def build(font: str, output_path: Path) -> None:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    for builder in SLIDE_BUILDERS:
        builder(prs, font)
    prs.save(str(output_path))


def main() -> None:
    here = Path(__file__).parent
    build("Calibri",        here / "thesis_prezi_powerpoint.pptx")
    build("Helvetica Neue", here / "thesis_prezi_keynote.pptx")
    print(f"Wrote {len(SLIDE_BUILDERS)} slides each to:")
    print(f"  - {here / 'thesis_prezi_powerpoint.pptx'}")
    print(f"  - {here / 'thesis_prezi_keynote.pptx'}")


if __name__ == "__main__":
    main()
