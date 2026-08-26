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
    "name_core": "Violet Core", "hex_core": "#59268C",
    "name_heat": "Orange Heat", "hex_heat": "#FF6600",
    "name_luma": "White Luma", "hex_luma": "#F2F2F2",
    "name_crust": "Umber Crust", "hex_crust": "#26140D",
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

# 2. Sidebar Controls (Now fully collapsable)
with st.sidebar:
    st.markdown("### Color Sphere Studio")
    st.markdown("[Find Pigment Hex Codes Here](https://inkswatch.com/)")
    
    with st.expander("💾 Save / Load Workspace", expanded=False):
        uploaded_file = st.file_uploader("Load Palette (.json)", type=["json"])
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
            mime="application/json"
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
        col3, col4 = st.columns(2)
        with col3:
            name_core = st.text_input("Core Name", key="name_core")
            hex_core = st.color_picker("Core Color", key="hex_core")
            name_heat = st.text_input("Heat Name", key="name_heat")
            hex_heat = st.color_picker("Heat Color", key="hex_heat")
        with col4:
            name_luma = st.text_input("Luma Name", key="name_luma")
            hex_luma = st.color_picker("Luma Color", key="hex_luma")
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

# 3. The WebGL Engine - Height increased to 900 for full screen feel
three_js_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        body {{ margin: 0; overflow: hidden; background-color: #0e1117; cursor: crosshair; user-select: none; }}
        body:active {{ cursor: grabbing; }}
        canvas {{ display: block; }}
        
        #hud {{
            position: absolute; top: 20px; right: 20px; color: #e0e0e0;
            font-family: 'Courier New', Courier, monospace; font-size: 13px;
            background: rgba(15, 17, 23, 0.9); padding: 15px; border-radius: 8px;
            pointer-events: auto; border: 2px solid rgba(255, 255, 255, 0.15);
            width: 280px; box-shadow: 0px 4px 15px rgba(0,0,0,0.5); transition: border-color 0.2s;
        }}
        .hud-section {{ margin-top: 10px; margin-bottom: 5px; color: #ffffff; font-weight: bold; border-bottom: 1px solid #444; padding-bottom: 3px; }}
        .row {{ display: flex; justify-content: space-between; margin-bottom: 2px; }}
        #swatch {{ width: 100%; height: 30px; border-radius: 4px; border: 1px solid #555; margin-bottom: 5px; background-color: #000; }}
        #hex-code {{ text-align: center; font-weight: bold; letter-spacing: 2px; margin-bottom: 5px; color: #fff; }}
        
        #freeze-status {{ text-align: center; color: gold; font-weight: bold; font-size: 11px; margin-bottom: 10px; display: none; }}
        #export-btn {{ display: none; width: 100%; padding: 8px; margin-top: 15px; background: #4CAF50; color: white; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; font-family: inherit; }}
        #export-btn:hover {{ background: #45a049; }}
        
        /* Subtle helper text overlay */
        #helper-text {{
            position: absolute; bottom: 20px; left: 20px; color: rgba(255,255,255,0.4);
            font-family: sans-serif; font-size: 12px; pointer-events: none;
        }}
    </style>
