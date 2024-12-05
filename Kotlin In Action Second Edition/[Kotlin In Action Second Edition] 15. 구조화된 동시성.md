코루틴을 내부에서 추적하기 위해 구조화된 동시성이란 개념을 제고한다. 이는 코루틴의 계층 구조와 수명을 관리하고 추적한다. 

## 15.1 코루틴 범위는 코루틴 간의 구조를 설정

구조화된 동시성을 사용하면 각 코루틴은 코루틴 스코프에 속하게 된다. 즉,다른 코루틴 빌더의 본문에서 `launch` 또는 `async`를 사용하여 새 코루틴을 만들면 새 코루틴이 자동으로 해당 코루틴의 하위 코루틴이 된다.

```kotlin
fun main() {
    runBlocking { // this: CoroutineScope
        launch { // this: CoroutineScope
            delay(1.seconds)
            launch {
                delay(250.milliseconds)
                log("Grandchild done")
            }
            log("Child 1 done!")
        }
        launch {
            delay(500.milliseconds)
            log("Child 2 done!")
		}
        log("Parent done!")
    }
}
```

"Parent done!"이 거의 실행과 동시에 표기 되지만, 모든 자식 코루틴이 완료될 때까지 프로 그램이 실제로 종료되지 않는다는 것 을 알 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/65fd2bdd-47a9-4ed0-bf86-f81bbd72243d/image.png)

이는 구조화된 동시성 덕분에 가능합니다. 코루틴(엄밀히 말하면 Job 객체) 사이에 부모-자식 관계가 존재하므로, `runBlocking` 호출은 얼마나 많은 자식이 아직 작업 중인지 알고 있으며, 모두 완료될 때까지 계속 대기한다. 

