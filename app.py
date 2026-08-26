import streamlit as st
import streamlit.components.v1 as components
import math
import json

# 1. Page Configuration MUST be first
st.set_page_config(page_title="Color Sphere - Custom Pigments", layout="wide")

# --- HACK: Remove Streamlit's massive default top padding ---
st.markdown("""
    <style>
           .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
    </style>
    """, unsafe_allow_html=True)

# --- HELPER FUNCTION: Convert Hex to GLSL & JS Vectors ---
def hex_to_vectors(hex_str):
    hex_str = hex_str.lstrip('#')
    r = int(hex_str[0:2], 16) / 255.0
    g = int(hex_str[2:4], 16) / 255.0
    b = int(hex_str[4:6], 16) / 255.0
    return f"vec3({r:.3f}, {g:.3f}, {b:.3f})", f"[{r:.3f}, {g:.3f}, {b:.3f}]"

# --- SESSION STATE INITIALIZATION ---
default_state = {
    "name_y_pos": "Red", "hex_y_pos": "#FF0000",
    "name_x_pos": "Yellow", "hex_x_pos": "#FFFF00",
    "name_z_pos": "Green", "hex_z_pos": "#00FF00",
    "name_y_neg": "Cyan", "hex_y_neg": "#00FFFF",
    "name_x_neg": "Blue", "hex_x_neg": "#0000FF",
    "name_z_neg": "Magenta", "hex_z_neg": "#FF00FF",
    "show_core": True, "name_core": "Violet Core", "hex_core": "#59268C",
    "show_heat": True, "name_heat": "Orange Heat", "hex_heat": "#FF6600",
    "show_luma": True, "name_luma": "White Luma", "hex_luma": "#F2F2F2",
    "show_crust": True, "name_crust": "Umber Crust", "hex_crust": "#26140D",
    "show_grid": False,
    "sun_intensity": 0.8,
    "shadow_depth": 0.3,
    "brilliance": 1.4,
    "rot_x": 0,
    "rot_y": 0
}

for k, v in default_state.items():
    if k not in st.session_state:
        st.session_state[k] = v

