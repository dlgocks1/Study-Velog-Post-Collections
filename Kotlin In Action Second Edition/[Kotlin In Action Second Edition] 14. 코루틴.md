모바일 및 데스크톱 앱은 초당 60회 이상 사용자 인터페이스를 다시 그리면서 장치 내 데이터베이스 쿼리, 센서 사용, 다른 장치와의 통신 등 다양한 작업을 수행해야 한다.


이를 처리하기 위해 최신 애플리케이션은 여러 작업을 동시에 비동기적으로 수행해야 한다.

## 14.1 동시성 대 병렬성

- 동시성

![](https://velog.velcdn.com/images/cksgodl/post/b3209faf-4cfa-49ad-a164-973c2fbdbe9e/image.png)

- 병렬성

![](https://velog.velcdn.com/images/cksgodl/post/e633070a-0b1c-4c47-af27-b2941487155d/image.png)


## 14.2 Kotlin 방식의 동시성: 함수 및 코루틴 일시 중단

코루틴은 비동기적으로 실행할 수 있고 차단되지 않는 동시성 코드를 작성하는 우아한 방법을 제공하는 `Kotlin`의 기능이다. 스레드와 같은 전통적인 접근 방식과 비교할 때 코루틴은 훨씬 더 가볍다. 또한 구조화된 동시성을 통해 동시 작업과 그 수명 주기를 관리하는 데 필요한 기능을 제공한다.

## 14.3 스레드와 코루틴 비교

`JVM`에서 동시 및 병렬 프로그래밍을 위한 고전적인 추상화는 스레드를 사용하여 서로 독립적으로 동시에 실행되는 코드 블록을 지정할 수 있는 기능을 제공하는 것이다. 

이 책을 통해 `Kotlin`은 `Java`와 100% 호환되며 스레드도 예외는 아니다. `Java`에서와 같이 스레드를 사용하려면 `Kotlin` 표준 라이브러리의 편리한 함수를 사용하면 된다. 

```kotlin
import kotlin.concurrent.thread
fun main() {
    println("I'm on ${Thread.currentThread().name}")
    thread {
        println("And I'm on ${Thread.currentThread().name}")
    }
}
// I'm on main
// And I'm on Thread-0
```

스레드를 사용하면 멀티코어 `CPU`의 개별 코어에 작업을 분산하여 애플리케이션의 응답성을 높이고 최신 시스템을 보다 효율적으로 사용할 수 있다.

하지만, `JVM`에서 사용자가 생성하는 각 스레드는 일반적으로 운영 체제에서 관리하는 스레드에 해당하고, 이러한 시스템 스레드를 생성하고 관리하는 데는 많은 비용이 들 수 있으며, 최신 시스템에서도 한 번에 수천 개의 스레드만 효과적으로 관리할 수 있다. 

각 시스템 스레드는 몇 메가바이트의 메모리를 할당해야 하며, 스레드 간 전환은 운영 체제 커널 수준에서 실행되는 작업이다. 

또한 스레드는 기본적으로 독립형 프로세스로만 존재하기 때문에 작업을 관리하고 조정할 때, 특히 취소 및 예외 처리와 같은 개념과 관련하여 어려움을 겪을 수 있다. 

---

`Kotlin`은 일시 중단 가능한 계산을 다시 전송하는 코루틴이라는 스레드에 대한 대체 추상화를 도입했다. 

- 코루틴은 매우 가벼운 추상화이다. 일반 노트북에서 10만 개 이상의 코루틴을 쉽게 실행할 수 있다. 
코루틴은 생성 및 관리 비용이 저렴하기 때문에 매우 짧은 작업에도 스레드를 사용하는 것보다 훨씬 더 광범위하고 세분화된 방식으로 사용할 수 있다.

- 코루틴은 시스템 리소스를 차단하지 않고 실행을 일시 중단했다가 나중에 중 단한 지점부터 다시 시작할 수 있다. 
따라서 코루틴은 스레드 차단과 비교되는 네트워크 요청 대기 또는 IO 작업과 같은 많은 비동기 작업에 효율적으 로 사용할 수 있다.

- 코루틴은 구조적 동시성이라는 개념을 통해 동시 작업의 구조와 계층을 설정 하여 취소 및 오류 처리를 위한 메커니즘을 제공한다. 
구조적 동시성은 동시 계산의 일부가 실패하거나 더 이상 필요하지 않은 경우 계산의 하위로 시작된 다른 코루틴이 취소되도록 한다.

![](https://velog.velcdn.com/images/cksgodl/post/2d53fb66-4105-47b4-b194-fafd544c2ab6/image.png)


## 14.4 일시중지할 수 있는 함수 : 일시중지 기능

스레드, 반응형 스트림 또는 콜백 같은 다른 동시성 접근 방식과 차별화되는 `Kotlin` 코루틴 작업의 주요 속성 중 하나는 일시 중단 함수이다.

### 14.4.1 일시 중단 함수를 사용하여 작성된 코드는 순차적으로 보인다.

`Kotlin`에서 일시 중단 함수가 어떻게 작동하는지 이해하기 위해 예제를 통해 알아보겠다. 

```kotlin
fun login(credentials: Credentials): UserID
fun loadUserData(userID: UserID): UserData
fun showData(data: UserData)
fun showUserInfo(credentials: Credentials) {
    val userID = login(credentials)
    val userData = loadUserData(userID)
    showData(userData)
}
```

계산 관점에서 볼 때 이 코드는 실제로 많은 작업을 수행하지 않는다. 대부분의 시간을 네트워크 작업의 결과를 기다리는 데 소비하며, `showUserInfo` 함수가 실행 중인 스레드를 차단한다.

![](https://velog.velcdn.com/images/cksgodl/post/e4b28a6b-4d00-46b8-bb9f-6bbddfd9ebc6/image.png)

코루틴, 더 구체적으로는 일시 중단 함수를 사용하면 더 나은 작업을 수행할 수 있다. 아래는 `Kotlin` 코루틴을 사용하여 비블록킹 구현과 동일한 코드를 작성한 것이다.

```kotlin
suspend fun login(credentials: Credentials): UserID
suspend fun loadUserData(userID: UserID): UserData
fun showData(data: UserData)

// 코드는 여전히 순차적으로 보인다. 
suspend fun showUserInfo(credentials: Credentials) {
    val userID = login(credentials)
    val userData = loadUserData(userID)
    showData(userData)
}
```

그렇다면 함수에 `suspend`을 표시한다는 것은 무엇을 의미할까? 

이 함수는 예를 들어 네트워크 응답을 기다리는 동안 실행을 일시 중지할 수 있음을 나타낸다. 일시 중단은 기본 스레드를 차단하지 않는다. 대신 함수 실행이 일시 중단되면 다른 코드가 동일한 스레드에서 실행될 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/25905722-23cf-4705-b0ea-34dc0cbb3bbc/image.png)

## 14.5 코루틴과 다른 접근방식 비교

가장 일반적인 접근 방식인 콜백, 리액티브 스트림(`RxJava`), 퓨처를 아우르는 세 가지 예시를 간략하게 살펴보겠다. 

여기서는 자세한 설계에 대해서는 다루지 않겠지만, 논의의 목적을 위해 몇 가지 샘플 구현을 간략하게 살펴보겠다. 물론 이러한 접근 방식을 사용해 본 적이 없다면 이 섹션을 건너뛰어도 된다.

콜백을 활용하고자한다면 콜백 매개 변수를 전달해야 한다.

```kotlin
fun loginAsync(credentials: Credentials, callback: (UserID) -> Unit)
fun loadUserDataAsync(userID: UserID, callback: (UserData) -> Unit)
fun showData(data: UserData)
fun showUserInfo(credentials: Credentials) {
    loginAsync(credentials) { userID ->
        loadUserDataAsync(userID) { userData ->
            showData(userData)
		} 
	}
}
```

로직이 커지면 중첩된 콜백으로 인해 읽기 어려운 혼란에 빠지게 된다. 이 문제는 "콜백 지옥"이라는 별명이 붙을 정도로 악명이 높다.

이를 해결하기 위해 `CompletableFuture`를 사용하면 콜백 중첩을 피할 수 있지만 `thenCompose` 및 `thenAccept`와 같은 새로운 연산자의 의미를 배워야 한다. 또한 `loginAsync` 및 `loadUserDataAsync` 함수의 반환 유형을 변경해야 하는데, 이제 해당 반환 유형은 `CompletableFuture`로 래핑되어야 한다.

```kotlin
fun loginAsync(credentials: Credentials): CompletableFuture<UserID>
        
fun loadUserDataAsync(userID: UserID): CompletableFuture<UserData>
fun showData(data: UserData)
fun showUserInfo(credentials: Credentials) {
	loginAsync(credentials)
    	.thenCompose { loadUserDataAsync(it) }
        .thenAccept { showData(it) }
}
```

마찬가지로 반응형 스트림을 통한 구현(예: `RxJava`)은 콜백 지옥을 피할 수 있지만 여전히 함수의 서명(이제 단일 래핑된 값을 반환)을 변경해야 하며 `flatMap`, `doonSuccess` 및 `subscribe`와 같은 연산자를사용해야 한다.

```kotlin
fun login(credentials: Credentials): Single<UserID>
fun loadUserData(userID: UserID): Single<UserData>
fun showData(data: UserData)

fun showUserInfo(credentials: Credentials) {
	login(credentials)
    	.flatMap { loadUserData(it) }
        .doOnSuccess { showData(it) }
        .subscribe()
}
```

두 접근 방식 모두 인지 오버헤드가 발생하며 러닝커브가 있다. 이를 `Kotlin` 코루틴을 사용하는 접근 방식과 비교해 보면, `suspend` 수정자를 사용하여 함수만 표시하면 나머지 코드는 동일하게 유지되고 순차적인 모양을 유지하며 스레드를 차단하는 초기 단점을 피할 수 있다.

### 14.5.1 일시 중단 함수 호출하기

일시 중단 함수는 실행을 일시 중지할 수 있으므로 일반 코드에서 아무 곳에서나 호출할 수 없으며, 실행을 일시 중지할 수 있는 코드 블록에서 호출해야 한다. 

즉, 또 다른 일시 중지 함수에서 실행되어야 한다.

`suspend`인 `showUserInfo` 함수는 일시 중단된 로그인 및 `loadUserData` 함수를 호출할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/6efa0a96-0060-4b9a-a166-13ef23c57d74/image.png)

일반 함수에서 호출하면 에러가 난다.

```kotlin
suspend fun mySuspendingFunction() {}
fun main() {
    mySuspendingFunction()
	// Error: Suspend function mySuspendingFunction should be called only from a coroutine or another suspend function.
}
```

## 14.6 코루틴의 세계로 들어가기: 코루틴 빌더

코루틴은 일시 중단 가능한 하나의 인스턴스이다. 스레드와 유사하게 다른 코루틴과 동시에(또는 병렬로) 실행할 수 있는 코드 블록으로 생각할 수 있다. 이러한 코루틴을 만들려면 코루틴 빌더 함수 중 하나를 사용해야 한다.

- `runBlocking`은 블록킹 코드와 일시중단기능의 세계를 연결하기 위해 설계 되었다.
- `launch`는 값을 반환하지 않는 새 코루틴을 시작하는데 사용된다.
- `async`는 비동기 방식으로 값을 계산하는 데 사용된다.


### 14.6.1 일반 코드에서 코루틴의 영역으로: runBlocking 함수

블로킹 코드의 세계를 일시 중단 함수의 영역으로 연결하려면 `runBlocking` 코루틴 빌더 함수를 사용할 수 있다. 이 함수는 새 코루틴을 생성 및 실행하고 코루틴이 완료될 때까지 현재 스레드를 간단히 차단한다. 

함수에 전달된 코드 블록 내에서 일시 중단된 함수를 호출 할수있다.

```kotlin
import kotlinx.coroutines.*
import kotlin.time.Duration.Companion.milliseconds

suspend fun doSomethingSlowly() {
    delay(500.milliseconds)
    println("I'm done")
}

fun main() = runBlocking {
    doSomethingSlowly()
}
```

_하지만 잠깐만요, 코루틴을 사용하는 목적이 스레드 차단을 피하기 위한 것이 아니었나요?_

그렇다면 왜 지금 `runBlocking`을 사용하는걸까? 실제로 `runBlocking`을 사용하면 하나의 스레드를 차단한다. 하지만 이코루틴 내에서 자식 코루틴을 얼마든지 추가로 시작할 수 있으며, 이 경우 더 이상 스레드가 차단되지 않는다. 

대신 동시에 실행되므로 다른 코루틴이 코드를 실행하기 위해 일시 중단될 때마다 하나의 스레드를 확보할 수 있다. 이러한 추가 자식 코루틴을 시작하려면 실행 코루틴 빌더를 사용하면 된다.

### 14.6.2 start-and-forget하는 코루틴 만들기: launch 함수

실행 함수는 새로운 자식 코루틴을 시작하는 데 사용된다. 일반적으로 어떤 코드를 실행하고 싶지만 반환값을 계산할 때까지 기다리지 않는 `start and forget` 시나리오에 사용된다. 

```kotlin
private var zeroTime = System.currentTimeMillis()

fun log(message: Any?) =
    println("${System.currentTimeMillis() - zeroTime} " +
    	"[${Thread.currentThread().name}] $message")

fun main() = runBlocking {
    log("The first, parent, coroutine starts")
    launch {
        log("The second coroutine starts and is ready to be suspended")
        delay(100.milliseconds)
        log("The second coroutine is resumed")
	}
	launch {
        log("The third coroutine can run in the meantime")
    }
    log("The first coroutine has launched two more coroutines")
}
```

시간은 달라도 순서는 모두 아래와 동일할 것이다.

![](https://velog.velcdn.com/images/cksgodl/post/6a6ba04a-4ede-44c8-bcee-781a5f20c113/image.png)


이 예제에서는 모든 코루틴이 메인이라는 하나의 스레드에서 실행된다. 그림으로 나타내면 아래와 같다.

![](https://velog.velcdn.com/images/cksgodl/post/796f657e-949c-4e4e-b5db-aaffea2a5959/image.png)

이 예제에서 코드는 실행 차단으로 시작된 첫 번째(부모) 코루틴과 launch를 두 번 호출하여 시작된 두 개의 자식 코루틴 등 세 개의 코루틴을 시작한다. 

1. `코루틴 2`가 지연 함수를 호출하면 코루틴의 일시 중단이 트리거된다. 이를 일시 중지 지점이라고 한다. (`delay`또한 지연 함수이다.) 
2. `코루틴 2`는 지정된 시간 동안 일시 중지되고 다른 코루틴이 작업한다. 
3. 즉, `코루틴 3`이 작업을 시작한다. `코루틴 3`은 하나 의 로그 호출만 포함하므로 빠르게 완료된다. 
4. 지정된 100밀리초가 지나면 `코루틴 2`가 작업을 재개하고 전체 프로그램 실행이 완료된다.

> _일시 중단된 코루틴은 어디로 이동하나요?_
>
> 코루틴을 작동시키기 위한 무거운 작업은 컴파일러가 담당하며, 코루틴 일시 중단, 재개, 스케줄링을 담당하는 슈퍼포팅 코드를 생성한다. 코루틴이 일시 중단되면 일시 중단 당시의 상태에 대한 정보가 메모리에 저장되고, 컴파일 시점에 일시 중단 함수 코드가 변환된다. 이 정보를 기반으로 나중에 실행을 복원하고 다시 시작할 수 있다.

`launch`의 설계는 실제 반환 값에 관심이 없는 경우 파일이나 데이터베이스에 쓰는 등의 부작용이 발생할 수 있는 `start and forget`작업에 더 적합하게 되어 있다. 

`launch`함수는 `Job` 객체를 생성하며, 이는 코루틴의 핸들러이라고 생각하면 된다. `Job`객체를 사용해 취소를 트리거하는 등 코루틴 실행을 제어할 수 있다

### 14.6.3 대기 중인 계산: async 빌더

비동기계산을 수행하려는 경우 `async` 빌더 기능을 사용할 수 있다. `async`함수의 반환 유형은 `Deferred<T>` 인스턴스이다. `Deferred`로 할 수 있는 주요 작업은 일시 중단 `await` 함수를 통해 결과를 기다리는 것 이다.

```kotlin
suspend fun slowlyAddNumbers(a: Int, b: Int): Int {
    log("Waiting a bit before calculating $a + $b")
    delay(100.milliseconds * a)
    return a + b
}

fun main() = runBlocking {
    log("Starting the async computation")
    val myFirstDeferred = async { slowlyAddNumbers(2, 2) }
    val mySecondDeferred = async { slowlyAddNumbers(4, 4) }
    log("Waiting for the deferred value to be available")
    log("The first result: ${myFirstDeferred.await()}")
    log("The second result: ${mySecondDeferred.await()}")
}
```

![](https://velog.velcdn.com/images/cksgodl/post/162efc87-fbcb-4475-89f5-dd7984976c01/image.png)

`async`는 각 함수 호출에 대해 새 코루틴을 시작하여 두 계산을 동시에 수행할 수 있도록 합한다. `async` 호출은 코루틴을 일시 중단하지 않는다. `await`를 호출하면 값을 사용할 수 있을 때까지 루트 코루틴이 일시 중단된다.

![](https://velog.velcdn.com/images/cksgodl/post/6979e6a7-db84-426d-8dcd-e457f9d916c3/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/6a6dfa6f-4851-403c-ab81-d35dc9c55c8a/image.png)

코루틴은 스레드 위에 있는 추상화이다. 하지만 코드는 실제로 어떤 스레드에서 실행될까? `runBlocking`의 경우는 코드는 함수를 호출하는 스레드에서 실행된다. 코드를 실행할 스레드를 보다 세밀하게 제어하려면 `Kotlin` 코루틴에서 디스패처를 사용해야 한다.

## 14.7 코드가 실행될 위치 결정하기: 디스패처

코루틴의 디스패처는 코루틴이 실행에 사용하는 스레드를 결정한다. 디스패처를 선택하면 코루틴 실행을 특정 스레드로 제한하거나 스레드 풀로 디스패치하여 코루틴이 특정 스레드에서 실행될지 또는 여러 스레드에서 실행될지 결정할 수 있다. 

본질적으로 코루틴은 특정 스레드에 구속되지 않으므로 디스패처의 지시에 따라 코루틴이 한 스레드에서 실행을 일시 중단했다가 다른 스레드에서 실행을 재개할 수도 있다.

### 14.7.1 디스패처 선택하기

14.8절에서 살펴보겠지만 코루틴은 기본적으로 부모로부터 디스패처를 상속받으므로 모든 코루틴에 대해 명시적으로 디스패처를 지정할 필요는 없다. 

#### 멀티스레드 범용 디스패처 : DISPATCHERS.DEFAULT

범용 작업에 사용할 수 있는 가장 일반적인 디스패처는 `Dis- patchers.Default`이다. 이는 사용 가능한 `CPU` 코어 수만큼의 스레드가 있는 스레드 풀에 의해 지원된다. 

즉, 기본 디스패처에서 코루틴을 예약하면 코루틴이 여러 스레드에 걸쳐 실행되도록 분산되므로 멀티코어 컴퓨터에서 병렬로 실행할 수 있다. 특정 스레드나 스레드 풀에 국한되어야 하는 특별한 시나리오가 아니라면 대부분의 코루틴을 시작할 때 기본 디스패처를 사용하는 것이 보통이다. 

_각 코루틴은 사용하는 스레드를 차단하지 않고 일시 중단하기 때문에 단일 스레드로도 수천 개의 코루틴을 처리할 수 있다는 점을 기억하세요._

#### UI 스레드에서 실행: DISPATCHERS.MAIN

`UI` 프레임워크는 특정 작업의 실행을 `UI` 스레드 또는 메인 스레드라고 하는 특정 스레드로 제한해야 할 때가 있다. 

코루틴에서 이러한 연산을 안전하게 실행하려면 코루틴을 디스패치할 때 `Dispatchers.Main`을 사용하면 된다. 애플리케이션의 `"UI"` 또는 `"메인"` 스레드가 무엇인지에 대한 보편적인 정의는 없으므로 사용 중인 프레임워크에 따라 `Dispatchers.Main`의 실제 값은 달라진다. 

#### IO 작업 차단하기: DISPATCHERS.IO

타사 라이브러리를 사용하는 경우 코루틴을 염두에 두고 구축된 API를 선택할 수 있는 옵션이 항상 있는 것은 아니다. 이러한 경우 데이터베이스 시스템과 상호 작용하기 위해 차단 `API`만 있는 경우 기본 디스패처에서 이 기능을 호출할 때 문제가 발생할 수 있다. (기본 디스패처의 스레드 수는 사용 가능한 `CPU` 코어 수와 같음) 

즉, 듀얼 코어 컴퓨터에서 두 개의 스레드 차단 작업을 호출하면 기본 스레드 풀이 소진되어 작업이 완료될 때까지 기다리는 동안 다른 코루틴을 실행할 수 없게 된다. `IO` 디스패처는 이러한 시나리오를 정확히 해결하도록 설계되었다. 이 디스패처에서 시작된 코루틴은 자동으로 확장되는 스레드 풀에서 실행되며, 이 풀은 차단 `API`가 반환되기를 기다리는 이런 종류의 `비 CPU 집약적 작업`에 정확하게 할당된다.

![](https://velog.velcdn.com/images/cksgodl/post/4993ca54-3283-40f1-ad07-7ca0dd7f1f93/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/1f776e9e-04f2-4bed-b185-beaad0c10480/image.png)

지금까지 살펴본 것처럼 새 코루틴을 시작할 때 디스패처를 지정할 필요는 없다. 그렇다면 코드가 어디에서 실행될까? 정답은 부모 코루틴의 디스패처이다. 

### 14.7.2 코루틴 빌더에 디스패처 전달하기

특정 디스패처에서 코루틴을 실행하려면 코루틴 빌더 함수에 디스패처를 인수로 전달하면 된다. `runBlocking`, `launch`, `async` 등 모든 코루틴빌더 함수를 사용하면 해당 코루틴의 디스패처를 명시적으로 지정할 수 있다.

```kotlin
fun main() {
    runBlocking {
        log("Doing some work")
        launch(Dispatchers.Default) {
            log("Doing some background work")
        }
	}
}
```

![](https://velog.velcdn.com/images/cksgodl/post/9e8d8c36-eead-4403-83b0-a9227d6e18a3/image.png)

### 14.7.3 withContext를 사용하여 코루틴 내에서 디스패처 전환하기

특히 `UI` 프레임워크로 작업할 때는 코드가 특정 기본 스레드에서 실행되도록 해야 할 수 있다. UI 애플리케이션을 개발할 때 일반적인 패턴은 백그라운드에서 오래 실행되는 계산을 수행한 다음 결과가 나오면 `UI` 스레드로 전환하여 사용자 인터페이스를 업데이트하는 것이다.

이미 존재하는 코루틴의 디스패처를 전환하려면 `withContext` 함수를 사용하고 다른 디스패처를 전달하면 된다. 

```kotlin
launch(Dispatchers.Default) {
    val result = performBackgroundOperation()
    withContext(Dispatchers.Main) {
        updateUI(result)
    }
}
```

![](https://velog.velcdn.com/images/cksgodl/post/3f98ad6d-1ad5-46ff-bfed-78ca4c42ce53/image.png)

### 14.7.4 코루틴과 디스패처는 스레드 안전 문제에 대한 마법의 해결책이 아니다.

방금 두 가지 기본 제공 멀티스레드 디스패처인 `Dispatchers.Default`와 `Dispatchers.IO` 에 대해 알아봤다. 멀티 스레드 디스패처는 코루틴을 둘 이상의 스레드에 분산시킨다. 

이전에 멀티스레드 프로그래밍을 해본 적이 있다면, 이제 일반적인 스레드 안전 문제가 발생하지 않는지 궁금할 것이다. 

단일 코루틴은 항상 순차적으로 실행되며, 개별 코루틴의 어떤 부분도 병렬로 실행되지 않는다. 이는 또한 단일 코루틴과 관련된 데이터에는 일반적인 동기화 문제가 발생하지 않는다는 의미이기도 하다. 여러 (병렬) 코루틴에서 데이터를 읽고 변경하는 것은 그리 쉬운 일이 아니다. 이 작지만 중요한 차이를 설명하기 위해 두 예제를 비교해보겠다.

```kotlin
runBlocking {
	launch(Dispatchers.Default) {
    	var x = 0
        repeat(10_000) {
        	x++
		}
        println(x) 
        // 10,000
	}
} 
```

```kotlin
fun main() {
    runBlocking {
        var x = 0
        repeat(10_000) {
            launch(Dispatchers.Default) {
                x++
			} 
		}
        delay(1.seconds)
		println(x) 
	}
}
// 9,916
// Starts the coroutines on the multithreaded default dispatcher
```

이 경우 카운터 값이 예상보다 낮은 이유는 동일한 데이터를 수정하는 코루틴이 여러개 있기 때문이다. 멀티스레드 디스패처에서 실행 중이기 때문에 이러한 작업 중 일부가 병렬로 수행되는 경우 일부 증분 작업이 서로를 덮어쓸 수 있다.

이 상황을 해결 하기 위해 사용할 수 있는 몇 가지 접근 방식이 있다.

```kotlin
fun main() = runBlocking {
    val mutex = Mutex()
    var x = 0
    repeat(10_000) {
        launch(Dispatchers.Default) {
            mutex.withLock {
				x++ 
			}
		}
	}
    delay(1.seconds)
	println(x) 
	// 10000
}
```

`AtomicInteger`나 `ConcurrentHashMap`과 같이 동시 수정용으로 만들어진 원자 및 스레드 안전 데이터 구조를 사용할 수도 있다. 또는 단일 스레드 디스패처에서 코루틴을 제한 (또는 `withContext`를 사용)하면 문제를 해결할 수 있지만 고려해야 할 고유한 성능 특성이 있다. 

코루틴으로 작업할 때는 스레드와 동일한 동시성 문제가 적용된다. 데이터가 단일 코루틴에 연결되어 있는 한, 코드는 즉시 예상대로 작동한다. 병렬로 실행되는 여러 코루틴이 동일한 데이터를 수정하는 경우 스레드에서와 마찬가 지로 동기화 또는 잠금을 수행해야 한다.

## 14.8 코루틴은 코루틴 컨텍스트에 추가 정보를 전달할 수 있다.

디스패처를 전달했을 때 함수의 매개변수를 살펴보면 실제로 매개변수가 코루틴 디스패처가 아니라는 것을 알 수 있다. 실제로 매개변수는 `CoroutineContext`이다. 이것이 무엇인지 살펴보겠다.

각 코루틴은 코루틴컨텍스트를 맵의 형태로 추가적인 컨텍스트 정보를 추가하여 전달한다. 이러한 요소 중 하나는 실제로 디스패처로, 주어진 코루틴이 실행될 스레드를 결정한다. 

또한 코루틴 컨텍스트에는 일반적으로 코루틴의 수명 주기 및 (잠재적으로 예외적인) 취소를 담당하는 코루틴과 관련된 `Job` 객체가 포함된다. 코루틴 컨텍스트에는 `CoroutineName` 또는 `CoroutineExceptionHandler`와 같은 추가 첨부 메타데이터도 포함될 수 있다.

일시 중단 함수 내부의 `coroutineContext`라는 특수 프로퍼티에 액세스하여 현재 코루틴 컨텍스트를 검사할 수 있다.

```kotlin
import kotlin.coroutines.coroutineContext

suspend fun introspect() {
    log(coroutineContext)
}

fun main() {
    runBlocking {
        introspect()
    }
}

// 25 [main @coroutine#1] [CoroutineId(1), "coroutine#1":BlockingCoroutine{Active}@610694f1, BlockingEventLoop@43814d18]
```

코루틴 빌더나 `withContext` 함수에 매개변수를 전달하면 자식 코루틴의 컨텍스트에서 이 특정 요소를 재정의한다. 한 번에 여러 매개변수를 재정의하려면 `+` 연산자를 사용하여 연결하면 되는데, 이 연산자는 코루틴 컨텍스트 객체에 대해 오버로드되어 있다. 

![](https://velog.velcdn.com/images/cksgodl/post/1fa91b86-c4bc-421d-863e-209f402420dc/image.png)

## 요약

- 동시성이란 여러 작업을 동시에 처리하는 것, 병렬성은 물리적으로 동시에 실행하는 것을 의미한다.
- 코루틴은 동시 실행을 위해 스레드 위에서 작동하는 경량 추상화이다.
- `Kotlin`의 핵심 동시성 프리미티브는 실행을 일시 중지할 수 있는 함수인 일시 중지 함수이다. 일시 중단 함수는 다른 일시 중단 함수에서 호출하거나 코루틴 내에서 호출할 수 있다.
- 반응형스트림, 콜백, 퓨처와 같은 다른 접근방식과 달리 `suspend`함수는 코드의 모양을 변경하지 않으며 순차적으로 보일 수 있다.
- 코루틴은 일시 중단 가능한 계산의 집합인 인스턴스이다.
- 코루틴은 비용이 많이 들고 제한된 시스템 리소스를 사용하는 스레드 차단으로 인해 발생하는 문제를 방지한다.
- `runBlocking`, `launch` 및 `async`와 같은 코루틴 빌더를 사용하면 새로운 코루틴을 만들 수 있다.
- 디스패처는 코루틴을 실행할 스레드 또는 스레드 풀을 결정한다.
- 내장된 여러 디스패처는 서로 다른 용도로 사용된다: `Dispatchers.Default`는 범용
디스패처이고, `Dispatchers.Main`은 UI 스레드에서 작업을 실행하는 데 도움이 되며, `Dispatchers.IO`는 블로킹 IO 작업을 호출하는 데 사용된다.
- `Dispatchers.Default` 및 `Dispatchers.IO`와 같은 대부분의 디스패처는 멀티 스레드 디스패처이므로 여러 코루틴이 동일한 데이터를 병렬로 수정할 때 각별히 주의해야 한다.
- 코루틴을 만들 때 디스패처를 지정하거나 `withContext`를 사용하여 디스패처 간에 전환할 수 있다.
- 코루틴 컨텍스트에는 코루틴과 관련된 추가 정보가 포함되어 있다. 코루틴의 디스패처는 코루틴 컨텍스트의 일부이다.