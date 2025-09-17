#!/usr/bin/env python3
"""Direct test to simulate the failing query and check reserved word handling."""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from query_generation_optimizer import QueryGenerationOptimizer

def test_failing_query_scenario():
    """Test the exact scenario that was failing with reserved words."""
    
    print("🧪 Testing Failing Query Scenario")
    print("=" * 50)
    
    # Simulate the actual Snowflake schema structure that caused the issue
    snowflake_schema = {
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
                {'name': 'START', 'type': 'TIMESTAMP'},  # This was causing the issue
                {'name': 'END', 'type': 'TIMESTAMP'},
                {'name': 'CODE', 'type': 'VARCHAR'},
                {'name': 'DESCRIPTION', 'type': 'VARCHAR'}
            ]
        },
        'CONDITIONS': {
            'name': 'CONDITIONS',
            'fields': [
                {'name': 'ID', 'type': 'VARCHAR'},
                {'name': 'ENCOUNTER', 'type': 'VARCHAR'},
                {'name': 'CODE', 'type': 'VARCHAR'},
                {'name': 'DESCRIPTION', 'type': 'VARCHAR'}
            ]
        },
        'MEDICATIONS': {
            'name': 'MEDICATIONS',
            'fields': [
                {'name': 'ID', 'type': 'VARCHAR'},
                {'name': 'ENCOUNTER', 'type': 'VARCHAR'},
                {'name': 'CODE', 'type': 'VARCHAR'},
                {'name': 'DESCRIPTION', 'type': 'VARCHAR'}
            ]
        },
        'PROCEDURES': {
            'name': 'PROCEDURES',
            'fields': [
                {'name': 'ID', 'type': 'VARCHAR'},
                {'name': 'ENCOUNTER', 'type': 'VARCHAR'},
                {'name': 'CODE', 'type': 'VARCHAR'},
                {'name': 'DESCRIPTION', 'type': 'VARCHAR'}
            ]
        }
    }
    
    # Test the exact parameters that failed
    patient_id = "edc17058-55fb-08c7-12df-ece93a402e50"
    query_type = "comprehensive"
    database_type = "snowflake"
    
    print(f"Patient ID: {patient_id}")
    print(f"Query Type: {query_type}")
    print(f"Database: {database_type}")
    print()
    
    # Initialize optimizer
    optimizer = QueryGenerationOptimizer()
    
    try:
        # Generate the optimized prompt
        prompt = optimizer.create_optimized_prompt(
            schema_dict=snowflake_schema,
            patient_id=patient_id,
            query_type=query_type,
            database_type=database_type
        )
        
        print("✅ Generated Prompt Successfully")
        print("-" * 30)
        
        # Check for reserved word handling in the prompt
        reserved_checks = [
            ('START quoted', '"START"' in prompt),
            ('END quoted', '"END"' in prompt),
            ('Reserved word rules', 'ALWAYS use "' in prompt),
            ('Critical examples', 'CRITICAL EXAMPLES' in prompt),
            ('Patient filtering', patient_id in prompt),
            ('Comprehensive guidance', 'comprehensive' in prompt.lower())
        ]
        
        for check_name, result in reserved_checks:
            status = "✅" if result else "❌"
            print(f"{status} {check_name}")
        
        # Show relevant parts of the prompt
        print("\n📋 Key Prompt Sections:")
        print("-" * 30)
        
        lines = prompt.split('\n')
        in_requirements = False
        in_examples = False
        
        for line in lines:
            if 'QUERY REQUIREMENTS FOR SNOWFLAKE' in line:
                in_requirements = True
            elif 'CRITICAL EXAMPLES' in line:
                in_examples = True
            elif in_requirements and line.strip():
                print(f"REQ: {line.strip()}")
                if 'CRITICAL RULES' in line:
                    in_requirements = False
            elif in_examples and line.strip() and '- ' in line:
                print(f"EX:  {line.strip()}")
                if len([l for l in lines[lines.index(line):] if l.strip()]) < 3:
                    break
        
        print("\n🎯 Expected AI Query Behavior:")
        print("- Should use e.\"START\" instead of e.start")
        print("- Should use e.\"END\" instead of e.end") 
        print("- Should use c.\"CODE\" instead of c.code")
        print("- Should use c.\"DESCRIPTION\" instead of c.description")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_failing_query_scenario()