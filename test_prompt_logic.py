#!/usr/bin/env python3
"""Test the prompt generation logic directly without database dependencies."""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_prompt_logic():
    """Test the prompt generation logic directly."""
    
    print("🧪 Testing Patient ID Filtering Logic")
    print("=" * 50)
    
    # Test the logic that determines patient filtering
    test_cases = [
        {"patient_id": "", "expected": "SAMPLE DATA"},
        {"patient_id": "   ", "expected": "SAMPLE DATA"},
        {"patient_id": "all", "expected": "SAMPLE DATA"}, 
        {"patient_id": "none", "expected": "SAMPLE DATA"},
        {"patient_id": "123", "expected": "PATIENT FOCUS"},
        {"patient_id": "patient-456", "expected": "PATIENT FOCUS"},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        patient_id = test_case['patient_id']
        expected = test_case['expected']
        
        # Replicate the logic from the updated bedrock service
        if patient_id and patient_id.strip() and patient_id.lower() not in ['all', 'none', '']:
            result = "PATIENT FOCUS"
        else:
            result = "SAMPLE DATA"
            
        status = "✅" if result == expected else "❌"
        print(f"{status} Test {i}: '{patient_id}' -> {result} (expected: {expected})")
        
    print("\n🔍 Example Query Generation Logic:")
    print("-" * 40)
    
    for test_case in [{"patient_id": "", "description": "Empty"}, 
                      {"patient_id": "123", "description": "Specific ID"}]:
        patient_id = test_case['patient_id']
        description = test_case['description']
        
        # Example query generation logic
        if patient_id and patient_id.strip() and patient_id.lower() not in ['all', 'none', '']:
            example_query = f"SELECT p.* FROM PATIENTS p WHERE p.id = '{patient_id}' LIMIT 10"
        else:
            example_query = f"SELECT p.* FROM PATIENTS p LIMIT 10"
            
        print(f"{description} patient_id ('{patient_id}'):")
        print(f"  -> {example_query}")

if __name__ == "__main__":
    test_prompt_logic()