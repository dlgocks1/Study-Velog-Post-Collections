> Kotlin 프로그래밍 언어의 소스 코드와 관련된 Google의 Android 코딩 표준을 알아보자.
 
 아래에서 설명한 코틀린 규칙을 준수하는 경우에만 Google Android 스타일로 간주한다고 한다.

[구글 안드로이드 코틀린스타일 가이드](https://developer.android.com/kotlin/style-guide?hl=ko)

# 소스파일

모든 소스파일은 UTF-8로 인코딩 되어야하며

# 파일 이름
```
// MyClass.kt
class MyClass { }
```
클래스가 하나이면 `Myclass.kt` 클래스 이름을 파일명으로 설정
```
// Map.kt
fun <T, O> Set<T>.map(func: (T) -> O): List<O> = // …
fun <T, O> List<T>.map(func: (T) -> O): List<O> = // …
```
소스 파일에 탑레밸 수준 함수가 여러 개 있는 경우 콘텐츠를 설명하는 이름을 `파스칼케이스`로 적용

# 구조
`.kt` 파일은 다음과 같은 순서로 구되어야한다.

1. 저작권 및/또는 라이선스 헤더(선택사항)
2. 파일 수준 주석
3. Package 문
4. Import 문
5. 최상위 수준 선언

저작권/라이선스는 Kdoc스타일을 사용하면 안된다.
```
Good Example
/*
 * Copyright 2017 Google, Inc.
 *
 * ...
 */
 
Bad Example
Kdoc Style
/**
 * Copyright 2017 Google, Inc.
 *
 * ...
 */

// Copyright 2017 Google, Inc.
//
// ...
```

**Package문**은 줄바꿈하지 않는다.

**import문**
클래스, 함수 및 속성의 import 문은 단일 목록으로 가져온다.
모든 유형을 가져오는 Wildcard imports는 허용되지 않는다.
```
import java.awt.*; // X
```
임포트문은 줄바꿈하지 않는다.

**최상위 수준 선언**

파일의 내용은 하나의 테마(기능)에 초점을 맞춰야 한다. 
관련 없는 기능은 자체 파일로 분리해야 하며 단일 파일 내의 Public선언은 최소화해야 한다.

소스 파일은 일반적으로 위에서 아래로 읽는다.
일반적으로 순서는 위의 소스를 이해하면 아래의 소스를 이해할 수 있게 순서를 지정한다.
파일, 컨벤션에 따라 순서를 달라질 수 있다.
하나의 파일에는 100개의 속성, 다른 10개의 함수 및 또 다른 단일 클래스가 포함될 수 있다.

**클래스 멤버 정렬**
클래스 내 멤버의 순서는 최상위 수준 선언과 동일한 규칙을 따른다.


# 서식

## 중괄호

한줄에 들어가는 `when`이나 `if`와 같은 브랜치 문은 중괄호가 필요없다.

```
if (string.isEmpty()) return

val result =
    if (string.isEmpty()) DEFAULT_VALUE else string

when (value) {
    0 -> return
    // …
}
```

`if`, `for`, `when` 브랜치, `do` 및 `while` 문과 표현식의 경우 본문이 비어 있거나 단일 구문만 포함하는 경우에도 줄이바뀌면 중괄호는 필요하다.
```
if (string.isEmpty())
    return  // WRONG!

if (string.isEmpty()) {
    return  // Okay
}

if (string.isEmpty()) return  // WRONG
else doLotsOfProcessingOn(string, otherParametersHere)

if (string.isEmpty()) {
    return  // Okay
} else {
    doLotsOfProcessingOn(string, otherParametersHere)
}
```

## 비어 있지 않은 블록

K&R 스타일(이집트 대괄호)를 따른다.

K&R 스타일
* 여는 중괄호 앞에 줄바꿈 없음.
* 여는 중괄호 뒤에 줄바꿈 있음.
* 닫는 중괄호 앞에 줄바꿈 있음.
* 중괄호로 구문이 종료되면 줄바꿈이 있음. 그러나 else 또는 쉼표가 오면 줄바꿈 없음

```
return Runnable {
    while (condition()) { // 여는 중괄호 뒤에 줄바꿈 있음.
        foo()
    } // 중괄호로 구문이 종료되면 줄바꿈이 있음.
}

return object : MyClass() {
    override fun foo() {
        if (condition()) {
            try {
                something()
            } catch (e: ProblemException) {
                recover()
            }
        } else if (otherCondition()) { // else 또는 쉼표가 오면 줄바꿈 없음
            somethingElse()
        } else {
            lastThing()
        }
    }
}
```


## 빈 블록

```
try {
    doSomething()
} catch (e: Exception) {} // WRONG! -> 여는 중괄호 뒤에 줄바꿈 있음.

try {
    doSomething()
} catch (e: Exception) {
} // Okay
```

## 표현식

표현식으로 사용되는 if/else 조건문에서는 전체 표현식이 한 줄에 들어가는 경우에만 중괄호를 생략할 수 있다.
```
val value = if (string.isEmpty()) 0 else 1  // Okay

val value = if (string.isEmpty())  // WRONG!
    0
else
    1
    
val value = if (string.isEmpty()) { // Okay
    0
} else {
    1
}
```


## 들여쓰기

새 블록 또는 블록 형식 구문이 열릴 때마다 들여쓰기 4칸씩 증가.
```
val value = if (string.isEmpty()) {
    0 // 4칸
} else {
    1
}
```


## 줄바꿈

코드의 열 제한은 최대 100글자이며 package문, import문, 주석의 명령줄 등 예외말고는 모두 줄바꿈 되어야한다.

## 줄바꿈 위치

우선적으로 줄바꿈은 더 높은 구문 수준에서 하는 것이 좋다.

> 줄바꿈의 기본 목표는 코드를 명확히 보여주는 것이며 코드를 최대한 적은 수의 줄에 표시할 필요는 없다.


## 함수

함수의 파라미터가 한 줄에 들어가지 않으면 각 매개변수 선언을 한 줄에 하나씩 표시한다.
이러한 파라미터는 들여쓰기(+4)를 사용해야 한다.
닫는 괄호()) 및 반환 유형은 추가 들여쓰기 없이 한 줄에 하나씩 입력한다.

