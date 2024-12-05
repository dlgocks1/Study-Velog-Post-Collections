## 16.1 플로우은 순차적인 값 스트림을 모델링한다.

14장에서 설명한 것처럼 일시 중단 함수는 한 번 또는 여러 번 실행을 일시 중지할 수 있다. 여러번 일시중지 할 수 있지만 반환값은 객체 또는 객체 컬렉션과 같은 단일 값만 반환할 수 있다.

```kotlin
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlin.time.Duration.Companion.seconds

suspend fun createValues(): List<Int> {
    return buildList {
        add(1)
        delay(1.seconds)
        add(2)
        delay(1.seconds)
        add(3)
        delay(1.seconds)
	} 
}

fun main() = runBlocking {
    val list = createValues()
    list.forEach {
		log(it) 
	}
}

// 3099 [main @coroutine#1] 1
// 3107 [main @coroutine#1] 2
// 3107 [main @coroutine#1] 3
```

그러나 실제 `createValues` 함수의 구현을 살펴보면 요소 1은 실제로 즉시 사용 가능 했음을 알 수 있다. 이와 같이 함수가 오랜 시간에 걸쳐 여러 값을 계산하는 시나리오에서는 함수 실행이 끝났을 때만 값을 반환하는 것이 아니라 값이 사용 가능해지면 비동기적으로 반환하고 싶을 수 있다. 
이때 플로우가 유용하다.


### 16.1.1 플로우를 사용하면 요소가 방출되는 대로 작업할 수 있다. 

`createValues` 함수를 플로우를 사용하도록 다시 작성해보겠다.

```kotlin
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.flow.*
import kotlin.time.Duration.Companion.milliseconds

fun createValues(): Flow<Int> {
    return flow {
        emit(1)
        delay(1000.milliseconds)
        emit(2)
        delay(1000.milliseconds)
        emit(3)
        delay(1000.milliseconds)
	} 
}

fun main() = runBlocking {
    val myFlowOfValues = createValues()
    myFlowOfValues.collect { log(it) }
}

// 29 [main @coroutine#1] 1
// 1100 [main @coroutine#1] 2
// 2156 [main @coroutine#1] 3
```

출력의 타임스탬프를 살펴보면 플로우의 요소가 배출되는 즉시 표시되는 것을 빠르게 확인할 수 있다. 코드는 모든 값이 계산될 때까지 기다릴 필요가 없습니다. 요소의 전체 배치가 생성될 때까지 기다릴 필요 없이 값이 계산되는 즉시 작업할 수 있는 이 기본적인 추상화는 `Kotlin`의 플로우의 핵심이다.

### 16.1.2 Kotlin의 다양한 Flow 유형

`Kotlin`에서는 `cold flow` 및 `hot flow`라는 두 가지 범주의 `flow`를 제공한다.

- `cold flow`는 컨슈머에 의해 항목이 소비될 때만 항목이 전송되기 시작하는 비동기 데이터 스트림을 나타낸다.
- `hot flow`는 아이템이 실제로 소비되는지 여부와 관계없이 아이템을 생산하며 방송 방식으로 진행된다.


## 16.2 콜드 플로우

### 16.2.1 플로우 빌더 기능으로 콜드 플로우 만들기

콜드 플로우의 빌더 함수의 블록 내부에서 특수한 `emit` 함수를 호출하여 `flow`의 콜렉터에게 값을 제공하고 콜렉터가 값을 처리할 때까지 빌더 함수의 실행을 일시 중단할 수 있는데, 이를 비동기 반환이라고 생각하면 된다. 

`flow`는 서스펜드 수정자를 사용하여 블록을 선언하므로 빌더 내에서 지연과 같은 다른 서스펜딩 함수를 호출할 수도 있다.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlin.time.Duration.Companion.milliseconds

