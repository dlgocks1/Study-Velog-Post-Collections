## 17.1 플로우 연산자로 플로우 조작하기

플로우는 중간 플로우 연산자와 터미널 플로우 연산자를 구분할 수 있다. 중간 플로우 연산자는 실제로 코드를 실행하지 않고 수정된 다른 플로우을 반환한다. 터미널 연산자는 플로우를 수집하고 실제 코드를 실행한 후 `컬렉션`, `플로우의 개별 엘리먼트`, `계산된 값` 또는 전혀 값과 같은 결과를 반환한다.

![](https://velog.velcdn.com/images/cksgodl/post/cfefd573-f34e-4c03-a09a-5d82f8ca3c33/image.png)

## 17.2 중간 연산자는 업스트림 플로우에 적용되어 다운스트림 플로우을 반환한다.

중간 연산자는 플로우에 적용되어 플로우 자체를 반환한다. 시퀀스와 마찬가지로 플로우에서 중간 연산자를 호출해도 코드가 실행되지 않으며 반환되는 플로우는 콜드 플로우이다.

![](https://velog.velcdn.com/images/cksgodl/post/05f7a382-5c27-4bd6-b72d-a91555c82709/image.png)

개념에 따라 `Upstream` 플로우가 중간 연산자를 거쳐 `Downstream` 플로우로 방출된다. 이러한 중간 연산자는 맵, 필터와 같은 콜렉션 `API`와 유사하며 동일하게 작동한다. 아래에선 이 연산자들에 대해 집중적으로 알아본다.

### 17.2.1 각 업스트림 요소에 대해 임의의 값을 방출한다: transfrom

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun main() {
    val names = flow {
        emit("Jo")
        emit("May")
        emit("Sue")
    }
    val uppercasedNames = names.map {
        it.uppercase()
    }
    runBlocking {
        uppercasedNames.collect { print("$it ")}
	}
	// JO MAY SUE
}
```

위의 예제에서 두 개 이상의 요소를 동시에 내보내고 싶은 상황에 처할 수도 있다. 예를 들어 각 이름의 대문자 변형만 출력하는 것이 아니라 각 이름의 소문자 변형도 출력 스트림에 포함시키고 싶을 수 있다.

`Kotlin` 플로우에서는 `transfrom` 함수를 통해 이 작업을 수행할 수 있다. 이 함수를 사용하면 업스트림 플로우의 각 요소에 대해 임의로 많은 요소를 다운스트림 플로우로 내보낼 수 있다.

```kotlin
import kotlinx.coroutines.flow.*
fun main() {
    val names = flow {
        emit("Jo")
        emit("May")
	}
    // val names = flowOf("Jo", "May", "Sue").
    val upperAndLowercasedNames = names.transform {
    	emit(it.uppercase())
        emit(it.lowercase())
	}
    runBlocking {
    	upperAndLowercasedNames.collect { print("$it ")}
	}
    // JO jo MAY may SUE sue
}
```

### 17.2.2 take 연산자는 플로우를 취소(terminate)한다.

`take` 연산자는 지정한 조건이 더 이상 유효하지 않으면 업스트림 플로우가 취소되어 더 이상 요소가 배출 되지 않는다는 것이다.

```kotlin
val temps = getTemperatures()
temps
	.take(5)
	.collect {
		log(it)
	}

// 37 [main @coroutine#1] 7
// 568 [main @coroutine#1] 9
// 1123 [main @coroutine#1] 2
// 1640 [main @coroutine#1] -6
// 2148 [main @coroutine#1] 7
```

`take` 함수는 제어된 방식으로 플로우의 수집을 취소하는 또 다른 방법이다.

### 17.2.3 onStart, onEach, onCompletion 및 onEmpty를 사용하여 플로우 단계 연결하기

요소를 수집한 후 실제로 완료되는지 확인하려면, 플로우가 정기적으로 종료되거나, 취소되거나, 종료된 후 실행되는 람다를 제공할 수 있는 `onCompletion` 연산자를 사용하면 된다.

```kotlin
flow
    .onEmpty {
	    println("Nothing - emitting default value!")
		emit(0)
	}
	.onStart {
    	println("Starting!")
	}
	.onEach {
    	println("On $it!")
	}
	.onCompletion {
    	println("Done!")
	}.collect()
```

```kotlin
 fun main() {
 	runBlocking {
    	process(flowOf(1, 2, 3))
        // Starting!
        // On 1!
        // On 2!
        // On 3!
        // Done!
        process(flowOf())
        // Starting!
        // Nothing – emitting default value!
        // On 0!
        // Done!
	}
}
```

이는 이러한 중간 연산자가 요소를 다운스트림 플로우로 방출한다는 것을 다시 한 번 설명하는 좋은 예시이다. (onEmpty가 onEach보다 먼저 검출된다. - onEach는 onEmpty의 다운스트림을 활용한다.)

### 17.2.4 다운스트림 오퍼레이터 및 수집기를 위한 버퍼: buffer

실제 애플리케이션 코드는 플로우 내부에서 많은 작업을 수행하는 경우가 많다. 플로우의 요소를 수집하거나 `onEach`와 같은 연산자를 사용하여 처리할 때 완료하는데 시간이 걸리는 일시 중단 함수를 자체적으로 호출하는 경우가 종종 있다.

```kotlin
fun getAllUserIds(): Flow<Int> {
	return flow {
    	repeat(3) {
        	delay(200.milliseconds) // Database latency
	        log("Emitting!")
    	    emit(it)
		}
	}
}

suspend fun getProfileFromNetwork(id: Int): String {
	delay(2.seconds) // Network latency
    return "Profile[$id]"
}
```

기본적으로 앞서 표시된 것과 같은 콜드 플로우로 작업할 때 값 생산자는 수집기가 처 리를 마칠 때까지 작업을 일시 중단한다.

```kotlin
fun main() {
    val ids = getAllUserIds()
    runBlocking {
        ids
            .map { getProfileFromNetwork(it) }
            .collect { log("Got $it") }
	}
}

// 310 [main @coroutine#1] Emitting!
// 2402 [main @coroutine#1] Got Profile[0]
// 2661 [main @coroutine#1] Emitting!
// 4732 [main @coroutine#1] Got Profile[1]
// 5007 [main @coroutine#1] Emitting!
// 7048 [main @coroutine#1] Got Profile[2]
```

요소가 방출되면 다운 스트림 플로우가 요소 처리를 마칠 때까지 프로듀서 코드가 계속 진행되지 않는다.

![](https://velog.velcdn.com/images/cksgodl/post/0a784f40-4994-4932-8142-ae7961107b6c/image.png)

버퍼 연산자는 다운스트림 플로우가전에 생성된 요소를 처리하는 동안에도 요소를 생성할 수 있는 버퍼를 도입한다. 이를 통해 플로우를 처리하는 오퍼레이터 체인의 일부를 효과적으로 분리할 수 있다.

3개의 요소 용량을 가진 버퍼를 추가하면, 이미터는 수집기가 추가 네트워크 요청을 할 준비가 될 때까지 계속해서 새로운 사용자 식별자를 생성하여 버퍼에 배치할 수 있다:

```kotlin
fun main() {
    val ids = getAllUserIds()
    runBlocking {
        ids
            .buffer(3)
            .map { getProfileFromNetwork(it) }
            .collect { log("Got $it") }
	}
}

// 304 [main @coroutine#2] Emitting!
// 525 [main @coroutine#2] Emitting!
// 796 [main @coroutine#2] Emitting!
// 2373 [main @coroutine#1] Got Profile[0]
// 4388 [main @coroutine#1] Got Profile[1]
// 6461 [main @coroutine#1] Got Profile[2]
```

특히 플로우에 따라 요소를 방출하고 처리하는 데 필요한 시간이 변동하는 경우, 연산자체인에 버퍼를 도입하면 시스템 처리량을 늘리는 데 도움이 될 수 있다. 

버퍼 연산자는 커스텀할 수도 있다. 크기 매개변수, 버퍼 용량이 모두 소진되었을 때 어떤 일이 일어날지, 즉 생산자가 일시 중단할지(SUSPEND), 일시 중단하지 않고 버퍼 의 가장 오래된 값을 삭제할지(DROP_OLDEST), 추가 중인 최신 값을 삭제할지(DROP_LATEST) 지정할 수 있는 매개변수도제공한다.

![](https://velog.velcdn.com/images/cksgodl/post/2d5680ae-4efa-4560-b3a7-8d0d2bea5f87/image.png)

### 17.2.5 중간 값 버리기: conflate 연산자

값 생산자가 방해받지 않고 작업할 수 있도록 하는 또 다른 방법은 수집기가 바쁜 동안 배출된 모든 항목을 버리는 것이다. `Kotlin` 플로우에서는 `conflate` 연산자를 통해 이 작업을 수행할 수 있다.

```kotlin
runBlocking {
	val temps = getTemperatures()
    temps
    	.onEach {
        	log("Read $it from sensor")
		}.conflate()
		}.collect {
    		log("Collected $it")
    		delay(1.seconds)
		}
        
        
// 43 [main @coroutine#2] Read 20 from sensor
// 51 [main @coroutine#1] Collected 20
// 558 [main @coroutine#2] Read -10 from sensor
// 1078 [main @coroutine#2] Read 3 from sensor
// 1294 [main @coroutine#1] Collected 3
// 1579 [main @coroutine#2] Read 13 from sensor
// 2153 [main @coroutine#2] Read 26 from sensor
// 2556 [main @coroutine#1] Collected 26
```

버퍼와 마찬가지로, 병합을 사용하면 업스트림 플로우의 실행과 다운스트림 연산자의 실행이 분리된다. 값이 빠르게 '오래된' 플로우로 작업하여 다른 배출 요소로 대체되는 경우, `conflate`를 사용하면 플로우의 최신 요소만 처리하여 느린 수집기가 따라잡는데 도움이 될 수 있다.

### 17.2.6 시간 초과 시 값을 필터링: debounce 

플로우의 처리에 대한 디바운싱을 제공한다.

```kotlin
val searchQuery = flow {
	emit("K")
    delay(100.milliseconds)
    emit("Ko")
    delay(200.milliseconds)
    emit("Kotl")
    delay(500.milliseconds)
    emit("Kotlin")
}
```

```kotlin
fun main() = runBlocking {
    searchQuery
        .debounce(250.milliseconds)
        .collect {
            log("Searching for $it")
        }
}

// 644 [main @coroutine#1] Searching for Kotl
// 876 [main @coroutine#1] Searching for Kotlin
```

### 17.2.7 흐름이 실행되는 코루틴 컨텍스트 전환: flowOn 

흐름 연산자가 블로킹 IO를 사용하거나 UI 스레드로 작업해야 하는 경우 일반 코루틴과 동일한 고려 사항이 적용된다. 코루틴 컨텍스트에 따라 흐름의 로직이 실행 되는 위치가 결정된다. (플로우는 중단 함수에서 실행됨으로 해당 콘텍스트를 상속받아 사용됨)

플로우를 사용하여 상당히 복잡한 데이터 처리 파이프라인을 구축할 수 있다. 처리 파이프라인의 일부가 다른 디스패처에서 실행되거나 다른 상관관계 컨텍스트에서 실행되기를 원할 수도 있다. `flowOn` 연산자를 사용하면 `withContext` 함수와 마찬가지로 코루틴 컨텍스트를 조정할 수 있다. 

```kotlin
runBlocking {
	flowOf(1)
    	.onEach { log("A") }
        .flowOn(Dispatchers.Default)
        .onEach { log("B") }
        .flowOn(Dispatchers.IO)
        .onEach { log("C") }
        .collect()
	} 
}

// 36 [DefaultDispatcher-worker-3 @coroutine#3] A
// 44 [DefaultDispatcher-worker-1 @coroutine#2] B
// 44 [main @coroutine#1] C
```

`flowOn` 오퍼레이터는 업스트림플로우의 디스패처, 즉 앞에오는 플로우(및 모든중간 오퍼레이터)에만 영향을 미친다는 점에 유의해야 한다. 위의 예시에서 디스패처를 `Dispatchers.Default`로 전환하면 "A"에만 영향을 미치고, `Dispatchers.IO`로 전환하면 "B"에만 영향을 미치며, "C"는 앞의 `flowOn` 호출에 전혀 영향을 받지 않는다.

## 17.3 사용자 지정 중간 연산자 만들기

```kotlin
 fun Flow<Double>.averageOfLast(n: Int): Flow<Double> =
 	flow {
    	val numbers = mutableListOf<Double>()
        collect {
        	if (numbers.size >= n) {
            	numbers.removeFirst()
			}
			numbers.add(it)
        	emit(numbers.average())
		}
}	
```

```kotlin
fun main() = runBlocking {
	flowOf(1.0, 2.0, 30.0, 121.0)
		.averageOfLast(3)
		.collect {
    		print("$it ")
		}
}

// 1.0 1.5 11.0 51.0
```


일반적으로 중간 오퍼레이터는 업스트림 플로우에서 요소를 수집하고, 변환, 부작 용 또는 기타 사용자 지정 동작을 수행한 다음 새 요소를 다운스트림 플로우으로 방출 하는 수집기와 방출기 역할을 동시에 수행한다.

위의 예시처럼 플로우를 `collect`함과 동시에 이를 방출하게 된다면 사용자 지점 중간 연산자를 만드는 것도 가능할 것이다. 즉, 업스트림 플로우에서 요소를 수집하는 것을 통해 새로운 다운스트림 플로우를 방출할 수 있다.

## 요약

- 중간 연산자는 플로우를 다른 플로우로 변환하는 데 사용되며, 업스트림 플로우에서 작동하고 다운스트림 플로우를 반환한다. 중간 연산자는 콜드 연산자이며, 터미널 연산자가 호출될 때까지 실행되지 않는다.
- 시퀀스에 사용할 수 있는 중간 연산자의 대부분은 플로우에 직접 사용할 수 있다. 
또한 흐름은 변환을 수행하고(`transform`), 흐름이 실행되는 컨텍스트를 관리 하고(`flowOn`), 흐름 실행 중 특정 단계에서 코드를 실행할 수 있는 추가 중간 연산자를 제공한다 (`onStart`, `onCompletion` 등)
- 수집과 같은 터미널 운영자는 플로우의 코드를 실행하거나 핫플로우의 경우 플로우에 대한 구독을 처리한다.
- 다른 플로우 빌더 내에서 플로우를 수집하여 변환된 요소를 방출하여 자신만의 커스텀 연산자를 구축할 수 있다.



