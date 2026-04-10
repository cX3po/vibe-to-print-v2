#!/usr/bin/env python3
"""
Vibe to Print v2 — Simple, Clean, Dad-Friendly
Photograph something broken. Get help fixing it.
"""
import streamlit as st
import os
import json
import io
import requests
from datetime import datetime

# ── API Key ──────────────────────────────────────────────────────────────────
def load_api_key():
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if key: return key
    except: pass
    env_path = os.path.expanduser("~/axiom/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith("ANTHROPIC_API_KEY="):
                    return line.strip().split("=", 1)[1].strip('"').strip("'")
    return os.getenv("ANTHROPIC_API_KEY", "")

API_KEY = load_api_key()
if API_KEY: os.environ["ANTHROPIC_API_KEY"] = API_KEY

# ── AX Chat ──────────────────────────────────────────────────────────────────
def chat_with_ax(message, context="", history=None):
    if not API_KEY: return "No API key. Add ANTHROPIC_API_KEY in settings."
    system = """You are AX, a friendly and practical AI assistant for the family.
You're an expert in home repair, 3D printing, and fixing broken things.
You know about materials (PLA, PETG, ABS, TPU), tools, adhesives, and where to buy replacement parts.
You give simple, clear advice that anyone can follow — even if they've never 3D printed before.
When someone shows you something broken, you explain what it is, the easiest way to fix it,
and whether it can be 3D printed, glued, or bought as a replacement.
Be warm, patient, and practical. Assume the person is NOT technical."""
    if context: system += f"\n\nContext: {context}"
    messages = []
    if history:
        for msg in history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})
    try:
        resp = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-haiku-4-5-20251001", "max_tokens": 1024,
                  "system": system, "messages": messages}, timeout=30)
        if resp.ok: return resp.json()["content"][0]["text"]
        return f"API error: {resp.status_code}"
    except Exception as e: return f"Error: {e}"