fun main() {
    val letters = flow {
        log("Emitting A!")
        emit("A")
        delay(200.milliseconds)
        log("Emitting B!")
        emit("B")
	}
}
```

이 코드를 실행하면 실제로 어떤 출력도 볼 수 없다는 점에 주목할 필요가 있다. 빌더 함수는 `Flow<T>` 타입의 객체를 반환하고 시퀀스와 마찬가지로 이 플로우는 처음에는 비활성 상태이다.

계산을 시작하는 플로우에서 터미널 연산자와 그 앞에 오는 다른 중간 연산자가 호출될 때 까지 실제로 실행되지 않는다. 

플로우 빌더 함수를 호출해도 실제로 작업이 트리거되지 않으므로 일시 중단되지 않는 "일반" `Kotlin` 코드로 플로우를 작성할 수 있다. 

```kotlin
 import kotlinx.coroutines.flow.*
 
 fun getElementsFromNetwork(): Flow<String> {
 	return flow {
    	// suspending network call here
	}
}
```

빌더 함수 내부의 코드는 한 번만 실행되므로 6장에서 살펴본 것처럼 시퀀스처럼 무한한 플로우를 정의하고 반환해도 괜찮다. 

```kotlin
val counterFlow = flow {
	var x = 0
    while (true) {
    	emit(x++)
        delay(200.milliseconds)
	}
}
```

### 16.2.2 콜드 플로우는 수집될 때까지 아무런 작업도 수행하지 않는다.

플로우에서 수집함수를 호출하면 해당 로직이 실행되며, 플로우 빌더 내부의 코드가 시작되게 된다. (수집하는 코드를 일반적으로 수집기라고 한다.) 

플로우을 수집하는 것은 실제로 플로우 내부에서 일시 중단 코드를 실행하기 때문에 수집은 일시 중단 함수이며 플로우가 완료될 때까지 일시 중단된다. 마찬가 지로 수집기에 전달된 람다도 일시 중단될 수 있으며, 이를 통해 추가 일시 중단 함수를 호출할 수 있다. 

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlin.time.Duration.Companion.milliseconds

val letters = flow {
	log("Emitting A!")
    emit("A")
    delay(200.milliseconds)
    log("Emitting B!")
    emit("B")
}

fun main() = runBlocking {
    letters.collect {
        log("Collecting $it")
        delay(500.milliseconds)
    }
}

// 27 [main @coroutine#1] Emitting A!
// 38 [main @coroutine#1] Collecting A
// 757 [main @coroutine#1] Emitting B!
// 757 [main @coroutine#1] Collecting B
```

출력의 타임스탬프를 살펴보면 수집기가 플로우의 로직을 실행하는 책임이 있다는 것을 다시 한 번 알 수 있다. 요소 A와 B의 수집 사이의 지연 시간은 약 700밀리초이다. 이는 다음과 같은 일련의 이벤트가 발생하기 때문이다:

- 수집기(`collector`)는 플로우 빌더에 정의된 로직을 트리거하여 첫 번째 배출을 요구한다.
- 수집기와 연결된 람다가 호출되어 메시지를 로깅하고 500밀리초 동안 지연된다.
- 그 이후 플로우람다가 계속 진행되어 200밀리초 동안 더 지연된 후 방출 이 발생한다.

