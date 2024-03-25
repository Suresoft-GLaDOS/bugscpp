import os
import sys 

sys.path.insert(0, '../bugscpp')
from command import CommandList

from whatthepatch import parse_patch

class BugscppInterface():
    def __init__(self, project, bug_index):
        self._commands = CommandList()
        self._project = project
        self._bug_index = bug_index
        self._path_to_repo = f'benchmark/{self._project}/buggy-{self._bug_index}'
        self._prepare_test_output_directory()
    
    def __str__(self):
        return f'{self._project}-{self._bug_index}'
        
    def _prepare_test_output_directory(self):
        self._output_dir = os.path.join(os.getcwd(), f'benchmark/{self._project}-{self._bug_index}')
        if not os.path.exists(self._output_dir):
            os.makedirs(self._output_dir)
    
    def _clear_test_output_directory(self):
        try:
            for file_name in os.listdir(self._output_dir):
                file_path = os.path.join(self._output_dir, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception as e:
            print(f"An error occurred while clearing test output: {e}")

    def checkout(self):
        checkout_args = [self._project, self._bug_index, '--buggy', '--target=benchmark']
        self._commands['checkout'](checkout_args)

    def build(self):
        build_args = [self._path_to_repo, '--coverage']
        self._commands['build'](build_args)

    def test(self):
        self._clear_test_output_directory()
        test_args = [self._path_to_repo, '--broken-cases', f'--output-dir={self._output_dir}', '--coverage']
        self._commands['test'](test_args)
            
    # legit interface to access metadata via bugscpp project?
    def _get_path_to_patch(self):
        return f'../bugscpp/taxonomy/{self._project}/patch/{int(self._bug_index):04}-buggy.patch'
    
    def get_path_to_repo(self):
        return self._path_to_repo
    
    def get_path_to_coverages(self):
        subdir = os.listdir(self._output_dir)[0] # Assume single failing test, called after running build & test
        return os.path.join(self._output_dir, subdir) if os.path.isdir(os.path.join(self._output_dir, subdir)) else ''
    
    def get_failing_test_code(self):
        if not self._test_file:
            return ''
        with open(os.path.join(self._path_to_repo, self._test_file), 'r') as f:
            test_lines = f.readlines()
        failing_lines = [line for i, line in enumerate(test_lines) if i + 1 in self._test_line]
        return f"\n\nFailing Test Code:\n{''.join(failing_lines)}"

    def extract_patch_info(self): # copied from bugscpp/tests/taxonomy/conftest.py
        patch = self._get_path_to_patch()
        patch_data = dict()
        with open(patch, encoding="utf-8", newline=os.linesep) as f:
            buggy_patches = f.read()
            for diff in parse_patch(buggy_patches):
                assert diff.header.new_path == diff.header.old_path
                path = diff.header.new_path
                fixed_lines = set()
                for change in diff.changes:
                    if change.new is not None and change.old is None:
                        fixed_lines.add(change.new)
                    elif change.new is None and change.old is not None:
                        fixed_lines.add(change.old)
                patch_data[path] = fixed_lines
        return patch_data
    

import json
import clang.cindex

def get_corresponding_code(cursor):
    start_location = cursor.extent.start
    end_location = cursor.extent.end

    start_offset = start_location.offset
    end_offset = end_location.offset

    file_path = start_location.file.name
    with open(file_path, 'r') as f:
        f.seek(start_offset)
        source_code = f.read(end_offset - start_offset)

    return source_code

def get_signature(function_snippet, function_name):
    signature = function_snippet.split('{')[0]
    signature = signature.replace('\n', ' ')
    signature = ', '.join([term.strip() for term in signature.split(',')])
    return signature[signature.find(function_name):] # better replace this with cursor.spelling either

def parse_gcov_file(path):
    execution_count = list()
    if not path:
        return execution_count
    with open(path) as f:
        lines = f.readlines()
        for line in lines:
            cov_info = line.split(':')
            if len(cov_info) < 3 or int(cov_info[1].strip()) == 0: # line number == 0
                continue
            
            exec_count = cov_info[0].strip()
            if exec_count.endswith('*'): # appended if not all codes are executed
                exec_count = exec_count[:-1]

            if exec_count.isdigit():
                execution_count.append(int(exec_count))
            else:
                execution_count.append(0)

    return execution_count

def get_coverage_file(coverage_dir, src_file):
    gcov_postfix = f'{src_file.replace("/", "#")}.gcov'
    for file in os.listdir(coverage_dir):
        if file.endswith(gcov_postfix):
            return os.path.join(coverage_dir, file)
    return ''

def collect_snippet(target_bugs):
    def iterate_over_source(src_path, consider_coverage=True):
        index = clang.cindex.Index.create()
        standard = 'c11'
        translation_unit = index.parse(src_path, args=[f'-std={standard}'])

        relative_path = src_path[len(repo_path) + 1:]
        gcov_path = get_coverage_file(coverage_path, relative_path)
        if consider_coverage and not gcov_path:
            return
        execution_count = parse_gcov_file(gcov_path)
        class_name = relative_path[:-2].replace('/', '.') # should I trim src, too? -> no

        for node in translation_unit.cursor.walk_preorder():
            if node.kind == clang.cindex.CursorKind.FUNCTION_DECL and node.is_definition(): # to exclude empty functions that came from headers
                start_line = node.extent.start.line
                end_line = node.extent.end.line
                if consider_coverage and sum(execution_count[start_line - 1:end_line]) == 0:
                    continue
                
                function_snippet = get_corresponding_code(node)
                signature = get_signature(function_snippet, node.spelling)
                
                is_buggy = False
                if relative_path in patch_info:
                    for line in patch_info[relative_path]:
                        is_buggy |= start_line <= line and line <= end_line 
                        # may lead to confusion if modification gets bigger

                data.append({'name' : f'{class_name}.{node.spelling}#{start_line}', \
                             'src_path': relative_path, \
                             'class_name': class_name, \
                             'signature': f'{class_name}.{signature}', \
                             'snippet': function_snippet, \
                             'begin_line': start_line, \
                             'end_line': end_line, \
                             'is_bug': is_buggy})

    def iterate_over_directory(dir_path, consider_coverage=True):
        for file_name in os.listdir(dir_path):
            full_path = os.path.join(dir_path, file_name)
            if os.path.isdir(full_path):
                iterate_over_directory(full_path, consider_coverage)
            elif file_name.endswith('.c'):
                iterate_over_source(full_path, consider_coverage)

    for project, bug_index in target_bugs:
        print(f'\nWorking on {project}-{bug_index}...')
        data_dir = f'data/{project}-{bug_index}'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)        

        bugscpp = BugscppInterface(project, bug_index)
        bugscpp.checkout()
        bugscpp.build()
        bugscpp.test()
        
        repo_path = bugscpp.get_path_to_repo()
        coverage_path = bugscpp.get_path_to_coverages()
        patch_info = bugscpp.extract_patch_info()

        src_dir = 'src' # for libchewing, libyara for yara
        test_dir = 'test' # for libchewing, tests for yara
        
        data = list()
        iterate_over_directory(os.path.join(repo_path, src_dir))        
        with open(os.path.join(data_dir, 'snippet.json'), 'w') as f:
            json.dump(sorted(data, key=lambda info: info['name']), f, indent=4)

        data.clear()
        iterate_over_directory(os.path.join(repo_path, test_dir), consider_coverage=False)
        with open(os.path.join(data_dir, 'test_snippet.json'), 'w') as f:
            json.dump(sorted(data, key=lambda info: info['name']), f, indent=4) 

