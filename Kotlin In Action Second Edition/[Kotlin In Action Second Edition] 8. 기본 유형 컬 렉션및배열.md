## 8.1 원시 및 기타 기본유형

### 8.1.1 정수, 부동 소수점 숫자, 문자, 부울을 기본 유형으로 표현하기

`Java`는 기본 유형과 참조 유형을 구분한다. 

- 기본 유형(예: int)의 변수는 해당 값을 직접 보유한다. 
- 참조 유형(예: String)의 변수는 객체가 포함된 메모리 위치에 대한 참조를 보유한다.

원시 타입의 값은 더 효율적으로 저장하고 전달할 수 있지만, 이러한 값에 대한 메서드 를 호출하거나 컬렉션에 저장할 수는 없다. 

Java는 객체가 필요할 때 상황에 따라 기본 유형을 캡슐화하는 특수 래퍼 유형(예: java.lang.Integer)을 제공한다. 따라서 정수 컬렉션을 정의하려면 `Collection<int>`를 작성할 수 없으며 대신 `Collection<Integer>`를 사용해야 한다.

Kotlin은 기본 유형과 래퍼 유형을 구분하지 않는다. 항상 `Int`를 사용한다.

```kotlin
val i: Int = 1
val list: List<Int> = listof(1, 2, 3)
```

```kotlin
fun showProgress(progress: Int) {
    val percent = progress.coerceIn(0, 100)
    println("We're $percent % done!")
}
fun main() {
    showProgress(146)
    // We're 100 % done!
}
```

기본 유형과 참조 유형이 동일하다면 `Kotlin`이 모든 숫자를 객체로 표현할까? 코틀린은 그렇게 하지 않는다.

런타임에 숫자 유형은 컴파일러에 의해 가능한 가장 효율적인 방식으로 표현된다. 대부분의 경우(변수, 속성, 매개 변수 및 반환 유형의 경우) `Kotlin`의 `Int` 유형은 `Java` 기본 유형인 `int` 로 컴파일된다. 이것이 가능하지 않은 유일한 경우는 컬렉션과 같은 제네릭 클래스일 경우이다. 

Java 기본 유형에 해당하는 전체 유형 목록은 다음과 같다:
- 정수유형 - 바이트,숏,인트,롱
- 부동 소수점 숫자 유형 - 플로트 및 더블 
- 문자유형 - 문자
- 부울 유형 - Bool

### 8.1.2 전체 비트 범위를 사용하여 양수를 표현: Unsigned number 타입

비트 및 바이트 수준에서 작업하거나 비트맵의 픽셀, 파일의 바이트 또는 기타 이진 데이터를 조작하는 경우와 같이 양수 값을 나타내는 정수의 전체 비트 범위를 활용 해야 하는 상황이 가끔 있다. 

