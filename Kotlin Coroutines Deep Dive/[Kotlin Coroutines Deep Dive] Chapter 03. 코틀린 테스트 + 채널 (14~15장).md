# 15장 코틀린 코루틴 테스트하기

코틀린의 테스트도 일반함수와 크게 다를 거 없으며, `runBlocking`과 어설트 도구를 활용해 테스트가 가능합니다.

```kotlin
@Test
fun main() = runBlocking {
	// ...
}
```

_`runBlocking`은 하나의 쓰레드를 점유하고 (`TestWorker @coroutine#1, CoroutineTest$main$1`) 위에서 코루틴을 실행합니다._


## 시간 의존성 테스트하기

코루틴의 테스트를 위해서는 `kotlinx-coroutines-test`라이브러리가 제공하는 `StandardTestDispatcher`를 활용할 수 있습니다.

이는 `가상 시간`이라는 개념을 도입하여 목 객체와 더불어 코루틴이 올바르게 동작하는지 확인 가능합니다.

```kotlin
@Test
fun main() = runBlocking {
    val scheduler = TestCoroutineScheduler()
    val testDispatcher = StandardTestDispatcher(scheduler)
    println(testDispatcher.scheduler.currentTime)
    testDispatcher.scheduler.advanceTimeBy(1000L)
    println(testDispatcher.scheduler.currentTime)
    testDispatcher.scheduler.advanceTimeBy(1000L)
    println(testDispatcher.scheduler.currentTime)
}

// 출력 결과
0
1000
2000
```

가상 시간을 지나게 하기 위해서는 테스트 스케줄러의

- `advanceTimeBy`
- `advanceUntilIdle`

등의 확장함수를 이용 가능합니다.

> 이런 가상 시간을 진행시키지 않으면 해당 테스트는 진행되지 않습니다. (무한 루프)

`StandardDispatcher`은 기본 생성자로 생성하면 기본 인자로 스케줄러를 넣습니다.

```kotlin
private class StandardTestDispatcherImpl(
    override val scheduler: TestCoroutineScheduler = TestCoroutineScheduler(),
    private val name: String? = null
) : TestDispatcher()
```

가상시간을 제어함에 따라서 이러한 중간중간 과정에서 내부 동작을 테스트할 수 있습니다.

```kotlin
@Test
fun main() = runTest {
    val userInfo = FetchUserInfo()
    
    delay(1000L)
    assert(progressbar.isLoading, true) // 로딩 중인지
    delay(1000L)
    assert(progressbar.isLoading, false) // 로딩이 끝났는지
    
}
```

이러한 가상시간은 실제 시간과 무관합니다. (`Thread.sleep`을 해도 테스트디스패쳐의 시간에 영향 X)

나아가 이런 `TestDispatcher`를 활용하는 `TestScope`를 따로 생성하여 테스트할 수 있습니다.

```kotlin
@Test
fun main() = runTest {
    val testScope = TestScope()
    testScope.launch {
        println(currentTime)
        advanceTimeBy(1000L)
    }
}
```


## runTest

> 위의 방식은 복잡함 -> 테스트를 할 떄는 `runTest` 권장

`runTest`는 스코프가 테스트코프타입인 코루틴을 빌드할 수 있는 확장함수입니다.

해당 스코프 내에서 `delay`를 하게 된다면 `testScheduler`에 의해 가상시간으로 연산되게 됩니다.

__즉 `mokk`객체와 더불어 좀 더 편리하게 코루틴 테스트를 진행할 수 있게 도와줍니다.__

```kotlin
@Test
fun main() = runTest {
    println(currentTime)
    advanceTimeBy(1000L)
    println(currentTime) // 1000
    delay(1000L)
    println(currentTime) // 2000
}
```

집합관계를 정리하자면 다음과 같습니다.

> `runTest` > `TestScope` > `StandardTestDispatcher` > `TestCoroutiineScheduler`

## 백그라운드 스코프

`runTest` 스코프 내부에서는 백그라운드 스코프사용할 수 있습니다. 특징으로써는

- 테스트가 끝날 때 자동으로 취소 됨
- 테스트 스코프 내부의 가상시간에 맞추어 함수가 실행됨
- 테스트 스코프에게 오류를 전달하지 않음 (구조화된 동시성 X)

```kotlin
@Test
fun main() = runTest {
    var x = 0
    backgroundScope.launch {
        while (true) {
            delay(1000L)
            x++
        }
    }
    delay(1001L)
    println("x : $x")
    delay(1000L)
    println("x : $x")
}

// 출력 결과
x : 1
x : 2
```

