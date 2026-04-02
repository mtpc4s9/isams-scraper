from bs4 import BeautifulSoup

def parse_applet(out):
    with open("classlink_applet.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
    out.write("--- APPLET PAGE URLS (View All Links) ---\n")
    topics = soup.find_all("a", href=True)
    for a in topics:
        text = a.get_text(strip=True)
        if 'View All' in text or 'view all' in text.lower():
            out.write(f"Topic Link: {a['href']} | Text: {text}\n")

def parse_article(out):
    with open("classlink_article.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
    out.write("\n--- ARTICLE INFO ---\n")
    
    # Try to find typical headers
    h1s = soup.find_all("h1")
    for h in h1s:
        out.write(f"H1: {h.get_text(strip=True)}\n")
        
    # Article details: product, audience, name
    spans = soup.find_all("span")
    for s in spans:
        txt = s.get_text(strip=True)
        if any(keyword in txt for keyword in ['Product', 'Audience', 'Title']):
            out.write(f"Possible Label/Value: {txt}\n")
            parent = s.parent.get_text(strip=True)
            out.write(f"  Parent context: {parent}\n")

    # For related articles:
    out.write("\n--- RELATED ARTICLES ---\n")
    related = soup.find_all("a", href=lambda x: x and '/article/' in x)
    for r in related:
        out.write(f"Related: {r.get_text(strip=True)} | {r['href']}\n")

if __name__ == "__main__":
    with open("parse_output.txt", "w", encoding="utf-8") as out:
        parse_applet(out)
        parse_article(out)