</head>
<body>
    <div id="hud">
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
        <div class="row"><span>{name_core}</span><span id="z-core">0%</span></div>
        <div class="row"><span>Pure Mantle</span><span id="z-pure">0%</span></div>
        <div class="row"><span>{name_luma}</span><span id="z-white">0%</span></div>
        <div class="row"><span>{name_heat}</span><span id="z-orange">0%</span></div>
        <div class="row"><span>{name_crust}</span><span id="z-umber">0%</span></div>
        
        <button id="export-btn">Export Pixel Snapshot to TXT</button>
    </div>
    
    <div id="helper-text">Drag to rotate • Double-click to freeze/export</div>

    <script>
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

                    vec3 darkViolet = {gl_core}; 
                    vec3 baseOrange = {gl_heat};
                    vec3 brightColor = mix(pureColor, {gl_luma}, 0.6); 
                    
                    vec3 resurgentColor = mix(baseOrange, pureColor, 0.65); 
                    vec3 darkUmber = mix({gl_crust}, pureColor, 0.4); 
                    
                    vec3 finalColor = darkViolet;
                    float coreEdge = uShadow * 0.1; 
                    finalColor = mix(finalColor, pureColor, smoothstep(coreEdge, coreEdge + 1.3, r));
                    
                    float crustEdge = 1.88 - (uSun * 0.15); 
                    finalColor = mix(finalColor, brightColor, smoothstep(crustEdge - 0.65, crustEdge - 0.1, r));
                    finalColor = mix(finalColor, resurgentColor, smoothstep(crustEdge - 0.35, crustEdge - 0.02, r));
                    finalColor = mix(finalColor, darkUmber, smoothstep(crustEdge - 0.02, 2.0, r));

                    gl_FragColor = vec4(finalColor, 1.0);
                }}
            `
        }});

        const group = new THREE.Group();
        const sphereGeo = new THREE.SphereGeometry(2, 64, 64);
        group.add(new THREE.Mesh(sphereGeo, material));

        if ({"true" if show_grid else "false"}) {{
            const wireMaterial = new THREE.MeshBasicMaterial({{ 
                color: 0xffffff, wireframe: true, transparent: true, opacity: 0.15 
            }});
            const wireSphere = new THREE.Mesh(sphereGeo, wireMaterial);
            group.add(wireSphere);
        }}

        const wallGeo = new THREE.CircleGeometry(2, 32, 0, Math.PI / 2);
        const wallXY = new THREE.Mesh(wallGeo, material); 
        const wallYZ = new THREE.Mesh(wallGeo, material); wallYZ.rotation.y = -Math.PI / 2; 
        const wallXZ = new THREE.Mesh(wallGeo, material); wallXZ.rotation.x = Math.PI / 2; 
        group.add(wallXY); group.add(wallYZ); group.add(wallXZ);
        scene.add(group);

        camera.position.set(3.464, 3.464, 3.464);
        camera.lookAt(0, 0, 0);

        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        function smoothstep(min, max, value) {{
            let x = Math.max(0, Math.min(1, (value - min) / (max - min)));
            return x * x * (3 - 2 * x);
        }}
        function mixVec(v1, v2, amount) {{
            return [v1[0]*(1-amount) + v2[0]*amount, v1[1]*(1-amount) + v2[1]*amount, v1[2]*(1-amount) + v2[2]*amount];
        }}
        const toHex = (c) => c.toString(16).padStart(2, '0').toUpperCase();

        let isDragging = false;
        let isFrozen = false;
        let lastMousePosition = {{ x: 0, y: 0 }};
        let snapshotData = "";

        document.addEventListener('dblclick', function(e) {{
            if(e.target.closest('#hud')) return; 
            isFrozen = !isFrozen;
            const hud = document.getElementById('hud');
            
            if(isFrozen) {{
                hud.style.borderColor = 'gold';
                document.getElementById('freeze-status').style.display = 'block';
                document.getElementById('export-btn').style.display = 'block';
            }} else {{
                hud.style.borderColor = 'rgba(255, 255, 255, 0.15)';
                document.getElementById('freeze-status').style.display = 'none';
                document.getElementById('export-btn').style.display = 'none';
            }}
        }});

        document.getElementById('export-btn').addEventListener('click', function() {{
            const blob = new Blob([snapshotData], {{ type: 'text/plain' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'PigmentSnapshot_' + document.getElementById('hex-code').innerText + '.txt';
            a.click();
            window.URL.revokeObjectURL(url);
        }});

        document.addEventListener('mousedown', function(e) {{ isDragging = true; }});
        document.addEventListener('mouseup', function(e) {{ isDragging = false; }});
        
        document.addEventListener('mousemove', function(e) {{
            if(isDragging) {{
                let deltaMove = {{ x: e.offsetX - lastMousePosition.x, y: e.offsetY - lastMousePosition.y }};
                customUniforms.uRotY.value += deltaMove.x * 0.01;
                customUniforms.uRotX.value += deltaMove.y * 0.01;
            }}
            lastMousePosition = {{ x: e.offsetX, y: e.offsetY }};

            if(isFrozen) return;

            mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);

            const intersectableObjects = group.children.filter(child => child.material.wireframe !== true);
            const intersects = raycaster.intersectObjects(intersectableObjects);
            
            let hitPoint = null;
            for(let i = 0; i < intersects.length; i++) {{
                let pt = intersects[i].point;
                if(pt.x > 0.001 && pt.y > 0.001 && pt.z > 0.001) continue; 
                hitPoint = pt;
                break;
            }}

            if(hitPoint) {{
                let r = Math.sqrt(hitPoint.x*hitPoint.x + hitPoint.y*hitPoint.y + hitPoint.z*hitPoint.z);
                let cx = Math.cos(customUniforms.uRotX.value), sx = Math.sin(customUniforms.uRotX.value);
                let cy = Math.cos(customUniforms.uRotY.value), sy = Math.sin(customUniforms.uRotY.value);
                
                let v1x = cy * hitPoint.x - sy * hitPoint.z;
                let v1y = hitPoint.y;
                let v1z = sy * hitPoint.x + cy * hitPoint.z;
                let spinPos = {{ x: v1x, y: cx * v1y + sx * v1z, z: -sx * v1y + cx * v1z }};
                
                let len = Math.sqrt(spinPos.x*spinPos.x + spinPos.y*spinPos.y + spinPos.z*spinPos.z);
                let n = {{ x: spinPos.x/len, y: spinPos.y/len, z: spinPos.z/len }};

                let wX = Math.pow(Math.abs(n.x), {brilliance});
                let wY = Math.pow(Math.abs(n.y), {brilliance});
                let wZ = Math.pow(Math.abs(n.z), {brilliance});
                let tot = wX + wY + wZ;
                wX /= tot; wY /= tot; wZ /= tot;

                let pr = (n.y > 0 ? (wY*100) : 0).toFixed(1);
                let pc = (n.y <= 0 ? (wY*100) : 0).toFixed(1);
                let py = (n.x > 0 ? (wX*100) : 0).toFixed(1);
                let pb = (n.x <= 0 ? (wX*100) : 0).toFixed(1);
                let pg = (n.z > 0 ? (wZ*100) : 0).toFixed(1);
                let pm = (n.z <= 0 ? (wZ*100) : 0).toFixed(1);

                document.getElementById('p-yp').innerText = pr + '%';
                document.getElementById('p-yn').innerText = pc + '%';
                document.getElementById('p-xp').innerText = py + '%';
                document.getElementById('p-xn').innerText = pb + '%';
                document.getElementById('p-zp').innerText = pg + '%';
                document.getElementById('p-zn').innerText = pm + '%';

                let coreEdge = {shadow_depth} * 0.1; 
                let crustEdge = 1.88 - ({sun_intensity} * 0.15);
                
                let v1 = smoothstep(coreEdge, coreEdge + 1.3, r);
                let v2 = smoothstep(crustEdge - 0.65, crustEdge - 0.1, r);
                let v3 = smoothstep(crustEdge - 0.35, crustEdge - 0.02, r);
                let v4 = smoothstep(crustEdge - 0.02, 2.0, r);

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
                
                let colorY = n.y > 0 ? {js_yp} : {js_yn};
                let colorX = n.x > 0 ? {js_xp} : {js_xn};
                let colorZ = n.z > 0 ? {js_zp} : {js_zn};

                let pureRGB = [
                    colorX[0]*wX + colorY[0]*wY + colorZ[0]*wZ,
                    colorX[1]*wX + colorY[1]*wY + colorZ[1]*wZ,
                    colorX[2]*wX + colorY[2]*wY + colorZ[2]*wZ
                ];

                let fColor = {js_core}; 
                fColor = mixVec(fColor, pureRGB, v1);
                fColor = mixVec(fColor, mixVec(pureRGB, {js_luma}, 0.6), v2);
                fColor = mixVec(fColor, mixVec({js_heat}, pureRGB, 0.65), v3);
                fColor = mixVec(fColor, mixVec({js_crust}, pureRGB, 0.4), v4);
                
                let rVal = Math.round(fColor[0]*255);
                let gVal = Math.round(fColor[1]*255);
                let bVal = Math.round(fColor[2]*255);
                let hexStr = "#" + toHex(rVal) + toHex(gVal) + toHex(bVal);

                document.getElementById('swatch').style.backgroundColor = `rgb(${{rVal}}, ${{gVal}}, ${{bVal}})`;
                document.getElementById('hex-code').innerText = hexStr;
                
                let degX = (customUniforms.uRotX.value * 180 / Math.PI) % 360;
                let degY = (customUniforms.uRotY.value * 180 / Math.PI) % 360;
                if (degX < 0) degX += 360;
                if (degY < 0) degY += 360;

                snapshotData = `CUSTOM PIGMENT SPHERE SNAPSHOT
