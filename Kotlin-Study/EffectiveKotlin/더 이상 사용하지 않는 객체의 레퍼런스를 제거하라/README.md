메모리 관리를 자동으로 해 주는 프로그래밍 언어에 익숙한 개발자는 객체관리를 따로 생각하지 않는다.
코틀린은 JVM환경에서 돌아가며, 자바의 가비지컬렉터를 사용한다. 자바는 가비지 컬렉터가 객체해제와 관련된 모든 작업을 수행해주지만, 그렇다고 메모리 관리를 완전히 무시해 버리면, 메모리 누수가 발생하여 ,`OutOfMemoryError`가 발생하기도 한다. 따라서

> 더 이상 사용하지 않는 객체의 레퍼런스를 유지하면 안 된다.

라는 규칙 정도는 지켜주는 것이 좋다.

다음은 안드로이드에서의 메모리 누수의 한 예이다.

```
class MainActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
    	super.onCreate(svaedInstanceState)
        // ...
        acitivity = this
    }

    // ...

    companion object {
    	// 메모리 누수가 발생
      	var activity: MainAcivity? = null
    }
}
```

`companion` 프로퍼티 (static 필드)에 액티비티를 할당하면 가비지 컬렉터가 해당 객체에 대한 메모리를 해제할 수 없다. (액티비티는 굉장히 큰 객체라 메모리 누수가 크다!)

## 메모리 누수를 개선할 수 있는 방법

1. 리소스를 정적으로 유지하지 말 것

2. 의존 관계를 정적으로 저장하지 않고, 다른방법을 활용해서 적절하게 관리하기

3. 객체에 대한 레퍼런스를 다른 곳에 저장할 때는 메모리 누수가 발생할 가능성을 언제나 염두하기

```
class MainActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
    	super.onCreate(svaedInstanceState)
        // ...
        logError = { Log.e()this::class.simpleName, it.message) }
    }

    // ...

    companion object {
    	// 메모리 누수가 발생
        val logError: ((Throwable) -> Unit)? = null
    }
}
```

에러를 출력하는 함수타입 `logError`는 메인액티비티에 대한 레퍼런스를 사용하고 있으며 이를 정적으로 저장하여 메모리 누수가 발생한다.

그렇다면 메모리 누수를 어떻게 해결해야할까?

간단하게 해당 객체를 더 이상 사용하지 않을 때, 그 레퍼런스에 `null`을 설정하는 것이다.

```
private var _binding: ActivityMainBinding? = null
private val binding get() = _binding!!

override fun onCreate(
    savedInstanceState: Bundle?
): View? {
    _binding = ActivityMainBinding.inflate(inflater, container, false)
    return binding.root
}

override fun onDestroy() {
    super.onDestroy()
    _binding = null
}
```

안드로이드에서의 뷰바인딩에서도 `_binding`이라는 레퍼런스를 `onDestory`될 때 반환하라고 권장하고 있다.

또 다른 예를 보자

`lazy`처럼 동작해야 하지만, 상태 변경도 수행하는 `mutableLazy`프로퍼티 델리게이트를 구현했다고 하자.

```
fun <T> mutableLazy(initializer: () -> T): ReadWriteProperty<Any?, T> = MutableLazy(initializer)

private class MutableLazy<T>(
    val initializer: () -> T
) : ReadWriteProperty<Any?, T> {

    private var value: T? = null
    private var initialized = false

    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        synchronized(this) {
            if (!initialized) {
                value = initializer()
                initialized = true
            }
            return value as T
        }
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        synchronized(this) {
            this.value = value
            initialized = true
        }
    }
}
```

사용예는 다음과 같다.

```
class Game() {
    var coin = 0

    fun onGameStart() {
        println("코인${coin}개와 함께 게임 시작")
    }

    companion object {
        fun newGame(coin: Int): Game {
            return Game().apply { this.coin = coin }
        }
    }
}

fun main() {
    var game: Game? by mutableLazy {
        Game().apply { coin = 5 }
    }
    game = Game.newGame(1) // mutableLazy로 구현하여 객체가 바뀔 수 있다.
    game?.onGameStart() // "코인1개와 함께 게임 시작"
}
```

위의 `mutableLazy`의 구현은 한 가지 결점을 갖고 있다. `initializer`가 사용 후에도 해제되지 않는다는 것이다. `MutableLazy`에 대한 참조가 존재한다면 이는 더이상 필요 없어도 유지된다. 이를 개선한 코드는 다음과 같다.

