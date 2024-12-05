# 컬렉션 처리 단계 수를 제한하라 🚫

개발을 하다보면 수많은 컬렉션을 처리하게된다. 이러한 컬레션 처리 메서드는 비용이 많이든다. 내부요소들을 반복을 돌며, 계산을 위해 추가적인 컬렉션을 만들어 사용한다. 

시퀀스를 만든다고 하여도, 시퀀스 전체를 랩하는 객체가 만들어지며, 조작을 위해서 또 다른 추가적인 객체를 만들어 낸다. 따라서

> 컬렉션 처리 단계 수를 적절하게 제한하는 것이 좋다.

다음 예를 보자.

```
Class Studnet(val name: String?)

// 동작은 합니다.
fun List<Studnet>.getNames(): List<String> = this
	.map { it.name }
    .filter { it!= null }
    .map { it!! }

// 더 좋습니다.
fun List<Student>.getNames(): List<String> = this
	.map { it.name }
    .filterNotNull()
    
// 가장 좋습니다.
fun List<Student>.getNames() : List<String> = this
	.mapNotNull { it.name }
```

사실 컬렉션 처리와 관련해서 비효율적인 코드를 작성하는 이유는 어떤 메서드가 존재하는지 몰라서인 경우가 많다. IDE에서 어느 정도 경고로 알려준다 하여도, 컬렉션 처리를 어떤 형태로 줄일 수 있는지 알아두면 좋다. 

다음은 두 단계 컬렉션 처리를 한번에 하는 메서드를 정리한 것이다.

`.filterNotNull`, `mapNotNull`, `joinToString`, `filterIsInstance<Type>`, `sortedWith(compareBy({ Key1 }, { Key2 }))`, `listOfNotNull`, `filterIndexed` 등등 ...


## 정리

대부분의 컬렉션의 비용은 `전체 컬렉션에 대한 반복`과 `중간 컬렉션 생성`이라는 비용이 발생한다. 이 비용은 적절한 컬렉션 처리 함수들을 활용해서 줄일 수 있다.

# 성능이 중요한 부분에는 기본 자료형 배열을 사용하라

