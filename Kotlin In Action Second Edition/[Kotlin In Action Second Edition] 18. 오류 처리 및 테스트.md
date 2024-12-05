## 18.1 코루틴 내부에서 발생하는 오류 처리하기

다른 `Kotlin` 코드와 마찬가지로 일시 중단 함수 또는 코루틴 빌더 내부에서 작성된 코드는 예외를 발생시킬 수 있다. 이러한 예외를 처리하기 위해 `try-catch`를 사용하여 런치 또는 비동기 호출을 서라운드하고 싶을 수 있습니다. 그러나 이는 작동하지 않는다.

코루틴 빌더 함수는 실행할 새로운 코루틴을 생성한다는 점을 기억하라. 이러한 새 코루틴 에서 던져진 예외는 캐치 블록에서 잡히지 않는다.(예를 들어 새로 생성된 스레드에서 던져진 예외가 스레드를 생성하는 코드에서 잡히지 않는 것과 마찬가지)

```kotlin
import kotlinx.coroutines.*

fun main(): Unit = runBlocking {
	try {
    	launch {
        	throw UnsupportedOperationException("Ouch!")
		}
	} catch (u: UnsupportedOperationException) {
		println("Handled $u") // 호출되지않음
	}
}

// 예외가 잡히지 않고 던져짐
// Exception in thread "main" java.lang.UnsupportedOperationException: Ouch!
//  at MyExampleKt$main$1$1.invokeSuspend(MyExample.kt:6)
//       ...
```

위의 코드는 오류가 잡히지 않는다. 이를 수정하기 위해서는 `try catch`를 `launch`문 내부로 이동해야 한다.

```kotlin
import kotlinx.coroutines.*

fun main(): Unit = runBlocking {
    launch {
        try {
            throw UnsupportedOperationException("Ouch!")
        } catch (u: UnsupportedOperationException) {
            println("Handled $u")
		}
	}
}
// 예외가 잡힘
// Handled java.lang.UnsupportedOperationException: Ouch!
```

---

`async`를 사용하여 만든 코루틴이 예외를 던지는 경우, 그 결과에서 `await`을 호출하면 이예외가 다시 던져진다.

```kotlin
import kotlinx.coroutines.*

fun main(): Unit = runBlocking {
    val myDeferredInt: Deferred<Int> = async {
        throw UnsupportedOperationException("Ouch!")
    }
    try {
        val i: Int = myDeferredInt.await()
        println(i)
    } catch (u: UnsupportedOperationException) {
        println("Handled: $u")
	}
}

Handled: java.lang.UnsupportedOperationException: Ouch!
Exception in thread "main" java.lang.UnsupportedOperationException: Ouch!
    at MyExampleKt$main$1$myDeferred$1.invokeSuspend(MyExample.kt:6)
...
```

원래 `myDeferredInt.await()`가 정수 값을 반환할 것으로 예상했지만, 이 값을 계산하는 비동기 코루틴 내부에서 예외가 발생했기 때문에 `await()`은 예외를 다시 던진다. 이 예외는 `try-catch` 블록으로 `await()`을 둘러싸서 잡는다.

위 예제를 실행하면 `await()`의 `try-catch`에 의해 예외가 잡힌 것을 관찰할 수 있다. 하지만 신기하게도 오류 콘솔에도 동시에 출력된다:

그 이유는 `await`이 예외를 다시 던지지만 원래 예외도 관찰하기 때문이다. 이 예제에서 비동기는 `runBlocking`을 사용하여 생성된 상위 코루틴으로 예외를 전파하고, 예외를 오류 콘솔에 출력하고 프로그램을 크래시한다. 자식 코루틴은 항상 잡히지 않은 예외를 부모에게 전파한다. 즉, 이 예외를 처리하는 것은 부모의 책임이 된다.

## 18.2 Kotlin 코루틴의 오류 전파

구조적 동시성 패러다임은 자식 코루틴이 잡히지 않은 예외를 던질 때 부모 코루틴에 일어나는 일에 관한 것이다. 자식 간에 작업을 나누는 개념적 방법에는 두 가지가 있으며, 따라서 자식의 오류를 처리하는 방법도 두 가지가 있다.

