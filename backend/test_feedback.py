"""Test script for feedback service"""
import sys
sys.path.insert(0, '.')

print("=" * 50)
print("TEST FEEDBACK SERVICE")
print("=" * 50)

# Test 1: Import
print("\n1. Import FeedbackService...")
try:
    from app.rag.feedback_service import get_feedback_service
    print("   OK - Import reussi")
except Exception as e:
    print(f"   ERREUR: {e}")
    sys.exit(1)

# Test 2: Initialize
print("\n2. Initialiser FeedbackService...")
try:
    fs = get_feedback_service()
    print("   OK - Service initialise")
except Exception as e:
    print(f"   ERREUR: {e}")
    sys.exit(1)

# Test 3: Add feedback
print("\n3. Ajouter un feedback test...")
try:
    result = fs.add_feedback(
        message_id="test_123",
        question="Quel est le sentiment de Bitcoin?",
        answer="Le sentiment de Bitcoin est positif.",
        feedback_type="positive",
        session_id="test_session"
    )
    print(f"   OK - Feedback ajoute: {result}")
except Exception as e:
    print(f"   ERREUR: {e}")
    sys.exit(1)

# Test 4: Get stats
print("\n4. Recuperer les statistiques...")
try:
    stats = fs.get_stats()
    print(f"   OK - Stats: {stats}")
except Exception as e:
    print(f"   ERREUR: {e}")
    sys.exit(1)

# Test 5: Get feedbacks
print("\n5. Recuperer les feedbacks...")
try:
    feedbacks = fs.get_feedbacks(limit=5)
    print(f"   OK - {len(feedbacks)} feedbacks trouves")
    if feedbacks:
        print(f"   Dernier: {feedbacks[0]['feedback_type']} - {feedbacks[0]['question'][:40]}...")
except Exception as e:
    print(f"   ERREUR: {e}")
    sys.exit(1)

print("\n" + "=" * 50)
print("TOUS LES TESTS PASSES!")
print("=" * 50)
