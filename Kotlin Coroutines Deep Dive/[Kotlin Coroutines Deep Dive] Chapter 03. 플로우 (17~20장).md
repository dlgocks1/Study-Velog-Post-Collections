# 17장 셀렉트

> `select`란?
> 
> 가장 먼저 완료되는 코루틴의 결과를 기다리는 함수이다. 아래에 더 정확히 설명

## 지연되는 값 선택하기

바로 예제

```kotlin
suspend fun requestData1() : String {
	delay(100000L)
	return "Data1"
}

suspend fun requestData2() : String {
	delay(1000L)
	return "Data2"
}

suspend fun askMultipleForData(): String = coroutineScope {
	val data1 = async { requestData1() }
	val data2 = async { requestData2() }
	select {
		data1.onAwait { it }
		data2.onAwait { it }
	}
}

@Test
fun main() = runTest {
	println(askMultipleForData())
}

// 출력
(1초 후)
Data2
```

`select`는 내부 스코프에서 가장 먼저 완료되는 값을 기다림. 하지만 `select`를 사용하면 명시적으로 코루틴을 닫아야 함

```kotlin
suspend fun askMultipleForData(): String = coroutineScope {
	val data1 = async { requestData1() }
	val data2 = async { requestData2() }
	select {
		data1.onAwait { it }
		data2.onAwait { it }
	}.also {
		coroutineContext.cancelChildren()
	}
}
```

## 채널에서 값 선택하기

채널에서도 `select`를 똑같이 사용할 수 있음. 설렉트와 함께 사용하는 채널의 주요 함수는 다음과 같음

- `onReceive` : 채널이 값을 가지고 있을 때 선택됨
- `onReceiveCatching` : 채널이 값을 가지고 있거나 닫혔을 때 선택됨 (람다 인자로 값 가져옴)
- `onSend` : 채널의 버퍼에 공간이 있을 때 선택됨

> 즉 설렉트 람다 내부에서 다양한 채널의 여러 값을 `onReceive`할 때 가장 먼저 채널에 들어간 값을 가져옴 (FIFO)


```kotlin
suspend fun CoroutineScope.produceString(
	s: String,
	time: Long
) = produce {
	while (true) {
		delay(time)
		send(s)
	}
}

@Test
fun main() = runBlocking {
	val fooChannel = produceString("foo", 201L)
	val barChannel = produceString("bar", 500L)

	repeat(7) {
		select {
			fooChannel.onReceive {
				println("Receive From Foo : $it")
			}
			barChannel.onReceive {
				println("Receive From Bar : $it")
			}
		}
	}

	coroutineContext.cancelChildren()
}

// 출력 
Receive From Foo : foo
Receive From Foo : foo
Receive From Bar : bar
Receive From Foo : foo
Receive From Foo : foo
Receive From Foo : foo
Receive From Bar : bar
```

`onSend`를 호출하여 버퍼에 공간이 있는 채널을 선택해 데이터를 보낼 수도 있음

```kotlin
@Test
fun main() = runTest {
	val c1 = Channel<Char>(capacity = 2)
	val c2 = Channel<Char>(capacity = 2)

	launch {
		for (c in 'A'..'H'){
			delay(400)
			select<Unit> {
				c1.onSend(c) {
					println("Send $c to C1")
				}
				c2.onSend(c) {
					println("Send $c to C2")
				}
			}
		}
	}

	launch {
		while (true) {
			delay(1000)
			val c = select<String> {
				c1.onReceive { "$it from C1"}
				c2.onReceive { "$it from C2"}
			}
			println(c)
		}
	}
}

// 출력
Send A to C1
Send B to C1
A from C1
Send C to C1
Send D to C2
B from C1
Send E to C1
Send F to C2
C from C1
Send G to C1
E from C1
Send H to C1
G from C1
H from C1
D from C2
F from C2
```

## 요약

먼저 완료되는 코루틴의 결괏값을 기다릴 때나, 여러 개의 채널 중 전송 또는 수신 가능한 채널을 선택할 때 유용함. 

`async`와 사용을 통해 다양한 패턴을 구현할 수도 있음


# 18장 핫 데이터 소스와 콜드 데이터 소스

코루틴의 채널은 핫 스트림이다. 하지만 필요할 때 데이터를 생성하는 데이터 스트림으로 사용할 수 없기에 콜드 스트림이 등장하게 됨.