# 2. Sidebar Controls
with st.sidebar:
    st.markdown("### Color Sphere Studio")
    
    with st.expander("📖 About & Guide", expanded=False):
        st.markdown("""
        **The Philosophy: Brilliant Depth, Zero Mud**
        For an artist, the ultimate goal is palette accessibility—using the most efficient range of pigments to create illuminating, dramatic images without them ever turning dark, dull, or muddy. 
        
        Mixing three carefully chosen colors is the ultimate way to avoid muddiness. By visually mapping out your pigments, you can intentionally avoid mixing exact opposites (like pure red and cyan), ensuring your mixes remain clean and vibrant. It bridges the gap between digital color (RGB/CMY) and traditional pigment mixing.

        **The 6+3 Minimalist Palette**
        You can achieve a staggering gamut of color with just 6 to 9 specific pigments, avoiding the use of flat Black entirely to create natural, dramatic shadows.
        * **The 6 Anchors:** Red, Green, Blue (RGB) and Cyan, Magenta, Yellow (CMY). 
        * **The Atmospheric Depth (+3):** The RGB/CMY spectrum naturally lacks rich purples and earthy oranges. To complete the universe, this tool introduces Violet (for natural, deep darkness without black), Orange (for brilliant warmth), and Burnt Umber (for deep, resonant earth tones). 
        
        **How to Use This Tool**
        * **Map Your Inks:** Replace the default digital colors with the exact hex codes of the physical paints or inks you own. 
        * **Test Limited Palettes:** If you only own three primary colors, input them across the six poles to see the exact gamut of what those three colors can achieve.
        * **Extract the Formula:** Spin the sphere to explore unexpected harmonies. Double-click (or double-tap on iPad) to freeze the sphere. The Data HUD will reveal the exact percentage of each pigment required to mix that specific hue on your physical palette.
        
        ---
        *Questions or feedback? Please contact the original poster of this tool!*
        """)

    st.markdown("[Find Pigment Hex Codes Here](https://inkswatch.com/)")
    
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
        st.download_button(
            label="Export Workspace to JSON",
            data=json.dumps(export_data, indent=4),
            file_name="my_color_sphere_workspace.json",
            mime="application/json",
            key="json_downloader"
        )
    
    with st.expander("🎨 6-Pole Anchor Pigments", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            name_y_pos = st.text_input("Top (Y+)", key="name_y_pos")
            hex_y_pos = st.color_picker("Y+ Color", key="hex_y_pos")
            name_x_pos = st.text_input("East (X+)", key="name_x_pos")
            hex_x_pos = st.color_picker("X+ Color", key="hex_x_pos")
            name_z_pos = st.text_input("Front (Z+)", key="name_z_pos")
            hex_z_pos = st.color_picker("Z+ Color", key="hex_z_pos")
        with col2:
            name_y_neg = st.text_input("Bottom (Y-)", key="name_y_neg")
            hex_y_neg = st.color_picker("Y- Color", key="hex_y_neg")
            name_x_neg = st.text_input("West (X-)", key="name_x_neg")
            hex_x_neg = st.color_picker("X- Color", key="hex_x_neg")
            name_z_neg = st.text_input("Back (Z-)", key="name_z_neg")
            hex_z_neg = st.color_picker("Z- Color", key="hex_z_neg")

    with st.expander("🌫️ Atmospheric Layers", expanded=False):
        st.markdown("*Toggle the atmospheric effects on/off. If you don't own these specific physical paints, you can mix them!*")
        st.markdown("- **Orange:** Mix Red/Magenta + Yellow\n- **Burnt Umber:** Mix Orange + a touch of Blue/Cyan\n- **Violet:** Mix Magenta + Cyan\n- **Luma:** The raw white of the paper")
        col3, col4 = st.columns(2)
        with col3:
            show_core = st.toggle("Enable Core", key="show_core")
            name_core = st.text_input("Core Name", key="name_core")
            hex_core = st.color_picker("Core Color", key="hex_core")
            
            show_heat = st.toggle("Enable Heat", key="show_heat")
            name_heat = st.text_input("Heat Name", key="name_heat")
            hex_heat = st.color_picker("Heat Color", key="hex_heat")
        with col4:
            show_luma = st.toggle("Enable Luma", key="show_luma")
            name_luma = st.text_input("Luma Name", key="name_luma")
            hex_luma = st.color_picker("Luma Color", key="hex_luma")
            
            show_crust = st.toggle("Enable Crust", key="show_crust")
            name_crust = st.text_input("Crust Name", key="name_crust")
            hex_crust = st.color_picker("Crust Color", key="hex_crust")

    with st.expander("🎛️ Atmosphere Controls", expanded=False):
        show_grid = st.toggle("Show Wireframe Grid", key="show_grid")
        sun_intensity = st.slider("Sun Intensity (Heat Zone)", 0.0, 1.0, key="sun_intensity")
        shadow_depth = st.slider("Shadow Depth (Core Zone)", 0.0, 1.0, key="shadow_depth")
        brilliance = st.slider("Brilliance (Overlap Spread)", 0.2, 5.0, key="brilliance")
    
    with st.expander("🔄 Rotation Math", expanded=False):
        st.markdown("*Use mouse-drag on canvas for fluid rotation.*")
        rot_x = st.slider("Rotate Latitude", 0, 360, key="rot_x")
        rot_y = st.slider("Rotate Longitude", 0, 360, key="rot_y")

# Pre-calculate all vectors for injection
gl_yp, js_yp = hex_to_vectors(hex_y_pos)
gl_yn, js_yn = hex_to_vectors(hex_y_neg)
gl_xp, js_xp = hex_to_vectors(hex_x_pos)
gl_xn, js_xn = hex_to_vectors(hex_x_neg)
gl_zp, js_zp = hex_to_vectors(hex_z_pos)
gl_zn, js_zn = hex_to_vectors(hex_z_neg)

gl_core, js_core = hex_to_vectors(hex_core)
gl_luma, js_luma = hex_to_vectors(hex_luma)
gl_heat, js_heat = hex_to_vectors(hex_heat)
gl_crust, js_crust = hex_to_vectors(hex_crust)

rad_x = rot_x * (math.pi / 180)
rad_y = rot_y * (math.pi / 180)

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
        
        #hud {{
            position: absolute; top: 20px; right: 20px; color: #e0e0e0;
            font-family: 'Courier New', Courier, monospace; font-size: 13px;
            background: rgba(15, 17, 23, 0.9); border-radius: 8px;
            pointer-events: auto; border: 2px solid rgba(255, 255, 255, 0.15);
            width: 280px; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); transition: border-color 0.2s;
            z-index: 100;
        }}
        #hud-header {{
            background: rgba(255, 255, 255, 0.1); padding: 8px 12px; cursor: move;
            display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1); border-radius: 6px 6px 0 0;
        }}
        #hud-header span {{ font-weight: bold; font-size: 12px; pointer-events: none; }}
        #hud-toggle {{ cursor: pointer; padding: 2px 8px; background: rgba(255,255,255,0.2); border-radius: 4px; pointer-events: auto !important; font-size: 14px !important; }}
        #hud-content {{ padding: 15px; }}
        
        .hud-section {{ margin-top: 5px; margin-bottom: 5px; color: #ffffff; font-weight: bold; border-bottom: 1px solid #444; padding-bottom: 3px; }}
        .row {{ display: flex; justify-content: space-between; margin-bottom: 2px; }}
        #swatch {{ width: 100%; height: 30px; border-radius: 4px; border: 1px solid #555; margin-bottom: 5px; background-color: #000; }}
        #hex-code {{ text-align: center; font-weight: bold; letter-spacing: 2px; margin-bottom: 5px; color: #fff; }}
        
        #freeze-status {{ text-align: center; color: gold; font-weight: bold; font-size: 11px; margin-bottom: 10px; display: none; }}
        #export-btn {{ display: none; width: 100%; padding: 8px; margin-top: 15px; background: #4CAF50; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; font-family: inherit; }}
        #export-btn:hover {{ background: #45a049; }}
        
        #helper-text {{
            position: absolute; bottom: 20px; left: 20px; color: rgba(255,255,255,0.4);
            font-family: sans-serif; font-size: 12px; pointer-events: none; white-space: pre-line;
        }}
    </style>
