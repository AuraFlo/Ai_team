# yoga_recommendation_app.py

import sqlite3
import os
import pandas as pd
import subprocess
from datetime import datetime
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
import pickle
import platform
from pathlib import Path
import json
import random

# ---------------------------- Config ----------------------------

class YogaAppConfig:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default config"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
        else:
            config = self.create_default_config()
            self.save_config(config)
        
        # Set attributes from config
        self.whisper_exe = config.get('whisper_exe', self.get_default_whisper_exe())
        self.whisper_model = config.get('whisper_model', self.get_default_whisper_model())
        self.audio_path = config.get('audio_path', self.get_default_audio_path())
        self.database_name = config.get('database_name', 'yoga_recommendation.db')
        self.model_file = config.get('model_file', 'fatigue_model.pkl')
    
    def create_default_config(self):
        """Create default configuration based on OS and common paths"""
        return {
            "whisper_exe": self.get_default_whisper_exe(),
            "whisper_model": self.get_default_whisper_model(),
            "audio_path": self.get_default_audio_path(),
            "database_name": "yoga_recommendation.db",
            "model_file": "fatigue_model.pkl"
        }
    
    def get_default_whisper_exe(self):
        """Get default whisper executable path based on OS"""
        system = platform.system().lower()
        
        possible_paths = [
            Path.home() / "whisper.cpp" / "build" / "bin" / "Release" / "main.exe",
            Path("C:") / "whisper.cpp" / "build" / "bin" / "Release" / "main.exe",
            Path("whisper.exe"),  # If in PATH
            Path("./whisper.exe")  # Local directory
        ]
        
        # Return first existing path or first option as fallback
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        return str(possible_paths[0])  # Fallback to first option
    
    def get_default_whisper_model(self):
        """Get default whisper model path"""
        system = platform.system().lower()
        
        possible_paths = [
            Path.home() / "whisper.cpp" / "models" / "ggml-base.en.bin",
            Path("C:") / "whisper.cpp" / "models" / "ggml-base.en.bin",
            Path("models") / "ggml-base.en.bin",
            Path("./ggml-base.en.bin")
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        return str(possible_paths[0])  # Fallback
    
    def get_default_audio_path(self):
        """Get default audio path"""
        system = platform.system().lower()
        
        possible_paths = [
            Path.home() / "whisper.cpp" / "samples" / "jfk.wav",
            Path("samples") / "jfk.wav",
            Path("./audio_input.wav")
        ]
       
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        return str(possible_paths[-1])  # Default to audio_input.wav
    
    def save_config(self, config=None):
        """Save current configuration to file"""
        if config is None:
            config = {
                "whisper_exe": self.whisper_exe,
                "whisper_model": self.whisper_model,
                "audio_path": self.audio_path,
                "database_name": self.database_name,
                "model_file": self.model_file
            }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"Configuration saved to {self.config_file}")
    
    def validate_paths(self):
        """Validate that all required files exist"""
        issues = []
        
        if not os.path.exists(self.whisper_exe):
            issues.append(f"Whisper executable not found: {self.whisper_exe}")
        
        if not os.path.exists(self.whisper_model):
            issues.append(f"Whisper model not found: {self.whisper_model}")
        
        if not os.path.exists(self.model_file):
            issues.append(f"Fatigue model not found: {self.model_file}")
        
        return issues
    
    def print_config(self):
        """Print current configuration"""
        print("Current Configuration:")
        print(f"  Whisper Executable: {self.whisper_exe}")
        print(f"  Whisper Model: {self.whisper_model}")
        print(f"  Audio Path: {self.audio_path}")
        print(f"  Database: {self.database_name}")
        print(f"  Model File: {self.model_file}")
        
        # Check file existence
        print("\nFile Status:")
        print(f"  Whisper Exe exists: {os.path.exists(self.whisper_exe)}")
        print(f"  Whisper Model exists: {os.path.exists(self.whisper_model)}")
        print(f"  Model File exists: {os.path.exists(self.model_file)}")

# Initialize global config
config = YogaAppConfig()

# ---------------------------- Database Setup ----------------------------

