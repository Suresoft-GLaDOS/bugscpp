from pathlib import Path

from bugscpp.taxonomy import Taxonomy

TARGET_TEXT = "@TABLE_OF_DEFECTS@"


def generate_readme(
    taxonomy: Taxonomy,
    input_file_path="README.rst.template",
    output_file_path="README.rst",
):
    table = generate_table(taxonomy)
    assert Path(input_file_path).is_file()
    with open(input_file_path, "r") as input_file:
        content = input_file.read()
        content = content.replace(TARGET_TEXT, table)
    with open(output_file_path, "w") as output_file:
        output_file.write(content)


def generate_table(taxonomy):
    table = ".. list-table::\n   :header-rows: 1\n\n   * - Project\n     - # of bugs\n     - Short Description\n"
    sum_of_defects = 0
    for project_name in taxonomy._lazy_taxonomy.keys():
        defects_num = len(taxonomy[project_name].defects)
        project_url = str(taxonomy[project_name].info).split("'")[1]
        project_name_with_url = "`" + str(project_name) + " <" + project_url + "/>`_"
        project_short_desc = str(taxonomy[project_name].info).split("'")[3]
        sum_of_defects = sum_of_defects + defects_num
        table = (
            table
            + "   * - "
            + project_name_with_url
            + "\n     - "
            + str(defects_num)
            + "\n     - "
            + project_short_desc
            + "\n"
        )
    table = (
        table
        + "   * - SUM\n     - "
        + str(sum_of_defects)
        + "\n     - Sum of all defects\n"
    )
    return table


if __name__ == "__main__":
    generate_readme(Taxonomy())
