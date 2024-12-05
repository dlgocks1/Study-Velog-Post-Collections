![](https://velog.velcdn.com/images/cksgodl/post/981c35fe-a6a1-4293-adee-3495d99c4833/image.png)


### [Android 스튜디오 Electric Eel | 2022.1.1 이 업데이트 되었습니다.](https://developer.android.com/studio/releases?utm_source=android-studio&hl=ko)



# 패치 내역


## [Kotlin 1.8](https://kotlinlang.org/docs/whatsnew18.html#revamped-and-new-pages)을 지원한다.


코틀린 1.8에서 바뀐점은 많지만 그 중 표준 라이브러리의 변화만 알고 넘어가자.

1. `cbrt()` 큐브 루트를 알 수 있는 함수가 `Stable`해 졌다.

```
import kotlin.math.*
​
fun main() {
    val num = 27
    val negNum = -num
​
    println("The cube root of ${num.toDouble()} is: " + 
            cbrt(num.toDouble()))
    println("The cube root of ${negNum.toDouble()} is: " + 
            cbrt(negNum.toDouble()))
}
The cube root of 27.0 is: 3.0
The cube root of -27.0 is: -3.0
```

2. 자바와 코틀린사이의 `TimeUnit`변환이 가능해 졌다.

`java.util.concurrent.TimeUnit` and Kotlin `kotlin.time.DurationUnit` 사이의 변환이 가능
```
import kotlin.time.*

// For use from Java
fun wait(timeout: Long, unit: TimeUnit) {
    val duration: Duration = timeout.toDuration(unit.toDurationUnit())
    ...
}
```


3. 타임마크 비교 및 추적이 용이해 졌다.(Experimental API)

Kotlin 1.8.0 이전에는 여러 TimeMarks와 현재의 시간 차이를 계산하려면 한 번에 하나의 `elapseNow()`를 사용할 수 밖에 없었다.
Kotlin 1.8.0에서는`TimeMark`인스턴스를 새로 생성하고 다른 `TimeMark`와의 연산이 가능해졌다.
```
val timeSource = TimeSource.Monotonic
val mark1 = timeSource.markNow()
Thread.sleep(500) // Sleep 0.5 seconds
val mark2 = timeSource.markNow()

// Before 1.8.0
repeat(4) { n ->
    val elapsed1 = mark1.elapsedNow()
    val elapsed2 = mark2.elapsedNow()

    println("Measurement 1.${n + 1}: elapsed1=$elapsed1, " +
            "elapsed2=$elapsed2, diff=${elapsed1 - elapsed2}")
}
println()

// Since 1.8.0
repeat(4) { n ->
    val mark3 = timeSource.markNow()
    val elapsed1 = mark3 - mark1
    val elapsed2 = mark3 - mark2

    println("Measurement 2.${n + 1}: elapsed1=$elapsed1, " +
            "elapsed2=$elapsed2, diff=${elapsed1 - elapsed2}")
}
println(mark2 > mark1)

// Result
Measurement 1.1: elapsed1=500.728191ms, elapsed2=9.474828ms, diff=491.253363ms
Measurement 1.2: elapsed1=520.053056ms, elapsed2=19.425402ms, diff=500.627654ms
Measurement 1.3: elapsed1=521.803271ms, elapsed2=21.168843ms, diff=500.634428ms
Measurement 1.4: elapsed1=521.878055ms, elapsed2=21.244455ms, diff=500.633600ms

Measurement 2.1: elapsed1=521.967329ms, elapsed2=21.326836ms, diff=500.640493ms
Measurement 2.2: elapsed1=522.044927ms, elapsed2=21.404434ms, diff=500.640493ms
Measurement 2.3: elapsed1=522.133124ms, elapsed2=21.492631ms, diff=500.640493ms
Measurement 2.4: elapsed1=522.202806ms, elapsed2=21.562313ms, diff=500.640493ms
true
```

4. `java.nio.file.path`의 확장함수인 `copyToRecursively()`및 `deleteRecursively()`가 출시되었다.

* `copyToRecursively()` : 디렉토리 및 파일들을 다른 목적지로 모두 복사할 수 있다.
* `deleteRecursively()` : 디렉토리 와 내용을 모두 제거 가능하다.

[API Reference는 여기서 확인](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.io.path/java.nio.file.-path/copy-to-recursively.html)


## 2. Logcat 업데이트

![](https://velog.velcdn.com/images/cksgodl/post/015fd724-75d2-4e3b-a2bc-667f518fdfc5/image.png)

새로운 버전의 로그캣이라는 데 무엇을 업데이트해 줬는지는 안알려준다.
[Logcat 사용방법](https://developer.android.com/studio/debug/logcat?hl=ko)


## 3. Firebase Crashlytics를 IDE내에서 확인 가능하다.

Android 스튜디오 Electric Eel부터 IDE에서 직접 Firebase Crashlytics의 앱 비정상 종료 데이터를 확인하고 조치를 취할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/bfec0e20-e1c3-4841-93a1-34a1b809a07f/image.png)

기존에 Firebase Crashlytics에 앱을 등록하고 앱이 크러쉬되는 오류가 발생한다면 다음과 같이 에러 스택 및 위치를 파이어 베이스에서 확인이 가능했다.

![](https://velog.velcdn.com/images/cksgodl/post/eb0f0759-5585-4ea0-b994-5e16a1c2b154/image.png)

```
Fatal Exception: java.lang.RuntimeException: Test Crash
       at com.cmc12th.runway.ui.home.view.HomeScreenKt$ShowNews$1.invoke(HomeScreen.kt:115)
       at com.cmc12th.runway.ui.home.view.HomeScreenKt$ShowNews$1.invoke(HomeScreen.kt:114)
       // ...
```

Android Studio Electric Eel에서는 `App Quality Insights`도구 창에서 해당 정보를 볼 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/aa12eb36-8960-4d1b-87e0-d4b5c31ed2f2/image.png)

크러쉬가 난 위치 및 에러 스택, 안드로이드 버전 및 기기 정보 등을 모두 제공한다.

![](https://velog.velcdn.com/images/cksgodl/post/e9f84e71-488b-4b88-a999-b4a11452be66/image.png)


## 4. `Compose`미리보기의 실시간 업데이트

기존 안드로이드 `Dolphin`에도 `Preview`에 대한 `Live Edit`를 지원했던 것 같은데 뭔가 더 지원한다고 한다. 

![](https://velog.velcdn.com/images/cksgodl/post/4e34109f-c475-46f2-af58-ec7c8e05eb10/image.gif)



## 5. 다양한 기기에서 Compose 미리보기 사용

다양한 기기에 대한 미리보기를 지원한다.

![](https://velog.velcdn.com/images/cksgodl/post/0f69fcc4-97e0-4175-b793-4a5de28efc29/image.png)

```
@Preview(
    showBackground = true,
    showSystemUi = true,
    device = "spec:width=673.5dp,height=841dp,dpi=480"
)
@Composable
private fun ShowNews2() {
    Text(
        modifier = Modifier
            .fillMaxWidth()
            .padding(start = 20.dp, end = 20.dp, top = 30.dp),
        text = "안녕하세요! 흥미로운 가게 소식을 알려드려요, ㅇ유아이가 업데이트 되빈다아앙 ",
        style = HeadLine4,
        color = Color.Black
    )
}
```

![](https://velog.velcdn.com/images/cksgodl/post/1b2bc5c3-5c00-46a7-96c7-0eadfa23bf62/image.png)



## 6. Layout Inspector 리컴포지션 렌더링 강조 표시

`Compose`의 `Layout Inspector`에서 리컴포지션 횟수를 표시할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/1c83986f-72b4-4fe3-ba3d-d2664b6b783a/image.png)

한 컴포저블이 다른 컴포저블보다 더 높은 속도로 재구성되는 경우 더 강한 그래디언트 오버레이 색상을 수신한다.

검색탭에서 텍스트를 수정하면 결과 화면과, TextBox가 뻘겋게 변한다.
 
![](https://velog.velcdn.com/images/cksgodl/post/77774ced-51fc-42f9-b4db-db7e017d577c/image.png)



## 7. 시각적 린트 작업

다양한 화면 크기에서 시각적 린트 문제를 확인 가능하다. `XML`로 작성된 뷰의 디자인 문제를 해결 가능하다.

![](https://velog.velcdn.com/images/cksgodl/post/adede585-fdd7-450c-bc4b-78ea894e2b64/image.png)


## 8. 크기 조절 가능한 에뮬레이터

이제 크기 조절 가능한 단일 에뮬레이터로 여러 화면 크기에서 앱을 테스트할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/157f4dcf-a5c0-478b-be45-f82d31391e12/image.png)

기존 디바이스 에물레이터를 설치하는 곳에 있다.

![](https://velog.velcdn.com/images/cksgodl/post/db9d7b83-9f43-4620-81b4-489129bf019f/image.png)

해당 디바이스를 실행시키면 폴드, 타블렛, 핸드폰 등의 사이즈를 설정할 수 있다.


## 9. 기기 미러링

Electric Eel의 `Running Devices` 창에서 기기를 미러링할 수 있다. 기기 화면을 Android 스튜디오로 직접 스트리밍하며 IDE 자체에서 바로 화면 회전이나 볼륨 변경, 기기 잠금/잠금 해제와 같은 일반적인 작업을 실행할 수 있다.

* 설정 -> Experimental 에서 디바이스 미러링을 체크한다.

![](https://velog.velcdn.com/images/cksgodl/post/b20411c2-f0f8-46a5-8be8-8c8ae4ec7bce/image.png)

핸드폰을 연결하고 `Running Devices` 상단 탭을 바꾸어주면 끝

![](https://velog.velcdn.com/images/cksgodl/post/855fe5b9-497a-419b-a06a-ca113cfe05ba/image.png)

_안녕,, 미러로이드!_
![](https://velog.velcdn.com/images/cksgodl/post/2305cb22-2f54-4078-89eb-5193861faa00/image.png)


## 10. 데스크톱 Android Virtual Device 이용 가능

데스크톱 Android Virtual Device(AVD)를 사용하여 Chromebook과 같은 데스크톱 기기에서 앱이 어떻게 작동하는지 테스트할 수 있다.

대형 화면 기기에서 앱이 어떻게 상호작용되는지 볼 수 있을 것이다. 

![](https://velog.velcdn.com/images/cksgodl/post/9907bc08-b444-4e6f-af5e-cc4651b2e8d3/image.png)

[Desktop AVD in Android](https://chromeos.dev/en/posts/desktop-avd-in-android-studio)에 설치 방법 및 활용방안이 설명되어 있다.


## 11. 빌드 분석 도구의 업데이트

빌드 분석 도구에서 종속 항목 다운로드에 소요된 시간에 관한 요약과 저장소별 다운로드에 관한 자세한 뷰를 제공한다

종속성 관리에 용이할 것

![](https://velog.velcdn.com/images/cksgodl/post/3e98b260-a5d4-47de-a9c0-f7be2ce29735/image.png)


![](https://velog.velcdn.com/images/cksgodl/post/6965de1d-7f3c-4022-ac62-9c41605f604e/image.png)


---

## 결론

1. 리사이저블 에뮬레이터는 쓸만하다.
2. 기기 페어링이 드디어 나왔다.
3. 로그캣, 컴포즈 미리보기 등이 꾸준히 업데이트 되는 중이다.
4. `Crashlytics`를 `IDE`에서 지원해주어 상당히 간편해 졌다.

끝
