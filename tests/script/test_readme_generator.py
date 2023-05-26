from pathlib import Path

from bugscpp.taxonomy import Taxonomy
from readme_generator import generate_readme


def test_readme_generator(tmpdir):
    output_readme_path = tmpdir / "README.rst"
    input_template_file_path = (
        Path(__file__).parent.parent.parent / "README.rst.template"
    )
    input_origin_readme_path = Path(__file__).parent.parent.parent / "README.rst"
    generate_readme(Taxonomy(), input_template_file_path, output_readme_path)

    readme_origin = open(input_origin_readme_path, "r")
    readme_output = open(output_readme_path, "r")

    assert (
        readme_origin.readlines() == readme_output.readlines()
    ), "README.rst is not correct!"
