## ReactiveX와 Rxjava에 관하여

지난번에는 [ReactvieX와 Rxjava](https://velog.io/@cksgodl/Kotlin-ReactiveX-%EC%99%80-RxKotlin)에 대하여 간단하게 알아보았다.

간단하게 요악하자면

> `Rxjava`에서는 쓰레드와 스케줄러를 활용하여 반응형 프로그래밍을 제공한다.
> `Observable`과 `Operator`를 활용해 데이터스트림을 조작하고 구독하며 비동기 작업을 수행한다.

안드로이드 개발에서도 `RxJava`는 지속해서 쓰이고 있지만 `2.x` 버전은 유지보수 모드로 버그 픽스만 적용될 뿐 새로운 기능 업데이트는 없고 현재 `3.x`버전이 업데이트 되고 있다. [[RxJava - Github]](https://github.com/ReactiveX/RxJava/wiki/What's-different-in-3.0)

---

## Flow에 관하여

`Kotlin`에서는 `Flow`는 비동기 데이터 스트림 처리 라이브러리이다. 코루틴을 기반으로 작동하며 반응형 프로그래밍을 구현할 수 있다.

```
// Dependency
implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.6.4")
```

기본적으로 반응형 프로그래밍은 `Producer(생산자)`, `Intermediary(중간 연산자)`, `Consumer(소비자)`로 이루어진다.

다음은 간단한 숫자를 생산하고 소비하는 예제이다.

```kotlin
// Producer
val emitter = flow<Int> {
    (0..100).forEach {
        println("emit $it")
        emit(it)
    }
}


fun main() = runBlocking {
    emitter
        // Intermediary
        .filter {
            it % 2 == 0
        }
        // Consumer
        .collect {
            println("collect: $it")
        }
}
```

![](https://velog.velcdn.com/images/cksgodl/post/ad22d014-c90f-4e50-9ae1-1f64c12d1db9/image.png)

이런 `Flow`는 기본적으로 `Cold Stream`이며 상태를 가지지 않으며, 새로운 데이터가 들어올 때 마다 새로운 스트림이 형성된다.

> 예시로는 `TV`와 `OTT` 생각해보자. `TV`는 켰을 때 현재 방송중인 프로그램(방출중인 데이터)를 수신해야 하지만, `OTT`는 기존의 보았던 시간때부터 다시 프로그램을 볼 수 있다.(이전 상태를 기록하고 있음)

`Cold Stream`을 활용하면 사용자가 핸드폰 화면을 돌릴 때 마다 데이터가 초기화 될 것이고, 서버 또는 `DB`로부터 데이터를 다시 가져와야 한다.

이를 방지하기 위해 `StateFlow`를 제공한다. 이는 `Hot Stream`이며 상태를 가지는 동시에 데이터 스트림의 역할까지 수행한다. `StateFlow`를 `ViewModel`단에 저장하고 화면이 돌아가도 데이터 홀더의 역할을 수행하기에 데이터를 다시 불러올 필요가 없다.

[Android Developer - 상태 생성 및 관리](https://developer.android.com/topic/architecture/ui-layer/state-production?hl=ko#stateflow)

```kotlin
data class DiceUiState(
    val firstDieValue: Int? = null,
    val secondDieValue: Int? = null,
    val numberOfRolls: Int = 0,
)

class DiceRollViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(DiceUiState())
    val uiState: StateFlow<DiceUiState> get() = _uiState.asStateFlow()

    // Called from the UI
    fun rollDice() {
        _uiState.update { currentState ->
            currentState.copy(
            firstDieValue = Random.nextInt(from = 1, until = 7),
            secondDieValue = Random.nextInt(from = 1, until = 7),
            numberOfRolls = currentState.numberOfRolls + 1,
            )
        }
    }
}
```

`Fragment`, `Activity`등의 생명주기에 맞추어 `uiState`를 `Observing`하며 뷰의 업데이트 수행한다.

```
lifecycleScope.launch {
	repeatOnLifecycle(Lifecycle.State.STARTED) {
    	viewModel.uiState.collect { uiState ->

        }
	}
}
```

옵저빙을 수행하며 뷰를 업데이트할 때 `Livedata`를 활용하는 것과 어떤 차이가 있을까?는 [LiveData 및 StateFlow에 대하여](https://velog.io/@cksgodl/AndroidKotlin-LiveData%EB%A7%90%EA%B3%A0-StateFlow%EB%A5%BC-%EC%93%B0%EB%9D%BC%EA%B3%A0%EC%9A%94)를 참고해보자!

---

> 참고) `Compose`에서는 `Flow`말고 `State`를 활용하여 상태를 저장하고, 이를 옵저빙할 필요가 없다!

`Compose`에서의 UI 상태 관리 소스

```kotlin
@Stable
interface DiceUiState {
    val firstDieValue: Int?
    val secondDieValue: Int?
    val numberOfRolls: Int?
}

private class MutableDiceUiState: DiceUiState {
    override var firstDieValue: Int? by mutableStateOf(null)
    override var secondDieValue: Int? by mutableStateOf(null)
    override var numberOfRolls: Int by mutableStateOf(0)
}

class DiceRollViewModel : ViewModel() {

    private val _uiState = MutableDiceUiState()
    val uiState: DiceUiState = _uiState

    fun rollDice() {
        _uiState.firstDieValue = Random.nextInt(from = 1, until = 7)
        _uiState.secondDieValue = Random.nextInt(from = 1, until = 7)
        _uiState.numberOfRolls = _uiState.numberOfRolls + 1
    }
}
```

---

## Flow를 응용해보자.

`Flow`는 데이터 파이프라인을 생성하며 이 데이터는 `collect`에 의해 소비된다.

> 다음 설명내용은 해당 블로그의 내용들을 [[collect와 collectLatest의 차이점]](https://kotlinworld.com/252?category=973477)를 많이 참고하였다.

### 데이터의 지연

위에서 예제로 보았던 `emitter`를 그대로 들고오자.

```kotlin
val emitter = flow<Int> {
    (0..20).forEach {
    	delay(100)
        println("emit $it")
        emit(it)
    }
}
```

그리고 데이터를 소비하는데 엄청난 시간이 걸리는 소스를 작성해보자.

```kotlin
fun main() = runBlocking {
    emitter
        .collect {
        	// 엄청난 처리중...
            delay(Long.MAX_VALUE)
            println("collect: $it")
        }
}
```

특정 데이터를 처리하기위해 많은 시간이 소요된다고 하면 그다음 데이터를 처리하는데 엄청난 지연이 발생할 것이다.
![](https://velog.velcdn.com/images/cksgodl/post/c9a43c34-6c3e-483f-946f-1601cdd7c5b1/image.png)
_소비가 안돼..._

![](https://velog.velcdn.com/images/cksgodl/post/53d7a7d5-d497-4abf-9232-f1cdf6364cea/image.png)

이 이유는 `Flow`의 `collect`함수는 이전 데이터의 소비가 끝나야지 다음 데이터를를 소비하기 때문이다.

이를 방지하기위해 `collectLatest`를 활용할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/1a98ec46-1d20-4d50-9cc0-28789b4a4409/image.png)

이는 새로운 데이터 스트림이 들어오면 기존의 처리를 강제 종료시키고 새로운 데이터를 처리한다.

```kotlin
fun main() = runBlocking {
    emitter
        .collectLatest {
            delay(200)
            println("collect: $it")
        }
}
```

0.2초를 기다리고 데이터를 소비하는데 0.2초가 지나기전에 새로운 데이터 스트림이 들어와 마지막 `20`만이 소비되는 것을 볼 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/6c76ab06-42b5-4b7c-82ca-aa9c5b6507d0/image.png)

> 이것이 `collectLatest`의 한계점이기도 하다. 해당 데이터를 처리하는 속도가 `emit`하는 속도보다 느리다면 마지막 데이터스트림까지 뷰에 아무런 업데이트도 수행되지 않을 것이다.

이를 방지하기 위해서는 `conflate()`를 활용할 수 있다. 이는 한번 시작 된 데이터 스트림의 소비는 끝날 때 까지 수행하고, 끝난 시점에서의 가장 최신 데이터를 소비하는 것이다.

![](https://velog.velcdn.com/images/cksgodl/post/ceaae741-4f59-4e98-a004-89d081a19cf5/image.png)

데이터를 발행하는데 0.1초가 걸리고 소비가 0.2초 걸릴 때 결과는 다음과 같다.

```kotlin
fun main() = runBlocking {
    emitter
        .conflate()
        .collect() {
            delay(200)
            println("collect: $it")
        }
}
```

![](https://velog.velcdn.com/images/cksgodl/post/e5091795-b1bf-4f1e-a154-8c283012e94e/image.png)

`0`이 소비됬을 때 최신 상태인 `1`을 소비하고 `1`이 소비되었을 때 최신 상태인 `3`을 소비한다.

### `collect`의 발행과 소비의 방식

> `flow`의 `collect`를 활용하면 하나의 `Coroutine`에서 발행과 소비가 같이 일어나기 때문에 데이터를 다 소비한 후 다음 데이터가 발행된다.
> ![](https://velog.velcdn.com/images/cksgodl/post/182c0458-1739-4d64-9e67-790ead572381/image.png)

발행과 소비에 모두 시간이 오래걸린다면 이것은 매우 비효율적인 코드가 될 것이다.

```kotlin
val emitter = flow<Int> {
    (0..10).forEach {
        delay(1000)
        println("emit $it")
        emit(it)
    }
}


fun main() = runBlocking {
    emitter
        .collect {
            delay(2000)
            println("collect: $it")
        }
}

--------

emit 0	// 1초
collect: 0 // 3초
emit 1 // 4초
collect: 1 // 6초
```

> 이를 방지하기 위해 `buffer`를 활용하여 발행과 소비를 위한 코루틴을 분리할 수 있다.
> ![](https://velog.velcdn.com/images/cksgodl/post/a70d614e-39ba-4687-b9ff-894ea7bc336a/image.png)

#### buffer()란??

> 지정된 용량의 채널을 통해 흐름 방출을 버퍼링하고 별도의 코루틴에서 컬렉터를 실행합니다.

간단하게 말하자면 발행을 위한 코루틴 채널을 따로 분리한다고 생각하면 된다.

기본적으로 `flow`의 발행과 소비는 순서적이며 `Q`자료구조를 가지고 실행된다.
![](https://velog.velcdn.com/images/cksgodl/post/a146b370-cdd1-4e8d-b184-78e04872deec/image.png)

하지만 `Buffer()`를 활용하면 데이터를 새로운 코루틴에서 발행한다.

![](https://velog.velcdn.com/images/cksgodl/post/25c812a4-1d3c-44a3-b4c3-29dc92277c78/image.png)

이를 활용하여 다음 예제를 확인해보자.

```kotlin
// 0.1초마다 데이터스트림 방출
fun main() = runBlocking {
    emitter
        .buffer()
        .collect {
            delay(200)
            println("collect: $it")
        }
}
```

![](https://velog.velcdn.com/images/cksgodl/post/4f9fb381-c02f-4f72-9215-32d4a4e0bc33/image.png)

데이터스트림의 방출과 소비가 각각 다른 코루틴에서 진행되는 것을 볼 수 있다.

---

여기서 `Backpressure`이라는 문제를 알고 넘어가면 좋을 것 같다.

### `Backpressure`란?

[[Backpressure in yout Kotlin Flows]](https://medium.com/google-developer-experts/backpressure-in-your-kotlin-flows-3eec980869c7)

한국어로 번역하면 배압이라고 하며 간단하게 설명하면 데이터스트림의 병목현상이라고 할 수 있겠다.

데이터를 방출하는 속도보다 소비하는 속도가 느릴 때 발생한다.

> `RxJava`에서는 `Observable`이 계속 쌓이면서 배압을 제어하지 못해 `MissingBackpressureException`이 발생할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/ed17ccd9-c990-4e37-a75c-ecc02470cb08/image.png)

하지만 `Kotlin Flow`에서는 위에 예시들을 활용하여 이를 관리할 수 있다.

- `collect`함수는 기본적으로 순서적으로(`Q`)처럼 작동하여 배압현상이 일어나지 않는다.
- `collectLatest`활용해 가장 최신의 데이터 스트림만 활용할 수 있다.
- `conflate()`함수를 활용해 가장 최신의 데이터 스트림만 활용할 수 있다.
  > 하지만 `buffer()`를 활용하면 새로운 코루틴에 해당 값이 쌓이면서 이 backpressure현상이 발생할 수 있다. 따라서 capacity를 조절하거나, dropLatest()연산자를 활용하여 사이즈를 조절해야 한다.

---

## 플로우끼리 합치기

### flatMapConcat

> `flatMapConcat`은 `Flow`에서 각각의 데이터를 처리하기 위해 다른 Flow를 호출하고, 그 결과들을 순차적으로 결합하여 새로운 Flow를 만드는 연산자이다.

```kotlin
val nums = flowOf(1, 2, 3)

nums.flatMapConcat { num ->
    flow {
        emit(num * 1)
        delay(1000)
        emit(num * 2)
        emit(num * 3)
    }
}.collect { println(it) } // 1, 2, 3, 2, 4, 6, 3, 6, 9가 출력됩니다.
```

`flatMapConcat`의 Flow의 처리는 순차적이며 이전 플로우가 발행되어야 다음 `Flow`가 실행된다.

`flatMapLatest`함수도 제공하며 이는 가장 최신의 `flow`만 소비한다.

### flatMapMerge

`flatMapMerge`는 각각의 다른 `Flow`들을 결합하여 새로운 `Flow`를 만드는 연산자이다.

`flatMapConcat`과의 차이점은 병렬적으로 실행되어 이전 처리가 완료되지 않아도 수행된다는 것이다. 따라서 순서를 보장하지 않는다.

```kotlin
val nums = flowOf(1, 2, 3)

nums.flatMapMerge { num ->
    flow {
        emit(num * 1)
        delay(1000)
        emit(num * 2)
        emit(num * 3)
    }
}
.collect { println(it) }
// 1, 2, 3, 2, 3, 4, 6, 6, 9가 출력됩니다.
```

`1`, `2`, `3`이 먼저 출력된 후에 `delay(1000)`를 거치고 난 후 그다음 값들이 `emit`됨

### combine

> `combine`은 여러 개의 `Flow`를 동시에 처리하고, 각 `Flow에`서 발행한 데이터를 조합하여 새로운 데이터를 만드는 연산자이다.

이 때, 모든 Flow가 새로운 데이터를 발행할 때마다 새로운 데이터를 만들어 낸다. **이는 병렬적으로 실행된다.**

```kotlin
val nums1 = flowOf(1, 2, 3)
val nums2 = flowOf(10, 20, 30)

nums1.combine(nums2) { a, b ->
    a + b
}
.collect { println(it) } // 11, 22, 33이 출력됩니다.
```

예를 들어 `nums1`과 `nums2` `Flow`를 `combine`하여 새로운 `Flow`를 만든다. 이 때, 각 `Flow`에서 발행한 데이터를 더하여 새로운 `Flow`를 만든다. 이 연산자는 각 `Flow`가 새로운 데이터를 발행할 때마다 실행된다.

다음 예는 `Android Compose`에서의 `combine`의 예제이다.

```kotlin
    val uiState = combine(
        _homeBanners, _nickName
    ) { homeBannerItems, nickName ->
        HomeUiState(
            homeBanners = homeBanners,
            nickName = nickName
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = HomeUiState()
    )
```

예제에서는 `_homeBanners`와 `_nickName`이라는 `Flow`를 수집하고 이를 합쳐서 `uiState`라는 새로운 `Flow`를 구성한다.
