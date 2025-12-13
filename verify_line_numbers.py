#!/usr/bin/env python3
import re
import sys

def load_cpp_file(cpp_file):
    with open(cpp_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines

def verify_ts_file(ts_file, cpp_file):
    with open(ts_file, 'r', encoding='utf-8') as f:
        ts_content = f.read()
    
    cpp_lines = load_cpp_file(cpp_file)
    
    ts_lines = ts_content.split('\n')
    
    total_checked = 0
    passed = 0
    failed = 0
    errors = []
    
    i = 0
    while i < len(ts_lines):
        line = ts_lines[i]
        
        if '<message>' in line:
            message_start = i
            message_end = i
            j = i + 1
            while j < len(ts_lines) and '</message>' not in ts_lines[j]:
                j += 1
            message_end = j
            
            source_text = None
            locations = []
            
            for k in range(message_start, message_end + 1):
                if '<source>' in ts_lines[k]:
                    source_match = re.search(r'<source>(.*?)</source>', ts_lines[k])
                    if source_match:
                        source_text = source_match.group(1)
                
                if 'filename="../gui/advancedsettings.cpp"' in ts_lines[k]:
                    line_match = re.search(r'line="(\d+)"', ts_lines[k])
                    if line_match:
                        line_num = int(line_match.group(1))
                        locations.append(line_num)
            
            if source_text and locations:
                for line_num in locations:
                    total_checked += 1
                    
                    if line_num <= len(cpp_lines):
                        cpp_line = cpp_lines[line_num - 1]
                        
                        escaped_source = re.escape(source_text)
                        pattern = rf'tr\s*\(\s*"({escaped_source})"\s*\)'
                        
                        if re.search(pattern, cpp_line):
                            passed += 1
                            print(f'✓ Line {line_num}: "{source_text[:50]}..." - PASSED')
                        else:
                            failed += 1
                            error_msg = f'✗ Line {line_num}: "{source_text[:50]}..." - FAILED'
                            print(error_msg)
                            print(f'  Expected to find: tr("{source_text}")')
                            print(f'  Actual line content: {cpp_line.strip()[:100]}')
                            errors.append((line_num, source_text, cpp_line.strip()))
                    else:
                        failed += 1
                        error_msg = f'✗ Line {line_num}: "{source_text[:50]}..." - FAILED (line number out of range)'
                        print(error_msg)
                        errors.append((line_num, source_text, 'OUT OF RANGE'))
            
            i = message_end + 1
        else:
            i += 1
    
    print('\n' + '='*80)
    print(f'Total checked: {total_checked}')
    print(f'Passed: {passed} ({passed*100//total_checked if total_checked > 0 else 0}%)')
    print(f'Failed: {failed} ({failed*100//total_checked if total_checked > 0 else 0}%)')
    
    if errors:
        print('\n' + '='*80)
        print('FAILED ITEMS:')
        for line_num, source_text, cpp_line in errors:
            print(f'\nLine {line_num}: {source_text}')
            if cpp_line != 'OUT OF RANGE':
                print(f'  CPP: {cpp_line[:100]}')
    
    return passed, failed

def main():
    ts_file = '/Users/soonco/Work/qBittorrent_514/src/lang/qbittorrent_zh_CN.ts'
    cpp_file = '/Users/soonco/Work/qBittorrent_514/src/gui/advancedsettings.cpp'
    
    print('Verifying line numbers in qbittorrent_zh_CN.ts...\n')
    passed, failed = verify_ts_file(ts_file, cpp_file)
    
    if failed == 0:
        print('\n✓ All verifications passed!')
        sys.exit(0)
    else:
        print(f'\n✗ {failed} verifications failed!')
        sys.exit(1)

if __name__ == '__main__':
    main()
