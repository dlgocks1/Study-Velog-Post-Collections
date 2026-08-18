## HTTP/1.0의 신택스 : 기본이 되는 네 가지 요소

### HTTTP 0.9 -> 1.0으로 진화

이전에는 HTTP/0.9를 활용 -> 이는 요청이 GET /경로 한 줄, 응답은 HTML 본문뿐이었음

- 헤더도, 상태 코드도, 메서드 선택지도 없었음 → 오류를 알릴 방법조차 없었음
- HTTP/1.0에서 ① 메서드와 경로 ② 헤더 ③ 바디 ④ 스테이터스 코드가 정립되었고, 
   - 이 네 요소는 HTTP/2·3까지 그대로 계승됨 (바뀐 건 전송 방식이지 의미론이 아님)
먼저 요청/응답 메시지가 실제로 어떻게 생겼는지 봅시다.

![](https://velog.velcdn.com/images/cksgodl/post/e0c3c871-ad76-4f84-a4d6-19bbcc608957/image.png)

### 스테이터스 코드

![](https://velog.velcdn.com/images/cksgodl/post/f4f45fd9-534a-4a29-ad8b-3f6fbcb5cd69/image.png)

### Content-Type과 보안

> **Content-Type의 정체**
바디의 형식을 선언하는 헤더. 전자메일 규격에서 파생 

문제의 본질: 이 값은 서버가 자기 마음대로 붙이는 자기 신고서일 뿐, 바디 내용과 일치한다는 보장이 전혀 없음

![](https://velog.velcdn.com/images/cksgodl/post/07ba3d75-5e8f-4dae-a031-5454c763988c/image.png)

#### MIME 스니핑 

> MIME : 파일의 종류를 구별하는 문자열 

- 초창기 웹은 서버 설정이 엉망이라 Content-Type이 틀린 경우가 흔했음
- 브라우저(특히 IE)는 사용자 편의를 위해 헤더를 무시하고 바디 앞부분을 훑어 타입을 추측하기 시작함. 
   - 이것이 MIME 스니핑임
   
시나리오: 공격자가 이미지 업로드 폼에 `<script>` 태그가 든 파일을 .png로 올림 → 서버는 image/png로 응답 → 브라우저가 스니핑해서 HTML이라 판단 → 스크립트 실행 = XSS

![](https://velog.velcdn.com/images/cksgodl/post/d7138dc2-fdb7-4df8-825c-511ec0f76c85/image.png)

`X-Content-Type-Options: nosniff` — 스니핑을 끄는 유일한 스위치. 사실상 모든 응답에 무조건 붙이는 게 정석이고, Spring Security, Chrome 등 인프라나, 브라우저, 프레임워크에서 기본적으로 nosniff 옵션 활용 

### 리다이렉트 

리다이렉트는 3xx 스테이터스 코드 + Location 헤더의 조합임. 

서버가 "여기 말고 저기로 가라"고 지시하면 클라이언트가 자동으로 재요청함
사용자 입장에선 한 번의 클릭이지만, 실제로는 왕복이 두 번 일어남

![](https://velog.velcdn.com/images/cksgodl/post/c9584e9d-febb-43d7-8af2-ea57802da660/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/49231921-9651-4811-87b6-f4b60b43802f/image.png)

- 304는 3xx지만 리다이렉트가 아님. If-None-Match / If-Modified-Since에 대한 캐시 응답이고 Location 헤더가 없음. 분류상 같이 묶여 있을 뿐임
  - 조건부 요청(conditional request)에 대한 응답
- 300, 305, 306은 사실상 사어임. 실무에서 볼 일 없음
- 실제로 쓰는 건 301, 302, 303, 307, 308 다섯 개뿐임

### 사실 URL의 "//"는 필요 없었다.

https://archive.nytimes.com/bits.blogs.nytimes.com/2009/10/12/the-webs-inventor-regrets-one-small-thing/

- WWW 창시자의 팀 버너스리 본인이 나중에 "//는 불필요했다" 고 인정. 
- 유래는 당시 쓰이던 Apollo Domain/OS의 네트워크 파일 경로 표기 관례를 그대로 활용했던 것
- http:example.com/path로 설계했어도 문법적으로 충분했음. 이미 전 세계에 퍼진 뒤라 되돌릴 수 없었을 뿐

사람들이 이걸 "백슬래시 백슬래시"라고 부르고 있다고 언급했으나 -> 실제로 /는 슬래시이고 백슬래시는 웹 주소에 거의 쓰이지 않음 

### 퓨니코드와 한글 URL

DNS는 ASCII만 허용함. -> 정확히는 영문자·숫자·하이픈(LDH 규칙)뿐
따라서 한글을 DNS에 그대로 실을 방법이 없음

그래서 기존 DNS는 손대지 않고, 한글을 ASCII 문자열로 인코딩해서 넣는 우회책이 나옴. 이게 IDN(국제화 도메인)이고, 그 인코딩 알고리즘이 퓨니코드(RFC 3492) 임

![](https://velog.velcdn.com/images/cksgodl/post/05ded30b-a867-4d74-b341-889c1f44e49c/image.png)

변환 결과 앞에 xn-- 라는 ACE 접두사가 붙음. 이게 "이건 퓨니코드다"라는 표시임

![](https://velog.velcdn.com/images/cksgodl/post/f2f97c13-d495-4d7b-a0be-b535e7f16561/image.png)

### Content-Length는 "압축 후" 크기다.

압축을 쓰면 Content-Length는 원본 리소스 크기가 아님.
스펙상 Content-Length는 전송되는 바디의 실제 바이트 수이고, 압축된 바이트가 곧 전송되는 바디이므로 그 크기를 측정한다.

즉 원본 크기는 HTTP 헤더 어디에도 없음. 받아서 풀어봐야 알 수 있음

![](https://velog.velcdn.com/images/cksgodl/post/b2a7c477-9a9d-4f03-96ca-e8e8eaebda0b/image.png)

### gzip의 실시간 스트리밍 압축

gzip의 경우 입력을 다 보지 않아도 앞부분부터 결과를 뱉을 수 있는 알고리즘이이다. 그래서 응답을 전부 완성할 때까지 기다릴 필요 없이, 만들면서 압축해서 만들면서 내보내는 게 가능함.

![](https://velog.velcdn.com/images/cksgodl/post/168002c7-ff12-4d29-88af-ba857a5aece1/image.png)


![](https://velog.velcdn.com/images/cksgodl/post/ea678046-1e0b-43e1-a6d0-9cc81af57d9c/image.png)

- Nginx가 gzip on으로 실시간 압축하면 응답을 흘려보내면서 압축하므로 최종 크기를 미리 알 수 없음
- 그래서 Content-Length를 빼고 Transfer-Encoding: chunked로 전환함
- HTTP/2 이후에는 chunked 자체가 없음. 프레임 단위 전송이라 길이 표기가 프로토콜 레벨로 내려갔음

#### Spring WebFlux에서는 스트리밍이 기본 전제임

`Flux<T>`를 반환하는 순간 응답은 조각 단위로 나가고, Content-Length는 붙지 않음.

```kotlin
@GetMapping("/export", produces = [MediaType.TEXT_EVENT_STREAM_VALUE])
fun export(): Flux<String> =
    repository.streamAll()          // 커서 기반, 메모리에 안 올림
        .map { it.toCsvLine() }
```

#### kafka의 gzip 압축 활용

https://developnote-blog.tistory.com/196

![](https://velog.velcdn.com/images/cksgodl/post/25df99ee-9ae8-411b-b73c-1a711aa8e18a/image.png)

- 카프카 프로두셔는 레코드 개별로 압축하지 않음. 각 파티션의 레코드를 배치형태로 압축함 
- 배치에 레코드가 많이 모일수록 압축률이 급격히 좋아짐. 비슷한 JSON 키가 반복되면 사전(dictionary)이 잘 잡히기 때문임

![](https://velog.velcdn.com/images/cksgodl/post/281d238e-2e16-4caf-b9c0-d711a9f33e00/image.png)

compression.type옵션을 지정하면 프로커와 프로듀셔(토픽), 브로커와 컨슈머(토픽)의 압축타입이 달라지고, 이 압축을 브로커단에서 수행함 -> 이에 대한 부하가 브로커에 존재

따라서 해당 설정 활용하지 않고, 프로듀셔 압축 타입으로 통일하는 것을 권장

- 참고) 압축률 
![](https://velog.velcdn.com/images/cksgodl/post/c1dd8214-58f0-46b4-87ba-f7953c48c510/image.png)




