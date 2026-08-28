import streamlit as st
import streamlit.components.v1 as components
import math
import json

# 1. Page Configuration MUST be first
st.set_page_config(page_title="Color Sphere - True Pigments", layout="wide")

st.markdown("""
    <style>
           .block-container { padding-top: 1rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem; }
    </style>
    """, unsafe_allow_html=True)

def hex_to_vectors(hex_str):
    hex_str = hex_str.lstrip('#')
    r, g, b = int(hex_str[0:2], 16)/255.0, int(hex_str[2:4], 16)/255.0, int(hex_str[4:6], 16)/255.0
    return f"vec3({r:.3f}, {g:.3f}, {b:.3f})", f"[{r:.3f}, {g:.3f}, {b:.3f}]"

# --- SESSION STATE INITIALIZATION ---
default_state = {
    "workspace_name": "Default Studio",
    "name_y_pos": "Red (PR202/PR254)", "yp_mass": "#B50027", "yp_mid": "#DB295B", "yp_wash": "#E39FBA",
    "name_x_pos": "Yellow (PY184)", "xp_mass": "#F2EF00", "xp_mid": "#F7F550", "xp_wash": "#FCFBA1",
    "name_z_pos": "Green (PG7/PY74)", "zp_mass": "#1B8724", "zp_mid": "#72C824", "zp_wash": "#B5E265",
    "name_y_neg": "Cyan (PB15/PG7)", "yn_mass": "#20415C", "yn_mid": "#3A7CA5", "yn_wash": "#6AB6CC",
    "name_x_neg": "Blue (PB15:2)", "xn_mass": "#1E154B", "xn_mid": "#1135A2", "xn_wash": "#8AB2D7",
    "name_z_neg": "Magenta (PR202)", "zn_mass": "#701B2E", "zn_mid": "#B80F62", "zn_wash": "#DD9BB9",
    "show_abyss": True, "name_abyss": "Indigo Abyss", "hex_abyss": "#080414",
    "show_core": True, "name_core": "Violet Core", "hex_core": "#59268C",
    "show_heat": True, "name_heat": "Orange Undercrust", "hex_heat": "#FF6600",
    "show_luma": True, "name_luma": "White Luma", "hex_luma": "#F2F2F2",
    "show_crust": True, "name_crust": "Umber Crust", "hex_crust": "#26140D",
    "show_grid": False, "brilliance": 1.4, "rot_x": 146, "rot_y": 315,
    
    # Planetary Strata Defaults
    "rad_abyss": 0.0, "fade_abyss": 0.4, "mix_abyss": 0.5,
    "rad_core": 0.2, "fade_core": 0.4, "mix_core": 0.5,
    "mass_start": 0.4, "mass_fade": 0.4,
    "wash_start": 1.2, "wash_fade": 0.4,
    "rad_luma": 1.4, "fade_luma": 0.4, "mix_luma": 0.5,
    "rad_heat": 1.6, "fade_heat": 0.39, "mix_heat": 0.5,
    "rad_crust": 1.8, "fade_crust": 0.4, "mix_crust": 0.5
}

for k, v in default_state.items():
    if k not in st.session_state:
        st.session_state[k] = v