|핫|콜드|
|---|---|
|컬렉션(List, Set)|Sequence, Stream|
|Channel|Flow, RxJava|


## 핫 vs 콜드

- 핫 스트림은 구독자와 무관하게 데이터를 생성함 -> 즉 상태가 있음
- 콜드 스트림은 게을러서 구독자가 있을 때만 작업을 수행 함

```kotlin
val s = sequence {
	var x = 0
    while(true) {
    	println("send $x")
        yield(x++)
	}
}
```

콜드 스트림은 따라서 다음과 같은 특징을 지님

- 무한할 수 있으며
- 최소한의 연산만 수행하며
- 메모리를 적게 사용함(중간 컬렉션을 생성하지 않음)

시퀀스의 경우 최종 연산(`toList`, `take`, `first` 등)이 모든 작업을 수행함 따라서 이는 찾아야하는 원소의 숫자가 정해져 있을 때 큰 성능향상을 이룸

자바의 스트림과 동일하다고 보아도 됨

## 핫 채널, 콜드 플로우

플로우를 생성하는 방법은 `produce`와 동일 함

```kotlin
val channel = produce {
	whilte (true) {
    	val x= computeNextValue()
        send(x)
    }
}

val flow = flow {
	while (true) {
    	val x = computeNextValue()
        emit(x)
    }
}
```

### 채널은

채널은 핫이라 값을 곧바로 계산함 따라서 `produce`는 `CoroutineScope`의 확장 함수로 정의되어 있는 코루틴의 빌더가 되어 채널 코루틴을 만들고, 채널의 `cappacity`만큼 값을 큐에 넣음

이러한 값들을 채널은 한 소비자에게 하나의 값이 전달되는 것이 보장되기 때문에 소비자1, 소비자2가 각각 다른 값을 할당 받을 수 밖에 없음


### 플로우는

콜드 데이터 소스이기 때문에 값을 필요할 때만 생성함. 따라서 `flow`는 코루틴 빌더가 아니며 어떤 처리도 하지 않음

`collect`와 같은 구독자가 발행될 때 원소가 생성되고 방출되는 방식을 정의할 뿐임. 따라서 `flow`는 정지 함수내부에서 선언되지 않아도 됨

`flow`빌더는 빌더를 호출한 최종 연산의 스코프에서 실행 됨 (`Unconfined`와 동일) 또한 플로우의 각 구독자는 처음부터 데이터를 받기 시작함 

```kotlin
private fun makeFlow() = flow {
	println("Flow started")
    for (i in 1..3) {
    	delay(1000)
        emit(i)
    }
}

fun main() = runBlocking {
	val flow = makeFlow()
    
    delay(1000)
    println("플로우 구독자 발행")
    flow.collect { println(it) }
    println("플로우 또 다른 구독자 발행 ")
    flow.collect { println(it) }
}

// 출력 결과
플로우 구독자 발행
Flow started
1
2
3
플로우 또 다른 구독자 발행 
Flow started
1
2
3
```

`Flow`와 `RxJava`는 사실상 동일하게 작동함 근데 좀 더 우아하게 사용하고자 한다면 코루틴을 활용할 것

## 요약

- `핫 데이터`는 열정적임 
	가능한 빨리 원소를 만들고 저장하며, 원소가 소비되는 것과 무관하게 생성함

- `콜드 데이터`는 게으름
 	최종 연산에서 값이 필요할 때가 되어서야 처리함(구독자가 있을 때) 따라서 연산을 최소한으로 수행 함
    
    
# 19장 플로우란 무엇인가?

> 플로우란 비동기적으로 계산해야 할 값의 스트림을 나타냅니다.


```kotlin
interface Flow<out T> {
	suspend fun collect(collector: FLowCollector<T>)
}
```

`Flow`의 유일한 멤버 함수는 `collect`임. 다른 함수들은 확장 함수로 정의되어 있음

## 플로우와 값들을 나타내는 다른 방법들의 비교

콜드 스트림, 즉 플로우 개념은 리액터나 `RxJava`와 비슷함 

`User`정보를 가져와 다른 `DB`를 찔러서 유저 프로필 정보를 가져오는 예시를 생각해보자.