- 코루틴을 사용하여 작업을 동시에 하는 경우 : 한 자식이 실패하면 더 이상 최종 결과를 얻을 수 없다. 부모 코루틴도 예외와 함께 완료되며, 더이상 필요하지 않은 결과를 생성하지 않기 위해 아직 작업 중인 다른 자식 코루틴도 취소된다. 즉, 한 자식의 실패는 부모의 실패로 이어진다.
- 두 번째 경우는 한 자녀의 실패가 일반적인 실패로 이어지지 않는 경우이다. 한 자식의 실패가를 부모가 처리해야 하고 전체 시스템 충돌로 이어지지 않아야 할 때 부모가 자식의 실행을 감독해야 한다고 말한다.
  일반적으로 이러한 감독 코루틴은 코루틴 계층 구조의 최상위에 위치한다. 이 시나리오에서는 자식 중 하나가 실패해도 부모가 실패하지 않는다.

`Kotlin` 코루틴에서 부모 코루틴이 자식 코루틴을 처리하는 방식은 부모 코루틴에 일반 `Job`(자식 실패가 일반 실패로 이어짐)이 있는지 또는 `SupervisorJob`(부모가 자식을 감독함)이 코루틴 컨텍스트에 있는지 여부에 따라 달라진다.

### 18.2.1 코루틴은 한 자녀가 실패하면 모든 자녀를 취소한다.

이전장에서 내부적으로 코루틴 간의 부모-자식 계층 구조 가 `Job` 객체를 통해 구축된다는 것을 배웠다. 따라서 코루틴이 `SupervisorJob`으로 명시적으로 생성되어 슈퍼바이저가 되지 않는 경우, 자식 코루틴 중 하나에서 잡히지 않은 예외가 처리되는 기본 방식은 예외로 부모 코루틴도 종료되는 것이다.

실패한 자식 코루틴은 그 실패를 부모에게 전파한다. 그러면 부모는 다음을 수행한다.

- 불필요한 작업을 피하기 위해 다른 모든 자식을 취소한다.
- 동일한 예외를 제외하고 자체적으로 실행을 완료한다.
- 예외를 계층 구조 위로 전파한다.

코루틴은 자체적으로 복구할 방법을 모르는 문제 가 발생하면 공통 결과를 더 이상 합리적으로 계산할 수 없다고 가정한다. 이러한 상황에서 형제 코루틴이 쓸모없는 계산을 계속하거나 리소스를 계속 보유하는 것을 방지하기 위해 형제 코루틴은 취소된다. 이렇게 하면 불필요한 작업을 피하고 리 소스를 해제할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/feb31214-a6a9-46cb-a640-cc37a1114445/image.png)

```kotlin
import kotlinx.coroutines.*
import kotlin.time.Duration.Companion.milliseconds
import kotlin.time.Duration.Companion.seconds

fun main(): Unit = runBlocking {
    launch {
        try {
            while (true) {
                println("Heartbeat!")
                delay(500.milliseconds)
			}
		} catch (e: Exception) {
        	println("Heartbeat terminated: $e")
				throw e
		}
	}
	launch {
    	delay(1.seconds)
        throw UnsupportedOperationException("Ow!")
	}
}

Heartbeat!
Heartbeat!
Heartbeat terminated: kotlinx.coroutines.JobCancellationException: Parent job
              is Cancelling; job=BlockingCoroutine{Cancelling}@1517365b
        Exception in thread "main" java.lang.UnsupportedOperationException: Ow!
```

기본적으로 이 예제의 `runBlocking`을 포함한 모든 코루틴 빌더는 규칙적인 비감독자 코루틴을 생성한다. 따라서 하나의 코루틴이 잡히지 않은 예외로 종료되면 다른 하위 코루틴도 취소된다.

### 18.2.2 구조적 동시성은 코루틴 경계를 넘어 던져진 예외에만 영향을 미친다.

형제 코루틴을 취소하고 예외를 코루틴 계층 구조 위로 전파하는 이 동작은 코루틴 경계를 넘어서는 잡히지 않은 예외에만 영향을 미친다.

따라서 이 동작을 처리하지 않 는 가장 쉬운 방법은 애초에 이러한 경계를 넘어 예외를 던지지 않는 것이다. 단일 코루틴(예: 일시 중단 함수 본문 내부)에 국한된 `try-catch` 블록은 예상한 대로 정확하게 동작한다.