```
fun <T> Iterable<T>.joinToString(
    separator: CharSequence = ", ",
    prefix: CharSequence = "",
    postfix: CharSequence = ""
): String {
    // …
}
```


## 표현식 함수

함수에 표현식이 하나만 포함되는 경우 표현식 함수로 표현한다.

```
override fun toString(): String = "Hey"
```

## 속성

속성 정의가 한 줄에 들어가지 않는 경우 등호(=)뒤에서 줄바꿈하고 들여쓰기를 사용한다.
```
private val defaultCharset: Charset? =
    EncodingRegistry.getInstance().getDefaultCharsetForPropertiesFiles(file)
```

`get`, `set`과 같은 경우는 일반 들여쓰기를 적용하여 한줄에 하나씩 입력한다.
```
var directory: File? 
	get() = null
    set(value) {
        // …
    }
```


## 공백(빈 줄)

* 클래스의 연속하는 멤버 사이: 속성, 생성자, 함수, 중첩 클래스 등
* 코드를 논리 하위 섹션으로 구성하는 데 필요하다면 식 사이에 빈 줄을 넣는다.

여러 개의 빈 줄을 연속으로 사용할 수 있지만 권장하지 않으며 필요하지도 않다.

## 수평

```
// WRONG!
for(i in 0..1) {
}

// Okay
for (i in 0..1) {
}
```
이는 IDE의 save actions와 같은 formatter을 사용하면 스스로 맞추어 준다.
설정의 coding style 탭에서 이러한 설정을 바꿀 수 있음

