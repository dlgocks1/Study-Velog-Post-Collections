
## 10.1 다른 함수를 반환하거나 수신하는 함수 선언하기: 고차 함수

 고차 함수는 다른 함수를 인수로 받거나 함수를 반환하는 함수이다. 이는 람다라고 하기도 하며 `Kotlin`에서 함수는 람다를 사용하거나 함수 참조를 통해 값으로 표현할 수 있다. 
 
따라서 고차 함수는 람다 또는 함수 참조를 인수로 전달할 수 있는 모든 함수 또는 둘 중 하나 또는 둘 모두를 반환하는 함수를 말한다. 예를 들어 필터 표준 라이브러리 함수는 술어 함수를 인수로 사용하므로 고차 함수에 해당한다.

`list.filter { x > 0 }`

### 함수 유형은 람다의 매개변수 유형과 반환값을 지정한다.

```kotlin
val sum = { x: Int, y: Int -> x + y }
val action = { println(42) }
```

이 경우 컴파일러는 합과 액션 변수 모두 함수 유형을 가지고 있다고 추론한다. 따라서 스마트 캐스팅이 가능해진다.

![](https://velog.velcdn.com/images/cksgodl/post/e503621c-f270-4474-8c25-545951245604/image.png)

이제 이러한 변수에 대한 명시적 타입 선언은 아래와 같다.

```kotlin
val sum: (Int, Int) -> Int = { x, y -> x + y }   
val action: () -> Unit = { println(42) }
```

반환 타입을 널 타입처럼 표시할 수 있다.

```kotlin
var canReturnNull: (Int, Int) -> Int? = { x, y -> null }

var funorNull: ((Int, Int) -> Int)? = null
```

![](https://velog.velcdn.com/images/cksgodl/post/a2a9c94d-8c0d-42d9-bfd8-b2955d6f80eb/image.png)


### 10.1.2 인자로 전달된 함수 호출

이제 지역 변수에 `Kotlin`에서 함수 유형을 지정하는 방법을 알았으니 이제 고차 함수를 구현하는 방법에 대해 알아보겠다. 

```kotlin
fun twoAndThree(operation: (Int, Int) -> Int) {
    val result = operation(2, 3)
    println("The result is $result")
}

fun main() {
    twoAndThree { a, b -> a + b }
    // The result is 5
    twoAndThree { a, b -> a * b }
    // The result is 6
}
```

인자로 전달된 함수를 호출하는 구문은 정규 함수를 호출하는 것과 동일하다. 함수 이름 뒤에 괄호를 붙이고 괄호 안에 매개 변수를 넣으면 된다.

+) 함수 유형의 매개변수 이름은 자유롭게 지정할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/891c080d-4e7b-4644-924f-5de24f5c3980/image.png)

### Java 람다가 Kotlin 함수 유형으로 자동 변환

5장에서 이미 살펴보았듯이 자동 SAM(단일 추상 메서드) 변환을 통해 함수형 인터페이스를 기대하는 모든 `Java` 메서드에 `Kotlin` 람다를 전달할 수 있다. 

즉, `Kotlin` 코드가 `Java` 라이브러리에 의존하고 `Java`에 정의된 고차 함수를 문제 없이 호출할 수 있다. 마찬가지로 함수형을 사용하는 `Kotlin` 함수도 `Java`에서 쉽게 호출할 수 있다. `Java` 람다는 다음 목록과 같이 함수 유형의 값으로 자동 변환된다.

```kotlin
* Kotlin declaration */
fun processTheAnswer(f: (Int) -> Int) {
    println(f(42))
}
/* Java call */
processTheAnswer(number -> number + 1);
// 43
```

> 함수유형 : 구현 세부 정보
> 
> 내부적으로 `Kotlin` 함수 유형은 일반 인터페이스이며, 함수 유형의 변수는 FunctionN 인 터페이스의 구현이다. 사용할 수 있는 인터페이스는 함수 인수의 수에 따라 열거된다: 
- `Function0<R>`(이 함수는 인수를 받지 않고 반환 유형만 지정함), 
- `Function1<P1, R>`(이 함수는 인수를 하나만 받음)
> 각 인터페이스는 하나의 호출 메서드를 정의하며, 이를 호출하면 함수가 실행된다.
```kotlin
fun processTheAnswer(f: Function1<Int, Int>) {
    println(f.invoke(42))
}
```

