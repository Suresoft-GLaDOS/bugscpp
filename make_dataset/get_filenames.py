from bs4 import BeautifulSoup

html_file_name = "./results/cpp_peglib_1/cpp_peglib-buggy-1-1/summary.html"

try:
  with open(html_file_name, "r") as html_file:
    html_content = html_file.read()

  # BeautifulSoup으로 HTML 파싱
  soup = BeautifulSoup(html_content, 'html.parser')

  # 파일 이름들을 저장할 리스트 생성
  file_names = []

  # 파일 리스트 테이블 내의 모든 <th> 요소를 찾아서 파일 이름을 추출하여 리스트에 추가
  for th_tag in soup.select('table.file-list th[scope="row"]'):
      file_name = th_tag.get_text(strip=True)  # 공백 제거하여 파일 이름 추출
      file_names.append(file_name)

  # 추출된 파일 이름들 출력
  print(file_names)

except FileNotFoundError:
  print(f"error: '{html_file_name}' is not found")