인터페이스 또는 상속클래스를 지정하기 위해서는 콜론앞에도 줄바꿈을 넣는다.
```
// WRONG!
class Foo: Runnable

// Okay
class Foo : Runnable

// WRONG
fun <T: Comparable> max(a: T, b: T)

// Okay
fun <T : Comparable> max(a: T, b: T)

// WRONG
fun <T> max(a: T, b: T) where T: Comparable<T>

// Okay
fun <T> max(a: T, b: T) where T : Comparable<T>
```

주석은 양쪽의 여러개의 공백을 넣는걸 허용하지만 필수는 아니다.
```
// WRONG!
var debugging = false//disabled by default

// Okay
var debugging = false // disabled by default
```

## Enum 클래스

열거형의 상수가 한줄에 표시되면 줄바꿈이 필요하지 않다.

```
enum class Answer { YES, NO, MAYBE }
```


## 어노테이션

어노테이션은 구문 바로 앞에 별도의 줄로 입력된다.
```
@Retention(SOURCE)
@Target(FUNCTION, PROPERTY_SETTER, FIELD)
annotation class Global
```

인수가 없으면 한 줄로 입력 가능
```
@JvmField @Volatile
var disposable: Disposable? = null

@Volatile var disposable: Disposable? = null
```

## 리턴 타입 / 속성 유형

표현식 함수 본문 또는 속성 이니셜라이저가 스칼라 값이거나 반환 유형을 본문에서 명확히 추론할 수 있는 경우 생략할 수 있다.

```
override fun toString(): String = "Hey"
override fun toString() = "Hey"

private val ICON: Icon = IconLoader.getIcon("/icons/kotlin.png")
private val ICON = IconLoader.getIcon("/icons/kotlin.png")
```


# 이름 지정

## 패키지이름
패키지이름은 모두 소문자이며 연속 단어도 밑줄 없이 연결된다.
```
// Okay
package com.example.deepspace
// WRONG!
package com.example.deepSpace
// WRONG!
package com.example.deep_space
```

## 유형이름
클래스 이름은 모두 파스칼케이스(PascalCase)로 작성된다.
테스트 클래스의 이름은 테스트 중인 클래스의 이름으로 시작하고 `Test`로 끝난다.
```
fun HashIntegrationTest() {
}
```

## 함수이름

함수 이름은 카멜케이스(camelCase)로 작성되며 일반적으로 동사 또는 동사구로 작성한다.(sendMessage, stop)

`@Composable`함수는 파스칼케이스로 작성되며 명사처럼 작명한다.
```
@Composable
fun NameTag(name: String) {
    // …
}
```

테스트 함수에는 밑줄을 표시할 수 있다.
```
@Test fun pop_emptyStack() {
    // …
}
```

함수 이름은 일부 플랫폼에서 지원되지 않으므로 공백을 포함하면 안 된다.
```
// WRONG!
fun `test every possible case`() {}
// OK
fun testEveryPossibleCase() {}
```


## 상수이름

상수 이름에는 UPPER_SNAKE_CASE(모두 대문자)를 사용하여 밑줄로 단어를 구분한다.

상수란 무엇을 의미하는가?
상수는 맞춤 `get`함수가 없는 읽기전용 콘텐츠를 의미하며, 변경할 수 없는 유형 및 컬렉션 도 이에 포함된다.(const로 포함된 경우도)
```
const val NUMBER = 5
val NAMES = listOf("Alice", "Bob")
val AGES = mapOf("Alice" to 35, "Bob" to 32)
val COMMA_JOINER = Joiner.on(',') // Joiner is immutable
val EMPTY_ARRAY = arrayOf()
```
상수 값은 `object` 내부 또는 내부 최상위 선언으로만 정의할 수 있다. 상수의 요구사항을 충족하지만, `class`의 내부에 정의된 값은 상수가 아닌 이름을 사용해야 한다.


## 상수가 아닌 이름