import tiktoken
ENCODING = tiktoken.encoding_for_model("gpt-3.5-turbo")

def collect_token_statistics(target_bugs):
    def iterate_over_source(src_path):
        index = clang.cindex.Index.create()
        standard = 'c11' if is_c else 'c++11'
        translation_unit = index.parse(src_path, args=[f'-std={standard}'])

        relative_path = src_path[len(repo_path) + 1:]
        class_name = relative_path[:-2].replace('/', '.')

        for node in translation_unit.cursor.walk_preorder():
            if node.kind == clang.cindex.CursorKind.FUNCTION_DECL and node.is_definition(): # to exclude empty functions that came from headers
                start_line = node.extent.start.line
                end_line = node.extent.end.line

                is_buggy = False
                if relative_path in patch_info:
                    for line in patch_info[relative_path]:
                        is_buggy |= start_line <= line and line <= end_line 
                
                data.append({'name' : f'{class_name}.{node.spelling}#{start_line}', \
                             'loc': end_line - start_line + 1, \
                             'token_count': len(ENCODING.encode(get_corresponding_code(node))), \
                             'is_bug': is_buggy})

    def iterate_over_directory(dir_path):
        for file_name in os.listdir(dir_path):
            full_path = os.path.join(dir_path, file_name)
            if os.path.isdir(full_path):
                iterate_over_directory(full_path)
            elif (is_c and file_name.endswith('.c')) or (not is_c and file_name.endswith('.cpp')):
                iterate_over_source(full_path)

    for project, bug_index, src_dir, is_c in target_bugs:
        print(f'\nWorking on {project}-{bug_index}...')
        data_dir = f'data/{project}-{bug_index}'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)        

        bugscpp = BugscppInterface(project, bug_index)
        bugscpp.checkout()
        
        repo_path = bugscpp.get_path_to_repo()
        patch_info = bugscpp.extract_patch_info()
        
        data = list()
        iterate_over_directory(os.path.join(repo_path, src_dir))        
        with open(os.path.join(data_dir, 'token_statistics.json'), 'w') as f:
            json.dump(sorted(data, key=lambda info: info['name']), f, indent=4)
 
if __name__ == "__main__":
    collect_snippet([('libchewing', '8')])
    # collect_token_statistics([('zsh', '1', 'Src', True), ('libchewing', '1', 'src', True), ('berry', '1', 'src', True), ('yara', '1', 'libyara', True)])