```kotlin
fun getList(): List<Int> = List(3) {
	Thread.sleep(1000) // IO 대기시간
	it
}

fun getProfile(users: Int): String {
	Thread.sleep(1000) // IO 대기시간
	return "User Prfile :$users"
}

@Test
fun main() {
	println("함수 시작..")
    val list = getList()
	list.forEach {
		println(getProfile(it))
	}
}

// 
함수 시작..
(3초 후)
(1초 후)
User Prfile :0
(1초 후)
User Prfile :1
(1초 후)
User Prfile :2
```

`List`, `Set`과 같은 핫 데이터는 모든 원소에 대한 계산은 완료한 후 값을 반환한다. 따라서 출력결과와 동일하게 총 6초 이상의 시간이 걸리게 된다.

하지만 시퀀스(플로우)의 경우 이런 CPU 집약적인 연산 또는 블로킹 연산일 때 필요할 때 마다 값을 계산하기에 좀 더 용이하다.

```kotlin
fun getList(): Sequence<Int> = sequence {
	repeat(3){
		Thread.sleep(1000) // IO 대기시간
		yield(it)
	}
}

fun getProfile(users: Int): String {
	Thread.sleep(1000) // IO 대기시간
	return "User Prfile :$users"
}

@Test
fun main() {
	val list = getList()
	println("함수 시작..")
	list.forEach {
		println(getProfile(it))
	}
}
// 출력
함수 시작..
(2초 후)
User Prfile :0
(2초 후)
User Prfile :1
(2초 후)
User Prfile :2
```

하지만 시퀀스의 경우 시퀀스 빌더의 스코프(`SequenceScope`) 리시버에서는 `yield`, `yieldAll` 이외의 중단 함수를 실행할 수 없다.

```kotlin
fun getSequence(): Sequence<String> = seqence {
	repeat(3) {
    	delay(1000L) // 컴파일 에러가 발생합니다.
        yield("User$it")
    }
}
```

이는 라이브러리 자체에서 시퀀스를 이렇게 사용하지 말라고 막아 둔 것

시퀀스는 데이터의 개수가 무한정으로 많거나, 원소가 무거운 경우, 컬렉션의 원소가 몇 개만 필요할 때 등 지연 연산을 하게 되는 상황에 쓰이도록 만들어짐

따라서 지연이 있는 경우는 플로우를 활용할 수 있다. 플로우의 빌더와 연산은 중단 함수이며 구조화된 동시성과 적절한 예외처리까지 지원한다. 

_`webFlux`에서의 `mono`와 `flux`도 `asFlow`로의 치환을 제공한다._


따라서 플로우의 구독은 코루틴 스코프에서 실행되어야 한다. 플로우의 확장함수 중

- `first()`를 통해 첫 번째 페이지
- `toList()`를 통해 모든 페이지
- `find { it.id == id }`를 통해 원하는 사용자를 찾을 때 까지

페이지를 받아올 수 있다.

## 플로우의 특징
 
 `collect`와 같은 플로우의 최종 연산은 코루틴을 중단 시킨다. 따라서 플로우 처리는 취소도 가능하며, 구조화된 동시성도 제공한다.
 
 > 다시한번 말하지만 flow 빌더는 중단 함수가 아니며, 구독자에 의해 연산이 실행될 때 부모의 콘텍스트에서 그대로 실행되게 된다. 구독자의 경우 중단함수 내부(코루틴 스코프)에서 구독을 해야 한다.
 
코루틴 컨텍스트는 `collect`에서 `flow` 빌더의 람다 표현식으로 전달 되며, 코루틴이 취소되면 플로우도 적절하게 취소됨

```kotlin
fun usersFlow(): Flow<String> = flow {
	repeat(3) {
		delay(1000L)
		val ctx = currentCoroutineContext()
		val name = ctx[CoroutineName]?.name
		emit(("User$it in $name"))
	}
}

@Test
fun main() = runTest {
	val users = usersFlow()
	withContext(CoroutineName("NameTest")) {
		val job = launch { users.collect { println(it) } }
		launch {
			delay(2100L)
			println("2100L After Cancel Job")
			job.cancel()
		}
	}
}

// 출력 결과
User0 in NameTest // 코루틴 콘텍스트가 그대로 넘어감
User1 in NameTest
2100L After Cancel Job
```
  
 ## 플로우 명명법
 
- 플로우는 어디선가 시작되어야 함. 
- 플로우의 마지막 연산은 최종 연산이라 불리며, 중단 가능하거나 스코프를 필요로 한다. 
- 시작 연산과 최종 연산사이에 중간 연산을 가질 수 있음