상수가 아닌 이름은 camelCase로 작성한다.
이는 인스턴스 속성, 로컬 속성, 매개변수 이름에 적용된다.
```
val variable = "var"
val nonConstScalar = "non-const"
val mutableCollection: MutableSet = HashSet()
val mutableElements = listOf(mutableInstance)
val mutableValues = mapOf("Alice" to mutableInstance, "Bob" to mutableInstance2)
val logger = Logger.getLogger(MyClass::class.java.name)
val nonEmptyArray = arrayOf("these", "can", "change")
```
 
## 백킹 프로퍼티

백킹 프로퍼티가 필요한 경우 `_실제변수명`으로 선언해야 한다.
```
private var _table: Map? = null

val table: Map
    get() {
        if (_table == null) {
            _table = HashMap()
        }
        return _table ?: throw AssertionError()
    }
```

## 카멜케이스로의 변환

XmlHttpRequest(O) <-> XMLHTTPRequest(X)
newCustomerId(O) <-> newCustomerID(X)
innerStopwatch(O) <-> innerStopWatch(X)
supportsIpv6OnIos(O) <-> supportsIPv6OnIOS(X)
YouTubeImporter(O) <-> YoutubeImporter(X)


## 문서화
Kdoc 블록을 사용하여 함수에 설명을 추가한다.
```
/**
 * Multiple lines of KDoc text are written here,
 * wrapped normally…
 */
fun method(arg: String) {
    // …
}
```

단일 행은 다음과 같이 표현한다.
```
/** An especially short bit of KDoc. */
```

이러한 주석 내에서는 다음과 같은 어노테이션을 사용할 수 있다.
@constructor, @receiver, @param, @property, @return, @throws, @see 순으로 표시된다.

설명이 필요 없는 함수 -> 단순하고 명확한 함수에는 주석을 달지 않는다.
또한 이러한 주석을 인용하여 사용하는 것 보다, 사용자가 알기 쉬운 함수명으로 작성하는 것이 더 효율적이다.
독자가 해당 함수에 대한 표준 동작을 이해하지 못할 때 이러한 주석을 단다.

---

# 코틀린 컨벤션 가이드

안드로이드에서의 코틀린 스타일과 겹치는 것이 많기 때문에 최대한 겹치지 않으면서 모를만한 컨벤션만 뽑아보았다.