이전 [`불필요한 객체 생성을 피하라`](https://velog.io/@cksgodl/Kotlin-%ED%9A%A8%EC%9C%A8%EC%84%B1-%EB%B6%88%ED%95%84%EC%9A%94%ED%95%9C-%EA%B0%9D%EC%B2%B4-%EC%83%9D%EC%84%B1%EC%9D%84-%ED%94%BC%ED%95%98%EB%9D%BC)에서 설명했듯이 기본 자료형은 장점 이있다.

1. 가볍다. (일반 객체들과는 다르게 추가적으로 포함되는 것이 없기 때문)
2. 빠르다. 값에 접근할 때 추가 비용이 들어가지 않는다.

따라서 대규모 데이터를 처리할 때 기본 자료형을 사용하면, 상당히 큰 최적화가 이루어진다. 

예를 들어 코틀린의 `List`, `Set`등과 같은 컬렉션은 제네릭 타입이다. [제네릭타입은 JVM에서 참조 타입](https://velog.io/@cksgodl/Kotlin-%ED%9A%A8%EC%9C%A8%EC%84%B1-Kolin%EA%B3%BC-Java%EC%9D%98-%EC%9B%90%EC%8B%9C-%ED%83%80%EC%9E%85-%EC%B0%B8%EC%A1%B0-%ED%83%80%EC%9E%85%EC%97%90-%EB%8C%80%ED%95%B4)으로 변환된다. 이렇게 하는 것이 더 처리가 쉬워짐으로 적합하지만, 성능이 중요한 코드라면 `IntArray`, `LongArray`등의 기본 자료형을 활용하는 배열을 사용하는 것이 좋다.

```
Kotlin.Int == Java.Int
List<Int> == Java.List<Integer>
Array<Int> == Java.Integer[]
IntArray == Java.int[]
```

기본 자료형 배열은 얼마나 가벼울까? 

코틀린/JVM에서 `1,000,000`개의 정수를 갖는 컬렉션을 만든다고 가정해보자. 이는 `IntArray`, `List<Int>`를 사용할 수 있을 것이다. 단순하게 할당되는 영역만 생각해도 이는 `IntArray`는 `400,000,016` 바이트, `List<Int>`는 `2,000,009,944`바이트를 할당한다. 

**약 5배정도가 차이나는 것이다. ** 또한 성능적으로도 약 25%더 빠르다.

기본 자료형을 포함하는 배열은 코드 성능이 중요한 부분을 최적화할 때 활용하면 좋다. 배열은 더 적은 메모리를 차지하고, 더 빠르게 동작한다. 다만 일반적인 경우에는 `List`의 경우가 더 편하고, 다양하고, 많은 곳에 쉽게 사용된다. 성능이 중요한 경우에만 `Array`를 사용하자.

## 정리

일반적으로 `Array`보다 `List`와 `Set`을 사용하는 것이 좋다. 하지만 기본 자료형의 컬렉션을 굉장히 많이 보유해야 하는 경우에는 성능을 높이고, 메모리 사용량을 줄일 수 있도록 `Array`를 사용하자.

---

# `mutable` 컬렉션 사용을 고려하라 🦽

> `immutable` 컬렉션보다 `mutable`컬렉션이 좋은 점은 성능적인 측면에서 빠르다는 것이다.

`immutable`컬렉션에 요소를 추가하려면, 새로운 컬렉션을 만들면서 여기에 요소를 추가해야 한다. 

```
public operator fun <T> Iterable<T>.plus(element: T): List<T> {
    if (this is Collection) return this.plus(element)
    val result = ArrayList<T>() 
    result.addAll(this) // 내부적으로 콜렉션을 복제
    result.add(element)
    return result
}
```

이처럼 콜렉션을 복제하는 비용은 굉장히 많이 든다. 그래서 복제 처리를 하지 않는 `mutable`컬렉션이 성능적 관점에서 좋다. 하지만 가변성을 제한하는 관점에서는 `immutable`컬렉션은 안전하다는 관점에서 좋다. 

일반적인 지역변수는 이러한 캡슐화의 대상이 되지 않음으로 지역변수를 사용할 때는 `mutable`컬렉션을 사용하는 것이 더 합리적이라고 할 수 있다. 표준 라이브러리도 어떤 처리를 내부적으로 할 때는`mutable`컬렉션을 사용하도록 구현되어 있다.


## 정리

가변 컬렉션을 추가처리가 더 빠르다. 일반적인 지역 변수는 `mutable`컬렉션을 사용하는 것을 고려하다. 


---

# 용어에 대해 😯

## 함수 vs 메서드??

코틀린에서 함수는 `fun`으로 시작한다. 이를 활용해서 다음과 같은 함수들을 만들 수 있다.

* 톱 레벨 함수
* 클래스의 멤버 함수
* 함수 내부의 지역 함수

다음 예를 보자

```
fun double(i: Int) = i * 2 // 톱 레벨 함수

class A {
	
    fun triple(i: Int) = i * 3 // 멤버 함수
    
    fun twelveTimes(i : Int): Int { // 멤버 함수 
    	fun fourTimes() = double(double(i)) // 지역 함수
    	return triple(fourTimes())
    }
}
```

추가적으로 함수 리터럴을 활용해서 익명 함수를 정의할 수도 있습니다.


```
val double = fun(i: Int) = i * 2 // 익명 함수
val triple = { i: Int -> i * 3 } // 람다 표현식
// 람다 표현식은 익명 함수를 더 짧게 표현한 것이다.
```

`메서드(method)`는 클래스와 연결된 함수이다. 위의 멤버함수(클래스에 정의되어 있는 함수)는 메서드이다. 메서드를 사용하려면 클래스 인스턴스가 존재해야 하며, 이를 활용해서 참조해야 한다. 다음 예제에서 `doubled`는 멤버이면서 메서드이다. 모든 메서드는 함수이므로, 함수이기도 하다

```
class IntWrapper(val i: Int) {
	fun doubled(): IntWrapper = IntWrapper(i * 2)
}

// 사용
val wrapper = IntWrapper(10)
val doubledWrapper = wrapper.doubled() // 메서드이자 함수

val doubledReference = IntWrapper::doubled
```

그렇다면 확장함수도 메서드인가? 에 대해서는 논란의 여지가 있겠지만, 이펙티브 코틀린의 저자는 확장함수를 호출할 때 인스턴트가 필요하므로 메서드로 보고 있다.

> 메서드는 함수의 부분집합이다.


## 파라미터 vs 아규먼트 🤔

파라미터(parameter)는 함수 선언에 정의되어 있는 변수를 의미하고, 아규먼트는 함수로 전달되는 실질적인 값을 의미한다. 다음 예제를 살펴보자. `randomString`의 `length`는 파라미터고, 함수 호출의 `10`이 아규먼트이다.


```
fun randomString(length: Int): String {
	// ...
}

randomString(10) // 아규먼트
```

제네릭 타입에서도 동일하게 적용된다. 제네릭으로 선언된 변할 수 있는 부분이 타입 파라미터이다. 실질적인 타입이 타입 아규먼트이다. 예를 보자

```
inline fun <refied T> printName() { // T -> 타입 파라미터
	print(T::class.simpleName)
}

fun main() {
	printName<String>() // String -> 타입 아규먼트
}
```

---

## 기본 생성자 vs 추가적인 생성자

생성자는 객체를 만들 때 호출하는 특별한 타입의 함수이다. 생성자는 클래스 내부에 다음과 같이 선언된다.
```
class SomeObject {
	val text: String
    
    constructor(text: String) {
    	this.text = text
        print("Creating object")
    }
}
```
생성자는 일반적으로 객체를 설정하는 데 사용된다. 이러한 생성자를 `기본 생성자(primary constructor)`라고 부른다. 기본 생성자는 클래스 이름 바로 뒤에 정의되며, 프로퍼티를 초기화할 때 사용할 파라미터를 받는다.

다음과 같은 단축 형식으로 많이 사용한다.

```
class SomeObject(val text: String) {
	
    init {
    	print("Creating object")
    }
}
```

추가로 다른 생성자를 만들어야 할 때는 어떻게 할까? 이때는 `추가적인 생성자(secondary constructor)`를 만들 수 있다. 추가적인 생성자는 `this`키워드를 활용하여 기본 생성자를 호출한다.

```
class SomeObject(val text: String) {
	
    constructor(date: Date): this(date.toString())
    
    iint {
    	print("Creating object")
    }
}
```

이러한 상황은 거의 사용되지 않는다. 대부분의 경우 디폴트 아규먼트 또는 팩토리 메서드를 활용하기 때문이다.