def ensure_users_table_exists():
    """Create users table if it doesn't exist"""
    conn = sqlite3.connect(config.database_name)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            gender TEXT,
            injury_history TEXT,
            fitness_goal TEXT
        )
    """)
    
    # Insert a sample user if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO users (user_id, name, age, gender, injury_history, fitness_goal)
            VALUES (1, 'Sample User', 30, 'Other', '', 'relaxation')
        """)
    
    conn.commit()
    conn.close()

def ensure_weekly_data_table_exists():
    """Create weekly_data table if it doesn't exist"""
    conn = sqlite3.connect(config.database_name)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weekly_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_date TEXT NOT NULL,
            pose_accuracy REAL,
            major_errors TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# ---------------------------- Transcription ----------------------------

def transcribe_voice(audio_path=None):
    """Transcribe voice using configured paths"""
    if audio_path is None:
        audio_path = config.audio_path
    
    # Check if whisper is available
    if not os.path.exists(config.whisper_exe):
        print(f"Warning: Whisper executable not found: {config.whisper_exe}")
        # Return a mock transcription for testing
        return "I feel tired and need some relaxing yoga poses"
    
    if not os.path.exists(config.whisper_model):
        print(f"Warning: Whisper model not found: {config.whisper_model}")
        return "I feel tired and need some relaxing yoga poses"
    
    try:
        command = [config.whisper_exe, "-m", config.whisper_model, "-f", audio_path]
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Transcription error: {e}")
        return "I feel tired and need some relaxing yoga poses"

# ---------------------------- Fatigue Classifier ----------------------------

def load_fatigue_model():
    """Load fatigue model using configured path"""
    model_path = config.model_file
    
    if not os.path.exists(model_path):
        print(f"Warning: Fatigue model not found: {model_path}")
        print("Training a new model...")
        train_fatigue_classifier()
    
    with open(model_path, "rb") as f:
        return pickle.load(f)

def predict_fatigue_level(text):
    try:
        model, vectorizer = load_fatigue_model()
        X = vectorizer.transform([text])
        return model.predict(X)[0]
    except Exception as e:
        print(f"Fatigue prediction error: {e}")
        # Simple fallback based on keywords
        text_lower = text.lower()
        if any(word in text_lower for word in ['tired', 'exhausted', 'fatigue', 'drained']):
            return 'high'
        elif any(word in text_lower for word in ['okay', 'fine', 'normal']):
            return 'medium'
        else:
            return 'low'

def get_database_connection():
    """Get database connection using configured database name"""
    return sqlite3.connect(config.database_name)

# ---------------------------- Yoga DB & Logs ----------------------------

YOGA_KNOWLEDGE_BASE = {
    "Tree Pose": {
        "benefits": "Improves balance, strengthens thighs, ankles, and spine",
        "for_issues": ["balance", "back pain", "focus"],
        "difficulty": "beginner"
    },
    "Cat-Cow": {
        "benefits": "Increases spinal flexibility, relieves back pain and stress",
        "for_issues": ["back pain", "posture", "stress", "spinal stiffness"],
        "difficulty": "beginner"
    },
    "Downward Dog": {
        "benefits": "Strengthens upper body, stretches hamstrings and calves",
        "for_issues": ["shoulder pain", "flexibility", "stress", "hamstring tightness"],
        "difficulty": "intermediate"
    },
    "Warrior II": {
        "benefits": "Strengthens legs and arms, opens hips",
        "for_issues": ["balance", "leg strength", "hip stiffness", "stamina"],
        "difficulty": "beginner"
    },
    "Bridge Pose": {
        "benefits": "Opens chest, strengthens back and glutes",
        "for_issues": ["back pain", "stress", "posture", "low mood"],
        "difficulty": "beginner"
    },
    "Child's Pose": {
        "benefits": "Relieves fatigue, soothes mind, reduces anxiety",
        "for_issues": ["fatigue", "stress", "anxiety", "insomnia"],
        "difficulty": "beginner"
    },
    "Seated Forward Bend": {
        "benefits": "Calms brain, stretches spine and hamstrings",
        "for_issues": ["fatigue", "stress", "tight hamstrings"],
        "difficulty": "beginner"
    },
    "Cobra Pose": {
        "benefits": "Strengthens spine, opens chest",
        "for_issues": ["back pain", "posture", "depression"],
        "difficulty": "beginner"
    },
    "Legs Up the Wall": {
        "benefits": "Improves circulation, relieves fatigue and swelling",
        "for_issues": ["fatigue", "swelling", "stress"],
        "difficulty": "beginner"
    },
    "Corpse Pose": {
        "benefits": "Deep relaxation, lowers blood pressure, mental reset",
        "for_issues": ["stress", "anxiety", "burnout"],
        "difficulty": "beginner"
    }
}