------------------------------
Final Hex Code:  ${{hexStr}}
Final RGB Value: (${{rVal}}, ${{gVal}}, ${{bVal}})

PIGMENT BLEND
-------------
{name_y_pos}: ${{pr}}%
{name_y_neg}: ${{pc}}%
{name_x_pos}: ${{py}}%
{name_x_neg}: ${{pb}}%
{name_z_pos}: ${{pg}}%
{name_z_neg}: ${{pm}}%

ATMOSPHERIC DEPTH
-----------------
{name_core}: ${{zCore}}%
Pure Mantle: ${{zPure}}%
{name_luma}: ${{zWhite}}%
{name_heat}: ${{zOrange}}%
{name_crust}: ${{zUmber}}%

RESTORATION COORDINATES
-----------------------
Latitude:  ${{Math.round(degX)}}
Longitude: ${{Math.round(degY)}}
`;

            }} else {{
                document.querySelectorAll('.row span:nth-child(2)').forEach(el => el.innerText = '0%');
                document.getElementById('swatch').style.backgroundColor = '#000';
                document.getElementById('hex-code').innerText = '-------';
                snapshotData = "";
            }}
        }});

        // Handle window resizing smoothly
        window.addEventListener('resize', onWindowResize, false);
        function onWindowResize() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }}

        function animate() {{
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
        }}
        animate();
    </script>
</body>
</html>
"""

components.html(three_js_code, height=900)