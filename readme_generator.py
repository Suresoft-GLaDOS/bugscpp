from defects4cpp.taxonomy import Taxonomy

TARGET_TEXT = "@TABLE_OF_DEFECTS@"

def generate_readme(taxonomy: Taxonomy, input_file_path = "README.rst.template", output_file_path = "README.rst"):
    table = generate_table(taxonomy)
    with open(input_file_path, 'r') as f:
        text = f.read()
        text = text.replace(TARGET_TEXT, table)
    with open(output_file_path, 'w') as f:
        f.write(text)

def generate_table(taxonomy):
    table = ".. list-table:: \n   :header-rows: 1\n\n   * - Project\n     - # of bugs\n"
    for project_name in list(taxonomy._lazy_taxonomy.keys()):
        defects_num = len(taxonomy[project_name].defects)
        table = table + "   * - " + project_name + "\n     - " + str(defects_num) + "\n"
    return table

if __name__ == "__main__":
    generate_readme(Taxonomy())