### 10.1.4 함수 유형이 있는 매개변수는 기본값을 제공하거나 `nullable`할 수 있다.

```kotlin
fun <T> Collection<T>.joinToString(
        separator: String = ", ",
        prefix: String = "",
        postfix: String = "",
        transform: (T) -> String = { it.toString() }
): String {
    val result = StringBuilder(prefix)
    for ((index, element) in this.withIndex()) {
        if (index > 0) result.append(separator)
        result.append(transform(element))
	}
    result.append(postfix)
    return result.toString()
}

fun main() {
    val letters = listOf("Alpha", "Beta")
    println(letters.joinToString())
    // Alpha, Beta
    println(letters.joinToString { it.lowercase() })
    // alpha, beta
    println(letters.joinToString(separator = "! ", postfix = "! ", transform = { it.uppercase() }))
	// ALPHA! BETA!
```

`transform`이 `nullable`이면 다음과 같이 수정할 수 있다.

```kotlin
fun <T> Collection<T>.joinToString(
        separator: String = ", ",
        prefix: String = "",
        postfix: String = "",
        transform: ((T) -> String)? = null
): String {
    val result = StringBuilder(prefix)
    for ((index, element) in this.withIndex()) {
        if (index > 0) result.append(separator)
        val str = transform?.invoke(element)
            ?: element.toString()
        result.append(str)
    result.append(postfix)
    return result.toString()
}
```

`transform`은 널 가능 함수 타입의 매개변수이지만 널 가능하지 않은 반환 타입을 가진다. `transform`이 `null`이 아닌 경우 `null`이 아닌 `String` 타입의 값을 반 환하도록 보장된다.

### 10.1.5 함수에서 함수 반환

다른 함수에서 함수를 반환해야 하는 요구 사항은 다른 함수에 함수를 전달하는 것 만큼 자주 발생하지는 않지만 여전히 유용하다.

```kotlin
enum class Delivery { STANDARD, EXPEDITED }

class Order(val itemCount: Int)

fun getShippingCostCalculator(delivery: Delivery): (Order) -> Double {
    if (delivery == Delivery.EXPEDITED) {
        return { order -> 6 + 2.1 * order.itemCount }
	}
    return { order -> 1.2 * order.itemCount }
}

fun main() {
	val calculator = getShippingCostCalculator(Delivery.EXPEDITED) 
    println("Shipping costs ${calculator(Order(3))}")
	// Shipping costs 12.3 Invokesthe
}
```

아래는 접두사를 확인하고 필요한 경우 전화번호가 있는지 여부도 확인하는 필터를 생성하는 예제이다.

```kotlin
data class Person(
        val firstName: String,
        val lastName: String,
        val phoneNumber: String?
)

class ContactListFilters {
    var prefix: String = ""
    var onlyWithPhoneNumber: Boolean = false
    fun getPredicate(): (Person) -> Boolean {
        val startsWithPrefix = { p: Person ->
			p.firstName.startsWith(prefix) || p.lastName.startsWith(prefix)
        }
        if (!onlyWithPhoneNumber) {
            return startsWithPrefix
        }
        return { startsWithPrefix(it)
                    && it.phoneNumber != null }
	} 
}

fun main() {
    val contacts = listOf(
        Person("Dmitry", "Jemerov", "123-4567"),
        Person("Svetlana", "Isakova", null)
    )
    val contactListFilters = ContactListFilters()
    with (contactListFilters) {
		prefix = "Dm"
        onlyWithPhoneNumber = true
    }
    println(contacts.filter(contactListFilters.getPredicate()))
	// [Person(firstName=Dmitry, lastName=Jemerov, phoneNumber=123-4567)]
}
```

### 10.1.6 람다로 중복을 줄여 코드 재사용성 높이기

많은 종류의 코드 중복을 이제 간결한 람다 표현식을 사용하여 제거할 수 있다.

```kotlin
data class SiteVisit(
    val path: String,
    val duration: Double,
    val os: OS
)

enum class OS { WINDOWS, LINUX, MAC, IOS, ANDROID }

val log = listOf(
    SiteVisit("/", 34.0, OS.WINDOWS),
    SiteVisit("/", 22.0, OS.MAC),
    SiteVisit("/login", 12.0, OS.WINDOWS),
    SiteVisit("/signup", 8.0, OS.IOS),
    SiteVisit("/", 16.3, OS.ANDROID)
)
```

