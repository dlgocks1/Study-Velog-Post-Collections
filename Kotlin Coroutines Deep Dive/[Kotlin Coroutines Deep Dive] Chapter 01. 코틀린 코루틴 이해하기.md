# 1. 코틀린 코루틴을 배워야 하는 이유

 JVM 계열 라이브러리(RxJava, Reactor)가 있음에도 불구하고 왜 코루틴을 배워야할까요?
 

1. `Kotlin`이라는 언어기반으로 개발되어 멀티플랫폼을 지원합니다.

2. 쓰레드의 생성 비용, 컨텍스트 스위칭 비용을 줄일 수 있습니다.
	- 쓰레드는의 생명주기를 관리하는 것은 복잡합니다.
    
3. 콜백 패턴을 완화할 수있습니다.

	- 콜백 지옥은 취소를 구현하기 어렵고, 두 작업을 동시에 처리할 수 없습니다.

```kotlin
// 콜백 패턴의 예
fun showNews() {
	getConfig { conf ->
    	getNews(conf.newsId) { news ->
        	getUserInfo(news.userId) {
            	// TODO
            }
        }
    }
}

// 콜백 패턴 완화
suspend fun showNews() {
	val config = aysnc { getConfig() }
    val news = async { getNews(config.await().newsId) }
    val userInfo = aysnc { getUserInfo(news.await().userId) }
}
```

4. `RxJava`와 리액티브 스트림

`RxJava`, `Reactor`같은 라이브러리는 쓰레드 전환과 동시성 처리를 지원합니다.

```kotlin
fun onCreate() {
	dispoasables += getNewsFromApi()
    	.observeOn(AndroidSchedulers.mainThread())
        .map { news ->
        	news.sortedByDescending { it. publishedAt }
        }.subscribe {
        	view.showNews(it)
        }
}
```

이는 콜백보다는 좋은 방법이지만, 러닝 커브가 높고, 구현하기가 아주 복잡합니다.(오퍼레이터가 너무 복잡하고 `Pair` 등으로 묶고 관리하는 등)


### 왜 코틀린 코루틴의 사용할까?

- 코루틴은 특정 지점에서 멈추고 이후에 재개할 수 있습니다. 
	
    - 쓰레드와는 달리 멈추는 특정 지점을 유추할 수 있습니다.

- 코루틴을 활용하면 하나의 쓰레드에서 각각의 코루틴을 병렬로 실행로 실행할 수 있습니다.

> 책에서는 코루틴을 중단했다가 다시 실행할 수 있는 컴포넌트라고 칭합니다.

#### 백엔드에서의 코루틴 사용

`RxJava`와 달리 코루틴은 기존 `Spring`코드와 크게 변화가 없습니다. 하지만 멀티 쓰레드와는 달리 저렴합니다.

```kotlin
@OptIn(ExperimentalTime::class)
@Test
fun coroutineTest() = runTest {
	var value = 0
	val time = measureTimedValue {
		List(100_000) {
			async {
				++value
				delay(1000L)
			}
		}.awaitAll()
	}
	println(value)
	println(time.duration)
}

// 출력
100000
961.539600ms
```

```kotlin
@OptIn(ExperimentalTime::class)
@Test
fun threadTest() {
	var value = 0
    val time = measureTimedValue {
        repeat(100_000) {
        thread {
        	++value
        	Thread.sleep(1000L)
            }
		}
	}
	println(value)
	println(time.duration)
}

// 출력
100000
21.864589500s
```

### 요약

코틀린은 동시성 프로그래밍을 최대한 쉽고 저렴하게 구현할 수 있도록 도와줍니다.

# 2. 시퀀스 빌더

> 코틀린의 시퀀스는 `List`나 `Set`과 같은 컬렉션과 비슷한 개념이지만, 코틀린과 정지함수를 활용해 값을 지연(Lazy)처리 합니다.

- 요구되는 연산을 최소한으로 수행합니다.
- 무한 시퀀스가 존재합니다.
- 메모리 사용이 효율적입니다.
	
    - 리스트를 정렬하는 작업은 효율 X, 특정 몇개의 값을 뽑아 내거나, 하나 이상의 처리 단계를 거치는 경우 효율적
    
    