def save_journal_entry(user_id, journal_text, fatigue_level):
    conn = sqlite3.connect(config.database_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            entry_date TEXT NOT NULL,
            journal_text TEXT NOT NULL,
            fatigue_level TEXT NOT NULL
        )
    """)
    cursor.execute("""
        INSERT INTO journal_logs (user_id, entry_date, journal_text, fatigue_level)
        VALUES (?, ?, ?, ?)
    """, (user_id, datetime.now().strftime("%Y-%m-%d"), journal_text, fatigue_level))
    conn.commit()
    conn.close()

def get_user_data(user_id):
    conn = sqlite3.connect(config.database_name)
    cursor = conn.cursor()
    cursor.execute("SELECT name, age, gender, injury_history, fitness_goal FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user is None:
        return {
            "name": "Unknown User",
            "age": 30,
            "gender": "Other",
            "injury": "",
            "goal": "relaxation"
        }
    
    return {
        "name": user[0],
        "age": user[1],
        "gender": user[2],
        "injury": user[3] or "",
        "goal": user[4] or "relaxation"
    }

# ---------------------------- Rule-Based Recommender ----------------------------

def generate_recommendations(user_data, fatigue_level, journal_text):
    issues = ["fatigue"] if fatigue_level == "high" else []
    if "back" in journal_text.lower():
        issues.append("back pain")
    if "stress" in journal_text.lower():
        issues.append("stress")

    recommendations = []
    for pose, info in YOGA_KNOWLEDGE_BASE.items():
        if any(issue in info["for_issues"] for issue in issues):
            recommendations.append((pose, info))

    if user_data['age'] > 50 or user_data['injury']:
        recommendations = [p for p in recommendations if p[1]['difficulty'] == 'beginner']

    return recommendations[:3]

# ---------------------------- Report ----------------------------

def build_summary(user, journal_text, fatigue_level, poses):
    text = f"""
📋 User Summary:
Name: {user['name']} | Age: {user['age']} | Goal: {user['goal']}
Fatigue Level: {fatigue_level.title()}
Journal: "{journal_text}"