![](https://velog.velcdn.com/images/cksgodl/post/8b3fc09d-63db-40c7-8402-26671be931db/image.png)

터미널 연산자를 사용할 때마다 시퀀스가 재평가되는 것처럼 콜드 플로우에서 수집 을 여러번 호출하면 해당 코드가 여러번 실행된다는점에 유의할 필요가 있다. 

```kotlin
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.*
import kotlin.time.Duration.Companion.milliseconds

fun main() = runBlocking {
	letters.collect {
    	log("(1) Collecting $it")
        delay(500.milliseconds)
	}
    letters.collect {
    	log("(2) Collecting $it")
        delay(500.milliseconds)
	} 
}

// 23 [main @coroutine#1] Emitting A!
// 33 [main @coroutine#1] (1) Collecting A
// 761 [main @coroutine#1] Emitting B!
// 762 [main @coroutine#1] (1) Collecting B
// 1335 [main @coroutine#1] Emitting A!
// 1335 [main @coroutine#1] (2) Collecting A
// 2096 [main @coroutine#1] Emitting B!
// 2096 [main @coroutine#1] (2) Collecting B
```

수집 함수는 플로우의 모든 요소가 처리될 때까지 일시 중단된다. 모든 요소가 처리되기 전에 플로우 수집을 중지하려면 플로우를 취소하면 된다.

### 16.2.3 플로우 수집 취소하기

이미 15장에서 코루틴을 취소하는 메커니즘에 대해 알아보았다. 이 메커니즘은 플로우 수집기에도 적용된다.

```kotlin
 import kotlinx.coroutines.flow.*
 import kotlinx.coroutines.*
 import kotlin.time.Duration.Companion.seconds
 
 fun main() = runBlocking {
 	val collector = launch {
	    counterFlow.collect {
    		println(it)
		} 
	}
    delay(5.seconds)
    collector.cancel()
}
// 1 2 3 ... 24
```

### 16.2.4 후드 아래로 흐르는 cold flow

플로우를 사용하는 데 내부 작동에 대한 지식이 반드시 필요한 것은 아니지만 콜드 플로우와 그 메커니즘을 더 잘 이해하는 데 도움이 될 수 있다.

`Kotlin`의 콜드 플로우는 이전 챕터에서 이미 알게 된 두 언어 기능인 정지 함수와 람다와 수신기의 영리한 조합이다. 

코루틴에서 제공하는 콜드 플로우의 정의는 실제로 몇 줄에 불과하며 두 개의 인터페이스만 필요하다. `Flow`와 `FlowCollector`. 이들은 각각 수집과 방출이라는 하나의 함수만 정의한다:

```kotlin
interface Flow<out T> {
    suspend fun collect(collector: FlowCollector<T>)
}

interface FlowCollector<in T> {
    suspend fun emit(value: T)
}
```

플로우 빌더 함수를 사용하여 플로우를 정의할 때 제공하는 람다에는 수신자 유형이 `FlowCollector`이다. 이를 통해 빌더 내에서 `emit` 함수를 호출할 수 있다. `emit`함수는 수집 함수에 전달된 람다를 호출한다. 사실상 두 개의 람다가 서로를 호출하는 것이다:

- `collect`을 호출하면 `flowCollector` 함수의 본문이 호출
- 이 코드가 `emit`을 호출하면 전달된 매개변수와 함께 `collect`하도록 전달된 람다를 차례로 호출.
- 람다표현식 실행이 완료되면 함수는 다시 빌더함수의 본문으로 돌아가 실행을 계속한다.

예제로 나타내면 아래와 같다.

```kotlin
val letters = flow {
    delay(300.milliseconds)
    emit("A")
    delay(300.milliseconds)
    emit("B")
}
letters.collect { letter ->
    println(letter)
    delay(200.milliseconds)
}
```

![](https://velog.velcdn.com/images/cksgodl/post/ee098777-09f0-43c2-ae43-9c8d9ec1549e/image.png)

### 16.2.5 채널 플로우와 함꼐하는 동시성

지금까지 플로우 빌더 기능을 사용하여 만든 콜드 플로우는 모두 시퀀스이다. 코드는 일시 중단 함수의 본문과 마찬가지로 하나의 코루틴으로 실행된다. 따라서 호출도 순차적으로 실행된다.

플로우가 서로 독립적으로 실행될 수 있는 여러 계산을 수행하는 경우 이러한 순차적 특성이 병목 현상이 될 수 있다. 

```kotlin
 import kotlinx.coroutines.flow.*
 import kotlinx.coroutines.*
 import kotlin.random.Random
 import kotlin.time.Duration.Companion.milliseconds
 
 suspend fun getRandomNumber(): Int {
 	delay(500.milliseconds)
    return Random.nextInt()
}

val randomNumbers = flow {
	repeat(10) {
		emit(getRandomNumber())
	}
}
    
fun main() = runBlocking {
	randomNumbers.collect {
		log(it) 
	}
}

// 583 [main @coroutine#1] 1514439879
// 1120 [main @coroutine#1] 1785211458
// 1693 [main @coroutine#1] -996479986
// ...
// 5463 [main @coroutine#1] -2047597449
```

이 플로우를 수집하는데는 5초가 조금 넘게 걸리는데, 이는 각`getRandomNumber`호출이 차례로 실행되기 때문이다.

![](https://velog.velcdn.com/images/cksgodl/post/32436d83-871a-431d-90ff-302144ef798a/image.png)

플로우은 순차적으로 실행되며, 모든 계산은 동일한 코어에서 실행된다. 

하지만 위의 코드에서 수행하는 연산(숫자 생성)은 서로 종속적이지 않기 때문에 동시에 또는 원하는 경우 병렬로 수행하기에 이상적인 것처럼 보인다.

지금까지 배운 내용을 적용하여 백그라운드 코루틴을 실행하고 거기에서 직접 값을 출력하여 플로우 빌더 호출에 동시성을 도입하고 싶을 수 있다. 그러나 그렇게 하면 오류가 발생한다: `Flow invariant is violated: Emission from another coroutine is detected`.

`FlowCollector`는 스레드 안전하지 않으며 동시 방출이 금지되어 있다." 라는 메시지가 표시된다.

```kotlin
val randomNumbers = flow {
    coroutineScope {
        repeat(10) {
			// Error: emit can’t be called from a different coroutine.
            launch { emit(getRandomNumber()) }
			} 
		}
	}
```

기본적인 콜드 플로우 추상화에서는 동일한 코루틴에서 `emit` 함수를 호출하는 것만 허용하기 때문이다. 

따라서 여러 코루틴에서 방출을 허용하는 동시 플로우을 빌드할 수 있는 플로우빌더가 필요하다. `Kotlin`에서는 이를 `channelFlow`라고 하며, `channelFlow` 빌더 함수를 사용하여 구성할 수 있다. 

채널 플로우은 콜드 플로우의 특수한 유형이다. 이는 순차적 방출을 위한 방출 함수를 제공하지 않는다. 대신 여러 코루틴에서 `send`를 사용하여 값을 제공할 수 있다. 이 플로우의 수집기는 여전히 순차적으로 값을 수신하고 수 집 람다가 작업을 수행할 수 있다. 

```kotlin
import kotlinx.coroutines.flow.channelFlow
import kotlinx.coroutines.launch

val randomNumbers = channelFlow {
    repeat(10) {
        launch {
            send(getRandomNumber())
		} 
	}
}

553 [main] -1927966915
568 [main] 222582016
...
569 [main] 1827898086
```

이전과 동일한 방식으로 이 플로우을 수집하지만 이제 채널 플로우을 사용하면 `getRandomNumber`가 실제로 동시에 실행되고 전체 실행이 약 500밀리초 내에 완료 되는 것을 관찰할 수 있다

![](https://velog.velcdn.com/images/cksgodl/post/4d8417d3-da1c-4708-8d05-9d89fc84f100/image.png)

이쯤되면 채널 플로우가 일반 플로우가 할 수 있는 모든 것을 할 수 있는데 굳이 비채널 플로우 를 사용할 이유가 있는지 의문이 들 수도 있다. 그렇다면 어떻게 결정할까?

일반적으로 일반 콜드 플로우는 가장 쉽고 성능이 뛰어난 추상화이며, 엄격하게 순차적이고 새로운 코루틴을 시작할 수 없지만 만들기가 매우 간단하고  오버헤드가 없다. 

반면에 채널 플로우은 동시 작업의 사용 사례를 위해 특별히 설계되었다. 또 다른 동시 작업의 기본 요소인 채널을 내부에서 관리해야 하기 때문에 생성 비용이 저렴하지 않다. 채널은 코루틴 간 통신을 위해 많이 사용된다.

> 일반 콜드 플로우와 채널 플로우 중 하나를 결정할 때는 플로우 내부에서 새 코루틴을 시작해야 하는 경우에만 채널 플로우를 선택하라. 그렇지 않은 경우에는 일반 콜드 플로를 선택하는 것이 좋다.

## 16.3 핫 플로우

핫 플로우는 전체적인 방출 및 수집 구조를 따르지만, 콜드 플로우와는 다른 여러 가지 속성을 가지고 있다. 핫 플로우는 각 수집기가 독립적으로 플로우 로직의 실행을 트리거하는 대신 구독자라고 하는 여러 수집기 간에 방출된 항목을 공유한다.

### 16.3.1 Shared flows은 구독자에게 값을 브로드캐스트한다.

`Shared flow`은 방송 방식으로 작동하며, 가입자(수집자)의 존재 여부와 관계없이 방출이 발생할 수 있다. 

![](https://velog.velcdn.com/images/cksgodl/post/df44f96c-dc0f-4c9d-afdb-ab39ece0b06e/image.png)

값을 내보내는데 사용할 수 있는 공유 플로우의 변경가능한 버전인 ` _messageFlow`와 같은 백킹필드를 활용하여 비공개 속성으로 캡슐화할 수 있다. 내보내기를 위해 `_messageFlow`를 사용 할 수 있고, 플로우의 읽기 전용 버전인 `messageFlow`는 공개 속성으로 노출하여 방송할 수 있다.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlin.random.*
import kotlin.time.Duration.Companion.milliseconds

class RadioStation {

	private val _messageFlow = MutableSharedFlow<Int>()
    val messageFlow = _messageFlow.asSharedFlow()
    
    fun beginBroadcasting(scope: CoroutineScope) {
    	scope.launch {
			while(true) {
            delay(500.milliseconds)
            val number = Random.nextInt(0..10)
            log("Emitting $number!")
			_messageFlow.emit(number)
		} 
	}
}
```

플로우 빌더를 사용하는 대신 변경 가능한 버전의 플로우에 대한 참조를 사용한다. 하위 스크립터의 존재 여부와 관계없이 배출이 발생하므로 실제 배출을 수행하는 코루틴을 시작하는것은 사용자의 책임이다. 또한 변경 가능한 공유 플로우로 값을 내보내는 코루틴을 두 개 이상 가질 수 있다는 의미이기도 하다.

```kotlin
fun main() = runBlocking {
	// runBlocking의 코루틴 범위에서 코루틴을 시작.
    RadioStation().beginBroadcasting(this)
}

// 575 [main @coroutine#2] Emitting 2!
// 1088 [main @coroutine#2] Emitting 10!
// 1593 [main @coroutine#2] Emitting 4!
// ...
```

구독자는 구독시작한 후의 값만 받을 수 있다는 점을 유의해야 한다.

```kotlin
fun main(): Unit = runBlocking {
    val radioStation = RadioStation()
    radioStation.beginBroadcasting(this)
    delay(600.milliseconds)
    radioStation.messageFlow.collect {
        log("A collecting $it!")
    }
}

611 [main @coroutine#2] Emitting 8!
1129 [main @coroutine#2] Emitting 9!
1131 [main @coroutine#1] A collecting 9!
1647 [main @coroutine#2] Emitting 1!
1647 [main @coroutine#1] A collecting 1!
```

출력을 살펴보면 약 500밀리초 후에 전송된 첫 번째 값이 구독자에 의해 수집되지 않았음을 알 수 있다:

공유 플로우는 브로드캐스트 방식으로 작동하기 때문에 기존 메시지 플로우의 배출을 수신하는 또 다른 구독자를 추가할 수 있다. 

```kotlin
launch {
    radioStation.messageFlow.collect {
        log("B collecting $it!")
    }
}
```

동일한 플로우는 다른 모든 구독자와 동일한 값을 수신하게 된다. 콜드 플로우와 달리 수집기는 플로우에서 요소의 실제 방출을 트리거할 책임이 없으며, 단지 새로운 요소가 방출될 때 알림을 받는 구독자일 뿐이라는 점에 유의하라.

#### 구독자를 위한 replaying values

공유 플로우를 사용할 때 구독자는 수집을 호출하여 구독을 시작한 후에 발생하는 값만 받는다. 구독자가 이전에 전송된 요소를 수신하도록 하려면 `MutableSharedFlow`를 구성할때 `replay` 매개변수를 사용하여 새구독자에 대한 최신값의 캐시를 설정할 수 있다.

```kotlin
private val _messageFlow = MutableSharedFlow<Int>(replay = 5)
```

이 변경 사항으로 인해 600밀리초의 짧은 지연 후 수집기를 실행하더라도 구독자는 구 독 이전의 요소를 최대 5개까지 계속 받게 된다.

#### 콜드 플로우에서 ShareIn을 통한 공유 플로우로 변환

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlin.random.*
import kotlin.time.Duration.Companion.milliseconds

fun querySensor(): Int = Random.nextInt(-10..30)

fun getTemperatures(): Flow<Int> {
    return flow {
        while(true) {
            emit(querySensor())
            delay(500.milliseconds)
		} 
	}
}
```

```kotlin
fun celsiusToFahrenheit(celsius: Int) = celsius * 9.0 / 5.0 + 32.0

fun main() {
    val temps = getTemperatures()
    runBlocking {
        launch {
            temps.collect {
                log("섭씨 : $it")
            }
		}
    
		launch {
			temps.collect {
        		log("화씨 : ${celsiusToFahrenheit(it)} Fahrenheit")
			}	 
		}
	}
}
```

두 수집기 간에 반환되는 플로우을 공유해야 하며, 두 수집기 모두 동일한 요소를 수신해야 할 때가 있다.

`shareIn` 함수를 사용하여 주어진 콜드 플로우를 핫 공유 플로우로 변환할 수 있다. 콜드에서 핫으로 변환하면 플로우 내부의 코드가 실행되므로 이 함수는 코루틴에서 실행 되어야 한다. 이를 위해 `shareIn`은 해당 코루틴이 실행되는 `CoroutineScope` 유형의 범위매개 변수를 받는다.

```kotlin
fun main() {
    val temps = getTemperatures()
    runBlocking {
        val sharedTemps = temps.shareIn(this, SharingStarted.Lazily)
        launch {
            sharedTemps.collect {
                log("$it Celsius")
			} 
		}	
        launch {
            sharedTemps.collect {
                log("${celsiusToFahrenheit(it)} Fahrenheit")
            }
		} 
	}
}

// 45 [main @coroutine#3] -10 Celsius
// 52 [main @coroutine#4] 14.0 Fahrenheit
// 599 [main @coroutine#3] 11 Celsius
// 599 [main @coroutine#4] 51.8 Fahrenheit
```

두 번째 매개변수 started는 플로우가 실제로 시작되어야 하는 시점을 정의한다. 

- `Eagerly` : 즉시 플로우 수집을 시작
- `Lazily` : 첫 번째 구독자가 나타날 때 시작
- `WhileSubscribed` 동안 구독은 첫 번째 구독자가 나타날때만 수집을 시작한 다음, 마지막 구독자가 사라지면 플로우의 수집을 취소.

`shareIn`은 코루틴 범위를 통해 구조화된 동시성에 참여하므로 애플리케이션에서 더 이상 공유 플로우의 정보가 필요하지 않게 되면 주변 코루틴 범위가 취소되면 내부 로직이 취소되도록 할 수 있다.

### 16.3.2 시스템에서 상태 추적하기: State flow

동시 시스템에서 발생하는 특별한 경우는 시간에 따라 변할 수 있는 값, 즉 값의 상태를 추적하는 경우이다 

상태플로우은 공유플로우의 특수버전으로, 시간에 따른 변수의 상태 변화를 특히 쉽게 추적할 수 있게 해준다. 아래와 같은 상황일 때 상태 플로우가 필요할 수 있다.

- 병렬로 액세스하는 경우에도 상태 플로우의 값을 안전하게 업데이트
- 상태 플로우이 실제로 값이 변경될 때만 발생하도록 하는 평등 기반 컨플레이션

콜드 플로우를 상태 플로우을 만드는 것은 공유 플로우을 만드는 것과 유사하게 작동한다. _클래스의 개인 속성으로 `MutableStateFlow`를 만들고 동일한 변수의 읽기 전용 `StateFlow` 변형을 노출하는 방식_이다.

```kotlin
fun main() {
    val vc = ViewCounter()
    runBlocking(Dispatchers.Default) {
        repeat(10_000) {
            launch { vc.increment() }
		} 
	}
	println(vc.counter.value)
	// 4103
}
```

보시다시피 카운터의 결과 숫자는 10,000보다 훨씬 낮다. 이는 이러한 코루틴이 여러 스레드에서 실행되고 있기 때문이다. 증분은 현재 값을 읽고, 새 값을 계산한 다음, 새 값을 쓰는 여러 단계로 비원자적으로 이루어진다. 두 개의 스레드가 동시에 현재 값을 읽으면 증분 연산 중 하나가 중단된다.

 문제를 해결하기 위해 상태 플로우은 상태 플로우의 값을 원자적으로 업데이트할 수 있는 업데이트 함수를 제공한다. 상태 플로우에 대한 두 번의 업데이트가 동시에 발생하는 경우 업데이트 함수를 새로 고친 이전 값으로 다시 실행하여 작업이 손실되지 않도록 한다.

#### 상태 플로우는 값이 실제로 변경된 경우에만 방출된다:

```kotlin
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.*

enum class Direction { LEFT, RIGHT }

class DirectionSelector {

	private val _direction = MutableStateFlow(Direction.LEFT)
    val direction = _direction.asStateFlow()
    
    fun turn(d: Direction) {
        _direction.update { d }
	}
}
```

그이 방향 선택기를 사용하여 "왼쪽"과 "오른쪽" 위치 사이에서 전환을 수행할 수 있다. 수집을 호출하면 새 값이 설정될 때마다 이러한 트랜지션을 기록하는 코루틴에 알림이 전송된다:

```kotlin
fun main() = runBlocking {
    val switch = DirectionSelector()
    launch {
        switch.direction.collect {
            log("Direction now $it")
		} 
	}
    delay(200.milliseconds)
    switch.turn(Direction.RIGHT)
    delay(200.milliseconds)
    switch.turn(Direction.LEFT)
    delay(200.milliseconds)
    switch.turn(Direction.LEFT)
}

// 37 [main @coroutine#2] Direction now LEFT
// 240 [main @coroutine#2] Direction now RIGHT
// 445 [main @coroutine#2] Direction now LEFT
```

위 예를 살펴보면 `LEFT`를 매개변수로 사용하여 차례로 두 번 호출되었음 에도 불구하고 구독자는 한 번만 호출된 것을 알 수 있다. 이는 상태 플로우가 동일성 기반 병합을 수행하여 값이 실제로 변경되었을 때만 수집기에 값을 전송하기 때문이다. 이전 값과 업데이트된 값이 같으면 아무런 방출도 일어나지 않는다

![](https://velog.velcdn.com/images/cksgodl/post/bbfd0e66-526d-49a3-8a2e-95deadf77a53/image.png)

#### 콜드 플로우에서 상태 플로우로 : stateIn

콜드 플로우를 제공하는 API로 작업할 때 `stateIn` 함수를 사용 하여 콜드 플로우를 상태 플로우로 변환하면 원래 플로우에서 항상 최신 값을 읽을 수 있다. 공유 흐름과 마찬가지로, 여러 수집기 또는 값 속성에 대한 액세스를 추가해도 업스트림 흐름은 실행되지 않는다.

```kotlin
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.*
import kotlin.time.Duration.Companion.milliseconds

fun main() {
    val temps = getTemperatures()
    runBlocking {
        val tempState = temps.stateIn(this)
        println(tempState.value)
        // 18
        delay(800.milliseconds)
        println(tempState.value)
		// -1 
	}
}
```

 공유 플로우와는 달리 `stateIn` 함수는 시작 전략을 제공하지 않는다. 항상 지정된 코루틴 범위에서 흐름을 시작하고 코루틴 범위가 취소될 때까지 값 속성을 통해 구독자에게 최신 값을 계속 제공한다.
 
### 16.3.3 상태플로우와 공유플로우 비교

- 공유 플로우는 구독자가 왔다 갔다 할 수 있는 이벤트를 브로드캐스트할 수 있으며, 구독자는 구독 중인 동안에만 방출을 수신한. 

- 상태 플로우는 모든 종류의 상태를 나타내도록 설계되었으며 동등성 기반 충돌을 사용하므로 상태 흐름이 나타내 는 값이 실제로 변경될 때만 배출이 발생한다.

일반적으로 상태 플로우는 공유 플로우보다 더 간단한 API를 제공하며, 단일 값만 나타낸다. 공유 플로우는 구독자가 전송을 받을 것으로 예상되는 시간에 구독자가 존재하는지 확인하는 것이 사용자의 책임이기 때문에 복잡성이 더 커질 수 있다. 따라서 시간 을 투자하여 공유 플로우를 사용하여 해결하려는 문제를 재구성하여 상태 플로우를 대신 사용할 수 있는지 알아보는 것이 좋다.

```kotlin
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.*
import kotlin.time.Duration.Companion.milliseconds

class Broadcaster {

	private val _messages = MutableSharedFlow<String>()
    val messages = _messages.asSharedFlow()
    
    fun beginBroadcasting(scope: CoroutineScope) {
        scope.launch {
            _messages.emit("Hello!")
            _messages.emit("Hi!")
            _messages.emit("Hola!")
		} 
	}
}

fun main(): Unit = runBlocking {
    val broadcaster = Broadcaster()
    broadcaster.beginBroadcasting(this)
    delay(200.milliseconds)
    broadcaster.messages.collect {
        println("Message: $it")
    }
}
// No values are collected, nothing is printed
```

구독자는 메시지가 브로드캐스트된 후에만 나타나기 때문에 메시지를 수신하지 않는다. 물론 공유 흐름의 재생 캐시를 조정할 수 있다는 것을 이미 보셨을 것이다. 하지만 그 대신 상태 흐름이라는 더 간단한 추상 개념을 사용할 수도 있다. 

```kotlin
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.*
import kotlin.time.Duration.Companion.milliseconds

class Broadcaster {
    
    private val _messages = MutableStateFlow<List<String>>(emptyList())
    val messages = _messages.asStateFlow()
    fun beginBroadcasting(scope: CoroutineScope) {
        scope.launch {
            _messages.update { it + "Hello!" }
            _messages.update { it + "Hi!" }
            _messages.update { it + "Hola!" }
		} 
	}
}

fun main() = runBlocking {
    val broadcaster = Broadcaster()
    broadcaster.beginBroadcasting(this)
    delay(200.milliseconds)
    println(broadcaster.messages.value)
}
// [Hello!, Hi!, Hola!]
```

### 16.3.4 16.3.4 핫, 콜드, 공유, 상태: 언제 어떤 플로우를 사용할지

![](https://velog.velcdn.com/images/cksgodl/post/5e1384e3-e8d4-4ef5-89e0-5280325cbafb/image.png)

일반적으로 서비스를 제공하는 함수(예: 네트워크 요청 또는 데이터베이스에서 읽기)는 콜드 플로를 사용하여 선언된다. 이러한 흐름을 사용하는 다른 클래스와 함수는 직접 수집하거나 해당되는 경우 상태 흐름 및 공유 흐름으로 변환하여 이 정보를 시스 템의 다른 부분에 노출할 수 있다.

> 다양한 리액티브 스트림 구현과의 상호 운용성
>
> 반응형 스트림에 이미 다른 추상화를 사용하는 프로젝트에서 작업하는 경우, (예: Project Reactor(https://projectreactor.io/))의 경우 기본 제공 변환 함수를 사용하여 해당 표현을 `Kotlin` 흐름으로 또는 그 반대로 변환할 수 있다. 이를 통해 기존 코드와 흐름을 원활하게 통합할 수 있다.

## 요약

- `Kotlin`에서 흐름은 코루틴 기반 추상화로, 시간이 지남에 따라 나타나는 값으로 작업할 수 있게 해준다.
- 핫 플로우와 콜드 플로우라는 두 가지 유형의 플로우를 구분한다.
- 콜드 플로우는 기본적으로 비활성 상태이며 단일 수집기와 연결된다. 콜드 플로우는 플로우 빌더 함수를 사용하여 구성된다. `emit` 함수를 사용하면 값을 비동기적으로 제공할 수 있다.
- 특별한 유형의 콜드 플로우인 채널플로우를 사용하면 `send`기능을 통해여러코루틴에서 값을 방출할 수 있다.
- 핫 플로우는 항상 활성화되어 있으며 구독자라고 하는 여러 수집기와 연결되어 있다. 공유 흐름과 상태 흐름은 핫플로우의 인스턴스이다.
- 공유 플로우는 코루틴 전반에 걸쳐 값을 브로드캐스트스타일로 전달하는데 사용할 수 있다.
- 공유 플로우의 구독자는 구독 시작 시점의 배출량과 공유 흐름에 의해 재생된 값을 받는다.
- 상태 플로우를 사용하여 동시 시스템의 상태를 관리할 수 있다.
- 상태 플로우는 동일한값을 여러번 할당 하는것이 아니라 실제로 값이 변경될때만 동일성 기반 인플레이션을 수행한다.
- 콜드 플로우는 `shareIn` 및 `stateIn` 함수를 통해 핫 플로우로 전환할 수 있다.