```kotlin
flow { eimit("someValue") }
	.onEach {}
    .onStart {]
    .onCompletion {}
    .catch {}
    .collect {}
```

## 실제 사용 예

많은 데이터를 가져올 때 `async`를 활용하여 비동기적으로 작업하기도 하지만, 데이터량이 많을 때는 쉽지 않다. 이때 플로우와 `flatMapMerger`를 활용하여 동시성을 제한하면서 데이터를 가져올 수 있다.

```kotlin
suspend fun getOffers(
	sellers : List<Seller>
): List<Offer> = sellers
	.asFlow()
    .flatMapMerge(concurrency = 20) { seller -> 
    	// 동시 호출의 수를 20으로 제한하여 각각의 seller에 대한 정보를 가져온다.
    	suspend { api.requestOffers(sellers.id) }.asFlow()
    }
    .toList()
```
컬렉션 대신 플로우를 활용하면 동시 처리, 컨텍스트, 예외를 비롯한 많은 것을 조절할 수 있다.


## 요약

플로우는 시퀀스와 달리 코루틴을 지원하며 비동기적으로 계산되는 값을 나타낸다. 플로우는 일반적인 컬렉션에 비해 더 싸고 효율적으로 작동한다.

# 20장 플로우의 실제 구현

플로우의 내부구현에 대해 알아보자.

## Flow 이해하기

간단한 람다식

```kotlin
@Test
fun main() = runTest {
    val f: () -> Unit = {
        println("A")
        println("B")
        println("C")
    }

    f()
}

// 출력 겨로가
A
B
C
```

플로우는 위의 람다식과 별반 다를것이 없다.

아래는 실제 플로우의 내부 구현을 간단하게 구현해본 것이다.

```kotlin
@Test
fun main() = runTest {
    val f: suspend ((String) -> Unit) -> Unit = { emit ->
        emit("A")
        emit("B")
        emit("C")
    }

    f { println(it) }
    f { println(it) }
}

// 출력 결과
A
B
C
A
B
C
```

내부 구성이 복잡하니까 함수인터페이스로 추출한다.

```kotlin
fun interface FlowCollector {
    suspend fun emit(string: String)
}

@Test
fun main() = runTest {
    val f: suspend (FlowCollector) -> Unit = {
        it.emit("A")
        it.emit("B")
        it.emit("C")
    }

    f { println(it) }
    f { println(it) }
}
```

위의 식은 `it`을 쓰기도 귀찮기에 리시버로 `FlowCollector`를 사용하면 다음과 같다.

```kotlin
@Test
fun main() = runTest {
    val f: suspend FlowCollector.() -> Unit = {
        emit("A")
        emit("B")
        emit("C")
    }

    f { println(it) }
    f { println(it) }
}
```

어디서 많이 본 형태이지 않은가? 하지만 이렇게 람다식을 전달하는 것 대신에 인터페이스를 구현하는 편이 더 낫다. (실제 플로우도 이렇게 구현되어 있다.)

```kotlin
fun interface FlowCollector {
    suspend fun emit(string: String)
}

interface Flow {
    suspend fun collect(collector: FlowCollector)
}

fun flow(
    builder: suspend FlowCollector.() -> Unit
) = object : Flow {
    override suspend fun collect(collector: FlowCollector) = builder {
        collector.emit(it)
    }
}

@Test
fun main() = runTest {
    val f = flow {
        emit("A")
        emit("B")
        emit("C")
    }

    f.collect { println(it) }
    f.collect { println(it) }
}
```

위의 형태가 실제 플로우의 구현 방식이라고 보아도 좋다. `collect`를 호출하면 `flow`빌더를 호출할 때 넣은 람다식이 실행된다.

다른 빌더들도 위와같은 형태로 `flow`를 빌드한다.

```kotlin
@FlowPreview
public fun <T> (suspend () -> T).asFlow(): Flow<T> = flow {
    emit(invoke())
}

public fun <T> Iterable<T>.asFlow(): Flow<T> = flow {
    forEach { value ->
        emit(value)
    }
}

public fun <T> Iterator<T>.asFlow(): Flow<T> = flow {
    forEach { value ->
        emit(value)
    }
}

public fun <T> Sequence<T>.asFlow(): Flow<T> = flow {
    forEach { value ->
        emit(value)
    }
}
```

## Flow 처리 방식

