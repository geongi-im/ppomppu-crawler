
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils.logger_util import LoggerUtil

def fetch_posts(keyword):
    logger = LoggerUtil().get_logger()
    base_url = "https://www.ppomppu.co.kr/zboard/zboard.php?id=phone&page=1&search_type=sub_memo&keyword="
    url = f"{base_url}{keyword}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        response.encoding = 'euc-kr' # 뽐뿌 웹사이트는 euc-kr 인코딩을 사용
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    
    posts = []
    
    # 게시글 목록을 포함하는 테이블 찾기 (id가 'revolution_main_table'인 테이블)
    board_table = soup.find('table', id='revolution_main_table')
    
    if not board_table:
        logger.warning("게시글 테이블을 찾을 수 없습니다.")
        return []

    # 각 게시글 행(tr)을 순회
    # 'baseList' 클래스를 가진 tr 태그만 선택 (공지사항 제외)
    for row in board_table.find_all('tr', class_='baseList'):
        try:
            # 게시글 번호 (td의 text)
            post_id_tag = row.find('td', class_='baseList-numb')
            if not post_id_tag or not post_id_tag.text.strip().isdigit():
                continue # 공지사항 등 번호가 없는 행은 건너뜀
            post_id = post_id_tag.text.strip()

            # 게시글 제목 및 URL
            title_tag = row.find('a', class_='baseList-title')
            
            if not title_tag:
                continue
            title = title_tag.text.strip()
            link = title_tag.get('href')
            url = f"https://www.ppomppu.co.kr/zboard/{link}"

            # 게시 시간 (time 태그의 text)
            created_at_tag = row.find('time', class_='baseList-time')
            created_at = created_at_tag.text.strip() if created_at_tag else ""

            # '25/07/18' 또는 '13:05:32' 형식 처리
            if created_at and ':' in created_at: # 시간만 있는 경우 (오늘 날짜)
                today = datetime.now().strftime('%y/%m/%d')
                created_at = f"{today} {created_at}"
            elif created_at and created_at.count('/') == 2: # 년/월/일 형식인 경우
                # 뽐뿌는 25/07/18 처럼 연도를 두자리로 표시하므로 20을 붙여줌
                created_at = f"20{created_at} 00:00:00" # 시간 정보가 없으므로 00:00:00으로 설정
            
            posts.append({
                'post_id': post_id,
                'title': title,
                'url': url,
                'created_at': created_at
            })
        except Exception as e:
            logger.error(f"Error parsing row: {e}, Row content: {row}")
            continue

    return posts

def fetch_post_content(url):
    logger = LoggerUtil().get_logger()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = 'euc-kr' # 뽐뿌 웹사이트는 euc-kr 인코딩을 사용
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching post content from {url}: {e}")
        return None
    
    soup = BeautifulSoup(response.text, 'lxml')
    
    # td.board-contents 클래스를 가진 요소에서 본문 내용 가져오기
    content_td = soup.select_one('td.board-contents')
    
    if content_td:
        # 불필요한 태그 제거 (예: 스크립트, 스타일, 광고 등)
        for script_or_style in content_td(['script', 'style', 'iframe', 'ins']):
            script_or_style.extract()
        
        # 텍스트만 추출하여 반환
        return content_td.get_text(separator=' ', strip=True)
    else:
        logger.warning(f"게시글 본문을 찾을 수 없습니다: {url}")
        return None

if __name__ == '__main__':
    # 테스트 코드
    logger = LoggerUtil().get_logger()
    keyword = "폴드7"
    crawled_posts = fetch_posts(keyword)
    if crawled_posts:
        for post in crawled_posts:
            logger.info(f"게시글: {post}")
            # 게시글 본문 테스트
            content = fetch_post_content(post['url'])
            if content:
                logger.info(f"본문 요약 (처음 200자): {content[:200]}...")
            else:
                logger.warning("본문 내용을 가져올 수 없습니다.")
            logger.info("="*50)
    else:
        logger.warning("크롤링된 게시글이 없습니다.")


