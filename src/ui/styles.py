"""NovelNexus UI Styling and Design System."""
import streamlit as st  # type: ignore


def inject_custom_css():
    """Injects high-performance, modern CSS styles into the Streamlit app."""
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    :root {
        --bg-canvas: #090C10;
        --surface-1: #111622;
        --surface-2: #161D2E;
        --surface-hover: #1C2438;
        --border-glass: rgba(255, 255, 255, 0.08);
        --border-accent: rgba(99, 102, 241, 0.4);
        --primary-indigo: #6366F1;
        --primary-purple: #A855F7;
        --accent-pink: #EC4899;
        --text-headline: #F8FAFC;
        --text-sub: #94A3B8;
        --text-muted: #64748B;
        --badge-emerald: #10B981;
        --badge-amber: #F59E0B;
    }

    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: var(--bg-canvas) !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text-headline) !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D111A 0%, #080A0E 100%) !important;
        border-right: 1px solid var(--border-glass) !important;
    }

    /* Ambient Spotlight Background Mesh */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.12) 0%, transparent 40%),
                    radial-gradient(circle at 85% 20%, rgba(168, 85, 247, 0.10) 0%, transparent 40%),
                    radial-gradient(circle at 50% 80%, rgba(236, 72, 153, 0.08) 0%, transparent 45%);
        pointer-events: none;
        z-index: 0;
    }

    /* Hero Showcase Banner */
    .nn-hero {
        position: relative;
        background: linear-gradient(135deg, rgba(22, 29, 46, 0.75) 0%, rgba(15, 19, 30, 0.9) 100%);
        border: 1px solid var(--border-glass);
        border-radius: 18px;
        padding: 26px 32px;
        margin-bottom: 22px;
        backdrop-filter: blur(20px);
        box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.6);
        overflow: hidden;
    }
    .nn-hero::after {
        content: "";
        position: absolute;
        top: -50%;
        right: -10%;
        width: 280px;
        height: 280px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.22) 0%, transparent 70%);
        filter: blur(40px);
        pointer-events: none;
    }
    .nn-hero-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.35);
        padding: 3px 10px;
        border-radius: 30px;
        font-size: 10.5px;
        font-weight: 700;
        color: #A5B4FC;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }
    .nn-hero-title {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.2;
        background: linear-gradient(135deg, #FFFFFF 0%, #CBD5E1 50%, #A5B4FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    .nn-hero-sub {
        color: var(--text-sub);
        font-size: 13.5px;
        font-weight: 400;
        line-height: 1.5;
        max-width: 720px;
    }

    /* Sidebar Border Containers as Modern Cards */
    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(135deg, rgba(22, 29, 46, 0.75) 0%, rgba(13, 17, 26, 0.95) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 14px 16px !important;
        box-shadow: 0 10px 24px -5px rgba(0, 0, 0, 0.45) !important;
        margin-bottom: 14px !important;
    }

    .profile-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6366F1, #A855F7);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }
    .profile-tag-box {
        display: flex;
        flex-direction: column;
        gap: 4px;
        padding: 10px 12px;
        background: rgba(9, 12, 18, 0.85);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        margin-top: 10px;
    }

    /* Unified Modern Book Card */
    .nn-card {
        background: linear-gradient(180deg, rgba(22, 29, 46, 0.85) 0%, rgba(16, 21, 33, 0.95) 100%);
        border: 1px solid var(--border-glass);
        border-radius: 14px;
        padding: 14px 14px 10px 14px;
        height: 350px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        backdrop-filter: blur(16px);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        box-shadow: 0 10px 24px -6px rgba(0, 0, 0, 0.4);
        margin-bottom: 8px;
    }
    .nn-card:hover {
        border-color: rgba(99, 102, 241, 0.5);
        background: linear-gradient(180deg, rgba(28, 36, 56, 0.9) 0%, rgba(20, 26, 40, 0.98) 100%);
        box-shadow: 0 16px 36px -8px rgba(99, 102, 241, 0.25);
        transform: translateY(-2px);
    }

    .nn-cover-wrapper {
        width: 100%;
        height: 175px;
        border-radius: 8px;
        background: #090C12;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        margin-bottom: 10px;
        position: relative;
    }
    .nn-cover-img {
        width: 110px;
        height: 165px;
        object-fit: cover;
        border-radius: 4px 8px 8px 4px;
        box-shadow: -4px 6px 16px rgba(0, 0, 0, 0.65);
        transition: transform 0.25s ease;
    }
    .nn-card:hover .nn-cover-img {
        transform: scale(1.04) rotate(-1deg);
    }
    .nn-book-title {
        font-size: 13px;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.35;
        min-height: 36px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        margin-bottom: 2px;
    }
    .nn-book-author {
        font-size: 11.5px;
        color: var(--text-sub);
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 4px;
    }
    .nn-rating-bar {
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 11px;
        color: var(--badge-amber);
        font-weight: 700;
        margin-bottom: 4px;
    }
    .nn-review-count {
        color: var(--text-muted);
        font-weight: 400;
        font-size: 10px;
    }
    .nn-meta-chip {
        font-size: 10.5px;
        color: var(--text-muted);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 4px;
    }

    /* Badges */
    .nn-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 9.5px;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .nn-badge-vintage {
        background: rgba(245, 158, 11, 0.12);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.25);
    }
    .nn-badge-modern {
        background: rgba(99, 102, 241, 0.12);
        color: #A5B4FC;
        border: 1px solid rgba(99, 102, 241, 0.25);
    }
    .nn-badge-saved {
        background: rgba(236, 72, 153, 0.15);
        color: #F472B6;
        border: 1px solid rgba(236, 72, 153, 0.35);
    }

    /* Pulse Dot */
    .pulse-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10B981;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulseAnimation 2s infinite;
    }
    @keyframes pulseAnimation {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Bento Stat Card */
    .bento-card {
        background: linear-gradient(135deg, rgba(22, 29, 46, 0.6) 0%, rgba(13, 17, 26, 0.8) 100%);
        border: 1px solid var(--border-glass);
        border-radius: 14px;
        padding: 16px;
        backdrop-filter: blur(12px);
    }
    .bento-title {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-muted);
        font-weight: 700;
        margin-bottom: 4px;
    }
    .bento-value {
        font-size: 17px;
        font-weight: 800;
        color: #FFFFFF;
    }

    /* Modern Sleek Action Button */
    div.stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(168, 85, 247, 0.12) 100%) !important;
        border: 1px solid rgba(99, 102, 241, 0.35) !important;
        color: #E2E8F0 !important;
        height: 36px !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.3) 0%, rgba(168, 85, 247, 0.3) 100%) !important;
        border-color: rgba(99, 102, 241, 0.75) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    /* Hide all default Streamlit spinners and running widgets */
    [data-testid=stStatusWidget], .stSpinner, div[data-testid=stToolbar] [data-testid=stStatusWidget] { display: none !important; visibility: hidden !important; }
</style>""", unsafe_allow_html=True)

