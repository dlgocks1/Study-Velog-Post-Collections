서비스를 런칭한 후 앱을 활용하는 사용자의 데이터, 동작이 필요할 수도 있다.
이에따라 `Firebase`에서는 `Analytics`라는 기능을 제공한다.

## Analytics

> `Firebase Analytics`는 앱 및 웹 애플리케이션의 사용자 동작 및 이벤트에 대한 데이터를 수집하고 분석하여 앱 또는 웹의 성능을 파악하고 개선할 수 있도록 도와주는 Google의 분석 도구이다.

`Firebase Analytics`를 사용하면 앱 또는 웹 사용자의 행동에 대한 세부 정보를 추적하고 이를 분석하여 다양한 이벤트를 생성할 수 있다.

예를 들어, 사용자의 이탈률, 활성 사용자 수, 매출 등을 추적할 수 있다. 또한 `Firebase Analytics`를 사용하면 사용자 그룹을 세분화하여 특정 그룹의 행동을 분석하거나 A/B 테스트를 실행할 수도 있다.

[_A/B테스트란_](https://www.oracle.com/kr/cx/marketing/what-is-ab-testing/)
분할 테스트 또는 버킷 테스트라고도 하는 A/B 테스트는 두 가지 콘텐츠를 비교하여 방문자/뷰어가 더 높은 관심을 보이는 버전을 추출해 낸다.

## Crashlytics

> `Crashlytics`는 앱의 충돌 및 오류를 모니터링하고 추적하여 해당 문제를 신속하게 식별하고 해결할 수 있도록 도와주는 Google의 오류 보고 도구이다.

Crashlytics를 사용하면 앱에서 발생한 크래시 및 오류의 상세 정보를 확인하고 해당 문제가 발생한 장치, 버전 및 사용자 정보를 파악할 수 있다.

또한 Crashlytics를 사용하면 문제가 식별되면 해당 문제에 대한 자동 알림을 수신하여 빠르게 대응할 수 있으며, 이를 통해 개발자는 앱의 안정성을 유지하고 사용자 경험을 개선할 수 있다.

---

서비스를 런칭한 후 이에 대한 성능 및 안전성을 유지보수를 진행하려면 `Analytics` 및 `Carshlytics`를 등록하는 것이 권장된다.

그렇다면 어떻게 등록하는걸까?

# 등록하기

[파이어베이스 콘솔](https://console.firebase.google.com/u/0/?hl=ko)에 들어가여 로그인 및 프로젝트 생성을 한다.

![](https://velog.velcdn.com/images/cksgodl/post/3c98fe7b-beb8-4e99-b038-42ac391aa7e3/image.png)

프로젝트가 생성됬으면 해당 프로젝트에 안드로이드 앱을 추가한다.

![](https://velog.velcdn.com/images/cksgodl/post/db1d8248-2a5b-40f0-a742-112488a241af/image.png)

1. SHA-1키는 그래들의 `signingReport`에서 얻을 수 있다.
   ![](https://velog.velcdn.com/images/cksgodl/post/042f0efa-4265-467e-8955-ead15180f16d/image.png)

2.`google-services.json`을 다운받아 프로젝트 `app`폴더 내부에 넣어 준다.

![](https://velog.velcdn.com/images/cksgodl/post/dcfbcd39-4448-4a05-9aca-db7ff9960dd4/image.png)

3. 파이어베이스 SDK를 안드로이드 프로젝트내에 등록해준다.

```
implementation platform('com.google.firebase:firebase-bom:31.2.3')
implementation 'com.google.firebase:firebase-crashlytics-ktx:18.3.5'
implementation 'com.google.firebase:firebase-analytics-ktx:21.2.0'
```

파이어베이스 내부에서 튜토리얼을 모두 제공해줌으로 따라가기만 하면 된다.

---

# Firebase Analytics 활성화 및 이벤트 추적

엑티비티의 `onCreate()`메서드에서 `FirebaseAnalytics.getInstance()`를 호출하여 `Firebase Analytics`를 활성화 한다.

```
firebaseAnalytics = FirebaseAnalytics.getInstance(this)
```

활성화된 인스턴스를 활용해 로그이벤트를 내보낼 수 있다.

로그이벤트를 내보내는 방법은

1. 번들에 putString(), putInt() 등으로 로그로 남기길 원하는 데이터들을 넣어주어 내보낼 수 있다.

```
val bundle = Bundle().apply {
	putString("screen_name", "{screenName}")
}
firebaseAnalytics.logEvent(FirebaseAnalytics.Event.SCREEN_VIEW, bundle)
```

2. `AnalyticsKt` 확장함수 이용하기

코틀린에서는 `AnalyticsKt`에서 `logEvent`확장함수를 다음과 같이 지원한다.

```
public inline fun FirebaseAnalytics.logEvent(name: kotlin.String, crossinline block: ParametersBuilder.() -> kotlin.Unit): kotlin.Unit { /* compiled code */ }
```

따라서 다음과같이 파라미터빌더를 활용해 간단하게 보낼 수 있다.

```
firebaseAnalytics.logEvent(FirebaseAnalytics.Event.SCREEN_VIEW) {
	param("screen_name", "{screenName}")
}
```

- `FirebaseAnalytics.Event.SCREEN_VIEW`는 이벤트 이름을 의미하며

- `screen_name`는 이벤트에 담길 정보의 키 값

- `"{screenName}"`은 이벤트에 담길 정보의 밸류 값을 의미한다.

---

## 실제 이벤트 추적해보기

사용자가 뷰에 진입할 때 마다 `screen_view`이벤트를 발생시켜 보기로 하자. 그러기 위해서 최상위 함수로 로그이벤트 확장함수를 선언하였다.

```
fun viewLogEvent(screenName: String) {
    MainActivity.firebaseAnalytics?.logEvent(FirebaseAnalytics.Event.SCREEN_VIEW) {
        param("screen_name", screenName)
    }
}
```

그리고 해당 뷰에 진입할 때 마다 로그이벤트를 발생 시킨다.

```
LaunchedEffect(key1 = Unit) {
    viewLogEvent("HomeScreen")
}
```

그리고 여러 화면을 움직인 후 시간이 지나면 파이어베이스 애널리틱스 콘솔에 다음과 같이 업데이트가 된다.

![](https://velog.velcdn.com/images/cksgodl/post/c9b12168-d8e4-4360-ba51-6b83a005e4e7/image.png)

_추가한 이벤트뿐만 아니라 자동으로 등록되는 이벤트도 여럿 있는것 같다._

`screen_view`의 상세정보를 조회하면 다음과 같이 어떤 페이지를 얼마나 조회했는지 알 수 있다.
![](https://velog.velcdn.com/images/cksgodl/post/a7949d51-8bce-4295-a8f6-41a55e64376c/image.png)

# Firebase Crashlytics 활성화하기

_파이어 베이스 프로젝트 등록 및 `Crashlytics`앱 등록, `SDK`등록은 모두 패스_

테스트용 버튼을 만들어 버튼이 눌렸을 때 오류가 발생하도록 설정하여 보았다.

```
Button(onClick = {
    throw RuntimeException("Test Crash")
}) {
    Text(text = "테스트 크래쉬 버튼")
}
```

![](https://velog.velcdn.com/images/cksgodl/post/8c1afe21-8592-4572-bd21-dafbb3a33d18/image.png)

해당 오류가 발생하고 앱이 비정상 종료되면 파이어베이스 콘솔에서 해당 오류가 발생하였음을 알 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/eabcd01b-f5aa-4af1-9d4d-fa07e8ea4e4f/image.png)

상세로그를 보면 `IDE`와 같이 에러 스택트레이스를 확인할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/1f339180-f375-4b13-8bf1-dd6f187fbf6d/image.png)

또한 어떤 오류가 발생했을 때 상황이나 플래그 값을 키형태로 집어 넣을 수 있다.

```
Button(onClick = {
    val crashlytics = FirebaseCrashlytics.getInstance()
    // 커스텀 로그 메시지 추가
    crashlytics.log("테스트용 메시지")

    // 커스텀 키 추가
    crashlytics.setCustomKeys {
        key("my_string_key", "hello")  // String value
        key("my_bool_key", true)        // boolean value
        key("my_double_key", 1.0)      // double value
        key("my_float_key", 1.0f)        // float value
        key("my_int_key", 2)              // int value
    }

    // 사용자 식별자 설정
    crashlytics.setUserId(uiState.nickName)
    throw RuntimeException("Test Crash")  // Force a crash - 테스트 비정상 종료를 강제로 적용
}) {
    Text(text = "테스트 크래쉬 버튼")
}
```

- 유저 아이디도 확인
  ![](https://velog.velcdn.com/images/cksgodl/post/12ce932f-5166-4946-b452-1037928bfec5/image.png)

- 커스텀 로그 메시지 확인
  ![](https://velog.velcdn.com/images/cksgodl/post/ebf5af1f-862e-4e8b-96d2-a5e5dbecc671/image.png)

- 크래쉬에 대한 커스텀 로그 메시지도 확인가능하다.
  ![](https://velog.velcdn.com/images/cksgodl/post/b6cdb814-d164-4ae6-ad87-1a1ac2c973ea/image.png)

그외에도 비정상 종료 로그를 모두 보여줌으로써 `QA`를 진행할 때 엄청난 도움이 된다.

![](https://velog.velcdn.com/images/cksgodl/post/159a6cca-7ea8-46fd-acda-ecf41be980a3/image.png)

---

`sendUnsentReports()`를 활용하면 에러가 났을 때가 아니라, 에러가 발생하였을 때 보고서를 모두 큐에 넣어두고 이후 한꺼번에 전송한다.
배터리 및 메모리 소모를 감소시키기 위해 사용한다고 한다.

```
val crashlytics = FirebaseCrashlytics.getInstance()
crashlytics.sendUnsentReports()
```

---

> 안드로이드 스튜디오 전기뱀장어 버전부터는 `Firebase Crashlytics`와 `IDE`와의 연결이 가능해졌다!

`View -> Tools -> App Quality Insights`를 활성화하고 파이어베이스를 연결화면 어디서 어떤 에러가 발생하였는지 바로 확인이 가능하다.

![](https://velog.velcdn.com/images/cksgodl/post/3c7d2f9d-6bec-4ad5-91ad-bce82a33ee16/image.png)

## 참고자료

[[Android/kotlin] 구글 Firebase Crashlytics 사용하기](https://eunoia3jy.tistory.com/173)
