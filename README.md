# 면접 관련 질문들

---

## 코틀린 관련 질문

- 지역함수(`Scope Function`)에 대해

- `by lazy`와 `lateinit`의 차이점

- 동일성과 동등성 비교

동등성은 `==`연산으로 두 객체의 값이 완전히 동일한 것인지 비교한다. 내부적으로 `equals`를 호출한다.
동일성은 `===`연산으로 같은 주소 값을 참조하는지 비교한다.
`Data Class`에서는 `equals`를 자동으로 오버라이드 하며, 내부 속성들이 동일한지 체크한다.

- `Data Class`에서의 `copy()`를 사용하는 이유와 데이터클래스를 불변으로 만드는 것을 권장하는 이유

복사본과 원본의 생명주기의 차이가 있을 수도 있다.
데이터 클래스의 속성값을 키값으로 하는 컨테이너에 키 값 프로퍼티를 변경하면 오류가 발생할 수도 있다.
다중 쓰레드 또는 쓰레드가 사용 중인 데이터를 다른 쓰레드가 변경할 수 없으므로 쓰레드 동기화가 불필요하다.

- `중첩 클래스`와 `내부 클래스`의 차이

둘다 외부 클래스와 동일한 접근 수준을 가진다.(외부가 `private`이면 `private`, `public`이면 `public`)

`중첩 클래스`는 외부 인스턴스에 접근할 수 없으며 외부 클래스 인스턴스에 종속적이지 않다.
`내부 클래스(inner)`는 외부 인스턴스에 접근할 수 있으며, 변수나, 함수를 자유롭게 사용 가능하다. 하지만 외부 클래스 인스턴스가 생성되어야만 한다.

- `Companion object`에 대하여

클래스가 메모리에 적재되면서 함께 생성되는 객체(자바의 `static`처럼 사용 가능하며 싱글톤으로 선언된다.)
자바의 `static`과는 다르게 변수에 직접 할당이 가능하고, 변수를 통해 멤버를 참조할 수 있다.

---

## 안드로이드 관련 질문

- 안드로이드 OS에 대하여