```kotlin
 import kotlinx.coroutines.*
 import kotlin.time.Duration.Companion.milliseconds
 import kotlin.time.Duration.Companion.seconds

 fun main(): Unit = runBlocking {
    launch {
        try {
            while (true) {
                println("Heartbeat!")
                delay(500.milliseconds)
            }
        } catch (e: Exception) {
            println("Heartbeat terminated: $e")
            throw e
		}
	}

    launch {
    	try {
            delay(1.seconds)
            throw UnsupportedOperationException("Ow!")
        } catch(u: UnsupportedOperationException) {
            println("Caught $u")
        }
	}
}

Heartbeat!
Heartbeat!
Caught java.lang.UnsupportedOperationException: Ow!
Heartbeat!
Heartbeat!
```

> 코루틴에서 예외를 잡을 때마다 취소 예외와 그 슈퍼타입을 염두에 두자. 취소는 코루틴 수명 주기의 자연스러운 일부이므로 이러한 예외를 코드에 집어넣어서는 안 된다. 애초에 잡히지 않거나 다시 던져야 한다

물론 잡히지 않은 예외 하나 때문에 전체 애플리케이션이 무너져서는 안 된다. `Kotlin` 코루틴에서는 수퍼바이저를 사용하여 이를 수행할 수 있다.

### 18.2.3 supervisor가 부모 및 형제자매가 취소되는 것을 방지한다.

`supervisor Job`는 자녀의 실패에도 살아남는다. 일반 작업을 사용하는 스코프와 달리, 수퍼바이저는 자식 중 일부가 실패를 보고해도 실패하지 않는다.

다른 자식 코루틴을 취소하지 않으며 구조화된 동시성 계층 구조 위로 예외를 전파하 지도 않는다. 이 때문에 코루틴 계층 구조에서 최상위 코루틴인 루트 코루틴으로 수퍼바이저를 자주 볼 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/ea5f69ee-c410-476c-9937-248d0bef41b5/image.png)

```kotlin
import kotlinx.coroutines.*
import kotlin.time.Duration.Companion.milliseconds
import kotlin.time.Duration.Companion.seconds
fun main(): Unit = runBlocking {
    supervisorScope {
		launch {
        	try {
                while (true) {
                    println("Heartbeat!")
                    delay(500.milliseconds)
                }
            } catch (e: Exception) {
                println("Heartbeat terminated: $e")
				throw e
			}
		}
		launch {
            delay(1.seconds)
            throw UnsupportedOperationException("Ow!")
        }
	}
}

Heartbeat!
Heartbeat!
Exception in thread "main" java.lang.UnsupportedOperationException: Ow!
...
Heartbeat!
Heartbeat!
```

`SupervisorJob`은 런치 빌더를 사용하여 시작된 자식 코루틴에 대해 `CoroutineExceptionHandler`를 제공한다.

수퍼바이저는 애플리케이션의 코루틴 계층 구조에서 '상위'에 위치해야 한다. 주로 코루틴은 애플리케이션의 전체 컨텍스트와 관련되어 사용된다. 세분화된 함수는 일반적으로 수퍼바이저를 사용하지 않으므로 불필요한 작업을 취소하는 것 이 코루틴에서 오류 전파의 바람직한 속성이다.

## 18.3 코루틴 예외 처리기: 예외 처리를 위한 최후의 수단

자식 코루틴은 예외가 수퍼바이저를 만나거나 예외가 계층 구조의 최상위(부모가없는 루트 코루틴)에 도달할 때까지 잡히지 않은 예외를 부모 코루틴에 전파한다.

이 시점에서 잡히지 않은 예외는 코루틴 컨텍스트의 일부인 코루틴 예외 핸들러라고 하는 특수 핸들러에 의해 제어된다. 컨텍스트에 코루틴 예외 처리기가 없는 경우, 잡히지 않은 예외는 시스템 전체 예외 처리기로 이동한다.

> 참고
>
> 시스템 전체 예외 처리기는 순수 `JVM` 프로젝트와 안드로이드 프로젝트에 서 다르다. 순수 `JVM` 프로젝트에서 핸들러는 단순히 예외 스택 추적을 오류 콘솔에 출력한다(JVM의 UncaughtExceptionHandler에 따라). `Android`에 서는 시스템 전체 예외 처리기가 앱을 충돌시킨다.