![](https://velog.velcdn.com/images/cksgodl/post/1c5b9a2b-e534-4856-8295-954ba235c43a/image.png)

코루틴이 자식 코루틴을 인식하고 추적할 수 있다는 사실은 부모 코루틴이 취소될 때 자식 코루틴을 자동으로 취소하는 등의 기능을 가능하게 해준다.
또한 예외 처리와 관련하여 원하는 동작을 표현하는 데 도움이 될 수 있는 데, 이에 대해서는 18장에서 설명하겠다.

## 15.1.1 코루틴 스코프 생성하기: 코루틴 스코프 함수

지금까지 살펴본 것처럼 코루틴 빌더를 사용해 새 코루틴을 만들 때마다 자체 코루틴 스코프가 생성된다. 하지만 완전히 새로운 코루틴을 만들지 않고도 자체 코루틴 스코프를 사용하여 코루틴을 그룹화할 수도 있다. 

그렇게 하려면 `coroutineScope` 함수를 사용한다. 이 함수는 새 코루틴 스코프를 생성하고 모든 하위 코루틴이 완료될 때까지 기다렸다가 자체 코루틴이 완료될 때까지 기다리는 일시 중단 함수이다.

```kotlin
import kotlinx.coroutines.*
import kotlin.random.Random
import kotlin.time.Duration.Companion.milliseconds

suspend fun generateValue(): Int {
    delay(500.milliseconds)
    return Random.nextInt(0, 10)
}

suspend fun computeSum() {
    log("Computing a sum...")
    val sum = coroutineScope {
        val a = async { generateValue() }
        val b = async { generateValue() }
        a.await() + b.await()
    }
    log("Sum is $sum")
}

fun main() = runBlocking {
    computeSum()
}

// 0 [main @coroutine#1] Computing a sum...
// 532 [main @coroutine#1] Sum is 10
```
![](https://velog.velcdn.com/images/cksgodl/post/1318005b-69b2-4505-a274-3916cbb8e232/image.png)

### 15.1.2 코루틴 스코프와 컴포넌트 연결하기: 코루틴 스코프

코루틴 스코프 함수는 작업을 분해하는 데 사용되지만, 동시 프로세스 및 코루틴의 시작과 중지를 관리하면서 자체적인 라이프사이클을 정의하는 클래스를 만들고 싶을 수도 있다. 

이러한 경우 `CoroutineScope` 생성자 함수를 사용하여 새로운 독립형 코루틴 스코프를 생성할 수 있다. 이 함수는 코루틴 스코프와 달리 실행을 일시 중지하지 않고 새 코루틴을 시작하는 데 사용할 수 있는 새 코루틴 스코프를 제공한다.

코루틴 스코프는 코루틴 스코프와 관련된 컨텍스트를 매개변수로 받는다. 

```kotlin
class ComponentWithScope(dispatcher: CoroutineDispatcher = Dispatchers.Default) {
    
    private val scope = CoroutineScope(dispatcher + SupervisorJob())
    
    fun start() {
        log("Starting!")
        scope.launch {
            while(true) {
                delay(500.milliseconds)
                log("Component working!")
            }
        }
        scope.launch {
            log("Doing a one-off task...")
            delay(500.milliseconds)
            log("Task done!")
		} 
	}
    
    fun stop() {
        log("Stopping!")
        scope.cancel()
    }
}
```

```kotlin
fun main() {
    val c = ComponentWithScope()
    c.start()
    Thread.sleep(2000)
    c.stop()
}

// 22 [main] Starting!
// 37 [DefaultDispatcher-worker-2 @coroutine#2] Doing a one-off task...
// 544 [DefaultDispatcher-worker-1 @coroutine#2] Task done!
// 544 [DefaultDispatcher-worker-2 @coroutine#1] Component working!
// 1050 [DefaultDispatcher-worker-1 @coroutine#1] Component working!
// 1555 [DefaultDispatcher-worker-1 @coroutine#1] Component working!
// 2039 [main] Stopping!
```

새 인스턴스를 생성하고 `start`를 호출하여 컴포넌트가 내부적으로 코루틴 을 실행하도록 할 수 있다. 그런 다음 `stop`을 호출하여 컴포넌트의 수명 주기를 끝 낼 수 있다.

> `coroutineScope`와 `CoroutineScope`의 차이
>
> - 작업의 병렬처리에는 `coroutineScope`를 사용한다. 여러 코루틴을 실행하고 모든 코루틴이 완료될 때까지 기다렸다가 어떤 종류의 결과를 계산할 수 있다. 
 	`CoroutineScope`는 모든 자식이 완료될 때까지 기다리는 일시 중단 함수이다.
- 코루틴을 클래스의 라이프사이클과 연관시키는 스코프를 만들려면 `CoroutineScope`를 사용한다. 이 함수는 스코프를 생성하지만 추가 작업을 기다리지 않으므로 빠르게 반환된다. 해당 코루틴 스코프에 대한 참조를 반환하므로 나중에 취소할 수 있다.
>
>실제로는 코루틴 스코프 생성자 함수(`CoroutineScope`)보다 일시 중단 코루틴 스코프(`coroutineScope`)가 더 많이 사용되는 것을 볼 수 있다. 일반적으로 일시 중단 함수의 본문에서 코루틴 스코프를 호출하는 것을 볼 수 있으며, 코루틴 스코프를 클래스의 속성으로 저장할 때 코루틴 스코프 생성자가 사용되는 것을 볼 수 있다.

### 15.1.3 GlobalScope의 위험

일부 샘플이나 코드 스니펫에서 코루틴 범위의 특수 인스턴스인 `GlobalScope`를 볼수 있다. 이름에서 알 수 있듯이 글로벌 수준에 존재하는 코루틴 범위이다. 특히 코루틴을 처음 사용하는 경우 코루틴을 만들 때 사용할 코루틴 범위를 결정할 때 전 세계에서 사용할 수 있다는 점에서 매력적인 선택이 될 수 있다.

그러나 `GlobalScope`를 사용하면 여러 가지 단점이 있다. 간단히 요약하면, 글로벌 스코프를 사용한다는 것은 구조화된동시성이 제공하는 모든이점을 포기하는 것을 의미한다. 글로벌 스코프에서 시작된 코루틴은 자동으로 취소할 수 없으며 수명 주기를 인식하지 못한다.

```kotlin
fun main() {
    runBlocking {
        GlobalScope.launch {
            delay(1000.milliseconds)
            launch {
                delay(250.milliseconds)
                log("Grandchild done")
            }
            log("Child 1 done!")
        }
        GlobalScope.launch {
            delay(500.milliseconds)
            log("Child 2 done!")
}
        log("Parent done!")
    }
}

// 28 [main @coroutine#1] Parent done!
```

구조화된 동시성을 사용할 때 일반적으로 설정된 계층구조가 `GlobalScope`를 사용하면 즉시 깨지기 때문에 이 코드는 즉시 종료된다. 애플리케이션의 전체 수명 동안 활성 상태를 유지해야 하는 최상위 백그라운드 프로세스가 아니면 해당 스코프를 활요하지 말 것을 권장한다.

![](https://velog.velcdn.com/images/cksgodl/post/9b16ac67-9a38-4232-9037-139a1cdeb95d/image.png)

### 15.1.4 코루틴 컨텍스트와 구조화된 동시성

코루틴 컨텍스트는 구조적 동시성의 개념과 밀접한 관련이 있으며, 코루틴 간에 설정된 동일한 상위-하위 계층 구조를 따라 상속된다.

그렇다면 새 코루틴을 시작할 때 코루틴 컨텍스트는 어떻게 될까? 

1. 자식 코루틴이 부모 컨텍스트를 상속한다. 
2. 새 코루틴은 부모-자식 관계를 설정하는 역할을 하는 새 Job 객체를 생성하여, `Job`이 부모코루틴에 있는 `Job`의 자식이된다.
3. 마지막으로 코루틴 컨텍스트에 제공된 모든 인수가 상속된다. 

```kotlin
fun main() {
	runBlocking(Dispatchers.Default) {
    	log(coroutineContext)
        launch {
        	log(coroutineContext)
            launch(Dispatchers.IO + CoroutineName("mine")) {
            	log(coroutineContext)
			}
		} 
	}
}
// 0 [DefaultDispatcher-worker-1 @coroutine#1] [CoroutineId(1), "coroutine#1":BlockingCoroutine{Active}@68308697, Dispatchers.Default]
// 1 [DefaultDispatcher-worker-2 @coroutine#2] [CoroutineId(2), "coroutine#2":StandaloneCoroutine{Active}@2b3ce773, Dispatchers.Default]
// 2 [DefaultDispatcher-worker-3 @mine#3] [CoroutineName(mine), CoroutineId(3), "mine#3":StandaloneCoroutine{Active}@7c42841a, Dispatchers.IO]
```

![](https://velog.velcdn.com/images/cksgodl/post/8774fe1b-5bb6-4487-bd4c-cbebbe2720de/image.png)

```kotlin
import kotlinx.coroutines.job
fun main() = runBlocking(CoroutineName("A")) {
    log("A's job: ${coroutineContext.job}")
    launch(CoroutineName("B")) {
    	log("B's job: ${coroutineContext.job}")
        log("B's parent: ${coroutineContext.job.parent}")
	}
    log("A's children: ${coroutineContext.job.children.toList()}")
}
// 0 [main @A#1] A's job: "A#1":BlockingCoroutine{Active}@41
// 10 [main @A#1] A's children: ["B#2":StandaloneCoroutine{Active}@24
// 11 [main @B#2] B's job: "B#2":StandaloneCoroutine{Active}@24
// 11 [main @B#2] B's parent: "A#1":BlockingCoroutine{Completing}@41
```

코루틴 빌더 함수가 `launch` 및 `async`와 같은 코루틴 빌더 함수에서 시작된 것처럼, `coroutineScope` 함수에도 부모-자식 계층 구조에 참여하는 자체 `Job` 객체가 있다. `coroutineContext.job` 속성을 확인하면 이것이 실제로 사실인지 확인할 수 있다.

```kotlin
fun main() = runBlocking<Unit> { 
	// coroutine#1
	log("A's job: ${coroutineContext.job}")
    coroutineScope {
    	log("B's parent: ${coroutineContext.job.parent}") // A
        log("B's job: ${coroutineContext.job}") // C
        launch { //coroutine#2
        	log("C's parent: ${coroutineContext.job.parent}") // B
		}
	} 
}

// 0 [main @coroutine#1] A's job: "coroutine#1":BlockingCoroutine{Active}@41 
// 2 [main @coroutine#1] B's parent: "coroutine#1":BlockingCoroutine{Active}@41
// 2 [main @coroutine#1] B's job: "coroutine#1":ScopeCoroutine{Active}@56
// 4 [main @coroutine#2] C's parent: "coroutine#1":ScopeCoroutine{Completing}@56
```

## 15.2 취소

### 15.2.1 취소 트리거

다른 코루틴 빌더의 반환값은 취소를 트리거하는 핸들로 사용할 수 있다. 실행 코루틴 빌더는 `Job`을 반환하고 비동기 코루틴 빌더는 `Deferred`를 반환한다. 

두 코루틴 빌더 모두 취소를 호출하여 각 코루틴의 취소를 트리거할 수 있다:

```kotlin
fun main() {
    runBlocking {
        val launchedJob = launch {
            log("I'm launched!")
            delay(1000.milliseconds)
            log("I'm done!")
        }
        val asyncDeferred = async {
            log("I'm async")
            delay(1000.milliseconds)
            log("I'm done!")
        }
        delay(200.milliseconds)
        launchedJob.cancel()
        asyncDeferred.cancel()
	} 
}

// 0 [main @coroutine#2] I'm launched!
// 7 [main @coroutine#3] I'm async
```

### 15.2.2 시간 제한 초과 후 자동으로 취소 호출하기

`withTimeout` 및 `withTimeoutorNull` 함수를 사용 하면 계산에 소요되는 최대 시간을 제한하면서 값을 계산할 수 있다.

`withTimeout` 함수는 시간 초과가 발생한 경우 예외(정확히 `TimeoutCancellation`예외를 던진다. 시간 초과를 처리하려면 `withTimeout` 호출을 시도에서 래핑하고 던져 진`TimeoutCancellation`예외를 잡으면 된다. 이와 유사하게, `withTimeoutorNull`함수는 시간초과가 발생하면 `null`을 반환한다.

```kotlin
import kotlinx.coroutines.*
import kotlin.time.Duration.Companion.seconds
import kotlin.time.Duration.Companion.milliseconds

suspend fun calculateSomething(): Int {
	delay(3.seconds)
    return 2 + 2 
}

fun main() = runBlocking {
	val quickResult = withTimeoutOrNull(500.milliseconds) {
    	calculateSomething()
	}
    println(quickResult)
    // null
    
    val slowResult = withTimeoutOrNull(5.seconds) {
    	calculateSomething()
	}
    println(slowResult)
	// 4
}
```

![](https://velog.velcdn.com/images/cksgodl/post/1aef0478-9745-4d8c-a270-58627ae4990b/image.png)

### 15.2.3 취소는 모든 자식에게 연쇄적으로 적용된다.

코루틴을 취소하면 해당 코루틴의 모든 하위 코루틴도 취소된다. 각 코루틴은 자신이 시작한 코루틴을 인식하기 때문에 불필요한 작업을 수행하거나 불필요한 데이터를 필요 이상으로 메모리에 오래 보관할 수 있는 불량 코루틴을 실행한채로 두지 않고 항상 스스로 정리한다.

```kotlin
fun main() = runBlocking {
    val job = launch {
        launch {
            launch {
                launch {
                    log("I'm started")
                    delay(500.milliseconds)
                    log("I'm done!")
				}				 
			}
		} 	
	}
    delay(200.milliseconds)
    job.cancel()
}

// 0 [main @coroutine#5] I'm started
```

### 15.2.4 취소된 코루틴은 특별한 장소에서 취소 예외를 던진다.

일반적인 취소 메커니즘은 예외 유형인 취소예외를 던지는 방식으로 작동한다. 

취소된 코루틴은 14장에서 간략하게 살펴본 것처럼 코루틴 실행이 일시 중지될 수 있는 지점인 일시 중지 지점에서 `CancellationException`을 던진다. 일반적으로 코루틴 라이브러리 내의 모든 일시 중단 함수는 이러한 지점에서 `CancellationException`을 던질 수 있다고 가정할 수 있다. 

```kotlin
coroutineScope {
    log("A")
	// The point where the function can be cancelled.
    delay(500.milliseconds)
    log("B")
    log("C")
}
```

스코프가 취소되었는지 여부에 따라 다음 코드 조각은 "A" 또는 "ABC"를 출력하지만 "B"와 "C" 사이에는 취소 지점이 없으므로 "AB"는 출력하지 않는다:

코루틴은 예외를 사용하여 코루틴 계층 구조 전체에 취소를 전파하므로 실수로 이 예외를 무시하거나 직접 처리하지 않도록 주의하는 것이 중요하다.

```kotlin
suspend fun doWork() {
    delay(500.milliseconds)
    throw UnsupportedOperationException("Didn't work!")
}

fun main() {
    runBlocking {
        withTimeoutOrNull(2.seconds) {
            while (true) {
                try {
                    doWork()
                } catch (e: Exception) {
                    println("Oops: ${e.message}")
				} 
			}
		} 
	}
}
// Oops: Didn't work!
// Oops: Didn't work!
// Oops: Didn't work!
// Oops: Timed out waiting for 2000 ms
// ... (does not terminate)
```

2초후, `withTimeoutorNull` 함수는 하위 코루틴범위의 취소를 요청한다. 이 과정에서 다음지연 호출은 취소예외를 던진다. 그러나 `catch` 문은 모든 유형의 예외를 잡기 때문에 코드가 무기한 반복을 계속하여 프로그램이 종료되지 않는다. 

이 문제를 해결하려면 예외를 다시 던지거나 (`if(e가 CancellationException) throw e))`, 처음부터 예외를 잡지 않거나 (`catch (e: UnsupportedoperationException)`) 할 수 있다. 이 중 하나를 적용하면 코드가 예상대로 취소된다.

### 취소는 협조적이다.

```kotlin
suspend fun doCpuHeavyWork(): Int {
    log("I'm doing work!")
    var counter = 0
    val startTime = System.currentTimeMillis()
    while (System.currentTimeMillis() < startTime + 500) {
		counter++
	}
    return counter
}

fun main() {
    runBlocking {
        val myJob = launch {
            repeat(5) {
                doCpuHeavyWork()
            }
        }
        delay(600.milliseconds)
        myJob.cancel()
	}
}

// 30 [main @coroutine#2] I'm doing work!
// 535 [main @coroutine#2] I'm doing work!
// 1036 [main @coroutine#2] I'm doing work!
// 1537 [main @coroutine#2] I'm doing work!
// 2042 [main @coroutine#2] I'm doing work!
```

이 코드는 취소되기 전에 "I'm doing work!"라는 텍스트를 두 번 출력할 것이라고 예상할 수 있다. 그러나 이 코드 스니펫의 실제 출력을 보면 실제로 프로그램이 종료되기전에 `doCpuHeavyWork`의 다섯 번의 반복이 모두 완료된다는 것을 알 수 있다:

__이유로는 코루틴의 취소가 함수내의 일시중단 지점에서 취소 예외를 던지는방식으로 작동하기 때문이다.__

`suspend` 수정자가 표시되어 있음에도 불구하고 `doCpuHeavyWork` 함수의 본문에는 실제로 일시 중단 지점이 포함되어 있지 않으며, 로그 호출을 수행한 다음 `CPU`를 많이 사용하는 장기 실행 연산을 수행한다. `repeat`함수에 대해 하나의 `launch`내부에 인라인되어 중지 시점이 없음으로 해당 코루틴은 취소되지 않는다.

일시 중단 함수는 그 자체로 취소할 수 있는 로직을 제공해야 한다. __코드에서 취소할 수 있는 다른 함수를 호출하면 자동으로 코드도 취소할 수 있는 지점이 생긴다.__

```kotlin
suspend fun doCpuHeavyWork(): Int {
    log("I'm doing work!")
    var counter = 0
    val startTime = System.currentTimeMillis()
    while (System.currentTimeMillis() < startTime + 500) {
    	counter++
        delay(100.milliseconds) // delay는 중단함수이다.
    }
    return counter
}
```

하지만 물론 취소를 위해 인위적으로 계산을 지연시키고 싶지는 않을 것이다. 코틀린은 따라서 `ensureActive` 및 `yield` 함수와 `isActive` 속성을 제공한다.

### 15.2.7 다른 코루틴을 재생: yield

코루틴 라이브러리에서는 `yield`라는 또 다른 관련 함수도 제공한다. 이 함수는 함수를 취소할 수 있는 지점을 도입하는 것 외에도 현재 점유 중인 디스패처에서 다른 코루틴이 작동하도록 하는 방법도 제공한다. 

```kotlin
import kotlinx.coroutines.*

fun doCpuHeavyWork(): Int {
    var counter = 0
    val startTime = System.currentTimeMillis()
    while (System.currentTimeMillis() < startTime + 500) {
		counter++ 
	}
    return counter
}

fun main() {
    runBlocking {
        launch {
            repeat(3) {
                doCpuHeavyWork()
            }
		}
		launch {
            repeat(3) {
                doCpuHeavyWork()
			} 
		}
	}
}

29 [main @coroutine#2] I'm doing work!
533 [main @coroutine#2] I'm doing work!
1036 [main @coroutine#2] I'm doing work!
1537 [main @coroutine#3] I'm doing work!
2042 [main @coroutine#3] I'm doing work!
2543 [main @coroutine#3] I'm doing work!
```

`doCpuHeavyWork` 구현에 일시 중단 지점이 없는 경우, 두 번째 코루틴이 실행되기 전에 첫 번째 실행된 코루틴이 완료되는 것을 확인할 수 있다

__코루틴 본문에 중단 지점이 없으면 코루틴이 첫 번째 코루틴 의 실행을 일시 중지하고 두 번째 코루틴의 실행을 시작할 기회가 없다.__

`isActive`를 확인하거나 `ensureActive`를 호출해도 아무 것도 바뀌지 않는다. 이러한 함수는 취소 여부만 확인할 뿐 실제로 코루틴을 일시 중단하지는 않는다. 여기서 `yield` 함수가 도움이 되는데, 코드에서 `CancellationException`이 발생할 수 있는 지점을 도입하고 대기 중인 코루틴이 있는 경우 디스패처가 다른 코루틴 작업으로 전환할 수 있도록 하는 일시 중단 함수이다. 

```kotlin

suspend fun doCpuHeavyWork(): Int {
    var counter = 0
    val startTime = System.currentTimeMillis()
    while (System.currentTimeMillis() < startTime + 500) {
		counter++
		yield() 
	}
    return counter
}

0 [main @coroutine#2] I'm doing work!
559 [main @coroutine#3] I'm doing work!
1062 [main @coroutine#2] I'm doing work!
1634 [main @coroutine#3] I'm doing work!
2208 [main @coroutine#2] I'm doing work!
2734 [main @coroutine#3] I'm doing work!
```

![](https://velog.velcdn.com/images/cksgodl/post/0bda3a35-9304-4a14-adf2-3801f8fbfc05/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/f425fa4b-a4d9-4ca5-8969-82000cbae070/image.png)

### 15.2.8 리소스 사용 시 취소를 염두할 것

실제 코드는 데이터베이스 연결, IO 등과 같은 리소스를 사용해야 하는 경우가 많으므로 사용 후 명시적으로 닫아서 제대로 해제되도록 해야한다. 

다른 유형의 예외 와 마찬가지로 취소는 코드의 조기 반환을 초래할 수 있으므로 코루틴이 취소된 후 실수로 리소스를 계속 보유하지 않도록 적절한 주의를 기울여야 한다. 

```kotlin
class DatabaseConnection : AutoCloseable {
    fun write(s: String) = println("writing $s!")
    override fun close() {
        println("Closing!")
    }
}

fun main() {
    runBlocking {
        val dbTask = launch {
            val db = DatabaseConnection()
            delay(500.milliseconds)
            db.write("I love coroutines!")
            db.close() 
		}
        delay(200.milliseconds)
        dbTask.cancel()
	}
    println("I leaked a resource!")
}
```

위의 코드는 리소스 유실이 발생한다. 따라서 아래와 같이 작성해야 한다.

```kotlin
val dbTask = launch {
	val db = DatabaseConnection()
    try {
    	delay(500.milliseconds)
        db.write("I love coroutines!")
	} finally {
		db.close() 
	}
}
```

코루틴 내부에서 사용 중인 리소스가 자동 닫을 수 있는 인터페이스를 구현하는 경우, `use`를 활용하여 더 관용적으로 사용할 수 있다.

```kotlin
val dbTask = launch {
	DatabaseConnection().use {
    	delay(500.milliseconds)
    	it.write("I love coroutines!")
    }
}
```

### 15.2.9 프레임워크에서 취소를 수행할 수 있다.

지금까지는 코루틴의 취소를 수동으로 트리거하거나, `withTimeoutorNull`의 경우 코루틴 라이브러리가 취소 트리거 시기를 결정하도록 했다. 하지만, 많은 실제 애플리케이션에서 프레임워크는 코루틴 범위 제공과 취소 트리거를 처리할 수 있다. 

안드로이드 애플리케이션의 컨텍스트에서 뷰모델 클래스는 `viewModelScope`를 제공한다. 뷰모델이 지워지면(예: 사용자가 뷰모델이 표시된 화면에서 벗어나면) 뷰모델 스코프가 취소되고 이 스코프에서 실행된 모든 코루틴도 취소된다:

```kotlin
class MyViewModel: ViewModel() {
    init {
        viewModelScope.launch {
            while (true) {
                println("Tick!")
                delay(1000.milliseconds)
            }
		} 
	}
}
```

## 요약

- 구조화된 동시성을 사용하면 코루틴이 수행하는 작업을 제어하고 불량 코루 틴이 취소를 피하지 못하도록 방지할 수 있다.
- 일시중단하는 코루틴스코프 도우미함수와 코루틴 스코프생성자 함수를 사용하여 새 코루틴 스코프를 만들 수 있다. 
- 코루틴 스코프는 여러 코루틴을 시작하고 결과를 계산할 때까지 기다린 다음 그 결과를 반환하는 등 작업을 동시에 분해할 수 있도록 설계되었다.
- 코루틴 스코프는 코루틴을 클래스의 라이프사이클과 연관시키는 데 사용되는 코루틴 스코프를 생성합니다. 일반적으로 `SupervisorJob`과 함께 사용된다.
- `GlobalScope는` 예제 코드 조각에 자주 표시되지만 구조화된 동시성을 깨뜨리기 때문에 애플리케이션 코드에서 사용해서는 안 되는 특수 코루틴 범위이다.
- 코루틴 컨텍스트는 개별 코루틴이 실행되는 방식을 관리한다. 이는 코루틴 계층구조를 따라 상속된다.
- 코루틴과 코루틴범위 사이의 상위-하위 계층 구조는 코루틴 컨텍스트에서 연결된 Job 객체를 통해 설정된다.
- 일시중단지점은 코루틴을 일시중지하고 다른 코루틴이 작업을 시작할 수 있는 곳이다.
- 취소는 일시 중단 지점에서 취소 예외를 던져 실현된다.
- 취소 예외는 절대 삼켜서는 안 된다. 대신 다시 던지거나 애초에 잡히지 않도록 해야 한다.
- 취소는 정상적인 현상이며, 코드가 이를 처리할 수 있도록 설계되어야 한다.

