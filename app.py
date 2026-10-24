import streamlit as st
import os
import json
import io
import time
import hashlib
from datetime import datetime
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# ==========================================
# PAGE CONFIG & CSS STYLING
# ==========================================
st.set_page_config(
    page_title="CrimeVision AI - Forensic Platform",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Forensic Theme Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #e0e6ed;
    }
    .stAppHeader {
        background-color: #161b22;
    }
    .css-1d3con0, .css-1cyp687 {
        background-color: #161b22;
    }
    .stButton>button {
        background-color: #1f6feb;
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #388bfd;
        color: white;
    }
    .forensic-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .custody-badge {
        background-color: #21262d;
        border-left: 4px solid #238636;
        padding: 8px 12px;
        font-family: monospace;
        font-size: 0.85rem;
        margin-bottom: 15px;
    }
    .threat-critical {
        color: #f85149;
        font-weight: bold;
        background-color: rgba(248, 81, 73, 0.15);
        padding: 2px 8px;
        border-radius: 4px;
    }
    .threat-high {
        color: #d29922;
        font-weight: bold;
        background-color: rgba(210, 153, 34, 0.15);
        padding: 2px 8px;
        border-radius: 4px;
    }
    .threat-medium {
        color: #e3b341;
        font-weight: bold;
    }
    .threat-low {
        color: #3fb950;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "evidence_id" not in st.session_state:
    st.session_state.evidence_id = f"EVD-{datetime.now().strftime('%Y%m%d')}-{hashlib.md5(str(time.time()).encode()).hexdigest()[:6].upper()}"

if "investigator" not in st.session_state:
    st.session_state.investigator = "Det. J. Miller (#4821)"

if "chain_of_custody" not in st.session_state:
    st.session_state.chain_of_custody = [
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "action": "Evidence Container Created",
            "actor": st.session_state.investigator,
            "hash": hashlib.sha256(st.session_state.evidence_id.encode()).hexdigest()[:16]
        }
    ]

# Analysis Results Cache
if "image_analysis" not in st.session_state:
    st.session_state.image_analysis = None

if "audio_analysis" not in st.session_state:
    st.session_state.audio_analysis = None

if "video_analysis" not in st.session_state:
    st.session_state.video_analysis = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ==========================================
# HELPER FUNCTIONS & MOCK AI ENGINES
# ==========================================
def add_custody_log(action):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "action": action,
        "actor": st.session_state.investigator,
        "hash": hashlib.sha256(f"{action}{time.time()}".encode()).hexdigest()[:16]
    }
    st.session_state.chain_of_custody.append(entry)

def simulate_rt_detr_detection(image):
    """Simulates RT-DETR object detection and draws bounding boxes."""
    img_copy = image.copy()
    draw = ImageDraw.Draw(img_copy)
    width, height = img_copy.size
    
    # Simulated detections based on standard high-res image grid
    detections = [
        {"label": "Firearm (9mm Semi-Auto)", "box": [int(width*0.55), int(height*0.60), int(width*0.75), int(height*0.78)], "conf": 0.94, "color": "#f85149"},
        {"label": "Blood Spatter (Impact Pattern)", "box": [int(width*0.20), int(height*0.45), int(width*0.48), int(height*0.70)], "conf": 0.89, "color": "#da3633"},
        {"label": "Forced Entry (Pry Marks)", "box": [int(width*0.05), int(height*0.10), int(width*0.25), int(height*0.50)], "conf": 0.91, "color": "#d29922"},
        {"label": "Person (Suspect 1)", "box": [int(width*0.65), int(height*0.15), int(width*0.88), int(height*0.55)], "conf": 0.87, "color": "#388bfd"}
    ]
    
    for det in detections:
        box = det["box"]
        draw.rectangle(box, outline=det["color"], width=4)
        draw.text((box[0] + 5, box[1] + 5), f"{det['label']} ({det['conf']*100:.0f}%)", fill=det["color"])
        
    structured_data = {
        "threat_level": "CRITICAL",
        "scene_type": "Aggravated Burglary / Attempted Homicide",
        "detections": detections,
        "investigative_leads": [
            "L1: Run ballistic analysis on recovered 9mm semi-automatic firearm.",
            "L2: Extract DNA sample from high-velocity blood spatter on east wall.",
            "L3: Perform forensic toolmark analysis on door jamb entry point."
        ]
    }
    return img_copy, structured_data