# 2. Sidebar Controls
with st.sidebar:
    st.markdown("### Color Sphere Studio")
    
    with st.expander("📖 About & Guide", expanded=False):
        st.markdown("""
        **Welcome to the Color Sphere**
        This tool is a 3D digital laboratory for physical artists. It is designed to map the actual, physical behavior of paint and ink, moving far beyond simple digital hex codes.
        
        **How It Works:**
        * **The Living Pigment:** Physical paint acts as a gradient. It has a Mass Tone (thick), a Midtone (pure), and a Wash (diluted). You can input all three states for your 6 main anchor colors.
        * **The Planetary Strata:** The sphere is mapped like a planet. The radius spans from `0.0` (Absolute Center) to `2.0` (Outer Edge).
        * **The Atmosphere:** Real painting doesn't rely on digital flat black or pure white. The atmosphere layers (like the Indigo Abyss or the Umber Crust) provide complex, tinted depths and highlights without muddying your colors.
        
        Hover over the `(?)` icons next to any control for specific guidance on how to use it!
        """)

    with st.expander("💾 Save / Load Workspace", expanded=False):
        uploaded_file = st.file_uploader("Load Palette (.json)", type=["json"], key="json_uploader", help="Upload a previously saved workspace file.")
        if uploaded_file is not None:
            file_id = uploaded_file.name + str(uploaded_file.size)
            if "last_loaded_file" not in st.session_state or st.session_state["last_loaded_file"] != file_id:
                try:
                    data = json.load(uploaded_file)
                    for k in default_state.keys():
                        if k in data and k != "workspace_name":
                            st.session_state[k] = data[k]
                    st.session_state["workspace_name"] = uploaded_file.name
                    st.session_state["last_loaded_file"] = file_id
                    st.rerun() 
                except Exception as e:
                    st.error("Invalid workspace file.")

        export_data = {k: st.session_state[k] for k in default_state.keys() if k != "workspace_name"}
        st.download_button(label="Export Workspace to JSON", data=json.dumps(export_data, indent=4), file_name="my_color_sphere_workspace.json", mime="application/json", key="json_downloader", help="Download your current colors and slider settings to your computer.")
    
    with st.expander("🎨 6-Pole Anchor Pigments", expanded=True):
        st.markdown("*Input the hex codes for the 3 physical states of your paint.*")
        
        name_y_pos = st.text_input("Top (Y+)", key="name_y_pos", help="Name your top anchor pigment.")
        c1, c2, c3 = st.columns(3)
        yp_mass = c1.color_picker("Mass", key="yp_mass", help="The thickest, darkest application of the ink.")
        yp_mid = c2.color_picker("Mid", key="yp_mid", help="The pure, most vibrant state of the ink.")
        yp_wash = c3.color_picker("Wash", key="yp_wash", help="The highly diluted, transparent wash.")
        st.markdown("---")
        
        name_y_neg = st.text_input("Bottom (Y-)", key="name_y_neg")
        c1, c2, c3 = st.columns(3)
        yn_mass = c1.color_picker("Mass", key="yn_mass")
        yn_mid = c2.color_picker("Mid", key="yn_mid")
        yn_wash = c3.color_picker("Wash", key="yn_wash")
        st.markdown("---")
        
        name_x_pos = st.text_input("East (X+)", key="name_x_pos")
        c1, c2, c3 = st.columns(3)
        xp_mass = c1.color_picker("Mass", key="xp_mass")
        xp_mid = c2.color_picker("Mid", key="xp_mid")
        xp_wash = c3.color_picker("Wash", key="xp_wash")
        st.markdown("---")
        
        name_x_neg = st.text_input("West (X-)", key="name_x_neg")
        c1, c2, c3 = st.columns(3)
        xn_mass = c1.color_picker("Mass", key="xn_mass")
        xn_mid = c2.color_picker("Mid", key="xn_mid")
        xn_wash = c3.color_picker("Wash", key="xn_wash")
        st.markdown("---")
        
        name_z_pos = st.text_input("Front (Z+)", key="name_z_pos")
        c1, c2, c3 = st.columns(3)
        zp_mass = c1.color_picker("Mass", key="zp_mass")
        zp_mid = c2.color_picker("Mid", key="zp_mid")
        zp_wash = c3.color_picker("Wash", key="zp_wash")
        st.markdown("---")
        
        name_z_neg = st.text_input("Back (Z-)", key="name_z_neg")
        c1, c2, c3 = st.columns(3)
        zn_mass = c1.color_picker("Mass", key="zn_mass")
        zn_mid = c2.color_picker("Mid", key="zn_mid")
        zn_wash = c3.color_picker("Wash", key="zn_wash")

    with st.expander("🌫️ Atmosphere Toggles", expanded=False):
        st.markdown("*Toggle and define the deep shadow and bright highlight layers.*")
        col3, col4 = st.columns(2)
        with col3:
            show_abyss = st.toggle("Enable Abyss", key="show_abyss", help="The absolute darkest core point.")
            name_abyss = st.text_input("Abyss Name", key="name_abyss")
            hex_abyss = st.color_picker("Abyss Color", key="hex_abyss")
            show_core = st.toggle("Enable Core", key="show_core", help="The shadow transition layer.")
            name_core = st.text_input("Core Name", key="name_core")
            hex_core = st.color_picker("Core Color", key="hex_core")
            show_heat = st.toggle("Enable Undercrust", key="show_heat", help="The glowing warmth just below the surface.")
            name_heat = st.text_input("Undercrust Name", key="name_heat")
            hex_heat = st.color_picker("Undercrust Color", key="hex_heat")
        with col4:
            show_luma = st.toggle("Enable Luma", key="show_luma", help="The paper white highlight transition.")
            name_luma = st.text_input("Luma Name", key="name_luma")
            hex_luma = st.color_picker("Luma Color", key="hex_luma")
            show_crust = st.toggle("Enable Crust", key="show_crust", help="The dark, earthy outer shell.")
            name_crust = st.text_input("Crust Name", key="name_crust")
            hex_crust = st.color_picker("Crust Color", key="hex_crust")

    with st.expander("🎛️ Planetary Strata (Boundaries & Fades)", expanded=False):
        st.markdown("*Geologic sizing. Radius spans from 0.0 (Center) to 2.0 (Outer Edge).*")
        show_grid = st.toggle("Show Wireframe Grid", key="show_grid")
        brilliance = st.slider("Color Overlap Brilliance", 0.2, 5.0, key="brilliance", step=0.01, help="Lower = muddy, blurry blends. Higher = sharper, more distinct poles.")
        
        st.markdown("### 🌑 Inner Core (Expanding Outward)")
        if show_abyss:
            st.markdown(f"**{name_abyss}**")
            c1, c2, c3 = st.columns(3)
            rad_abyss = c1.slider("Boundary", 0.0, 2.0, key="rad_abyss", step=0.01, help="The specific point where this layer stops.")
            fade_abyss = c2.slider("Fade", 0.0, 2.0, key="fade_abyss", step=0.01, help="How softly it bleeds into the next layer.")
            mix_abyss = c3.slider("Midtone Mix", 0.0, 1.0, key="mix_abyss", step=0.01, help="0.0 = Pure Midtone color. 1.0 = Pure Abyss color.")
        if show_core:
            st.markdown(f"**{name_core}**")
            c1, c2, c3 = st.columns(3)
            rad_core = c1.slider("Boundary", 0.0, 2.0, key="rad_core", step=0.01, help="The specific point where this layer stops.")
            fade_core = c2.slider("Fade", 0.0, 2.0, key="fade_core", step=0.01, help="How softly it bleeds into the next layer.")
            mix_core = c3.slider("Midtone Mix", 0.0, 1.0, key="mix_core", step=0.01, help="0.0 = Pure Midtone color. 1.0 = Pure Core color.")
            
        st.markdown("### 🎨 Pigment Mantle (The Paint)")
        st.markdown("**Mass Transition (Fading to Midtone)**")
        c1, c2 = st.columns(2)
        mass_start = c1.slider("Mass Start Point", 0.0, 2.0, key="mass_start", step=0.01, help="Radius where the pure Mass Tone begins to fade out.")
        mass_fade = c2.slider("Mass Fade Range", 0.0, 2.0, key="mass_fade", step=0.01, help="Distance required to fade completely into the Midtone.")
        st.markdown("**Wash Transition (Midtone fading to Wash)**")
        c3, c4 = st.columns(2)
        wash_start = c3.slider("Wash Start Point", 0.0, 2.0, key="wash_start", step=0.01, help="Radius where the Midtone begins to fade into the Wash.")
        wash_fade = c4.slider("Wash Fade Range", 0.0, 2.0, key="wash_fade", step=0.01, help="Distance required to fade completely into the Wash.")

        st.markdown("### 🌍 Outer Crust (Expanding Inward)")
        if show_luma:
            st.markdown(f"**{name_luma}**")
            c1, c2, c3 = st.columns(3)
            rad_luma = c1.slider("Boundary", 0.0, 2.0, key="rad_luma", step=0.01, help="The specific point where this layer starts.")
            fade_luma = c2.slider("Fade", 0.0, 2.0, key="fade_luma", step=0.01, help="How softly it bleeds into the previous layer.")
            mix_luma = c3.slider("Midtone Mix", 0.0, 1.0, key="mix_luma", step=0.01, help="0.0 = Pure Midtone color. 1.0 = Pure Luma color.")
        if show_heat:
            st.markdown(f"**{name_heat}**")
            c1, c2, c3 = st.columns(3)
            rad_heat = c1.slider("Boundary", 0.0, 2.0, key="rad_heat", step=0.01, help="The specific point where this layer starts.")
            fade_heat = c2.slider("Fade", 0.0, 2.0, key="fade_heat", step=0.01, help="How softly it bleeds into the previous layer.")
            mix_heat = c3.slider("Midtone Mix", 0.0, 1.0, key="mix_heat", step=0.01, help="0.0 = Pure Midtone color. 1.0 = Pure Heat color.")
        if show_crust:
            st.markdown(f"**{name_crust}**")
            c1, c2, c3 = st.columns(3)
            rad_crust = c1.slider("Boundary", 0.0, 2.0, key="rad_crust", step=0.01, help="The specific point where this layer starts.")
            fade_crust = c2.slider("Fade", 0.0, 2.0, key="fade_crust", step=0.01, help="How softly it bleeds into the previous layer.")
            mix_crust = c3.slider("Midtone Mix", 0.0, 1.0, key="mix_crust", step=0.01, help="0.0 = Pure Midtone color. 1.0 = Pure Crust color.")
    
    with st.expander("🔄 Rotation Math", expanded=False):
        rot_x = st.slider("Rotate Latitude", 0, 360, key="rot_x", step=1, help="Spin the sphere vertically.")
        rot_y = st.slider("Rotate Longitude", 0, 360, key="rot_y", step=1, help="Spin the sphere horizontally.")

