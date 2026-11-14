"""Look and feel: neutral palette, Inter, flat surfaces, no chrome."""
import gradio as gr


def make_theme() -> gr.themes.Base:
    return gr.themes.Base(
        primary_hue="emerald",
        neutral_hue="zinc",
        radius_size="lg",
        font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
        font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "ui-monospace", "monospace"],
    ).set(
        block_border_width="0px",
        block_shadow="none",
        block_title_text_weight="500",
        button_primary_shadow="none",
        button_secondary_border_color="transparent",
    )


CSS = """
.gradio-container { max-width: 1440px !important; margin: 0 auto; }
footer { display: none !important; }
#header { padding: 8px 0 4px; }
#header h1 { font-size: 1.35rem; font-weight: 600; letter-spacing: -0.01em; margin: 0; }
#header p { margin: 2px 0 0; opacity: .6; font-size: .9rem; }
#chat { border: 1px solid var(--border-color-primary); border-radius: 16px; }
#chat .bubble-wrap { background: transparent; }
#composer textarea { border-radius: 12px; }
#quota { opacity: .5; font-size: .8rem; }
#side { border: 1px solid var(--border-color-primary); border-radius: 16px; padding: 4px 8px; }
.tab-wrapper, .tab-container { border-color: transparent !important; }
button.selected { font-weight: 600; }
table { font-size: .85rem; }
"""
