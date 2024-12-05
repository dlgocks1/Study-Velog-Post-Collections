이번장에서 배우는 것

- 컬렉션, 문자열 및 정규식 작업 함수 작성
- 명명된 인수, 기본 매개 변수 값 및 접두사 호출 구문 사용
- 확장 함수 및 속성을 통해 Java 라이브러리를 Kotlin 에 적용하기
- 최상위 및 로컬 함수 및 프로퍼티로 코드 구조화하기

## 3.1 Kotlin에서 컬렉션 만들기

아래 예제처럼 컬렉션을 만들 수 있다.

```kotlin
val set = setOf(1, 7, 53)
val list = listOf(1, 7, 53)
val map = mapOf(1 to "1", 7 to "7", 53 to "53")

println(set.javaClass)
// 클래스 java.util.LinkedHashSet
println(list.javaClass)
// 클래스 java.util.Arrays$ArrayList
println(map.javaClass)
// 클래스 java.util.LinkedHashMap
```

이러한 `setOf`, `listOf`, `mapOf`등의 함수는 코틀린에서 선언한 일반 함수이다. (컬렉션 클래스의 멤버 함수가 아님) 이는 추후 설명한다.

`Kotlin`은 표준 `Java` 컬렉션 클래스를 사용한다. 즉, `Kotlin`은 컬렉션 클래스를 다시 구현하지 않는다. `Java` 컬렉션에 대한 기존의 모든 지식이 여기에도 그대로 적용된다. 하지만 `Java`와 달리 `Kotlin`의 컬렉션 인터페이스는 기본적으로 읽기 전용이라는 점에 주목할 필요가 있다.

표준 `Java` 컬렉션을 사용하면 `Java` 코드와 훨씬 쉽게 상호 작용할 수 있다. `Kotlin`에서 `Java` 함수를 호출하거나 그 반대로 호출할 때 컬렉션을 어느 한 쪽 또는 다른 쪽으로 변환할 필요가 없기 때문이다.

```kotlin
fun main() {
	val strings = listof("first", "second", "14th")
	strings.last() // 열네 번째
	println(strings.shuffled()) // [열네 번째, 두 번째, 첫 번째]
	val numbers = setof(1, 14, 2) println(numbers.sum())// 17
}
```

`Kotlin`의 기본 컬렉션은 `Java` 컬렉션과 완전히 동일한 클래스이지만 `Kotlin`에서는 컬렉션으로 훨씬 더 많은 작업을 수행할 수 있다. (예를 들어 목록에서 마지막 요소를 가져오거나, 목록의 셔플 버전을 가져오거나, 컬렉션을 합산할 수 있다(숫자 컬렉션 인 경우))

## 3.2 함수를 더 쉽게 호출하기

코틀린에서는 이미 선언된 클래스라도 추가 확장 함수를 통해 더 쉽게 기능을 추가할 수 있다.

```kotlin
public fun <T> Iterable<T>.joinToString(separator: CharSequence = ", ", prefix: CharSequence = "", postfix: CharSequence = "", limit: Int = -1, truncated: CharSequence = "...", transform: ((T) -> CharSequence)? = null): String {
    return joinTo(StringBuilder(), separator, prefix, postfix, limit, truncated, transform).toString()
}
```

### 3.2.1 named argument


```kotlin
joinToString(collection, " ", " ", ".")
```

`joinToString`을 사용할 때 위처럼 사용하면 시그니쳐에 대해 함수안을 들여다 봐야 할 수 있다. 코틀린은 이에따라 `named parameter`기능을 제공한다.

```kotlin
  val excluded = exclude.get().takeIf(List<*>::isNotEmpty)
            ?.joinToString(separator = ",", prefix = "[", postfix = "]") ?: "undefined"
```

### 3.2.2 default argument

```kotlin
fun joinToString(
	separator: CharSequence = "", 
    prefix: CharSequence = "", 
    postfix: CharSequence = "", 
    limit: Int = -1, 
    truncated: CharSequence = "...", 
    transform: ((T) -> CharSequence)? = null):
```

일반 호출 구문을 사용할 때는 함수 선언에서와 같은 순서로 인수를 지정해야 하며, 후행 인수만 생략할 수 있다. `named arguemnt`를 사용하는 경우 매개변수 목록의 중 간에서 일부 인수를 생략하고 필요한 인수만 원하는 순서대로 지정할 수 있다.

> 기본값 및 Java
>
> Java에는 기본 매개 변수 값의 개념이 없으므로 Kotlin에서 Java 함수를 호출할 때는 모든 매개 변수 값을 명시적으로 지정해야 한다. Java에서 함수를 자주 호출해야 하고 Java 호출자가 더 쉽게 사용할 수 있도록 하려면 `@Jvmoverloads` 로 함수에 주석을 달면 된다. 이렇게 하면 컴파일러가 마지막 매개변수부터 하나씩 생략 하여 `Java` 오버로드된 메서드를 생성하도록 지시한다. 

