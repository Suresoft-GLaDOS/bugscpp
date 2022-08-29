import os
from taxonomy import Taxonomy
from pathlib import Path


def generate_wiki_defects4cpp_bugs_table(output_file_path="wiki/home.md"):
    table = generate_table()

    if not os.path.isdir('wiki'):
        os.mkdir('wiki')
    with open(output_file_path, 'w') as output_file:
        output_file.write(table)

def generate_table():
    table = "# Defects4cpp Bugs\n"
    table = table + "|Project|BugID|Files|LinesAdd|LinesDel|Methods|More Description|\n|--|--|--|--|--|--|--|\n"
    t = Taxonomy()
    for name in t:
        for info in t[name].defects:
            with open(Path(t.base) / name / 'patch' / Path(info.buggy_patch).name) as buggy:
                buggy_lines = buggy.readlines()
                bug_id = info.id
                file_changed = 0
                lines_add = 0
                lines_del = 0
                methods = 0
                for line in buggy_lines:
                    lines = line.split()
                    if not lines:
                        continue
                    # check the number of files , added_lines , deleted_lines
                    if len(lines) > 2 and lines[2] == 'changed,':
                        file_changed = lines[0]
                        # buggy patch with insertion and deletion
                        if len(line.split()) == 7:
                            lines_add = int(lines[3])
                            lines_del = int(lines[5])
                        # buggy patch only with deletion
                        elif line[-3] == '-':
                            lines_del = int(lines[3])
                        # buggy patch only with insertion
                        elif line[-3] == '+':
                            lines_add = int(lines[3])
                    if lines[0] == '@@':
                        methods += 1
                table = table + "|" + name + "|" + str(bug_id) + "|" + str(file_changed) + "|" + str(lines_add) + "|" + str(lines_del) + "|" + str(methods) + \
                        "|[" + "More " + name + "-" + str(bug_id) + "]" + "(https://github.com/Suresoft-GLaDOS/defects4cpp/wiki/" + name + "#" + str(bug_id) + ")|\n"
    return table

def generate_patchlog():
    t = Taxonomy()
    for name in t:
        output_file_path = "wiki/" + name + ".md"
        full_patch = ""
        for info in t[name].defects:
            with open(Path(t.base) / name / 'patch' / Path(info.buggy_patch).name) as buggy:
                buggy_lines = buggy.readlines()
                bug_id = info.id
                # buggy_patch url
                url = t[name].info.url
                if t[name].info.url[-3:] == 'git' and name != 'libssh':
                    url = url[:-4]
                bug_link = "# #" + str(bug_id) + "\nLink : " + url + "/commit/" + info.hash + "<br>"
                # description of defect
                desc = info.description
                if desc[:3] == 'CVE':
                    cve_id = desc.split(' ', 1)[0]
                    desc = desc.split(' ', 1)[1]
                    desc = desc + '<br>' + 'More Information of CVE: [' + cve_id + ']' + '(https://nvd.nist.gov/vuln/detail/' + cve_id + ')'
                bug_desc = "Description: " + desc + '<br>'
                patch_info = ""
                diff_log = ""
                diff_flag = False

                for line in buggy_lines:
                    lines = line.split()
                    if not lines:
                        continue
                    if lines[0] == '--':
                        patch_info = patch_info + "```patch\n" + diff_log + "\n```\n"
                        break
                    if diff_flag:
                        if lines[0] == 'diff':
                            patch_info = patch_info + "```patch\n" + diff_log + "\n```\n"
                            diff_flag = False
                        if line[0] == '+':
                            line = '-' + line[1:]
                        elif line[0] == '-':
                            line = '+' + line[1:]
                        diff_log += line
                    if lines[0] == '@@':
                        if not diff_log:
                            patch_info = patch_info + "```patch\n" + diff_log + "```\n"
                            diff_log = ""

                    if lines[0] == '+++':
                        diff_flag = True
                        patch_info = patch_info + "<p><strong>At " + lines[1][2:] + "</strong></p>\n\n"
                        diff_log = ""


                full_patch = full_patch + bug_link + bug_desc + patch_info
        with open(output_file_path, 'w') as output_file:
            output_file.write(full_patch)

if __name__ == "__main__":
    generate_wiki_defects4cpp_bugs_table()
    generate_patchlog()