평균을 구해야한다고 할 때 다음과 같이 작업을 수행할 수 있다.

```kotlin
fun main() {
    val averageWindowsDuration = log
    	.filter { it.os == OS.WINDOWS }
    	.map(SiteVisit::duration)
	    .average()

	println(averageWindowsDuration)
    // 23.0
}
```

아래처럼 확장함수로 구현할 수도 있다.

```kotlin
fun List<SiteVisit>.averageDurationFor(os: oS) =
		filter { it.os == os 
    }.map(SiteVisit::duration)
    .average()

fun main() { 	
	println(log.averageDurationFor(oS.WINDoWS)) 
    // 23.0 		
	println(log.averageDurationFor(oS.MAC))
	// 22.0
}
```

## 10.2 인라인 함수로 람다의 오버헤드 제거하기

`Kotlin`에서 람다를 함수에 인수로 전달하는 속기 구문이 `if` 및 `for`와 같은 일반문 구문과 비슷하다는 것을 눈치챘을 것이다. 

5장에서는 람다가 일반적으로 익명 클래스로 컴파일된다고 설명했다. 하지 만 이는 람다 표현식을 사용할 때마다 추가 클래스가 생성되고, 람다가 일부 변수를 캡처하는 경우 호출할 때마다 새 객체가 생성된다는 것을 의미한다. 이로 인해 런타임 오버헤드가 발생하여 람다를 사용하는 구현이 동일한 코드를 직접 실행하는 함수보다 효율성이 떨어진다.

### 10.2.1 인라이닝은 각 호출 사이트에 함수 본문을 대체하는 것을 의미한다.

함수를 인라인으로 선언하면 본문이 인라인이 된다. 즉, 함수가 호출되는 위치에서 호출되지 않고 직접 대체된다.결과 코드를 이해하기 위해 예제를 살펴보겠다.

```kotlin
import java.util.concurrent.locks.Lock
import java.util.concurrent.locks.ReentrantLock

inline fun <T> synchronized(lock: Lock, action: () -> T): T {
    lock.lock()
	try {
        return action()
	} finally {
        lock.unlock()
    }
}
```

위와같은 `synchronized`함수를 아래 함수로 작성할 수 있다.

```kotlin
fun foo(l: Lock) {
    println("Before sync")
    synchronized(l) {
        println("Action")
    }
    println("After sync")
}
```