[Andorid Quick Overview](https://velog.io/@jeongminji4490/Android-Quick-Overview)

안드로이드는 리눅스 커널을 기반으로 한다. 리눅스 커널 위에 구글이 개발한 다양한 시스템 라이브러리 및 프레임워크를 추가하여 구성된다.
리눅스 커널은 하드웨어와 상호작용하며 프로그램과 데이터를 관리하는 오픈소스 운영체제 보안성과 안정성이 높음

- Thread간 통신 방법에 대하여

`Hanlder`와 `Looper`를 이용한다.
두 개 이상의 스레드를 활용할 때의 동기화 이슈를 차단하기 위해 `Looper`와 `Handler`를 사용한다.
`Handler`란? `Looper`로 부터 받은 `Message`를 실행, 처리하거나 다른 스레드로부터 메시지를 받아서 `Message Queue`에 넣는 역할을 하는 스레드 간의 통신 장치이다.
`Looper`란? 무한 루프를 실행하면서 `Message Queue`에서 `Message`를 가져와 핸들러에게 전달한다.
`Message`는 문자와 필드로 구성된 메시지 객체 또는 `Runnable`객체로 이루어진다.

한 쓰레드에서는 하나의 `Looper`와 하나의 `Message Queue`만 생성될 수 있다.
메인 쓰레드(UI 쓰레드)는 루퍼가 기본적으로 생성되 있다. 새로 생성한 쓰레드는 `Looper`를 가지고 있지 않다. 따라 메시지를 받기 위해서는 `Looper`를 생성해 주어야 한다.

> 다른 쓰레드에서의 `Handler`를 통해 현재 쓰레드의 `Looper`(`Message Queue`)에게 메시지를 보내어 쓰레드간의 통신을 할 수 있다.

- 백그라운드 쓰레드에서 `UI`를 업데이트하는 법

또는 `AsyncTask`를 이용한다.
이는 백그라운드에서 작업을 수행하고, 작업이 완료되면 결과를 `UI`쓰레드에서 처리할 수 있도록 한다.
백그라운드 작업이 길어지나, 실행 중 화면이 회전하는 경우 `ANR`이 발생하여 `Deprecated`됨

대신 `Coroutine`의 `Dispatchers.Main`을 활용하여 `UI`를 업데이트 할 수 있다.

```
// UI 업데이트를 하는 함수
suspend fun updateUI(text: String) = withContext(Dispatchers.Main) {
    textView.text = text
}

// 코루틴에서 비동기 작업을 처리하고, UI 업데이트를 호출하는 함수
suspend fun doSomeWork() {
    // 비동기 작업 처리 withContext를 사용하거나 Aysnc, Await 또는 Launch, Join 을 사용해도 된다.
    val result = withContext(Dispatchers.IO) {
        // 작업 처리
    }

    // UI 업데이트
    updateUI(result)
}
```

- Context에 대하여

현재 사용되고 있는 어플리케이션(또는 액티비티)에 대한 포괄적인 정보를 지니고 있는 객체이며 4대 컴포넌트를 생성할 때 사용된다.
`Compose`에서는 `LocalContext.current`를 활용해 콘텍스트를 얻을 수 있으며 `Theme`, `Resource`등에 접근이 가능하다.

- 4대 컴포넌트에 대해
  Activity
  Service
  Broadcast Receiver
  Content Provider

- `Content Provider`와 `Content Resolver`의 차이

단어 그대로 `Provider`은 정보를 제공하는 쪽이다.
데이터 베이스, 파일 시스템, 네트워크와 같은 데이터를 공유하기 위한 컴포넌트
`Resolver`는 `Provider`가 제공한 데이터를 읽고 쓰는 작업을 수행 한다. (쿼리를 수행해서 데이터를 가져온다.)

- [`Content URI`와 `File URI`의 차이점은 무엇인지](https://velog.io/@cksgodl/Android-Content-URI%EC%99%80-File-URI%EC%9D%98-%EC%B0%A8%EC%9D%B4%EC%A0%90-File-Provider%EC%99%80-Content-URI%EB%A5%BC-%ED%99%9C%EC%9A%A9%ED%95%98%EC%97%AC-%EC%B9%B4%EB%A9%94%EB%9D%BC-%EC%9D%B4%EB%AF%B8%EC%A7%80-%EA%B0%80%EC%A0%B8%EC%98%A4%EA%B8%B0)

`File URI` : 파일 시스템에 직접 참조하기 위한 `URI`이다.
`Content URI` : `Content Provider`를 통해 데이터를 가져오기 위한 `URI`이다.
`File URI`는 안드로이드 `7.0`버전 이후 부터 보안상의 이유로 금지 되었다. 따라 `Content URI`를 통해 임시 엑세스 권한을 부여하고 파일을 공유해야 한다.

- Activity의 생명주기에 대하여

- Fragment의 생명주기에 대하여

- ANR이 무엇인지?

`Main Thread`가 일정 시간 응답을 하지 않는 경우 발생하는 오류이다.
화면이 5초이상 반응하지 않을 때
`BroadcastReceiver`나 `Service`가 10초이상 처리를 수행할 때

따라 코루틴, 쓰레드를 활용해 작업을 처리하던가, 프로그레스 바를 이용해 진행과정을 알려 기다리게 한다.

- Manifest가 무엇인지?

코드를 실행하기전에 `Android` 시스템이 알아야하는 어플리케이션 정보를 포함하는 곳
퍼미션, 프로파이더, 앱이름, 가로 세로 디렉션 등등...

- `Okhttp`와 `Retrofit`에 대하여

둘다 모두 네트워크 통신을 위한 라이브러리이며 `Retrofit`이 좀더 상위 단계의 추상화를 가진 라이브러리이다.
`OkHttp`는 캐싱 요청 및 응답 인터셉트, 자동 리다이렉션, 풀링 등 다양한 기능을 제공한다.
`Retrofit2`에서는 `API` 인터페이스를 생성해 간단하게 `HTTP`요청을 보낼 수 있고, `Json` 응답값을 자동으로 데이터클래스로 바꿔주는 기능도 제공한다.

- `intent`에 대하여

- `Toast`와 `Snackbar`의 차이

스낵바는 되돌리기와 같은 유저 입력을 받을 수 있다.

- 서비스와 스레드의 차이점

- `bundle`이란?

- `Jetpack`이란?

- 안드로이드 앱의 빌드 과정

- JAR, AAR, DEX, APK에 대하여

- `String`과 `StringBuffer`의 차이

`String`은 불변이며 문자를 수정하려면 지우고 다시 생성한다.
`StringBuffer`은 가변이며 필요할 때 크기를 변경하여 문자를 수정한다. 그러나 멀티쓰레드 환경에서는 동기화 문제 발생가능

- 어떤 정보를 `Application` 클래스에서 관리하는 것과 싱클톤으로 관리하는 것의 차이점

`Application`은 라이프사이클을 알고 있고, 힙 영역 내에서 선언된다.
`싱글톤`은 스태틱 메모리에서 관리된다.

- 뷰모델에서 `get()`을 활용해 `Livedata`를 얻는데 이유가 뭔지?

`LiveData`는 `Only Read`다. `MutableLiveData`는 외부에서 접근이 불가능해야 한다.
객체지향 프로그래밍의 `캡슐화`를 의미한다.
실제 구현 내용 일부를 외부에 감추어 은닉하는 것 (사용자는 알약의 쓴 내용을 알 필요가 없다.)

- `MutableLivedata`를 참조할 때 `get()=`과 `=`의 차이점

`get()=`은 해당 변수를 참조할 때 자동으로 `MutableLivedata`를 참조할 수 있게 가져오는데 `=`으로 가져오면 불필요한 `LiveData`변수가 하나 더 생성된다.

- 왜 `Database`를 활용할 때 `SQLite`대신 `RoomDB`를 사용헀나요?

구글에서도 `SQLite`에서 `Room`으로의 이전을 권장하고 있기에 사용했다.
반복적이고 오류가 발생하기 보일러플레이트 코드를 최소화 가능
쿼리에 대한 에러를 컴파일시 확인 가능
`Flow`로 데이터를 내보내는 것이 가능

---

## CS 관련 질문

- 싱글톤이란 무엇인지?
- MVP, MVC, MVVM에 대하여
- DI란 무엇인가?
- 객체지향 프로그래밍에 대하여
- Process와 Thread에 대하여
- JVM에 대하여
- REST, RESTFful하다에 대하여
- OSI 7계층
- 런타임과 컴파일타임의 차이

`컴파일타임` : 개발자가 작성한 언어를 컴퓨터가 인식할 수 있게 기계어 코드로 변환하는 것
`런타임` : 컴파일 과정을 마쳐서 사용자에 의해 실행되는 것

- `HashTable`과 해싱에 대해
- `Semaphore`와 `Muutext`에 대해
- 블로킹과 논블로킹의 차이점에 대해, 동기와 비동기의 차이점에 대하여
- 교착 상태(데드락)에 대해, 또한 데드락의 조건에 대해
- `DI`와 `Service Locator`의 차이점에 대하여

- `TDD`에 대하여

---

## 프로젝트 관련 질문

프로젝트를 진행하며 해당 라이브러리를 사용한 **이유**
대체할 기술이 있는지

---

## 이외 질문

- 자기소개
- 지원동기
- 개발을하면서 행복한 점, 힘든 점
- 최근 관심있는 기술
- 어떤방식으로 공부를 진행하는 지
- 회사의 발전과 개인의 발전 중 더 중요한 것
- 개발자로써의 나의 목표
- 회사 주력 서비스의 좋은 점, 아쉬운 점, 오류
- 알고 있는 알고리즘 하나 설명해주세요.
- 서버와 협업에서 문제점과 해결한 경험
- 디자이너와 협업에서 문제점과 해결한 경험

- 마지막으로 궁금한 점, 질문하고 싶은 점
  - 배포 주기 및 방식
  - 개발자 중 안드로이드 개발자의 수
  - 주니어 시니어 비율
  - 사내에 정착되어 있는 개발문화

## 참고자료

[Android Interview](https://imwj.notion.site/imwj/Android-Interview-3ce7ddf12ddb413a9d2213173654d52c)

[신입 안드로이드 면접 준비](https://github.com/taeiim/Android-Study/blob/master/study/week16/%EC%95%88%EB%93%9C%EB%A1%9C%EC%9D%B4%EB%93%9C%20%EA%B0%9C%EB%B0%9C%EC%9E%90%EB%A1%9C%20%EC%B7%A8%EC%97%85%ED%95%98%EA%B8%B0%20-%20%EB%A9%B4%EC%A0%91/%EC%8B%A0%EC%9E%85%20%EC%95%88%EB%93%9C%EB%A1%9C%EC%9D%B4%EB%93%9C%20%EA%B0%9C%EB%B0%9C%EC%9E%90%EB%A1%9C%20%EC%B7%A8%EC%97%85%ED%95%98%EA%B8%B0%20-%20%EB%A9%B4%EC%A0%91.md)
