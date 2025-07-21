import time
from crawler import fetch_posts
from database import PostDatabase
from summarizer import PostSummarizer
from datetime import datetime
from dotenv import load_dotenv
from utils.telegram_util import TelegramUtil
from utils.logger_util import LoggerUtil
import os

def main():
    load_dotenv()

    # 환경변수 설정안되어있으면 오류 발생
    if not os.getenv("SEARCH_KEYWORD") or not os.getenv("GEMINI_API_KEY"):
        raise ValueError("환경변수가 설정되어 있지 않습니다.")
    
    SEARCH_KEYWORD = os.getenv("SEARCH_KEYWORD")
    
    telegram_bot = TelegramUtil()
    db = PostDatabase()
    summarizer = PostSummarizer()
    logger = LoggerUtil().get_logger()
    this_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    logger.info("크롤링 시작...")
    posts = fetch_posts(SEARCH_KEYWORD)
    logger.info(f"{len(posts)}개의 게시글 크롤링 완료.")

    new_posts_count = 0
    new_posts_to_summarize = []

    for post in posts:
        if not db.post_exists(post["post_id"]):
            db.insert_post(post["post_id"], post["title"], post["url"], post["created_at"])
            new_posts_count += 1
            new_posts_to_summarize.append(post)
    
    logger.info(f"{new_posts_count}개의 새로운 게시글 발견 및 저장.")

    if new_posts_to_summarize:
        logger.info("새로운 게시글 요약 및 전송 시작...")
        
        for post in new_posts_to_summarize:
            try:
                logger.info(f"게시글 {post['post_id']} 요약 시작...")
                
                # 게시글 한 개씩 요약
                summary = summarizer.summarize_post(
                    title=post['title'],
                    url=post['url']
                )
                
                if summary:
                    logger.info(f"게시글 {post['post_id']} 요약 완료.")
                    
                    # 텔레그램 메시지 구성 및 전송
                    message = f"<a href=\"{post['url']}\">{post['title']}</a>\n\n[요약]\n{summary}"
                    try:
                        telegram_bot.send_message(message)
                        logger.info(f"게시글 {post['post_id']} 전송 완료.")
                        db.mark_as_sent(post["post_id"])
                    except Exception as e:
                        logger.error(f"게시글 {post['post_id']} 전송 실패: {e}")
                        db.mark_as_sent(post["post_id"])
                else:
                    logger.warning(f"게시글 {post['post_id']} 요약 실패.")
                    
            except Exception as e:
                logger.error(f"게시글 {post['post_id']} 처리 중 오류 발생: {e}")
                continue
        
        logger.info("모든 게시글 처리 완료.")
    else:
        logger.info("새로운 게시글이 없어 요약 및 전송을 건너뜁니다.")

    logger.info("작업 완료.")

if __name__ == "__main__":
    main()