![](https://velog.velcdn.com/images/cksgodl/post/4eb4ce9c-b30c-47e2-95d0-1a9ceaf41e35/image.png)

실제 바이트코드 단 구현은 위 그림과 같이 구현된다. 이렇게 함수 본문에 인라인 됨으로써 오버헤드를 줄일 수 있다.

### 10.2.2 인라인 기능에 대한 제한사항

인라인이 수행되는 방식 때문에 람다를 사용하는 모든 함수에 인라인을 적용할 수 있는 것은 아닙니다. 함수가 인라인 처리되면 인수로 전달된 람다 표현식의 본문이 결과 코드에 직접 대체됩니다. __이렇게 하면 함수 본문에서 해당 매개변수의 사용 가능성이 제한된다.__

람다 매개변수가 호출되면 이러한 코드는 쉽게 인라인 처리될 수 있다. 그러나 매개변수가 나중에 사용하기 위해 어딘가에 저장되어 있는 경우 이 코드를 포함하는 객체가 있어야 하므로 람다 표현식의 코드를 인라인 처리할 수 없다:

```kotlin
class FunctionStorage {
	var myStoredFunction: ((Int) -> Unit)? = null 
	inline fun storeFunction(f:(Int)->Unit){
        myStoredFunction = f
    }
}
```

따라서 위와 같은 코드는 에러가 발생하게 된다.

`
Illegal usage of inline-parameter 'f' in 'public final inline fun storeFunction(f: (Int) -> Unit): Unit defined in com. navercorp. gcclab. service. productmanage. FunctionStorage'. Add 'noinline' modifier to the parameter declaration
`

따라서 두 개 이상의 람다를 인자로 받는 함수가 있는 경우 일부 람다만 인라인 처리하도록 선택할 수 있다. 이는 람다 중 하나에 많은 코드가 포함될 것으로 예상되거나 인라인을 허용하지 않는 방식으로 사용되는 경우에 유용하다. 인라인이 불가능한 람다를 허용하는 매개변수에는 `noinline` 수정자를 사용하여 표시할 수 있다:

```kotlin
inline fun foo(inlined: () -> Unit, noinline notInlined: () -> Unit) {
  // ...
}
```

### 10.2.3 수집 작업 인라이닝

컬렉션에서 작동하는 `Kotlin` 표준 라이브러리 함수의 성능을 고려해 볼 수 있다.

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(Person("Alice", 29), Person("Bob", 31))

fun main() {
    println(people.filter { it.age < 30 })
    // [Person(name=Alice, age=29)]
}
```

`Kotlin`에서 필터 함수는 인라인으로 선언된다. 즉, 필터 함수의 바이트코드가 필터 함수에 전달된 람다의 바이트코드와 함께 필터가 호출되는 위치에 인라인 처리된다. __결과적으로는 `Kotlin`의 인라인 함수 지원으로 성능에 대해 걱정할 필요가 없다.__

추가적으로 성능에 대한 걱정으로 모든 컬렉션처리를 `Sequence`로 처리하는 것은 그렇게 좋지 못하다. 이는 대규모 컬렉션에만 도움이 되며, 소규모 컬렉션은 일반 컬렉션 연산으로 잘 처리할 수 있다.

### 10.2.4 함수를 인라인으로 선언할 시기 결정하기

코드 베이스 전체에 인라인을 사용하여 더 빠르게 실행하려는 시도를 해볼 수 있다. 하지만 이는 좋은 생각이 아니다. 인라인 키워드를 사용하면 람다를 인수로 사용하는 함수에서만 성능이 향상될 가능성이 높으며, 다른 모든 경우에는 애플리케이션에 대한 추가 조사, 측정 및 프로파일링이 필요하다.

일반 함수 호출의 경우, `JVM`은 이미 강력한 인라이닝 지원을 제공합니다. 코드 실행을 분석하여 호출을 인라인 처리하는 것이 가장 이점이 있을 때마다 인라인 처리한다. 이는 바이트코드를 머신 코드로 변환하는 동안 자동으로 이루어진다. 

바이트코드에서는 각 함수의 구현이 한 번만 반복되므로 `Kotlin`의 인라인 함수처럼 함수가 호출되는 모든 위치에 복사할 필요가 없다. 또한 함수가 직접 호출되는 경우 스택 추적이 더 명확하다.

> 현재 JVM은 호출과 람다를 통해 항상 인라이닝을 수행할 만큼 충분히 똑 똑하지 않는다. 인라이닝을 잘 사용하면 이 장의 뒷부분에서 설명할 비로컬 리턴과 같이 일반 람다로는 불가능한 기능을 사용할 수 있다

### 10.2.5 인라인 람다를 사용하여 리소스 관리에 withLock, use 및 useLines 사용

람다가 중복 코드를 제거할 수 있는 일반적인 패턴 중 하나는 리소스 관리입니다. 작업 전에 리소스를 확보하고 작업 후에 해제하는 것이다. 여기서 리소스란 파일, 락, 데이터베이스 트랜잭션 등 다양한 것을 의미할 수 있다. 

이러한 패턴을 구현 하는 표준 방법은 시도 블록 전에 리소스를 획득하고 최종 블록에서 해제하는 `try/finally` 문을 사용하거나 `Java`의 `try-with-resources`와 같은 특수 언어 구문을 사용하는 것이다.

코틀린에서는 표준 라이브러리에서 편의 기능(`withLock`, `use`, `useLines`등)을 람다로 제공한다.

```kotlin
val l: Lock = ReentrantLock()
l.withLock {
    // access the resource protected by this lock
}
```

```kotlin
inline fun <T> Lock.withLock(action: () -> T): T {
    lock()
    try {
        return action()
    } finally {
        unlock()
	}
}
```

## 10.3 람다에서 반환하기: 고차 함수의 제어 흐름

람다에서 에서의 브랜치 문을 다루는 방법을 알아보자.

### 10.3.1 람다의 반환문: 둘러싸는 함수에서 반환하기

컬렉션을 반복하는 두 가지 방법을 비교해 보자.

```kotlin
data class Person(val name: String, val age: Int)

val people = listOf(Person("Alice", 29), Person("Bob", 31))

// 1
fun lookForAlice(people: List<Person>) {
    for (person in people) {
        if (person.name == "Alice") {
            println("Found!")
            return
		} 
	}
    println("Alice is not found")
}

// 2
fun lookForAlice(people: List<Person>) {
    people.forEach {
		if (it.name == "Alice") {
    		println("Found!")
        	return
		} 
    }
    println("Alice is not found")
}

fun main() {
    lookForAlice(people)
    // Found!
}
```

람다에서 `return` 키워드를 사용하면 람다 자체에서 반환되는 것이 아니라 람다를 호출한 함수에서 반환된다. 이러한 반환문은 반환문이 포함된 블록보다 더 큰 블록에서 반환되므로 __비로컬반환__이라고 한다.

람다를 인수로 받는 함수에 `inline`이 있는 경우에만 외부 함수에서 반환이 가능하다는 점에 유의하자. 이유는 인라인 함수가 전달된 람다를 변수에 저장할 수 있기 때문이다. 즉, 함수가 이미 반환된 후에 람다가 실행될 수 있으므로 람다가 주변 함수가 반환되는 시점에 영향을 미치기에는 너무 늦는다.

### 10.3.2 람다에서 돌아오기: 레이블과 함께 반환

람다 표현식에서 로컬 반환을 작성할 수도 있다. 로컬 반환은 람다의 실행을 중지하고 람다가 호출된 코드의 실행을 계속한다. 

로컬 반환과 비로컬 반환을 구별하기 위해 2장에서 간략하게 살펴본 레이블을 사용한다. 반환하려는 람다 표현식에 레이블을 지정한 다음 반환 키워드 뒤에 이 레이블을 참조할 수 있다. 

```kotlin
fun lookForAlice(people: List<Person>) {
    people.forEach label@{
		if (it.name != "Alice") return@label
			print("Found Alice!")
		} 
	}
}

