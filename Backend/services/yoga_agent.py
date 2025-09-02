# app/services/yoga_agent.py
from datetime import datetime
import random
import pickle
import os

from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC

from app.db import models, database

# ---------------------------- Yoga Knowledge Base ----------------------------

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

# ---------------------------- Motivational Quotes ----------------------------

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

# ---------------------------- Fatigue Classifier ----------------------------

MODEL_FILE = "fatigue_model.pkl"

def train_fatigue_classifier():
    """Train and save fatigue classifier (simple demo model)."""
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

    with open(MODEL_FILE, "wb") as f:
        pickle.dump((clf, vectorizer), f)
    print(f"Fatigue model saved to {MODEL_FILE}")

def load_fatigue_model():
    """Load fatigue model (train if missing)."""
    if not os.path.exists(MODEL_FILE):
        train_fatigue_classifier()
    with open(MODEL_FILE, "rb") as f:
        return pickle.load(f)

def predict_fatigue_level(text: str) -> str:
    try:
        model, vectorizer = load_fatigue_model()
        X = vectorizer.transform([text])
        return model.predict(X)[0]
    except Exception as e:
        # fallback: keyword-based
        text_lower = text.lower()
        if any(word in text_lower for word in ["tired", "exhausted", "fatigue", "drained"]):
            return "high"
        elif any(word in text_lower for word in ["okay", "fine", "normal"]):
            return "medium"
        else:
            return "low"

# ---------------------------- Recommendation Logic ----------------------------

def generate_recommendations(user: models.User, fatigue_level: str, journal_text: str):
    issues = []
    if fatigue_level == "high":
        issues.append("fatigue")
    if "back" in journal_text.lower():
        issues.append("back pain")
    if "stress" in journal_text.lower():
        issues.append("stress")

    recommendations = []
    for pose, info in YOGA_KNOWLEDGE_BASE.items():
        if any(issue in info["for_issues"] for issue in issues):
            recommendations.append({"pose": pose, **info})

    # adjust for injuries/age
    if user.age and user.age > 50 or user.injury_history:
        recommendations = [p for p in recommendations if p["difficulty"] == "beginner"]

    return recommendations[:3] if recommendations else [{"pose": "Child's Pose", **YOGA_KNOWLEDGE_BASE["Child's Pose"]}]

def get_motivational_quote(goal=None, fatigue_level=None):
    if fatigue_level == "high":
        return random.choice(quotes["fatigue_high"])
    if goal and goal in quotes:
        return random.choice(quotes[goal])
    return random.choice(quotes["default"])

# ---------------------------- Main Entry ----------------------------

def recommend_yoga(user_id: int, journal_text: str):
    db: Session = database.SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            return {"error": f"No user found with ID {user_id}"}

        if not journal_text or not journal_text.strip():
            return {
                "details": "Please provide some journal input to get recommendations.",
                "quote": "Every journey begins with a single step."
            }

        # predict fatigue
        fatigue_level = predict_fatigue_level(journal_text)

        # save journal entry
        entry = models.JournalEntry(
            user_id=user_id,
            entry_text=journal_text,
            injury_history=user.injury_history or "",
            created_at=datetime.now()
        )
        db.add(entry)
        db.commit()

        # generate recommendations
        poses = generate_recommendations(user, fatigue_level, journal_text)
        quote = get_motivational_quote(goal=user.fitness_goal, fatigue_level=fatigue_level)

        return {
            "user": {"id": user.id, "name": user.name, "goal": user.fitness_goal},
            "fatigue": fatigue_level,
            "recommendations": poses,
            "quote": quote
        }

    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()