🧘 Recommended Poses:
"""
    for pose, info in poses:
        text += f"- {pose}: {info['benefits']}\n"
    return text

# ---------------------------- Motivational Quote ----------------------

# Sample quotes categorized by goal (you can expand this)
quotes = {
    "relaxation": [
        "Breathe in peace, breathe out stress.",
        "Rest is not idleness.",
        "Relax, refresh, recharge."
    ],
    "flexibility": [
        "Progress, not perfection.",
        "Each stretch brings strength.",
        "Flexibility is a journey."
    ],
    "strength": [
        "Stronger every session.",
        "Push your limits.",
        "Discipline brings results."
    ],
    "fatigue_high": [
        "Even rest is productive.",
        "Listen to your body. It knows best.",
        "Rest now to rise stronger."
    ],
    "default": [
        "Believe in your inner strength.",
        "You are your only limit.",
        "Consistency beats intensity."
    ]
}

def get_motivational_quote(goal=None, fatigue_level=None):
    if fatigue_level == "high":
        return random.choice(quotes["fatigue_high"])
    if goal in quotes:
        return random.choice(quotes[goal])
    return random.choice(quotes["default"])

# ---------------------------- Main Flow ----------------------------

def recommend_yoga(user_id, journal_input=None, voice=False):
    try:
        # Ensure all tables exist
        ensure_users_table_exists()
        ensure_weekly_data_table_exists()
        
        # Get journal text
        if voice and journal_input:  # journal_input is actually audio_path when voice=True
            journal_text = transcribe_voice(journal_input)
        else:
            journal_text = journal_input or ""
        
        if not journal_text.strip():
            return {
                "details": "Please provide some journal input to get recommendations.",
                "quote": "Every journey begins with a single step."
            }
        
        # Predict fatigue and save entry
        fatigue_level = predict_fatigue_level(journal_text)
        save_journal_entry(user_id, journal_text, fatigue_level)
        
        # Get user data and generate recommendations
        user = get_user_data(user_id)
        poses = generate_recommendations(user, fatigue_level, journal_text)
        quote = get_motivational_quote(goal=user['goal'], fatigue_level=fatigue_level)
        summary = build_summary(user, journal_text, fatigue_level, poses)
        
        return {
            "details": summary,
            "quote": quote
        }
        
    except Exception as e:
        print(f"Error in recommend_yoga: {e}")
        return {
            "details": f"Error generating recommendations: {str(e)}",
            "quote": "Breathe through the challenges."
        }

# ---------------------------- Training Helper (Run Once) ----------------------------

def train_fatigue_classifier():
    """Train and save fatigue classifier"""
    data = [
        ("I feel very tired and exhausted today", "high"),
        ("Feeling a bit low on energy", "medium"),
        ("I'm active and ready", "low"),
        ("Back pain and fatigue hit me", "high"),
        ("Calm and relaxed", "low"),
        ("I'm drained and need rest", "high"),
        ("Feeling okay today", "medium"),
        ("Full of energy and motivation", "low"),
        ("Stressed and tired", "high"),
        ("Normal energy levels", "medium")
    ]
    texts, labels = zip(*data)
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    clf = SVC()
    clf.fit(X, labels)

    with open(config.model_file, "wb") as f:
        pickle.dump((clf, vectorizer), f)
    
    print(f"Fatigue model saved to {config.model_file}")

def generate_weekly_report(user_id):
    conn = sqlite3.connect(config.database_name)
    cursor = conn.cursor()

    # Fetch session accuracy data
    cursor.execute("SELECT session_date, pose_accuracy FROM weekly_data WHERE user_id=? ORDER BY session_date", (user_id,))
    session_data = cursor.fetchall()

    # Fetch journal fatigue data
    cursor.execute("SELECT entry_date, journal_text FROM journal_logs WHERE user_id=?", (user_id,))
    journal_data = cursor.fetchall()

    # Fetch major pose errors
    cursor.execute("SELECT major_errors FROM weekly_data WHERE user_id=?", (user_id,))
    errors = [row[0].lower() for row in cursor.fetchall() if row[0]]

    conn.close()

    session_df = pd.DataFrame(session_data, columns=["Date", "Accuracy"])
    fatigue_scores = [
        (date, sum(1 for word in ["tired", "pain", "exhausted"] if word in text.lower()))
        for date, text in journal_data
    ]
    fatigue_df = pd.DataFrame(fatigue_scores, columns=["Date", "Fatigue"])

    error_counts = Counter()
    for error in errors:
        error_counts.update(error.split())

    return session_df, fatigue_df, error_counts.most_common(3)

def setup_yoga_app():
    """Interactive setup for first-time users"""
    print("🧘 Yoga App Setup")
    print("=" * 40)
    
    # Check current config
    config.print_config()
    
    issues = config.validate_paths()
    if issues:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        
        print("\n🔧 Let's fix these issues:")
        
        # Ask user to provide correct paths
        if not os.path.exists(config.whisper_exe):
            new_path = input(f"Enter path to whisper executable (current: {config.whisper_exe}): ").strip()
            if new_path and os.path.exists(new_path):
                config.whisper_exe = new_path
        
        if not os.path.exists(config.whisper_model):
            new_path = input(f"Enter path to whisper model (current: {config.whisper_model}): ").strip()
            if new_path and os.path.exists(new_path):
                config.whisper_model = new_path
        
        # Save updated config
        config.save_config()
    else:
        print("\n✅ All paths are valid!")
    
    return config

# Initialize on import
if __name__ == "__main__":
    # Train the model if it doesn't exist
    if not os.path.exists(config.model_file):
        print("Training fatigue classifier...")
        train_fatigue_classifier()
    
    # Ensure database tables exist
    ensure_users_table_exists()
    ensure_weekly_data_table_exists()
    
    print("Yoga agent ready!")