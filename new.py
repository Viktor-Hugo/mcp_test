import threading
import requests
import time
from functools import wraps

# 로깅 데코레이터
def log_execution(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] {func.__name__} 시작")
        start = time.time()
        try:
            result = func(*args, **kwargs)
            print(f"[LOG] {func.__name__} 성공 (소요시간: {time.time() - start:.2f}s)")
            return result
        except Exception as e:
            print(f"[ERROR] {func.__name__}: {e}")
            raise
    return wrapper

class WebScraper:
    def __init__(self, urls, output_file):
        self.urls = urls
        self.output_file = output_file
        self.results = []
        self.lock = threading.Lock()

    @log_execution
    def fetch_and_parse(self, url):
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            title = self.parse_title(resp.text)
            with self.lock:
                self.results.append((url, title))
        else:
            raise Exception(f"HTTP {resp.status_code}")

    def parse_title(self, html):
        start = html.find('<title>')
        end = html.find('</title>', start)
        if start != -1 and end != -1:
            return html[start+7:end].strip()
        return "No Title"

    @log_execution
    def run_multithreaded(self):
        threads = []
        for url in self.urls:
            t = threading.Thread(target=self.fetch_and_parse, args=(url,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        self.save_results()

    @log_execution
    def save_results(self):
        with open(self.output_file, 'w', encoding='utf-8') as f:
            for url, title in self.results:
                f.write(f"{url}\t{title}\n")

if __name__ == "__main__":
    urls = [
        "https://www.python.org",
        "https://www.github.com",
        "https://www.naver.com",
        "https://www.google.com"
    ]
    scraper = WebScraper(urls, "results.txt")
    scraper.run_multithreaded()
    print("모든 작업 완료!")