예시로는 다음과 같이 구현된다.

```kotlin
@Jvmoverloads
fun <T> joinToString(
	collection: Collection<T>, 
    seperator: String = ""
	prefix: String = "", 
    postfix: String = "" 
): String { /* ... */ }
```

```java
/* 자바 */
String joinToString(Collection<T> collection, String seperator, String prefix,
String postfix);
String joinToString(Collection<T> collection, String seperator, String prefix); String joinToString(Collection<T> collection, String separator); String joinToString(Collection<T> collection);
```

이는 인자의 개수만큼 오버헤드가 발생한다는 것을 잊지말자.

### 3.2.3 정적 유틸리티 클래스 제거하기: 최상위 함수 및 프로퍼티

객체 지향 언어인 `Java`는 모든 코드를 클래스의 메서드로 작성해야 한다.  일반적으로는 잘 작동하지만 실제로는 거의 모든 대규모 프로젝트 에는 단일 클래스에 명확하게 속하지 않는 코드가 많이 포함되어 있다. (공통 로직을 포함하는 클래스)

결과적으로 상태나 인스턴스 메서드를 포함하지 않는 클래스를 만들게 된다. 이러한 클래스는 몇 가지 정적 메서드의 컨테이너 역할만 하게된다. `Util`이 포함된 클래스 대부분이 그렇다.

`Kotlin`에서는 의미 없는 클래스를 모두 만들 필요가 없다. 대신 클래스 외부의 소스 파일 최상위 레벨에 함수를 직접 배치할 수 있다. 이러한 함수는 여전히 파일 최상위에 선언된 패키지의 멤버이며 다른 패키지에서 호출하려는 경우 여전히 임포트해야 하지만 불필요한 추가 중첩 수준은 더 이상 존재하지 않는다.

```kotlin
package strings

fun joinToString( /* ... */ ): String { /* ... */ }
```

`Kotlin` 컴파일러에서 생성된 클래스 이름은 `Java`의 패키지 체계와 일치하도록 변경된다. 함수가 포함된 파일 이름에 대문자로 표시되고 `Kt`가 접미사로 붙는 것을 볼 수 있다. 파일의 모든 최상위 함수는 해당 클래스의 정적 메서드로 컴파일된다. 따라서 `Java`에서 이 함수를 호출하는 것은 다른 정적 메서드를 호출하는 것과 동일하다.

```kotlin
JoinKt.joinToString(list, ", ", "", "");
```

### 3.2.3 최상위 프로퍼티

```kotlin
var opCount = 0 // 최상위 프로퍼티

fun performoperation() { 
	opCount++
	// ...
}
```

이러한 프로퍼티의 값은 정적 필드에 저장된다. 최상위 프로퍼티를 사용하면 코드에서 상수를 정의할 수도 있다

```kotlin
val UNIX_LINE_SEPARAToR = "\n"
```

기본적으로 최상위 프로퍼티는 다른 프로퍼티와 마찬가지로 `Java` 코드에 접근자 메서드 (`val` 프로퍼티의 경우 게터, `var` 프로퍼티의 경우 게터-세터 쌍)로 노출된다. 상수를 `Java` 코드에 공용 정적 최종 필드로 노출하여 보다 자연스럽게 사용하려면 `const`를 사용하여 표시하면 된다

```kotlin
const val UNIX_LINE_SEPARAToR = "\n"
```
이렇게 하면 다음 Java 코드와 동일한 결과를 얻을 수 있다.

```java
publie static final String UNIX_LINE_SEPARAToR = "\n";
```

### 3.3 다른 사람의 클래스에 메서드 추가하기: 확장 함수 및 프로퍼티

`Kotlin`의 주요 테마 중 하나는 기존 `java` 코드와의 원활한 통합이다. 순수 `Kotlin` 프로젝트도 `JDK`, `Android` 프레임워크 및 기타 타사 프레임워크와 같은 Java 라이브러리 위에 빌드된다. 

또한 `Kotlin`을 `Java` 프로젝트에 통합할 때 `Kotlin`으로 변환되지 않았거나 변환되지 않을 기존 코드도 처리하게 된다. 이러한 `API`로 작업할 때 다시 작성할 필요없이 `Kotlin`의 모든 장점을 사용할 수 있다면 좋지 않을까? 이것이 바로 확장 기능을 통해 가능해진다.

> 개념적으로 __확장 함수__는 클래스의 멤버로 호출할 수 있지만 클래스 외부에서 정의 되는 함수이다.

```kotlin
package string

fun String.lastChar(): Char = this.get(this.length - 1)
```

추가하려는 함수 이름 앞에 확장하려는 클래스 또는 인터페이스의 이름을 넣기만 하면 된다. 이 클래스 이름을 수신자 유형이라고 하고, 확장 함수를 호출하는 값을 수신자 객체라고 한다.

