
# kevin-story2009 블로그 미러 - 구글 검색 노출용

네이버 블로그 `https://blog.naver.com/kevin-story2009/` 글을 구글 검색에 노출시키기 위한 미러 사이트입니다.

네이버 블로그는 구글봇 수집을 제한해서 구글에서 검색이 잘 안 됩니다. 이 저장소는 RSS를 읽어서 GitHub Pages에 미러 HTML을 만들어 구글에 색인시키는 자동화입니다.

## 동작 방식
1. 매일 KST 09:00 GitHub Actions가 `scripts/sync.py` 실행
2. `https://rss.blog.naver.com/kevin-story2009.xml` 에서 최신 20개 글 수집
3. `posts/{글번호}.html` 생성, `index.html`, `sitemap.xml` 재생성
4. 자동 커밋 & 푸시 → GitHub Pages 배포 → 구글이 sitemap 크롤링

## 최초 1회 설정 (5분)

### 1. GitHub 저장소 만들기
1. GitHub에서 `blog-mirror` 라는 이름으로 **Public** 저장소 생성
2. 이 폴더의 모든 파일을 그대로 업로드 (drag & drop)
   - `scripts/sync.py`
   - `.github/workflows/sync.yml`
   - `robots.txt` 등

### 2. Pages 켜기
- 저장소 Settings → Pages → Source: **Deploy from a branch**, Branch: **main** / **/(root)** 선택 → Save

### 3. Actions 권한 켜기
- Settings → Actions → General → Workflow permissions → **Read and write permissions** 체크 → Save

### 4. 첫 실행
- Actions 탭 → "Sync Naver Blog to GitHub Pages" → **Run workflow** 버튼 클릭
- 1분 후 `https://당신의아이디.github.io/blog-mirror/` 접속 확인

### 5. 구글 서치콘솔에 제출
1. https://search.google.com/search-console 접속 → 속성 추가 (URL 접두어) → `https://당신의아이디.github.io/blog-mirror/` 입력
2. HTML 파일 방식 확인 (GitHub Pages는 파일 업로드 가능)
3. 좌측 Sitemaps → `sitemap.xml` 입력 → 제출

며칠 뒤 구글에서 `site:당신의아이디.github.io` 검색하면 글이 잡힙니다.

## 로컬 테스트
```bash
python scripts/sync.py
```
`index.html` 파일을 브라우저로 열면 됩니다.

## 문제 해결
- 글이 안 올라옴: 네이버 블로그 관리 → 기본 설정 → RSS 공개 허용 확인
- 구글에 안 잡힘: 서치콘솔에서 URL 검사 → 색인 생성 요청
