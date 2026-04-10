from bs4 import BeautifulSoup
import re

html_content = """
<div class="article-main">
    <p class="page-title">Executing a scenario automation on your tickets</p>
    <p>Executing a Scenario on a Ticket</p>
    <ul>
        <li>Click on any ticket from the dashboard or the ticket list to see its details</li>
        <li>Click on the <strong>Execute scenarios</strong> option from the <strong>More</strong> drop-down menu</li>
        <li>The list of all available scenario automations will be displayed to you.</li>
    </ul>
    <p>Click on the &nbsp;Execute scenarios&nbsp; option from the <strong>More</strong> drop-down menu</p>
</div>
"""

soup = BeautifulSoup(html_content, 'html.parser')
content_element = soup.find(class_='article-main')

# Chèn newline trước/sau các block elements để đảm bảo xuống dòng
for tag in content_element.find_all(['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
    tag.insert_before('\n')
    tag.insert_after('\n')
for tag in content_element.find_all('br'):
    tag.replace_with('\n')
for tag in content_element.find_all('li'):
    tag.insert(0, '- ')
    tag.insert_before('\n')
    tag.insert_after('\n')

# Dùng dấu cách cho các inline elements (như bold, strong) để tránh dính chữ
text_content = content_element.get_text(separator=' ')

# Xử lý các khoảng trắng thừa
text_content = text_content.replace('\xa0', ' ')
# Loại bỏ multiple spaces (nhưng giữ lại newlines)
text_content = re.sub(r'[ \t]+', ' ', text_content)

# Clean up newlines: split by newline, strip spaces, then join
lines = [line.strip() for line in text_content.split('\n')]
lines = [line for line in lines if line]
text_content = '\n'.join(lines)

print("--- RESULT ---")
print(text_content)
print("--- END ---")
