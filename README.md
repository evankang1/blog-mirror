
# kevin-story2009 블로그 미러 - 구글 검색 노출용

네이버 블로그 `https://blog.naver.com/kevin-story2009/` 글을 구글 검색에 노출시키기 위한 미러 사이트입니다.

네이버 블로그는 구글봇 수집을 제한해서 구글에서 검색이 잘 안 됩니다. 이 저장소는 RSS를 읽어서 GitHub Pages에 미러 HTML을 만들어 구글에 색인시키는 자동화입니다.

## 동작 방식
1. `Sync Naver Blog Mirror` 워크플로가 `push` 또는 매일 KST 09:10에 `scripts/sync.py` 실행
2. `https://rss.blog.naver.com/kevin-story2009.xml` 에서 최신 글을 읽고, 중복/무효 링크/형식이 이상한 항목을 필터링
3. `posts/{글번호}.html` 생성, `index.html`, `sitemap.xml`, `robots.txt`를 다시 생성
4. 생성 직후 merge conflict 마커와 `<script>` 태그를 정리해서 정적 페이지를 깨끗하게 유지
5. 자동 커밋 & 푸시 → `Deploy Blog Mirror to GitHub Pages` 워크플로가 Pages 배포 → 구글이 sitemap 크롤링

### 현재 자동화 기준
- 동기화 워크플로: `.github/workflows/sync.yml` (`Sync Naver Blog Mirror`)
- 배포 워크플로: `.github/workflows/pages.yml` (`Deploy Blog Mirror to GitHub Pages`)
- 실행 시점: `main` 브랜치 push 시 + 매일 UTC 00:10 (KST 09:10)
- 생성물 검증: `index.html`과 `sitemap.xml` 에서 병합 마커와 script 태그가 없는지 확인
- sitemap 정리 규칙: 중복 URL 제거, 최신 순 정렬, 상위 100개 항목만 유지

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
- Actions 탭 → "Sync Naver Blog Mirror" → **Run workflow** 버튼 클릭
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
이 명령으로 `index.html`, `sitemap.xml`, `posts/` 내용을 다시 생성합니다. 생성 후에는 브라우저에서 `index.html`을 열어 목록과 sitemap 구조를 확인하면 됩니다.

## 문제 해결
- 글이 안 올라옴: 네이버 블로그 관리 → 기본 설정 → RSS 공개 허용 확인
- sitemap이 비정상적: `.github/workflows/sync.yml`의 검증 단계 또는 `scripts/sync.py`의 sanitize 로직 확인
- 구글에 안 잡힘: 서치콘솔에서 URL 검사 → 색인 생성 요청
- HTML 상단에 이상한 텍스트가 보임: merge conflict 마커와 `<script>` 태그가 남았는지 확인하고, `scripts/sync.py`의 sanitize 함수 재검증

## 운영 메모: 배포 전 체크리스트

다음 항목을 브랜치 배포 전에 확인하면 안전합니다.

- [ ] 로컬/CI에서 `python scripts/sync.py` 실행 후 정상 종료
- [ ] `index.html` 상단에 merge conflict 마커가 없는지 확인
- [ ] `sitemap.xml`에서 `<script>` 태그와 `<<<<<<<` / `>>>>>>>` 문자열이 없는지 확인
- [ ] `posts/` 디렉터리에 최신 글 번호 HTML이 생성되었는지 확인
- [ ] 브랜치가 `main` 기준으로 최신 상태인지 확인
- [ ] GitHub Actions에서 `Sync Naver Blog Mirror` 워크플로가 성공했는지 확인
- [ ] Pages 배포 워크플로 `Deploy Blog Mirror to GitHub Pages`가 정상 완료되었는지 확인
- [ ] 공개 페이지 주소가 정상 접속되는지 확인
- [ ] Google Search Console에 sitemap 재제출이 필요한 경우 수행

> 운영 기준: 배포 전에는 생성물 검증을 우선하고, 마지막에 Pages 배포 결과를 확인한 뒤 공개 URL과 sitemap을 검증한다.
