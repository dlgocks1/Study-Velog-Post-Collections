# 26장 일반적인 사용 예제

책에서 필자는 대부분의 어플리케이션은 세 가지 계층으로 구분한다.

- 데이터/어뎁터 계층 
   - 데이터를 저장하거나 다른 시스템과 통신하는 것을 저장하는 계층 (코루틴을 지원하는 다른 라이브러리를 사용해야할 수도 있음)
- 도메인 계층 
   - 어플리케이션의 비즈니스 로직이 구현된 계층. 핵심 프로세스를 최적화하도록 코루틴을 활용해야 함
- 표현/API/UI 계층 
   - 어플리케이션으로 들어가는 진입점이라고 볼 수 있다. 코루틴을 시작하고 실행 결과를 처리한다.
   
각각의 계층에서 어떻게 코루틴을 활용하는지 알아보자.

## 데이터/어댑터 계층

> 레포지토리, 프로바이더, 어댑터 등 데이터 소스를 구현하는 계층

보통은 정지 함수를 지원하는 라이브러리인 `reative repository`, `retorift`등을 활용할 수 있지만 이를 지원하지 않을 수도 있다.

### 콜백 함수 활용

코루틴을 지원하지 않는 라이브러리라면 `suspendCacellableCoroutine`을 활용해 콜백 함수를 중단 함수로 변환할 수 있다. 이는

- 콜백 함수가 호출되면 `Continuation` 객체의 `resume`을 활용해 코루틴을 재개한다. 
- 콜백 함수가 취소 가능하다면, `invokeOnCancellation`람다식을 활용해 취소한다.

```kotlin
suspend fun requestNews() {
    return suspendCancellableCoroutine { conf ->
        requestNewsApi(
        	onSuccess = {
        		conf.resume(Result.Success(it.convert()))
            },
            onFailure = {
                conf.resume(Result.Failure(it.message))
			}
        ) 
        conf.invokeOnCancellation {
        	call.resume(null)
        }  
    }
}
```

위의 예제는 대표적으로 사용되는 `API`의 예제이다.

### 블로킹 함수

블로킹 함수를 어쩔 수 없이 사용해야 하는 라이브러리도 많이 볼 수 있다. (일반적인 중단함수에서는 절대로 블로킹 함수를 호출해서는 안 된다.)

`Dispatcher.Main`쓰레드가 멈추게되면 `ANR`을 내고, `Dispatcher.Default`의 스레드를 블로킹하면 프로세서를 효율적으로 사용하지 못하게 된다.

따라서 디스ㅐ쳐를 명시하지 않고 블로킹 함수를 호출하면 절대 안된다.

블로킹함수를 호출하고자 한다면 `withContext`를 사용해 디스패쳐를 명시해야 한다. 대부분의 경우 저장소를 구현할 때 `Dispatcher.IO`를 활용하면 된다.

> 만약 `Dispatcher.IO`의 쓰레드 개수보다 더 많은 요청을 하게 된다면 커스텀 디스패쳐를 활용해 새로운 쓰레드 풀을 만들면 된다.

```kotlin
withContext(Dispatcher.IO) {
	requestNewsApi() ?: Result.Failure
}
```

### 플로우로 감지하기

여러개의 값을 다루는 경우에는 `Flow`를 활용해야 한다. 

네트워크의 호출의 경우 `API`를 통해 하나의 값을 가져오는 경우는 중단 함수(`cancellableCoroutine`)을 활용하는 것이 좋지만, 웹소켓을 설정하고 메시지를 기다릴 때는 플로우를 활용해야 한다.

```kotlin
fun listenMessages(): Flow<List<Message>> = callbackFlow {
	socket.on("NewMessage") { args -> 
    	trySend(args.toMessage())
    }
    awaitClose()
}
```

플로우를 만들 떄는 `callbackFlow`또는 `channelFlow`를 사용한다. 또한 플로우 빌더의 끝에는 `awaitClose`를 무조건 넣어줘야 한다.

이러한 플로우의 `subscribe`, `publish` 디스패쳐를 조절하기 위해 `launchIn`, `flowOn`을 활용할 수 있다.

## 도메인 계층

도메인 계층에서는 비즈니스 로직을 구현하며, 사용 예, 서비스, 퍼사드 객체를 정의한다.

