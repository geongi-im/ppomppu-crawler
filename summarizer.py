import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from crawler import fetch_post_content
from utils.logger_util import LoggerUtil

class PostSummarizer:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.logger = LoggerUtil().get_logger()
        self.prompt_path = os.path.dirname(os.path.abspath(__file__))
    
    def summarize_post(self, title, content=None, url=None):
        """게시글 요약 생성"""
        
        try:
            # 본문이 없으면 URL에서 가져오기 시도
            if not content and url:
                content = fetch_post_content(url)

            if not content:
                raise Exception("본문 내용을 가져올 수 없습니다.")

            model = "gemini-2.0-flash-lite"
            
            # 프롬프트 템플릿에 title과 content를 포함
            user_prompt_template = open(os.path.join(self.prompt_path, "user_prompt.md"), "r", encoding="utf-8").read()
            user_prompt_with_data = f"{user_prompt_template}\n\n제목: {title}\n\n본문 내용:\n{content}"
            
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=user_prompt_with_data),
                    ],
                ),
            ]

            generate_content_config = types.GenerateContentConfig(
            temperature=0.7,
            response_mime_type="text/plain",
            system_instruction=[
                types.Part.from_text(
                    text=open(os.path.join(self.prompt_path, "system_prompt.md"), "r", encoding="utf-8").read()
                ),
            ],
        )
            
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=generate_content_config
            )
            result = response.text.strip().replace("```", "").replace("```text", "").replace("text", "")
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return f"[요약 실패] {title} - 요약 생성 중 오류가 발생했습니다."
    
    def summarize_posts_batch(self, posts):
        """여러 게시글을 배치로 요약"""
        summaries = []
        for post in posts:
            summary = self.summarize_post(
                title=post['title'],
                url=post['url']
            )
            summaries.append({
                'post_id': post['post_id'],
                'title': post['title'],
                'url': post['url'],
                'summary': summary,
                'created_at': post['created_at']
            })
        return summaries

if __name__ == '__main__':
    # 테스트 코드
    summarizer = PostSummarizer()
    logger = LoggerUtil().get_logger()
    
    # 테스트 게시글
    test_post = {
        'post_id': '3871406',
        'title': '폴드7 자급제 저도 졸업했습니다(hmall)',
        'url': 'https://www.ppomppu.co.kr/zboard/view.php?id=phone&page=1&divpage=700&search_type=sub_memo&keyword=%ED%8F%B4%EB%93%9C7&no=3871406',
        'created_at': '2025/07/19 13:05:32'
    }
    
    # 단일 게시글 요약 테스트
    summary = summarizer.summarize_post(
        title=test_post['title'],
        url=test_post['url']
    )
    
    logger.info("=== 게시글 요약 테스트 ===")
    logger.info(f"제목: {test_post['title']}")
    logger.info(f"요약: {summary}")
    
    # 배치 요약 테스트
    test_posts = [test_post]
    summaries = summarizer.summarize_posts_batch(test_posts)
    
    logger.info("=== 배치 요약 테스트 ===")
    for summary_data in summaries:
        logger.info(f"게시글 ID: {summary_data['post_id']}")
        logger.info(f"제목: {summary_data['title']}")
        logger.info(f"요약: {summary_data['summary']}")

