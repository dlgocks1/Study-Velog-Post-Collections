# 11장 코투린 스코프 함수

여러개의 `HTTP`통신을 통해 데이터를 동시에 얻어야 하는 경우를 생각해봅시다.

중단 함수에서 중단 함수를 호출하는 것이 첫 번째 방법입니다. 문제는 작업이 동시에 진행되지 않는 다는 점입니다.

```kotlin
suspend fun getUserProfile(): UserProfileData {
	val user = getUserData() // 1초 후
    val notifications = getNotifications() // 1초 후
    
    return UserProfileData(
    	user, notifications
    )
}
```

하나의 엔드포인트에서 데이터를 얻는 데 1초씩 걸리기 때문에 함수는 총 2초가 걸리게 됩니다.

> 따라서 두개의 중단 함수를 동시에 실행하고자 한다면 `async`로 매핑해야 합니다.

---

### GlobalScope란?

`GlobalScope`는 그저 `EmptyCoroutineContext`를 가진 스코프일 뿐입니다. 

```kotlin
@DelicateCoroutinesApi
public object GlobalScope : CoroutineScope {
    override val coroutineContext: CoroutineContext
        get() = EmptyCoroutineContext
}
```

따라서 `GlobalScope`에서 `async`를 호출하면 부모 코루틴과 아무런 관계가 없습니다. 이 때 `async`코루틴은

- 취소될 수 없습니다. (구조화된 동시성 제공 X, 함수가 실행 중인 상태가 되므로 작업이 끝날 때까지 자원이 낭비)

- 부모로부터 스코프를 상속받지 않습니다.(항상 기본 디스패처에서 실행되며, 부모의 컨텍스트를 전혀 신경 쓰지 않습니다.)


이에 따라 메모리누수가 발생할 수 있으며, `CPU`를 낭비합니다. 

> 따라서 `GlobalScope.Async`를 활용하는 것은 자제해야 합니다. 

---

그렇다면 스코프를 인자로 넘기는 방법은 어떨까요??

```kotlin
suspend fun getUesrProfile(
	scope: CoroutineScope
) : UserProfileData {
	val user = scope.async { getUserData() }
    val notification scope.async { getNotification() }
    
    // ..
}
```

이 방식은 좀 더 나아보입니다.

특정 스코프에서의 작업을 강제하고자 한다면 해당 방식이 맞지만, 예상치 못한 문제가 발생할 수 있습니다. 

- `async`에서 예외가 발생하면 인자로 들어온 스코프가 모두 닫힘

- `cancel`메서드를 수행하는 경우 모든 코루틴이 최소되는 점

따라서 이를 해결하기위해 `coroutineScope`가 등장합니다.

### `coroutineScope`

이는 새로운 코루틴 스코프를 시작하는 중단 함수이며, 인자로 들어온 함수가 생성한 값을 반환합니다. (`let`과 비슷하게 동작)

특징으로써

- 생성한 새로운 코루틴이 끝날 때 까지 기존 코루틴을 중단합니다.
- 리시버 없이 곧바로 호출이 가능합니다.

```kotlin
fun main() = runBlocking {
	val a = coroutineScope {
    	delay(1000)
        10
    }
    println("게산 중..")
    val b = coroutineScope {
    	delay(1000)
        20
    }
    println(a)
    println(b)
}

// 1초 뒤
게산 중..
// 1초 뒤
10
20
```

`coroutineScope`는 부모에게서 코루틴 콘텍스트를 상속받지만, `Job`은 따로 오버라이딩합니다. 따라서 구조화된 동시성을 제공합니다.

- 부모로부터 컨텍스트를 상속받습니다.
- 자신의 작업이 끝내기 전까지 모든 자식을 기다립니다.
- 부모가 취소되면 자식들 모두 취소합니다.

따라서 다음과 같이 사용하는 것을 추천합니다.

```kotlin
suspend fun getUserProfile(): UserProfileData = coroutineScope {
	val user = aysnc { getUserData() }
 	val notifications = async { getNotifications() }
    
    UserProfileData(user, notifications)
}
```

> `coroutineScope` : 스코프를 하나 더 만들어 현재 코루틴을 중단시키고 지정된 작업을 수행합니다. 
> 
> 내부에서 오류가 발생해도 `coroutineScope`로 지정된 범위만 종료됩니다. (부모 코루틴(Job)에게 전달 X `try-catch`로 잡히는 에러) 


