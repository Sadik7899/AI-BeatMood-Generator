import streamlit as st
import json
import os
from datetime import datetime
import time
import requests

# Page configuration
st.set_page_config(
    page_title="AI BeatMood Generator",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #FF6B6B;
        transform: translateY(-2px);
    }
    .music-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .mood-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .genre-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    h1 {
        color: #667eea;
        text-align: center;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    h2 {
        color: #764ba2;
    }
    .stTextArea textarea {
        border-radius: 10px;
    }
    .stSelectbox {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'history' not in st.session_state:
    st.session_state.history = []

def generate_music_content(prompt, api_key):
    """Generate music-related content using Groq (Llama 3.1 - FREE)"""
    try:
        if not api_key:
            st.error("⚠️ Please enter your Groq API key!")
            return None
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama-3.1-8b-instant",  # Using faster 8B model
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        # Better error handling
        if response.status_code != 200:
            error_detail = response.json() if response.text else "Unknown error"
            st.error(f"API Error ({response.status_code}): {error_detail}")
            return None
            
        result = response.json()
        return result["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None
    except KeyError as e:
        st.error(f"Response format error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def create_remix_prompt(song_name, artist, original_genre, target_genre, mood, additional_info):
    """Create a detailed prompt for music remix suggestions"""
    prompt = f"""As an expert music producer and AI music assistant, provide detailed remix suggestions for the following:

Song: {song_name}
Artist: {artist}
Original Genre: {original_genre}
Target Genre: {target_genre}
Desired Mood: {mood}
Additional Information: {additional_info}

Please provide:
1. **Remix Concept**: A creative concept for transforming this song
2. **Musical Elements to Change**:
   - Tempo adjustments (BPM suggestions)
   - Key/scale modifications
   - Rhythm patterns
   - Instrumentation changes
3. **Production Techniques**:
   - Effects to apply (reverb, delay, distortion, etc.)
   - Mixing suggestions
   - Sound design ideas
4. **Arrangement Ideas**:
   - Intro/outro modifications
   - Verse/chorus transformations
   - Bridge and breakdown suggestions
5. **Genre-Specific Elements**: What makes this remix fit the {target_genre} genre
6. **Mood Enhancement**: How to achieve the {mood} feeling
7. **Creative Additions**: Unique elements that would make this remix stand out

Format your response in a clear, organized manner with sections and bullet points."""
    
    return prompt

def create_mood_music_prompt(mood, genre, duration, instruments, purpose):
    """Create a prompt for generating original mood-based music"""
    prompt = f"""As an expert music composer and AI music assistant, create a detailed composition guide for original music with these specifications:

Mood: {mood}
Genre: {genre}
Duration: {duration}
Preferred Instruments: {instruments}
Purpose: {purpose}

Please provide:
1. **Composition Overview**: A brief description of the overall piece
2. **Musical Structure**:
   - Song structure (intro, verse, chorus, bridge, outro with timings)
   - Chord progressions with specific chords
   - Melodic ideas and motifs
3. **Instrumentation Details**:
   - Main instruments and their roles
   - Layering suggestions
   - Sound palette recommendations
4. **Rhythm & Tempo**:
   - BPM recommendation
   - Time signature
   - Rhythmic patterns for each section
5. **Mood Elements**:
   - Specific techniques to evoke {mood}
   - Dynamics (loud/soft sections)
   - Emotional arc of the piece
6. **Production Notes**:
   - Mixing suggestions
   - Effects and processing
   - Spatial arrangement (stereo field)
7. **Creative Flourishes**: Unique elements that enhance the composition
8. **Reference Tracks**: Similar songs or artists for inspiration

Format your response clearly with sections and detailed explanations."""
    
    return prompt

def create_genre_transformation_prompt(description, from_genre, to_genre):
    """Create a prompt for genre transformation"""
    prompt = f"""As an expert music producer specializing in genre transformation, help transform a musical idea:

Musical Description: {description}
From Genre: {from_genre}
To Genre: {to_genre}

Please provide:
1. **Transformation Strategy**: Overall approach to the genre shift
2. **Core Elements to Preserve**: What should stay from the original
3. **Elements to Transform**:
   - Instrumentation changes
   - Rhythm and groove modifications
   - Harmonic adjustments
   - Melodic adaptations
4. **Genre-Specific Techniques**: Key characteristics of {to_genre} to incorporate
5. **Production Style**: How production should change
6. **Arrangement Modifications**: Structural changes needed
7. **Examples**: Similar successful genre transformations
8. **Step-by-Step Guide**: Practical steps to achieve this transformation

Provide detailed, actionable advice that a student can understand and apply."""
    
    return prompt

# Main App
def main():
    # Header
    st.markdown("<h1>🎵 AI BeatMood Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>Create amazing music remixes and mood-based compositions with AI assistance</p>", unsafe_allow_html=True)
    
    # Sidebar for API configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Groq API Key (FREE)",
            type="password",
            value=st.session_state.api_key,
            help="Get your FREE API key from https://console.groq.com/keys"
        )
        
        if api_key:
            st.session_state.api_key = api_key
            st.success("✅ API Key configured!")
        else:
            st.warning("⚠️ Please enter your Groq API key to use the app")
            st.info("📝 Get your FREE API key from [Groq Console](https://console.groq.com/keys) - No credit card required!")
        
        st.divider()
        
        # Information
        st.header("ℹ️ About")
        st.markdown("""
        This app helps you:
        - 🎧 Get AI-powered remix suggestions
        - 🎼 Generate mood-based music ideas
        - 🎸 Transform songs between genres
        - 🎹 Learn music production techniques
        
        **No technical skills required!**
        """)
        
        st.divider()
        
        # History
        if st.session_state.history:
            st.header("📜 Recent Generations")
            for i, item in enumerate(reversed(st.session_state.history[-5:])):
                with st.expander(f"{item['type']} - {item['timestamp']}", expanded=False):
                    st.write(item['summary'])
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎧 Remix Generator", "🎼 Mood Music Creator", "🎸 Genre Transformer", "📚 Music Theory Helper"])
    
    # Tab 1: Remix Generator
    with tab1:
        st.header("🎧 AI BeatMood Generator")
        st.markdown("Transform existing songs into new remixes with AI-powered suggestions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            song_name = st.text_input("🎵 Song Name", placeholder="e.g., Blinding Lights")
            artist = st.text_input("👤 Artist", placeholder="e.g., The Weeknd")
            original_genre = st.selectbox(
                "🎼 Original Genre",
                ["Pop", "Rock", "Hip-Hop", "EDM", "Jazz", "Classical", "R&B", "Country", "Reggae", "Metal", "Folk", "Blues", "Other"]
            )
        
        with col2:
            target_genre = st.selectbox(
                "🎯 Target Genre (Remix Style)",
                ["EDM", "Lo-fi Hip-Hop", "Acoustic", "Jazz", "Orchestral", "Trap", "House", "Dubstep", "Reggaeton", "Synthwave", "Ambient", "Drum & Bass", "Other"]
            )
            mood = st.selectbox(
                "😊 Desired Mood",
                ["Energetic", "Chill/Relaxed", "Dark/Mysterious", "Happy/Uplifting", "Melancholic", "Aggressive", "Romantic", "Dreamy", "Epic", "Funky"]
            )
        
        additional_info = st.text_area(
            "📝 Additional Information (Optional)",
            placeholder="Any specific elements you want to keep or change? Favorite parts of the song? Specific instruments you want to add?",
            height=100
        )
        
        if st.button("🎨 Generate Remix Ideas", key="remix_btn"):
            if not st.session_state.api_key:
                st.error("⚠️ Please enter your Groq API key in the sidebar first!")
            elif not song_name or not artist:
                st.warning("⚠️ Please enter both song name and artist!")
            else:
                with st.spinner("🎵 Generating creative remix ideas..."):
                    prompt = create_remix_prompt(song_name, artist, original_genre, target_genre, mood, additional_info)
                    result = generate_music_content(prompt, st.session_state.api_key)
                    
                    if result:
                        st.markdown("<div class='music-card'>", unsafe_allow_html=True)
                        st.markdown(f"### 🎧 Remix Ideas: {song_name} ({target_genre} Remix)")
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown(result)
                        
                        # Add to history
                        st.session_state.history.append({
                            'type': 'Remix',
                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                            'summary': f"{song_name} → {target_genre}"
                        })
                        
                        # Download button
                        st.download_button(
                            label="💾 Download Remix Ideas",
                            data=result,
                            file_name=f"remix_{song_name.replace(' ', '_')}_{target_genre}.txt",
                            mime="text/plain"
                        )
    
    # Tab 2: Mood Music Creator
    with tab2:
        st.header("🎼 Mood-Based Music Creator")
        st.markdown("Generate original music compositions based on mood and purpose")
        
        col1, col2 = st.columns(2)
        
        with col1:
            mood_select = st.selectbox(
                "😊 Select Mood",
                ["Happy & Uplifting", "Calm & Peaceful", "Energetic & Motivating", "Sad & Melancholic", 
                 "Dark & Mysterious", "Romantic & Intimate", "Epic & Cinematic", "Funky & Groovy",
                 "Dreamy & Ethereal", "Aggressive & Intense"],
                key="mood_select"
            )
            
            genre_select = st.selectbox(
                "🎼 Genre",
                ["Pop", "Electronic", "Ambient", "Classical", "Jazz", "Rock", "Hip-Hop", "Lo-fi",
                 "Cinematic", "World Music", "Experimental", "R&B"],
                key="genre_select"
            )
            
            duration = st.selectbox(
                "⏱️ Duration",
                ["30 seconds (Short)", "1-2 minutes (Medium)", "3-4 minutes (Full Song)", "5+ minutes (Extended)"]
            )
        
        with col2:
            instruments = st.multiselect(
                "🎹 Preferred Instruments",
                ["Piano", "Guitar", "Synthesizer", "Drums", "Bass", "Strings", "Brass", "Vocals",
                 "Flute", "Saxophone", "Violin", "Electronic Beats", "Ambient Pads", "Percussion"],
                default=["Piano", "Synthesizer"]
            )
            
            purpose = st.selectbox(
                "🎯 Purpose",
                ["Background Music", "Study/Focus", "Workout/Exercise", "Meditation/Relaxation",
                 "Party/Dancing", "Gaming", "Film/Video", "Personal Enjoyment", "Creative Project"]
            )
        
        additional_notes = st.text_area(
            "📝 Additional Notes (Optional)",
            placeholder="Any specific ideas, references, or requirements?",
            height=100,
            key="mood_notes"
        )
        
        if st.button("🎼 Generate Music Composition", key="mood_btn"):
            if not st.session_state.api_key:
                st.error("⚠️ Please enter your Groq API key in the sidebar first!")
            else:
                with st.spinner("🎵 Composing your music..."):
                    instruments_str = ", ".join(instruments) if instruments else "Any suitable instruments"
                    full_notes = f"{additional_notes}\n\nAdditional context: {purpose}" if additional_notes else purpose
                    
                    prompt = create_mood_music_prompt(mood_select, genre_select, duration, instruments_str, full_notes)
                    result = generate_music_content(prompt, st.session_state.api_key)
                    
                    if result:
                        st.markdown("<div class='mood-card'>", unsafe_allow_html=True)
                        st.markdown(f"### 🎼 Your {mood_select} Composition")
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown(result)
                        
                        # Add to history
                        st.session_state.history.append({
                            'type': 'Mood Music',
                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                            'summary': f"{mood_select} - {genre_select}"
                        })
                        
                        # Download button
                        st.download_button(
                            label="💾 Download Composition Guide",
                            data=result,
                            file_name=f"composition_{mood_select.replace(' ', '_')}_{genre_select}.txt",
                            mime="text/plain"
                        )
    
    # Tab 3: Genre Transformer
    with tab3:
        st.header("🎸 Genre Transformation Tool")
        st.markdown("Transform your musical ideas from one genre to another")
        
        music_description = st.text_area(
            "🎵 Describe Your Music Idea",
            placeholder="Describe the song, melody, or musical idea you have. Include details about tempo, instruments, mood, or any specific elements.",
            height=150
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            from_genre = st.selectbox(
                "📍 From Genre",
                ["Pop", "Rock", "Hip-Hop", "EDM", "Jazz", "Classical", "Country", "R&B", "Metal",
                 "Folk", "Blues", "Reggae", "Punk", "Indie", "Soul", "Funk"],
                key="from_genre"
            )
        
        with col2:
            to_genre = st.selectbox(
                "🎯 To Genre",
                ["EDM", "Jazz", "Classical", "Lo-fi Hip-Hop", "Acoustic", "Orchestral", "Trap",
                 "House", "Reggaeton", "Synthwave", "Ambient", "Metal", "Country", "R&B", "Funk"],
                key="to_genre"
            )
        
        if st.button("🔄 Transform Genre", key="transform_btn"):
            if not st.session_state.api_key:
                st.error("⚠️ Please enter your Groq API key in the sidebar first!")
            elif not music_description:
                st.warning("⚠️ Please describe your music idea!")
            else:
                with st.spinner("🎵 Transforming your music..."):
                    prompt = create_genre_transformation_prompt(music_description, from_genre, to_genre)
                    result = generate_music_content(prompt, st.session_state.api_key)
                    
                    if result:
                        st.markdown("<div class='genre-card'>", unsafe_allow_html=True)
                        st.markdown(f"### 🎸 {from_genre} → {to_genre} Transformation")
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown(result)
                        
                        # Add to history
                        st.session_state.history.append({
                            'type': 'Genre Transform',
                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                            'summary': f"{from_genre} → {to_genre}"
                        })
                        
                        # Download button
                        st.download_button(
                            label="💾 Download Transformation Guide",
                            data=result,
                            file_name=f"transform_{from_genre}_to_{to_genre}.txt",
                            mime="text/plain"
                        )
    
    # Tab 4: Music Theory Helper
    with tab4:
        st.header("📚 Music Theory & Production Helper")
        st.markdown("Get help with music theory, production techniques, and creative questions")
        
        help_category = st.selectbox(
            "📂 Category",
            ["Music Theory Basics", "Chord Progressions", "Melody Writing", "Rhythm & Timing",
             "Mixing & Mastering", "Sound Design", "Song Structure", "Production Techniques",
             "Instrumentation", "General Question"]
        )
        
        user_question = st.text_area(
            "❓ Your Question",
            placeholder="Ask anything about music theory, production, composition, or get creative advice...",
            height=150
        )
        
        if st.button("💡 Get Answer", key="theory_btn"):
            if not st.session_state.api_key:
                st.error("⚠️ Please enter your Groq API key in the sidebar first!")
            elif not user_question:
                st.warning("⚠️ Please enter your question!")
            else:
                with st.spinner("🤔 Thinking..."):
                    theory_prompt = f"""As an expert music educator and producer, answer this question about {help_category}:

Question: {user_question}

Please provide:
1. A clear, easy-to-understand explanation
2. Practical examples
3. Tips for application
4. Common mistakes to avoid
5. Resources for further learning

Make your answer accessible to students without deep technical expertise."""
                    
                    result = generate_music_content(theory_prompt, st.session_state.api_key)
                    
                    if result:
                        st.markdown("### 💡 Answer")
                        st.markdown(result)
                        
                        # Add to history
                        st.session_state.history.append({
                            'type': 'Theory Help',
                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                            'summary': help_category
                        })
                        
                        # Download button
                        st.download_button(
                            label="💾 Download Answer",
                            data=result,
                            file_name=f"music_theory_{help_category.replace(' ', '_')}.txt",
                            mime="text/plain"
                        )
    
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 2rem;'>
            <p>🎵 AI Music Remix & Mood Generator | Made with ❤️ using Streamlit & Groq (Llama 3.1)</p>
            <p style='font-size: 0.9rem;'>Perfect for students exploring music creation without technical expertise!</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