이는 특징적으로써는 `GlobalScope`를 쓰는 것과 비슷하게 작동합니다. (`GlobalScope`은 함수가 종료되도 살아있음)

```kotlin
@Test
fun main() = runBlocking {
    var x = 0
    GlobalScope.launch {
        while (true) {
            delay(1000L)
            x++
        }
    }
    delay(1001L)
    println("x : $x")
    delay(1000L)
    println("x : $x")
}
```

## UnconfinedTestDispatcher

테스트를 위한 디스패처 중 `StandardDispatcher` 말고도 `UnconfinedTestDispatcher`가 있습니다.

이는 가상 시간 기능을 제공하되 `Unconfined` 특징을 가집니다. (첫 번째 지연이 일어나기 전까지 모든 연산을 즉시 수행합니다.)

```kotlin
@Test
fun main() = runTest(StandardTestDispatcher()) {
    launch {
        println("a")
    }
    launch {
        delay(100L)
        println("b")
    }
    launch {
        println("c")
    }
    println("d")
}
// 출력 결과
d
a
c
b

@Test
fun main() = runTest(UnconfinedTestDispatcher()) {
    launch {
        println("a")
    }
    launch {
        delay(100L)
        println("b")
    }
    launch {
        println("c")
    }
    println("d")
}

// 출력 결과
a
c
d
b
```


## mock 사용하기

가짜 객체를 제공하는 라이브러리를 활용해 코루틴 테스트가 가능합니다.

- [mockk/mockk - github](https://github.com/mockk/mockk)

## 디스패처를 바꾸는 함수 테스트하기

다음과 같은 함수는 `Dispatcher.IO`를 활용하기에 시간에 대한 테스트가 용이하지 않습니다.

```kotlin
suspend fun doSomething() = withContext(Dispatcher.IO) {
	val data = async { repository.fetchData() }
    // ...
}
```

가상 시간에서 목객체와 함께 테스트하기 위해서는 `Dispatcher`를 `DI`를 통해 주입하는 방식으로 코드를 구성하는 것이 좋습니다.


```kotlin
@Bean("ioDispatcher")
fun provideIoDispatcher() : CoroutineDispatcher = Dispatcher.IO

@Service
class userService(
	private val userRepo: UserRepository,
    private val ioDispatcher: CoroutineDispatcher
) {

	suspend fun doSomething() = withContext(ioDispatcher) {
		val data = async { repository.fetchData() }
    	// ...
	}
}
```

위의 함수를 통해 테스트할 때 `TestDispatcher`주입한 후, 목객체를 활용해 가상 시간 테스트가 가능합니다.

- 주로 사용하는 디스패처는 싱글톤으로 등록하여 다양한 곳에서 주입받아 활용하는 것을 권장합니다.

## 메인 디스패처 등록하여 테스트하기

단위 테스트단에서는 메인 디스패처를 사용할 수 없습니다. 따라서 `Dispatcher.setMain`을 통해 메인 디스패처를 등록하여 메인 디스패처를 테스트할 수 있습니다.

```kotlin
Dispatchers.setMain(StanddardTestDispatcher())
```



# 16장 채널

코루틴끼리의 통신을 위해서는 채널을 활용할 수 있습니다.

- `SendChannel`
- `ReceiveChannel`

두개의 구현되며, `send`, `receive`를 통해 원소를 주고 받을 수 있습니다. __Channel은 두 인터페이스를 모두 구현합니다.__

`send, receive`는 내부적으로 `ProducerCoroutine`을 실행합니다. 즉 이들은 값을 생성하고 소비하는 코루틴의 빌더입니다.

> `send`는 버퍼가 가득차면 중단, `receive`는 채널에 원소가 없다면 중단됩니다.


```kotlin
@Test
fun main(): Unit = runBlocking {
    
    val channel = Channel<Int>()
    launch {
        repeat(5) {
            delay(1000)
            println("Produce $it")
            channel.send(it)
        }
        // channel.close()
    }

    launch {
        for (i in channel) {
            println("Receive : $i")
        }
    }
}

// 출력 결과
Produce 0
Receive : 0
Produce 1
Receive : 1
Produce 2
Receive : 2
Produce 3
Receive : 3
Produce 4
Receive : 4
(무한히 실행)
```

컨슘을 위해서는 `for`루프나 `consumeEach`활용을 권장

+) `consumeEach`은 채널이 닫히면 자동으로 루프를 종료합니다.

 사용되지 않는 채널은 `close()`를 수행해야 함 -> `receive`가 무한히 중단되지 않습니다. 
 
 채널 닫는걸 깜박한다면 `produce`를 활용하는 채널을 이용하는 것을 권장합니다. 왜냐하면 이는 코루틴이 종료될 때(실패, 취소 등) 채널을 닫기 때문입니다.

