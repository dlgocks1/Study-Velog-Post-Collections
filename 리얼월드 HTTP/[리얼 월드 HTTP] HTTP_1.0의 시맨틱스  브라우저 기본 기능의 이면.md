## 2.1 단순한 폼 전송(x-www-form-urlencoded)

데이터를 전송하는 것은 두 가지 방식 있음

HTML `<form>`의 method 속성이 GET이냐 POST냐에 따라 값이 실리는 위치가 달라짐

인코딩 규칙 자체는 둘 다 동일함. 위치만 다름
![](https://velog.velcdn.com/images/cksgodl/post/457025c8-c765-49e7-87ea-be7e2dcaa0cf/image.png)

인코딩을 통해 변환을하여 문자 전송

![](https://velog.velcdn.com/images/cksgodl/post/3f093dea-ff9a-4c70-bbca-47d1b0dc4ba2/image.png)

## 2.2 폼을 이용한 파일 전송

2.1의 `x-www-form-urlencoded`로는 파일을 못 보냄. 이 때 `"multipart/form-data"` 활용 가능

- 이름 그대로 바디를 여러 파트로 쪼개는 형식 
- 사진 전송에 쓰일 수 있음

핵심 제약 — 바디의 Content-Type은 하나뿐임
HTTP 메시지에서 Content-Type은 바디 전체에 하나만 붙음
그런데 파일 업로드 폼은 보통 이렇게 생겼음

```html
<form method="POST" enctype="multipart/form-data">
  <input name="title" type="text">      <!-- 텍스트 -->
  <input name="image" type="file">      <!-- 바이너리 PNG -->
</form>
```

#### 활용 이유

1. 여러 바디타입의 혼용

- 텍스트와 PNG는 타입이 다름. 하나의 Content-Type으로 묶을 방법이 없음
- 멀티파트는 이 문제를 "바디 안에 작은 메시지 여러 개를 넣는" 방식으로 푼 것. 각 파트가 자기 헤더를 가지므로 파트마다 다른 타입을 선언할 수 있음. 겉 봉투 안에 각각 라벨 붙은 봉투를 여러 개 넣는 구조.

2. 이스케이프 없이 바이너리를 실을 수 있음

- urlencoded는 구분자(&, =)와 데이터를 구분하려고 모든 특수문자를 퍼센트 인코딩함. 그래서 바이너리가 3배로 부풂
- 멀티파트는 구분을 바운더리 문자열에 맡김. 본문에 없는 랜덤 문자열을 쓰기 때문에 데이터를 건드릴 필요가 없음
- 즉 PNG 바이트를 원본 그대로 실을 수 있음. 이게 크기 면에서 결정적임
- 파일 하나만 보낼 거면 사실 멀티파트가 필요 없음

![](https://velog.velcdn.com/images/cksgodl/post/2f825f9f-6666-4f5f-b69f-7e312ad58868/image.png)

규칙)
- 바운더리는 요청 헤더에서 선언하고, 바디에서는 앞에 --를 붙여 씀
- 마지막 바운더리에는 뒤에도 -- 를 붙여 끝을 알림
- 바운더리는 본문에 절대 등장하지 않는 문자열이어야 함. 브라우저가 랜덤 생성함
- 맨끝에는 경계 문자열 +--

![](https://velog.velcdn.com/images/cksgodl/post/38e57dd7-5ebc-480d-9606-d6679442b93b/image.png)


## 2.3 폼을 이용한 리다이렉트

### 3xx 리다이렉트의 한계

1장에서 본 리다이렉트는 데이터를 실어 보낼 수 없음.

- Location 헤더는 URL 하나뿐임. 바디를 함께 보낼 자리가 없음
- 301/302/303은 메서드를 GET으로 바꿔버림. 원래 POST였어도 바디가 사라짐
- 307/308은 바디를 유지하지만, 원래 요청에 있던 바디를 그대로 재전송할 뿐임. 서버가 새 데이터를 끼워 넣을 수 없음
- 데이터를 URL 쿼리에 붙이면 로그·히스토리·리퍼러에 전부 남음. 결제 정보라면 치명적임

> 그래서 "다른 사이트로 POST하면서 이동" 이 필요한 경우, HTTP 리다이렉트로는 답이 없음.

#### 해결책 — 자동 제출 폼

서버가 리다이렉트 대신 200 OK로 HTML 한 장을 내려주고, 그 안에 자동으로 제출되는 폼을 심는 방식임.

![](https://velog.velcdn.com/images/cksgodl/post/eae9670f-7e78-4014-a8c6-d7571b5d62f3/image.png)


![](https://velog.velcdn.com/images/cksgodl/post/16f09acf-1bb9-4b3b-a3b9-908fdb4b565e/image.png)


## 2.4 콘텐츠 니고시에이션

하나의 URL, 여러 표현
- 같은 리소스라도 한국어판/영어판, HTML/JSON, 압축본/비압축본처럼 여러 형태가 있을 수 있음
- 이 각각을 표현(representation) 이라 부름
- 클라이언트가 선호를 밝히고 서버가 하나를 고르는 과정이 콘텐츠 니고시에이션임

![](https://velog.velcdn.com/images/cksgodl/post/e4df5fa9-1c73-4403-ae53-c3571143354e/image.png)

#### 실제로 동작할 때는 q값을 통해  우선순위 매김

선호도를 0~1 사이의 품질 계수(quality value) 로 표현함. 생략하면 1임
콤마로 여러 후보를 나열하고, 각각에 ;q=를 붙임
```
Accept-Language: ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,*;q=0.1
```

#### Accecpt-Language는 URL 분리로 대체

Accept-Language로 언어를 고르는 방식은 이론적으로 우아하지만 현실에서 밀려났음.

- SEO에 불리함 — 검색 엔진이 한국어판과 영어판을 같은 URL로 인식해 하나만 색인함
- 공유가 안 됨 — 한국어 페이지 링크를 보내도 상대방 브라우저 설정에 따라 영어로 열림
- 캐시 효율이 나쁨 — Vary로 키가 쪼개져 CDN 히트율이 떨어짐
- 사용자가 못 바꿈 — 브라우저 설정을 고쳐야 하는데 대부분 그럴 줄 모름

```
/ko/article/123      ← 언어별로 URL을 나눔
/en/article/123
<link rel="alternate" hreflang="ko" href="https://example.com/ko/article/123">
```

Accept-Language는 첫 방문 시 어느 URL로 보낼지 결정하는 힌트로만 쓰고, 302로 언어 URL로 보냄


## 2.5 쿠키 

> 상태 없는 HTTP 프로토콜에 상태를 붙이는 장치

- HTTP는 요청마다 독립적임. 서버는 직전 요청이 누구였는지 모름
- 로그인 상태를 유지하려면 어딘가에 표식이 필요한데, 서버가 전부 기억하기엔 확장성이 없음
- 그래서 표식을 클라이언트에 맡기고 매 요청마다 되돌려받는 방식을 씀. 이게 쿠키

#### 헤더 구조 — 비대칭이 특징

- 서버 → 클라이언트: Set-Cookie 헤더
- 클라이언트 → 서버: Cookie 헤더 한 줄에 세미콜론으로 이어붙임

← Set-Cookie: sid=abc123; Max-Age=3600; Path=/; Secure; HttpOnly
← Set-Cookie: theme=dark; Max-Age=31536000; Path=/

![](https://velog.velcdn.com/images/cksgodl/post/944cf03f-4209-4b50-87e9-aa3c93ffd61c/image.png)

### 믿을 수 없는 쿠키

서버는 쿠키 값을 신뢰할 수 없음

- 쿠키는 클라이언트가 보관하는 데이터임. 개발자 도구로 5초면 고칠 수 있음
- 서버가 심은 값이 그대로 돌아온다는 보장이 전혀 없음

특히 위험한 것 — 쿠키는 오리진을 구분하지 않음

- 포트를 무시함 — :8080에서 심은 쿠키가 :3000에도 감. 개발 환경에서 세션이 뒤섞이는 원인임
- 스킴을 무시함 — http://에서 심은 쿠키가 https://에도 감

![](https://velog.velcdn.com/images/cksgodl/post/75e6185b-4ec6-49df-b243-9dbc8fbad5df/image.png)

( Secure 속성은 쿠키를 평문으로 보내지 않게 할 뿐, 평문으로 심는 것을 막지 못함 )

### 서드파티 쿠키 폐지와 그 이후

쿠키가 도메인 단위로 동작한다는 성질이 광고 추적에 쓰이면서, 브라우저들이 이를 막는 방향으로 움직였음.

Safari(ITP), Firefox(ETP)는 이미 서드파티 쿠키를 기본 차단함
퍼스트파티 쿠키도 스크립트로 심으면 만료가 7일로 단축되는 정책이 있음 (Safari)


## 2.6 인증과 세션

HTTP가 원래 제공하던 인증
- HTTP는 프로토콜 차원의 인증 기능을 처음부터 갖고 있었음. 로그인 화면을 직접 만들 필요가 없는 구조였음
- 핵심은 401 챌린지-리스폰스임. 서버가 "인증하고 다시 와라"고 되돌려 보내면 클라이언트가 자격증명을 붙여 재요청함

### BASIC 인증

아이디:비밀번호를 base64로 인코딩해 Authorization 헤더에 넣음
base64는 암호화가 아니라 인코딩임. 디코딩에 키가 필요 없음. 평문과 사실상 동일함

```python
import base64
base64.b64decode("dXNlcjpwdw==")   # b'user:pw'  ← 한 줄이면 끝
```

그래서 HTTPS가 아니면 절대 쓰면 안 됨

#### Authorization 헤더 자체는 지금도 현역

```
Authorization: Basic dXNlcjpwdw==
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

OAuth 2.0의 Bearer도 같은 헤더, 같은 401 챌린지 구조를 그대로 씀


### Digest 인증

BASIC의 "비밀번호가 그대로 흐른다"는 문제를 해결하려고 나왔음.

서버가 일회성 난수(realm)를 챌린지에 담아 보냄
클라이언트는 아이디 : realm : 비밀번호와 논스 등을 조합해 해시를 계산해서 응답함
비밀번호 자체는 네트워크에 흐르지 않음. 재전송 공격도 논스로 막음

그런데 널리 쓰이지 못했음.

- 서버가 비밀번호를 평문에 준하는 형태로 보관해야 함. 해시 검증을 하려면 원본이 필요하기 때문임. 서버가 털리면 끝임
- MD5 기반이라 현대 기준으로 취약함
- 중간자가 Basic으로 다운그레이드시키는 공격이 가능함

### 쿠키 세션

![](https://velog.velcdn.com/images/cksgodl/post/be4963cf-b132-4ddd-92c7-35758a37899f/image.png)

>세션 저장소 선택이 곧 아키텍처 결정임

세션 방식을 택하면 "상태를 어디에 둘 것인가"가 따라옴. 선택지마다 트레이드오프가 뚜렷함.

![](https://velog.velcdn.com/images/cksgodl/post/dd82aa6f-6837-46e0-9fd4-88dc3da813b9/image.png)

- 현실적인 절충은 짧은 액세스 토큰 + 서버 관리 리프레시 토큰임. 액세스 토큰은 5~15분으로 짧게 두고, 회수는 리프레시 토큰 단계에서 함


## 2.7 프록시

HTTP 통신을 중계하는 서버 
클라이언트의 요청을 대신 받아 목적지로 전달하고, 응답을 되돌려줌

HTTP는 처음부터 프록시를 전제로 설계됐음. 요청 라인에 절대 URL을 쓸 수 있는 게 그 흔적임

```
일반 요청:    GET /path HTTP/1.1
              Host: example.com

프록시 요청:  GET http://example.com/path HTTP/1.1    ← 절대 URL
```

프록시는 어느 서버로 보낼지 알아야 하므로 경로만으로는 부족함. 그래서 전체 URL을 씀

### 포워드 프록시와 리버스 프록시

![](https://velog.velcdn.com/images/cksgodl/post/9b7bc0b0-c35b-4d47-b89f-6f997d372bf2/image.png)

### 프록시의 헤더

![](https://velog.velcdn.com/images/cksgodl/post/6f424d71-ab22-4b05-847b-575027df0bd8/image.png)

#### HTTPS는 프록시가 못 들여다봄

포워드 프록시의 근본 한계
HTTPS는 내용이 암호화돼 있어 중계할 수가 없음.

![](https://velog.velcdn.com/images/cksgodl/post/780e0f5a-b5b6-442f-836f-21d4fbf75e13/image.png)

- CONNECT는 HTTP 요청이 아니라 TCP 터널 개통 요청임. 프록시는 이후 양방향 바이트를 그냥 옮기기만 함
- 프록시가 알 수 있는 건 목적지 호스트명과 포트뿐임. 경로도 헤더도 못 봄
- 그래서 사내 프록시에서 HTTPS 트래픽을 검사하려면 자체 인증서를 설치해 중간자 역할을 하는(TLS 인터셉션) 방법밖에 없음

## 2.8 캐시 

캐시가 해결하는 것
- 대역폭 — 같은 리소스를 다시 받지 않음
- 지연 — 가까운 곳에서 즉시 응답함
- 서버 부하 — 원본 서버까지 요청이 도달하지 않음

세 가지가 한꺼번에 개선되므로, 웹 성능 최적화에서 가장 효과가 큰 수단임.

#### 캐시는 두 층으로 나뉨

![](https://velog.velcdn.com/images/cksgodl/post/4b53ef00-5fd5-4e39-a807-034e885b1a07/image.png)

#### HTTP/1.0과 HTTP/1.1 차이

![](https://velog.velcdn.com/images/cksgodl/post/75bf30a4-6e44-404a-8e55-93195b7f95cc/image.png)


### 캐시 컨트롤

![](https://velog.velcdn.com/images/cksgodl/post/12319c50-1179-4832-a27b-4edc8d574d16/image.png)


#### 브라우저의 새로고침과 캐시 초기화

같은 페이지를 다시 열어도 어떻게 다시 여느냐에 따라 브라우저가 보내는 헤더가 달라짐.

![](https://velog.velcdn.com/images/cksgodl/post/3a5ae62e-0c9c-4b68-a6f3-91b05ba4ddf4/image.png)


## 2.9 리퍼러

어느 페이지에서 이 요청이 시작됐는지를 알려주는 요청 헤더

- 스펙 제정 당시 Referrer의 철자를 Referer로 잘못 적었고, 그대로 표준이 됐음. 지금도 헤더 이름은 r이 하나임

언제 전송되나
- 링크 클릭으로 다른 페이지에 갈 때
- 이미지·CSS·JS 같은 서브리소스를 불러올 때
- 폼을 전송할 때
- 리다이렉트로 이동할 때


### Referrer-Policy

전송 범위를 제어하는 헤더

![](https://velog.velcdn.com/images/cksgodl/post/3d3f401b-36aa-4050-94ff-421f8e0cd7a1/image.png)

## 2.10 검색 엔진용 콘텐츠 접근 제어

세 가지 수단

크롤러를 제어하는 방법은 적용 범위와 시점이 각각 다름.

![](https://velog.velcdn.com/images/cksgodl/post/f167699d-1851-4b78-b81e-925f84fad40c/image.png)


### 사이트 맵 (sitemap.xml)

- "우리 사이트에 이런 페이지들이 있다" 고 크롤러에게 건네는 목록 파일임
- robots.txt가 "여기는 가지 마라"라면, 사이트맵은 "여기 있으니 와서 봐라" 임. 방향이 정반대임

크롤러는 기본적으로 링크를 타고 다님. 그래서 링크로 도달할 수 없는 페이지는 존재 자체를 모름.
![](https://velog.velcdn.com/images/cksgodl/post/107fb0b9-6546-481c-a407-8e438b5c5bb2/image.png)