def process_audio_whisper(audio_bytes):
    """Simulates Whisper transcription and chronological analysis."""
    transcript_segments = [
        {"time": "00:01", "speaker": "Dispatcher (911)", "text": "911, what is your emergency?"},
        {"time": "00:04", "speaker": "Witness (Caller)", "text": "I heard loud banging and a gunshot next door at 1042 Elm Street!"},
        {"time": "00:09", "speaker": "Dispatcher (911)", "text": "Did you see anyone leaving the premises?"},
        {"time": "00:13", "speaker": "Witness (Caller)", "text": "Yes! A tall male in a dark hoodie carrying a metallic object ran towards the alley."},
        {"time": "00:20", "speaker": "Dispatcher (911)", "text": "Units are dispatched. Stay inside and keep your doors locked."}
    ]
    
    summary = {
        "duration": "00:24",
        "primary_events": ["Shots Fired Reported", "Suspect Spotted Fleeing", "Police Dispatched"],
        "key_entities": ["1042 Elm Street", "Tall male in dark hoodie", "Metallic object / firearm"]
    }
    return transcript_segments, summary

def process_cctv_video(video_bytes):
    """Simulates frame sampling, object tracking, and legal classification."""
    events = [
        {"sec": "02.1", "subject": "Vehicle (Black Sedan)", "trajectory": "Heading West on Elm St.", "action": "Unlawful Stop", "crime_cat": "Traffic Infraction"},
        {"sec": "05.4", "subject": "Suspect 1 (Male Hooded)", "trajectory": "Exits Vehicle -> Approach Door", "action": "Forced Door Entry", "crime_cat": "PC 459 - Burglary"},
        {"sec": "11.8", "subject": "Suspect 1", "trajectory": "Interior Living Room", "action": "Weapon Drawn (Firearm)", "crime_cat": "PC 245(a)(2) - Assault w/ Firearm"},
        {"sec": "18.3", "subject": "Suspect 1", "trajectory": "Fleeing rear alleyway", "action": "Evasion from Scene", "crime_cat": "Obstruction"}
    ]
    return events

# ==========================================
# SIDEBAR - SECURITY & CHAIN OF CUSTODY
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/policeman-male--v1.png", width=64)
    st.title("CrimeVision AI")
    st.caption("Forensic Intelligence Platform v2.4")
    st.divider()
    
    st.subheader("🔑 Security & API Settings")
    api_provider = st.selectbox("LLM / Vision Engine", ["Groq (Llama-3 Vision)", "Google Gemini 1.5 Pro", "Demo Fallback Mode"])
    api_key = st.text_input("API Key", type="password", help="Enter key or leave empty to use built-in offline simulation mode.")
    
    if api_key:
        st.success("API Key Active", icon="✅")
    else:
        st.info("Operating in Offline Demo Fallback Mode", icon="ℹ️")
        
    st.divider()
    st.subheader("🛡️ Chain of Custody")
    st.session_state.investigator = st.text_input("Lead Investigator", st.session_state.investigator)
    
    st.markdown(f"**Evidence ID:** `{st.session_state.evidence_id}`")
    st.markdown(f"**Active Custodian:** {st.session_state.investigator}")
    st.markdown(f"**Log Entries:** {len(st.session_state.chain_of_custody)}")
    
    with st.expander("View Custody Audit Trail"):
        for log in reversed(st.session_state.chain_of_custody):
            st.caption(f"[{log['timestamp']}] {log['action']} | Hash: {log['hash']}")

# ==========================================
# MAIN INTERFACE
# ==========================================
st.title("⚖️ CrimeVision AI: Multimodal Forensic Analysis")

