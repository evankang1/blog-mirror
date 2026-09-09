
# kevin-story2009 블로그 미러

네이버 블로그 글을 GitHub Pages 정적 사이트로 미러링해 검색 노출을 보완하는 프로젝트입니다.

이 저장소는 네이버 RSS를 읽어서 포스트 HTML, 목록 페이지, sitemap, robots 파일을 생성하고, GitHub Actions로 자동 동기화 및 배포를 수행합니다. 최종적으로 공개 페이지는 정적 HTML 기반으로 유지되며, 생성 직후 병합 마커와 스크립트 주입 흔적을 제거해 깨끗한 결과물을 만듭니다.

## 현재 자동화 흐름

1. `Sync Naver Blog Mirror` 워크플로가 `main` 브랜치의 `push`, 수동 실행, 또는 매일 UTC 00:10 (KST 09:10) 에 실행됩니다.
2. `scripts/sync.py`가 네이버 RSS를 가져와 최신 포스트를 파싱하고, 중복 링크와 비정상 항목을 필터링합니다.
3. `posts/{글번호}.html`, `index.html`, `sitemap.xml`, `robots.txt`를 새로 생성합니다.
4. 생성 직후 HTML/XML 전용 sanitize 로직이 실행되어 Git merge marker, `<script>` 태그, 의도치 않은 스크립트 블록을 제거합니다.
5. 생성 결과를 검증하고, 변경 사항이 있으면 자동 커밋 후 같은 브랜치에 push합니다.
6. `Deploy Blog Mirror to GitHub Pages` 워크플로가 실행되어 정적 사이트를 GitHub Pages에 배포합니다.

### 현재 기준
- 동기화 워크플로: `.github/workflows/sync.yml` (`Sync Naver Blog Mirror`)
- 배포 워크플로: `.github/workflows/pages.yml` (`Deploy Blog Mirror to GitHub Pages`)
- 트리거: `main` 브랜치 push, `workflow_dispatch`, 매일 UTC 00:10
- 유효성 검사: `index.html`과 `sitemap.xml`에서 병합 마커와 `<script>` 태그가 없는지 확인
- 정리 규칙: 중복 URL 제거, 최신순 정렬, 상위 100개 항목 유지

## 초기 설정

### 1. 저장소 준비
1. GitHub에서 `blog-mirror` 저장소를 생성합니다.
2. 이 폴더의 파일을 그대로 업로드합니다.
   - `scripts/sync.py`
   - `.github/workflows/sync.yml`
   - `.github/workflows/pages.yml`
   - `robots.txt` 및 기타 정적 파일

### 2. GitHub Pages 활성화
- 저장소 Settings → Pages → Source: **Deploy from a branch**
- Branch: **main** / **/(root)**
- Save

### 3. GitHub Actions 권한 설정
- Settings → Actions → General → Workflow permissions
- **Read and write permissions** 활성화
- Save

### 4. 첫 동기화 실행
- Actions 탭에서 `Sync Naver Blog Mirror`를 선택해 **Run workflow** 실행
- 잠시 후 공개 페이지가 생성됩니다.

### 5. Google Search Console 제출
1. https://search.google.com/search-console 에 접속
2. 속성 추가 → URL 접두어 방식으로 `https://당신의아이디.github.io/blog-mirror/` 등록
3. Sitemaps 탭에서 `sitemap.xml` 제출

구글 색인 반영은 보통 며칠 걸릴 수 있습니다.

## 로컬 실행

```bash
python3 scripts/sync.py
```

이 명령으로 포스트 HTML, 인덱스, sitemap, robots 파일을 다시 생성할 수 있습니다. 생성 후에는 브라우저에서 `index.html` 또는 공개 URL을 열어 목록과 sitemap 구조를 확인하면 됩니다.

## 운영 체크리스트

배포 전 또는 수동 점검 시 아래 항목을 확인하면 안전합니다.

- [ ] 로컬에서 `python3 scripts/sync.py` 실행이 정상 종료
- [ ] `index.html` 상단에 merge marker가 없는지 확인
- [ ] `sitemap.xml`에서 `<script>` 태그와 `<<<<<<<` / `>>>>>>>` 문자열이 없는지 확인
- [ ] `posts/` 디렉터리에 최신 글 번호의 HTML이 생성되었는지 확인
- [ ] `main` 브랜치 기준으로 최신 상태인지 확인
- [ ] GitHub Actions에서 `Sync Naver Blog Mirror`가 성공했는지 확인
- [ ] Pages 배포 워크플로 `Deploy Blog Mirror to GitHub Pages`가 정상 완료되었는지 확인
- [ ] 공개 주소에 접속해 페이지가 정상 노출되는지 확인
- [ ] Search Console에서 sitemap 재전송이 필요한 경우 수행

## 문제 해결

- RSS 글이 안 보임: 네이버 블로그 설정에서 RSS 공개가 활성화되어 있는지 확인
- sitemap이 이상함: `.github/workflows/sync.yml` 검증 단계와 `scripts/sync.py`의 sanitize 로직 재확인
- HTML 상단에 이상한 텍스트가 보임: merge marker 혹은 `<script>` 태그가 남아 있지 않은지 검사
- Google에서 안 잡힘: Search Console의 URL 검사와 sitemap 재제출 수행

> 현재 운영 기준: 정적 파일 생성 → sanitize → validation → 자동 커밋/푸시 → Pages 배포 순서로 진행합니다.