이러한 상황에서 `Kotlin`은 Java 가상 머신(JVM)의 일반 기본 유형을 `Unsigned` 정수에 대한 유형으로 확장한다.
![](https://velog.velcdn.com/images/cksgodl/post/ec6f1a3c-7b72-49ab-bfe7-0cd0cf35153e/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/e5da2c97-47b7-43bd-beac-b1610be0d2d5/image.png)

다른 기본 유형과 마찬가지로 Kotlin의 부호 없는 숫자는 필요한 경우에만 래핑된다.

### 8.1.3 널 가능 원시 타입: Int?, Boolean? 등

`Java` 참조 유형의 변수에만 널을 저장할 수 있기 때문에 `Kotlin`의 널 가능 유형은 Java 기본 유형으로 표현할 수 없다. 즉, `Kotlin`에서 기본 유형의 널러블 버전을 사용할 때 마다 해당 유형은 해당 랩퍼 유형으로 컴파일된다.

```kotlin
data class Person(val name: String,
                  val age: Int? = null) {
    fun isOlderThan(other: Person): Boolean? {
        if (age == null || other.age == null)
            return null
        return age > other.age
	} 
}

fun main() {
	println(Person("Sam", 35).isOlderThan(Person("Amy", 42)))
    // false
    println(Person("Sam", 35).isOlderThan(Person("Jane")))
    // null
}
```

`Person`클래스에서 선언된 나이 속성값은 `java.lang.Integer`로 저장된다.

기본 유형을 클래스의 유형 인수로 사용하는 경우 `Kotlin`은 해당 유형의 박스형 표현을 사용한다. 예를들어, 아래처럼 하면 널가능유형을 지정하거나 널값을 사용한적이 없더라도 박스형 정수값의 리스트가 생성된다:
```kotlin
val listofInts = listof(1, 2, 3)
```

### 8.1.4 숫자 변환을 명시적으로 만드는 Kotlin

`Kotlin`과 `Java`의 중요한 차이점 중 하나는 숫자 변환을 처리하는 방식이다. 값을 할당 하려는 유형이 더 크고 할당하려는 값을 편안하게 담을 수 있는 경우에도 `Kotlin`은 한 유형에서 다른 유형으로 숫자를 자동으로 변환하지 않는다.

```kotlin
val i = 1
val l: Long = i // ERROR

val i = 1
val l: Long = i.toLong()
```

코틀린에서 변환 함수는 모든 기본 유형(부울 제외)에 대해 정의되어 있다: `toByte(), toShort(), toChar()` 등. 이 함수는 `Int.toLong()`과 같이 작은 타입을 큰 타입으로 확장하거나 `Long.toInt()`와 같이 큰 타입을 작은 타입으로 자르는 등 양방향 변환을 지원한다.

코틀린에선 암시적 변환을 제공하지 않는다.

```kotlin
val x = 1
val list = listof(1L, 2L, 3L)
x in list // False
```

동일한 유형의 값만 비교됨으로 유형을 명시적으로 변환해야 한다:

```kotlin
fun main() {
    val x = 1
	println(x.toLong() in listof(1L, 2L, 3L))
	// true
}
```

또한 `Kotlin`은 추가 오버플로 검사를 도입하지 않는다 (Java와 동일):

```kotlin
fun main() { 
	println(Int.MAX_VALUE + 1) 
    // -2147483648 
    println(Int.MIN_VALUE - 1) 
    // 2147483647
}
```

### 8.1.5 Any 및 Any? Kotlin 유형 계층 구조의 루트

`Java`에서 `Object`가 클래스 계층 구조의 루트인 것과 유사하게, `Any` 유형은 `Kotlin`에서 모든 `null` 가능하지 않은 유형의 루트이다. 

```kotlin
val answer: Any = 42 // Any가 참조형임으로 박스형이다.
```

내부적으로 `Any` 유형은 `java.lang.object`에 해당한다. `Java` 메서드의 매개변수 및 반환 유형에 사용되는 객체 유형은 `Kotlin`에서 `Any`로 표시된다. (보다 구체적으로, 이 유형은 null 가능성을 알 수 없기 때문에 플랫폼 유형)

### 8.1.6 Unit 타입: Kotlin의 void

`Kotlin`의 `Unit` 유형은 `Java`의 `void`와 동일한 기능을 수행한다. 반환할 것이 없는 함수의 반환 유형으로 사용할 수 있다 (타입 선언 없으면 Unit을 반환하는 것과 동일)

```kotlin
fun f() { /* ... */ }
```

`Kotlin`의 `Unit`이 `Java`의 `void`와 다른 점은 무엇일까? `Unit`은 `full-fledged` 유형으로, `void`와 달리 인수로 사용할 수 있다. 이 유형의 값은 하나만 존재하며 Unit이라고도 하며 암시적으로 반환될 수 있다.

```kotlin
interface Processor<T> {
    fun process(): T
}

class NoResultProcessor : Processor<Unit> {
    override fun process() {
		// do stuff
	}
}
```

### 8.1.7 Nothing 유형: "이 함수는 절대 반환되지 않는다"

`Kotlin`의 일부 함수의 경우 성공적으로 완료되지 않기 때문에 "반환 값"이라는 개념이 의미가 없다. 이럴 때 `Kotlin`에서는 특수 반환 유형인 `Nothing`호출한다.

```kotlin
fun fail(message: String): Nothing {
    throw IllegalStateException(message)
}
fun main() { 
	fail("오류 발생")
}
// java.lang.IllegalStateException: 오류가 발생했습니다.
```

`Nothing` 유형은 값이 없으므로 함수 반환 유형으로 사용하거나 일반 함수 반환 유형으로 사용되는 유형 매개변수의 유형 인수로만 사용하는 것이 합리적이다. 그 외의 모든 경우에는 값을 저장할 수 없는 변수를 선언하는 것은 의미가 없다.

아무것도 반환하지 않는 함수는 엘비스 연산자의 오른쪽에서 전제 조건 검사를 수행하는 데 사용할 수 있다:

```kotlin
val address = company.address ?: fail("주소 없음") println(address.city)
```

## 8.2 컬렉션 및 배열

### 8.2.1 nullable값 및 nullable 컬렉션의 컬렉션

```kotlin
fun readNumbers(text: String): List<Int?> {
    val result = mutableListOf<Int?>()
    for (line in text.lineSequence()) {
        val numberOrNull = line.toIntOrNull()
        result.add(numberOrNull)
    }
    return result
}
```

`List<Int?>`는 `Int?` 타입의 값, 즉 `Int` 또는 `null`을 담을 수 있는 목록이다. 줄을 파싱할 수 있는 경우 결과 목록에 정수를 추가하고 그렇지 않은 경우 `null`을 추가한다.

아래 그림을 참고하라.

![](https://velog.velcdn.com/images/cksgodl/post/940b4cbd-ff69-4ea1-b8c2-923942cc5f69/image.png)

함수형 프로그래밍과 람다에 대한 지식이 있다면 이를 다음과 같이 리팩토링할 수 있다.

```kotlin
fun readNumbers2(text: String): List<Int?> =
    text.lineSequence().map { it.toIntorNull() }.toList()
```

목록의 개별 요소가 없을 수도 있지만 목록 전체가 없을 수도 있음을 표현할 수 있다. 이를 작성하는 Kotlin 방 식은 두 개의 물음표가 있는 `List<Int?>?` 이다.

![](https://velog.velcdn.com/images/cksgodl/post/8fe791b9-892d-4363-87f8-4fd321ae2e46/image.png)

```kotlin
fun addValidNumbers(numbers: List<Int?>) {
    var sumOfValidNumbers = 0
    var invalidNumbers = 0
    for (number in numbers) {
        if (number != null) {
            sumOfValidNumbers += number
        } else {
            invalidNumbers++
		} 
	}
    println("Sum of valid numbers: $sumOfValidNumbers")
    println("Invalid numbers: $invalidNumbers")
}

fun main() {
    val input = """
		1 abc 42
    """.trimIndent()
    val numbers = readNumbers(input)
    addValidNumbers(numbers)
    // Sum of valid numbers: 43
    // Invalid numbers: 1
}
```

`null` 가능한 값의 컬렉션을 가져와서 `null`을 필터링하는 것은 매우 일반적인 작업임으로, `Kotlin`에서는 이를 수행할 수 있는 표준 라이브러리함수 `filterNotNull`을 제공한다. 

```kotlin
fun addValidNumbers(numbers: List<Int?>) {
    val validNumbers = numbers.filterNotNull()
    println("Sum of valid numbers: ${validNumbers.sum()}")
    println("Invalid numbers: ${numbers.size - validNumbers.size}")
}
```

![](https://velog.velcdn.com/images/cksgodl/post/06c57294-993b-4f66-aabd-f985a60a0465/image.png)

### 8.2.2 읽기 전용 및 변경 가능한 컬렉션

`Kotlin`의 컬렉션 디자인이 `Java`와 다른 중요한 특징은 컬렉션의 데이터에 액세스하고 데이터를 수정하기 위한 인터페이스를 분리한다는 점이다. 

이러한 구분은 컬렉션 작업 을 위한 가장 기본적인 인터페이스인 `kotlin.collections.Collection`부터 시작된다. 요소의 크기를 구하고, 특정 요소가 포함되어 있는지 확인하고, 컬렉션에서 데이터를 읽는 기타 작업을 수행할 수 있다. 하지만 이 인터페이스에는 요소를 추가하 거나 제거하는 메서드가 없다.

컬렉션의 데이터를 수정하려면 `kotlin.collections.MutableCollection` 인터페이스를 사용해야 한다. 이 인터페이스는 일반 `kotlin.collections.Collection`을 확장하며 요소 추가 및 제거, 컬렉션 지우기 등의 메서드를 제공한다.

![](https://velog.velcdn.com/images/cksgodl/post/f4994268-4639-4163-bd4f-3d8646508dba/image.png)

아래는 콜렉션의 방어적 복사의 예이다.

```kotlin
fun <T> copyElements(source: Collection<T>,
                     target: MutableCollection<T>) {
    for (item in source) {
        target.add(item)
	} 
}

fun main() {
    val source: Collection<Int> = arrayListOf(3, 5, 7)
    val target: MutableCollection<Int> = arrayListOf(1)
    copyElements(source, target)
    println(target)
    // [1, 3, 5, 7]
}
```

컬렉션 인터페이스로 작업할 때 명심해야 할 핵심 아이디어는 읽기 전용 컬렉션이 반드시 변경 불가능하지는 않다는 것이다. 읽기 전용 인터페이스 유형을 가진 변수로 작업하는 경우, 이는 동일한 컬렉션에 대한 많은 참조 중 하나에 불과할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/d3e48d62-7b8a-4494-bf96-634b467f13cb/image.png)

> 읽기 전용 컬렉션은 스레드세이프하지 않다.

코드의 한 부분이 변경 가능한 컬렉션에 대한 참조를 보유하는 경우, 같은 컬렉션에 대한 읽기 전용 '보기'를 보유하는 코드의 다른 부분은 컬렉션이 첫 번째 부분에 의해 동시에 수정될 수 있다.

코드가 작업하는 동안 컬렉션이 수정되면 `ConcurrentModificationException` 오류 및 기타 문제가 발생할 수 있다.


### 8.2.3 Kotlin 컬렉션과 Java 컬렉션은 깊은 관련이 있다.

모든 `Kotlin` 컬렉션은 해당 `Java` 컬렉션 인터페이스의 인스턴스이다. `Kotlin`과 `Java` 간에 이동할 때 변환이 필요하지 않으므로 래퍼를 사용하거나 데이터를 복사할 필요가 없다. 

하지만 모든 `Java` 컬렉션 인터페이스에는 `Kotlin`에서 읽기 전용 인터페이스와 변경 가능한 인터페이스의 두 가지 표현이 있다.

![](https://velog.velcdn.com/images/cksgodl/post/7ea1dc90-ae9f-47a5-836e-b7b5ad100b8e/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/cd9fd57a-5312-4ad7-bb88-930c4e7df838/image.png)

`Java`는 읽기 전용 컬렉션과 변경 가능한 컬렉션을 구분하지 않기 때문에 `Kotlin` 측에서 읽기 전용 컬렉션으로 선언된 경우에도 `Java` 코드가 컬렉션을 변경할 수 있다. 

`Kotlin` 컴파일러는 Java 코드에서 컬렉션에 대해 수행되는 작업을 완전히 분석할 수 없으므로 읽기 전용 컬렉션을 수정하는 `Java` 코드에 전달되는 호출을 거부할 방법이 없다.

```kotlin
/* Java */
// CollectionUtils.java
public class CollectionUtils {
    public static List<String> uppercaseAll(List<String> items) {
        for (int i = 0; i < items.size(); i++) {
            items.set(i, items.get(i).toUpperCase());
        }
        return items;
    }
}

// Kotlin
// collections.kt
fun printInUppercase(list: List<String>) {
	println(CollectionUtils.uppercaseAll(list))
	println(list.first())
}
fun main() {
	val list = listOf("a", "b", "c")
	printInUppercase(list)
	// [A, B, C]
	// A
}
```

따라서 컬렉션을 가져와 `Java`로 전달하는 `Kotlin` 함수를 작성하는 경우 호출하는 `Java` 코드가 컬렉션을 수정할지 여부에 따라 매개변수에 올바른 유형을 사용하는 것은 사용자의 책임이다.

### 8.2.4 Java로 선언된 컬렉션은 Kotlin에서 플랫폼 타입으로 간주된다.

코틀린에서 자바의 코드를 활용하고자 한다면 자바 인터페이스 또는 클래스가 따라야 하는 정확한 계약을 알고 있어야 한다. 이는 일반적으로 구현이 수행해야 하는 작업을 기반으로 쉽게 이해할 수 있다.

### 8.2.5 객체 및 원시타입 배열 만들 때 상호 운용성 및 성능상의 이유 생각하기.

배열이 어떻게 생성되는짖 다시 한번 살펴보겠다.

```kotlin
fun main(args: Array<String>) {
    for (i in args.indices) {
         println("Argument $i is: ${args[i]}")
    }
}
```

Kotlin에서 배열을 만들려면 다음과 같은 방법이 있다:
- `arrayOf` 함수는 이 함수의 인수로 지정된 요소를 포함하는 배열을 생성한다.
- `arrayOfNulls` 함수는 널 엘리먼트를 포함하는 지정된 크기의 배열을 생성한다.
- 배열 생성자는 배열의 크기와 람다를 취하고 람다를 호출하여 각 배열요소를 초기화한다. 
   - 이렇게 하면 각 요소를 명시적으로 전달하지 않고도 null이 아닌 요 소 유형으로 배열을 초기화할 수 있다.

```kotlin
fun main() {
    val letters = Array<String>(26) { i -> ('a' + i).toString() }
    println(letters.joinToString(""))
    // abcdefghijklmnopqrstuvwxyz
}
```

```kotlin
fun main() {
	val strings = listof("a", "b", "c") println("%s/%s/%s".format(*strings.toTypedArray())) // a/b/c
}
```

아래 예제 표시된 것처럼 `Kotlin` 코드에서 배열을 만드는 가장 일반적인 경우 중 하나는 배열을 취하는 `Java` 메서드나 `vararg` 매개 변수가 있는 `Kotlin` 함수를 호출 해야 할 때이다.

이러한 상황에서는 데이터가 이미 컬렉션에 저장되어 있는 경우가 많으므로 이를 배열로 변환하기만 하면 된다. 이 작업은 `toTypedArray` 메서드를 사용하여 수행할 수 있다.


다른 타입과 마찬가지로 배열 타입의 타입 인자는 항상 객체 타입이 된다. 따라서 `Array<Int>`와 같은 것을 선언하면 박스형 정수의 배열이 된다(`Java` 유형은 `java.lang.Integer[]`). 박싱 없이 기본 유형의 값 배열을 생성해야 하는 경우 기본 유형의 배열을 위한 특수 클래스 중 하나를 사용해야 한다.

기본 유형의 배열을 표현하기 위해 `Kotlin`은 각 기본 유형에 대해 하나씩 여러 개의 별도 클래스를 제공한다. 예를 들어 `Int` 유형의 값 배열은 `IntArray`라고 한다.

다른 유형의 경우 `Kotlin`은 `ByteArray`, `CharArray`, `BooleanArray` 등을 제공한다. 이러한 모든유형은 `int[]`, `byte[]`, `char[]` 등과 같은 일반 `Java`기본 유형배열로 컴파일된다. 

```kotlin
val fiveZeros = IntArray(5)
val fiveZerosToo = intArrayof(0, 0, 0, 0, 0, 0)


fun main() {
	val squares = IntArray(5) { i -> (i+1) * (i+1) } 	
	println(squares.joinToString())
	// 1, 4, e, 16, 25
}
```

## 요약
- 기본 숫자(예: Int)를 나타내는 유형은 일반 클래스처럼 보이고 작동하지만 일반 적으로 `Java` 기본 유형으로 컴파일된. Kotlin의 서명되지 않은 숫자 클래스는 `JVM`에 정확히 대응하는 클래스가 없지만 인라인 클래스를 통해 기본 유형처럼 동작하고 수행하도록 변환된.
- `nullable`한 기본 유형(예: `Int?`)은 `Java`의 박스형 기본 유형(예: `java.lang.Integer`)으로 치환된다.
- `Any` 타입은 다른 모든 타입의 상위 타입이며 `Java`의 `Object`와 유사하다. `Unit`은 `void`와 유사하다.
- `Nothing` 유형은 정상적으로 종료되지 않는 함수의 반환 유형으로 사용된다.
- `Java`에서 오는 타입은 `Kotlin`에서 플랫폼 유형으로 해석되므로 개발자는 이를 널 가능 또는 널이 아닌 것으로 취급할 수 있다.
- `Kotlin`은 컬렉션에 표준 `Java` 클래스를 사용하며 읽기 전용 컬렉션과 변경 가능한 컬렉션을 구분하여 컬렉션을 개선한다.
- `Kotlin`에서 `Java` 클래스를 확장하거나 `Java` 인터페이스를 구현할 때는 매개 변수의 널 가능성 및 변경 가능성을 신중하게 고려해야 한다.
- `Kotlin`에서 배열을 사용할 수 있지만 일반적으로 기본적으로 컬렉션을 사용하는 것이 좋다.
- `Kotlin`의 `Array` 클래스는 일반 제네릭 클래스처럼 보이지만 `Java` 배열로 컴파일된다.
- 원시 타입의 배열은 `IntArray`와 같은 특수 클래스로 표현된다.