[Coding Convention - kotlinlang.org](https://kotlinlang.org/docs/coding-conventions.html#function-names)

## 테스트 메소드의 네이밍
```
class MyTestCase {
     @Test fun `ensure everything works`() { /*...*/ }

     @Test fun ensureEverythingWorks_onAndroid() { /*...*/ }
}
```
코틀린의 테스트명은 백틱 안에 들어갈 수 있다.
하지만 안드로이드 런타임에는 지원하지 않는 다는 것을 명심하자.

## 프로퍼티 네이밍

`const`를 사용하거나 최상위 오브젝트, 상수 등의 경우는 대문자만을 사용한 스네이크케이스를 사용하여 표현한다.
```
const val MAX_COUNT = 8
val USER_NAME_FIELD = "UserName"
```
최상위래밸의 오브젝트나 프로퍼티여도 `mutable`데이터면 카멜케이스로 작성한다.
```
val mutableCollection: MutableSet<String> = HashSet()
```
싱글톤 프로퍼티는 파스칼케이스를 사용하여 작성한다.
```
val PersonComparator: Comparator<Person> = /*...*/
```
Enum 클래스의 상수는 모두 대문자로 작성하는 거나, `-`를 사용한 대문자 스네이크케이스로 표현한다.
```
val PersonComparator: Comparator<Person> = /*...*/
```

## 공백

* 연산자 사이에는 공백을 넣자. `a + b`
* 괄호 사이에는 공백을 넣지 말자. `(, [, ], )` 사이에 공백 금지
* `.`이나 `?.`사이에 공백 금지
* `//`주석 뒤에는 공백 한칸 두기 `// 주석이예용`
* `::`근처에 주석 금지, `String::length`
* `?`앞에 주석금지 `String?`

## 클래스

너무 긴 클래스의 파라미터들은 다음과 같이 줄바꿈한다.
```
class Person(
    id: Int,
    name: String,
    surname: String
) : Human(id, name) { /*...*/ }
```
비슷하게 여러 인터페이스 또는 슈퍼클래스를 상속받는 클래스는 다음과 같이 표현한다.
```
class MyFavouriteVeryLongClassHolder :
    MyLongHolder<MyFavouriteVeryLongClass>(),
    SomeOtherInterface,
    AndAnotherOne {

    fun foo() { /*...*/ }
}
```

## 수식자 순서

여러개의 수식자가 온다면 순서는 다음과 같다.
```
1. public / protected / private / internal
2. expect / actual
3. final / open / abstract / sealed / const
4. external
5. override
6. lateinit
7. tailrec // 꼬리 재귀
8. vararg
9. suspend
10. inner
11. enum / annotation / fun // as a modifier in `fun interface`
12. companion
13. inline / value
14. infix
15. operator
16. data
```

## 함수

한줄에 들어가지 않는 함수는 다음과 같이 작성한다.
```
fun longMethodName(
    argument: ArgumentType = defaultValue,
    argument2: AnotherArgumentType,
): ReturnType {
    // body
}
```

## 메소드 콜

많은 아규먼트 있는 메소드 호출시 이름있는 아규먼트를 사용하자.
```
drawSquare(
    x = 10, y = 10,
    width = 100, height = 100,
    fill = true
)
```

## 연속 호출

연속된 호출이 요청되면 `.`이나 `?.`를 기준으로 줄바꿈을 하자. (탭은 덤)
```
val anchor = owner
    ?.firstChild!!
    .siblings(forward = true)
    .dropWhile { it is PsiComment || it is PsiWhiteSpace }
```

## 람다식

람다식의 기본은 다음과 같지만,
```
appendCommaSeparated(properties) { prop ->
    val propertyValue = prop.get(obj)  // ...
}
```

변수명이 너무 길거나 많으면 다음과 같이 줄바꿈을 해도 된다.
```
foo {
   context: Context,
   environment: Env
   ->
   context.configureEnv(environment)
}
```

## Trailing commas

코틀린에서는 마지막 아이템 뒤에 콤마를 붙일 수 있다.

```
class Person(
    val firstName: String,
    val lastName: String,
    val age: Int, // trailing comma
)
```

이는 코틀린 1.4 이상의 버전에서 가능해졌으며

* 이에 따라 버전차이의 컨트롤이 쉬워진다.

* 요소를 쉽게 추가하고 순서를 변경할 수 있다.

트레일링 콤마는 완전이 optional이다. 같이 일하는 팀, 그룹에 맞추자.

## 문자열 템플릿

```
println("$name has ${children.size} children")
```
문자열 템플릿에 단순 변수를 삽입할 때 `곱슬곱슬한` 대괄호를 사용하지 말기.
더 긴 식에 대해서만 `곱슬곱슬한` 중괄호를 사용하자.

# 코틀린에 대한 관용적 기능

## 불변성
변하지 않는 값에 대해서는 `var`보다 `val`로 선언하자.

변경되지 않은 컬렉션을 선언하려면 항상 불변 컬렉션 인터페이스(Collection, List, Set, Map)를 사용하자.
팩토리 함수를 이용하여 콜렉션 인스턴스를 만들 때는 불변의 콜렉션 유형을 반환하는 함수로 만들어라.

```
// Bad: arrayListOf() returns ArrayList<T>, which is a mutable collection type
val allowedValues = arrayListOf("a", "b", "c")

// Good: listOf() returns List<T>
val allowedValues = listOf("a", "b", "c")
```

## 기본값 정의
기본값을 정의하여 함수 오버로딩 파라미터를 정의하라.
```
// Bad
fun foo() = foo("a")
fun foo(a: String) { /*...*/ }

// Good
fun foo(a: String = "a") { /*...*/ }
```

## 타입 별명
코드에서 여러 번 사용되는 유형 매개변수를 가진 유형이 있는 경우
타입별명을 정의하자.

```
// 변수타입
typealias NodeSet = Set<Network.Node>
typealias FileTable<K> = MutableMap<K, MutableList<File>>
typealias PersonIndex = Map<String, Person>

// 함수타입
typealias MouseClickHandler = (Any, MouseEvent) -> Unit
typealias MyHandler = (Int, String, Any) -> Unit
typealias Predicate<T> = (T) -> Boolean
```

```
typealias Predicate<T> = (T) -> Boolean

fun main() {
    val f: (Int) -> Boolean = { it > 0 }
    println(listOf(1, -2).filter(p)) // prints "[1]"
}
```

## 람다 매개변수

짧고 중첩되지 않은 람다식에서 매개 변수를 명시적으로 선언하는 대신 it을 사용하자.
매개 변수가 있는 중첩된 람다에서는 항상 매개 변수를 명시적으로 선언하자.


## 람다에서의 리턴

람다에 여러 개의 레이블링된 리턴을 사용하지 않도록 하자.
```
listOf(1, 2, 3, 4, 5).forEach {
	if (it == 3) return@forEach 
	print(it)
}
```

람다가 끝날 수 있는 방식이 하나뿐이도록 구성하라.
이게 가능하지 않거나 충분히 명확하지 않으면 람다를 익명 함수로 변환하는 것을 고려해 봐라.

## 반복

`for`루프보다 고차 함수(filter, map 등)를 사용하는 것을 선호하라.

그러나 각각에 대해 (리시버가 null이 될 수 있거나, 긴 연속 호출의 일부로 사용되는 경우를 제외하고)

```
for (i in 0..n - 1) { /*...*/ }  // bad
for (i in 0 until n) { /*...*/ }  // good
```

## 함수 vs 프로퍼티

만약 함수가 아무런 아규먼트를 받지 않으면, 읽기 전용 속성과 상호 호환될 수 있다.

코틀린의 기본 알고리즘은 함수보다 프로퍼티를 선호한다. 그 이유는

* throw를 뱉지 않는다.

* 계산 비용이 저렴함(또는 첫 번째 실행 시 캐시됨)

* 개체 상태가 변경되지 않은 경우 호출에 대해 동일한 결과를 반환합니다.

함수와 프로퍼티를 사용하는 것에 차이가 없다면 프로퍼티를 사용하라.


## 확장함수
확장 함수를 자유롭게 만들어 사용하자.

객체에 주로 작용하는 함수가 있을 때마다 해당 객체를 리시버로 받아들이는 확장 함수로 만드는 것을 고려하자.
또한 API 오염을 최소화하기 위해 확장 기능의 가시성을 최대한 제한합니다.
(IDE에 자꾸 추천됨)
필요에 따라 최상위 확장 기능을 사용하자.

## Infix 함수

인픽스 함수
비슷한 역할을 하는 두 개체에서 작동하는 경우에만 함수를 infix로 선언하자.
좋은 예: `and`, `to`, `zip` 잘못된 예: `add`

메서드가 리시버 객체를 변경하는 경우 메서드를 infix로 선언하지 마라.


## 팩토리 함수

어떤 클래스에 대한 팩토리 함수를 선언하는 경우 클래스와 동일한 이름을 지정하지 말기

팩토리 함수의 특별한 동작을 정의한 이름을 사용하는 것을 선호하자.
특별한 의미가 없는 경우에만 클래스와 동일한 이름을 사용.

```
class Point(val x: Double, val y: Double) {
    companion object {
        fun fromPolar(angle: Double, radius: Double) = Point(...)
    }
}
```