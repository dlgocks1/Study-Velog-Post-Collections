이번장에서는 아래 포인트 클래스에 대한 산술연산자 오버로딩 예제를 보며 컨벤션과 오퍼레이터 오버로딩에 대해 알아본다.

```kotlin
data class Point(val x: Int, val y: Int)
```

## 9.1 산술 연산자를 오버로드하면 임의의 클래스에 대한 연산이 더 편리해진다.

`Kotlin`에서 규칙을 사용하는 가장 간단한 예는 산술 연산자이다. `Java`에서는 전체 산술 연산자 집합을 기본유형에만 사용할 수 있으며, 추가로 `+` 연산자를 문자열값에 사용할 수 있다. 

하지만 이러한 연산은 다른 경우에도 편리할 수 있다. 예를 들어 `BigInteger` 클래스를 통해 숫자로 작업하는 경우 `add` 메서드를 명시적으로 호출하는 것보다 `+`를 사용하여 합산하는 것이 더 우아할 수 있다

### 9.1.1 또한 곱하기, 나누기 등 다양한 연산이 가능하다: 이진 산술 연산 오버로딩

첫번째로 지원하게 될 연산은 두점을 더하는 것이다. 이 연산은 점의 x좌표와 y좌표를 합산한다.

```kotlin
data class Point(val x: Int, val y: Int) {
    operator fun plus(other: Point): Point {
		return Point(x + other.x, y + other.y)
	} 
}

fun main() {
    val p1 = Point(10, 20)
    val p2 = Point(30, 40)
    println(p1 + p2)
    // Point(x=40, y=60)
}
```

더하기연산자는 내부적으로는 아래 그림과 같이 더하기 함수를 참조한다.

