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

# --- SESSION STATE INITIALIZATION (Pre-loaded with your scanned swatches) ---
default_state = {
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
    "show_grid": False, "brilliance": 1.4, "rot_x": 0, "rot_y": 0,
    "rad_abyss": 0.1, "fade_abyss": 0.5, "rad_core": 0.5, "fade_core": 0.7,
    "rad_luma": 1.2, "fade_luma": 0.4, "rad_heat": 1.5, "fade_heat": 0.3, "rad_crust": 1.8, "fade_crust": 0.2
}

for k, v in default_state.items():
    if k not in st.session_state:
        st.session_state[k] = v

# 2. Sidebar Controls
with st.sidebar:
    st.markdown("### Color Sphere Studio")
    
    with st.expander("📖 About & Guide", expanded=False):
        st.markdown("""
        **The True Pigment Architecture**
        Physical paints possess a **mass tone** (thick application), a **mid-tone**, and an **undertone/wash** (diluted). A single tube of paint is effectively a living gradient. 
        
        This sphere maps that physical reality in 3D space. The deeper into the core you probe, the heavier the mass tone. The closer to the surface, the more diluted the wash. This mimics the behavior of physical paint interacting with light and water, long before it hits the atmospheric extremes of the Indigo Abyss or the White Luma.
        """)

    with st.expander("💾 Save / Load Workspace", expanded=False):
        uploaded_file = st.file_uploader("Load Palette (.json)", type=["json"], key="json_uploader")
        if uploaded_file is not None:
            file_id = uploaded_file.name + str(uploaded_file.size)
            if "last_loaded_file" not in st.session_state or st.session_state["last_loaded_file"] != file_id:
                try:
                    data = json.load(uploaded_file)
                    for k in default_state.keys():
                        if k in data:
                            st.session_state[k] = data[k]
                    st.session_state["last_loaded_file"] = file_id
                    st.rerun() 
                except Exception as e:
                    st.error("Invalid workspace file.")

        export_data = {k: st.session_state[k] for k in default_state.keys()}
        st.download_button(label="Export Workspace to JSON", data=json.dumps(export_data, indent=4), file_name="my_color_sphere_workspace.json", mime="application/json", key="json_downloader")
    
    with st.expander("🎨 6-Pole Anchor Pigments", expanded=True):
        st.markdown("*Input the 3 stages of your physical paint.*")
        
        name_y_pos = st.text_input("Top (Y+)", key="name_y_pos")
        c1, c2, c3 = st.columns(3)
        yp_mass = c1.color_picker("Mass", key="yp_mass")
        yp_mid = c2.color_picker("Mid", key="yp_mid")
        yp_wash = c3.color_picker("Wash", key="yp_wash")
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

    with st.expander("🌫️ Atmospheric Layers", expanded=False):
        col3, col4 = st.columns(2)
        with col3:
            show_abyss = st.toggle("Enable Abyss", key="show_abyss")
            name_abyss = st.text_input("Abyss Name", key="name_abyss")
            hex_abyss = st.color_picker("Abyss Color", key="hex_abyss")
            show_core = st.toggle("Enable Core", key="show_core")
            name_core = st.text_input("Core Name", key="name_core")
            hex_core = st.color_picker("Core Color", key="hex_core")
            show_heat = st.toggle("Enable Undercrust", key="show_heat")
            name_heat = st.text_input("Undercrust Name", key="name_heat")
            hex_heat = st.color_picker("Undercrust Color", key="hex_heat")
        with col4:
            show_luma = st.toggle("Enable Luma", key="show_luma")
            name_luma = st.text_input("Luma Name", key="name_luma")
            hex_luma = st.color_picker("Luma Color", key="hex_luma")
            show_crust = st.toggle("Enable Crust", key="show_crust")
            name_crust = st.text_input("Crust Name", key="name_crust")
            hex_crust = st.color_picker("Crust Color", key="hex_crust")

    with st.expander("🎛️ Atmosphere Fine-Tuning", expanded=False):
        show_grid = st.toggle("Show Wireframe Grid", key="show_grid")
        brilliance = st.slider("Color Overlap Brilliance", 0.2, 5.0, key="brilliance")
        st.markdown("---")
        if show_abyss:
            st.markdown(f"**{name_abyss}**")
            c1, c2 = st.columns(2)
            rad_abyss = c1.slider("Start Radius", 0.0, 2.0, key="rad_abyss")
            fade_abyss = c2.slider("Soft Fade", 0.0, 2.0, key="fade_abyss")
        if show_core:
            st.markdown(f"**{name_core}**")
            c1, c2 = st.columns(2)
            rad_core = c1.slider("Start Radius", 0.0, 2.0, key="rad_core")
            fade_core = c2.slider("Soft Fade", 0.0, 2.0, key="fade_core")
        if show_luma:
            st.markdown(f"**{name_luma}**")
            c1, c2 = st.columns(2)
            rad_luma = c1.slider("Start Radius", 0.0, 2.0, key="rad_luma")
            fade_luma = c2.slider("Soft Fade", 0.0, 2.0, key="fade_luma")
        if show_heat:
            st.markdown(f"**{name_heat}**")
            c1, c2 = st.columns(2)
            rad_heat = c1.slider("Start Radius", 0.0, 2.0, key="rad_heat")
            fade_heat = c2.slider("Soft Fade", 0.0, 2.0, key="fade_heat")
        if show_crust:
            st.markdown(f"**{name_crust}**")
            c1, c2 = st.columns(2)
            rad_crust = c1.slider("Start Radius", 0.0, 2.0, key="rad_crust")
            fade_crust = c2.slider("Soft Fade", 0.0, 2.0, key="fade_crust")
    
    with st.expander("🔄 Rotation Math", expanded=False):
        rot_x = st.slider("Rotate Latitude", 0, 360, key="rot_x")
        rot_y = st.slider("Rotate Longitude", 0, 360, key="rot_y")

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
        #hud-toggle {{ cursor: pointer; padding: 2px 8px; background: rgba(255,255,255,0.2); border-radius: 4px; pointer-events: auto; font-size: 14px; }}
        #hud-content {{ padding: 15px; }}
        .hud-section {{ margin-top: 5px; margin-bottom: 5px; color: #fff; font-weight: bold; border-bottom: 1px solid #444; padding-bottom: 3px; }}
        .row {{ display: flex; justify-content: space-between; margin-bottom: 2px; }}
        #swatch {{ width: 100%; height: 30px; border-radius: 4px; border: 1px solid #555; margin-bottom: 5px; background-color: #000; }}
        #hex-code {{ text-align: center; font-weight: bold; letter-spacing: 2px; margin-bottom: 5px; color: #fff; }}
        #freeze-status {{ text-align: center; color: gold; font-weight: bold; font-size: 11px; margin-bottom: 10px; display: none; }}
        #export-btn {{ display: none; width: 100%; padding: 8px; margin-top: 15px; background: #4CAF50; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }}
        #export-btn:hover {{ background: #45a049; }}
        #helper-text {{ position: absolute; bottom: 20px; left: 20px; color: rgba(255,255,255,0.4); font-family: sans-serif; font-size: 12px; pointer-events: none; white-space: pre-line; }}
    </style>
</head>
<body>
    <div id="hud">
        <div id="hud-header"><span>DATA HUD</span><span id="hud-toggle">–</span></div>
        <div id="hud-content">
            <div id="freeze-status">[ FROZEN - DBL CLICK TO UNLOCK ]</div>
            <div id="swatch"></div>
            <div id="hex-code">#000000</div>
            <div class="hud-section">Pigment Blend</div>
            <div class="row"><span>{name_y_pos} (Y+)</span><span id="p-yp">0%</span></div>
            <div class="row"><span>{name_y_neg} (Y-)</span><span id="p-yn">0%</span></div>
            <div class="row"><span>{name_x_pos} (X+)</span><span id="p-xp">0%</span></div>
            <div class="row"><span>{name_x_neg} (X-)</span><span id="p-xn">0%</span></div>
            <div class="row"><span>{name_z_pos} (Z+)</span><span id="p-zp">0%</span></div>
            <div class="row"><span>{name_z_neg} (Z-)</span><span id="p-zn">0%</span></div>
            <div class="hud-section">Atmospheric Depth</div>
            <div class="row" style="display: {'flex' if show_abyss else 'none'};"><span>{name_abyss}</span><span id="z-abyss">0%</span></div>
            <div class="row" style="display: {'flex' if show_core else 'none'};"><span>{name_core}</span><span id="z-core">0%</span></div>
            <div class="row"><span>Pure Mantle</span><span id="z-pure">0%</span></div>
            <div class="row" style="display: {'flex' if show_luma else 'none'};"><span>{name_luma}</span><span id="z-white">0%</span></div>
            <div class="row" style="display: {'flex' if show_heat else 'none'};"><span>{name_heat}</span><span id="z-orange">0%</span></div>
            <div class="row" style="display: {'flex' if show_crust else 'none'};"><span>{name_crust}</span><span id="z-umber">0%</span></div>
            <button id="export-btn">Export Pixel Snapshot</button>
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
            uAbRad: {{ value: {r_ab} }}, uAbFade: {{ value: {f_ab} }},
            uCoRad: {{ value: {r_co} }}, uCoFade: {{ value: {f_co} }},
            uLuRad: {{ value: {r_lu} }}, uLuFade: {{ value: {f_lu} }},
            uHeRad: {{ value: {r_he} }}, uHeFade: {{ value: {f_he} }},
            uCrRad: {{ value: {r_cr} }}, uCrFade: {{ value: {f_cr} }}
        }};

        const material = new THREE.ShaderMaterial({{
            side: THREE.DoubleSide, uniforms: customUniforms,
            vertexShader: `varying vec3 vPos; void main() {{ vec4 wp = modelMatrix * vec4(position, 1.0); vPos = wp.xyz; gl_Position = projectionMatrix * viewMatrix * wp; }}`,
            fragmentShader: `
                uniform float uBrilliance, uRotX, uRotY; 
                uniform float uAbRad, uAbFade, uCoRad, uCoFade, uLuRad, uLuFade, uHeRad, uHeFade, uCrRad, uCrFade;
                varying vec3 vPos;
                mat3 rx(float a) {{ float s=sin(a), c=cos(a); return mat3(1.,0.,0.,0.,c,-s,0.,s,c); }}
                mat3 ry(float a) {{ float s=sin(a), c=cos(a); return mat3(c,0.,s,0.,1.,0.,-s,0.,c); }}
                
                vec3 getDynamicColor(vec3 mass, vec3 mid, vec3 wash, float r) {{
                    float t = clamp(r / 2.0, 0.0, 1.0);
                    if (t < 0.5) {{ return mix(mass, mid, t * 2.0); }} 
                    else {{ return mix(mid, wash, (t - 0.5) * 2.0); }}
                }}
                
                void main() {{
                    if(vPos.x > 0.001 && vPos.y > 0.001 && vPos.z > 0.001) discard;
                    float r = length(vPos); vec3 n = normalize(rx(uRotX) * ry(uRotY) * vPos);
                    
                    vec3 cY = n.y > 0. ? getDynamicColor({gl_yp_ma}, {gl_yp_mi}, {gl_yp_wa}, r) : getDynamicColor({gl_yn_ma}, {gl_yn_mi}, {gl_yn_wa}, r);
                    vec3 cX = n.x > 0. ? getDynamicColor({gl_xp_ma}, {gl_xp_mi}, {gl_xp_wa}, r) : getDynamicColor({gl_xn_ma}, {gl_xn_mi}, {gl_xn_wa}, r);
                    vec3 cZ = n.z > 0. ? getDynamicColor({gl_zp_ma}, {gl_zp_mi}, {gl_zp_wa}, r) : getDynamicColor({gl_zn_ma}, {gl_zn_mi}, {gl_zn_wa}, r);
                    
                    float wX = pow(abs(n.x), uBrilliance), wY = pow(abs(n.y), uBrilliance), wZ = pow(abs(n.z), uBrilliance);
                    float tot = wX + wY + wZ; vec3 pC = cX*(wX/tot) + cY*(wY/tot) + cZ*(wZ/tot);
                    
                    float v0 = {1 if show_abyss else 0}==1 ? smoothstep(uAbRad, uAbRad + uAbFade, r) : 1.0;
                    float v1 = {1 if show_core else 0}==1 ? smoothstep(uCoRad, uCoRad + uCoFade, r) : 1.0;
                    float v2 = {1 if show_luma else 0}==1 ? smoothstep(uLuRad, uLuRad + uLuFade, r) : 0.0;
                    float v3 = {1 if show_heat else 0}==1 ? smoothstep(uHeRad, uHeRad + uHeFade, r) : 0.0;
                    float v4 = {1 if show_crust else 0}==1 ? smoothstep(uCrRad, uCrRad + uCrFade, r) : 0.0;
                    
                    vec3 fC = {gl_abyss}; 
                    fC = mix(fC, {gl_core}, v0); 
                    fC = mix(fC, pC, v1);
                    fC = mix(fC, mix(pC, {gl_luma}, 0.6), v2); 
                    fC = mix(fC, mix({gl_heat}, pC, 0.65), v3); 
                    fC = mix(fC, mix({gl_crust}, pC, 0.4), v4);
                    
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
        
        function getJSColor(mass, mid, wash, r) {{
            let t = Math.max(0, Math.min(1, r / 2.0));
            if (t < 0.5) return mVec(mass, mid, t * 2.0);
            return mVec(mid, wash, (t - 0.5) * 2.0);
        }}

        let isDrag=false, isPan=false, isFroz=false, lastMouse={{x:0,y:0}}, snapData="", iDist=null, lMid={{x:0,y:0}}, hDrag=false, hOx=0, hOy=0;
        const hud=document.getElementById('hud'), hHead=document.getElementById('hud-header'), hCont=document.getElementById('hud-content'), hTog=document.getElementById('hud-toggle');
        
        hTog.addEventListener('click', () => {{ hCont.style.display = hCont.style.display==='none'?'block':'none'; hTog.innerText = hCont.style.display==='none'?'+':'–'; }});
        const stDrag = (e) => {{ if(e.target.id==='hud-toggle') return; hDrag=true; let evt=e.touches?e.touches[0]:e; hOx=evt.clientX-hud.offsetLeft; hOy=evt.clientY-hud.offsetTop; }};
        hHead.addEventListener('mousedown', stDrag); hHead.addEventListener('touchstart', stDrag, {{passive:true}});
        const endAll = () => {{ hDrag=isDrag=isPan=false; iDist=null; }};
        window.addEventListener('mouseup', endAll); window.addEventListener('mouseleave', endAll); window.addEventListener('touchend', endAll);
        const doMove = (e) => {{ if(!hDrag) return; let evt=e.touches?e.touches[0]:e; hud.style.left=(evt.clientX-hOx)+'px'; hud.style.top=(evt.clientY-hOy)+'px'; hud.style.right='auto'; }};
        window.addEventListener('mousemove', doMove); window.addEventListener('touchmove', doMove, {{passive:true}});

        function togFroz() {{ isFroz=!isFroz; hud.style.borderColor=isFroz?'gold':'rgba(255,255,255,0.15)'; document.getElementById('freeze-status').style.display=isFroz?'block':'none'; document.getElementById('export-btn').style.display=isFroz?'block':'none'; }}
        document.addEventListener('dblclick', (e) => {{ if(!e.target.closest('#hud')) togFroz(); }});
        let lTap=0; document.addEventListener('touchend', (e) => {{ if(e.target.closest('#hud')||hDrag) return; let t=new Date().getTime(); if(t-lTap<400 && t-lTap>0) togFroz(); lTap=t; }});
        
        document.getElementById('export-btn').addEventListener('click', () => {{
            const a = document.createElement('a'); a.href = window.URL.createObjectURL(new Blob([snapData], {{type:'text/plain'}}));
            a.download = 'Sphere_'+document.getElementById('hex-code').innerText+'.txt'; a.click();
        }});

        function processRay(cX, cY) {{
            if(isFroz) return; mouse.x=(cX/window.innerWidth)*2-1; mouse.y=-(cY/window.innerHeight)*2+1; raycaster.setFromCamera(mouse, camera);
            const ints = raycaster.intersectObjects(group.children.filter(c => !c.material.wireframe));
            let hPt = null; for(let i=0; i<ints.length; i++) {{ if(ints[i].point.x>0.001 && ints[i].point.y>0.001 && ints[i].point.z>0.001) continue; hPt=ints[i].point; break; }}
            
            if(hPt) {{
                let r = Math.sqrt(hPt.x*hPt.x + hPt.y*hPt.y + hPt.z*hPt.z);
                let cx=Math.cos(customUniforms.uRotX.value), sx=Math.sin(customUniforms.uRotX.value), cy=Math.cos(customUniforms.uRotY.value), sy=Math.sin(customUniforms.uRotY.value);
                let spX=cy*hPt.x-sy*hPt.z, spY=hPt.y, spZ=sy*hPt.x+cy*hPt.z;
                let sP = {{ x:spX, y:cx*spY+sx*spZ, z:-sx*spY+cx*spZ }};
                let l = Math.sqrt(sP.x*sP.x+sP.y*sP.y+sP.z*sP.z); let n = {{ x:sP.x/l, y:sP.y/l, z:sP.z/l }};

                let wX=Math.pow(Math.abs(n.x),{brilliance}), wY=Math.pow(Math.abs(n.y),{brilliance}), wZ=Math.pow(Math.abs(n.z),{brilliance});
                let tot=wX+wY+wZ; wX/=tot; wY/=tot; wZ/=tot;
                let pr=(n.y>0?wY*100:0).toFixed(1), pc=(n.y<=0?wY*100:0).toFixed(1), py=(n.x>0?wX*100:0).toFixed(1), pb=(n.x<=0?wX*100:0).toFixed(1), pg=(n.z>0?wZ*100:0).toFixed(1), pm=(n.z<=0?wZ*100:0).toFixed(1);

                document.getElementById('p-yp').innerText=pr+'%'; document.getElementById('p-yn').innerText=pc+'%';
                document.getElementById('p-xp').innerText=py+'%'; document.getElementById('p-xn').innerText=pb+'%';
                document.getElementById('p-zp').innerText=pg+'%'; document.getElementById('p-zn').innerText=pm+'%';

                let v0={1 if show_abyss else 0}===1?sstep({r_ab}, {r_ab}+{f_ab}, r):1.0;
                let v1={1 if show_core else 0}===1?sstep({r_co}, {r_co}+{f_co}, r):1.0;
                let v2={1 if show_luma else 0}===1?sstep({r_lu}, {r_lu}+{f_lu}, r):0.0;
                let v3={1 if show_heat else 0}===1?sstep({r_he}, {r_he}+{f_he}, r):0.0;
                let v4={1 if show_crust else 0}===1?sstep({r_cr}, {r_cr}+{f_cr}, r):0.0;

                let zA=((1.-v0)*100).toFixed(1), zC=((v0*(1.-v1))*100).toFixed(1), zP=((v1*(1.-v2))*100).toFixed(1), zW=((v2*(1.-v3))*100).toFixed(1), zO=((v3*(1.-v4))*100).toFixed(1), zU=(v4*100).toFixed(1);
                document.getElementById('z-abyss').innerText=zA+'%'; document.getElementById('z-core').innerText=zC+'%'; document.getElementById('z-pure').innerText=zP+'%';
                document.getElementById('z-white').innerText=zW+'%'; document.getElementById('z-orange').innerText=zO+'%'; document.getElementById('z-umber').innerText=zU+'%';
                
                let cY = n.y > 0. ? getJSColor({js_yp_ma}, {js_yp_mi}, {js_yp_wa}, r) : getJSColor({js_yn_ma}, {js_yn_mi}, {js_yn_wa}, r);
                let cX = n.x > 0. ? getJSColor({js_xp_ma}, {js_xp_mi}, {js_xp_wa}, r) : getJSColor({js_xn_ma}, {js_xn_mi}, {js_xn_wa}, r);
                let cZ = n.z > 0. ? getJSColor({js_zp_ma}, {js_zp_mi}, {js_zp_wa}, r) : getJSColor({js_zn_ma}, {js_zn_mi}, {js_zn_wa}, r);
                
                let pRGB = [ cX[0]*wX+cY[0]*wY+cZ[0]*wZ, cX[1]*wX+cY[1]*wY+cZ[1]*wZ, cX[2]*wX+cY[2]*wY+cZ[2]*wZ ];
                let fC = {js_abyss}; fC=mVec(fC, {js_core}, v0); fC=mVec(fC, pRGB, v1); fC=mVec(fC, mVec(pRGB, {js_luma}, 0.6), v2); fC=mVec(fC, mVec({js_heat}, pRGB, 0.65), v3); fC=mVec(fC, mVec({js_crust}, pRGB, 0.4), v4);
                let rV=Math.round(fC[0]*255), gV=Math.round(fC[1]*255), bV=Math.round(fC[2]*255); let hS="#"+tHex(rV)+tHex(gV)+tHex(bV);

                document.getElementById('swatch').style.backgroundColor=`rgb(${{rV}}, ${{gV}}, ${{bV}})`; document.getElementById('hex-code').innerText=hS;
                let dX=(customUniforms.uRotX.value*180/Math.PI)%360, dY=(customUniforms.uRotY.value*180/Math.PI)%360; if(dX<0) dX+=360; if(dY<0) dY+=360;

                let dE = ""; if({1 if show_abyss else 0}===1) dE+=`{name_abyss}: ${{zA}}%\\n`; if({1 if show_core else 0}===1) dE+=`{name_core}: ${{zC}}%\\n`;
                dE+=`Pure Mantle: ${{zP}}%\\n`; if({1 if show_luma else 0}===1) dE+=`{name_luma}: ${{zW}}%\\n`; if({1 if show_heat else 0}===1) dE+=`{name_heat}: ${{zO}}%\\n`; if({1 if show_crust else 0}===1) dE+=`{name_crust}: ${{zU}}%\\n`;

                snapData = `CUSTOM PIGMENT SPHERE\\n-------------------\\nHex: ${{hS}}\\nRGB: (${{rV}},${{gV}},${{bV}})\\n\\nBLEND\\n-----\\n{name_y_pos}: ${{pr}}%\\n{name_y_neg}: ${{pc}}%\\n{name_x_pos}: ${{py}}%\\n{name_x_neg}: ${{pb}}%\\n{name_z_pos}: ${{pg}}%\\n{name_z_neg}: ${{pm}}%\\n\\nDEPTH\\n-----\\n`+dE+`\\nCOORD\\n-----\\nLat: ${{Math.round(dX)}}\\nLon: ${{Math.round(dY)}}\\n`;
            }} else {{
                document.querySelectorAll('.row span:nth-child(2)').forEach(el=>el.innerText='0%'); document.getElementById('swatch').style.backgroundColor='#000'; document.getElementById('hex-code').innerText='-------'; snapData="";
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