`Kotlin` 프레임워크는 자체적으로 코루틴 예외 처리기를 제공한다. 이 핸들러의 정의는 매우 간단하다. 코루틴 컨텍스트와 잡히지 않은 예외를 람다의 매개변수로 받는다.

```kotlin
val exceptionHandler = CoroutineExceptionHandler { context, exception ->
    println("[ERROR] $exception")
}
```

코루틴 예외핸들러는 코루틴 컨텍스트에 추가할 수 있는 코루틴 컨텍스트 요소이다. 아래 예제에서는 `SupervisorJob`으로 스코프를 정의하여 슈퍼바이저로 만드는 `ComponentWithScope`를 만든다.

```kotlin
import kotlinx.coroutines.*
import kotlin.time.Duration.Companion.seconds

class ComponentWithScope(dispatcher: CoroutineDispatcher = Dispatchers.Default) {

	private val exceptionHandler = CoroutineExceptionHandler { _, e ->
       println("[ERROR] ${e.message}")
	}

    private val scope = CoroutineScope(
        SupervisorJob() + dispatcher + exceptionHandler
	)

    fun action() = scope.launch {
       throw UnsupportedOperationException("Ouch!")
	}
}

fun main() = runBlocking {
    val supervisor = ComponentWithScope()
    supervisor.action()
    delay(1.seconds)
}

// 수퍼바이저가 자식 들의 예외를 처리한다.
[ERROR] Ouch!
```

자식 코루틴 또는 다른 코루틴에서 시작된 코루틴은 잡히지 않은 예외의 처리를 부모에게 위임한다는 점을 다시 한 번 강조할 필요가 있다. 이들은 차례로 계층 구조의 루트까지 이 처리를 더 위임한다. 따라서 루트 코루틴이 아닌 코루틴의 컨텍스트에 설치된 핸들러는 절대 사용되지 않으며, "중간" 코루틴 예외 핸들러 같은 것은 존재하지 않는다.

```kotlin
import kotlinx.coroutines.*

private val topLevelHandler = CoroutineExceptionHandler { _, e ->
    println("[TOP] ${e.message}")
}

private val intermediateHandler = CoroutineExceptionHandler { _, e ->
    println("[INTERMEDIATE] ${e.message}")
}

@OptIn(DelicateCoroutinesApi::class)
fun main() {
    GlobalScope.launch(topLevelHandler) {
        launch(intermediateHandler) {
            throw UnsupportedOperationException("Ouch!")
        }
	}
    Thread.sleep(1000)
}
// [TOP] Ouch!
```