# ── Photo Guide SVG ──────────────────────────────────────────────────────────
PHOTO_GUIDE_SVG = """
<svg viewBox="0 0 520 420" xmlns="http://www.w3.org/2000/svg" style="max-width:520px;font-family:sans-serif;">
  <!-- Broken part -->
  <rect x="120" y="80" width="160" height="100" rx="5" fill="#d4c4a8" stroke="#333" stroke-width="2"/>
  <line x1="180" y1="80" x2="200" y2="180" stroke="#e74c3c" stroke-width="3" stroke-dasharray="5"/>
  <text x="200" y="140" text-anchor="middle" font-size="12" fill="#666">BROKEN PART</text>

  <!-- Reference object (coin) -->
  <circle cx="340" cy="140" r="22" fill="#daa520" stroke="#b8860b" stroke-width="2"/>
  <text x="340" y="145" text-anchor="middle" font-size="9" fill="#333" font-weight="bold">25c</text>
  <line x1="365" y1="140" x2="420" y2="110" stroke="#3498db" stroke-width="1.5"/>
  <text x="390" y="105" font-size="10" fill="#3498db">Reference</text>
  <text x="390" y="117" font-size="10" fill="#3498db">object for</text>
  <text x="390" y="129" font-size="10" fill="#3498db">size (coin,</text>
  <text x="390" y="141" font-size="10" fill="#3498db">credit card,</text>
  <text x="390" y="153" font-size="10" fill="#3498db">or ruler)</text>

  <!-- Break callout -->
  <line x1="190" y1="130" x2="60" y2="100" stroke="#e74c3c" stroke-width="1.5"/>
  <text x="5" y="95" font-size="10" fill="#e74c3c">Show the break</text>
  <text x="5" y="107" font-size="10" fill="#e74c3c">or damage clearly</text>

  <!-- Dimension arrows -->
  <line x1="120" y1="200" x2="280" y2="200" stroke="#2ecc71" stroke-width="1.5"/>
  <line x1="120" y1="195" x2="120" y2="205" stroke="#2ecc71" stroke-width="2"/>
  <line x1="280" y1="195" x2="280" y2="205" stroke="#2ecc71" stroke-width="2"/>
  <text x="200" y="218" text-anchor="middle" font-size="10" fill="#2ecc71">Width</text>

  <line x1="290" y1="80" x2="290" y2="180" stroke="#9b59b6" stroke-width="1.5"/>
  <line x1="285" y1="80" x2="295" y2="80" stroke="#9b59b6" stroke-width="2"/>
  <line x1="285" y1="180" x2="295" y2="180" stroke="#9b59b6" stroke-width="2"/>
  <text x="308" y="135" font-size="10" fill="#9b59b6">Height</text>

  <!-- Camera -->
  <rect x="160" y="260" width="100" height="35" rx="5" fill="#333"/>
  <circle cx="210" cy="277" r="10" fill="none" stroke="white" stroke-width="2"/>
  <circle cx="210" cy="277" r="4" fill="white"/>

  <!-- 4 photo tips -->
  <text x="260" y="250" font-size="12" font-weight="bold" fill="#333">Take 2-4 photos:</text>
  <text x="260" y="268" font-size="11" fill="#555">1. Broken part + coin/ruler</text>
  <text x="260" y="284" font-size="11" fill="#555">2. Close-up of the break</text>
  <text x="260" y="300" font-size="11" fill="#555">3. Where it goes (appliance)</text>
  <text x="260" y="316" font-size="11" fill="#555">4. Bottom/back (part numbers)</text>

  <text x="260" y="345" font-size="11" font-weight="bold" fill="#333">Good light. Flat angle. No shadows.</text>

  <!-- Reference objects guide -->
  <text x="20" y="370" font-size="11" font-weight="bold" fill="#333">Reference Objects for Size:</text>
  <text x="20" y="386" font-size="10" fill="#555">Quarter = 24.3mm | Nickel = 21.2mm | Credit card = 85.6 x 53.98mm</text>
  <text x="20" y="400" font-size="10" fill="#555">AA Battery = 50.5 x 14.5mm | Dollar bill = 156 x 66.3mm</text>
  <text x="20" y="414" font-size="10" fill="#555">Ruler/tape measure = best option for accurate dimensions</text>
</svg>
"""