> 퍼사드 객체란?
>
> 클래스 라이브러리 같은 어떤 소프트웨어의 다른 커다란 코드 부분에 대한 간략화된 인터페이스를 제공하는 객체

비즈니스계층에서 연산을 처리하거나, 중단 함수를 노출시키는 것은 절대 안된다. 코루틴을 시작하는 것은 표현 층이 담당해야 하며, **도메인 계층에서는 코루틴 스코프함수를 활용해야 한다.(다른 코루틴 스코프를 열면 안된다.)**

실제 예를 살펴보면 다른 중단함수를 호출하는 중단 함수를 호출하는 것이 대부분이다.

```kotlin
class NetworkNewsService(
	private val newsRepo: NewsRepository,
    private val settings: SettingsRepository
) {
	suspend fun getNews(): List<News> = newsRepo
    	.getNews()
        .map { it.toDomainNews() }
        
	suspend fun getNewsSummary(): List<News> {
    	val type = settings.getNewsSummaryType()
        return newsRepo.getNewsSummary(type)
    }
}
```

### 동시 호출

두 개의 프로세스를 병렬로 실행하고자 한다면 함수 본체를 `coroutineScope`으로 래핑하고 내부에서 `async`빌더를 활용해 각 프로세스를 비동기로 실행해야 한다.

```kotlin
suspend fun produceCUrrentUser(): User = coroutineScope {
	val profile = async { repo.getProfile() }
    val friends = async { repo.getFirends() }
    User(profile.awaite(), friends.await())
}
```

또한 `async`함수와 `awaitAll`을 활용해 리스트의 각 원소를 비동기로 처리할 수 있따.

다양한 API리스트를 호출하는데 있어 동시성을 제한하고자 한다면, `flatMapMerge`의 동시성제어를 활용할 수 있다.

더해 예외처리도 생각해야한다. `coroutineScope`은 구조화된 동시성을 제공하기에 적절히 오류를 처리하고자 한다면, `supervisorScope`를 활용하는 것이 권장된다.

`withTimeout`이나 `withTimeoutOrNull`을 활용하여 시간을 제한할 수 있다.

### 플로우 변환

- 하나의 플로우를 여러 개의 코루틴이 감지하길 원한다면 `SharedFlow`로 변환하여 사용할 것
   - 코루틴스코프에서 `shareIn`을 사용하여 해당 스코프내에서 변환할 것
   
_안드로이드의 경우 코루틴 및 공유상태, 그리고 상태를 가진 플로우를 활용하는 것이 중요하지만 백엔드에서의 코루틴은 효율적인 데이터파이프라인의 구축에 좀 더 힘들 쓰자._

### 코루틴 스코프에 대하여

`Webflux`를 활용한 스프링 부트 프로젝트에서는 컨트롤러 함수에 `suspend`오퍼레이터를 추가하거나, 라우터로 등록함 함수를 `suspend`를 활용하여 시작할 수 있다.

코루틴 스코프를 제공하는데에 있어 안드로이드의 경우는 `lifecycle-viewmodel-ktx`가 있어서, 대부분의 경우 `viewModelScope` 또는 컴포넌트의 `lifecycleScope`를 활용하여 코루틴을 생성할 수 있다.

백엔드의 경우는 `org.springframework.boot:spring-boot-starter-webflux`에서 리액터 콘텍스트에서의 코루틴 컨텍스트로의 치환을 제공함으로 언제 어디서든 `suspend`오퍼레이터를 활용하여 코루틴를 시작할 수 있는 것이다.

치환 하는 방식에 대해서는 다음 블로그에서 잘 설명해주고 있다.