# Pre-calculate all 18 anchor vectors
gl_yp_ma, js_yp_ma = hex_to_vectors(yp_mass); gl_yp_mi, js_yp_mi = hex_to_vectors(yp_mid); gl_yp_wa, js_yp_wa = hex_to_vectors(yp_wash)
gl_yn_ma, js_yn_ma = hex_to_vectors(yn_mass); gl_yn_mi, js_yn_mi = hex_to_vectors(yn_mid); gl_yn_wa, js_yn_wa = hex_to_vectors(yn_wash)
gl_xp_ma, js_xp_ma = hex_to_vectors(xp_mass); gl_xp_mi, js_xp_mi = hex_to_vectors(xp_mid); gl_xp_wa, js_xp_wa = hex_to_vectors(xp_wash)
gl_xn_ma, js_xn_ma = hex_to_vectors(xn_mass); gl_xn_mi, js_xn_mi = hex_to_vectors(xn_mid); gl_xn_wa, js_xn_wa = hex_to_vectors(xn_wash)
gl_zp_ma, js_zp_ma = hex_to_vectors(zp_mass); gl_zp_mi, js_zp_mi = hex_to_vectors(zp_mid); gl_zp_wa, js_zp_wa = hex_to_vectors(zp_wash)
gl_zn_ma, js_zn_ma = hex_to_vectors(zn_mass); gl_zn_mi, js_zn_mi = hex_to_vectors(zn_mid); gl_zn_wa, js_zn_wa = hex_to_vectors(zn_wash)

gl_abyss, js_abyss = hex_to_vectors(hex_abyss)
gl_core, js_core = hex_to_vectors(hex_core)
gl_luma, js_luma = hex_to_vectors(hex_luma)
gl_heat, js_heat = hex_to_vectors(hex_heat)
gl_crust, js_crust = hex_to_vectors(hex_crust)

rad_x = rot_x * (math.pi / 180)
rad_y = rot_y * (math.pi / 180)

r_ab, f_ab = (rad_abyss, fade_abyss) if show_abyss else (0.0, 0.0)
r_co, f_co = (rad_core, fade_core) if show_core else (0.0, 0.0)
r_lu, f_lu = (rad_luma, fade_luma) if show_luma else (0.0, 0.0)
r_he, f_he = (rad_heat, fade_heat) if show_heat else (0.0, 0.0)
r_cr, f_cr = (rad_crust, fade_crust) if show_crust else (0.0, 0.0)

mix_ab = st.session_state["mix_abyss"] if show_abyss else 0.0
mix_co = st.session_state["mix_core"] if show_core else 0.0
mix_lu = st.session_state["mix_luma"] if show_luma else 0.0
mix_he = st.session_state["mix_heat"] if show_heat else 0.0
mix_cr = st.session_state["mix_crust"] if show_crust else 0.0

workspace_name = st.session_state["workspace_name"]