![](https://velog.velcdn.com/images/cksgodl/post/21d7d358-e13f-4e9b-9983-7cfe672d70b6/image.png)


`sequence`를 통해 빌드하거나 만들어 낼 수 있으며 `yield`로 값을 배출합니다.

```kotlin
@Test
fun main() = runTest {
	val seq = sequence {
		println("Gnerating 1")
		yield(1)
		println("Gnerating 2")
		yield(2)
		println("Gnerating 3")
		yield(3)
	}
	for (num in seq) {
		println(num)
	}
}

// 출력
Gnerating 1
1
Gnerating 2
2
Gnerating 3
3
```

시퀀스의 `yield`는 정지 함수로 구현되어 있습니다.

```kotlin
public abstract suspend fun yield(value: T)
```

> 따라서 `yield(1)`에서 1을 방출하고 함수가 정지됩니다. (코틀린의 특징 : 정지 시점을 예측할 수 있음) 이에 따라 `main`함수와 `sequence`제너레이터가 번갈아 가면서 정지, 수행 됩니다.

함수가 정지될 수 있는 이유는

```kotlin
override suspend fun yield(value: T) {
	nextValue = value
	state = State_Ready
    return suspendCoroutineUninterceptedOrReturn { c ->
		nextStep = c
		COROUTINE_SUSPENDED
	}
}
    
public suspend inline fun <T> suspendCoroutineUninterceptedOrReturn(crossinline block: (Continuation<T>) -> Any?): T {
    contract { callsInPlace(block, InvocationKind.EXACTLY_ONCE) }
    throw NotImplementedError("Implementation of suspendCoroutineUninterceptedOrReturn is intrinsic")
}
```

`suspendCoroutineUninterceptedOrReturn` 함수는 현재 코루틴의 `Continuation`을 획득하여 유저의 `block()`을 마저 수행합니다. 만약 `block`에서 `COROUTINE_SUSPENDED`를 반환한다면 이 코루틴은 반환됩니다.

- `suspendCoroutineUninterceptedOrReturn`함수는 취소가능한 모든 코루틴에서 많이 사용됩니다.

쓰레드를 이를 구현하기에는 막대한 비용이 듭니다. 코투린을 활용하면 더 빠르고 간단하게 정지가 가능합니다.


# 3. 중단은 어떻게 작동할까?

중단은 모든 코루틴의 필수적인 요소입니다. 코루틴은 중단될 때 `Continuation`을 반환합니다. `Continuation`은 게임의 체크포인트와 비슷합니다. 이를 통해 멈췄던 곳에서 코루틴을 실행할 수 있습니다.

코루틴은 어떤 자원도 사용하지 않고, 다른 쓰레드에서 시작할 수 있고, `Continuation` 객체는 직렬화와 역직렬화되며 다시 실행됩니다. 

---

### [How does method in coroutine block work in Kotlin?](https://stackoverflow.com/questions/67483210/how-does-method-in-coroutine-block-work-in-kotlin)

코틀린의 코루틴은 `stackful`과 `stackless`한 코루틴의 짬뽕입니다. `suspend` 함수를 실행시키면 일반 함수와 같이 자바 스택프레임에 쌓이지만, 정지하지 않고 함수가 종료된다면 일반 함수처럼 `JVM`에서 해당 스택을 `unwind`합니다. 

함수가 일시 중단되면 동작 과정이 약간 바뀝니다. 그 시점에서 자바 메서드가 반환되고 `JVM` 스택이 `unwind`됩니다. **스택이 사라지고, `콜 체인`이 구축되는 동안 `heap`메모리 위에 `Linked list Of Continuation`가 생성됩니다.** 모든 일시 중단 함수 호출은 스택메모리가 아니라 힙 위의 `Java 객체`로 `바이트코드` 수준에서 구현됩니다.

 `Continuation`을 재개하면 가장 앞쪽의 있는 함수를 호출하여 시작됩니다. 함수가 반환되기를 원할 때는 정상적인 방법으로 반환되지 않고 대신 호출자(`Caller`)의 `Continuation`을 `resume`합니다. 이는 호출자에게서도 반복되므로 코루틴의 일시 중단, 실행 로직이 구현될 수 있습니다.
 
 ![](https://velog.velcdn.com/images/cksgodl/post/4b250eef-9e19-4a94-afeb-61cfcfbaa598/image.png)

 
---

### 중단과 재개

`suspend`함수는 말 그대로 코루틴을 중단할 수 있는 함수입니다. 중단 함수는 코루틴 내부 또는 다른 `suspend` 함수에 의해 호출되어야 합니다.

```kotlin
@Test
fun main() = runTest {
	println("Before")
	someSuspendFunction() // 코루틴 스코프 내부에서 실행 가능
	println("After")
}
```


```kotlin
@Test
fun main() = runTest {
	println("Before")
	suspendCoroutine<Unit> {  }
	println("After")
}

// 출력
Before
...
```

위의 예제는 `After`은 출력되지 않으며, 코드는 실행된 상태로 유지됩니다.

> `suspendCoroutine`은 현재 `Continuation` 인스턴스를 가져오고 현재 실행 중인 코루틴을 suspend합니다.
> 
> 따라서 `Continuation.resume` 및 `Continuation.resume WithException`를 활용해 개발자가 직접 일시 코루틴의 재개 부분을 지정할 수 있습니다. 


```kotlin
@SinceKotlin("1.3")
@InlineOnly
public suspend inline fun <T> suspendCoroutine(crossinline block: (Continuation<T>) -> Unit): T {
    contract { callsInPlace(block, InvocationKind.EXACTLY_ONCE) }
    return suspendCoroutineUninterceptedOrReturn { c: Continuation<T> ->
        val safe = SafeContinuation(c.intercepted())
        block(safe)
        safe.getOrThrow()
    }
}
```

참고로 `suspendCoroutine`은 코루틴 스코프나 정지함수 내에서 실행이 가능하지만 내부는 코루틴으로 이루어져 있지 않습니다.

![](https://velog.velcdn.com/images/cksgodl/post/eacfb9e3-5081-4002-972c-0d32c8197fc9/image.png)

따라서 `I/O`가 필요 없는 곳, 굳이 `suspend`되지 않을 곳에서 `suspendCoroutine`을 활용하는 것을 권장합니다.

```kotlin
@Test
fun main() = runTest {
	println("Before")
	suspendCoroutine<Unit> { c : Continuation<Unit> ->
		println("This coroutines does not switch..")
        c.resumeWith(Result.success(Unit))
	}
	println("After")
}

// 출력
Before
This coroutines does not switch..
After
```

### 값으로 재개하기

책의 예제가 다음과 같이 제공하는데 마음에 안듬

```kotlin 
@Test
fun main() = runTest {
	println("Before")
	val user = suspendCoroutine<String> { c ->
		requestUser { // DB, Network I/O
			c.resumeWith(Result.success(it.name))
		}
	}
	println("After")
}
```

`requestUser`가 콜백을 제공할 때 까지 `I/O`를 제공할 때 까지 코루틴을 멈추고 값을 반환합니다.

### 함수가 아닌 코루틴을 중단시킵니다.

> 중단 함수는 코루틴이 아니고, 단지 코루틴을 중단할 수 있는 함수입니다.

```kotlin
@Test
fun main() = runTest {
	println("Before")
	suspendCoroutine {
		continuation = it
	}
	continuation?.resume(Unit)
	println("After")
}

// 출력
Before
```
해당 함수는 예상대로 종료되지 않습니다. `main()`이라는 함수가 아닌 `suspendCoroutine`을 중단시키기 때문입니다.

# 4. 코루틴의 실제 구현

- `suspend function`은 코틀린 컴파일러에 의해 상태 머신을 생성합니다.

- `Continuation` 객체는 상태를 나타내는 숫자와 로컬 데이터를 가지고 있습니다.

- 함수의 컨티뉴에이션 객체가 이 함수를 부르는 다른 함수의 컨티뉴에이션 객체를 장식합니다. 모든 컨티뉴에이션 객체는 실행을 재개하거나 재개된 함수를 완료할 떄 사용되는 콜 스택으로 사용됩니다.

### 코틀린의 `CSP`(Continuation Passing Style) 방식

```kotlin
suspend fun getUser(): String {
	return "해찬"
}

@Nullable
public final Object getUser(@NotNull Continuation $completion) {
	return "해찬";
}
```

코틀린 컴파일러는 컴파일 시 `Continuation`객체를 마지막 인자로 끼워 넣습니다.

또한 반환값이 `Object` (Kotlin의 `Any`)로 변환됨을 알 수 있습니다. 이는 해당 중단 함수가 결과 값(`"해찬"`)을 반환할 수도 있지만 중단됬을 때 마커인 `COROUTINE_SUSPENDED`를 반환할 수도 있기 때문입니다.

	
### 코틀린의 상태 머신

```kotlin
suspend fun myFunction() {
	println("Before")
    delay(1000) // 중단 가능 지점
    println("After")
}
```

컴파일러는 다음과 같은 코드를 아래와 같이 컴파일합니다.

```kotlin
fun myFunction(continuation: Continuation<Unit>): Any {
	val continuation = continuation as? MyFunctionContinuation ?: MyFunctionContinuation(continuation)
    
    if (continuation.label == 0) {
    	println("Before")
        // 중단 가능 지점
        if(delay(1000, continuation) == COROUTINE_SUSPENDED) {
        	return COROUTINE_SUSPENDED
        }
    }
    if (continuation.label == 1) {
    	println("After")
        return Unit
    }
    error("Impossible")
}

class MyFunctionContinuation(
	val completion: Continuation<Unit>
) {
	override val context: CoroutineContext
    	get() = completion.context
        
`	var label = 0
	var result: Result<Any>? = null
    
    override fun invokeSuspended(result: Result<Unit>) {
    	this.result = result
        val res = try {
        	val r = myFunction(this)
            if (r == COROUTINE_SUSPENDED) return
            Result.succes(r as Unit)
        } catch (e: Throwable) {
        	Result.failure(e)
        }
        completion.resumeWith(res)
    }
}
```

만약 값을 반환하는 중단함수가 있다면 모든 값들은 상태 머신에 저장됩니다.

```kotlin
suspend fun main(token: String) {
	val userId = getUserId(token)
    val uesrName = getUserName(token)
    // ...
}
```

```kotlin
fun myFunction(continuation: Continuation<Unit>): Any {
	val continuation = continuation as? MyFunctionContinuation ?: MyFunctionContinuation(continuation)
    
    if (continuation.label == 0) {
    	val userId = getUserId(token, continuation)
	    continuation.userId = userId
        continuation.label = 1
    }
    // ...
}

class MyFunctionContinuation(
	val completion: Continuation<Unit>
) {
        
`	var label = 0
	var result: Result<Any>? = null
 	var userId: String? = null // 특정 값을 반환..
	var userName: String? = null // 특정 값을 반환...
}
```

### 콜 스택

함수 a가 함수 b를 호출하면 일반적인 JVM은 스택 자료구조에 주소값을 저장하고 점프를 뜁니다. 코루틴의 경우는 컨텍스트 스위칭을 할 때 해당 주소값을 저장하는 스택이 없습니다. 코루틴의 경우는 `Linked List of Continuation` 객체가 콜 스택의 역할을 대신합니다. 

> [의견] : 쓰레드에 상관없이 코루틴이 실행될 때는 힙 메모리 위에 있는 `Continuation`객체를 가져다가 씁니다. (`CoroutineDispatcher`가 해당 쓰레드로 객체를 던짐
> 
> 코루틴이 가볍다고 의미하는 이유는 쓰레드의 TCB보다 `Continuation`의 크기가 작기 때문이 아닐까 생각됩니다.

`Linked list Continuation`객체라고 생각 -> `Continuation`객체는 중단이 되었을 떄의 상태(`label`)과 함수의 지역 변수, 파라미터 필드, 그리고 중단 함수를 호출한 함수가 재개될 위치정보를 가지고 있습니다. 

> `Continuation`은 한 객체가 다른 하나를 참조하고, 참조된 객체가 다른 `Continuation`을 참조하는 거대한 양파같은 구조입니다.

```kotlin
AContinuation(
	i = 4,
    label 1,
    completion = BContinuation(
    	i = 4,
        label = 1,
        completion = Continuation(
 			userId = 4,
            label = 2,
            completion = ...
		)		
    )
)
```

이러한 콜백은 `Continuation`의 `resume` or `resumeWith`을 활용하여 실행됩니다.

`Continuation` 구현체 실제 코드

```kotlin
internal abstract class BaseContinuationImpl(
    public val completion: Continuation<Any?>?
) : Continuation<Any?>, CoroutineStackFrame, Serializable {
 	
    public final override fun resumeWith(result: Result<Any?>) {
        var current = this
        var param = result
        while (true) {
            with(current) {
            	//  완료되지 않은 상태에서 Continuation을 재개하면 실패
                val completion = completion!!
                val outcome: Result<Any?> =
                    try {
                        val outcome = invokeSuspend(param)
                        if (outcome === COROUTINE_SUSPENDED) return
                        Result.success(outcome)
                    } catch (exception: Throwable) {
                        Result.failure(exception)
                    }
                releaseIntercepted() 
                // 상태 머신이 종료되는 중일 때 호출
                if (completion is BaseContinuationImpl) {
                    current = completion
                    param = outcome
                } else {
                	// 최상위 컨티뉴에이션 객체에 도달했을 때
                    completion.resumeWith(outcome)
                    return
                }
            }
        }
}
```

`resumeWith` 함수는 재귀를 통해 현재 코루틴을 재개하고, 필요한 경우 상위 코루틴으로 계속해서 재귀적으로 이동합니다.

### 중단 함수의 비용

- 함수를 상태로 나누는 것은 숫자를 비교하는 것만큼 쉬운 일

- 컨티뉴에이션 객체에 상태를 저장하는 것 또한 간단

멀티쓰레드보단 싸다.

# 언어 차원에서의 지원 vs 코루틴 라이브러리

코틀린 언어 차원에서는 코루틴을 최소한으로 지원하고, 좀 더 많은 코루틴을 활용하기 위해서는 라이브러리가 필수

|언어차원에서의 지원| kotlinx.coroutines 라이브러리|
|---|---|
|코틀린 기본 라이브러리에 포함 | 의존성 별도 추가 필요 |
| Continuation, suspendCoroutines 등 기본적인 것들 제공| launch, async 등 다양한 기능 제공|
|직접 사용하기 어렵다.| 직접 사용하기 쉽다.|



# 참고자료

https://www.youtube.com/watch?v=YrrUCSi72E8
https://stackoverflow.com/questions/67483210/how-does-method-in-coroutine-block-work-in-kotlin