#!/usr/bin/env python3
"""Direct test of the enhanced query generation with reserved word handling."""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from query_generation_optimizer import QueryGenerationOptimizer

def test_comprehensive_query_generation():
    """Test comprehensive query generation with reserved words."""
    
    print("🧪 Testing Comprehensive Query Generation with Reserved Words")
    print("=" * 70)
    
    # Sample schema with reserved words (similar to Snowflake healthcare schema)
    sample_schema = {
        'PATIENTS': {
            'name': 'PATIENTS',
            'fields': [
                {'name': 'ID', 'type': 'VARCHAR'},
                {'name': 'FIRST', 'type': 'VARCHAR'},
                {'name': 'LAST', 'type': 'VARCHAR'},
                {'name': 'BIRTHDATE', 'type': 'DATE'},
            ]
        },
        'ENCOUNTERS': {
            'name': 'ENCOUNTERS',
            'fields': [
                {'name': 'ID', 'type': 'VARCHAR'},
                {'name': 'PATIENT', 'type': 'VARCHAR'},
                {'name': 'START', 'type': 'TIMESTAMP'},  # Reserved word
                {'name': 'END', 'type': 'TIMESTAMP'},    # Reserved word
                {'name': 'CODE', 'type': 'VARCHAR'},     # Reserved word
                {'name': 'DESCRIPTION', 'type': 'VARCHAR'} # Reserved word
            ]
        },
        'CONDITIONS': {
            'name': 'CONDITIONS',
            'fields': [
                {'name': 'ID', 'type': 'VARCHAR'},
                {'name': 'ENCOUNTER', 'type': 'VARCHAR'},
                {'name': 'CODE', 'type': 'VARCHAR'},     # Reserved word
                {'name': 'DESCRIPTION', 'type': 'VARCHAR'} # Reserved word
            ]
        },
        'MEDICATIONS': {
            'name': 'MEDICATIONS',
            'fields': [
                {'name': 'ID', 'type': 'VARCHAR'},
                {'name': 'ENCOUNTER', 'type': 'VARCHAR'},
                {'name': 'CODE', 'type': 'VARCHAR'},     # Reserved word
                {'name': 'DESCRIPTION', 'type': 'VARCHAR'} # Reserved word
            ]
        }
    }
    
    # Initialize optimizer
    optimizer = QueryGenerationOptimizer()
    
    # Test comprehensive query generation
    test_cases = [
        {
            "patient_id": "edc17058-55fb-08c7-12df-ece93a402e50",
            "query_type": "comprehensive",
            "description": "Comprehensive query with specific patient"
        },
        {
            "patient_id": "",
            "query_type": "comprehensive", 
            "description": "Comprehensive query without patient filter"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 Test Case {i}: {test_case['description']}")
        print("-" * 50)
        
        try:
            # Generate optimized prompt
            prompt = optimizer.create_optimized_prompt(
                schema_dict=sample_schema,
                patient_id=test_case['patient_id'],
                query_type=test_case['query_type'],
                database_type="snowflake"
            )
            
            print(f"Patient ID: '{test_case['patient_id']}'")
            print(f"Query Type: {test_case['query_type']}")
            
            # Check for reserved word handling in prompt
            reserved_words_mentioned = []
            for word in ['START', 'END', 'CODE', 'DESCRIPTION']:
                if f'"{word}"' in prompt:
                    reserved_words_mentioned.append(word)
            
            if reserved_words_mentioned:
                print(f"✅ Reserved words properly quoted: {', '.join(reserved_words_mentioned)}")
            else:
                print("ℹ️  No reserved word examples in prompt")
            
            # Check specific database requirements
            if 'ALWAYS use "' in prompt and 'reserved words' in prompt.lower():
                print("✅ Explicit reserved word quoting instructions found")
            else:
                print("⚠️  Reserved word instructions may be unclear")
                
            # Check for comprehensive query guidance
            if 'comprehensive' in prompt.lower() and 'join' in prompt.lower():
                print("✅ Comprehensive query guidance included")
            else:
                print("ℹ️  Basic query guidance")
                
            # Check for patient filtering instructions
            if test_case['patient_id']:
                if test_case['patient_id'] in prompt:
                    print("✅ Patient-specific filtering instructions")
                else:
                    print("⚠️  Patient ID not found in prompt")
            else:
                if 'SAMPLE DATA' in prompt or 'without specific patient' in prompt:
                    print("✅ Sample data instructions (no patient filter)")
                else:
                    print("ℹ️  General query instructions")
                    
        except Exception as e:
            print(f"❌ Error generating prompt: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_comprehensive_query_generation()