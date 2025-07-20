import sqlite3
import os
from datetime import datetime
from utils.logger_util import LoggerUtil

class PostDatabase:
    def __init__(self, db_path='posts.db'):
        self.db_path = db_path
        self.logger = LoggerUtil().get_logger()
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # posts 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                created_at TEXT,
                summary_sent INTEGER DEFAULT 0,
                inserted_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_post(self, post_id, title, url, created_at):
        """새로운 게시글 삽입 (중복 방지)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO posts (post_id, title, url, created_at)
                VALUES (?, ?, ?, ?)
            ''', (post_id, title, url, created_at))
            
            # 실제로 삽입된 행의 수를 반환
            inserted_rows = cursor.rowcount
            conn.commit()
            return inserted_rows > 0
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            return False
        finally:
            conn.close()
    
    def insert_posts_batch(self, posts):
        """여러 게시글을 배치로 삽입"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_posts = []
        try:
            for post in posts:
                cursor.execute('''
                    INSERT OR IGNORE INTO posts (post_id, title, url, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (post['post_id'], post['title'], post['url'], post['created_at']))
                
                if cursor.rowcount > 0:
                    new_posts.append(post)
            
            conn.commit()
            return new_posts
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            return []
        finally:
            conn.close()
    
    def get_unsent_posts(self):
        """요약이 전송되지 않은 게시글 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT post_id, title, url, created_at
                FROM posts
                WHERE summary_sent = 0
                ORDER BY inserted_at ASC
            ''')
            
            posts = []
            for row in cursor.fetchall():
                posts.append({
                    'post_id': row[0],
                    'title': row[1],
                    'url': row[2],
                    'created_at': row[3]
                })
            
            return posts
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            return []
        finally:
            conn.close()
    
    def mark_as_sent(self, post_id):
        """게시글을 전송 완료로 표시"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE posts
                SET summary_sent = 1
                WHERE post_id = ?
            ''', (post_id,))
            
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_posts(self):
        """모든 게시글 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT post_id, title, url, created_at, summary_sent, inserted_at
                FROM posts
                ORDER BY inserted_at DESC
            ''')
            
            posts = []
            for row in cursor.fetchall():
                posts.append({
                    'post_id': row[0],
                    'title': row[1],
                    'url': row[2],
                    'created_at': row[3],
                    'summary_sent': row[4],
                    'inserted_at': row[5]
                })
            
            return posts
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            return []
        finally:
            conn.close()
    
    def post_exists(self, post_id):
        """게시글이 이미 존재하는지 확인"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT COUNT(*) FROM posts WHERE post_id = ? AND summary_sent = 1
            ''', (post_id,))
            
            count = cursor.fetchone()[0]
            return count > 0
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            return False
        finally:
            conn.close()

if __name__ == '__main__':
    # 테스트 코드
    db = PostDatabase()
    logger = LoggerUtil().get_logger()
    
    # 테스트 데이터 삽입
    test_posts = [
        {
            'post_id': '1234567',
            'title': '테스트 게시글 1',
            'url': 'https://example.com/1',
            'created_at': '2025/07/19 10:00:00'
        },
        {
            'post_id': '1234568',
            'title': '테스트 게시글 2',
            'url': 'https://example.com/2',
            'created_at': '2025/07/19 11:00:00'
        }
    ]
    
    # 배치 삽입 테스트
    new_posts = db.insert_posts_batch(test_posts)
    logger.info(f"새로 삽입된 게시글: {len(new_posts)}개")
    
    # 전체 게시글 조회
    all_posts = db.get_all_posts()
    logger.info(f"전체 게시글: {len(all_posts)}개")
    for post in all_posts:
        logger.info(f"- {post['post_id']}: {post['title']} (전송됨: {post['summary_sent']})")
    
    # 미전송 게시글 조회
    unsent_posts = db.get_unsent_posts()
    logger.info(f"미전송 게시글: {len(unsent_posts)}개")
    
    # 첫 번째 게시글을 전송 완료로 표시
    if unsent_posts:
        first_post = unsent_posts[0]
        db.mark_as_sent(first_post['post_id'])
        logger.info(f"게시글 {first_post['post_id']}를 전송 완료로 표시")
    
    # 다시 미전송 게시글 조회
    unsent_posts = db.get_unsent_posts()
    logger.info(f"미전송 게시글: {len(unsent_posts)}개")