- [Webflux to Coroutine](https://huisam.tistory.com/entry/webflux-coroutine)

필요한 스코프가 없거나, 특정 스코프를 정의하여야할 때는 `Singleton`형태로 코루틴 디스패쳐를 정의하여 활용하는 것을 권장한다. (안드로이드 `Hilt`, 스프링 `Bean`등 활용)

```kotlin
val analyticsScope = CoroutineScope(SupervisoreJob())
```

보통 스코프를 활용할 때는 `SupervisorJob`을 활용하는 것이 일반적으로 통용되는 방식이다.

또한 스코프 객체를 정의할 때 특정 상황에서의 예외처리나 쓰레드 수를 정의할 수 있다.

```kotlin
private val exceptionHandler = COroutineExceptionHandler { _, throwable -> 
	// Do Something
} 

private val context = Dispatchers>Main + SupervisorJob() + exceptionHandler
```

### runblocking 활용하기

스코프 객체에서 코루틴을 시작하는 대신, 코루틴을 시작하고, 코루틴이 종료될 때 까지 현재 쓰레드를 블로킹하는 `runBlocking`함수가 있다.

책을 작성한 필자는 2가지 상황에서만 `runBlocking`을 활용하라고 권장한다.

1. `main`함수를 포장할 때
2. 테스트 함수를 포장할 때
   - `runTest`을 활용한다면 테스트 디스패쳐 및 스코프에서 시간 테스트 가능
   

> `Srping MVC`의 경우에는 코루틴 스코프를 열 수 있는 환경을 제공하지 않기에 비동기적인 처리가 필요하면 `runBlocking`을 통해 스코프를 열고 코루틴을 처리할 수 있다. -> `MVC`는 하나의 요청에 하나의 쓰레드를 활용 

`webFlux`를 활용한다면 코루틴 스코프르 자유자재로 사용할 수 있지만 러닝커브가 높고 뛰어난 성능 향상이 없을 수도 있다. -> `webFlux`의 경우 최적화 하기 위해 정말 많은 설정이 필요하고, 동작 원리를 이해해야 한다. 또한 대부분의 경우는 성능이 향상되는 것이 아닌 `처리량`이 늘어나는 형태로 동작하기 때문에 `ratency`자체는 `MVC`와 크게 다를 것이 없을 수 있다. (처리량이 늘어남에 따라 `ratency`는 달라질 수 있음)

`MVC`를 잘 활용하고 있다면 비동기 처리할 때 `runBlocking`을 활용해 쓰레드 스코프를 여는 것도 고려해도 좋을 것 같다.


### 플로우 활용하기

안드로이드의 경우는 플로우에 따른 처리, 뷰업데이트 등 `onEach`, `onCompletion`, `catch`등의 다양한 데이터 처리 오퍼레이터를 활용할 수 있지만, 백엔드의 경우 이를 활용할 기회는 많지 않다. 

> 어플리케이션 내부에서 데이터 파이프라인을 구성하는 것 보다는 카프카등 메시지 큐를 활용하는 방식이 더 확장적이고, 성능보장이 용이하기 떄문


## 요약

코루틴을 어떻게 활용할 지는 확실한 정답은 없다. 

`async`, `await`를 활용해 비동기 처리만 제대로 하여도 코루틴을 잘 사용할 수 있고, 각 팀마다 처한 상황에 따라 코루틴을 공부하고 적용하길 바란다.

# 27장 코루틴 활용 비법

필자가 겪은 코루틴 활용 꿀팁을 정리한다.

## 비법 1: 비동기 맵

하나의 패턴으로 정형화되어 있는 주제이지만, 자주 사용하는 패턴이라 함수로 추출하는 것이 좋다.

- 필자가 추출하혀 사용중인 `mapAsync`

```kotlin
suspend fun <T, R> List<T>.mapAsync(
    transformation: suspend (T) -> R
) = coroutineScope {
    this@mapAsync.map { async { transformation(it) } }.awaitAll()
}
```

이렇게 한번 잘 추출해 놓으면 다른 이들도 `map`, `awaitall`, `coroutineScope`를 따로 추상화하여 사용하지 않아도 된다. 또한 세마포어를 구현하여 처리율 제한을 할 수도 있다.

```kotlin
suspend fun <T, R> List<T>.mapAsync(
    concurrencyLimit: Int = Int.MAX_VALUE,
    transformation: suspend (T) -> R
) = coroutineScope {
    val semaphore = Semaphore(concurrencyLimit)
    this@mapAsync.map {
        async {
            semaphore.withPermit {
                transformation(it)
            }
        }
    }
}
```

_이 예제는 쓸만한 듯 하다. 나중에 다시와서 가져다 쓰기_

## 비법 2 : 지연 초기화 중단

필자는 중단 함수에서 사용할 수 있는 `Lazy` 델리게이트를 만들었다.

이것이 필요하게 된 이유는 아래와 같은 함수를 실행시키고자 이다.

```kotlin
suspend fun makeConnection(): Connection = TODO

val connection by lazy { makeConnection() } // COMPILE ERROR

Suspend function 'makeConnection' should be called only from a coroutine or another suspend function
```

`lazy`를 활용하고자 한다면 `suepndLazy`를 구현해야 한다. 

```kotlin
fun <T> suspendLazy(
    initializer: suspend () -> T
): suspend () -> T {

    var initializer: (suspend () -> T)? = initializer
    val mutex = Mutex()
    var holder: Any? = Any()

    return {
        if (initializer == null) holder as T
        else mutex.withLock {
            initializer?.let {
                holder = it()
                initializer = null
            }
            holder as T
        }
    }
}
```

어디선가 많이 본 형식이지 않는가? 이는 코틀린의 `by`를 통한 `Delegate` 소스를 거의 그대로 사용한 것 이다.

```kotlin
private class SynchronizedLazyImpl<out T>(initializer: () -> T, lock: Any? = null) : Lazy<T>, Serializable {
    private var initializer: (() -> T)? = initializer
    @Volatile private var _value: Any? = UNINITIALIZED_VALUE
    // final field is required to enable safe publication of constructed instance
    private val lock = lock ?: this

    override val value: T
        get() {
            val _v1 = _value
            if (_v1 !== UNINITIALIZED_VALUE) {
                @Suppress("UNCHECKED_CAST")
                return _v1 as T
            }

            return synchronized(lock) {
                val _v2 = _value
                if (_v2 !== UNINITIALIZED_VALUE) {
                    @Suppress("UNCHECKED_CAST") (_v2 as T)
                } else {
                    val typedValue = initializer!!()
                    _value = typedValue
                    initializer = null
                    typedValue
                }
            }
        }

    override fun isInitialized(): Boolean = _value !== UNINITIALIZED_VALUE

    override fun toString(): String = if (isInitialized()) value.toString() else "Lazy value not initialized yet."

    private fun writeReplace(): Any = InitializedLazyImpl(value)
}
```

위의 동기식 `delegate`와는 달리 `Mutex`를 활용하여 하나의 쓰레드만 해당 값에 접근할 수 있도록 하였고, `initializer`에 `null`을 대입함으로써 메모리 누수도 방지하였다.

실제 사용 예는 다음과 같다.

```kotlin
suspend fun makeConnection(): String {
    println("generate Connection")
    delay(1000L)
    return "Connection"
}

private val connection = suspendLazy { makeConnection() }

@Test
fun main() = runTest {
    println(connection())
    println(currentTime)
    println(connection())
    println(currentTime)
    println(connection())
    println(currentTime)
}

// 출력 결과
generate Connection
Connection
1000
Connection
1000
Connection
1000
```

`by` 델리게이터도 따로 구현할 수 있곘지만, 현재 상황에서는 다음과 같이 사용하는 것으로 만족

## 비법 3: 연결 재사용

`TCP`연결을 위해서는 3번 악수를 통해 연결을 해야한다. 하지만 공유플로우를 활용하면 초기 플로우가 해당 연결을 수행하고 다양한 코루틴으로 해당 값을 전파할 수 있다.

연결을 유지하는 것은 많은 비용이 들기 떄문에, 같은 데이터를 받을 때 두개의 연결을 수행할 필요도, 연결을 유지할 필요도 없다. 

- 아래의 예제는 위치 정보를 가져와 공유플로우로 활용하는 예제이다.

```kotlin
private val locations = locationDao.observeLocations()
	.shareIn(
    	scope = scope,
        started = SharingStared.WhileSubscribed(),
    )
    
fun observeLocations(): Flow<List<Location>> = locations
```

이는 데이터를 한번 가져오고 다양한 코루틴에게 전달하는데에 있어 용이한 예제이지만, 한번 커넥션을 생성하고 이를 고융하고자 한다면 이후 나오는 `ConnectionPool`클래스를 활용하는 것을 권장한다.


```kotlin
class ConnectionPool<K, V>(
    private val scope: CoroutineScope,
    private val builder: (K) -> Flow<V>
) {

    private val connections = mutableMapOf<K, Flow<V>>()

    fun getConnection(key: K): Flow<V> = synchronized(this) {
        connections.getOrPut(key) {
            builder(key).shareIn(
                scope = scope,
                started = SharingStarted.WhileSubscribed()
            )
        }
    }
}
```

아래의 예제에서는 쓰레드ID를 기반으로 코넥션 풀을 생성한다.

- 최소한 하나의 플로우가 연결을 필요로할 때 연결이 생성된다.
- `Flow`를 생성하는 방법만을 정의하기에 일반 함수에서 실행된다.(동기적)
- `Key`값을 기반으로 연결된 코넥션은 `map`형태로 저장되게 된다.

```kotlin
private val scope = CoroutineScope(SupervisorJob())
private val messageConnections = ConnectionPool(scope) { threadId: String ->
    // TODO 컨넥션 가져오기
}

fun getApiThread(threadId: String) = messageConnections.getConnection(threadId)
```

이외에도 `shareIn`의 확장 파라미터를 활용하여서 `replyCount`, `stopTimeout`,` replyExpiration` 등의 설정도 추가적으로 할 수 있다.

## 비법 4: 코루틴 경합

`설렉트`에서 본 것 처럼, 중단 가능한 프로세스 여러 개를 시작하고, 먼저 끝나는 것의 결과를 기다리려면, `raceOf`확장함수를 구현하여 사용할 수 있습니다.

> race상황이 필요한 곳? -> 광고, 대리운전 비딩 

```kotlin
suspend fun <T> raceOf(
    racer: suspend CoroutineScope.() -> T,
    vararg racers: suspend CoroutineScope.() -> T
): T = coroutineScope {
    select {
        (listOf(racer) + racers).forEach { racer ->
            async { racer() }.onAwait {
                coroutineContext.job.cancelChildren()
                it
            }
        }
    }
}
```

위의 함수는 다양한 프로세스를 실행하고 그 중 가장 빠른 값만 리턴한다.

## 비법 5 : 중단 가능한 프로세스 재시작하기

`API`콜이 실패했을 떄 재시도하여 값을 가져오는 것은 이상한 일이 아니다. 플로우에서는  재시작할 수 있는 여러 오퍼레이터를 제공한다. (`retry`, `retryWhen` 등등) 

필자는 이런 재시작 로직 중 다음과 같은 것을 추가하고자 한다.

- 재시도 횟수와 에외 종류에 따라 프로세스가 재시도되는 조건
- 재시도 사이의 시간 간격 증가
- 예외와 그 정보 로깅

재시도를할 때 사용하는 대표적인 알고리즘 중 하나는 `지수 백오프`로 재시도할 때마다 백오프 지연 시간을 늘리는 것이다. 

```kotlin
suspend fun <T> retryWithExponentialBackoff(
    maxRetries: Int,
    initialDelayMillis: Long = 100,
    maxDelayMillis: Long = 1000,
    factor: Double = 2.0,
    block: suspend () -> T
): T {
    var currentDelay = initialDelayMillis
    repeat(maxRetries) { retryCount ->
        try {
            return block()
        } catch (e: Exception) {
            if (retryCount == maxRetries - 1) {
                throw e // If we reached max retries, propagate the exception.
            }
            // Exponential backoff with a maximum delay.
            delay(currentDelay)
            currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelayMillis)
        }
    }
    throw IllegalStateException("Unreachable") // This line should never be reached.
}

@Test
fun main() = runTest {
    try {
        val result = retryWithExponentialBackoff(10) {
            // Simulate some operation that might fail.
            println("Attempting operation... Time : ${currentCoroutineContext()}")
            if (Math.random() < 0.8) {
                throw RuntimeException("Operation failed")
            }
            "Operation succeeded"
        }
        println("Result: $result")
    } catch (e: Exception) {
        println("All retries failed. Exception: $e")
    }
}

// 출력 결과
Attempting operation... Time : [RunningInRunTest, kotlinx.coroutines.test.TestCoroutineScheduler@327bcebd, kotlinx.coroutines.test.TestScopeKt$TestScope$$inlined$CoroutineExceptionHandler$1@19c65cdc, TestScope[test started], StandardTestDispatcher[scheduler=kotlinx.coroutines.test.TestCoroutineScheduler@327bcebd]]
Attempting operation... Time : [RunningInRunTest, kotlinx.coroutines.test.TestCoroutineScheduler@327bcebd, kotlinx.coroutines.test.TestScopeKt$TestScope$$inlined$CoroutineExceptionHandler$1@19c65cdc, TestScope[test started], StandardTestDispatcher[scheduler=kotlinx.coroutines.test.TestCoroutineScheduler@327bcebd]]
Attempting operation... Time : [RunningInRunTest, kotlinx.coroutines.test.TestCoroutineScheduler@327bcebd, kotlinx.coroutines.test.TestScopeKt$TestScope$$inlined$CoroutineExceptionHandler$1@19c65cdc, TestScope[test started], StandardTestDispatcher[scheduler=kotlinx.coroutines.test.TestCoroutineScheduler@327bcebd]]
Attempting operation... Time : [RunningInRunTest, kotlinx.coroutines.test.TestCoroutineScheduler@327bcebd, kotlinx.coroutines.test.TestScopeKt$TestScope$$inlined$CoroutineExceptionHandler$1@19c65cdc, TestScope[test started], StandardTestDispatcher[scheduler=kotlinx.coroutines.test.TestCoroutineScheduler@327bcebd]]
Attempting operation... Time : [RunningInRunTest, kotlinx.coroutines.test.TestCoroutineScheduler@327bcebd, kotlinx.coroutines.test.TestScopeKt$TestScope$$inlined$CoroutineExceptionHandler$1@19c65cdc, TestScope[test started], StandardTestDispatcher[scheduler=kotlinx.coroutines.test.TestCoroutineScheduler@327bcebd]]
Result: Operation succeeded
```

이외에도 `retry`, `retryWhen`으르 활용하여 원하는 로직을 추가적으로 구현하도록 하자.


## 요약

필자가 사용하는 예제 소스를 몇개 가져다가 응용하여 사용하는 것을 권장


# 29장 코루틴을 시작하는 것과 중단 함수 중 어떤 것이 나을까?

여러개의 동시성 작업을 수행할 때 사용할 수 있는 함수는 두 종류가 있다.

- 코루틴 스코프 객체에서 실행되는 일반 함수

```kotlin
fun sendNotifications(
	notifications: List<Notification>
) {
	for (n in notifications) {
    	notificationScope.launch {
        	client.send(n)
        }
    }
}
```

- 중단 함수

```kotlin
suspend fun sendNotifications(
	notifications: List<Notification>
) = supervisoreScope {
	for (n in notifications) {
    	launch {
        	client.send(n)
        }
    }
}
```

두 가지 방식은 비슷하지만, 다르게 동작한다.

- 일반 함수가 코루틴을 시작하려면 스코프 객체를 외부에서 받아야 한다. -> 따라서 일반함수는 코루틴이 완료되는 것을 기다리지 않는다. (바로 끝남)
   - 해당 작업은 스코프 내에서 처리됨 따라서 함수를 취소하고자 한다면 스코프를 취소해야 함

- 중단 함수의 경우는 모든 코루틴이 끝날 때 까지 중단 함수가 끝나지 않음
   - 시작한 코루틴과 관계를 유지
   

일반적인 상황에서 선택할 수 있다면 후자의 중단함수를 선택하는 것이 낫다.  하지만 특정 케이스에서는 두 종류의 함수를 혼합해서 사용해야 한다.

> 예를 들어 특정 결과값을 반환하되 해당 이벤트로그를 카프카로 보내야 하는 경우는 따로 스코프를 두어 이벤트로그가 전송되기 까지 기다리지 않아도 된다.


# 30장 모범 사례

## async 코루틴 빌더 뒤에 await()를 호출하지 말 것


```kotlin
suspend fun getUser(): User = coroutineScope {
	val user = async { repo.getUser() }.await()
	user.toUser()
}
```

스코프가 필요하다면 `coroutineScope`를, 컨텍스트를 지정해야 한다면 `withContext`를 활용할 것

또한 비동기 작업을 수행할 때 마지막 잡업을 제외한 모든 작업이 `async`를 사용해야 한다. 가독성을 위해 모든 작업에 `async`를 사용하자.

## withContext(EmptyCoroutineContext) 대신 coroutineScope를 사용하세요

`coroutineScope`와  `withContext`의 차이는 컨텍스트를 설정할 수 있다는 것이다. `withContext(EmptyCoroutineContext)`는 아무런 의미도 없음으로 `coroutineScope`를 사용하라

## awaitAll을 사용하기

`map { it.await() }`는 작업을 하나씩 기다리므로 `awaitAll()`을 사용해야 한다.

## 중단 함수는 어떤 쓰레드에서 호출되더라도 안전해야 한다.

중단 함수가 블로킹 함수를 호출할 때는 `Dispatchers.IO`나 블로킹에 사용하기로 설계된 커스텀 디스패쳐를 사용해야 한다. 함수를 호출할 때 디스패처를 설정할 필요가 없도록 `withContext`로 디스패처를 설정해야 한다.

`flow`를 반환하는 함수는 `flowOn`을 통해 디스패처를 지정해야 한다.(중복된 디스패쳐는 가장 처음 오퍼레이터만 적용되며, 위쪽 소스에만 디스패쳐가 적용된다.)

또한 디스패쳐는 싱글톤으로 등록하여 사용할 것을 권장한다.

## Dispatchers.Main 대신 Dispatchers.Main.immediate를 사용하라

`Dispatcehrs.Main>immediate`는 필요한 경우에만 코루틴을 재분배한다. 보통의 경우에는 이를 활용하라. 

## 무거운 함수에서는 yield를 사용하라

중단 가능하지 않으면서 CPU를 집약적이거나, 시간 집약적인 연산들 중간 중간에는 yeidl를 사용하는 것을 권장한다.

```kotlin
suspend fun cpuIntensiveOperations() = withContext(Dispatchers.Default) {
	cpuIntensiveOperation1()
    yield()
	cpuIntensiveOperation2()
    yield()
	cpuIntensiveOperation3()
}
```

또한 코루틴 빌더 내부에서 `ensureActive`를 사용할 수도 있다.

## 중단 함수는 자식 코루틴이 완료되는 걸 기다린다.

`coroutineScope`, `withContext`와 같은 코루틴 스코프 함수는 스코프 내의 코루틴이 완료될 때까지 부모 코루틴을 중단시킨다. 그 결과, 부모 코루틴은 부모 코루틴이 시작한 모든 코루틴을 기다리게 된다.

```kotlin
suspend fun longTask() = coroutineScope {
	launch {
    	delay(1000)
        println("Done 1")
    }
    
    launch {
    	delay(2000)
        println("Done 2")
    }
}


@Test
fun main() = runTest {
	println("Before")
	longTask()
	println("After")
}

// 출력 결과
Before
(1초 후)
Done 1
(2초 후)
Done 2
After
```

코루틴 스코프 함수의 마지막 코드에 `launch`를 사용하면 `launch`를 제거해도 동일하게 작동한다.

```kotlin
suspend fun getUser() = coroutineScope {
	// Do Something
    
    launch { sendEvent() } // 이렇게 구현 X
}
```

> 중단 함수는 함수 내에서 시작한 코루틴이 완료되는걸 기다린다.
>
> 외부 스코프를 사용하면 이 원칙을 위배할 수 있으며, 합당한 이유가 있을 경우에만 사용할 것


## Job은 상속되지 않으며, 부모 관계를 위해 사용된다.

> Job컨텍스트는 유일하게 상속되지 않은 컨텍스트이다.

Job은 부모 관계를 정립하기 위해 사용된다. 따라서 다음과 같은 예제는 무의미하다.

```kotlin
fun main() = runBlocking(SupervisorJob()) {
	launch {
    	delay(1000)
        throw Error()
    }
    launch {
    	delay(2000)
		println("Done")
    }
}
```

코루틴은 각자의 잡을 가지고 있으며, 잡을 자식 코루틴으로 전달하고, 전달된 잡은 자식 코루틴에서 잡의 부모가 된다. 

위의 예제를 구현하고자 한다면 자식 코루틴에서 발생한 예외를 무시하는 `supervisorScope`를 활용하라.

## 구조화된 동시성을 깨뜨리지 마라.

외부의 잡이나 스코프를 사용하면 구조화된 동시성이 깨지며, 코루틴이 취소되지 않아 메모리 누수가 발생할 수 있다. 

```kotlin
// 이렇게 사용하지 마세요.
suspend fun getPosts() = withContext(Job()) {
	// Do something
}
```

## CoroutineScope를 만들 때는 SupervisorJob을 사용하라.

스코프를 만들 때 스코프에서 시작한 코루틴에서 예외가 발생하면 모든 스코프에 예외가 전파된다. 따라서 `SupervisorJob`을 사용하거나, `supervisorScope`를 활용하라.

## 스코프의 자식은 취소할 수 있다.

스코프가 취소되고 나면, 취소된 스코프를 다시 사용할 수 없다. 

스코프에서 시작한 모든 작업을 취소하지만 스코프를 액티브 상태로 유지하고 싶은 경우, 스코프의 자식을 취소하면 된다. 스코프를 유지하는 것은 아무런 비용이 들지 않는다.

```kotlin
// 자식들 모두 취소 (스코프 유지)
scope.coroutineContext.cancelChildren()

// 스코프 취소
scope.cancle()
```
안드로이드에서는 `ktx`라이브러리가 인지하는 코루틴 스코프를 활용하라. (`viewModelScope`, `lifecycleScope`)

## 스코프를 사용하기 전에, 어떤 조건에서 취소가 되는지 알아야 한다.

안드로이드의 경우는 뷰의 라이프싸이클에 연동하여 뷰모델스코프를 제공한다. 이는 뷰가 사라졌을 때 코루틴도 종료되는 명확한 종료시점을 제공한다.

`GlobalScope`는 절대 취소되지 않는다. 따라서 `GlobalScope`는 사용하지 않는 것을 권장한다. `GlobalScope`는 관계가 없으며, 취소도 할 수 없고, 테스트를 위해 오버라이딩하는 것도 힘들다. 

```kotlin
val scope = CoroutineScope(SupervisorJob())

fun main() = runTest {
	// 이러지 마세요.
	GloablScope.launch { task() }
		
	// 이렇게 구현하세요.
    scope.launch { task() }
}
```

위의 예제와 같이 차라리 `SupervisorJob`만 컨텍스트로 가지는 간단한 스코프를 만들어라.

## 스코프를 만들 때를 제외하고 `Job`빌더는 그냥 사용하지 마라.

`Job`함수를 활용해 잡을 생성하면 구조화된 동시성이 깨지게 된다.

이에 따라 자식 코루틴과 부모코루틴의 연결이 끊어지며, 자식 코루틴 일부가 완료되더라도, 부모 또한 완료되는 것은 아니다.

`CoroutineScope(SupervisorJob())`이외의 상황에서는 `Job()`빌더를 그냥 사용하지 마라.

## Flow를 반환하는 함수가 중단 함수가 되어서는 안된다.

플로우는 `collect`함수를 사용해 시작되는 특정 프로세스의 내용을 나타낸다. 따라서 `flow`의 프로세스는 중단함수일 필요가 없다. 

필자는 직관적이지 않은점과, 플로우를 반환하는 함수는 전체 프로세스를 처리하도록 하는것이 일반적인 점을 들고 있다.

```kotlin
fun observeNewsServices(): Flow<News> = flow {
	emitAll(fetchNewsServices().asFlow().flatMapMerge { it.observe() }
}

fun main() {
	observeNewsServices().collect {
    	println(it)
    }
}
```

## 하나의 값만 필요하다면 플로우 대신 중단 함수를 사용하라.

단 하나의 값만 반환한다면 플로우를 사용하지 말 것 `Flow`타입은 내보내는 데이터 흐름을 나타내도록 설계되었다. 

```kotlin
interface UserRepository {
	fun getUser(): Flow<User> // X
	suspend fun getUser(): User // O
}
```

이는 어디서든 플로우를 활용하는 팀에 들어간다면, 팀의 정책에 따르는 것이 좋지만 가능한 경우에 하나의 값만 얻기 위한 곳에는 플로우를 사용하지 않는 것이 좋다. 

더 효율적이고, 간단하고, 쉽게 이해할 수 있는 코드를 만들기 위해서다.

위의 사례는 언제나 옳은 것은 아니며 알잘딱깔센하라.