이는 아래 그림을 참고하자.

![](https://velog.velcdn.com/images/cksgodl/post/ca812a99-c731-471c-b5de-88aa1adba3f8/image.png)

일반 클래스 멤버에 사용하는 것과 동일한 구문을 사용하여 함수를 호출할 수 있다.

```kotlin
fun main() { 
	println("Kotlin".lastChar()) // n
}
// 이 예제에서 String은 수신자 유형이고 "Kotlin"은 수신자 개체
```

어떤 의미에서 여러분은 `String` 클래스에 자신만의 메서드를 추가한 것이다. `String`이 내 코드의 일부가 아니며 해당 클래스의 소스 코드가 없더라도 프로젝트에 필요한 메서드를 사용하여 확장할 수 있다. 

`String`이 `Java`로 작성되었는지, `Kotlin`으로 작성되었는지, `Groovy`와 같은 다른 `JVM` 언어로 작성되었는지, 심지어 최종적으로 표시 되어 서브클래싱을 방지하는지 여부도 중요하지 않다. `Java` 클래스로 컴파일되기만 하면 해당 클래스에 자신만의 확장을 추가할 수 있다.

```kotlin
fun String.lastChar(): Char = get(length - 1)
// 확장 함수에서는 클래스 자체에 정의된 메서드에서와 마찬가지로 확장하는 클래스 의 메서드와 프로퍼티에 직접 액세스할 수 있다.
```

확장 함수는 캡슐화를 해제할 수 없다는 점에 유의하라. 클래스에 정의된 메서드와 달리 확장 함수는 클래스의 비공개 또는 보호된 멤버에 액세스할 수 없다.

호출 사이트에서 확장 함수는 멤버와 구분할 수 없으며, 특정 메서드가 멤버인지 확장 함수인지는 중요 하지 않은 경우가 많다.

### 3.3.1 가져오기 및 확장기능

확장 함수를 정의하면 전체 프로젝트에서 자동으로 사용할 수 있게 되는 것은 아니다. 대신 다른 클래스나 함수와 마찬가지로 임포트해야 한다. 

```kotlin
import strings.lastChar
val c = "Kotlin".lastChar()
```

`as`를 사용하여 임포트하는 클래스 또는 함수의 이름을 변경할 수 있다. 

```kotlin
import strings.lastChar as last
val c = "Kotlin".last()
```

### 3.3.2 Java에서 확장 함수 호출하기

내부적으로 확장 함수는 수신자 객체를 첫 번째 인수로 받아들이는 정적 메서드이다. 이 함수를 호출할 때 어댑터 객체나 기타 런타임 오버헤드를 생성하지 않는다.

정적 메서드를 호출하고 수신자 객체 인스턴스를 전달하면 `Java`에서 확장 함수를 매우 쉽게 사용할 수 있다. 다른 최상위 함수와 마찬가지로 메서드가 포함된 `Java` 클래스의 이름은 함수가 선언된 파일 이름에서 결정된다. 

예를들어 이 함수가 `StringUtil.kt` 파일에서 선언되었다고 가정해 보자.

```kotlin
// Java
String c = StringUtilKt.lastChar("Java");
```

이 확장 함수는 최상위 함수로 선언되어 있으므로 정적 메서드로 컴파일된다.

### 3.3.4 확장 함수에 대한 재정의 불가능

`Kotlin`의 메서드 재정의는 멤버 함수에 대해서는 평소와 같이 작동하지만 확장 함수에 대해서는 재정의할 수 없다. `View`와 `Button`이라는 두개의 클래스가 있다고 가정해 보자. 

`Button`은 `View`의 하위 클래스이며 슈퍼클래스의 클릭 함수를 재정의한다. 이를 구현하려면 `View`와 클릭을 재정의할 수 있도록 개방 수정자 `open`으로 표시하고 재정의 수정자를 사용하여 서브클래스에 구현을 제공해야한다.

```kotlin
open class View {
    open fun click() = println("View clicked")
}

class Button: View() {
    override fun click() = println("Button clicked")
}
```

`View` 타입의 변수를 선언하는 경우 `Button`은 `View`의 하위 유형이므로 해당 변수에 `Button` 타입의 값을 저장할 수 있다. 이 변수에서 클릭과 같은 일반 메서드를 호출 하고 해당 메서드가 Button 클래스에서 재정의된 경우 Button 클래스에서 재정의된 구현이 사용된다.

```kotlin
fun main() {
	val view: View = Button() 
	view.click() // Button clicked
}
```

하지만 확장 함수에서는 위와 같은 방식으로 작동하지 않는다. 확장 함수는 아래와 같이 클래스의 일부가 아니라 외부에서 선언된다.

![](https://velog.velcdn.com/images/cksgodl/post/3397f938-53ab-4e60-b936-65c5789d11d4/image.png)
-  view.xhowoff() 및 button.xhowoff() 확장함수는 뷰 및 버튼 클래스 외부에 정의되어 있다.

기본 클래스와 그 하위 클래스에 대해 동일한 이름과 매개 변수 유형을 가진 확장 함수를 정의할 수 있지만 호출되는 함수는 런타임이 아니라 컴파일 시점에 결정된다. 

> 다음 예제는 `View` 및 `Button` 클래스에 선언된 두 개의 `showoff `확장 함수를 보여 준다. `View` 유형의 변수에 대해 `showoff`를 호출하면 값의 실제 유형이 `Button`이더라도 연관된 확장함수가 호출된다.

```kotlin
fun View.showOff() = println("I'm a view!")
fun Button.showOff() = println("I'm a button!")

fun main() {
	val view: View = Button()
	view.showOff() // I'm a view!
}
```

확장 함수는 `Java`에서 수신자를 첫 번째 인수로 사용하여 정적 함수로 컴파일된다는 점을 기억하면 도움이 될 것이다.

```java
/* Java */
class Demo {
    public static void main(String[] args) {
        View view = new Button();
        ExtensionsKt.showOff(view);
        // I'm a view!
	}
}
```

보시다시피 재정의는 확장 함수에는 적용되지 않으며 `Kotlin`은 이를 정적으로 해결한다.

> 참고) 클래스에 확장함수와 동일한 이름을 가진 멤버함수가 있는 경우, 항상 멤버 함수가 우선시 된다. 클래스의 정의된 확장 함수와 동일한 이름을 가진 멤버 함수를 추가한 다음 코드를 다시 컴파일하면 해당 함수의 의미 가 변경되어 새 멤버 함수를 참조하기 시작하므로 클래스의 API를 확장할 때 이 점을 염두에 두어야 한다. 
>
>또한 IDE는 확장 함수가 멤버 함수에 의해 섀도 처리된다는 경고를 표시한다. 


### 3.3.5 확장 속성

함수 구문이 아닌 속성 구문을 사용하여 액세스할 수 있는 인터페이스로 클래스를 확장할 수 있다. 프로퍼티라고 불리지만, 프로퍼티는 다음을 가질 수 없다.

상태를 저장할 적절한 장소가 없기 때문에 기존 `Java` 객체의 인스턴스에 추가 필드를 추가할 수 없다. 따라서 확장 프로퍼티는 항상 사용자 정의 접근자를 정의해야 한다. 그래도 더 짧고 간결한 호출 규칙을 제공하므로 유용하게 사용할 수 있다.

아래 예시를 보자.

```kotlin
val String.lastChar: Char
    get() = this.get(length - 1)
```

함수와 마찬가지로 확장 프로퍼티는 수신자 유형이 추가된 일반 프로퍼티처럼 보인다. 게터는 항상 정의해야 하는데, 그 이유는 백킹 필드가 없으므로 기본 게터 구현이 없기 때문이다. 이니셜라이저 같은 이유로 허용되지 않는다. 이니셜라이저로 지정된 값을 저장할 곳이 없기 때문이다. 

문자열 빌더에 동일한 프로퍼티를 정의하면 문자열 빌더의 내용을 수정할 수 있으므로 이를변수로 만들 수 있다.

```kotlin
var StringBuilder.lastChar: Char
    get() = this.get(length - 1)
    set(value) {
		this.setCharAt(length - 1, value)
	}
    
    
fun main() {
val sb = StringBuilder("Kotlin?") 
println(sb.lastChar) // ?
sb.lastChar = '!'
println(sb) // Kotlin!
}
```

Java에서 확장 프로퍼티에 액세스해야 하는 경우 해당 프로퍼티의 게터와 세터를 명시적으로 호출해야 한다는 점에 유의하자.

```kotlin
StringUtilKt.getLastChar("Java") 
String- UtilKt.setLastChar(sb, '!').
```

## 3.4 컬렉션 작업: vararg, infix fun 및 라이브러리 지원

- 임의의 개수의 인수를 받는함수를 선언할 수 있는 `vararg` 키워드
- infix 표기법으로 일부 인자 하나 함수를 수식없이 호출할 수 있다.
- 단일 복합값을 여러 변수로 압축해제할 수 있는 구조화 선언 디스트럭처링


### 3.4.1 Java 컬렉션 API 확장하기

`Kotlin`의 컬렉션이 `Java`의 컬렉션과 동일한 클래스이지만 `API`가 확장되었다. 

```kotlin
fun main() {
val strings: List<String> = listof("first", "second", "14th") 
strings.last() // 14th
val numbers: Collection<Int> = setof(1, 14, 2) 
numbers.sum() // 17
}
```

`Java` 라이브러리 클래스의 인스턴스임에도 불구하고 `Kotlin`에서 컬렉션을 사용하여 즉시 많은 작업을 수행할 수 있는 이유가 무엇일까? 

> `last()` 함수와 `sum()` 함수는 확장 함수로 선언되며 `Kotlin` 파
일에서 항상 기본적으로 임포트되기 때문이다.

`last()` 함수는 이전 섹션에서 설명한 문자열의 `lastChar`보다 더 복잡하지 않으며, `List` 클래스의 확장함수이다. `sum()`의 경우, 단순화된 피라레이션을 노출한다. (실제 라이브러리함수는 `Int` 숫자뿐만 아니라 모든 숫자 유형에 대해 작동함)

```kotlin
fun <T> List<T>.last(): T { /* returns the last element */ }
fun Collection<Int>.sum(): Int { /* sum up all elements */ }
```

`Kotlin` 표준 라이브러리에 있는 모든 것을 학습할 필요는 없지만, 무엇이 있는지 궁금할 수 있다. 컬렉션이나 다른 객체로 작업을 수행해야 할 때마다 `IDE`의 코드 완성 기능이 해당 유형의 객체에 사용할 수 있는 모든 함수를 표시해 준다. 이 목록에는 일반 메서드와 확장 함수가 모두 포함되어 있으므로 필요한 함수를 선택하여 사용하라.

- 표준 라이브러리 참조(https://kotlinlang.org/api/latest/jvm/stdlib/)

### 3.4.2 Varargs: 임의의 수의 인수를 허용하는 함수

함수를 호출하여 콜렉션을 만들 때 함수에 인수를 얼마든지 전달할 수 있다

```kotlin
val list = listof(2, 3, 5, 7, 11)
```

표준 라이브러리에서 이 함수가 어떻게 선언되었는지 찾아보면 다음과 같다.

```kotlin
fun listof<T>(vararg value: T): List<T> { /* 구현 */ }
```

이 메서드는 값을 배열로 패킹하여 메서드에 임의의 개수의 값을 전달할 수 있는 언어 기능인 `varargs`를 사용한다. `Kotlin`의 `vararg`는 `Java`의 `vararg`와 유사하지만 구문은 약간 다르다. 유형뒤에 점 세개를 붙이는 대신 매개변수에 `vararg` 수정자를 사용한다.


`Kotlin`과 `Java`의 또 다른 차이점은 함수 호출 구문이다.`varags`를 사용하면 전달해야 하는 인수가 이미 배열로 패킹되어 있는 경우에 사용할 수 있다. `Java`에서는 배열을 그대로 전달하지만, `Kotlin`에서는 모든 배열 요소가 호출되는 함수에 대해 별도의 인수가 되도록 명시적으로 배열의 압축을 풀어야 한다. 이 기능을 스프레드 연산자라고 하며, 해당인수 앞에 * 문자를 넣는 것 만으로 간단하게 사용할 수 있다. 

```kotlin
fun main(args: Array<String>) {
	val list = listof("args: ", *args) 
    println(list)
}
```

이 예는 스프레드 연산자를 사용하여 배열의 값과 일부 고정 값을 한 번의 호출로 결합할 수 있음을 보여준다. (이 기능은 Java에서는 지원되지 않음)

### 3.4.3 pairs으로 작업하기: infix 호출 및 선언 파괴하기

`map`을 만들려면 `mapOf` 함수를 사용한다.

```kotlin
val map = mapOf(1 to "1", 7 to "7", 53 to "53")
```

위 코드에서 `to` 라는 단어는 내장된 구조체가 아니라 특수한 종류의 메서드 호출, 즉 `infix` 함수의 호출이다. `infix` 호출에서 메서드 이름은 별도의 구분 기호 없이 대상 객체 이름과 매개변수 사이에 바로 배치된다. 다음 두 호출은 동일하다.

```kotlin
1.to("one") 
1 to "one"
```

`infix` 호출은 필수 __매개변수가 정확히 하나만 있는__ 일반 메서드 및 확장 함수와 함께 사용할 수 있다. 함수를 `infix` 표기법을 사용하여 호출할 수 있도록 하려면 함수에 `infix`수정자를 표시해야 한다. 다음은 `to` 함수 선언의 간소화된 버전이다.

```kotlin
infix fun Any.to(other: Any) = Pair(this, other)
```

`to` 함수는 당연히 한 쌍의 요소를 나타내는 `Kotlin` 표준 라이브러리 클래스인 `Pair`의 인스턴스를 반환합니다. `Pair`의 실제 선언과 제네릭을 사용할 수 있지만 여기서는 간단하게 하기 위해 생략하겠다.

`Pair`의 콘텐츠로 두 변수를 직접 초기화할 수 있다는 점에 유의하라.

```
VAL(숫자, 이름) = 1 to "1"
```

이 기능을 디스트럭처링 선언이라고 한다.

![](https://velog.velcdn.com/images/cksgodl/post/f8e678fb-bb0a-4697-b492-71129112fdf7/image.png)

이는 `withIndex` 함수를 사용하는 루프에서도 작동한다.

```kotlin
for ((index, element) in collection.withIndex()) {
	println("$index: $element")
}
```

이후 9장에서는 표현식을 분해하고 이를 사용하여 여러 변수를 초기화하는 일반적인 규 칙에 대해 설명한다.

`to` 함수는 확장 함수이다. 1을 "one", "one"을 1, list를 list.size()로 쓰는 등 모든 요소의 `Pair`을 만들 수 있으며, 이는 일반 수신자의 확장함수라는 의미이다. `mapOf` 함수의 시그니처를 살펴보자.

```kotlin
fun <K, V> mapof(vararg value: Pair<K, V>): Map<K, V>
```

`listOf`와 마찬가지로 `mapo`f는 다양한 수의 인수를 허용하지만 이번에는 키와 값의 쌍 이어야 한다. 새 맵을 만드는 것은 `Kotlin`에서 특별한 구조처럼 보일 수 있지만 간결한 구문을 가진 일반 함수이다. 

## 3.5 문자열 및 정규식 작업

`Kotlin` 문자열은 `Java` 문자열과 완전히 동일하다. `Kotlin` 코드에서 생성된 문자열을 모든 `Java` 메서드로 전달할 수 있으며, `Java` 코드에서 받은 문자열에 대해 모든 `Kotlin` 표준 라이브러리 메서드를 사용할 수 있다. __변환이 필요하지 않으며 추가 래퍼 객체가 생성되지 않는다.__

> String의 경우는 변환 및 추가 래퍼가 생성되지 않지만, `Int`와 `Integer`와 같은 경우 원시 타입을 활용하지 않은 경우 레퍼런스 타입으로 여겨져 추가 래퍼객체가 생성될 수 있다.

`Kotlin`은 여러 가지 유용한 확장 함수를 제공하여 표준 `Java` 문자열 작업을 더욱 쉽게 만든다. 또한 일부 혼란스러운 메서드를 숨기고 더 명확한 확장 함수를 추가한다. `API` 차이점의 첫 번째 예로 `Kotlin`에서 문자열 분할을 처리하는 방법을 살펴보겠다.

### 3.5.1 문자열 분할

문자열의 `split()` 메서드에 익숙할 것이다. 누구나 이 메서드를 사용하지만, 가끔 스택 오버플로(http://stackoverflow.com)에서 이 메서드에 대해 불만을 제기하는 사람들이 있다. 

_"Java의 split메서드가 점으로 작동하지 않아요.""_

`12.345-6.A".split(".")`을 호출하고 그 결과로 배열 `[12, 345-6, A]`를 기대한다. 하지만 `Java`의 `split()` 메서드는 빈 배열을 반환한다. 이는 정규식을 매개변수로 받아 그 표현식에 따라 문자열을 여러 개의 문자열로 분할하기 때문에 발생하는 현상이다. (여기서 점(.)은 임의의 문자를 나타내는 정규식으로 표현된다)

`Kotlin`은 혼란스러운 방법을 숨기고 대체 방법으로 몇 가지 오버
인수가 다른 `split`이라는 이름의 확장을 로드했다. 정규식을 취하는 메서드에는 문자열이 아닌 정규식 또는 패턴 및 특정 클래스 유형 값이 필요하다. 이렇게 하면 메서드에 전달된 문자 열이 일반 텍스트로 해석되는지 정규식으로 해석되는지 항상 명확하게 알 수 있다.

```kotlin
fun main() {
    println("12.345-6.A".split("\\.|-".toRegex()))
    // [12, 345, 6, A]
}
```

`Kotlin`은 `Java`와 정확히 동일한 정규식 구문을 사용한다. 정규식 작업을 위한 `API`도 표준 `Java` 라이브러리 `API`와 유사하지만 더 관용적이다. 예를 들어, `Kotlin`에서는 확장 함수 `toRegex`를 사용하여 문자열을 정규식으로 변환한다.

(아래같은 간단한 경우에는 정규식을 사용할 필요가 없다. )

```kotlin
fun main() { 
	println("12.345-6.A".split(".", "-")) // [12, 345, 6, A]
}
```

### 3.5.2 정규식 및 큰 따옴표로 묶인 문자열

_첫 번째 구현은 문자열의 확장자를 사용하고 두 번째 구현은 정규식으로 작동하는 두 가지 다른 예제를 살펴보자. 작업은 파일의 전체 경로 이름을 디렉터리, 파일 이름 및 확장자라는 구성 요소로 구문 분석하는 것이다._

![](https://velog.velcdn.com/images/cksgodl/post/fb3a9ce8-c4fa-4814-9ece-770d9e6a57cc/image.png)

`Kotlin` 표준 라이브러리에는 지정된 구분 기호의 첫 번째(또는 마지막) 발생 전(또는 후)에 부분 문자열을 가져오는 함수가 포함되어 있다. 따라서 아래 예시처럼 간단하게 구현할 수 있다. `Kotlin`을 사용하면 강력하고, 작성된 후에는 이해하기 어려운 정규식을 사용하지 않고도 문자열 작업을 더 쉽게 수행할 수 있다. 

```kotlin
fun parsePath(path: String) {
    val directory = path.substringBeforeLast("/")
    val fullName = path.substringAfterLast("/")
    val extension = fullName.substringAfterLast(".")
    println("Dir: $directory, name: $fileName, ext: $extension")
}

fun main() {
    parsePath("/Users/yole/kotlin-book/chapter.adoc")
    // Dir: /Users/yole/kotlin-book, name: chapter, ext: adoc
}
```

정규 표현식을 사용하려는 경우 `Kotlin` 표준 라이브러리가 도움이 될 수 있습니다. 아래 예시는 정규식을 사용하여 동일 한 작업을 수행하는 방법을 보여준다.

```kotlin
fun parsePathRegex(path: String) {
    val regex = """(.+)/(.+)\.(.+)""".toRegex()
    val matchResult = regex.matchEntire(path)
    if (matchResult != null) {
        val (directory, filename, extension) = matchResult.destructured
        println("Dir: $directory, name: $filename, ext: $extension")
    }
}

fun main() {
    parsePathRegex("/Users/yole/kotlin-book/chapter.adoc")
    // Dir: /Users/yole/kotlin-book, name: chapter, ext: adoc
}
```
![](https://velog.velcdn.com/images/cksgodl/post/a3afcb26-4e1f-414c-800f-c111da81cba4/image.png)

### 3.5.3 여러줄로된 큰따옴표로 묶인 문자열

```kotlin
val kotlinLogo =
    """
    | //
    |//
    |/ \
    """.trimIndent()
fun main() {
    println(kotlinLogo)
    // | //
    // |//
    // |/ \
}
```

여러 줄 문자열에는 큰따옴표 사이의 모든 문자가 포함된다. 여기에는 코드 서식을 지정하는 데 사용되는 줄 바꿈과 들여쓰기가 포함된다. 이런 경우에는 문자열의 실제 내용에만 관심이 있을 가능성이 높다. `trimIndent`를 호출하면 문자열의 모든 줄 에 대한 공통 최소 들여쓰기를 제거하고 문자열의 첫 번째 줄과 마지막 줄이 비어 있는 경우 제거할 수 있다.

여러 줄 문자열에도 문자열 템플릿을 사용할 수 있다. 여러 줄 문자열은 이스케이프 시퀀스를 지원하지 않으므로 문자열 내용에 리터럴 달러 기호나 이스케이프 유니 코드 기호를 사용해야 하는 경우 임베디드 표현식을 사용해야 한다. 따라서 이 문자열에 인코딩된 이스케이프 기호를 올바르게 해석하려면 

```kotlin
val think = """Hmm \uD83E\uDD14"""
```
를 작성하는 대신 다음과 같이 작성해야 한다.

```kotlin
val think = """Hmm ${"\uD83E\uDD14"}"""
```

## 3.6 코드를 깔끔하게 정리하기: Local Funtions 및 Extensions

많은 개발자는 좋은 코드의 가장 중요한 특성 중 하나가 중복이 없는 것이라고 생각한다. 이 원칙에 대한 특별한 이름도 있다. -> `반복하지 않기(DRY)` 

하지만 `Java`로 코드를 작성할 때 이 원칙을 따르는것이 항상 쉬운일은 아니다. 많은 경우 `IDE`의 메서드 추출 리팩터링 기능을 사용하여 긴 메서드를 작은 덩어리로 쪼개고 그 덩어리를 재사용할 수 있다. 하지만 이렇게 하면 작은 메서드가 많고 메서드 간의 관계가 명확하지 않은 클래스가 되기 때문에 코드를 이해하기 더 어려워질 수 있다.

추출한 함수를 포함하는 함수 안에 중첩할 수 있는 `Kotlin`은 더 깔끔한 솔루션을 제공한다. 이렇게 하면 추가 구문 오버헤드 없이 필요한 구조를 만들 수 있다. 로컬 함수를 사용하여 상당히 일반적인 코드 중복 사례를 수정하는 방법을 살펴 보겠다.

```kotlin
class User(val id: Int, val name: String, val address: String)

fun saveUser(user: User) {
    if (user.name.isEmpty()) {
    throw IllegalArgumentException(
        "Can't save user ${user.id}: empty Name")
	}

	if (user.address.isEmpty()) {
        throw IllegalArgumentException("Can't save user ${user.id}: empty Address")
	} // Save user to the database
}
    
fun main() {
    saveUser(User(1, "", ""))
    // java.lang.IllegalArgumentException: Can't save user 1: empty Name
}
```

여기서 중복되는 코드의 양은 상당히 적으며, 사용자 유효성 검사라는 특수한 경우를 처리하는 전체 메서드를 클래스에 갖고 싶지 않을 것이다. 하지만 유효성 검사 코드를 로컬 함수에 넣으면 중복을 없애고 여전히 명확한 코드 구조를 유지할 수 있다. 

```kotlin
class User(val id: Int, val name: String, val address: String)
fun saveUser(user: User) {
    fun validate(user: User,
                 value: String,
                 fieldName: String) {
    	if (value.isEmpty()) {
			throw IllegalArgumentException("Can't save user ${user.id}: empty $fieldName")
        } 
	}
    
    validate(user, user.name, "Name")
    validate(user, user.address, "Address")
    // Save user to the database
}
```

유효성 검사 로직이 중복되지는 않지만 여전히 유효성 검사 기능의 범위에 국한되어 있다. 프로젝트가 발전함에 따라 `User`에 다른 필드를 추가해야 하는 경우 더 많은 유효성 검사를 쉽게 추가할 수 있다. 하지만 User 객체를 유효성 검사 함수에 전달하는 것은 다소 불편하다. 좋은 소식은 로컬 함수는 둘러싸는 함수의 모든 매개변수와 변수에 액세스할 수 있기 때문에 완전히 불필요하다는 것이다. 이 점을 활용하여 추가 `User` 매개변수를 제거해보자.

```kotlin
class User(val id: Int, val name: String, val address: String)
fun saveUser(user: User) {
    fun validate(value: String, fieldName: String) {
        if (value.isEmpty()) {
            throw IllegalArgumentException(
                "Can't save user ${user.id}: " +
                    "empty $fieldName")
	}}
    
    validate(user.name, "Name")
    validate(user.address, "Address")
    // Save user to the database
}
```

이 예제를 더욱 개선하려면 유효성 검사 로직을 `User` 클래스의 확장 함수로 이동하면 된다.

```kotlin
class User(val id: Int, val name: String, val address: String)

fun User.validateBeforeSave() {
    fun validate(value: String, fieldName: String) {
        if (value.isEmpty()) {
            throw IllegalArgumentException("Can't save user $id: empty $fieldName")
	}}
    validate(name, "Name")
    validate(address, "Address")
}

fun saveUser(user: User) {
    user.validateBeforeSave() // Save user to the database
}
```

위의 예시를 통해 확장 함수로 추출하는 것은 의외로 유용하게 쓰이는 것으로 밝혀졌다. `User`는 라이브러리 클래스가 아니지만, 이 로직은 `User`가 사용되는 다른 곳과 관련이 없으므로 `User`의 메서드에 넣지 않는 것이 좋다. 

이 접근 방식을 따르면 클래스의 API에는 모든 곳에서 사용되는 필수 메서드만 포함되도록 클래스는 작고 이해하기 쉬운 상태로 유지되는 것이 좋다. 반면에 단일 객체를 주로 다루고 해당 객체의 비공개 데이터에 액세스할 필요가 없는 함수는 별도의 조건 없이 해당 멤버에 액세스할 수 있다.

확장 함수는 로컬 함수로 선언할 수도 있으므로 한 단계 더 나아가 `saveUser`에 `User.validateBeforeSave`를 로컬 함수로 포함할 수도 있다. 그러나 깊게 중첩된 로컬 함수는 일반적으로 읽기가 상당히 어렵기 때문에 일반적으로 두 수준 이상의 중첩을 사용하지 않는 것이 좋다.

## 요약

- Kotlin은 더 풍부한 API로 Java 컬렉션 클래스를 개선한다.
- 함수 매개변수의 기본값을 정의하면 오버로드된 함수를 정의할 필요성이 크게 줄어들고, 명명된 인수 구문을 사용하면 매개변수가 많은 함수를 훨씬 더 읽기 쉽게 호출할 수 있다.
- 함수와 프로퍼티를 클래스의 멤버가 아닌 파일에서 직접 선언할 수 있으므로보다 유연한 코드 구조를 만들 수 있다.
- 확장 함수 및 프로퍼티를 사용하면 소스코드를 수정하지 않고 런타임 오버헤드없이 외부 라이브러리에 정의된 클래스를 포함하여 모든 클래스의 API를 확장 할 수 있다.
- `infix` 함수는 단일 인수로 연산자와 유사한 메서드를 호출할 수 있는 깔끔한 구문을 제공한다.
- `Kotlin`은 정규식과 일반 문자열 모두를 위한 편리한 문자열 처리 함수를 다수 제공한다.
- 큰따옴표로 묶인 문자열은 `Java`에서 이스케이프 이스케이프와 문자열 연결이 많이 필요한 표현식을 깔끔하게 작성할 수 있는 방법을 제공한다.
- 로컬함수를 사용하면 코드를 보다 깔끔하게 구성하고 중복을 제거할 수 있다.

