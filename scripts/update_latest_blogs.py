import requests

GENERATE_FILE_NAME = "README.md"
ZENN_BASE = "https://zenn.dev/"
ZENN_URL = "https://zenn.dev/api/articles?username=naoki0103"
QIITAURL = "https://qiita.com/api/v2/users/c-naoki/items"


def fetch_data_from_api(zenn_url: str, qiita_url: str) -> tuple[dict, dict]:
    """
    Get json data from Zenn/Qiita API
    """
    try:
        z_res = requests.get(zenn_url)
        z_res.raise_for_status()
        q_res = requests.get(qiita_url)
        q_res.raise_for_status()
        return z_res.json(), q_res.json()
    except (requests.RequestException, ValueError) as err:
        print(f"Error while getting data from API - {err}")
        return None


def prepare_content(zenn_ls: list, qiita_ls: list) -> str:
    """
    format a feed data to markdown
    """
    if zenn_ls is None or qiita_ls is None:
        return

    articles_ls = []
    for za in zenn_ls[:5]:
        article_txt = f"- {za['emoji']} {za['title']} [[Zenn]]({ZENN_BASE + za['path']})"
        qiita_url = next(
            (qa["url"] for qa in qiita_ls if qa["title"] == za["title"]), None
        )
        if qiita_url:
            article_txt += f" [[Qiita]]({qiita_url})"
        articles_ls.append(article_txt)

    return """
    {zennArticle}
    """.strip().format(zennArticle="\n".join(articles_ls))


def write_to_file(file_name: str, content: str) -> None:
    """
    write blogs content to `file_name`
    """
    with open(file_name, "r", encoding="utf-8") as file:
        lines = file.readlines()

    inside = False
    updated_lines = []
    for line in lines:
        if line.strip() == "<!--START_SECTION:blogs-->":
            inside = True
            updated_lines.append(line)
            updated_lines.append(content + "\n")
        elif line.strip() == "<!--END_SECTION:blogs-->":
            inside = False

        if not inside:
            updated_lines.append(line)

    with open(file_name, "w", encoding="utf-8") as file:
        file.writelines(updated_lines)

if __name__ == "__main__":
    zenn_json, qiita_json = fetch_data_from_api(ZENN_URL, QIITAURL)
    content = prepare_content(zenn_json["articles"], qiita_json)

    if content:
        write_to_file(GENERATE_FILE_NAME, content)