```kotlin
@Test
fun main(): Unit = runBlocking {
    val channel = produceNumbers(5)
    channel.consumeEach {
        println("Consume $it")
    }
}

fun CoroutineScope.produceNumbers(
    max: Int = 5
): ReceiveChannel<Int> = produce {
    var x = 0
    while (x < max) send(x++)
}

// 출력 결과
Consume 0
Consume 1
Consume 2
Consume 3
Consume 4
```

> 프로듀서와 리시버의 수가 제한되어 있지 않습니다. 다중 컨슈머 다중 프로듀서 가능하기에 코루틴에서 내부의 카프카와 비슷

## 채널 타입

#### 채널 생성자

```kotlin
public fun <E> Channel(
    capacity: Int = RENDEZVOUS,
    onBufferOverflow: BufferOverflow = BufferOverflow.SUSPEND,
    onUndeliveredElement: ((E) -> Unit)? = null
): Channel<E>
```

채널 용량 크기에 따라 설정이 달라집니다.

- `Unlimited`
  - 무제한 용량 버퍼로 `send`가 중단되지 않습니다.
- `Buffered`
  - 기본값 64
- `Rendezvous`
  - 기다리는 수신자가 있을 때만 송신자가 송신 (없으면 바로 suspend)
- `Conflated`
  - 크기가 1인 채널이며, 새로운 원소가 이전 원소를 대체합니다. 


## 오버 플로우 커스텀

버퍼가 오버플로우일 때 행동을 정의할 수 잇습니다.

- SUSPEND (기본 값) : `send`메소드 중단
- DROP_OLDEST : `QUEUE`
- DROP_LATEST : `STACK`

> Conflated는 버퍼사이즈 1 + DROP_OLDEST


## 전달되지 않은 원소 핸들러

채널의 파라미터로 `onUndeliveredElement`가 있습니다.

이는 원소가 정상적으로 처리되지 않을 때 호출되는 콜백입니다.

대부분은 채널이 닫히거나 취소되었음을 의미하지만, `send`, `receive`, `hasNext`등이 에러를 던질 때 발생할 수도 있습니다. 보통 채널에서 자원을 닫을 때 사용합니다.

```kotlin
    val channel = Channel<Int>(
        capacity = 64,
        onUndeliveredElement = {
            println("메시지 전송 중 오류")
        }
    )
```

위와 같은 채널이 있을 때
```kotlin
launch {
	repeat(5) {
    	println("send : $it")
		channel.send(it)
	}
}


launch {
    channel.consumeEach {
        println("Receive : $it")
        try {
            if (it == 2) {
                channel.close()    // #1
                return@consumeEach  // #2
                return@launch        // #3
                throw IllegalArgumentException("someError") // #4
            }
        } catch (e: Exception) {
            println("Channel is Stopped")
            e.printStackTrace()
        }
    }
}
```


- `#1`, `#2`, `#4`

```kotlin
// 출력 결과
Send : 0
Send : 1
Send : 2
Send : 3
Send : 4
Receive : 0
Receive : 1
Receive : 2
java.lang.IllegalArgumentException: Test // Why?
Receive : 3
Receive : 4
```

- `onUndeliveredElement` 콜백 실행 X
- `consume`이 멈춰지지도 않음

이유를 찾아보니 `return@consumeEach`를 사용하거나 `close()`를 해도 채널이 닫혀서 `send`가 안될 뿐 닫힌 채널의 데이터를 계속 컨슘 합니다. 따라서 원소가 정상적으로 처리되는 것으로 판정 `onUndeliveredElement` 콜백 X

__따라서 소비자 코루틴 자체를 종료해야 합니다__

```kotlin
launch {
    channel.consumeEach {
        println("Receive : $it")
        if (it == 2) {
            return@launch
        }
    }
}

// 출력 결과
Send : 0
Send : 1
Send : 2
Send : 3
Send : 4
Receive : 0
Receive : 1
Receive : 2
메시지 전송 중 오류
메시지 전송 중 오류
```

## 팬 아웃(Fan-out)

여러개의 코루틴이 하나의 채널로부터 원소를 받을 수도 있습니다. 

```
코루틴#1 ->  채널  -> 수신1 소비자 #1
			     -> 수신2 소비자 #2 
```

> 멀티 쓰레드에서 채널을 적절하게 처리하고자 한다면 for 루프를 사용해야 합니다.(consumeEach는 여러 개의 코루틴이 사용하기에는 안전하지 않습니다.) - 경쟁상태