### 또다른 코루틴 스코프 함수

- `supervisoreScope`

`coroutineScope`와 비슷하지만, `Job`대신 `SupervisorJob`을 사용합니다.

- `withContext`

코루틴 컨텍스트를 바꿀 수 있는 `coroutineScope`입니다. `Job`을 오버라이딩 하되, 콘텍스트 또한 바꿀 수 있습니다. _(디스패쳐를 통해 쓰레드풀 변경또한 가능)_

- `withTimeout`

타임아웃이 있는 `coroutineScope`입니다.

---

알아두어야할 점은 `코루틴 빌더`와 `코루틴 스코프 함수`는 다르다는 점입니다.

|코루틴 빌더(runBlocking 제외)|코루틴 스코프 함수|
|---|---|
|launch, async, produce, actor|coroutineScope, superivsoreScope, withContext|
|CoroutineScope의 확장 함수|suspend function|
|CoroutineScope 리시버의 코루틴 컨텍스트 활용|부모의 컨티뉴에이션 객체가 가진 코루틴 컨텍스트 활용|
|예외는 Job을 통해 부모로 전파 됨|일반 함수와 같은 방식으로 예외를 던짐 (try-catch로 잡힘)|
|비동기인 코루틴을 시작함|코루틴 빌더로 만들어진 곳에서 스코프 코루틴을 시작함|

`runBlocking`은 함수를 정지하고 코루틴스코프를 만듭니다. 이는 해당 쓰레드또한 중지시키게 됩니다.


### withContext

`withContext`는 스코프의 컨텍스트를 변경할 수 있는 코루틴스코프입니다. 

따라서 아래 함수들은 동일합니다.

```kotlin
withContext(EmptyCoroutineContext) {}

coroutineScope {}

launch { }.join()

// 이는 스코프를 필요로 합니다! withcontext는 함수를 호추한 중단점에서 스코프를 들고 옵니다.
async { }.await() 
```

### supervisorScope

`supervisorScope`함수는 `SupervisorJob`을 오버라이딩 하기때문에 자식 코루틴이 예외를 던지더라도 취소되지 않습니다.

```kotlin
println("Before")

supervisorScope {
	launch {
    	delay(1000)
        throw Error()
    }
    
    launch {
    	delay(2000)
        println("Done")
    }
}

println("After")

// -----
Before
// 1초 후
예외가 발생
// 1초 후
Done
After
```

이는 서로 독립적인 작업을 시작하는 함수에서 주로 사용됩니다. 

`async`를 활용한다면 예외가 부모로 전파되는 걸 막는 것 외에 추가적인 예외처리가 필요합니다. `await`를 호출하고 `async` 코루틴이 예외로 끝나게 된다면 `await`는 예외를 다시 던지게 됩니다. 따라서 `async`에서 발생하는 예외를 전부 처리하려면 `try-catch`로 `await`호출을 래핑해야 합니다.

```kotlin
class ArticlesRepositoryImpl(
	private val articleRepositories: List<ArticleRepository>
) : ArticleRepository {
	
    overrdie suspend fun fetchArticles(): List<Article> = supervisorScope {
    	articleRepositories
        	.map { async { it.fetchArticless() } }
            .mapNotNull {
            	try {
                	it.await()
                } catch (e: Throwable) {
                	e.printStackTrace()
                    null
                }
            }
            .flatten()
            .sortedByDescending { it.publishedAt }
    }
}
```

>  Q. `supervisorScope` 대신 `withContext(SupervisorJob())`을 사용할 수 있나요??

아니요, `withContext(SupervisorJob())`을 활용하면 부모의 `Job`을 오버라이딩 하여 `SupervisorJob()`이 해당 잡의 부모가 됩니다. 따라서 자식 코루틴이 예외를 던진다면 다른 자식들 또한 취소 됩니다. 

> A. 자식 코루틴이 예외를 던지면 `withContext`또한 예외를 던지기 때문에 `SupervisorJob()`은 사실상 쓸모가 없게 됩니다. 

```kotlin
@Test
fun coroutineTest() = runBlocking {
    println("Before")

    withContext(SupervisorJob()) {
        launch {
            delay(1000)
            throw Error()
        }
        launch {
            delay(2000)
            println("Done")
        }
    }
    println("After")
}

Before
// 1초 후
[Error] ...
// 함수 종료
```

