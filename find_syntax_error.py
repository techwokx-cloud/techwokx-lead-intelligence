# find_syntax_error.py
import os
import sys
import traceback

def check_syntax(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        compile(content, filepath, 'exec')
        return True, None
    except SyntaxError as e:
        return False, f"{filepath}: Line {e.lineno} - {e.msg}"
    except Exception as e:
        return False, f"{filepath}: {e}"

def main():
    print("Checking Python files for syntax errors...")
    print("-" * 50)
    
    errors = []
    
    # Check pages directory
    if os.path.exists('pages'):
        for filename in os.listdir('pages'):
            if filename.endswith('.py'):
                filepath = os.path.join('pages', filename)
                is_valid, error = check_syntax(filepath)
                if is_valid:
                    print(f"✅ {filepath}")
                else:
                    print(f"❌ {error}")
                    errors.append(error)
    
    # Check modules directory
    if os.path.exists('modules'):
        for filename in os.listdir('modules'):
            if filename.endswith('.py'):
                filepath = os.path.join('modules', filename)
                is_valid, error = check_syntax(filepath)
                if is_valid:
                    print(f"✅ {filepath}")
                else:
                    print(f"❌ {error}")
                    errors.append(error)
    
    # Check root directory
    for filename in os.listdir('.'):
        if filename.endswith('.py') and filename not in ['find_syntax_error.py']:
            filepath = filename
            is_valid, error = check_syntax(filepath)
            if is_valid:
                print(f"✅ {filepath}")
            else:
                print(f"❌ {error}")
                errors.append(error)
    
    print("-" * 50)
    if errors:
        print(f"\n❌ Found {len(errors)} syntax error(s):")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✅ All files have valid syntax!")

if __name__ == "__main__":
    main()