</head>
<body>
    <div id="hud">
        <div id="hud-header"><span>DATA HUD</span><span id="hud-toggle">–</span></div>
        <div id="hud-content">
            <div id="freeze-status">[ FROZEN - DBL CLICK/TAP TO UNLOCK ]</div>
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
            <div class="row" style="display: {'flex' if show_core else 'none'};"><span>{name_core}</span><span id="z-core">0%</span></div>
            <div class="row"><span>Pure Mantle</span><span id="z-pure">0%</span></div>
            <div class="row" style="display: {'flex' if show_luma else 'none'};"><span>{name_luma}</span><span id="z-white">0%</span></div>
            <div class="row" style="display: {'flex' if show_heat else 'none'};"><span>{name_heat}</span><span id="z-orange">0%</span></div>
            <div class="row" style="display: {'flex' if show_crust else 'none'};"><span>{name_crust}</span><span id="z-umber">0%</span></div>
            
            <button id="export-btn">Export Pixel Snapshot to TXT</button>
        </div>
    </div>
    
    <div id="helper-text">Left-Click / 1-Finger: Rotate
    Right-Click / 2-Fingers: Pan & Move
    Scroll / Pinch: Zoom In/Out</div>

    <script>
        document.addEventListener('contextmenu', event => event.preventDefault());

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        const customUniforms = {{
            uBrilliance: {{ value: {brilliance} }},
            uSun: {{ value: {sun_intensity} }},
            uShadow: {{ value: {shadow_depth} }},
            uRotX: {{ value: {rad_x} }},
            uRotY: {{ value: {rad_y} }}
        }};

        const material = new THREE.ShaderMaterial({{
            side: THREE.DoubleSide, 
            uniforms: customUniforms,
            vertexShader: `
                varying vec3 vUnifiedPos;
                void main() {{
                    vec4 worldPos = modelMatrix * vec4(position, 1.0);
                    vUnifiedPos = worldPos.xyz;
                    gl_Position = projectionMatrix * viewMatrix * worldPos;
                }}
            `,
            fragmentShader: `
                uniform float uBrilliance;
                uniform float uSun;
                uniform float uShadow;
                uniform float uRotX;
                uniform float uRotY;
                varying vec3 vUnifiedPos;
                
                mat3 rotX(float a) {{ float s = sin(a), c = cos(a); return mat3(1.0, 0.0, 0.0, 0.0, c, -s, 0.0, s, c); }}
                mat3 rotY(float a) {{ float s = sin(a), c = cos(a); return mat3(c, 0.0, s, 0.0, 1.0, 0.0, -s, 0.0, c); }}
                
                void main() {{
                    if(vUnifiedPos.x > 0.001 && vUnifiedPos.y > 0.001 && vUnifiedPos.z > 0.001) {{ discard; }}
                    float r = length(vUnifiedPos);
                    vec3 spinPos = rotX(uRotX) * rotY(uRotY) * vUnifiedPos;
                    vec3 n = normalize(spinPos);

                    vec3 colorY = (n.y > 0.0) ? {gl_yp} : {gl_yn};
                    vec3 colorX = (n.x > 0.0) ? {gl_xp} : {gl_xn};
                    vec3 colorZ = (n.z > 0.0) ? {gl_zp} : {gl_zn};

                    float wX = pow(abs(n.x), uBrilliance);
                    float wY = pow(abs(n.y), uBrilliance);
                    float wZ = pow(abs(n.z), uBrilliance);
                    
                    float total = wX + wY + wZ;
                    vec3 pureColor = colorX * (wX/total) + colorY * (wY/total) + colorZ * (wZ/total);

                    // Dynamic Toggling Math
                    float v1 = {1 if show_core else 0} == 1 ? smoothstep(uShadow * 0.1, (uShadow * 0.1) + 1.3, r) : 1.0;
                    float crustEdge = 1.88 - (uSun * 0.15);
                    float v2 = {1 if show_luma else 0} == 1 ? smoothstep(crustEdge - 0.65, crustEdge - 0.1, r) : 0.0;
                    float v3 = {1 if show_heat else 0} == 1 ? smoothstep(crustEdge - 0.35, crustEdge - 0.02, r) : 0.0;
                    float v4 = {1 if show_crust else 0} == 1 ? smoothstep(crustEdge - 0.02, 2.0, r) : 0.0;

                    vec3 fColor = {gl_core};
                    fColor = mix(fColor, pureColor, v1);
                    fColor = mix(fColor, mix(pureColor, {gl_luma}, 0.6), v2);
                    fColor = mix(fColor, mix({gl_heat}, pureColor, 0.65), v3);
                    fColor = mix(fColor, mix({gl_crust}, pureColor, 0.4), v4);

                    gl_FragColor = vec4(fColor, 1.0);
                }}
            `
        }});

        const group = new THREE.Group();
        const sphereGeo = new THREE.SphereGeometry(2, 64, 64);
        group.add(new THREE.Mesh(sphereGeo, material));

        if ({"true" if show_grid else "false"}) {{
            const wireMaterial = new THREE.MeshBasicMaterial({{ color: 0xffffff, wireframe: true, transparent: true, opacity: 0.15 }});
            group.add(new THREE.Mesh(sphereGeo, wireMaterial));
        }}

        const wallGeo = new THREE.CircleGeometry(2, 32, 0, Math.PI / 2);
        const wallXY = new THREE.Mesh(wallGeo, material); 
        const wallYZ = new THREE.Mesh(wallGeo, material); wallYZ.rotation.y = -Math.PI / 2; 
        const wallXZ = new THREE.Mesh(wallGeo, material); wallXZ.rotation.x = Math.PI / 2; 
        group.add(wallXY); group.add(wallYZ); group.add(wallXZ);
        scene.add(group);

        let currentZoom = 6.0; 
        let panTarget = new THREE.Vector3(0, 0, 0);

        function updateCamera() {{
            currentZoom = Math.max(2.5, Math.min(25.0, currentZoom)); 
            let camVal = currentZoom / Math.sqrt(3);
            camera.position.set(camVal + panTarget.x, camVal + panTarget.y, camVal + panTarget.z);
            camera.lookAt(panTarget);
        }}
        updateCamera();

        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        function smoothstep(min, max, value) {{ let x = Math.max(0, Math.min(1, (value - min) / (max - min))); return x * x * (3 - 2 * x); }}
        function mixVec(v1, v2, amount) {{ return [v1[0]*(1-amount) + v2[0]*amount, v1[1]*(1-amount) + v2[1]*amount, v1[2]*(1-amount) + v2[2]*amount]; }}
        const toHex = (c) => c.toString(16).padStart(2, '0').toUpperCase();

        let isDragging = false, isPanning = false, isFrozen = false;
        let lastMousePosition = {{ x: 0, y: 0 }};
        let snapshotData = "";
        let initialPinchDist = null, lastPinchMidpoint = {{ x: 0, y: 0 }};

        const hud = document.getElementById('hud');
        const hudHeader = document.getElementById('hud-header');
        const hudContent = document.getElementById('hud-content');
        const hudToggle = document.getElementById('hud-toggle');
        
        let hudDragging = false;
        let hudOffsetX = 0, hudOffsetY = 0;

        hudToggle.addEventListener('click', () => {{
            if (hudContent.style.display === 'none') {{
                hudContent.style.display = 'block'; hudToggle.innerText = '–';
            }} else {{
                hudContent.style.display = 'none'; hudToggle.innerText = '+';
            }}
        }});

        hudHeader.addEventListener('mousedown', (e) => {{
            if(e.target.id === 'hud-toggle') return;
            hudDragging = true; hudOffsetX = e.clientX - hud.offsetLeft; hudOffsetY = e.clientY - hud.offsetTop;
        }});
        hudHeader.addEventListener('touchstart', (e) => {{
            if(e.target.id === 'hud-toggle') return;
            hudDragging = true; hudOffsetX = e.touches[0].clientX - hud.offsetLeft; hudOffsetY = e.touches[0].clientY - hud.offsetTop;
        }}, {{passive: true}});

        window.addEventListener('mouseup', () => {{ hudDragging = false; isDragging = false; isPanning = false; }});
        window.addEventListener('mouseleave', () => {{ hudDragging = false; isDragging = false; isPanning = false; }});
        window.addEventListener('touchend', () => {{ hudDragging = false; isDragging = false; isPanning = false; initialPinchDist = null; }});

        window.addEventListener('mousemove', (e) => {{
            if (hudDragging) {{ hud.style.left = (e.clientX - hudOffsetX) + 'px'; hud.style.top = (e.clientY - hudOffsetY) + 'px'; hud.style.right = 'auto'; }}
        }});
        window.addEventListener('touchmove', (e) => {{
            if (hudDragging) {{ hud.style.left = (e.touches[0].clientX - hudOffsetX) + 'px'; hud.style.top = (e.touches[0].clientY - hudOffsetY) + 'px'; hud.style.right = 'auto'; }}
        }}, {{passive: true}});

        function toggleFreeze() {{
            isFrozen = !isFrozen;
            if(isFrozen) {{
                hud.style.borderColor = 'gold'; document.getElementById('freeze-status').style.display = 'block'; document.getElementById('export-btn').style.display = 'block';
            }} else {{
                hud.style.borderColor = 'rgba(255, 255, 255, 0.15)'; document.getElementById('freeze-status').style.display = 'none'; document.getElementById('export-btn').style.display = 'none';
            }}
        }}

        document.addEventListener('dblclick', function(e) {{ if(e.target.closest('#hud')) return; toggleFreeze(); }});

        let lastTap = 0;
        document.addEventListener('touchend', function(e) {{
            if(e.target.closest('#hud') || hudDragging) return;
            let currentTime = new Date().getTime(); let tapLength = currentTime - lastTap;
            if (tapLength < 400 && tapLength > 0) {{ toggleFreeze(); }}
            lastTap = currentTime;
        }});

        document.getElementById('export-btn').addEventListener('click', function() {{
            const blob = new Blob([snapshotData], {{ type: 'text/plain' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a'); a.href = url;
            a.download = 'PigmentSnapshot_' + document.getElementById('hex-code').innerText + '.txt';
            a.click(); window.URL.revokeObjectURL(url);
        }});

        function processRaycaster(clientX, clientY) {{
            if(isFrozen) return;
            mouse.x = (clientX / window.innerWidth) * 2 - 1; mouse.y = -(clientY / window.innerHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);

            const intersectableObjects = group.children.filter(child => child.material.wireframe !== true);
            const intersects = raycaster.intersectObjects(intersectableObjects);
            
            let hitPoint = null;
            for(let i = 0; i < intersects.length; i++) {{
                let pt = intersects[i].point;
                if(pt.x > 0.001 && pt.y > 0.001 && pt.z > 0.001) continue; 
                hitPoint = pt; break;
            }}

            if(hitPoint) {{
                let r = Math.sqrt(hitPoint.x*hitPoint.x + hitPoint.y*hitPoint.y + hitPoint.z*hitPoint.z);
                let cx = Math.cos(customUniforms.uRotX.value), sx = Math.sin(customUniforms.uRotX.value);
                let cy = Math.cos(customUniforms.uRotY.value), sy = Math.sin(customUniforms.uRotY.value);
                
                let v1x = cy * hitPoint.x - sy * hitPoint.z; let v1y = hitPoint.y; let v1z = sy * hitPoint.x + cy * hitPoint.z;
                let spinPos = {{ x: v1x, y: cx * v1y + sx * v1z, z: -sx * v1y + cx * v1z }};
                
                let len = Math.sqrt(spinPos.x*spinPos.x + spinPos.y*spinPos.y + spinPos.z*spinPos.z);
                let n = {{ x: spinPos.x/len, y: spinPos.y/len, z: spinPos.z/len }};

                let wX = Math.pow(Math.abs(n.x), {brilliance}); let wY = Math.pow(Math.abs(n.y), {brilliance}); let wZ = Math.pow(Math.abs(n.z), {brilliance});
                let tot = wX + wY + wZ; wX /= tot; wY /= tot; wZ /= tot;

                let pr = (n.y > 0 ? (wY*100) : 0).toFixed(1); let pc = (n.y <= 0 ? (wY*100) : 0).toFixed(1);
                let py = (n.x > 0 ? (wX*100) : 0).toFixed(1); let pb = (n.x <= 0 ? (wX*100) : 0).toFixed(1);
                let pg = (n.z > 0 ? (wZ*100) : 0).toFixed(1); let pm = (n.z <= 0 ? (wZ*100) : 0).toFixed(1);

                document.getElementById('p-yp').innerText = pr + '%'; document.getElementById('p-yn').innerText = pc + '%';
                document.getElementById('p-xp').innerText = py + '%'; document.getElementById('p-xn').innerText = pb + '%';
                document.getElementById('p-zp').innerText = pg + '%'; document.getElementById('p-zn').innerText = pm + '%';

                let coreEdge = {shadow_depth} * 0.1; let crustEdge = 1.88 - ({sun_intensity} * 0.15);
                
                let v1 = {1 if show_core else 0} === 1 ? smoothstep(coreEdge, coreEdge + 1.3, r) : 1.0;
                let v2 = {1 if show_luma else 0} === 1 ? smoothstep(crustEdge - 0.65, crustEdge - 0.1, r) : 0.0;
                let v3 = {1 if show_heat else 0} === 1 ? smoothstep(crustEdge - 0.35, crustEdge - 0.02, r) : 0.0;
                let v4 = {1 if show_crust else 0} === 1 ? smoothstep(crustEdge - 0.02, 2.0, r) : 0.0;

                let zCore = ((1.0 - v1) * 100).toFixed(1); 
                let zPure = ((v1 * (1.0 - v2)) * 100).toFixed(1);
                let zWhite = ((v2 * (1.0 - v3)) * 100).toFixed(1); 
                let zOrange = ((v3 * (1.0 - v4)) * 100).toFixed(1);
                let zUmber = (v4 * 100).toFixed(1);

                document.getElementById('z-core').innerText = zCore + '%'; 
                document.getElementById('z-pure').innerText = zPure + '%';
                document.getElementById('z-white').innerText = zWhite + '%'; 
                document.getElementById('z-orange').innerText = zOrange + '%';
                document.getElementById('z-umber').innerText = zUmber + '%';
                
                let colorY = n.y > 0 ? {js_yp} : {js_yn}; let colorX = n.x > 0 ? {js_xp} : {js_xn}; let colorZ = n.z > 0 ? {js_zp} : {js_zn};
                let pureRGB = [ colorX[0]*wX + colorY[0]*wY + colorZ[0]*wZ, colorX[1]*wX + colorY[1]*wY + colorZ[1]*wZ, colorX[2]*wX + colorY[2]*wY + colorZ[2]*wZ ];

                let fColor = {js_core}; 
                fColor = mixVec(fColor, pureRGB, v1); 
                fColor = mixVec(fColor, mixVec(pureRGB, {js_luma}, 0.6), v2);
                fColor = mixVec(fColor, mixVec({js_heat}, pureRGB, 0.65), v3); 
                fColor = mixVec(fColor, mixVec({js_crust}, pureRGB, 0.4), v4);
                
                let rVal = Math.round(fColor[0]*255); let gVal = Math.round(fColor[1]*255); let bVal = Math.round(fColor[2]*255);
                let hexStr = "#" + toHex(rVal) + toHex(gVal) + toHex(bVal);

                document.getElementById('swatch').style.backgroundColor = `rgb(${{rVal}}, ${{gVal}}, ${{bVal}})`;
                document.getElementById('hex-code').innerText = hexStr;
                
                let degX = (customUniforms.uRotX.value * 180 / Math.PI) % 360; let degY = (customUniforms.uRotY.value * 180 / Math.PI) % 360;
                if (degX < 0) degX += 360; if (degY < 0) degY += 360;

                let dynExport = "";
                if ({1 if show_core else 0} === 1) dynExport += `{name_core}: ${{zCore}}%\\n`;
                dynExport += `Pure Mantle: ${{zPure}}%\\n`;
                if ({1 if show_luma else 0} === 1) dynExport += `{name_luma}: ${{zWhite}}%\\n`;
                if ({1 if show_heat else 0} === 1) dynExport += `{name_heat}: ${{zOrange}}%\\n`;
                if ({1 if show_crust else 0} === 1) dynExport += `{name_crust}: ${{zUmber}}%\\n`;

                snapshotData = `CUSTOM PIGMENT SPHERE SNAPSHOT\\n------------------------------\\nFinal Hex Code:  ${{hexStr}}\\nFinal RGB Value: (${{rVal}}, ${{gVal}}, ${{bVal}})\\n\\nPIGMENT BLEND\\n-------------\\n{name_y_pos}: ${{pr}}%\\n{name_y_neg}: ${{pc}}%\\n{name_x_pos}: ${{py}}%\\n{name_x_neg}: ${{pb}}%\\n{name_z_pos}: ${{pg}}%\\n{name_z_neg}: ${{pm}}%\\n\\nATMOSPHERIC DEPTH\\n-----------------\\n` + dynExport + `\\nRESTORATION COORDINATES\\n-----------------------\\nLatitude:  ${{Math.round(degX)}}\\nLongitude: ${{Math.round(degY)}}\\n`;
            }} else {{
                document.querySelectorAll('.row span:nth-child(2)').forEach(el => el.innerText = '0%');
                document.getElementById('swatch').style.backgroundColor = '#000'; document.getElementById('hex-code').innerText = '-------'; snapshotData = "";
            }}
        }}

        document.addEventListener('mousedown', function(e) {{
            if(e.target.closest('#hud')) return;
            if (e.button === 2) {{ isPanning = true; }} else {{ isDragging = true; }}
            lastMousePosition = {{ x: e.clientX, y: e.clientY }};
        }});
        
        document.addEventListener('mousemove', function(e) {{
            if(isDragging && !hudDragging) {{
                let deltaMove = {{ x: e.clientX - lastMousePosition.x, y: e.clientY - lastMousePosition.y }};
                customUniforms.uRotY.value += deltaMove.x * 0.01; customUniforms.uRotX.value += deltaMove.y * 0.01;
                lastMousePosition = {{ x: e.clientX, y: e.clientY }};
            }} else if (isPanning && !hudDragging) {{
                let dx = e.clientX - lastMousePosition.x; let dy = e.clientY - lastMousePosition.y;
                let panSpeed = currentZoom * 0.0015;
                let camRight = new THREE.Vector3(1, 0, 0).applyQuaternion(camera.quaternion);
                let camUp = new THREE.Vector3(0, 1, 0).applyQuaternion(camera.quaternion);
                panTarget.add(camRight.multiplyScalar(-dx * panSpeed)); panTarget.add(camUp.multiplyScalar(dy * panSpeed));
                updateCamera(); lastMousePosition = {{ x: e.clientX, y: e.clientY }};
            }}
            processRaycaster(e.clientX, e.clientY);
        }});

        document.addEventListener('wheel', function(e) {{
            if(e.target.closest('#hud')) return; currentZoom += e.deltaY * 0.01; updateCamera();
        }});

        document.addEventListener('touchstart', function(e) {{
            if(e.target.closest('#hud')) return;
            if (e.touches.length === 1) {{
                isDragging = true; lastMousePosition = {{ x: e.touches[0].clientX, y: e.touches[0].clientY }};
            }} else if (e.touches.length === 2) {{
                isDragging = false; let dx = e.touches[0].clientX - e.touches[1].clientX; let dy = e.touches[0].clientY - e.touches[1].clientY;
                initialPinchDist = Math.sqrt(dx*dx + dy*dy);
                lastPinchMidpoint = {{ x: (e.touches[0].clientX + e.touches[1].clientX)/2, y: (e.touches[0].clientY + e.touches[1].clientY)/2 }};
            }}
        }}, {{passive: true}});

        document.addEventListener('touchmove', function(e) {{
            if(e.target.closest('#hud') || hudDragging) return;
            if (e.touches.length === 1 && isDragging) {{
                let deltaMove = {{ x: e.touches[0].clientX - lastMousePosition.x, y: e.touches[0].clientY - lastMousePosition.y }};
                customUniforms.uRotY.value += deltaMove.x * 0.01; customUniforms.uRotX.value += deltaMove.y * 0.01;
                lastMousePosition = {{ x: e.touches[0].clientX, y: e.touches[0].clientY }};
                processRaycaster(e.touches[0].clientX, e.touches[0].clientY);
            }} else if (e.touches.length === 2 && initialPinchDist) {{
                let dx = e.touches[0].clientX - e.touches[1].clientX; let dy = e.touches[0].clientY - e.touches[1].clientY;
                let dist = Math.sqrt(dx*dx + dy*dy); let zoomDelta = initialPinchDist - dist;
                currentZoom += zoomDelta * 0.02; initialPinchDist = dist;
                let midX = (e.touches[0].clientX + e.touches[1].clientX)/2; let midY = (e.touches[0].clientY + e.touches[1].clientY)/2;
                let panDx = midX - lastPinchMidpoint.x; let panDy = midY - lastPinchMidpoint.y;
                let panSpeed = currentZoom * 0.002;
                let camRight = new THREE.Vector3(1, 0, 0).applyQuaternion(camera.quaternion);
                let camUp = new THREE.Vector3(0, 1, 0).applyQuaternion(camera.quaternion);
                panTarget.add(camRight.multiplyScalar(-panDx * panSpeed)); panTarget.add(camUp.multiplyScalar(panDy * panSpeed));
                lastPinchMidpoint = {{ x: midX, y: midY }}; updateCamera();
            }}
        }}, {{passive: true}});

        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight; camera.updateProjectionMatrix(); renderer.setSize(window.innerWidth, window.innerHeight);
        }});

        function animate() {{ requestAnimationFrame(animate); renderer.render(scene, camera); }}
        animate();
    </script>
</body>
</html>
"""

components.html(three_js_code, height=900)
