#!/usr/bin/env python3
"""Test the fixed query generation with improved patient_id handling."""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pha.services.bedrock_service import BedrockService
from pha.db.session import DatabaseManager

def test_prompt_generation():
    """Test prompt generation with different patient_id values."""
    
    print("🧪 Testing Prompt Generation with Different Patient IDs")
    print("=" * 60)
    
    try:
        # Initialize services
        db_manager = DatabaseManager()
        bedrock_service = BedrockService(db_manager)
        
        # Sample schema (simplified)
        sample_schema = {
            'PATIENTS': {
                'name': 'PATIENTS',
                'fields': [
                    {'name': 'id', 'type': 'VARCHAR'},
                    {'name': 'first_name', 'type': 'VARCHAR'},
                    {'name': 'last_name', 'type': 'VARCHAR'},
                    {'name': 'birth_date', 'type': 'DATE'},
                ]
            },
            'CONDITIONS': {
                'name': 'CONDITIONS',
                'fields': [
                    {'name': 'id', 'type': 'VARCHAR'},
                    {'name': 'patient_id', 'type': 'VARCHAR'},
                    {'name': 'condition_code', 'type': 'VARCHAR'},
                ]
            }
        }
        
        # Test cases for prompt generation
        test_cases = [
            {"patient_id": "", "query_type": "basic", "description": "Empty patient_id"},
            {"patient_id": "all", "query_type": "basic", "description": "patient_id = 'all'"}, 
            {"patient_id": "123", "query_type": "basic", "description": "Specific patient_id"},
            {"patient_id": "  ", "query_type": "basic", "description": "Whitespace patient_id"},
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🔬 Test Case {i}: {test_case['description']}")
            print("-" * 40)
            
            try:
                # Generate prompt using the new optimized method
                prompt = bedrock_service.create_optimized_prompt(
                    schema_dict=sample_schema,
                    patient_id=test_case['patient_id'],
                    query_type=test_case['query_type'],
                    database_type="snowflake"
                )
                
                print(f"Patient ID input: '{test_case['patient_id']}'")
                
                # Check key parts of the prompt
                if "SAMPLE DATA" in prompt:
                    print("✅ Prompt indicates sample data (no specific patient filter)")
                elif "PATIENT FOCUS" in prompt:
                    print("✅ Prompt indicates patient-specific filtering")
                    
                # Check example query in prompt
                if "WHERE" in prompt and "= ''" in prompt:
                    print("⚠️  Warning: Prompt contains empty WHERE clause example")
                elif test_case['patient_id'] and test_case['patient_id'].strip() and test_case['patient_id'].lower() not in ['all', 'none']:
                    if test_case['patient_id'] in prompt:
                        print("✅ Patient ID correctly included in prompt example")
                else:
                    print("✅ No empty WHERE clause in prompt")
                        
            except Exception as e:
                print(f"❌ Error in test case: {str(e)}")
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_prompt_generation()