### withTimeout

이 함수는 인자로 실행하는 람다에 시간 제한이 있습니다. 시간제한이 지나면 `TimeoutCancellationException`을 던집니다. 이는 `CancellationException`의 하위타입입니다. 따라서 해당 코루틴만 취소가 되고 부모에게는 영향을 주지 않습니다.

- `runTest`내부에서 사용된다면 `withTimeout`은 가상 시간으로 작동하게 됩니다.
- 특정 함수의 실행 시간을 제어하기 위해 `runBlocking` 내부에서도 사용할 수 있습니다.

`withTimeoutOrNull`은 예외를 던지지 않습니다. 이는 타임아웃을 초과하면 람다식이 취소되고 `null`이 반한됩니다. 따라서 래핑 함수에서 걸리는 시간이 너무 길 때 무언가 잘못되었음을 알리는 용도로 사용합니다.

### 코루틴 스코프 함수 연결하기

서로 다른 코루틴 스코프 함수의 두 가지 기능이 모두 필요하다면 두 함수를 모두 실행시키면 됩니다.

```kotlin
withContext(Dispatcher.Default) {
	withTimeOutOrNull(1000) {
    	// ...
    }
}
```

### 추가적인 연산

코루틴 스코프의 주입을 통한 추가적인 연산은 자주 사용되는 방법입니다. 

> (특정 연산이 끝나지 않아도 될 때는 스코프를 주입하여 코루틴 스코프에서 기다리지 않을 수 있습니다.)

```kotlin
coroutineScope {
	val name = aysnc { repo.getName() }
    val friends = async { repo.getFriends() }
    val user = User(
    	name = name.await(),
        friends = friends.await()
    )
    
    view.show(user)
    anayticsScope.launch { repo.notifyProfileShown() }
}
```

> 로그 데이터의 전송 같은 경우는 굳이 해당 스코프에서 동작할 필요가 없습니다. 따라서 이는 다른 스코프에서 독립적인 작업으로 수행할 수 있습니다. (주입된 스코프에서의 연산은 끝날 때 까지 기다리지 않습니다.) 


## 요약

코루틴 스코프 함수는 모든 중단함수에서 사용할 수 있습니다. 코루틴 영역을 분리하거나, 특정 영역에서의 디스패쳐를 분리하는 등 다양한 역할을 수행할 수 있습니다.

# 12장 디스패처

코루틴 라이브러리가 제공하는 중요한 기능 중 하나는 코루틴이 실행되어야 할 쓰레드를 결정할 수 있다는 것입니다.

> 이는 RXJava의 스케줄러와 비슷한 개념입니다.


### Default Dispatcher

기본 설정되는 디스패처는 `Dispatcher.Default`입니다. 이 디스패쳐는 컴퓨터 `CPU`와 동일한 수의 쓰레드 풀을 가지고 있습니다. 따라서 CPU 집약적인 계산을 수행하며 블로킹이 일어나지 않는 환경에서는 최적의 쓰레드 수라고 할 수 있습니다.

```kotlin
@Test
fun main() = runTest {
	coroutineScope {
		repeat(1000) {
				launch(Dispatchers.Default) {
					List(1000) { Random.nextInt() }.maxOrNull()
					println("Thread : ${Thread.currentThread().name}")
				}
		}
	}
}
// 출력
...
Thread : DefaultDispatcher-worker-14 @coroutine#887
Thread : DefaultDispatcher-worker-3 @coroutine#1000
Thread : DefaultDispatcher-worker-12 @coroutine#989
Thread : DefaultDispatcher-worker-2 @coroutine#980
Thread : DefaultDispatcher-worker-9 @coroutine#978
Thread : DefaultDispatcher-worker-13 @coroutine#964

```

(필자의 컴퓨터엔 약 CPU코어가 16개 정도 있는 것 같다.)


### 디스패처 제한하기

비용이 많이 드는 작업이 `Dispatcher.Defaul`의 스레드를 다써버려서 같은 디스패처를 사용하는 코루틴이 실행될 기회를 제한하고 있다고 의심하는 상황을 떠올려봅시다.

이때 `limitedParallelism`를 활용하여 디스패처의 쓰레드 수를 제한할 수 있습니다.