![](https://velog.velcdn.com/images/cksgodl/post/ed2fe2b2-9310-429c-82e5-658146411682/image.png)

즉 아래처럼 구현되어도 상관없다.

```kotlin
operator fun Point.plus(other: Point): Point {
    return Point(x + other.x, y + other.y)
}
```

Kotlin에는 오버로드할 수 있는 연산자 집합이 제한되어 있으며, 각 연산자는 클래스에서 정의해야 하는 함수의 이름에 해당한다. 아래 표에는 정의할 수 있는 모든 이진 연산자와 해당 함수 이름이 나열되어 있다.

![](https://velog.velcdn.com/images/cksgodl/post/e84b6466-165c-4b5b-94a6-86317e7ad4e0/image.png)

연산자를 정의할 때 두 연산자에 동일한 유형을 사용할 필요는 없다. 예를 들어, 소수점 단위로 점의 크기를 조정할 수 있는 연산자를 정의해 보겠다.

```kotlin
operator fun Point.times(scale: Double): Point {
    return Point((x * scale).toInt(), (y * scale).toInt())
}
fun main() {
    val p = Point(10, 20)
    println(p * 1.5)
    // Point(x=15, y=30)
}
```

### 9.1.2 연산을 적용하고 즉시 값을 할당: 복합 할당 연산자 오버로딩

일반적으로 `+`와 같은 연산자를 정의할 때 `Kotlin`은 `+` 연산뿐만 아니라 `+=`도 지원한다. `+=`, `-=` 등과 같은 연산자를 복합 할당 연산자라고 한다.

```kotlin
fun main() {
	var point = Point(1, 2) point += Point(3, 4)	 
    println(point)
	// Point(x=4, y=6)
}
```

`Kotlin` 표준 라이브러리에는 변경 가능한 컬렉션에 `plusAssign` 함수가 정의되어 있으며, 이를 오버로딩하여 사용한다.

```kotlin
operator fun <T> MutableCollection<T>.plusAssign(element: T) {
    this.add(element)
}
```

`mutable` 콜렉션의 경우 기존의 콜렉션에 요소를 더하는 반면, `immutable`한 콜렉션의 경우 새로운 객체를 반환한다.

```kotlin
fun main() {
	val list = mutableListOf(1, 2)
	list += 3 +=changeslist.
	val newList = list + listOf(4, 5)
	println(list)
	// [1, 2, 3]
	println(newList)
	// [1, 2, 3, 4, 5]
}
```

### 9.1.3 피연산자가 하나만 있는 연산자: 단항 연산자 오버로딩

단항 연산자를 오버로드하는 절차는 앞서 살펴본 것과 동일하다.

```kotlin
operator fun Point.unaryMinus(): Point {
    return Point(-x, -y)
}
fun main() {
    val p = Point(10, 20)
    println(-p)
    // Point(x=-10, y=-20)
}
```
![](https://velog.velcdn.com/images/cksgodl/post/7e691af4-bc2f-4258-97c7-50075a962bd0/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/b8e669c1-a490-4bf7-b612-d60ce3da1553/image.png)

## 9.2 비교 연산자를 오버로드하면 개체 간의 관계를 쉽게 확인할수 있다.

산술 연산자와 마찬가지로 `Kotlin`에서는 기본 유형뿐만 아니라 모든 객체에 비교 연산자 (`==`, `!=`, `>`, `<` 등)를 사용할 수 있다.

### 9.2.1 등호 연산자: 등호(==)

`Kotlin`에서 `==` 연산자를 사용하면 `equals` 메서드의 호출로 변환되는 것을 보았다. `nullable`하여도 널처리가 들어갈 뿐 `equals`를 호출하는 것은 동일하다.

![](https://velog.velcdn.com/images/cksgodl/post/da95aa0c-3499-4464-aea3-9a57b15bdd2c/image.png)

```kotlin
class Point(val x: Int, val y: Int) {
    override fun equals(other: Any?): Boolean {
        if (other === this) return true
        if (other !is Point) return false
        return other.x == x && other.y == y
	} 
}

fun main() {
    println(Point(10, 20) == Point(10, 20))
    // true
    println(Point(10, 20) != Point(5, 5))
    // true
    println(null == Point(1, 2))
    // false
}
```

### 9.2.2 순서 연산자: 비교 대상(<, >, ? , >=)

`Java`에서 클래스는 최대값 찾기나 정렬과 같이 값을 비교하는 알고리즘에 사용하기 위해 `Comparable` 인터페이스를 구현할 수 있다.

`Kotlin`은 동일한 `Comparable` 인터페이스를 지원한다. 아래 그림같이 해당 인터페이스에 정의된 `compareTo` 메서드를 규칙에 따라 호출할 수도 있으며 비교 연산자(`<, >, ? 및 >=`)의 사용은 `compareTo`의 호출로 변환된다. `compareTo`의 반환 유형은 `Int`여야 한다.

![](https://velog.velcdn.com/images/cksgodl/post/98464a1d-d2b4-4b67-bfdc-096f0f9468d7/image.png)

```kotlin
class Person(
        val firstName: String, val lastName: String
) : Comparable<Person> {
    override fun compareTo(other: Person): Int {
        return compareValuesBy(this, other,
            Person::lastName, Person::firstName)
	} 
}

fun main() {
    val p1 = Person("Alice", "Smith")
    val p2 = Person("Bob", "Johnson")
    println(p1 < p2)
    // false
}
```

## 9.3 컬렉션 및 범위에 사용되는 규칙

컬렉션 작업에서 인덱스는 많이 활용된다. 인덱스 연산을 지원하는 데 사용되는 규칙을 살펴보자.

### 9.3.1 인덱스로 요소에 액세스하기: 가져오기 및 설정 규칙

`Kotlin`에서는 대괄호를 통해 `Java`에서 배열에 액세스하는 방식과 유사하게 맵의 요소에 액세스할 수 있다는 것을 이미 알고 있을 것이다.

`val value = map[key]`

동일한 연산자를 사용하여 변경 가능한 맵에서 키의 값을 변경할 수 있다: 

`mutableMap[key] = newValue`

이제 이것이 어떻게 작동하는지 알아보겠다. 액세스 연산자를 사용하여 요소를 읽는 것은 `get` 연산자 메서드의 호출로 변환되고, 요소를 쓰는 것은 `set` 메서드의 호출로 변환된다. 

```kotlin
operator fun Point.get(index: Int): Int { 
	return when(index) {
		0 -> x
		1 -> y
		else -> throw IndexOutOfBoundsException("Invalid coordinate $index")
	}
}

fun main() {
    val p = Point(10, 20)
    println(p[1])
    // 20
}
```

`get`의 매개변수는 `Int`뿐만 아니라 모든 유형이 될 수 있다는 점에 유의하자. 예를 들어 맵에서 인덱싱 연산자를 사용하는 경우 매개변수 유형은 맵의 키 유형이며 임의의 유형이될 수 있다.

여러 매개변수를 사용하여 `get` 메서드를 정의할 수 도 있다. 예를 들어 2차원 배열이나 행렬을 나타내는 클래스를 구현하는 경우 다음과 같은 메서드를 정의할 수있다.

`get(rowIndex: Int, colIndex: Int)` 그리고 `matrix[row, col]`로 호출한다. 여러 개의 오버로드된 컬렉션에 다른 키 유형으로 액세스할 수 있는 경우 다른 매개변수 유형으로 메서드를 가져올 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/9cd48488-29fb-4f1d-b62d-6a5ab9c7be42/image.png)

```kotlin
data class MutablePoint(var x: Int, var y: Int)

operator fun MutablePoint.set(index: Int, value: Int) {
    when(index) {
    	0 -> x = value
		1 -> y = value
		else -> throw IndexOutOfBoundsException("Invalid coordinate $index")
	} 
}

fun main() {
	val p = MutablePoint(10, 20)
	p[1] = 42
	println(p)
	// MutablePoint(x=10, y=42)
}
```

### 9.3.2 객체가 컬렉션에 속하는지 확인하기: "in" 컨벤션

컬렉션에서 지원하는 다른 연산자 중 하나는 객체가 컬렉션에 속하는지 확인하는 데 사용되는 `in` 연산자이다. 해당 함수를 `contains`라고 한다. `in` 연산자를 사용하여 점이 직사각형에 속하는지 여부를 확인할 수 있도록 구현해 보겠다.

```kotlin
data class Rectangle(val upperLeft: Point, val lowerRight: Point)

operator fun Rectangle.contains(p: Point): Boolean {
    return p.x in upperLeft.x..<lowerRight.x &&
           p.y in upperLeft.y..<lowerRight.y
}

fun main() {
    val rect = Rectangle(Point(10, 20), Point(50, 50))
    println(Point(20, 30) in rect)
    // true
    println(Point(5, 5) in rect)
    // false
}
```

![](https://velog.velcdn.com/images/cksgodl/post/aeca4700-299e-4a89-a0c2-3607f58f9d19/image.png)

### 9.3.3 객체에서 범위 만들기: To 및 Until 컨벤션

```kotlin
import java.time.LocalDate
fun main() {
    val now = LocalDate.now()
    val vacation = now..now.plusDays(10)
    println(now.plusWeeks(1) in vacation)
    // true
}
```

![](https://velog.velcdn.com/images/cksgodl/post/ace72131-85e7-4ff9-b935-d02cef6f1bdc/image.png)

`rangeTo` 연산자는 산술 연산자보다 우선 순위가 낮다. 그러나 인수를 괄호 로 묶어 혼동을 피하는 것이 좋다:

```kotlin
fun main() {
    val n = e
    println(0...(n +
    1))
    // 0..10
}
```

### 9.3.4 유형에 대한 반복: Iterator 컨벤션

`Kotlin`의 루프는 범위 검사와 동일한 연산자를 사용한다. 그러나 이 문맥에서는 반복을 수행하는 데 사용된다는 점에서 의미가 다르다. 즉, `for (x in list) { ... }`와 같은문은 `Java`에서와 마찬가지로 `hasNext` 및 `next` 메서드가 반복적으로 호출되는 `list.iterator()`의 호출로 변환된다.

```kotlin
operator fun CharSequence.iterator(): CharIterator
fun main() {
    for (c in "abc") { }
}
```

```kotlin
operator fun ClosedRange<LocalDate>.iterator(): Iterator<LocalDate> =
	object : Iterator<LocalDate> {
    	var current = start
    	override fun hasNext() = current <= endInclusive
	    override fun next(): LocalDate {
    	    val thisDate = current
        	current = current.plusDays(1)
        	return thisDate
	} 
}

fun main() {
    val newYear = LocalDate.ofYearDay(2042, 1)
    val daysOff = newYear.minusDays(1)..newYear
    for (dayOff in daysOff) { println(dayOff) }
    // 2041-12-31
    // 2042-01-01
}
```

## 9.4 컴포넌트 함수로 구조분해 선언하기

이 기능을 사용하면 하나의 복합 값을 언패킹하여 여러 개의 개별 로컬 변수를 초기화하는 데 사용할 수 있다.

```kotlin
fun main() {
    val p = Point(10, 20)
    val (x, y) = p
    println(x)
    // 10
    println(y)
    // 20
}
```

내부적으로 구조분해 선언은 다시 한 번 규칙의 원칙을 사용합니다. 디스트럭처링 선언에서 각 변수를 초기화하기 위해 `componentN`이라는 함수가 호출되며, 여기서 `N`은 선언에서 변수의 위치이다.

즉, 아래 그림에 표시된 것처럼 이전 예제가 변형된다.

![](https://velog.velcdn.com/images/cksgodl/post/981feb69-67b6-4dd1-8c2b-2137e7def738/image.png)

```kotlin
class Point(val x: Int, val y: Int) {
    operator fun component1() = x
    operator fun component2() = y
}
```

`data class`의 경우 모든 프로퍼티에 대해 `componentN`함수를 생성한다.

구조 해체 선언 구문을 사용하면 함수를 호출 한 후 값을 쉽게 언패킹하여 사용할 수 있다. 

```kotlin
data class NameComponents(val name: String,
                          val extension: String)
                          
fun splitFilename(fullName: String): NameComponents {
    val result = fullName.split('.', limit = 2)
    return NameComponents(result[0], result[1])
}

fun main() {
    val (name, ext) = splitFilename("example.kt")
    println(name)
    // example
    println(ext)
    // kt
}

// Better
fun splitFilename2(fullName: String): NameComponents {
    val (name, extension) = fullName.split('.', limit = 2)
    return NameComponents(name, extension)
}
```

물론 이러한 `componentN` 함수를 무한대로 정의할 수는 없고 임의의 수의 항목에 대해 작동한다. 표준 라이브러리에서는 이 구문을 사용하여 컨테이너의 처음 5개의 엘리먼트에 액세스할 수 있다.

함수에서 여러값을 반환하는 더 간단한 방법은 표준 라이브러리의 `Pair` 및 `Triple` 클래스를 사용하는 것이다. 이 경우 자체 클래스를 정의하는 것보다 코드가 덜 필요할 수 있지만, `Pair` 및 `Triple`은 반환되는 객체에 무엇이 포함되어 있는지 명확하지 않기 때문에 코드에서 중요한 표현력을 포기하게 된다.

### 9.4.1 선언 및 루프 분해하기

구조 파괴 선언은 함수의 최상위 문뿐만 아니라 변수를 선언할 수 있는 다른 위치(예 : 루프)에서도 작동한다. 이를 잘 활용하는 한 가지 예는 맵에서 항목을 열거하는 것이다.

```kotlin
fun printEntries(map: Map<String, String>) {
    for ((key, value) in map) {
        println("$key -> $value")
    }
}

fun main() {
    val map = mapOf("Oracle" to "Java", "JetBrains" to "Kotlin")
    printEntries(map)
    // Oracle -> Java
    // JetBrains -> Kotlin
}
```

맵또한 `componentN`함수를 지원한다.

```kotlin
for (map.entries의 항목) {
	val key = entry.component1()
	val value = entry.component2()
	// ...
}
```

### 9.4.2 문자를 사용하여 분해된 값 무시하기

많은 컴포넌트가 있는 객체를 디스트럭처링할 때 실제로 모든 컴포넌트가 필요하지 않을 수 있다. 

아래예제에서는 Person 클래스를 디스트럭처링하지만 실제로는 이름과 나이 필드만사용한다.

```kotlin
data class Person(
            val firstName: String,
            val lastName: String,
            val age: Int,
            val city: String,
)
        fun introducePerson(p: Person) {
            val (firstName, lastName, age, city) = p
            println("This is $firstName, aged $age.")
}
```

필요하지 않은 필드를 `_`로 바꾸고 분해하면 필요한 필드만 활용할 수 있다.

```kotlin
fun introducePerson(p: Person) {
    val (firstName, _, age) = p
	println("이것은 $firstName, 나이 $age입니다.")
}
```

> 
Kotlin의 구조 분해 선언 구현은 위치 기반이므로 구조 분해 작업의 결과는 전적으로 인수의 위치에 따라 달라진다. 
>
> `val (이름, 성, 나이, 도시) = p`
>
> 디스트럭처링의 결과가 할당되는 변수의 이름은 중요하지 않다. 하지만, 리팩토링 중에 데이터 클래스의 속성 순서를 변경하면 미묘한 문제가 발생할 수 있다.
이 동작은 구조 파괴 선언이 작은 컨테이너 클래스(예: 키-값 쌍 또는 인덱스-값 쌍) 또는 향 후 변경될 가능성이 거의 없는 클래스에만 사용하는 것이 가장 좋다는 것을 의미한다.


## 프로퍼티 접근자 로직 재사용: 위임된 속성

`Kotlin`에서 가장 독특하고 강력한 기능 중 하나인 위임 프로퍼티에 대해 한 가지 더 살펴보겠다. 이 기능을 사용하면 각 접근자에 로직을 복제하지 않고도 백킹 필드에 값을 저장하는 것보다 더 복잡한 방식으로 작동하는 속성을 쉽게 구현할 수 있다.

### 9.5.1 위임된 프로퍼티의 기본 구문 및 내부작동 방식

위임된 프로퍼티의 일반적인 구문은 다음과 같다.

```kotlin
class Foo {
	var p: Type by Delegate()
}
```

델게이트 프로퍼티를 정의하는 클래스의 내부에서 어떤 일이 일어나는지 살펴보겠다:

```kotlin
class Foo {
    private val delegate = Delegate()
    var p: Type
       set(value: Type) = delegate.setValue(/* ... */, value)
       get() = delegate.getValue(/* ... */)
}
```

```kotlin
class Delegate {
    operator fun getValue(/* ... */) { /* ... */ }
	operator fun setValue(/* ... */, value: Type) { /* ... */ }
	operator fun provideDelegate(/* ... */): Delegate { /* ... */ }
}

class Foo {
    var p: Type by Delegate()
}

fun main() {
    val foo = Foo()
    val oldValue = foo.p
    foo.p = newValue
}
```

`foo.p`를 일반 프로퍼티로 사용하지만, 내부적으로는 델리게이트 유형의 헬퍼 프로퍼티의 메서드가 호출된다. 

### 9.5.2 위임된 프로퍼티 사용: 지연 초기화 및 lazy()

지연 초기화는 개체를 처음 액세스할 때 필요에 따라 객체의 일부를 생성하는패턴이다. 이는 초기화 프로세스에 상당한 리소스가 소모되고 객체를 사용할 때 데이터가 항상 필요한 것은 아닌 경우에 유용하다.

```kotlin
class Person(val name: String) {
    private var _emails: List<Email>? = null
    val emails: List<Email>
       get() {
			if (_emails == null) {
    			_emails = loadEmails(this)
			}
			return _emails!!
        }
}

fun main() {
    val p = Person("Alice")
    p.emails
    // Load emails for Alice
    p.emails
}
```

여기서는 소위 백킹 프로퍼티 기법을 사용한다. 

값을 저장하는 `_emails`라는 프로퍼티가 하나있고 이에 대한 읽기 액세스권한을 제공하는 이메일이라는 프로퍼티가 또 하나 있다. 두 프로퍼티의 유형이 다르기 때문에 두 개의 프로퍼티를 사용해야 한다. 이메일은 널 가능하지만 이메일은 널이 아니다. 클래스에 동일한 개념을 나타내는 두 개의 속성이 있는 경우 비공개 속성에는 밑줄(`_emails`)이 붙고, 공개 속성에는 접두사(`_`)가 붙지 않는 간단한 규칙에 따라 이름을 지정한다.

`Kotlin`은 이것보다 더 나은 솔루션을 제공한다.

```kotlin
class Person(val name: String) {
    val emails by lazy { loadEmails(this) }
}
```

`lazy` 함수는 기본적으로 스레드 안전하며, 필요한 경우 추가 옵션을 지정하여 사용할 잠금을 지정하거나 멀티스레드 환경에서 클래스가 사용되지 않는 경우 동기화를 완전히 우회할 수 있다.

### 9.5.3 나만의 위임된 속성 구현하기

위임된 프로퍼티가 어떻게 구현되는지 알아보기 위해 객체의 프로퍼티가 변경될 때 리스너에게 알리는 작업을 예로 들어 보겠다.

이런 프로퍼티를 일반적으로 `observable`이라고 한다. 코틀린에서 이를 구현하는 방법을 알아보자.

```kotlin
fun interface Observer {
    fun onChange(name: String, oldValue: Any?, newValue: Any?)
}

open class Observable {
	val observers = mutableListOf<Observer>()
	
    fun notifyObservers(propName: String, oldValue: Any?, newValue: Any?) {
        for (obs in observers) {
            obs.onChange(propName, oldValue, newValue)
		} 
    }
}
```

아래의 Person 객체는 나이나 급여가 변경되면 관찰자에게 알린다.


```kotlin
class Person(val name: String, age: Int, salary: Int): Observable() {
    var age: Int = age
        set(newValue) {
	        val oldValue = field
    	    field = newValue
        	notifyObservers(
            	"age", oldValue, newValue
        	)
		}

	var salary: Int = salary
    	set(newValue) {
        	val oldValue = field
        	field = newValue
        	notifyObservers(
            	"salary", oldValue, newValue
        	)
    	)
}

fun main() {
    val p = Person("Seb", 28, 1000)
    p.observers += Observer { propName, oldValue, newValue ->
	println( """
        프로퍼티 $propName이 $oldValue에서 $newValue로 변경되었습니다!
		""".trimIndent()
	p.age = 29
	// 프로퍼티 age이 28에서 29로 변경되었습니다!
	p.salary = 1500
	// 프로퍼티 salary이 1000에서 1500로 변경되었습니다!
}
```

위의 코드의 세터에는 반복되는 코드가 꽤 많이 있다. 프로퍼티의 값을 저장하고 필요한 알림을 실행하는 클래스를 추출해 보겠다.

```kotlin
class ObservableProperty(
    val propName: String,
    var propValue: Int,
	val observable: Observable 
) {
    
    fun getValue(): Int = propValue
  
  	fun setValue(newValue: Int) {
        val oldValue = propValue
        propValue = newValue
        observable.notifyObservers(propName, oldValue, newValue)
	} 
}

class Person(val name: String, age: Int, salary: Int): Observable() {
    val _age = ObservableProperty("age", age, this)
    var age: Int
        get() = _age.getValue()
        set(newValue) {
            _age.setValue(newValue)
        }
    
    val _salary = ObservableProperty("salary", salary, this)
    var salary: Int
		get() = _salary.getValue()
		set(newValue) {
        	_salary.setValue(newValue)
		}
}
```

`Kotlin`에서는 위와같은 위임속성 기능을 이미 제공하고, 그 형식은 실질적으로 아래와 비슷하다.

```kotlin
import kotlin.reflect.KProperty
class ObservableProperty(var propValue: Int, val observable: Observable) {
  operator fun getValue(thisRef: Any?, prop: KProperty<*>): Int = propValue
  operator fun setValue(thisRef: Any?, prop: KProperty<*>, newValue: Int) {
      val oldValue = propValue
      propValue = newValue
      observable.notifyObservers(prop.name, oldValue, newValue)
	}
}
```

프로퍼티는 `KProperty` 타입의 객체로 표현된다. 12장에서 더 자세히 살펴보겠지만, 지금은 프로퍼티의 이름을 `KProperty.name`으로 액세스할 수 있다는 것만 알아두면 된다.

```kotlin
class Person(val name: String, age: Int, salary: Int) : observable() { 
	var age by observableProperty(age, this)
	var salary by observableProperty(salary, this)
}
```

코드가 엄청나게 짧아졌다. 이런 상황이 필요할 때 관찰 가능한 속성 로직을 직접 구현하는 대신 `Kotlin` 표준 라이브러리를 사용할 수 있다.

표준 라이브러리에는 이미 자체 관찰 가능한 속성 클래스가 포함되어 있다. 그러나 표준 라이브러리 클래스는 앞서 정의한 관찰 가능한 인터페이스에 대해 아무 것도 알지 못하므로 속성 값의 변경 사항을 보고하는 방법을 알려주는 람다를 전달해야 한다. 

```kotlin
import kotlin.properties.Delegates
class Person(val name: String, age: Int, salary: Int) : Observable() { private val onChange = { property: KProperty<*>, oldValue: Any?,  ̄ newValue: Any? ->
        notifyObservers(property.name, oldValue, newValue)
    }
    var age by Delegates.observable(age, onChange)
    var salary by Delegates.observable(salary, onChange)
}
```

### 9.5.4 위임된 프로퍼티는 사용자 지정 접근자를 사용하여 숨겨진 프로퍼티로 변환된다.

```kotlin
class C {
    var prop: Type by MyDelegate()
}
val c = C()
```

`MyDelegate`의 인스턴스는 다음과 같은 숨겨진 프로퍼티에 저장된다. `<delegate>`. 컴파일러는 프로퍼티를 표현하기 위해 `KProperty` 유형의 객체도 사용한다. 이 객체를 `<property>`라고 한다.

컴파일러는 다음 코드를 생성한다:

```kotlin
class C {
    private val <delegate> = MyDelegate()
	var prop: Type
		get() = <delegate>.getValue(this, <property>)
		set(value: Type) = <delegate>.setValue(this, <property>, value)
}
```

![](https://velog.velcdn.com/images/cksgodl/post/f877267f-0323-40b2-aff8-910fbca0a59c/image.png)

### 9.5.5 맵에 위임하여 동적 속성에 액세스하기

```kotlin
class Person {
    private val _attributes = mutableMapOf<String, String>()
    fun setAttribute(attrName: String, value: String) {
        _attributes[attrName] = value
	}
    
    var name: String
        get() = _attributes["name"]!!
        set(value) {
            _attributes["name"] = value
        }
}

fun main() {
    val p = Person()
    val data = mapOf("name" to "Seb", "company" to "JetBrains")
    for ((attrName, value) in data)
       p.setAttribute(attrName, value)
    println(p.name)
    // Seb
    p.name = "Sebastian"
    println(p.name)
    // Sebastian
}
```

### 9.5.6 실제 프레임워크에서 위임된 프로퍼티를 사용하는 방법

```kotlin
object Users : IdTable() {
    val name = varchar("name", length = 50).index()
    val age = integer("age")
}

class User(id: EntityID) : Entity(id) {
    var name: String by Users.name
    var age: Int by Users.age
}
```

프레임워크를 사용하면 프로퍼티에 액세스하면 `Entity` 클래스의 매핑에서 해당 값을 자동으로 검색하고 이를 수정하면 객체를 가져와서 필요할 때 데이터베이스에 저장할 수 있으므로 특히 편리하다. `Kotlin` 코드에 `user.age += 1`을 작성하면 데이터 베이스의 해당 엔티티가 자동으로 업데이트된다.

이제 이러한 API가 포함된 프레임워크가 어떻게 구현되는지 충분히 이해하셨을 것입니다. 각 엔티티 속성(이름, 나이)은 열 개체(Users.name, Users.age)를 델리게이트 로 사용하여 위임된 속성으로 구현된다:

## 요약

- `Kotlin`에서는 해당 이름을 가진 함수를 정의하여 표준 수학 연산중 일부를 오버로드할 수 있다. 자체 연산자를 정의할 수는 없지만 보다 표현력 있는 대안으로 접두사 함수를 사용할 수 있다.
- 비교연산자(==,!=,>,< 등)를 모든 객체에 사용할 수 있다. 비교 연산자는 `equals`과 비교 대상 메서드의 호출에 매핑된다.
- `get`, `set`, `contains`라는 이름의 함수를 연산자에 추가하여 클래스를 `Kotlin`컬렉션과 유사하게 만들 수 있다.
- 범위를 만들고 컬렉션과 배열을 반복하는 것도 규칙을 통해 작동한다.

