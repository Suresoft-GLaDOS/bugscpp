import os
from pathlib import Path

from taxonomy import Taxonomy


def generate_wiki_bugscpp_bugs_table(output_file_path="wiki/home.md"):
    table = generate_table()

    if not os.path.isdir("wiki"):
        os.mkdir("wiki")
    with open(output_file_path, "w") as output_file:
        output_file.write(table)


def generate_table():
    table = "# BugsCpp Bugs\n"
    table = (
        table
        + "|Project|BugID|Files|LinesAdd|LinesDel|Methods|Information|\n|--|--|--|--|--|--|--|\n"
    )
    t = Taxonomy()
    for name in t:
        if name == "example":
            continue
        for info in t[name].defects:
            with open(
                Path(t.base) / name / "patch" / Path(info.buggy_patch).name
            ) as buggy:
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
                    if len(lines) > 2 and lines[2] == "changed,":
                        file_changed = lines[0]
                        # buggy patch with insertion and deletion
                        if len(line.split()) == 7:
                            lines_add = int(lines[3])
                            lines_del = int(lines[5])
                        # buggy patch only with deletion
                        elif line[-3] == "-":
                            lines_del = int(lines[3])
                        # buggy patch only with insertion
                        elif line[-3] == "+":
                            lines_add = int(lines[3])
                    if lines[0] == "@@":
                        methods += 1
                table = (
                    table
                    + "|"
                    + name
                    + "|"
                    + str(bug_id)
                    + "|"
                    + str(file_changed)
                    + "|"
                    + str(lines_add)
                    + "|"
                    + str(lines_del)
                    + "|"
                    + str(methods)
                    + "|["
                    + name
                    + "-"
                    + str(bug_id)
                    + "]"
                    + "(https://github.com/Suresoft-GLaDOS/bugscpp/wiki/"
                    + name
                    + "#"
                    + str(bug_id)
                    + ")|\n"
                )
    return table


def generate_patchlog():
    t = Taxonomy()
    for name in t:
        if name == "example":
            continue
        output_file_path = "wiki/" + name + ".md"
        full_patch = ""
        for info in t[name].defects:
            with open(
                Path(t.base) / name / "patch" / Path(info.buggy_patch).name
            ) as buggy:
                # defect_tags
                tag_list = info.tags
                bug_tags = "<strong>Tags</strong><br>\n"
                for tag in tag_list:
                    tag = tag.capitalize()
                    if tag == "Cve":
                        tag = "CVE"
                    bug_tags = (
                        bug_tags
                        + "[`#"
                        + tag
                        + "`](https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp#"
                        + tag
                        + ")\n"
                    )
                bug_tags = bug_tags + "<br>\n"
                buggy_lines = buggy.readlines()
                bug_id = info.id
                # buggy_patch url
                url = t[name].info.url
                if t[name].info.url[-3:] == "git" and name != "libssh":
                    url = url[:-4]
                bug_link = "Link : " + url + "/commit/" + info.hash + "<br>"
                # description of defect
                desc = info.description
                if desc[:3] == "CVE":
                    cve_id = desc.split(" ", 1)[0]
                    desc = desc.split(" ", 1)[1]
                    desc = (
                        desc
                        + "<br>"
                        + "CVE Info: <strong>["
                        + cve_id
                        + "]"
                        + "(https://nvd.nist.gov/vuln/detail/"
                        + cve_id
                        + ")</strong>"
                    )
                bug_desc = "Description: " + desc + "<br>"
                patch_info = ""
                diff_log = ""
                diff_flag = False

                for line in buggy_lines:
                    lines = line.split()
                    if not lines:
                        continue
                    if lines[0] == "--":
                        patch_info = patch_info + "```patch\n" + diff_log + "\n```\n"
                        break
                    if diff_flag:
                        if lines[0] == "diff":
                            patch_info = (
                                patch_info + "```patch\n" + diff_log + "\n```\n"
                            )
                            diff_flag = False
                        if line[0] == "+":
                            line = "-" + line[1:]
                        elif line[0] == "-":
                            line = "+" + line[1:]
                        diff_log += line
                    if lines[0] == "@@":
                        if not diff_log:
                            patch_info = patch_info + "```patch\n" + diff_log + "```\n"
                            diff_log = ""

                    if lines[0] == "+++":
                        diff_flag = True
                        patch_info = (
                            patch_info
                            + "<p><strong>At "
                            + lines[1][2:]
                            + "</strong></p>\n\n"
                        )
                        diff_log = ""
                full_patch = (
                    full_patch
                    + "# #"
                    + str(bug_id)
                    + "\n"
                    + bug_link
                    + bug_desc
                    + patch_info
                    + bug_tags
                )
        with open(output_file_path, "w") as output_file:
            output_file.write(full_patch)