```kotlin
@Test
fun main() = runTest {
	val dispatcher = Dispatchers.Default.limitedParallelism(5)
	coroutineScope {
		repeat(1000) {
				launch(dispatcher) {
					List(1000) { Random.nextInt() }.maxOrNull()
					println("Thread : ${Thread.currentThread().name}")
				}
		}
	}
}

// 출력
Thread : DefaultDispatcher-worker-5 @coroutine#78
Thread : DefaultDispatcher-worker-1 @coroutine#79
Thread : DefaultDispatcher-worker-4 @coroutine#80
Thread : DefaultDispatcher-worker-3 @coroutine#81
```

### IO 디스패처

> `IO 디스패처`는 블로킹 함수를 호출하는 경우처럼 `IO`블록이 있을 때 사용하기 위해 설계되었습니다.

```kotlin
@OptIn(ExperimentalTime::class)
@Test
fun main() = runTest {
	val time = measureTime {
		coroutineScope {
			repeat(1000) {
					launch(Dispatchers.IO) {
						delay(1000)
						println("Thread : ${Thread.currentThread().name}")
					}
			}
		}
	}
	println(time)
}

// 출력
...
Thread : DefaultDispatcher-worker-26 @coroutine#946
Thread : DefaultDispatcher-worker-56 @coroutine#947
Thread : DefaultDispatcher-worker-13 @coroutine#942
1.084738100s
```

디스패처 IO또한 쓰레드풀을 활용해 1000개가 넘는 작업을 쓰레드풀을 활용해 1.08초 이내로 처리함을 볼 수 있습니다.

> `IO`의 쓰레드풀은 max(64, CPU코어 수)로 제한됩니다. _(64코어 이상의 컴퓨터..?)_

#### IO디스패처와 Default 디스패처는 같은 쓰레드풀을 공유합니다.

```kotlin
coroutineScope(Dispatcher.Default) {
	coroutineScope(Dispatcher.IO) {
    	// Do Something
    }
}
```

쓰레드는 재사용되고 다시 배분될 필요가 없습니다.  따라서 위의 함수는 대부분은 같은 쓰레드 내부에서 실행이 됩니다. 하지만, 쓰레드 수가 `Dispatchers.Default`의 한계가 아닌 `Dispatcher.IO`의 한도로 적용이 됩니다. 

쓰레드의 한도는 독립적이기 때문에 한 디스패처가 다른 디스패처의 쓰레드를 고갈시키는 경우는 없습니다. 그래도 같은 디스패처 내부에서 한계가 있기 때문에 쓰레드가 고갈되는 상황이면 `limitedParallelism`을 활용하는 것을 권장합니다.

### 커스텀 쓰레드 풀을 사용하는 IO 디스패처

`limitedParalleism`은 디스패처에 쓰레드 수를 제한하지만, 디스패처마다 동작 과정이 약간 다릅니다.

- `Dispatcher.Default`에서 `limitedParalleism`은 예상한 것 처럼 활성 쓰레드를 제한합니다.

-  `Dispatcher.IO`의 `limitedParalleism`은 `Dispatchers.IO`와 독립적인 쓰레드풀을 만듭니다. 이는 아래의 소스와 비슷하게 동작합니다.

```kotlin
val dispatcher = Executors.newFixedThreadPool(1000).asCoroutineDispatcher()
```

하지만 위처럼 `Executors`를 활용해 쓰레드풀을 직접 만들면 이는 후에 `close`를 해주어야 합니다. _`Dispatcher.IO.limitedParalleism`은 안해줘도 되는 듯..?_

이렇게 디스패처의 쓰레드풀을 1개로 하여 경쟁상태를 해결할 수 있습니다. 스프링에서 거의 모든 백엔드 처리는 이렇게 진행됩니다. 이에 관해서는 14장에서 더 설명합니다.

### 프로젝트 룸의 가상 스레드 사용하기

`JVM` 플랫폼에선 프로젝트 룸이라는 새로운 기술을 발표했습니다. 이는 기존의 OS에서 돌아가는 쓰레드가 아니라 `JVM`위에서 돌아가는 가벼운 **가상 쓰레드**를 의미합니다.

코루틴에서는 `Dispatchers.IO`와 가상 스레드를 활용할 수 있습니다.

```kotlin
val LoomDispatcher = Executors
	.newVirtualThreadPerExecutor()
    .asCoroutineDispatcher()

launch(LoomDispatcher) {
	// ...
    Thread.Sleep(1000)
} 
```