fun main() {
    lookForAlice(people)
    // Found Alice!
}
```

### 10.3.3 익명 함수: 기본적으로 로컬 반환

익명 함수는 람다식을 작성하는 또 다른 구문 형식이다. 따라서 익명 함수를 사용하는 것은 다른 함수에 전달할 수 있는 코드 블록을 작성하는 또 다른 방법이다. 

```kotlin
fun lookForAlice(people: List<Person>) {
    people.forEach(fun (person) {
        if (person.name == "Alice") return
        println("${person.name} is not Alice")
    }
}

fun main() {
    lookForAlice(people)
    // Bob is not Alice.
}
```

익명함수는 이름이 생략되고 매개변수 유형을 유추할 수 있다는점을 제외하면 일반함수와 비슷해 보인다. 다음은 또 다른 예시이다.

```kotlin
people.filter(fun (person): Boolean {
    return person.age < 30
})
```

![](https://velog.velcdn.com/images/cksgodl/post/6fd68dd3-9544-49bf-9424-15febd6dc561/image.png)

익명 함수는 일반 함수 선언과 비슷해 보이지만 람다 표현식의 또 다른 구문 형식이 라는 점에 유의하라. 일반적으로는 익명 함수보단 람다 구문을 사용하게 된다. 익명 함수는 주로 람다 구문을 사용할 때 레이블을 지정해야 하는 초기 반환문이 많은 코드를 단축하는 데 도움이 된다.

람다 표현식이 구현되는 방식과 인라인 함수에 대한 인라인 방식에 대한 논의는 익명 함수에도 적용된다.

## 요약

- 함수유형을 사용하면 함수에 대한 참조가 있는 변수, 매개변수 또는 함수반환값을 선언할 수 있다.
- 고차 함수는 다른 함수를 인수로 받거나 반환한다. 함수 유형을 함수 매개변수 또는 반환 값의 유형으로 사용하여 이러한 함수를 만들 수 있다.
- 인라인 함수가 컴파일되면 해당 바이트코드가 전달된 람다의 바이트코드와 함께 호출 함수의 코드에 직접 삽입된다. 이렇게 하면 유사한 코드를 직접 작성할 때와 비교하여 오버헤드 없이 호출이 이루어진다.
- 고차함수를 사용하면 단일 컴포넌트의 파트내에서 코드를 재사용할 수 있으며 강력한 일반 및 범용 라이브러리를 구축할 수 있다.
- 인라인 함수를 사용하면 둘러싸는 함수에서 반환되는 람다에 위치하는 비로컬 반환 표현식을 사용할 수 있다.
- 익명함수는 반환식을 해결하는 다른 규칙을 가진 람다식에 대한 대체구문을 제공한다. 여러 종료 지점이 있는 코드 블록을 작성해야 하는 경우 사용할 수 있다.




