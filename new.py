import asyncio
import time
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

# 비동기 HTTP 요청을 위한 aiohttp 라이브러리 필요
# pip install aiohttp
try:
    import aiohttp
except ImportError:
    print("aiohttp 라이브러리가 필요합니다. 'pip install aiohttp' 명령어로 설치해주세요.")
    exit()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] (%(threadName)s) %(message)s',
)

class AsyncDataFetcher:
    """
    여러 URL로부터 데이터를 비동기적으로 수집하는 클래스.
    동시 요청 수를 제어하여 서버 부하를 조절합니다.
    """

    def __init__(self, urls: List[str], max_concurrent_requests: int = 5):
        """
        초기화 메서드
        :param urls: 데이터를 가져올 URL 목록
        :param max_concurrent_requests: 동시에 실행할 최대 요청 수
        """
        self.urls = self._validate_urls(urls)
        # Semaphore를 사용하여 동시 실행 작업 수를 제어
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.results: List[Dict[str, Any]] = []
        self.session: Optional[aiohttp.ClientSession] = None

    def _validate_urls(self, urls: List[str]) -> List[str]:
        """URL 유효성을 검사하고 중복을 제거합니다."""
        valid_urls = set()
        for url in urls:
            if urlparse(url).scheme in ['http', 'https']:
                valid_urls.add(url)
            else:
                logging.warning(f"유효하지 않은 URL 형식입니다: {url}")
        return list(valid_urls)

    async def _fetch_one(self, url: str) -> Optional[Dict[str, Any]]:
        """
        하나의 URL에서 데이터를 가져오는 내부 메서드.
        Semaphore를 사용하여 동시 요청 수를 제어합니다.
        """
        async with self.semaphore:
            logging.info(f"요청 시작: {url}")
            try:
                # self.session은 run 메서드에서 생성됨
                if not self.session:
                    raise RuntimeError("ClientSession이 초기화되지 않았습니다.")
                
                async with self.session.get(url, timeout=10) as response:
                    response.raise_for_status()  # 200번대 상태 코드가 아니면 예외 발생
                    data = await response.json()
                    logging.info(f"요청 성공: {url}")
                    return {'url': url, 'status': response.status, 'data': data}
            except asyncio.TimeoutError:
                logging.error(f"타임아웃 발생: {url}")
            except aiohttp.ClientError as e:
                logging.error(f"클라이언트 에러 발생: {url} - {e}")
            except Exception as e:
                logging.error(f"알 수 없는 에러 발생: {url} - {e}")
            return None

    async def run(self) -> List[Dict[str, Any]]:
        """
        데이터 수집을 시작하는 메인 메서드.
        """
        start_time = time.time()
        logging.info(f"총 {len(self.urls)}개의 URL에 대한 데이터 수집을 시작합니다.")

        # aiohttp.ClientSession을 생성하여 커넥션 풀을 재사용
        async with aiohttp.ClientSession() as session:
            self.session = session
            # 각 URL에 대한 fetch 작업을 비동기 태스크(Task)로 만듭니다.
            tasks = [self._fetch_one(url) for url in self.urls]
            
            # asyncio.gather를 사용하여 모든 태스크가 완료될 때까지 기다립니다.
            # return_exceptions=True로 설정하면 예외가 발생해도 중단되지 않고 결과에 포함됩니다.
            responses = await asyncio.gather(*tasks, return_exceptions=True)

        # 결과 처리
        for res in responses:
            if isinstance(res, dict) and res is not None:
                self.results.append(res)
            elif isinstance(res, Exception):
                logging.warning(f"작업 중 예외가 결과에 포함되었습니다: {res}")
        
        end_time = time.time()
        logging.info(f"데이터 수집 완료. 총 소요 시간: {end_time - start_time:.2f}초")
        return self.results


# --- 코드 실행 부분 ---
if __name__ == "__main__":
    # 테스트용 공개 API (JSONPlaceholder)
    # 일부러 중복되고 순서가 섞인 URL을 제공
    sample_urls = [
        f"https://jsonplaceholder.typicode.com/posts/{i}" for i in range(1, 21)
    ]
    sample_urls.extend([
        "https://jsonplaceholder.typicode.com/posts/1", # 중복 URL
        "https://invalid-url-for-testing.com", # 잘못된 URL
        f"https://jsonplaceholder.typicode.com/comments/{i}" for i in range(1, 11)
    ])

    # 1. 클래스 인스턴스 생성
    # 최대 7개의 요청을 동시에 처리하도록 설정
    fetcher = AsyncDataFetcher(urls=sample_urls, max_concurrent_requests=7)

    # 2. 비동기 이벤트 루프를 실행하여 데이터 수집 시작
    # asyncio.run()은 async def로 정의된 함수를 실행하고 루프를 관리합니다.
    final_results = asyncio.run(fetcher.run())

    # 3. 결과 출력
    print("\n--- 최종 수집 결과 ---")
    print(f"성공적으로 가져온 데이터 개수: {len(final_results)}")

    if final_results:
        print("수집된 데이터 샘플 3개:")
        for result in final_results[:3]:
            # 데이터가 너무 길 수 있으므로 일부만 출력
            post_title = result.get('data', {}).get('title', 'N/A')
            print(f"  - URL: {result['url']}, Status: {result['status']}, Title: '{post_title}'")