def generate_tag_page(output_file_path="wiki/tags_bugscpp.md"):
    t = Taxonomy()
    tag_dict = {}
    defects_list_with_tag = ""
    for name in t:
        for info in t[name].defects:
            tag_list = info.tags
            for tag in tag_list:
                if tag == "cve":
                    tag = "CVE"
                if not tag_dict.get(tag):
                    tag_dict[tag] = []
                tag_dict[tag].append(name + "#" + str(info.id))
    for tag_name in tag_dict.keys():
        defects_list_with_tag = defects_list_with_tag + "# #" + tag_name
        defects_list_with_tag = (
            defects_list_with_tag
            + "\n<strong>Total Defects with `#"
            + tag_name
            + "`: "
            + str(len(tag_dict[tag_name]))
            + "</strong><br>\n"
        )
        for defect in tag_dict[tag_name]:
            defects_list_with_tag = (
                defects_list_with_tag
                + "["
                + defect
                + "](https://github.com/Suresoft-GLaDOS/bugscpp/wiki/"
                + defect
                + ")<br>\n"
            )
    with open(output_file_path, "w") as output_file:
        output_file.write(defects_list_with_tag)


def generate_sidebar(output_file_path="wiki/_sidebar.md"):
    text_sidebar = (
        '<h1><a href="https://github.com/Suresoft-GLaDOS/bugscpp/wiki">HOME</a></h1>\n'
    )
    text_sidebar = (
        text_sidebar
        + '<h1><a href="https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp">TAGS</a></h1>\n'
    )
    text_sidebar = text_sidebar + "<h2>Lines</h2>\n"
    text_sidebar = text_sidebar + "  <ul>\n"
    text_sidebar = (
        text_sidebar
        + '    <li><a href="https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp#single-line">#Single_Line</a></li>\n'
    )
    text_sidebar = (
        text_sidebar
        + '    <li><a href="https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp#multi-line">#Multi_Lines</a></li>\n'
    )
    text_sidebar = text_sidebar + "  </ul>\n"
    text_sidebar = text_sidebar + "<h2>Patch Type</h2>\n"
    text_sidebar = text_sidebar + "  <ul>\n"
    text_sidebar = (
        text_sidebar
        + '    <li><a href="https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp#added">#Added</a></li>\n'
    )
    text_sidebar = (
        text_sidebar
        + '    <li><a href="https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp#removed">#Removed</a></li>\n'
    )
    text_sidebar = (
        text_sidebar
        + '    <li><a href="https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp#modified">#Modified</a></li>\n'
    )
    text_sidebar = text_sidebar + "  </ul>\n"
    text_sidebar = text_sidebar + "<h2>Error Type</h2>\n"
    text_sidebar = text_sidebar + "  <ul>\n"
    text_sidebar = (
        text_sidebar
        + '    <li><a href="https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp#invalid-condition">#Invalid_Condition</a></li>\n'
    )
    text_sidebar = (
        text_sidebar
        + '    <li><a href="https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp#invalid-format-string">#Invalid_Format_String</a></li>\n'
    )
    text_sidebar = (
        text_sidebar
        + '    <li><a href="https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp#memory-error">#Memory_Error</a></li>\n'
    )
    text_sidebar = (
        text_sidebar
        + '    <li><a href="https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp#logical-error">#Logical_Error</a></li>\n'
    )
    text_sidebar = (
        text_sidebar
        + '    <li><a href="https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp#omission">#Omission</a></li>\n'
    )
    text_sidebar = (
        text_sidebar
        + '    <li><a href="https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp#infinite-loop-error">#Infinite_Loop</a></li>\n'
    )
    text_sidebar = (
        text_sidebar
        + '    <li><a href="https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp#division-by-zero">#Division_by_Zero</a></li>\n'
    )
    text_sidebar = text_sidebar + "  </ul>\n"
    text_sidebar = (
        text_sidebar
        + '<h3><a href="https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp#CVE">#CVE</a></h3>\n'
    )
    text_sidebar = (
        text_sidebar
        + '<h3><a href="https://github.com/Suresoft-GLaDOS/bugscpp/wiki/tags_bugscpp#address-sanitizer">#Address_Sanitizer</a></h3>\n'
    )
    with open(output_file_path, "w") as output_file:
        output_file.write(text_sidebar)


if __name__ == "__main__":
    generate_wiki_bugscpp_bugs_table()
    generate_patchlog()
    generate_tag_page()
    generate_sidebar()