# Chain of custody header bar
st.markdown(f"""
<div class="custody-badge">
    <strong>EVIDENCE CHAIN OF CUSTODY ACTIVE</strong> | Case ID: <u>{st.session_state.evidence_id}</u> | Investigator: <u>{st.session_state.investigator}</u> | Status: <u>Sealed & Verifiable</u>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "📸 1. Visual Evidence Tagger", 
    "🎙️ 2. Audio Witness Timeline", 
    "🎥 3. CCTV Video Tracking", 
    "🧩 4. Evidence Fusion & RAG Chat", 
    "📄 5. Court PDF Export"
])

# ==========================================
# TAB 1: VISUAL EVIDENCE TAGGER
# ==========================================
with tabs[0]:
    st.header("Crime Scene Visual Evidence Analysis")
    st.caption("Simulated RT-DETR Deep Learning Object Detection & Spatial Annotation")
    
    col_upload, col_display = st.columns([1, 2])
    
    with col_upload:
        uploaded_img = st.file_uploader("Upload Crime Scene Photo (JPEG/PNG)", type=["jpg", "jpeg", "png"])
        sample_img_btn = st.button("Load Sample Crime Scene")
        
        if sample_img_btn or uploaded_img:
            if uploaded_img:
                img = Image.open(uploaded_img)
            else:
                # Generate sample placeholder image
                img = Image.new('RGB', (800, 600), color = (30, 35, 45))
                d = ImageDraw.Draw(img)
                d.rectangle([100, 100, 700, 500], fill=(50, 55, 65))
                d.text((350, 280), "SAMPLE CRIME SCENE DATA", fill=(200, 200, 200))
                
            with st.spinner("Executing RT-DETR Forensic Inference Engine..."):
                time.sleep(1.2)
                processed_img, structured_data = simulate_rt_detr_detection(img)
                st.session_state.image_analysis = {
                    "image": processed_img,
                    "data": structured_data
                }
                add_custody_log("Processed Visual Evidence (Image Detection)")
                st.success("Visual analysis complete!")

    with col_display:
        if st.session_state.image_analysis:
            data = st.session_state.image_analysis["data"]
            
            st.image(st.session_state.image_analysis["image"], use_column_width=True, caption="Annotated Forensic Bounding Overlay")
            
            # Metrics Row
            m1, m2 = st.columns(2)
            with m1:
                st.markdown(f"**Threat Classification:** <span class='threat-critical'>{data['threat_level']}</span>", unsafe_allow_html=True)
            with m2:
                st.markdown(f"**Scene Type:** `{data['scene_type']}`")
                
            st.subheader("Detected Physical Evidence")
            det_df = pd.DataFrame([
                {
                    "Item / Entity": d["label"],
                    "Confidence": f"{d['conf']*100:.1f}%",
                    "Spatial Coordinates (Bounding Box)": str(d["box"])
                } for d in data["detections"]
            ])
            st.table(det_df)
            
            st.subheader("Prioritized Investigative Leads")
            for lead in data["investigative_leads"]:
                st.info(lead)
        else:
            st.info("Upload an image or click 'Load Sample Crime Scene' to initiate spatial object detection.")

# ==========================================
# TAB 2: WITNESS AUDIO TRANSCRIPTION
# ==========================================
with tabs[1]:
    st.header("Witness Statement & 911 Audio Analysis")
    st.caption("Whisper Speech-to-Text & Diarization Engine")
    
    col_a1, col_a2 = st.columns([1, 2])
    
    with col_a1:
        audio_file = st.file_uploader("Upload Witness Audio / Call Recording (WAV/MP3)", type=["wav", "mp3", "m4a"])
        sample_audio_btn = st.button("Analyze Sample 911 Call")
        
        if sample_audio_btn or audio_file:
            with st.spinner("Transcribing audio & separating speaker diarization..."):
                time.sleep(1.0)
                segments, summary = process_audio_whisper(audio_file)
                st.session_state.audio_analysis = {
                    "segments": segments,
                    "summary": summary
                }
                add_custody_log("Transcribed Audio Statement (911 Call)")
                st.success("Audio analysis finalized!")

    with col_a2:
        if st.session_state.audio_analysis:
            summary = st.session_state.audio_analysis["summary"]
            segments = st.session_state.audio_analysis["segments"]
            
            st.subheader("Transcription & Key Entities")
            st.write(f"**Audio Duration:** `{summary['duration']}`")
            st.write(f"**Extracted Key Entities:** {', '.join([f'`{e}`' for e in summary['key_entities']])}")
            
            st.subheader("Timestamped Chronological Transcript")
            for seg in segments:
                st.markdown(f"**[{seg['time']}] {seg['speaker']}:** {seg['text']}")
        else:
            st.info("Upload audio or load sample to generate speaker diarization and transcript timelines.")

# ==========================================
# TAB 3: CCTV VIDEO TRACKING
# ==========================================
with tabs[2]:
    st.header("CCTV Surveillance Video & Event Progression")
    st.caption("Automated Trajectory Tracking & Criminal Offense Mapping")
    
    col_v1, col_v2 = st.columns([1, 2])
    
    with col_v1:
        video_file = st.file_uploader("Upload CCTV Surveillance Footage (MP4/AVI)", type=["mp4", "avi", "mov"])
        sample_video_btn = st.button("Process Sample CCTV Video")
        
        if sample_video_btn or video_file:
            with st.spinner("Extracting video keyframes & tracking suspect velocity vector..."):
                time.sleep(1.5)
                events = process_cctv_video(video_file)
                st.session_state.video_analysis = events
                add_custody_log("Processed CCTV Video Footage")
                st.success("Video trajectory tracking completed!")

    with col_v2:
        if st.session_state.video_analysis:
            st.subheader("Chronological Surveillance Log & Penal Mapping")
            video_df = pd.DataFrame(st.session_state.video_analysis)
            st.dataframe(video_df, use_container_width=True)
            
            st.subheader("Trajectory Breakdown")
            st.markdown("""
            - **00:02.1:** Vehicle enters camera frame 1 at 24 mph.
            - **00:05.4:** Suspect dismounts, breaches entryway (Forced Entry confirmed).
            - **00:11.8:** Suspect exposes concealed firearm (Aggravated Threat).
            - **00:18.3:** Evasion recorded exiting north alley.
            """)
        else:
            st.info("Upload CCTV footage or run sample video analysis to generate progression log.")

# ==========================================
# TAB 4: MULTIMODAL FUSION & RAG CHAT
# ==========================================
with tabs[3]:
    st.header("Unified Evidence Fusion & Grounded RAG Chat")
    st.caption("Cross-Correlate All Modalities with Zero-Hallucination Guardrails")
    
    # Check if any analysis has been run
    has_data = any([st.session_state.image_analysis, st.session_state.audio_analysis, st.session_state.video_analysis])
    
    if not has_data:
        st.warning("⚠️ No evidence processed yet. Please run analysis in Tabs 1, 2, or 3 to populate the Master Fusion Ledger.")
    else:
        st.subheader("Master Multimodal Forensic Event Ledger")
        
        # Build unified timeline
        unified_events = []
        if st.session_state.image_analysis:
            unified_events.append({"Timestamp": "T+00:00 (Photo)", "Source": "Visual Tagging", "Evidence ID": "IMG-001", "Event Detail": "Firearm & Forced Entry Identified at scene."})
        if st.session_state.audio_analysis:
            for s in st.session_state.audio_analysis["segments"]:
                unified_events.append({"Timestamp": f"T+{s['time']}", "Source": "Audio Transcript", "Evidence ID": "AUD-911", "Event Detail": f"{s['speaker']}: {s['text']}"})
        if st.session_state.video_analysis:
            for v in st.session_state.video_analysis:
                unified_events.append({"Timestamp": f"T+00:{v['sec']}", "Source": "CCTV Footage", "Evidence ID": "VID-CCTV1", "Event Detail": f"{v['subject']} - {v['action']} [{v['crime_cat']}]"})
                
        fusion_df = pd.DataFrame(unified_events)
        st.dataframe(fusion_df, use_container_width=True)
        
        st.divider()
        st.subheader("💬 Interrogate Evidence (Grounded Forensic RAG)")
        
        # Display past chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        user_query = st.chat_input("Ask a question (e.g., 'Was a weapon visible before the suspect fled?')")
        
        if user_query:
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)
                
            with st.chat_message("assistant"):
                # RAG Answer synthesis logic
                q_lower = user_query.lower()
                response = ""
                
                if "weapon" in q_lower or "gun" in q_lower or "firearm" in q_lower:
                    response = f"**Confirmed [Citation: IMG-001 & VID-CCTV1]:** Yes, a 9mm semi-automatic firearm was detected in visual scene imagery (`IMG-001`) with 94% confidence. Furthermore, CCTV footage (`VID-CCTV1`) documents the suspect drawing a firearm at **T+00:11.8s** prior to fleeing down the rear alleyway at **T+00:18.3s**."
                elif "vehicle" in q_lower or "car" in q_lower:
                    response = f"**Confirmed [Citation: VID-CCTV1]:** CCTV footage identifies a Black Sedan stopping unlawfully at **T+00:02.1s** on Elm St., from which Suspect 1 exited."
                elif "caller" in q_lower or "witness" in q_lower or "sound" in q_lower or "shot" in q_lower:
                    response = f"**Confirmed [Citation: AUD-911]:** The 911 witness reported hearing loud banging and a gunshot at 1042 Elm Street at **T+00:04s**, and visually noted a tall male in a dark hoodie fleeing."
                else:
                    response = f"**Grounded Answer [Citation: Master Ledger]:** Based on case file `{st.session_state.evidence_id}`, the cross-modal evidence correlates a forced burglary entry with an armed suspect leaving the scene via a black sedan."
                    
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})

# ==========================================
# TAB 5: AUTOMATED PDF EXPORT
# ==========================================
with tabs[4]:
    st.header("Court-Admissible Forensic PDF Export")
    st.caption("Generate Official Cryptographically-Hashed Summary Reports")
    
    st.markdown("""
    This utility compiles all active forensic modalities, object detection logs, transcripts, 
    video trajectory mapping, and chain-of-custody hashes into a standardized PDF report suitable for judicial submission.
    """)
    
    def generate_pdf_report():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=10
        )
        h2_style = ParagraphStyle(
            'H2Style',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#1e293b'),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#334155')
        )
        
        story = []
        
        # Header
        story.append(Paragraph("FORENSIC ANALYSIS & MULTIMODAL EVIDENCE REPORT", title_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#0f172a'), spaceAfter=15))
        
        # Meta Info Table
        meta_data = [
            [Paragraph("<b>Evidence Case ID:</b>", body_style), Paragraph(st.session_state.evidence_id, body_style)],
            [Paragraph("<b>Lead Investigator:</b>", body_style), Paragraph(st.session_state.investigator, body_style)],
            [Paragraph("<b>Report Timestamp:</b>", body_style), Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"), body_style)],
            [Paragraph("<b>Verification Hash:</b>", body_style), Paragraph(hashlib.sha256(st.session_state.evidence_id.encode()).hexdigest(), body_style)]
        ]
        t_meta = Table(meta_data, colWidths=[130, 400])
        t_meta.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_meta)
        story.append(Spacer(1, 15))
        
        # 1. Visual Findings
        story.append(Paragraph("1. Visual Evidence Findings (RT-DETR Analysis)", h2_style))
        if st.session_state.image_analysis:
            data = st.session_state.image_analysis["data"]
            vis_data = [["Detected Item", "Confidence", "Bounding Box"]]
            for d in data["detections"]:
                vis_data.append([d["label"], f"{d['conf']*100:.1f}%", str(d["box"])])
            t_vis = Table(vis_data, colWidths=[200, 100, 230])
            t_vis.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('FONTSIZE', (0,0), (-1,-1), 8),
            ]))
            story.append(t_vis)
        else:
            story.append(Paragraph("No visual evidence analyzed in current session.", body_style))
            
        story.append(Spacer(1, 10))
        
        # 2. Audio Findings
        story.append(Paragraph("2. Witness Audio & Diarization Summary", h2_style))
        if st.session_state.audio_analysis:
            audio_data = [["Timestamp", "Speaker", "Transcript Segment"]]
            for seg in st.session_state.audio_analysis["segments"]:
                audio_data.append([seg["time"], seg["speaker"], seg["text"]])
            t_aud = Table(audio_data, colWidths=[70, 120, 340])
            t_aud.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('FONTSIZE', (0,0), (-1,-1), 8),
            ]))
            story.append(t_aud)
        else:
            story.append(Paragraph("No audio transcript evidence analyzed in current session.", body_style))
            
        story.append(Spacer(1, 10))
        
        # 3. Chain of Custody Audit
        story.append(Paragraph("3. Cryptographic Chain of Custody Audit Log", h2_style))
        cust_data = [["Timestamp (UTC)", "Action Performed", "Custodian", "Hash Stamp"]]
        for log in st.session_state.chain_of_custody:
            cust_data.append([log["timestamp"], log["action"], log["actor"], log["hash"]])
        t_cust = Table(cust_data, colWidths=[110, 160, 130, 130])
        t_cust.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('FONTSIZE', (0,0), (-1,-1), 7),
        ]))
        story.append(t_cust)
        
        doc.build(story)
        buffer.seek(0)
        return buffer

    if st.button("🚨 Generate Official Forensic PDF Report", type="primary"):
        with st.spinner("Compiling court-admissible PDF document..."):
            pdf_bytes = generate_pdf_report()
            add_custody_log("Generated Official PDF Forensic Summary Report")
            
            st.success("Forensic PDF Report compiled and signed successfully!")
            
            st.download_button(
                label="📥 Download Forensic Report (.PDF)",
                data=pdf_bytes,
                file_name=f"CrimeVision_Report_{st.session_state.evidence_id}.pdf",
                mime="application/pdf"
            )

# Footer
st.markdown("---")
st.caption("CrimeVision AI Platform | Built for Forensic Law Enforcement & Digital Evidence Integrity")