# ── Main App ─────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="Vibe to Print", page_icon="\U0001f527", layout="wide")

    # Family login
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    if not st.session_state.user_name:
        st.markdown("## \U0001f527 Vibe to Print")
        st.markdown("**Photograph something broken. Get help fixing it.**")
        st.markdown("---")
        st.markdown("**Sign in so AX knows who you are:**")
        name = st.text_input("Your name", placeholder="e.g. Dad, Phil, Colin")
        if name and st.button("Sign In", type="primary"):
            st.session_state.user_name = name
            st.rerun()
        st.stop()
    user_name = st.session_state.user_name

    st.title("\U0001f527 Vibe to Print")
    st.caption("Photograph something broken. Get help fixing it.")

    # Sidebar
    with st.sidebar:
        st.markdown(f"**Signed in as:** {user_name}")
        if st.button("Sign Out", key="signout"):
            st.session_state.user_name = ""
            st.rerun()
        st.markdown("---")
        st.markdown("### Settings")
        if API_KEY:
            st.success("AI Connected")
        else:
            user_key = st.text_input("API Key", type="password", placeholder="sk-ant-...")
            if user_key:
                os.environ["ANTHROPIC_API_KEY"] = user_key
                st.success("Key set!")
                st.rerun()
            st.caption("Get a free key at console.anthropic.com")

        st.markdown("---")
        st.markdown("### How It Works")
        st.markdown("""
        1. **Take a photo** of the broken thing
        2. **AX identifies it** and tells you what's wrong
        3. **Get fix options**: buy replacement, 3D print, or glue it
        4. **Find parts**: search links for Amazon, eBay, hardware store
        5. **Ask AX** any follow-up questions
        """)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["\U0001f4f7 Fix Something", "\U0001f916 Ask AX", "\U0001f4da How to 3D Print"])

    # ── TAB 1: Fix Something ──
    with tab1:
        st.markdown("### What needs fixing?")

        upload_mode = st.radio("", [
            "Take/Upload a photo of the broken part",
            "Describe what's broken (no photo)"
        ], horizontal=True, label_visibility="collapsed")

        if upload_mode.startswith("Take"):
            # Photo guide
            with st.expander("How to photograph for best results", expanded=False):
                st.markdown(PHOTO_GUIDE_SVG, unsafe_allow_html=True)
                st.markdown("""
                **For accurate identification and sizing:**

                **Photo 1 — The broken part + a reference object:**
                - Place the broken part on a flat surface
                - Put a **coin (quarter), credit card, or ruler** next to it
                - This lets AX estimate the real size

                **Photo 2 — Close-up of the break:**
                - Show exactly what's broken, cracked, or worn
                - Get close so AX can see the damage clearly

                **Photo 3 — Where it came from:**
                - Show where the part goes on the appliance/furniture
                - This helps identify the exact part number

                **Photo 4 (optional) — The bottom/back:**
                - Many parts have brand names, model numbers, or part numbers
                - These make finding a replacement much easier

                **Good light, no shadows, flat angle = best results**
                """)

            photos = st.file_uploader("Upload photo(s) of the broken part",
                type=["jpg","jpeg","png","webp"], accept_multiple_files=True,
                help="Tip: photograph the broken part up close, in good light. Include a coin or ruler for size reference.")

            if photos and st.button("What's broken & how do I fix it?", type="primary"):
                if not API_KEY:
                    st.error("Add your API key in the sidebar to use AI features.")
                else:
                    try:
                        from engine import VisionEngine
                        from print_prompts import IDENTIFY_BROKEN, ROOM_SCAN_BROKEN
                        engine = VisionEngine(provider="haiku")

                        all_results = []
                        for i, photo in enumerate(photos):
                            img_bytes = photo.read()
                            prompt = IDENTIFY_BROKEN if len(photos) <= 2 else ROOM_SCAN_BROKEN
                            with st.spinner(f"AX is looking at photo {i+1}..."):
                                results = engine.analyze(img_bytes, prompt)
                                for r in results:
                                    all_results.append({"image": img_bytes if i == 0 else None, "data": r.raw})

                        if all_results:
                            for item in all_results:
                                d = item["data"]
                                st.markdown("---")

                                # Show image if available
                                if item.get("image"):
                                    col1, col2 = st.columns([1, 2])
                                    with col1:
                                        st.image(item["image"], width=280)
                                else:
                                    col2 = st.container()

                                with (col2 if item.get("image") else st):
                                    st.markdown(f"### {d.get('part_name', d.get('item_name', 'Unknown Part'))}")

                                    # What broke
                                    what_broke = d.get('what_broke', d.get('fix_suggestion', ''))
                                    if what_broke:
                                        st.markdown(f"**What's wrong:** {what_broke}")

                                    # Fix options
                                    st.markdown("#### How to fix it:")

                                    fix_cols = st.columns(3)

                                    with fix_cols[0]:
                                        if d.get('can_buy_replacement', True):
                                            st.markdown("**Buy a replacement**")
                                            search = d.get('buy_search_term', d.get('part_name', ''))
                                            price = d.get('estimated_buy_price', d.get('estimated_cost', '?'))
                                            st.markdown(f"Est. cost: ${price}")
                                            if search:
                                                st.markdown(f"[Search Amazon](https://www.amazon.com/s?k={search.replace(' ', '+')})")
                                                st.markdown(f"[Search eBay](https://www.ebay.com/sch/i.html?_nkw={search.replace(' ', '+')})")

                                    with fix_cols[1]:
                                        if d.get('can_3d_print', False):
                                            st.markdown("**3D Print it**")
                                            mat = d.get('print_material', 'PLA')
                                            st.markdown(f"Best material: **{mat}**")
                                            search_3d = d.get('part_name', '').replace(' ', '+')
                                            st.markdown(f"[Search Thingiverse](https://www.thingiverse.com/search?q={search_3d})")
                                            st.markdown(f"[Search Printables](https://www.printables.com/search/all?q={search_3d})")
                                        else:
                                            st.markdown("**3D Printing**")
                                            st.markdown("Not ideal for this part")

                                    with fix_cols[2]:
                                        if d.get('can_glue_repair', False):
                                            st.markdown("**Quick fix: Glue it**")
                                            tip = d.get('repair_tip', 'Try super glue or epoxy')
                                            st.markdown(tip)
                                        else:
                                            st.markdown("**Repair tip**")
                                            st.markdown(d.get('repair_tip', 'See options at left'))

                                    # Dimensions with reference object
                                    st.markdown("#### Measurements")
                                    ref = d.get('reference_object_found', 'none')
                                    if ref and ref != 'none':
                                        st.markdown(f"Reference object detected: **{ref}**")
                                    w = d.get('estimated_width_mm')
                                    h = d.get('estimated_height_mm')
                                    dp = d.get('estimated_depth_mm')
                                    if w or h or dp:
                                        dim_cols = st.columns(4)
                                        with dim_cols[0]: st.metric("Width", f"{w or '?'}mm")
                                        with dim_cols[1]: st.metric("Height", f"{h or '?'}mm")
                                        with dim_cols[2]: st.metric("Depth", f"{dp or '?'}mm")
                                        conf = d.get('dimension_confidence', '?')
                                        conf_color = {"high":"green","medium":"orange","low":"red"}.get(conf.lower() if isinstance(conf,str) else "","gray")
                                        with dim_cols[3]: st.metric("Confidence", conf)
                                    else:
                                        st.caption("Include a coin or ruler in the photo for accurate measurements.")

                                    # Cost summary
                                    rep_cost = d.get('replacement_cost')
                                    rep_repair = d.get('repair_cost')
                                    item_val = d.get('value_of_item')
                                    if rep_cost or rep_repair or item_val:
                                        st.markdown("#### Cost")
                                        cost_cols = st.columns(3)
                                        if rep_cost: cost_cols[0].metric("Replace Part", f"${rep_cost}")
                                        if rep_repair: cost_cols[1].metric("Repair Cost", f"${rep_repair}")
                                        if item_val: cost_cols[2].metric("Item Worth", f"${item_val}")

                                    # Difficulty
                                    diff = d.get('difficulty', d.get('urgency', ''))
                                    if diff:
                                        color = {"easy":"green","low":"green","moderate":"orange","medium":"orange","hard":"red","high":"red"}.get(diff.lower(),"gray")
                                        st.markdown(f"Difficulty: :{color}[**{diff}**]")

                                    # Deep search button
                                    part_name = d.get('part_name', '')
                                    if part_name and st.button(f"Find exact replacement for '{part_name}'", key=f"find_{part_name[:20]}"):
                                        with st.spinner("AX is searching for this exact part..."):
                                            search_result = chat_with_ax(
                                                f"Help me find an exact replacement for: {part_name}. "
                                                f"Material: {d.get('material','')}. Size: {w}x{h}x{dp}mm. "
                                                f"Give me: 1) Exact Amazon search term, 2) eBay search term, "
                                                f"3) Hardware store description (what to ask for), "
                                                f"4) Thingiverse/Printables search for 3D printable version, "
                                                f"5) If brand-specific, the exact part number. "
                                                f"6) Pro tips for finding this specific part."
                                            )
                                            st.markdown(search_result)

                        else:
                            st.warning("Couldn't identify the part. Try a clearer, closer photo.")

                    except Exception as e:
                        st.error(f"Error: {e}")

        else:
            # Text description mode
            describe = st.text_area("Describe what's broken",
                placeholder="e.g. The plastic clip that holds my refrigerator shelf broke. It's about 2 inches long, white plastic, clips onto a metal rail.",
                height=100)

            if describe and st.button("Help me fix this", type="primary"):
                with st.spinner("AX is thinking..."):
                    response = chat_with_ax(
                        f"I have something broken and need help fixing it. Here's what happened: {describe}\n\n"
                        f"Please help me with:\n"
                        f"1. What part this probably is\n"
                        f"2. Can I buy a replacement? What should I search for?\n"
                        f"3. Can it be 3D printed? What material?\n"
                        f"4. Can I glue/repair it? What adhesive?\n"
                        f"5. Links or search terms to find the part\n"
                        f"6. Estimated cost to fix"
                    )
                    st.markdown(response)

    # ── TAB 2: Ask AX ──
    with tab2:
        st.subheader("Ask AX")
        st.caption("Your repair assistant. Ask about fixing things, 3D printing, materials, tools — anything.")

        if "print_chat" not in st.session_state:
            st.session_state.print_chat = []

        # Starter suggestions
        if not st.session_state.print_chat:
            st.markdown("**Try asking:**")
            suggestions = [
                "What's the difference between PLA and PETG?",
                "How do I get started with 3D printing?",
                "What glue works best for plastic?",
                "How do I measure a broken part for a replacement?",
                "Where can I download free 3D printable parts?",
            ]
            cols = st.columns(len(suggestions))
            for i, s in enumerate(suggestions):
                with cols[i]:
                    if st.button(s, key=f"suggest_{i}"):
                        st.session_state.print_chat.append({"role": "user", "content": s})
                        st.rerun()

        for msg in st.session_state.print_chat:
            with st.chat_message(msg["role"], avatar="\U0001f916" if msg["role"]=="assistant" else "\U0001f9d1"):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask AX about repairs, printing, materials..."):
            st.session_state.print_chat.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="\U0001f9d1"):
                st.markdown(prompt)
            with st.chat_message("assistant", avatar="\U0001f916"):
                with st.spinner("AX is thinking..."):
                    resp = chat_with_ax(prompt, context=f"You're talking to {user_name}.", history=st.session_state.print_chat)
                    st.markdown(resp)
                    st.session_state.print_chat.append({"role": "assistant", "content": resp})

        if st.session_state.print_chat and st.button("Clear Chat"):
            st.session_state.print_chat = []
            st.rerun()

    # ── TAB 3: How to 3D Print ──
    with tab3:
        st.subheader("Getting Started with 3D Printing")
        st.markdown("""
        ### What You Need
        1. **A 3D printer** — Good starter options:
           - **Bambu Lab A1 Mini** (~$200) — easiest to use, great prints
           - **Creality Ender 3 V3** (~$200) — popular, lots of community support
           - **Prusa Mini+** (~$400) — reliable, great support

        2. **Filament** (the "ink" for your printer):
           - **PLA** — easiest, works for most household parts, $15-20/roll
           - **PETG** — stronger, heat resistant, good for functional parts
           - **TPU** — flexible, good for grips and gaskets

        3. **Slicer software** (free):
           - **Bambu Studio** — if you have a Bambu printer
           - **Cura** — works with most printers
           - **PrusaSlicer** — works with most printers

        ### How It Works
        1. **Find or create an STL file** — the 3D model
           - Search [Thingiverse](https://thingiverse.com) or [Printables](https://printables.com)
           - Or use this app to identify what you need
        2. **Open the STL in your slicer** — it converts 3D model to printer instructions
        3. **Send to printer** — via USB, WiFi, or SD card
        4. **Print** — takes 30 min to a few hours depending on size

        ### Tips for Replacement Parts
        - **Measure carefully** — use calipers ($10 on Amazon) for accuracy
        - **Print a test piece first** — check the fit before printing the final part
        - **Add 0.2-0.3mm tolerance** for parts that need to fit together
        - **PETG for functional parts** — it's stronger and more heat resistant than PLA
        - **100% infill** for small structural parts — makes them strongest

        ### Where to Find Free Replacement Parts
        - [Thingiverse](https://thingiverse.com) — largest library of free 3D models
        - [Printables](https://printables.com) — high quality, well-organized
        - [MyMiniFactory](https://myminifactory.com) — curated, tested prints
        - Search: "[broken part name] replacement STL" on Google
        """)

if __name__ == "__main__":
    main()
