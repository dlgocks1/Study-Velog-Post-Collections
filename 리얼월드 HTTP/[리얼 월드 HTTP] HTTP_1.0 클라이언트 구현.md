> HTTP/1.0 클라이언트는 결국 "TCP 소켓 열고 → 텍스트 몇 줄 던지고 → 돌아온 바이트를 헤더/바디로 쪼개기" 가 전부

![](https://velog.velcdn.com/images/cksgodl/post/e2d674a0-c424-4919-8e8a-9627d33e5cc0/image.png)


## 3.5 GET 메서드+쿼리 전송

![](https://velog.velcdn.com/images/cksgodl/post/262c92f7-be6d-493b-a3d0-25da7e755106/image.png)


## 3.6 HEAD 메서드로  헤더 가져오기

HEAD는 GET과 완전히 똑같은 요청인데 바디만 안 받는 것. 

서버는 GET이었다면 보냈을 헤더를 그대로 돌려주고, 바디는 한 바이트도 안 보냄.

![](https://velog.velcdn.com/images/cksgodl/post/d3fdaf63-97f0-4361-8941-32719bead0d7/image.png)

### 바디 유무 판정

HTTP 응답에서 "바디가 어디서 시작해서 어디서 끝나는가"를 정하는 걸 프레이밍이라 함.

핵심은 순서임.

![](https://velog.velcdn.com/images/cksgodl/post/240a149f-e2c5-4a50-b26d-c30ab8b2e4a1/image.png)


## 3.7 x-www-form-urlencoded 형식 POST 메서드 전송

GET 쿼리와 POST 폼은 바이트 포맷이 완전히 똑같음. key=value&key=value에 퍼센트 인코딩. 다른 건 그 문자열이 요청라인에 붙느냐, 바디로 가느냐 뿐임.

![](https://velog.velcdn.com/images/cksgodl/post/603ada88-6e3c-4e7a-a0d4-19d65007f570/image.png)

### 폼 인코딩 3종

![](https://velog.velcdn.com/images/cksgodl/post/efdcd390-2346-427d-b66c-57f08b637056/image.png)

## 3.8 POST 메서드로 임의 바디 전송 

3.7이 "폼 형식이라는 약속된 포맷"이었다면, 3.8은 바디에 아무 바이트나 넣는 것임. JSON, 평문, 이미지, 바이너리 전부 가능함.

클라이언트가 할 일은 두 가지뿐임. "이게 무슨 형식인지(Content-Type)" 와 "몇 바이트인지(Content-Length)" 를 정확히 알려주는 것.

![](https://velog.velcdn.com/images/cksgodl/post/50aabf10-6323-43f7-b7ae-f2be40d3f881/image.png)

### Content-Type을 고르는 기준

- application/json — API 호출. 가장 흔함
- text/plain; charset=UTF-8 — 로그, 평문. 한글이 있으면 charset 필수
- image/png, application/pdf — 정해진 타입이 있으면 그걸 씀

### Content-Type을 서버가 그대로 믿지 않음

브라우저와 일부 서버는 바디 앞부분을 보고 타입을 추측함`(MIME sniffing)`. text/plain으로 올린 파일이 `<script>`로 시작하면 HTML로 해석돼 실행될 수 있음

그래서 업로드 결과를 다시 서빙하는 엔드포인트는 `X-Content-Type-Options: nosniff`를 반드시 붙여야 함

## 3.9 multipart/form-data 형식으로 파일 전송

urlencoded는 바이너리를 못 담음. %EC%95%88 처럼 바이트당 최대 3배로 팽창하고, 텍스트 필드와 파일을 섞어 보낼 구조도 없음.

multipart는 하나의 바디 안에 여러 파트를 넣고, 구분선(boundary)으로 나누는 방식임. 각 파트는 자기만의 헤더를 가짐. 사실상 작은 HTTP 메시지를 여러 개 이어붙인 모양임.

![](https://velog.velcdn.com/images/cksgodl/post/f7ffb680-b80f-4d42-8514-1515ad27fecb/image.png)

## 3.10 쿠키 송수신

HTTP는 상태가 없음. 쿠키는 서버가 클라이언트에게 메모지를 맡기고, 다음 요청 때 돌려받는 방식으로 상태를 흉내 냄.

![](https://velog.velcdn.com/images/cksgodl/post/3504ebd5-d5ed-411e-a208-65032e82a6d6/image.png)


### 쿠키는 매 요청마다 전부 실려 나감

- 브라우저 제한이 대략 도메인당 4KB, 개수 50개 내외임. 이걸 넘으면 오래된 것부터 버려짐
- 중요한 건 대역폭임. 1KB 쿠키를 심어두면 정적 리소스 100개를 받을 때 100KB가 요청 헤더로만 나감
- 그래서 정적 자원은 쿠키가 안 붙는 별도 도메인으로 서빙하는 패턴이 오래된 최적화임
- 실제 데이터는 서버에 두고 쿠키에는 세션 ID만 담는 것이 기본 설계임. 쿠키 자체는 클라이언트가 얼마든지 조작할 수 있으므로 신뢰해서도 안 됨

## 3.11 프록시 이용

프록시를 쓰면 TCP 연결 상대가 목적지 서버가 아니라 프록시가 됨. 그래서 프록시는 "어디로 보내야 하는지"를 따로 알아야 함.

![](https://velog.velcdn.com/images/cksgodl/post/03c24ac3-44f7-46e8-a1d5-092f26e8e999/image.png)

### 요청라인이ㅡ 네 가지 형태

![](https://velog.velcdn.com/images/cksgodl/post/c42cc043-2ad8-43fe-9dc8-c2ac5063866f/image.png)

## 3.12 파일 시스템 엑세스 

file:// 은 HTTP가 아님. 네트워크 패킷이 한 바이트도 오가지 않음.

그런데도 HTTP 클라이언트로 다룰 수 있음. URL이 "프로토콜 + 위치"를 함께 표현하는 구조라서, 클라이언트 라이브러리가 스킴을 보고 처리 방식을 갈아끼우는 형태로 만들어져 있기 때문임.

![](https://velog.velcdn.com/images/cksgodl/post/2bab9eed-0e09-4044-8988-6b8141caf42a/image.png)

### file:// URL 문법


```
file://<호스트>/<절대경로>
file:///etc/hosts          ← 호스트 생략 (슬래시 3개)
file://localhost/etc/hosts ← 위와 동일한 의미
file:///C:/Users/lee/a.txt ← Windows, 드라이브 문자도 경로의 일부
```


## 3.13 자유로운 메서드 전송

get(), post(), head() 같은 편의 함수는 메서드가 하드코딩된 래퍼일 뿐임. PUT, DELETE, PATCH와 같은 별도 메서드를 쓰려면 메서드를 인자로 받는 범용 API를 써야 함.

![](https://velog.velcdn.com/images/cksgodl/post/868b0486-232e-46a4-928b-1588f4b22f22/image.png)

### 표준 메서드와 속성


![](https://velog.velcdn.com/images/cksgodl/post/4b41f7df-5626-4667-b027-938df1ec1e90/image.png)

- 안전(safe) = 서버 상태를 바꾸지 않음. 크롤러와 프리페치가 마음대로 호출해도 됨
- 멱등(idempotent) = 몇 번 보내도 결과가 같음. 네트워크 재시도를 해도 안전함
- PATCH가 비멱등인 게 헷갈리는 지점임. {"count": 5}처럼 절대값이면 멱등이지만, JSON Patch의 {"op": "add"}처럼 상대 연산이면 반복할 때마다 결과가 달라짐. 규격은 최악의 경우를 기준으로 비멱등으로 규정함

## 3.14 헤더 전송

헤더는 이름: 값 한 줄이 전부임. 문법이 단순해서 오히려 지켜야 할 제약을 놓치기 쉬움.

특히 값에 뭘 넣을 수 있는지, 같은 헤더를 여러 번 보내면 어떻게 되는지가 실무에서 계속 문제가 됨.

![](https://velog.velcdn.com/images/cksgodl/post/d53de057-fa1b-4b3a-84e3-3d508dc4ec4d/image.png)


### X- 접두사는 2012년에 폐지 권고됐음

- 원래 "비표준 확장은 X-로 시작"이라는 관례가 있었음. RFC 6648이 이걸 하지 말라고 뒤집음
- 권고는 처음부터 접두사 없이 고유한 이름을 쓰는 것임. 실무에서는 회사·서비스 이름을 접두사로 붙이는 방식이 많음
- 다만 이미 X-로 굳어진 것들(X-Request-Id, X-Forwarded-For)은 바꿀 수 없어서 현실에서는 계속 섞여 있음

### 헤더 전체 크기에 상한이 있음

- 서버 기본값이 대체로 8KB 내외임. nginx large_client_header_buffers 4 8k, 톰캣 maxHttpHeaderSize 8192
- 초과하면 431 Request Header Fields Too Large, 또는 구현에 따라 400이나 연결 끊김
- 실제로 이걸 터뜨리는 주범은 쿠키임. 세션 데이터를 쿠키에 넣다가 4KB를 넘기면 한계에 붙음

## 3.15 국제화 도메인

도메인 이름은 원래 영문자·숫자·하이픈(LDH) 만 쓸 수 있음. DNS 프로토콜과 전 세계 리졸버가 그 전제 위에 만들어져 있어서 지금도 바꿀 수 없음.

그래서 한국.kr 같은 도메인은 Punycode로 ASCII로 변환해서 전송함.

![](https://velog.velcdn.com/images/cksgodl/post/b1e486da-0065-40fe-b44e-5b7d548c6adb/image.png)

