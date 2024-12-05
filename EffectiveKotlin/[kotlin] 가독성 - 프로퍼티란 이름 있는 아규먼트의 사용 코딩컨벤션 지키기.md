
### 프로퍼티란??

[kotlinlang-properties](https://kotlinlang.org/docs/properties.html#backing-fields)

코틀린 클래스에서의 프로퍼티는 수정가능한 프로퍼티`var`과 read-only 읽기전용 프로퍼티 `val`로 나뉜다.
```
class Address {
    var name: String = "Holmes, Sherlock"
    var street: String = "Baker"
    var city: String = "London"
    var state: String? = null
    var zip: String = "123456"
}
```
프로퍼티를 활용하기 위해서는 이름으로 참조가 가능하다.
```
val result = Address() // deafult값으로 다 선언되어 있음
result.name = address.name // Holmes, Sherlock
result.street = address.street
```

#### Getters와 Setters

프로퍼티를 정의하는 전체 문법은 다음과 같다.

```
var <propertyName>[: <PropertyType>] [= <property_initializer>]
    [<getter>]
    [<setter>
```

생성자 게터, 세터의 정의는 `Optional`이며 프로퍼티의 타입은 코틀린의 타입추론에 의해 자동으로 추론된다.

```
var initialized = 1
var initialized: Int = 1 // Equal
```

변수를 읽기전용 프로퍼티인 `val`로 선언하면 setter를 지원하지 않는다.

또한 프로퍼티에 대해 커스텀 접근자를 선언이 가능하다. 이말은 즉 커스텀 `getter`을 활용하여 해당 프로퍼티에 접근할 때 어떠한 작업을 수행한 결과 값을 리턴할 수 있다.
```
class Rectangle(val width: Int, val height: Int) {
    val area: Int // getter의 리턴타입으로 추론되는 타입
        get() = this.width * this.height 
}
```

또한 커스텀 setter을 활용하여 해당 프로퍼티에 값을 정의할 때 이를 커스텀할 수 있다.
```
var stringRepresentation: String
    get() = this.toString()
    set(value) {
        field = setDataFromString(value) // 해당 함수의 리턴값이 assign된다.
    }
```
컨벤션에 따라 setter의 파라미터는 `value`로 정의한다.

#### Backing fields(백킹 필드)

코틀린에서 필드는 프로퍼티의 일부로써 값을 잠시 메모리에 잡아두기 위해 사용된다. Fields는 직접적으로 선언될 수 없으며 프로퍼티가 백킹필드가 필요할 때 자동으로 제공해준다. 백킹필디는 `field`접근자를 활용하여 참조한다.
```
var counter = 0 //  초기 initializer는 백킹필드에 직접 적용된다.
    set(value) {
        if (value >= 0)
            field = value
            // counter = value // ERROR StackOverflow : counter라는 프로퍼티에 set을 재귀적으로 불르고 있음
    }
```

백킹필드는 하나이상의 기본 접근자가 사용되거나, 커스텀 접근자에 의해 참조될 때 `field`를 통해 자동 생성된다.

다음예는 백킹필드가 생성되지 않는다.
```
val isEmpty: Boolean
    get() = this.size == 0
```

#### Backing properties(백킹 프로퍼티)

백킹 필드를 이용하고 싶지 않다면 백킹 프로퍼티를 사용할 수 있다.
```
private var _table: Map<String, Int>? = null
public val table: Map<String, Int>
    get() {
        if (_table == null) {
            _table = HashMap() // Type parameters are inferred
        }
        return _table ?: throw AssertionError("Set to null by another thread")
    }
```

---

### 프로퍼티는 동작이 아니라 상태를 나타내야 한다.

`var`을 사용해서 커스텀 게터와 세터를 정의한 프로퍼티를 **파생 프로퍼티**(derived property)라고 부른다.

코틀린의 모든 프로퍼티는 디폴트로 캡슐화가 되어있다. 
프로퍼티는 필드가 필요가 없다. 프로퍼티는 개념적으로 접근자`val`의 경우 게터, `var`의 경우 세터와 게터로 나타낸다. 따라서 코틀린은 인터페이스에서도 프로퍼티를 정의할 수 있다.
```
interface Person {
	val name: String
}
```
이렇게 코드를 작성하면 이는 게터를 가질 것이라는 것을 의미한다. 그럼으로 다음과 같이 오버라이드할 수 있다.
```
class Student: Person() {
	override val name: String = "해찬"
}
```
다음과 같이 프로퍼티를 위임할 수도 있다.

```
val Context.perferences: SharedPreferences
	get() = PreferenceManager.getDefaultSHaredPreferences(this)
```

프로퍼티를 함수 대신 사용할 수 있지만 완전히 대체해서 사용하는 것은 좋지 않다. 
다음과 같은 예를 보자.
```
val Tree<Int>.sum: Int
	get() = when (this) {
    	is Leaf -> value
        is Node -> left.sum + right.sum
    }
```
이러한 처리는 프로퍼티가 아니라 함수로 구현해야 한다.
```
val Tree<Int>.sum: Int = when (this) {
    	is Leaf -> value
        is Node -> left.sum + right.sum
    }
```
> 프로퍼티는 상태를 나타내거나 설정하기 위한 목적으로 사용되어야 한다.

프로퍼티 대신 함수를 사용해야하는 예이다.

* 연산 비용이 높거나, 복잡도가 O(1)보다 큰 경우
* 비즈니스 로직을 포함하는 경우
* 결정적이지 않은 경우 -> 같은 동작을 여러번했을 때 다른 값이 나오는 경우
* 변환의 경우 -> Int.toDouble()과 같은 경우 프로퍼티로 만들면 오해의 소지가 있다.
* 게터에서 프로퍼티의 상태 변경이 일어나야 하는 경우

반대로 상태를 추출/설정할 때는 프로퍼티를 사용해야 한다. 특별한 이유가 없다면 함수를 사용하면 안된다.

```
// 이렇게 하지 마세요!
class UserIncorrect {
	private var name: String = ""
    
    fun getName() = name
    
    fun setName(name: String) {
    	this.name = name
    }
}

calss UserCorrect {
	var anme: String = ""
}
```

> 프로퍼티는 상태 집합을 나타내고, 함수는 행동을 나타낸다.

---

### 이름 있는 아규먼트를 사용하라

코드에서 아규먼트의 의미가 명확하지 않은 경우가 있다.
```
val text = (1..100).joinToString("|")
```
다음 코드를 보고 `"|"`로 구분을 하는건지 합친다는 것인지 한눈에 알아보기 힘들다.

따라서 명확하게 보이지 않는 파라미터는 이를 직접 지정해서 명확하게 만들어 줄 수 있다. `이름 있는 아규먼트`를 사용하자

```
val text = (1..100).joinToString(separator = "|")
```
또는 변수를 활용해서 의미를 명확하게 할 수 있다.
```
val separator = "|"
val text = (1..100).joinToString(separator = separator)
```

#### 이름있는 아규먼트는 언제 사용해야 할까?

이름 있는 아규먼트의 장점은 다음과 같다.

* 이름을 기반으로 값이 무엇을 나타내는지 알 수 있다.
* 파라미터 입력 순서와 상관 없음으로 안전하다.

어떠한 람다함수가 무슨 행동을 하는지, 순서가 바뀌어도 명확하다.

* 디폴트 아규먼트가 있는경우
* 같은 타입의 파라미터가 많은 경우
* 함수 타입의 파라미터가 있는 경우
```
		repository.getData(
			{ setIsLoading(true) },
			{ setIsLoading(false) },
			{ setOnErrorMsg(it) },
			{ setOnException(it) },
			{ setOnFailureMsg(it) }
		)
        // And
		repository.getData(
			onStart = { setIsLoading(true) },
			onComplete = { setIsLoading(false) },
			onError = { setOnErrorMsg(it) },
			onException = { setOnException(it) },
			onFailure = { setOnFailureMsg(it) }
		)
```
이름있는 아규먼트를 사용하는 것이 훨씬 이해하기 쉽다. 

> 이는 개발자가 코드를 읽을 때도 편리하게 활용되며, 코드의 안정성도 향상시킬 수 있다. 또한 함수에 같은 타입의 라파미터가 여러개인 경우, 함수 타입의 파라미터가 있는 경우, 옵션 파라미터가 있는 경우 등은 이름 있는 아규먼트를 활용하자.


### 코딩 컨벤션을 지키자

코딩 컨벤션을 지켜야 하는 이유
* 어떤 프로젝트를 접해도 쉽게 이해할 수 있다.
* 다른 외부 개발자도 프로젝트의 코드를 쉽게 이해할 수 있다.
* 다른 개발자도 코드의 작동 방식을 쉽게 추측할 수 있다.
* 코드를 병합하고, 한 프로젝트의 코드 일부를 다른 코드로 이동하는 것이 쉽다.

> 코딩 컨벤션을 확실하게 읽고, 정적 검사기 static checker를 활용하여 코딩 컨벤션의 일관성을 준수하자.