![](https://velog.velcdn.com/images/cksgodl/post/c1dadb5e-a66a-4571-8548-baeb9c62ef91/image.png)

### 18.3.1 launch 또는 aysnc와 함께 코루틴 예외핸들러를 사용할때의 차이점

코루틴 예외 처리기를 살펴볼 때, 예외 처리기는 계층 구조의 최상위 코루틴이 실행과 함께 생성되었을 때만 호출된다는 점에 유의해야 한다. 즉, `async`를 최상위 코루틴으로 사용하면 `CoroutineExceptionHandler`가 호출되지 않는다.

```kotlin
import kotlinx.coroutines.*
import kotlin.time.Duration.Companion.seconds

class ComponentWithScope(dispatcher: CoroutineDispatcher = Dispatchers.Default) {
	private val exceptionHandler = CoroutineExceptionHandler { _, e ->
    	println("[ERROR] ${e.message}")
	}

    private val scope = CoroutineScope(SupervisorJob() + dispatcher)

  	fun action() = scope.launch {
    	async {
        	throw UnsupportedOperationException("Ouch!")
	    }
	}
}

fun main() = runBlocking {
	val supervisor = ComponentWithScope()
    supervisor.action()
    delay(1.seconds)
}

// [ERROR] Ouch!
```

외부 코루틴이 비동기를 사용하여 시작되도록 액션 구현을 변경하면 코루틴예외처리기가 호출되지 않는 것을 볼 수 있다.

```kotlin
import kotlinx.coroutines.*
import kotlin.time.Duration.Companion.seconds

class ComponentWithScope(dispatcher: CoroutineDispatcher = Dispatchers.Default) {

 	private val exceptionHandler = CoroutineExceptionHandler { _, e ->
        println("[ERROR] ${e.message}")
    }

    private val scope = CoroutineScope(SupervisorJob() + dispatcher)

	fun action() = scope.async {
    		launch {
    			throw UnsupportedOperationException("Ouch!")
        	}
	}
}

fun main() = runBlocking {
    val supervisor = ComponentWithScope()
    supervisor.action()
    delay(1.seconds)
}

// No output is printed
```

그 이유는 다음과 같다. **최상위 코루틴이 `async`를 사용하여 시작되면, 이 예외를 처리하는 것은 `Deferred`의 소비자가 `await()`을 호출하여 이 예외를 처리하는 책임이 된다.**

코루틴 예외 처리기는 이 예외를 무시할 수 있으며, `Deferred`와 함께 작동하는 호출코드는 `try-catch`블록에서 `await` 호출을 래핑할 수 있다. 그러나 이것은 코루틴 취소에는 영향을 미치지 않는다는 점에 유의해야 한다. 앞의 예제에서 스코프에 컨텍스트에 `SupervisorJob`이 설치되어 있지 않았다면 이 잡히지 않은 예외는 여전히 스코프의 자식인 다른 모든 코루틴의 취소를 트리거 한다.

## 18.4 플로우의 오류 처리

플로우도 예외를 `throw`할 수 있다.

```kotlin
 import kotlinx.coroutines.*
 import kotlinx.coroutines.flow.*

 class UnhappyFlowException: Exception()
 val exceptionalFlow = flow {
 	repeat(5) { number ->
    	emit(number)
	}
    throw UnhappyFlowException()
}
```

일반적으로 플로우가 생성, 변환 또는 수집되는 동안 플로우의 어느 부분에서든 예외가 발생 하면 `collect`에서 예외가 던져진다.

즉, `collect` 호출을 `try-catch`블록으로 둘러싸면 예상대로 작동할 수 있다. (물론 이 경우 `CancellationException`에 관한 특수 규칙을 염두에 두어야 함). 이는 플로우에 적용된 중간 연산자가 있는지 여부와 무관하다.

```kotlin
 fun main() = runBlocking {
 	val transformedFlow = exceptionalFlow.map { it * 2 }
	try {
    	transformedFlow.collect {
			print("$it ")
		}
    } catch (u: UnhappyFlowException) {
		println("\nHandled: $u")
    }
    // 0 2 4 6 8
    // Handled: UnhappyFlowException
}
```

더 길고 복잡한 플로우 파이프라인을 구축한 경우 더 편리하게 작동하는 또다른방법이있는데, 바로 `catch` 연산자이다.

### 18.4.1 캐치 연산자로 업스트림 예외 처리

`catch`는 플로우에서 발생하는 예외를 처리할 수 있는 중간 연산자이다. 함수와 연결된 람다에서 매개변수(일반적으로 기본적으로 암시적으로 이름이 지정됨)를 통해 던져진 예외에 액세스할 수 있다.

이 연산자는 이미 캔셀링 예외를 처리하고 있는 경우 `catch`에 제공된 블록이 호출되지 않는다. 또한 `catch`는 자체적으로 값을 방출할 수도 있으므로 예외를 다운스트림 흐름에서 사용할 수 있는 오류 값으로 전환하려는 경우에 유용하다.

```kotlin
fun main() = runBlocking {
    exceptionalFlow
        .catch { cause ->
            println("\nHandled: $cause")
            emit(-1)
		}.collect {
            print("$it ")
        }
}

// 0 1 2 3 4
// Handled: UnhappyFlowException
// -1
```

`catch` 연산자는 플로우 처리파이프라인에서 업스트림에서만 작동한다는 점을 다시 한 번 강조하는 것이 중요하다. `catch` 호출 이후에 이어지는 `onEach` 람다에서 던져진 예외는 잡히지 않은 상태로 유지된다:

```kotlin
fun main() = runBlocking {
    exceptionalFlow
		.map { it + 1 }
		.catch { cause ->
    		println("\nHandled $cause")
		}
		.onEach {
    		throw UnhappyFlowException()
		}.collect()
// Exception in thread "main" UnhappyFlowException
```

![](https://velog.velcdn.com/images/cksgodl/post/4333c032-a7e7-4b77-b2bc-ae7b7a59ec90/image.png)

### 18.4.2 참인경우 플로우를 다시시도: retry

플로우 처리 중에 예외가 발생하면 단순히 오류 메시지로 종료하는 대신 작업을 다시 시도하고 싶을 수 있다. 내장된 재시도 연산자는 `catch`와 마찬가지로 재시도를 통해 업스트림 예외를 잡을 수 있어 매우 편리하다. 그런 다음 연결된 람다를 사용하여 예외를 처리하고 부울 값을 반환할 수 있다. 람다가 참을 반환하면 재시도가 시작되게할 수 있다.(지정된 최대 재시도 횟수까지). 재시도 중에는 업스트림 흐름이 처음부터 다시 수집되어 모든 중간 작업을 다시 한 번 실행한다.

```kotlin
 import kotlinx.coroutines.flow.*
 import kotlinx.coroutines.*
 import kotlin.random.Random

 class CommunicationException : Exception("Communication failed!")
 	val unreliableFlow = flow {
    	println("Starting the flow!")
        repeat(10) { number ->
        	if (Random.nextDouble() < 0.1) throw CommunicationException()
                emit(number)
            }
		}
	}
}

fun main() = runBlocking {
	unreliableFlow
    	.retry(5) { cause ->
        	println("\nHandled: $cause")
		}
		.collect { number ->
    		print("$number ")
		}
}

Starting the flow!
01234
Handled: CommunicationException: Communication failed! Starting the flow!
0123
Handled: CommunicationException: Communication failed! Starting the flow!
0123456789
```

## 요약

- 단일 코루틴 내에서 발생한 예외는 일반적인 비동기 코드에서와 동일한 방식으로 처리할 수 있다. 하지만 코루틴 경계를 넘어가는 예외는 추가적인 처리가 필요하다.
- 기본적으로 코루틴에서 처리되지 않은 예외가 발생하면, 부모 코루틴과 모든 형제 코루틴이 취소된다. 이는 구조적 동시성(Structured Concurrency) 개념을 적용되기 때문이다.
- `Supervisors`는 `supervisorScope`나 `SupervisorJob`을 사용하는 다른 코루틴 스코프를 통해 사용되며, 하나의 자식 코루틴이 실패하더라도 다른 자식 코루틴을 취소하지 않으며, 처리되지 않은 예외를 상위 코루틴 계층으로 전달하지 않는다.
- `await`는 `async` 코루틴에서 발생한 예외를 다시 던진다.
- `Supervisors`는 애플리케이션의 장기 실행되는 부분에서 자주 사용된다.
- 처리되지 않은 예외는 `supervisor`에 도달하거나 예외가 코루틴 계층의 최상위에 도달할 때까지 전파된다.
  이 시점에서 `CoroutineExceptionHandler`로 전달되며, 이는 코루틴 컨텍스트의 일부이다. 만약 컨텍스트에 코루틴 예외 핸들러가 없으면, 처리되지 않은 예외는 시스템 전역 예외 처리기로 전달된다.
- `JVM`과 `Android`의 기본 시스템 전역 예외 처리기는 다르다: `JVM`에서는 스택 트레이스를 에러 콘솔에 기록하고, `Android`에서는 애플리케이션을 크래시시킨다.
- `CoroutineExceptionHandler`는 마지막 수단으로 예외를 처리한다. 예외를 잡아내지는 않지만, 예외를 기록하는 방식을 커스터마이징할 수 있다. `CoroutineExceptionHandler`는 계층의 맨 위에 있는 루트 코루틴의 컨텍스트에 있다.
- `CoroutineExceptionHandler`는 최상위 코루틴이 `launch` 빌더로 시작된 경우에만 호출된다. 만약 `async` 빌더로 시작된 경우에는 예외가 핸들러에 도달하지 않으며, 대신 `Deferred`를 기다리는 코드가 예외를 처리해야 한다.
- `Flow에`서의 에러 처리는 `collect`를 `try-catch` 구문으로 감싸거나 `catch` 연산자를 사용하여 처리할 수 있다.
- `catch` 연산자는 업스트림에서 발생한 예외만 처리하며, 다운스트림의 예외는 무시한다. 또한 예외를 다시 던져 하류에서 추가로 처리할 수도 있다.
- `retry` 연산자를 사용하면 예외가 발생할 경우 `Flow` 수집을 처음부터 다시 시작하여 복구할 기회를 줄 수 있다.