플로우는 그냥 람다식에 비해 훨씬 복잡하다고 여겨진다. 하지만 플로우의 강력한 점은 플로우를 생성하고, 처리하고, 감지하기 위해 정의한 함수에서 찾을 수 있다.

```kotlin
@Test
fun main() = runBlocking {

    flowOf("A", "B", "C")
        .map {
            delay(1000L)
            it.lowercase()
        }.collect {
            println(it)
        }
}

// 출력 결과
(1초 후)
a
(1초 후)
b
(1초 후)
c
```

플로우는 다양한 형태의 확장함수를 처리할 수 있도록 제공하고 있으며 이는 다음과 같이 비슷한 형태로 제공된다.

```kotlin
public fun <T> Flow<T>.onEach(action: suspend (T) -> Unit): Flow<T> = transform { value ->
    action(value)
    return@transform emit(value)
}

public inline fun <T, R> Flow<T>.map(crossinline transform: suspend (value: T) -> R): Flow<R> = transform { value ->
    return@transform emit(transform(value))
}

internal inline fun <T, R> Flow<T>.unsafeTransform(
    @BuilderInference crossinline transform: suspend FlowCollector<R>.(value: T) -> Unit
): Flow<R> = unsafeFlow { // Note: unsafe flow is used here, because unsafeTransform is only for internal use
    collect { value ->
        return@collect transform(value)
    }
}
```

## 동기로 작동하는 flow

플로우 또한 중단 함수처럼 동기로 작동하기에 플로우가 완료될 때 까지 `collect`의 호출이 중단된다. 

즉, 하나의 원소가 `collect`되기 전까지 내부는 동기적으로 작동함  (플로우는 새로운 코루틴을 시작하지 않는다.)

다음 예를 보면 될 듯

```kotlin
    flowOf("A", "B", "C")
        .map {
            delay(1000L)
            it.lowercase()
        }.collect {
            println(it)
        }
```

## 플로우와 공유상태

플로우를 활용할 때는 경쟁상태를 생각해야 한다.

하나의 플로우내부에서는 동기적으로 작동하기에 큰 문제가 없지만, 

> 다양한 플로우에서 사용하는 외부 변수는 동기화가 필수이며 플로우 컬렉션이 아니라 플로우에 종속되게 된다.

다음 예를 보자.


```kotlin
fun Flow<Int>.counter(): Flow<Int> {
    var counter = 0
    return this.map {
        counter++
        List(10000) { Random.nextLong() }.shuffled().sorted() // 특정 작업 수행
        counter
    }
}

@Test
fun main() = runTest {
    launch(Dispatchers.Default) {
        val f1 = List(1_000) { it }.asFlow()
        val f2 = List(1_000) { it }.asFlow().counter()

        launch { println(f1.counter().last()) }
        launch { println(f1.counter().last()) }
        launch { println(f2.last()) }
        launch { println(f2.last()) }
    }
}
// 출력 결과
1000
1000
1991 // 2000보다 작은 값
1999 // 2000보다 작은 값
```

_주의 `Dispatcher.Default`를 통하지 않으면 단일 쓰레드에서 테스트가 돌아가기에 2000이라는 정확한 값이 출력 됨_

두개의 코루틴이 병렬로 원소를 세게 되어 `f2.last()`는 2000을 반환하게 되는 것이 맞지만 2000을 정확하게 반환하지는 않고(변수를 공유하기에) 2000보다 작은 값을 반환하게 됩니다.

> 따라서 플로우에서 사용하는 변수가 함수 외부, 클래스의 스코프, 최상위 래벨등에 정의되어 있으면 동기화가 필요합니다.

```kotlin
var counter = 0
fun Flow<Int>.counter(): Flow<Int> {
    return this.map {
        counter++
        List(10000) { Random.nextLong() }.shuffled().sorted() // 특정 작업 수행
        counter
    }
}

@Test
fun main() = runTest {
    launch(Dispatchers.Default) {
        val f1 = List(1_000) { it }.asFlow()
        val f2 = List(1_000) { it }.asFlow().counter()

        launch { println(f1.counter().last()) }
        launch { println(f1.counter().last()) }
        launch { println(f2.last()) }
        launch { println(f2.last()) }
    }
}

// 출력 결과
3968 // 4000보다 작은 값들
3968
3982
3998
```

## 요약

Flow는 리시버를 가진 중단 람다식보다 조금 더 복잡하지만, 다양한 확장함수를 통해 데코레이트하여 유용하게 활용할 수 있습니다.