# 3. The WebGL Engine 
three_js_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #0e1117; cursor: crosshair; user-select: none; touch-action: none; overscroll-behavior: none; }}
        body:active {{ cursor: grabbing; }}
        canvas {{ display: block; }}
        #hud {{ position: absolute; top: 20px; right: 20px; color: #e0e0e0; font-family: monospace; font-size: 13px; background: rgba(15, 17, 23, 0.9); border-radius: 8px; pointer-events: auto; border: 2px solid rgba(255, 255, 255, 0.15); width: 280px; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); z-index: 100; }}
        #hud-header {{ background: rgba(255, 255, 255, 0.1); padding: 8px 12px; cursor: move; display: flex; justify-content: space-between; align-items: center; border-radius: 6px 6px 0 0; }}
        #hud-header span {{ font-weight: bold; font-size: 12px; pointer-events: none; }}
        #hud-toggle {{ cursor: pointer; padding: 2px 8px; background: rgba(255,255,255,0.2); border-radius: 4px; pointer-events: auto; font-size: 14px; font-weight: bold; display: inline-block; }}
        #hud-content {{ padding: 15px; max-height: 80vh; overflow-y: auto; }}
        .hud-section {{ margin-top: 5px; margin-bottom: 5px; color: #fff; font-weight: bold; border-bottom: 1px solid #444; padding-bottom: 3px; }}
        .row {{ display: flex; justify-content: space-between; margin-bottom: 2px; }}
        
        #workspace-label {{ text-align: center; color: #5bc0de; font-weight: bold; font-size: 11px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }}
        #swatch {{ width: 100%; height: 30px; border-radius: 4px; border: 1px solid #555; margin-bottom: 5px; background-color: #000; }}
        #hex-code {{ text-align: center; font-weight: bold; letter-spacing: 2px; margin-bottom: 2px; color: #fff; font-size: 16px; }}
        #live-coords {{ text-align: center; color: #aaa; font-weight: bold; font-size: 11px; letter-spacing: 1px; margin-bottom: 10px; }}
        #freeze-status {{ text-align: center; color: gold; font-weight: bold; font-size: 11px; margin-bottom: 10px; display: none; }}
        
        #add-batch-btn {{ display: none; width: 100%; padding: 8px; margin-top: 15px; background: #5bc0de; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }}
        #add-batch-btn:hover {{ background: #31b0d5; }}
        #export-batch-btn {{ display: none; width: 100%; padding: 8px; margin-top: 8px; background: #5cb85c; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }}
        #export-batch-btn:hover {{ background: #4cae4c; }}
        #unlock-btn {{ display: none; width: 100%; padding: 8px; margin-top: 8px; background: #d9534f; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }}
        #unlock-btn:hover {{ background: #c9302c; }}
        
        #helper-text {{ position: absolute; bottom: 20px; left: 20px; color: rgba(255,255,255,0.4); font-family: sans-serif; font-size: 12px; pointer-events: none; white-space: pre-line; }}
    </style>
</head>
<body>
    <div id="hud">
        <div id="hud-header"><span style="pointer-events:none;">DATA HUD</span><div id="hud-toggle">–</div></div>
        <div id="hud-content">
            <div id="workspace-label">📦 {workspace_name}</div>
            <div id="freeze-status">[ TARGET LOCKED ]</div>
            
            <div id="swatch"></div>
            <div id="hex-code">#000000</div>
            <div id="live-coords">LAT 0° &nbsp;|&nbsp; LON 0°<br><span style="color:#888; font-size:10px;">X: 0.00 &nbsp;|&nbsp; Y: 0.00</span></div>
            
            <div id="pie-container" style="display: none;">
                <div id="pie-chart-circle" style="width: 140px; height: 140px; border-radius: 50%; margin: 15px auto;"></div>
                <div class="hud-section">Active Mix Recipe</div>
                <div id="pie-legend"></div>
            </div>

            <div class="hud-section">Application Weight</div>
            <div class="row"><span>Heavy Weight (Mass)</span><span id="ld-mass">0%</span></div>
            <div class="row"><span>Normal Weight (Mid)</span><span id="ld-mid">0%</span></div>
            <div class="row"><span>Light Weight (Wash)</span><span id="ld-wash">0%</span></div>

            <div id="standard-lists">
                <div class="hud-section">Pole Coordinates</div>
                <div class="row"><span>{name_y_pos} (Y+)</span><span id="p-yp">0%</span></div>
                <div class="row"><span>{name_y_neg} (Y-)</span><span id="p-yn">0%</span></div>
                <div class="row"><span>{name_x_pos} (X+)</span><span id="p-xp">0%</span></div>
                <div class="row"><span>{name_x_neg} (X-)</span><span id="p-xn">0%</span></div>
                <div class="row"><span>{name_z_pos} (Z+)</span><span id="p-zp">0%</span></div>
                <div class="row"><span>{name_z_neg} (Z-)</span><span id="p-zn">0%</span></div>
                
                <div class="hud-section">Atmosphere Addition</div>
                <div class="row" style="display: {'flex' if show_abyss else 'none'};"><span>{name_abyss}</span><span id="z-abyss">0%</span></div>
                <div class="row" style="display: {'flex' if show_core else 'none'};"><span>{name_core}</span><span id="z-core">0%</span></div>
                <div class="row" style="display: {'flex' if show_luma else 'none'};"><span>{name_luma}</span><span id="z-luma">0%</span></div>
                <div class="row" style="display: {'flex' if show_heat else 'none'};"><span>{name_heat}</span><span id="z-heat">0%</span></div>
                <div class="row" style="display: {'flex' if show_crust else 'none'};"><span>{name_crust}</span><span id="z-crust">0%</span></div>
            </div>
            
            <button id="add-batch-btn">ADD TO BATCH (<span id="batch-count">0</span>)</button>
            <button id="export-batch-btn">EXPORT BATCH HTML</button>
            <button id="unlock-btn">UNLOCK TARGET</button>
        </div>
    </div>
    <div id="helper-text">Left-Click: Rotate | Right-Click: Pan | Scroll: Zoom</div>
    <script>
        document.addEventListener('contextmenu', e => e.preventDefault());
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        const customUniforms = {{
            uBrilliance: {{ value: {brilliance} }}, uRotX: {{ value: {rad_x} }}, uRotY: {{ value: {rad_y} }},
            uMassStart: {{ value: {mass_start} }}, uMassFade: {{ value: {mass_fade} }},
            uWashStart: {{ value: {wash_start} }}, uWashFade: {{ value: {wash_fade} }},
            uAbRad: {{ value: {r_ab} }}, uAbFade: {{ value: {f_ab} }}, uAbMix: {{ value: {mix_ab} }},
            uCoRad: {{ value: {r_co} }}, uCoFade: {{ value: {f_co} }}, uCoMix: {{ value: {mix_co} }},
            uLuRad: {{ value: {r_lu} }}, uLuFade: {{ value: {f_lu} }}, uLuMix: {{ value: {mix_lu} }},
            uHeRad: {{ value: {r_he} }}, uHeFade: {{ value: {f_he} }}, uHeMix: {{ value: {mix_he} }},
            uCrRad: {{ value: {r_cr} }}, uCrFade: {{ value: {f_cr} }}, uCrMix: {{ value: {mix_cr} }}
        }};

        const material = new THREE.ShaderMaterial({{
            side: THREE.DoubleSide, uniforms: customUniforms,
            vertexShader: `varying vec3 vPos; void main() {{ vec4 wp = modelMatrix * vec4(position, 1.0); vPos = wp.xyz; gl_Position = projectionMatrix * viewMatrix * wp; }}`,
            fragmentShader: `
                uniform float uBrilliance, uRotX, uRotY; 
                uniform float uMassStart, uMassFade, uWashStart, uWashFade;
                uniform float uAbRad, uAbFade, uAbMix, uCoRad, uCoFade, uCoMix;
                uniform float uLuRad, uLuFade, uLuMix, uHeRad, uHeFade, uHeMix, uCrRad, uCrFade, uCrMix;
                varying vec3 vPos;
                mat3 rx(float a) {{ float s=sin(a), c=cos(a); return mat3(1.,0.,0.,0.,c,-s,0.,s,c); }}
                mat3 ry(float a) {{ float s=sin(a), c=cos(a); return mat3(c,0.,s,0.,1.,0.,-s,0.,c); }}
                
                void main() {{
                    if(vPos.x > 0.001 && vPos.y > 0.001 && vPos.z > 0.001) discard;
                    float r = length(vPos); vec3 n = normalize(rx(uRotX) * ry(uRotY) * vPos);
                    
                    float wX = pow(abs(n.x), uBrilliance), wY = pow(abs(n.y), uBrilliance), wZ = pow(abs(n.z), uBrilliance);
                    float tot = wX + wY + wZ; 
                    
                    vec3 cY_ma = n.y > 0. ? {gl_yp_ma} : {gl_yn_ma}; vec3 cX_ma = n.x > 0. ? {gl_xp_ma} : {gl_xn_ma}; vec3 cZ_ma = n.z > 0. ? {gl_zp_ma} : {gl_zn_ma};
                    vec3 pC_ma = cX_ma*(wX/tot) + cY_ma*(wY/tot) + cZ_ma*(wZ/tot);
                    
                    vec3 cY_mi = n.y > 0. ? {gl_yp_mi} : {gl_yn_mi}; vec3 cX_mi = n.x > 0. ? {gl_xp_mi} : {gl_xn_mi}; vec3 cZ_mi = n.z > 0. ? {gl_zp_mi} : {gl_zn_mi};
                    vec3 pC_mi = cX_mi*(wX/tot) + cY_mi*(wY/tot) + cZ_mi*(wZ/tot);
                    
                    vec3 cY_wa = n.y > 0. ? {gl_yp_wa} : {gl_yn_wa}; vec3 cX_wa = n.x > 0. ? {gl_xp_wa} : {gl_xn_wa}; vec3 cZ_wa = n.z > 0. ? {gl_zp_wa} : {gl_zn_wa};
                    vec3 pC_wa = cX_wa*(wX/tot) + cY_wa*(wY/tot) + cZ_wa*(wZ/tot);
                    
                    float mix1 = smoothstep(uMassStart, uMassStart + uMassFade + 0.0001, r);
                    float mix2 = smoothstep(uWashStart, uWashStart + uWashFade + 0.0001, r);
                    
                    vec3 c_mass_to_mid = mix(pC_ma, pC_mi, mix1);
                    vec3 pC_pure = mix(c_mass_to_mid, pC_wa, mix2);
                    
                    float vAb = {1 if show_abyss else 0}==1 ? 1.0 - smoothstep(uAbRad, uAbRad + uAbFade + 0.0001, r) : 0.0;
                    float vCo = {1 if show_core else 0}==1 ? 1.0 - smoothstep(uCoRad, uCoRad + uCoFade + 0.0001, r) : 0.0;
                    float vLu = {1 if show_luma else 0}==1 ? smoothstep(uLuRad, uLuRad + uLuFade + 0.0001, r) : 0.0;
                    float vHe = {1 if show_heat else 0}==1 ? smoothstep(uHeRad, uHeRad + uHeFade + 0.0001, r) : 0.0;
                    float vCr = {1 if show_crust else 0}==1 ? smoothstep(uCrRad, uCrRad + uCrFade + 0.0001, r) : 0.0;
                    
                    vec3 fC = pC_pure; 
                    
                    fC = mix(fC, mix(pC_mi, {gl_core}, uCoMix), vCo); 
                    fC = mix(fC, mix(pC_mi, {gl_abyss}, uAbMix), vAb); 
                    fC = mix(fC, mix(pC_mi, {gl_luma}, uLuMix), vLu); 
                    fC = mix(fC, mix(pC_mi, {gl_heat}, uHeMix), vHe); 
                    fC = mix(fC, mix(pC_mi, {gl_crust}, uCrMix), vCr); 
                    
                    gl_FragColor = vec4(fC, 1.0);
                }}`
        }});

        const group = new THREE.Group();
        const sphereGeo = new THREE.SphereGeometry(2, 64, 64);
        group.add(new THREE.Mesh(sphereGeo, material));

        if ({"true" if show_grid else "false"}) {{
            group.add(new THREE.Mesh(sphereGeo, new THREE.MeshBasicMaterial({{color:0xffffff, wireframe:true, transparent:true, opacity:0.15}})));
        }}

        const wallGeo = new THREE.CircleGeometry(2, 32, 0, Math.PI / 2);
        const w1 = new THREE.Mesh(wallGeo, material); const w2 = new THREE.Mesh(wallGeo, material); w2.rotation.y = -Math.PI / 2;
        const w3 = new THREE.Mesh(wallGeo, material); w3.rotation.x = Math.PI / 2;
        group.add(w1); group.add(w2); group.add(w3); scene.add(group);

        let curZoom = 6.0, panT = new THREE.Vector3(0,0,0);
        function updCam() {{ curZoom = Math.max(2.5, Math.min(25., curZoom)); let cV = curZoom/Math.sqrt(3); camera.position.set(cV+panT.x, cV+panT.y, cV+panT.z); camera.lookAt(panT); }}
        updCam();

        const raycaster = new THREE.Raycaster(), mouse = new THREE.Vector2();
        function sstep(min, max, val) {{ let x = Math.max(0, Math.min(1, (val-min)/(max-min))); return x*x*(3-2*x); }}
        function mVec(v1, v2, a) {{ return [v1[0]*(1-a)+v2[0]*a, v1[1]*(1-a)+v2[1]*a, v1[2]*(1-a)+v2[2]*a]; }}
        const tHex = (c) => c.toString(16).padStart(2,'0').toUpperCase();
        
        let isDrag=false, isPan=false, isFroz=false, lastMouse={{x:0,y:0}}, iDist=null, lMid={{x:0,y:0}}, hDrag=false, hOx=0, hOy=0;
        let colorCart = []; 
        let currentX = "0.00", currentY = "0.00"; // Store exact physical mouse X/Y tracking
        let workspaceName = "{workspace_name}";
        
        const hud=document.getElementById('hud'), hHead=document.getElementById('hud-header'), hCont=document.getElementById('hud-content'), hTog=document.getElementById('hud-toggle');
        
        hTog.addEventListener('pointerdown', (e) => {{
            e.stopPropagation();
            hCont.style.display = hCont.style.display === 'none' ? 'block' : 'none';
            hTog.innerText = hCont.style.display === 'none' ? '+' : '–';
        }});
        
        const stDrag = (e) => {{ if(e.target.id==='hud-toggle') return; hDrag=true; let evt=e.touches?e.touches[0]:e; hOx=evt.clientX-hud.offsetLeft; hOy=evt.clientY-hud.offsetTop; }};
        hHead.addEventListener('mousedown', stDrag); hHead.addEventListener('touchstart', stDrag, {{passive:true}});
        const endAll = () => {{ hDrag=isDrag=isPan=false; iDist=null; }};
        window.addEventListener('mouseup', endAll); window.addEventListener('mouseleave', endAll); window.addEventListener('touchend', endAll);
        const doMove = (e) => {{ if(!hDrag) return; let evt=e.touches?e.touches[0]:e; hud.style.left=(evt.clientX-hOx)+'px'; hud.style.top=(evt.clientY-hOy)+'px'; hud.style.right='auto'; }};
        window.addEventListener('mousemove', doMove); window.addEventListener('touchmove', doMove, {{passive:true}});

        // --- THE HARD LOCK MECHANISM ---
        function lockHud() {{ 
            if(isFroz) return; 
            isFroz = true; 
            hud.style.borderColor = 'gold'; 
            document.getElementById('freeze-status').style.display = 'block'; 
            document.getElementById('add-batch-btn').style.display = 'block'; 
            document.getElementById('export-batch-btn').style.display = 'block'; 
            document.getElementById('unlock-btn').style.display = 'block'; 
            document.getElementById('pie-container').style.display = 'block';
            document.getElementById('standard-lists').style.display = 'none';
        }}
        
        function unlockHud() {{
            isFroz = false;
            hud.style.borderColor = 'rgba(255,255,255,0.15)'; 
            document.getElementById('freeze-status').style.display = 'none'; 
            document.getElementById('add-batch-btn').style.display = 'none'; 
            document.getElementById('export-batch-btn').style.display = 'none'; 
            document.getElementById('unlock-btn').style.display = 'none'; 
            document.getElementById('pie-container').style.display = 'none';
            document.getElementById('standard-lists').style.display = 'block';
        }}

        // Listeners for Locking/Unlocking
        document.getElementById('unlock-btn').addEventListener('click', unlockHud);
        document.addEventListener('dblclick', (e) => {{ if(!e.target.closest('#hud')) lockHud(); }});
        let lTap=0; document.addEventListener('touchend', (e) => {{ if(e.target.closest('#hud')||hDrag) return; let t=new Date().getTime(); if(t-lTap<400 && t-lTap>0) lockHud(); lTap=t; }});
        
        // --- ADD TO BATCH LOGIC ---
        document.getElementById('add-batch-btn').addEventListener('click', () => {{
            let currentHex = document.getElementById('hex-code').innerText;
            let recipe = document.getElementById('pie-legend').innerHTML;
            let pieSvg = document.getElementById('pie-chart-circle').innerHTML;
            let weightMass = document.getElementById('ld-mass').innerText;
            let weightMid = document.getElementById('ld-mid').innerText;
            let weightWash = document.getElementById('ld-wash').innerText;
            
            let dX = Math.round((customUniforms.uRotX.value*180/Math.PI)%360); if(dX<0) dX+=360;
            let dY = Math.round((customUniforms.uRotY.value*180/Math.PI)%360); if(dY<0) dY+=360;
            
            colorCart.push({{
                hex: currentHex,
                recipe: recipe,
                pieSvg: pieSvg,
                wMass: weightMass,
                wMid: weightMid,
                wWash: weightWash,
                lat: dX,
                lon: dY,
                tX: currentX,
                tY: currentY
            }});
            
            let btn = document.getElementById('add-batch-btn');
            btn.innerText = "ADDED!";
            btn.style.background = "#4CAF50";
            setTimeout(() => {{
                btn.innerHTML = `ADD TO BATCH (<span id="batch-count">${{colorCart.length}}</span>)`;
                btn.style.background = "#5bc0de";
            }}, 800);
        }});

        // --- EXPORT BATCH LOGIC ---
        document.getElementById('export-batch-btn').addEventListener('click', () => {{
            if(colorCart.length === 0) {{
                alert("Your batch is empty! Click 'ADD TO BATCH' first to save a color.");
                return;
            }}
            
            let htmlStr = `<!DOCTYPE html>
<html>
<head>
    <title>Color Sphere Batch Export</title>
    <style>
        body {{ 
            font-family: system-ui, sans-serif; 
            background: #f4f4f9; 
            padding: 40px; 
            color: #333; 
            -webkit-print-color-adjust: exact !important; 
            print-color-adjust: exact !important; 
        }}
        .card {{ background: white; border-radius: 12px; padding: 20px; margin-bottom: 25px; display: flex; gap: 30px; align-items: stretch; box-shadow: 0 4px 10px rgba(0,0,0,0.05); page-break-inside: avoid; break-inside: avoid; }}
        
        .swatch-group {{ display: flex; gap: 15px; align-items: center; border-right: 2px solid #f0f0f0; padding-right: 20px; }}
        .swatch-col {{ text-align: center; display: flex; flex-direction: column; align-items: center; }}
        
        .swatch, .empty-box {{ width: 120px; height: 120px; border-radius: 12px; }}
        .swatch {{ box-shadow: inset 0 0 0 1px rgba(0,0,0,0.1); }}
        .empty-box {{ background: white; border: 2px dashed #bbb; }}
        
        .hex {{ font-weight: bold; font-size: 1.1rem; margin-top: 10px; letter-spacing: 1px; color: #555; }}
        
        .pie-container {{ display: flex; align-items: center; padding: 0 15px; border-right: 2px solid #f0f0f0; }}
        .pie {{ width: 100px; height: 100px; border-radius: 50%; overflow: hidden; border: 1px solid rgba(0,0,0,0.1); flex-shrink: 0; background: white; }}
        
        .recipe-col {{ flex-grow: 1; display: flex; flex-direction: column; justify-content: center; }}
        .coords {{ font-size: 0.9rem; color: #888; margin-bottom: 5px; font-weight: bold; letter-spacing: 0.5px; text-transform: uppercase; }}
        .recipe-row {{ display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px solid #eee; font-size: 1rem; }}
        .weights {{ display: flex; gap: 15px; margin-top: 15px; font-size: 0.9rem; color: #666; font-weight: bold; }}
        .w-box {{ background: #eee; padding: 6px 12px; border-radius: 6px; }}
        
        @media print {{
            body {{ padding: 10px; background: white; }}
            .card {{ padding: 15px; margin-bottom: 20px; border: 1px solid #ccc; box-shadow: none; gap: 15px; }}
            .swatch-group {{ padding-right: 15px; }}
            .pie-container {{ padding: 0 10px; }}
            .swatch, .empty-box {{ width: 100px; height: 100px; }}
            .pie {{ width: 80px; height: 80px; border: none; }}
            .hex {{ font-size: 1rem; }}
            h1 {{ font-size: 1.3rem; margin-top: 0; }}
            .weights {{ font-size: 0.8rem; gap: 10px; flex-wrap: wrap; }}
        }}
    </style>
</head>
<body>
    <h1>My Custom Color Recipe Workbook</h1>
    <p style="color: #666; margin-top: -15px; margin-bottom: 30px; font-weight: bold;">📦 Workspace: ${{workspaceName}}</p>`;

            colorCart.forEach(item => {{
                htmlStr += `
                <div class="card">
                    <div class="swatch-group">
                        <div class="swatch-col">
                            <div class="swatch" style="background-color: ${{item.hex}};"></div>
                            <div class="hex">${{item.hex}}</div>
                        </div>
                        <div class="swatch-col">
                            <div class="empty-box"></div>
                            <div class="hex" style="color: #aaa; font-weight: normal; font-size: 0.9rem;">Physical Match</div>
                        </div>
                    </div>
                    
                    <div class="pie-container">
                        <div class="pie">${{item.pieSvg}}</div>
                    </div>
                    
                    <div class="recipe-col">
                        <div class="coords">📍 Lat ${{item.lat}}°, Lon ${{item.lon}}° &nbsp;|&nbsp; 🎯 Target X: ${{item.tX}}, Y: ${{item.tY}}</div>
                        <h3 style="margin-top:0; margin-bottom: 10px;">Active Recipe</h3>
                        <div style="max-width: 350px;">
                            ${{item.recipe.replace(/class="row"/g, 'class="recipe-row"')}}
                        </div>
                        <div class="weights">
                            <div class="w-box">Heavy Weight: ${{item.wMass}}</div>
                            <div class="w-box">Normal: ${{item.wMid}}</div>
                            <div class="w-box">Light: ${{item.wWash}}</div>
                        </div>
                    </div>
                </div>`;
            }});

            htmlStr += `</body></html>`;
            
            const a = document.createElement('a'); 
            a.href = window.URL.createObjectURL(new Blob([htmlStr], {{type:'text/html'}}));
            a.download = 'Color_Workbook_Export.html'; 
            a.click();
        }});

        function processRay(cX, cY) {{
            if(isFroz) return; mouse.x=(cX/window.innerWidth)*2-1; mouse.y=-(cY/window.innerHeight)*2+1; raycaster.setFromCamera(mouse, camera);
            const ints = raycaster.intersectObjects(group.children.filter(c => !c.material.wireframe));
            let hPt = null; for(let i=0; i<ints.length; i++) {{ if(ints[i].point.x>0.001 && ints[i].point.y>0.001 && ints[i].point.z>0.001) continue; hPt=ints[i].point; break; }}
            
            if(hPt) {{
                currentX = hPt.x.toFixed(2);
                currentY = hPt.y.toFixed(2);
                
                let r = Math.sqrt(hPt.x*hPt.x + hPt.y*hPt.y + hPt.z*hPt.z);
                let cx=Math.cos(customUniforms.uRotX.value), sx=Math.sin(customUniforms.uRotX.value), cy=Math.cos(customUniforms.uRotY.value), sy=Math.sin(customUniforms.uRotY.value);
                let spX=cy*hPt.x-sy*hPt.z, spY=hPt.y, spZ=sy*hPt.x+cy*hPt.z;
                let sP = {{ x:spX, y:cx*spY+sx*spZ, z:-sx*spY+cx*spZ }};
                let l = Math.sqrt(sP.x*sP.x+sP.y*sP.y+sP.z*sP.z); let n = {{ x:sP.x/l, y:sP.y/l, z:sP.z/l }};

                let wX=Math.pow(Math.abs(n.x),{brilliance}), wY=Math.pow(Math.abs(n.y),{brilliance}), wZ=Math.pow(Math.abs(n.z),{brilliance});
                let tot=wX+wY+wZ; wX/=tot; wY/=tot; wZ/=tot;
                let pr=(n.y>0?wY*100:0).toFixed(1), pc=(n.y<=0?wY*100:0).toFixed(1), py=(n.x>0?wX*100:0).toFixed(1), pb=(n.x<=0?wX*100:0).toFixed(1), pg=(n.z>0?wZ*100:0).toFixed(1), pm=(n.z<=0?wZ*100:0).toFixed(1);

                let dX=(customUniforms.uRotX.value*180/Math.PI)%360, dY=(customUniforms.uRotY.value*180/Math.PI)%360; if(dX<0) dX+=360; if(dY<0) dY+=360;
                
                document.getElementById('live-coords').innerHTML = `LAT ${{Math.round(dX)}}° \u00A0|\u00A0 LON ${{Math.round(dY)}}°<br><span style="color:#888; font-size:10px;">X: ${{currentX}} \u00A0|\u00A0 Y: ${{currentY}}</span>`;

                document.getElementById('p-yp').innerText=pr+'%'; document.getElementById('p-yn').innerText=pc+'%';
                document.getElementById('p-xp').innerText=py+'%'; document.getElementById('p-xn').innerText=pb+'%';
                document.getElementById('p-zp').innerText=pg+'%'; document.getElementById('p-zn').innerText=pm+'%';
                
                let vAb = {1 if show_abyss else 0}===1 ? 1.0 - sstep({r_ab}, {r_ab}+{f_ab}+0.0001, r) : 0.0;
                let vCo = {1 if show_core else 0}===1 ? 1.0 - sstep({r_co}, {r_co}+{f_co}+0.0001, r) : 0.0;
                let vLu = {1 if show_luma else 0}===1 ? sstep({r_lu}, {r_lu}+{f_lu}+0.0001, r) : 0.0;
                let vHe = {1 if show_heat else 0}===1 ? sstep({r_he}, {r_he}+{f_he}+0.0001, r) : 0.0;
                let vCr = {1 if show_crust else 0}===1 ? sstep({r_cr}, {r_cr}+{f_cr}+0.0001, r) : 0.0;

                let zA = vAb; let zC = vCo * (1.0 - vAb); let zCr = vCr; let zH = vHe * (1.0 - vCr); let zL = vLu * (1.0 - vHe) * (1.0 - vCr);
                let zAtmos = zA + zC + zCr + zH + zL;
                let zPure = Math.max(0.0, 1.0 - zAtmos);

                let mix1 = sstep({mass_start}, {mass_start}+{mass_fade}+0.0001, r);
                let mix2 = sstep({wash_start}, {wash_start}+{wash_fade}+0.0001, r);
                
                let f_mass = 1.0 - mix1;
                let f_wash = mix2;
                let f_mid = 1.0 - f_mass - f_wash;

                let l_mass = f_mass * zPure * 100;
                let l_wash = f_wash * zPure * 100;
                let l_mid = (f_mid * zPure * 100) + (zAtmos * 100); 

                document.getElementById('ld-mass').innerText=l_mass.toFixed(1)+'%';
                document.getElementById('ld-mid').innerText=l_mid.toFixed(1)+'%';
                document.getElementById('ld-wash').innerText=l_wash.toFixed(1)+'%';

                document.getElementById('z-abyss').innerText=(zA*100).toFixed(1)+'%'; 
                document.getElementById('z-core').innerText=(zC*100).toFixed(1)+'%'; 
                document.getElementById('z-luma').innerText=(zL*100).toFixed(1)+'%'; 
                document.getElementById('z-heat').innerText=(zH*100).toFixed(1)+'%'; 
                document.getElementById('z-crust').innerText=(zCr*100).toFixed(1)+'%';
                
                // --- PIE CHART (SVG) & DYNAMIC RECIPE LOGIC ---
                let ingredients = [];
                if (wY > 0 && zPure > 0) ingredients.push({{ name: n.y > 0 ? '{name_y_pos}' : '{name_y_neg}', hex: n.y > 0 ? '{yp_mid}' : '{yn_mid}', pct: wY * zPure * 100 }});
                if (wX > 0 && zPure > 0) ingredients.push({{ name: n.x > 0 ? '{name_x_pos}' : '{name_x_neg}', hex: n.x > 0 ? '{xp_mid}' : '{xn_mid}', pct: wX * zPure * 100 }});
                if (wZ > 0 && zPure > 0) ingredients.push({{ name: n.z > 0 ? '{name_z_pos}' : '{name_z_neg}', hex: n.z > 0 ? '{zp_mid}' : '{zn_mid}', pct: wZ * zPure * 100 }});
                if (zA > 0) ingredients.push({{ name: '{name_abyss}', hex: '{hex_abyss}', pct: zA * 100 }});
                if (zC > 0) ingredients.push({{ name: '{name_core}', hex: '{hex_core}', pct: zC * 100 }});
                if (zL > 0) ingredients.push({{ name: '{name_luma}', hex: '{hex_luma}', pct: zL * 100 }});
                if (zH > 0) ingredients.push({{ name: '{name_heat}', hex: '{hex_heat}', pct: zH * 100 }});
                if (zCr > 0) ingredients.push({{ name: '{name_crust}', hex: '{hex_crust}', pct: zCr * 100 }});

                ingredients = ingredients.filter(i => i.pct > 0.1).sort((a,b) => b.pct - a.pct);

                let svgHtml = `<svg viewBox="-1 -1 2 2" style="transform: rotate(-90deg); width: 100%; height: 100%; border-radius: 50%;">`;
                let currentPct = 0;
                let legendHtml = "";
                ingredients.forEach(i => {{
                    let pctDec = i.pct / 100;
                    let startAngle = currentPct * 2 * Math.PI;
                    let endAngle = (currentPct + pctDec) * 2 * Math.PI;
                    currentPct += pctDec;
                    
                    if (pctDec >= 0.999) {{
                        svgHtml += `<circle cx="0" cy="0" r="1" fill="${{i.hex}}" />`;
                    }} else {{
                        let x1 = Math.cos(startAngle), y1 = Math.sin(startAngle);
                        let x2 = Math.cos(endAngle), y2 = Math.sin(endAngle);
                        let largeArc = pctDec > 0.5 ? 1 : 0;
                        svgHtml += `<path d="M 0 0 L ${{x1}} ${{y1}} A 1 1 0 ${{largeArc}} 1 ${{x2}} ${{y2}} Z" fill="${{i.hex}}" />`;
                    }}
                    
                    legendHtml += `<div class="row"><span><span style="display:inline-block;width:10px;height:10px;background:${{i.hex}};border-radius:50%;margin-right:6px;vertical-align:middle;"></span>${{i.name}}</span><span>${{i.pct.toFixed(1)}}%</span></div>`;
                }});
                svgHtml += `</svg>`;

                document.getElementById('pie-chart-circle').innerHTML = svgHtml;
                document.getElementById('pie-legend').innerHTML = legendHtml;

                let cY_ma = n.y>0?{js_yp_ma}:{js_yn_ma}; let cX_ma = n.x>0?{js_xp_ma}:{js_xn_ma}; let cZ_ma = n.z>0?{js_zp_ma}:{js_zn_ma};
                let cY_mi = n.y>0?{js_yp_mi}:{js_yn_mi}; let cX_mi = n.x>0?{js_xp_mi}:{js_xn_mi}; let cZ_mi = n.z>0?{js_zp_mi}:{js_zn_mi};
                let cY_wa = n.y>0?{js_yp_wa}:{js_yn_wa}; let cX_wa = n.x>0?{js_xp_wa}:{js_xn_wa}; let cZ_wa = n.z>0?{js_zp_wa}:{js_zn_wa};
                
                let pC_ma = [cX_ma[0]*wX+cY_ma[0]*wY+cZ_ma[0]*wZ, cX_ma[1]*wX+cY_ma[1]*wY+cZ_ma[1]*wZ, cX_ma[2]*wX+cY_ma[2]*wY+cZ_ma[2]*wZ];
                let pC_mi = [cX_mi[0]*wX+cY_mi[0]*wY+cZ_mi[0]*wZ, cX_mi[1]*wX+cY_mi[1]*wY+cZ_mi[1]*wZ, cX_mi[2]*wX+cY_mi[2]*wY+cZ_mi[2]*wZ];
                let pC_wa = [cX_wa[0]*wX+cY_wa[0]*wY+cZ_wa[0]*wZ, cX_wa[1]*wX+cY_wa[1]*wY+cZ_wa[1]*wZ, cX_wa[2]*wX+cY_wa[2]*wY+cZ_wa[2]*wZ];
                
                let c_mass_to_mid = mVec(pC_ma, pC_mi, mix1);
                let pC_pure = mVec(c_mass_to_mid, pC_wa, mix2);

                let fC = pC_pure; 
                fC = mVec(fC, mVec(pC_mi, {js_core}, {mix_co}), vCo); 
                fC = mVec(fC, mVec(pC_mi, {js_abyss}, {mix_ab}), vAb); 
                fC = mVec(fC, mVec(pC_mi, {js_luma}, {mix_lu}), vLu); 
                fC = mVec(fC, mVec(pC_mi, {js_heat}, {mix_he}), vHe); 
                fC = mVec(fC, mVec(pC_mi, {js_crust}, {mix_cr}), vCr); 

                let rV=Math.round(fC[0]*255), gV=Math.round(fC[1]*255), bV=Math.round(fC[2]*255); let hS="#"+tHex(rV)+tHex(gV)+tHex(bV);

                document.getElementById('swatch').style.backgroundColor=`rgb(${{rV}}, ${{gV}}, ${{bV}})`; document.getElementById('hex-code').innerText=hS;
            }} else {{
                document.getElementById('live-coords').innerHTML = 'LAT ---° \u00A0|\u00A0 LON ---°<br><span style="color:#888; font-size:10px;">X: 0.00 \u00A0|\u00A0 Y: 0.00</span>';
                document.querySelectorAll('.row span:nth-child(2)').forEach(el=>el.innerText='0%'); document.getElementById('swatch').style.backgroundColor='#000'; document.getElementById('hex-code').innerText='-------';
            }}
        }}

        document.addEventListener('mousedown', (e) => {{ if(e.target.closest('#hud')) return; if(e.button===2) isPan=true; else isDrag=true; lastMouse={{x:e.clientX, y:e.clientY}}; }});
        document.addEventListener('mousemove', (e) => {{
            if(isDrag && !hDrag) {{ customUniforms.uRotY.value += (e.clientX-lastMouse.x)*0.01; customUniforms.uRotX.value += (e.clientY-lastMouse.y)*0.01; lastMouse={{x:e.clientX, y:e.clientY}}; }}
            else if(isPan && !hDrag) {{
                let pS=curZoom*0.0015, cR=new THREE.Vector3(1,0,0).applyQuaternion(camera.quaternion), cU=new THREE.Vector3(0,1,0).applyQuaternion(camera.quaternion);
                panT.add(cR.multiplyScalar(-(e.clientX-lastMouse.x)*pS)); panT.add(cU.multiplyScalar((e.clientY-lastMouse.y)*pS));
                updCam(); lastMouse={{x:e.clientX, y:e.clientY}};
            }}
            processRay(e.clientX, e.clientY);
        }});
        document.addEventListener('wheel', (e) => {{ if(!e.target.closest('#hud')) {{ curZoom+=e.deltaY*0.01; updCam(); }} }});

        document.addEventListener('touchstart', (e) => {{
            if(e.target.closest('#hud')) return;
            if(e.touches.length===1) {{ isDrag=true; lastMouse={{x:e.touches[0].clientX, y:e.touches[0].clientY}}; }}
            else if(e.touches.length===2) {{
                isDrag=false; let dx=e.touches[0].clientX-e.touches[1].clientX, dy=e.touches[0].clientY-e.touches[1].clientY;
                iDist=Math.sqrt(dx*dx+dy*dy); lMid={{x:(e.touches[0].clientX+e.touches[1].clientX)/2, y:(e.touches[0].clientY+e.touches[1].clientY)/2}};
            }}
        }}, {{passive:true}});

        document.addEventListener('touchmove', (e) => {{
            if(e.target.closest('#hud') || hDrag) return;
            if(e.touches.length===1 && isDrag) {{
                customUniforms.uRotY.value += (e.touches[0].clientX-lastMouse.x)*0.01; customUniforms.uRotX.value += (e.touches[0].clientY-lastMouse.y)*0.01;
                lastMouse={{x:e.touches[0].clientX, y:e.touches[0].clientY}}; processRay(e.touches[0].clientX, e.touches[0].clientY);
            }} else if(e.touches.length===2 && iDist) {{
                let dx=e.touches[0].clientX-e.touches[1].clientX, dy=e.touches[0].clientY-e.touches[1].clientY, dst=Math.sqrt(dx*dx+dy*dy);
                curZoom += (iDist-dst)*0.02; iDist=dst;
                let mX=(e.touches[0].clientX+e.touches[1].clientX)/2, mY=(e.touches[0].clientY+e.touches[1].clientY)/2, pS=curZoom*0.002;
                let cR=new THREE.Vector3(1,0,0).applyQuaternion(camera.quaternion), cU=new THREE.Vector3(0,1,0).applyQuaternion(camera.quaternion);
                panT.add(cR.multiplyScalar(-(mX-lMid.x)*pS)); panT.add(cU.multiplyScalar((mY-lMid.y)*pS));
                lMid={{x:mX, y:mY}}; updCam();
            }}
        }}, {{passive:true}});

        window.addEventListener('resize', () => {{ camera.aspect=window.innerWidth/window.innerHeight; camera.updateProjectionMatrix(); renderer.setSize(window.innerWidth, window.innerHeight); }});
        function animate() {{ requestAnimationFrame(animate); renderer.render(scene, camera); }}
        animate();
    </script>
</body>
</html>
"""

components.html(three_js_code, height=900)

# ========================================================
# END OF FILE - MAKE SURE YOU HIGHLIGHT ALL THE WAY DOWN TO HERE!
# ========================================================