> 디스패처 룸에서 작업을 수행한 결과 쓰레드에 대한 블로킹이 있을 때 기존의 쓰레드 보다 더 빠른 성능과 시간을 보여줍니다.


### 제한받지 않는 디스패처

`Dispatcher.Unconfined`는 쓰레드를 바꾸지 않는다는 점에서 이전 디스패처와 다릅니다.

이는 현재 콘텍스트의 쓰레드에서 바로 실행됩니다. 이는 실행되는 쓰레드에 대해 전혀 신경 쓰지 않아도 된다면 성능적인 관점에서 유용합니다.

_책에서는 Android의 `Main`쓰레드에서 실행되어 `ANR`을 일으킬 수 있다고 경고합니다. (안드로이드의 경우 Dispatchers.Main.immediate를 활용해 메인 쓰레드에서 실행될 시 즉시 쓰레드를 지정할 수 있습니다._


### 컨티뉴에이션 인터셉터

디스패쳐는 `ContinuationInterceptor`라는 코루틴 컨텍스트의 하위 객체입니다.

이는 코루틴이 중단되었을 때 `interceptContinuation` 메서드를 통해 컨티뉴에시션 객체를 수정하고 포장합니다. 

```kotlin
@SinceKotlin("1.3")
public interface ContinuationInterceptor : CoroutineContext.Element {

    companion object Key : CoroutineContext.Key<ContinuationInterceptor>

    public fun <T> interceptContinuation(continuation: Continuation<T>): Continuation<T>

    public fun releaseInterceptedContinuation(continuation: Continuation<*>) 
```

디스패처는 `interceptContinuation`함수를 활용해 `Continuation`을 `DispatchedContinuation`으로 변환합니다. 이는 특정 쓰레드 풀에서 실행되는 컨티뉴에이션을 의미합니다.

`DispatchedContinuation`은 `resume` 시점에 등록된 디스패처와 현재 컨텍스트의 디스패처를 비교하여 일치 하지 않으면 (스레드가 달라 스레드 전환이 필요하면) 해당 스레드로 디스패치 후 실행이 재개 되도록 합니다.


### 디스패처 성능 비교

아래는 디스패처 및 쓰레드에 따라 평균 실행 시간을 나타냅니다.

|-|중단|블로킹|CPU 집약적 연산|메모리 집약적인 연산|
|----|----|----|----|----|
|싱글 쓰레드|1,002|100,003|39,103|94,358|
|디폴트 디스패처(쓰레드 8개)|1,002|13,003|8,473|21,461|
|IO 디스패처(쓰레드 64개)|1,002|2,003|9,893|20,776|
|멀티 쓰레드|1,002|1,003|16,379|21,004|

위의 결과로 알 수 있는 것은

1. 중단을 하는건 쓰레드 수에 상관이 없다.

2. 블로킹할 경우에는 쓰레드 수가 많을수록 유리합니다 or `Dispatchers.IO`를 활용

3. CPU 집약적인 연산에는 `Dispatchers.Default`가 유리하다.

4. 메모리 집약적인 연산을 처리하고 있다면, 더 많은 쓰레드를 사용하는 것이 더 낫다.


## 요약

- `Dispatchers.Default`는 CPU 집약적 연산에 사용하기

- `Dispatchers.IO`는 블로킹 연산을 수행할 때 사용하기

- 병렬 처리를 제한한 `Dispatchers.IO`나 특정 쓰레드 풀을 사용하는 커스텀 디스패처는 블로킹 호출이 아주 많을 때 사용 가능

- 병렬 처리를 1로 제한하여 경쟁 상태를 임시로 해결할 수 있다.

- `Dispatcehrs.Unconfined`는 무지성 빠르게 실행하기 위해 사용됩니다.


# 13장 코루틴 스코프 만들기


### 백엔드에서 코루틴 만들기

스프링 부트는 컨트롤러 함수가 `suspend`로 선언되는 것을 허용합니다. 따라서 따로 스코프를 만들 필요는 없습니다. 만약 그래도 코루틴 스코프를 만들고자 한다면 다음과 같은 것이 필요합니다.

- 쓰레드 풀(또는 `Dispatchers.Default`)을 가진 커스텀 디스패처
- 각각의 코루틴을 독립적으로 만들어 주는 `SupervisorJob`
- 적절한 에러 로그를 남기고 처리하는 `CoroutineExceptionHandler`

```kotlin
@Configuration
class CoroutineScopeConfig {
	
    @Bean("coroutineDispatcher")
    fun coroutineDispatcehr(): CoroutineDispatcher = Dispatchers.IO.limitedParallelism(5)
    
    @Bean("coroutineExceptionHandler")
    fun coroutineExceptionHandler(): CoroutineExceptionHandler 
    	= CoroutineExceptionHandler { _, e -> 
        	logger.error(e)
        }
        
    @Bean
    fun coroutineScope(
    	coroutineDispatcher: CoroutineDispatcher,
        coroutineExceptionHandler: CoroutineExceptionHandler,
    ) = CoroutineScope(
    	SuperVisorJob() + coroutineDispatcher + coroutineExceptionHandler
    )
}
```

> 이렇게 싱글톤으로 생성된 스코프, 디스패처를 활용하여 매번 생성하지 않고 사용하는 것을 권장합니다.


### 추가적인 호출을 위한 스코프 만들기

추가적인 연산이 필요할 경우 메소드 내에서 생성하여 함수나 생성자의 인자를 통해 주입하는 방식을 사용합니다.

```kotlin
val analyticsScope = CoroutineScope(SupervisorJob())
```

## 요약

현업에서 코루틴을 활용할 때 스코프를 지정하여 사용하는 것은 중요합니다. 하지만 적절한 동기화와 테스트를 통해 적절한가를 측정해야 합니다.


# 14장 공유 상태로 인한 문제

멀티 쓰레딩, 멀티 프로세싱에서 빼놓을 수 없는 것이 공유 상태 및 경쟁 상태입니다. 서로 다른 두 쓰레드에서 하나의 값을 수정 및 조회할 때 서로다른 값이 출력되는 것을 의미합니다.

```kotlin
suspend fun main() {
	var i = 0
    coroutineScope {
    	repeat(1_000_000) {
        	launch {
            	i ++
            }
        }
    }
    
    println(i) // ~998323
}
```

코루틴에서도 이러한 상황은 빈번하게 일어나며 이를 막기 위해선 다음과 같은 방법이 있습니다.

### 동기화 블로킹

자바에서 널리 사용되는 도구인 `synchronized`블록이나 동기화된 컬렉션을 활용할 수 있습니다.

```kotlin
var counter = 0

fun main() = runBlocking {
	val lock = Any()
    repeat(1_000_000) {
        synchronized(rock) {
            coiunter ++
        }
    }
    println(counnter) // 1000000
}
```

이는 동작하긴 하지만 몇가지 문제점이 있습니다.

1. `synchronized` 블록 내부에서 중단 함수를 활용할 수 없다는 것입니다.

2. `synchronized` 블록 내부에서 본인의 차례를 기다릴 때 쓰레드를 블록킹 합니다. -> **⭐️성능 멸망 ⭐️**

이처럼 코루틴을 활용하며 스레드를 블로킹하는 것은 지양해야 합니다. 따라서 블로킹 없이 중단하거나 충돌을 회피하는 방식을 사용해야 합니다. 다른 방법을 살펴봅시다.


### 원자성

자바의 경우 간단하게 사용할 수 있는 원자성 값들이 존재합니다.

- `AtomicInteger`
- `AtomicBoolean`
- `AtomicReference`

이는 완벽하게 작동하지만 특정 타입 등에만 사용이 가능합니다. 또한 전체 연산에서 원자성이 보장되는 것은 아닙니다.

```kotlin
@Test
fun main(): Unit = runTest {
    val counter = AtomicInteger()
    repeat(1_000_000) {
        counter.set(counter.get() + 1)
    }
    println(counter.get()) // 1000000
}
```

단순한 변수에 대해 원자성을 보장하기 위해서는 사용하지만 복잡한 경우에는 다른 방식을 사용해야 합니다.

### 싱글스레드로 제한된 디스패처

공유상태를 해결하기 위한 가장 간단한 방법입니다. 싱글 스레드 디스패처를 사용하여 하나의 쓰레드에서만 코루틴이 돌아가게끔 하는 것입니다.

```kotlin
val dispatcher = Dispatchers.IO
	.limitedParallelism(1)
    
fun main() = runBlocking {
	var counter = 0
	repeat(1_000_000) {
    	counter++
    }
    println(counter) // 1000000
}
```

이는 사용하기 쉬우며 충돌을 방지할 수 있지만, 함수 전체에서 멀티스레딩의 이점을 누리지 못하는 문제가 있습니다. 

따라서 또다른 스코프와 코루틴 빌더를 활용하면 여러 개의 스레드에서 병렬로 시작할 수 있지만, 함수는 싱글스레드로 실행되게 할 수 있습니다. 이에 따라 성능저하가 발생할 수 있습니다.

> 이는 __파인 그레인드 스레드 한정__이라고 하며 크리티컬 섹션만 해당 디스패처로 래핑하는 것을 의미합니다.

```kotlin
val dispatcher = Dispatchers.IO
	.limitedParallelism(1)
    
suspend fun update() {
	withContext(dispatcher) {
    	counter ++
    }
}

fun main() = runBlocking {
	launch { 
    	// ...
	    update()
    }
    async {}
}
```

### 뮤텍스

뮤텍스는 쓰레드를 잠그는 것을 의미합니다. `kotlinx`에서 제공하는 뮤텍스틑 쓰레드를 잠그지 않습니다. 이는 코루틴을 중지시키는 것을 의미합니다.

```kotlin
@Test
fun main(): Unit = runBlocking {
    repeat(5) {
        launch {
            delayAndPrint()
        }
    }
}

val mutex = Mutex()
private suspend fun delayAndPrint() {
    mutex.lock()
    delay(1000)
    println("Done")
    mutex.unlock()
}

Done
// 1초 뒤
Done
// 1초 뒤
Done
// 1초 뒤
Done
// 1초 뒤
Done
```

하나의 코루틴만이 `lock`과 `unlock`사이에 있을 수 있습니다.

하지만, `lock`과, `unlock`을 직접 사용하는 것은 위험합니다. 두 함수 사이에서 예외가 발생할 경우 `lock`이 반환되지 않을 수 있으며, 다른 코루틴이 접근할 수 없습니다. (`Deadlock`문제)

대신 `lock`으로 시작해 `finally`에서 `unlock`을 수행하는 `withLock`함수를 사용하여 어떤 예외가 발생하더라도 언락이 되게 할 수 있습니다.

```kotlin
mutext.withLock {
	// do something
}
```

> `synchronized`와의 차이점은 뭐죠?

스레드를 블로킹하는 대신 코루틴을 중단시킨다는 것입니다. 이는 좀 더 안전하고 가벼운 방식입니다. 병렬 실행이 싱글스레드로 제한된 디스패처를 사용하는 것과 비교하면 뮤텍스가 좀 더 가벼우며, 좀 더 나은 성능을 가질 수 있습니다.

하지만 몇가지 주의점이 있습니다.

1. 뮤텍스의 락을 두번 통과할 수 없습니다.
	(열쇠가 문 안쪽에 있으면 같은 열쇠를 필요로 하는 다른 문을 통과할 수 없습니다.)
    
2. 코루틴이 중단되었을 때 뮤텍스를 풀 수 없습니다. 
	즉 내부에서 중단함수가 실행되면(정지되면) 해당 쓰레드를 아예 잠가버립니다.
    
    
> 따라서 뮤텍스를 활용할 땐 락을 두번 걸지 않고, 중단 함수를 호출하지 않도록 신경써야 합니다.

이에 따라 파인 그레인드 쓰레드 한정을 활용할 수 있습니다.

### 세마포어

세마오퍼는 둘 이상이 접근할 수 있도록 제어하는 방식입니다. 이는

- `acquire`
- `release`
- `withPermit`

함수를 가지고 있습니다.

```kotlin
suspend fun main() = coroutineScope {
	val semaphore = Semaphore(2)
    
    repeat(5) {
    	launch {
        	semaphore.withPermit {
            	delay(1000)
                print(it)
            }
        }
    }
}

// 01
// 1초 후
// 23
// 1초 후
// 4
```

세마포어를 활용하여 동시 요청을 처리하는 수를 제한할 때 사용할 수 있어 **처리율 제한 장치**를 구현할 때 도움이 됩니다. `limitParalliesm`과 비교하여 사용하기


## 요약

공유 상태를 변경할 때 활용 방식

1. 싱글 스레드로 제한된 디스패처 사용 (파인 그레인드 스레드 한정)
2. 뮤텍스
3. 세마포어
4. 원자값

등 방식 활용하기