같은 컨슈머 그룹내에 있다고 생각될 수 있지만 처리 속도와는 관계없이 원소는 공정하게 배분됩니다. 

```kotlin
@Test
fun main(): Unit = runBlocking {
    val channel = produceNumbers(10)
    repeat(5) { index ->
        launch {
            channel.consumeEach { number ->
            	delay(Random.nextLong(1000L))
                println("launch#$index is consume $number")
            }
        }
    }
}

private fun CoroutineScope.produceNumbers(
    max: Int = 5
): ReceiveChannel<Int> = produce {
    var x = 0
    while (x < max) send(x++)
}

// 출력 결과 - 처리 속도와는 별개로 공정하게 배분
launch#1 is consume 1
launch#3 is consume 3
launch#2 is consume 2
launch#4 is consume 4
launch#4 is consume 8
launch#1 is consume 5
launch#0 is consume 0
launch#2 is consume 7
launch#3 is consume 6
launch#4 is consume 9
```

각 채널은 코루틴들을 처리하는 `FIFO`큐를 활용해 처리합니다.

## 팬 인(Fan-in)

여러개의 코루틴이 하나의 채널로 원소를 전송할 수 있습니다.

```
코루틴#1 ->  채널  -> 수신1 소비자 #1
코루틴#2 ->	     
```

`fanIn`은 개념이며 `fanIn`이라는 확장함수가 `kotlin`에 정의되어 있지 않음

```kotlin
@Test
fun main(): Unit = runBlocking {
    val channel = sendString("channel#1")
    val channel2 = sendString("channel#2")

    val totalChannel = fanIn(listOf(channel, channel2))
    totalChannel.consumeEach {
        println(it)
    }
}

private fun <T> CoroutineScope.fanIn(
    channels: List<ReceiveChannel<T>>
) = produce<T> {
    for (channel in channels) {
        launch {
            for (element in channel) {
                send(element)
            }
        }
    }
}

private suspend fun CoroutineScope.sendString(title: String): ReceiveChannel<String> =
    produce {
        repeat(5) {
            delay(Random.nextLong(100L))
            send("$title produce $it")
        }
    }
    
// 출력 결과
channel#2 produce 0
channel#1 produce 0
channel#2 produce 1
channel#2 produce 2
channel#1 produce 1
channel#1 produce 2
channel#2 produce 3
channel#2 produce 4
channel#1 produce 3
channel#1 produce 4
```

## 파이프라인

한 채널로부터 원소를 다른 채널로 전송하는 것을 파이프라인이라고 합니다.

```kotlin
@Test
fun main() = runBlocking {
    val numbers = generateNum()
    val squared = square(numbers)
    for (num in squared) {
        println(num)
    }
}

fun CoroutineScope.generateNum() = produce<Int> {
    repeat(3) {
        send(it + 1)
    }
}

fun CoroutineScope.square(numbers: ReceiveChannel<Int>) = produce<Int> {
    for (num in numbers) {
        send(num * num)
    }
}
```

채널은 서로 다른 코루틴이 통신할 때 유용합니다. 

> 이는 공유상태로 인한 문제가 일어나지 않습니다.

### 사용처

채널은 특정 작업에 사용되는 코루틴의 수를 조절하는 파이프라인을 설정할 때 사용할 수 있습니다.

> A라는 작업이 평균 소요시간이 5초이고, B라는 작업의 평균 소요시간은 2초라면
> 
> `A -> Channel -> B` 형태로 구성함으로써
> 
> A에서 20개의 코루틴으로 send()하고, B에서 5개의 코루틴으로 consume하면 밸런스있게 프로세스 처리가 가능할 것입니다.

_안드로이드의 경우 스레드 안정성이 필요한 이벤트의 경우는 `Channel`을 활용해 순차적으로 이벤트를 처리하지만, 대부분의 `UI`업데이트에서는 최신의 정보만을 노출하면 되기에`Flow`와 `collectLatest`를 활용하는 방식으로 진행합니다. (Flow에 관해서는 뒷장에서 설명)_

## 요약

채널은 코루틴끼리 통신할 때 사용할 수 있는 강력한 도구입니다. 특징으로써는

- 채널을 통해 보내진 데이터는 단 한 번 받는 것이 보장됩니다.
  - 실패했을 때 콜백도 달 수 있습니다.
- `produce`빌더를 활용해 채널을 생성하는 것을 권장
  - `Channel`을 활용하면 수동으로 닫아주어야 하며, 닫지 않으면 함수가 종료되지 않고 무한정 `consume`하는 상황 발생
- 특정 작업에 사용되는 코루틴의 수를 조절하는 파이프라인을 설정할 때 사용할 수 있습니다.
 