```
private class MutableLazy<T>(
    val initializer: () -> T
) : ReadWriteProperty<Any?, T> {

    private var value: T? = null

    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        synchronized(this) {
        	val initializer = initializer
            if (initializer != null) {
                value = initializer()
                this.initializer = null
            }
            return value as T
        }
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        synchronized(this) {
            this.value = value
            this.initializer = null
        }
    }
}
```

`initializer`를 `null`로 설정하기 만하면, 가비지 컬렉터가 이를 처리해줄 것이다.

## 최적화 처리가 중요할까?

거의 사용되지 않는 객체가 이런 것을 신경 쓰는 것은 오히려 좋지 않을 수 있다. `쓸데없는 최적화가 모든 악의 근원`이라는 말도 있다. 하지만 오브젝트에 null을 설정하는 것은 그렇게 어려운 일이 아니므로, 무조건 하는 것이 좋다. 특히 많은 변수를 캡처할 수 있는 함수 타입, `Any` 또는 `제너릭` 타입과 같은 미지의 클래스일 때는 이렇나 처리가 중요하다.

라이브러리를 만들 때 이런 최적화는 중요시되며, 코틀린의 `lazy` 델리게이트는 사용 후 모두 `initialzer`를 `null`로 초기화한다.

```
private class SynchronizedLazyImpl<out T>(initializer: () -> T, lock: Any? = null) : Lazy<T>, Serializable {
    private var initializer: (() -> T)? = initializer
    @Volatile private var _value: Any? = UNINITIALIZED_VALUE
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
                    initializer = null // 객체를 놓아주기
                    typedValue
                }
            }
        }

    override fun isInitialized(): Boolean = _value !== UNINITIALIZED_VALUE

    override fun toString(): String = if (isInitialized()) value.toString() else "Lazy value not initialized yet."

    private fun writeReplace(): Any = InitializedLazyImpl(value)
}
```

코드를 작성할 때는 `메모리와 성능`뿐만 아니라 `가독성과 확장성`을 고려해야 한다. 라이브러리를 구현할 때는 메모리와 성능을 더 중요시 해야하며, 개발자가 읽을 코드는 가독성과 확장성을 더 중요시 해야한다.

메모리 누수가 발생하는 또 다른 예로 `절대 사용되지 않는 객체를 캐시해서 저장해 두는 경우`도 있다. 물론 캐시를 해 두는 것이 나쁜 것은 아니지만, 이것이 `OutOfMemoryError`를 일으킬 수 있다면, 아무런 도움도 되지 않을 것이다. 해결 방법으로는 `소프트 레퍼런스(soft refernce)`를 사용하는 것이다. 소프트 레퍼런스를 활용하면 메모리가 필요한 경우 가비지 컬렉터가 이를 알아서 해제한다. 하지만 메모리가 부족하지 않아서 해제되지 않다면 이를 사용한다.

화면 위의 대화상자와 같은 경우 일부 객체는 약한 레퍼런스를 사용하는 것이 좋을 수 있다. 대화상자가 출력되는 동안에는 가비지 컬렉터가 이를 수집하지 않고, 대화상자를 닫은후에는 이에 대한 참조를 유지할 필요가 없기에 정리된다.

## 정리

메모리 누수는 예측하기 어렵다. 어플리케이션이 크래시(crash)되기 전까지 있는지 확인하기 힘들 수도 있다. 특히 안드로이드(모바일)은 메모리 사용량에 엄격한 제한이 있기 때문에 별도의 도구를 활용해 메모리 누수를 찾을 수 있다. 기본적으로는 안드로이드 스튜디오에서 제공하는 프로파일러를 활용할 수 있으며, 메모리 누수를 검출해 주는 라이브러리 `LeakCanary`를 활용할 수 있다.

- 프로 파일러
  ![](https://velog.velcdn.com/images/cksgodl/post/45822b32-8d29-4fea-9270-fcafdd60d22c/image.png)

- `LeackCanary` 라이브러리

```
debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.6'
```

객체를 수동으로 해제해야 하는 경우는 굉장히 드물다. 안드로이드에서는 생명주기에 따라 객체를 해제해 주고 있으며, 대부분은 스코프를 벗어나면서 객체를 가리키는 레퍼런스가 제거될 때 자동으로 해제된다. 따라 메모리와 관련된 문제를 피하는 가장 좋은 방법은

> 변수의 스코프를 지역 스코프에 정의하고, 톱레벨 프로퍼티 또는 객체 선언(COMPANION 객체)로 큰 데이터를 저장하지 않는 것이다.
