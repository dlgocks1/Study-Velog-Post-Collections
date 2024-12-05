
이 장에서는 첫 번째 `Kotlin` 프로그램을 작성하는 데 필요한 `Kotlin` 언어의 기본 사항을 학습한다. 기본사항의 예는 아래와 같다.

- 함수, 변수, 클래스, 열거형 및 속성 선언하기
- Kotlin의 제어 구조
- 스마트 캐스트
- 예외 던지기 및 처리

이 장이 끝날 때쯤이면 가장 관용적이지는 않더라도 `Kotlin` 언어의 기본 사항을 조합하여 자신만의 `Kotlin` 코드를 작성할 수 있을 것이다.

>  관용적 Kotlin이란 무엇인가??
>
> 관용적 코틀린은 '코틀린 원어민'이 적절한 경우 언어 기능과 구문 설탕을 사용 하여 코드를 작성하는 방식이다. 관용적 코드는 커뮤니티에서 일반적 으로 받아들여지는 프로그래밍 스타일에 적합하며 언어 디자이너의 권장 사항을 따른다.
>
> 다른 기술과 마찬가지로 관용적 `Kotlin`을 작성하는 방법을 배우려면 시간과 연습이 필요하다. 이 책을 진행하면서 제공된 코드 샘플을 살펴보고 직접 코드를 작성하다 보면 점차 관용적 `Kotlin` 코드의 모양과 느낌에 대한 직관이 생기고 이러한 학습 내용을 자신의 코드에 독립적으로 적용할 수 있는 능력을 갖추게 될 것이다.

## 2.1 기본 요소: 함수 및 변수

이 섹션에서는 모든 Kotlin 프로그램이 구성하는 기본 요소인 함수와 변수에 대해 소개한다.

### 2.1.1 첫 번째 Kotlin 프로그램 작성하기 "안녕하세요, 세상!"

```kotlin
fun main() {
	println("Hello, world!")
}
```

- `fun` 키워드는 함수를 선언하는 데 사용된다. `Kotlin`으로 프로그래밍하는 것은 정말 `fun` `fun` 하군요!!
- 이 함수는 클래스에 넣을 필요없이 모든 `Kotlin` 파일의 최상위 수준에서 선언 할 수 있다. (최상위 함수)
- 최상위 수준에서 추가 인수 없이 메인 함수를 애플리케이션의 진입점으로 지정할 수 있다
- `Kotlin`은 간결함을 강조한다. 콘솔에 텍스트를 표시하려면 println을 작성하기만 하면 된다.(자바 : System.out.println)
- 다른 많은 현대 언어와 마찬가지로 줄 끝에서 세미콜론을 생략할 수 있다

### 2.1.2 매개변수와 반환값이 있는 함수 선언하기

```kotlin
fun max(a: Int, b: Int): Int {
	return if (a > b) a else b
}

fun main() { println(max(1, 2)) // 2
```

> 메인함수의 매개변수 및 반환유형
> 
> "Hello, World!" 예제에서 이미 살펴보았듯이 모든 Kotlin 프로시저의 진입점은 `main` 함수 이다. 이 함수는 매개 변수 없이 선언하거나 문자열 배열을 인수로 사용하여 선언할 수 있다(`args: Array<String>`). 후자의 경우 배열의 각 요소는 애플리케이션에 전달된 명령줄 매개변수에 해당한다. 또한 어떤 경우든 메인 함수는 어떤 값도 반환하지 않는다.


### 2.1.3 표현식 본문을 사용하여 함수 정의를 더 간결하게 만들기

```kotlin
fun max(a: Int, b: Int): Int = if (a > b) a else b // if, when, try 등 가능
```

표현식을 활용하여 함수를 간단하게 표현할 수 있다. (IDE에서도 제공한다.)

![](https://velog.velcdn.com/images/cksgodl/post/cf7bf56d-8eb2-4204-b473-edee5a2d8587/image.png)

### 2.1.4 데이터를 저장하는 변수 선언하기

```kotlin
val question: String = "삶, 우주, 그리고 모든 것에 대한 궁극적인 질문" 
val answer: Int = 42
// 유형 선언을 생략하여 예제를 좀 더 간결하게 만들 수도 있다
val question = "삶, 우주, 그리고 모든 것에 대한 궁극적인 질문" 
val answer = 42
```

유형을 지정하지 않으면 컴파일러가 이니셜라이저 표현식을 분석하여 그 유형을 변수 유형으로 사용한다. 이 경우 이니셜라이저인 `42`의 타입은 `Int`이므로 변수 응답의 타입도 동일하다.


```kotlin
fun main() {
	val answer: Int
	answer = 42
}
```

변수를 즉시 초기화하지 않고 나중에 할당하는 경우 컴파일러가 변수의 유형을 유추할 수 없다. 이 경우 변수의 유형을 명시적으로 지정해야 한다.

### 2.1.5 변수를 읽기 전용 또는 재할당 가능으로 표시하기

`Kotlin`은 두가지 변수 타입을 제공한다. -> `val` 및 `var`

- val(에서 값)은 읽기 전용 참조를 선언한다. val로 선언된 변수는 한 번만 할당할 수 있다. (java에서는 final로 표시된다.)
- var(변수에서)는 재할당 가능한 참조를 선언한다. 이러한 변수는 초기화된 후에 도 다른 값을 할당할 수 있다. (이 동작은 Java의 일반적이고 최종적이지 않은 변수와 유사)

기본적으로 `Kotlin`의 모든변수는 `val` 키워드로 선언하고, 필요한 경우에만 `var`로 변경 해야 한다. 

```kotlin
fun canPerformoperation(): Boolean {
    return true
}

fun main() {
	val result: String
	if (canPerformoperation()) {
		result = "성공" 
	} else {
		result = "작업을 수행할 수 없습니다" 
    }
}    
```

값 참조는 그 자체가 읽기 전용이고 일단 할당 된 후에는 변경할 수 없지만, 참조가 가리키는 객체는 변경 가능할 수 있다. 

```kotlin
fun main() {
	val languages = mutableListof("Java") 
    languages.add("Kotlin")
}
```

### 2.1.6 더 쉬운 문자열 서식 지정: 문자열 템플릿

```kotlin
fun main() {
	val input = readln()
	val name = if (input.isNotBlank()) input else "Kotlin"
	println("안녕하세요, $name!")
} 
```

## 2.2 동작 및 데이터 캡슐화: 클래스 및 속성

다른 객체 지향 프로그래밍 언어와 마찬가지로 `Kotlin`은 클래스의 추상화를 제공한다. 이 영역에 대한 개념은 익숙하겠지만 다른 객체 지향 언어보다 훨씬 적은 코드로 많은 일반적인 작업을 수행할 수 있다는 것을 알게 될 것이다.

```java
// In Java
public class Person {
	private final String name;
    public Person(String name) {
    	this.name = name;
	}

	public String getName() { return name; }
}
```

```kotlin
// In Kotlin
class Person(val name: String)
```

`Kotlin`은 클래스, 특히 데이터만 있고 코드가 없는 클래스를 선언 하기 위한 간결한 구문을 제공한다. 또한 `Java`에서 `Kotlin`으로 변환하는 동안 `public` 수정자가 사라졌다. `Kotlin`에서는 공개가시자가 기본 가시성이므로 이를 생략할 수 있다.

### 2.2.1 데이터를 클래스로 관리하기

`Java`에서 데이터는 일반적으로 비공개인 필드에 저장된다. 클래스의 클 라이언트가 해당 데이터에 액세스할 수 있도록 해야 하는 경우 접근자 메서드(getter 및 setter)를 제공해야 한다. `Java`에서는 필드와 해당 접근자의 조합을 종종 프로퍼티라고 하며, 많은 프레임워크에서 이 개념을 많이 사용한다. `Kotlin`에서 프로퍼티는 필드와 접근자 메서드를 완전히 대체하는 일급 언어 기능을 제공한다. 

```kotlin
class Person(
	val name: String, // getter 제공
	var isStudent: Boolean  // getter, setter 제공
)
```

또한 호출시 프로퍼티를 호출함으로써 게터와 세터의 호출을 암묵적으로 가린다.

```kotlin
public class Demo {
    public static void main(String[] args) {
        Person person = new Person("Bob", true);
        System.out.println(person.getName());
        System.out.println(person.isStudent());
        person.setStudent(false);
        System.out.println(person.isStudent());
	}
}

fun main() {
    val person = Person("Bob", true)
    println(person.name)
    println(person.isStudent) )
    person.isStudent = false // setter 호출
    println(person.isStudent) // getter 호출
}
```

### 2.2.2 값을 저장하는 대신 프로퍼티를 계산 -> 사용자 정의 접근자

프로퍼티 중 하나인 사용자 정의 구현을 제공한다.

```kotlin
class Rectangle(val height: Int, val width: Int) { 
	val isSquare: Boolean
		get() {
          	return height == width
          }
}
```

위와 같은 사용자 정의 프로퍼티는 커스텀 게터와 동일하게 작동한다.

```kotlin
// Custom Getter
fun isIsquare() = height == width
```

보시다시피 표현식-본문 구문을 사용하면 속성 유형을 명시적으로 지정하지 않고 컴파일러가 대신 유형을 유추하도록 할 수 있다.

```kotlin
fun main() {
	val rectangle = Rectangle(41, 43) 	
    println(rectangle.isSquare) // false
}
```

> Q. 사용자 지정 게터를 사용하여 프로퍼티를 선언하는 것이 더 나은지 아니면 클래스 내부에서 함수를 정의하는 것이 더 나은지?(`Kotlin`에서는 멤버 함수 또는 메서드라고 함)
>
> A. 두 옵션 모두 구현이나 성능에는 차이가 없고 가독성만 다를 뿐 비슷하다. 일반적으로 클래스의 특성(속성)을 설명하는 경우 이를 프로퍼티로 선언한다. 클래스의 동작을 설명하는 경우 멤버 함수를 선택하라.

이후 4장에서는 클래스, 속성 및 멤버 함수를 사용하는 더 많은 예제를 살펴보고 생성자를 명시적으로 선언하는 구문을 살펴본다. 

### 2.2.3 Kotlin 소스 코드 레이아웃: 디렉터리 및 패키지

`Kotlin`은 패키지 개념을 사용하여 클래스를 구성한다(Java에서 익숙한 개념과 유사) 모든 `Kotlin` 파일은 시작 부분에 패키지문을 가질 수 있으며, 파일에 정의된 모든 선언(클래스, 함수 및 속성)은 해당 패키지에 배치된다.

```kotlin
package geometry.shapes

class Rectangle(val height: Int, val width: Int) { 
	val isSquare: Boolean
		get() = height == width
}

fun createUnitSquare(): Rectangle {
	return Rectangle(1, 1)
}
```

## 2.3 When 표현 및 열거형 

`Kotlin`에서 열거형을 선언하는 예제를 살펴보고 when 구문에 대해 이야기한다.

### 2.3.1 열거형 클래스 선언

```kotlin
enum class Color {
	레드, 오렌지, 옐로우, 그린, 블루, 인디고, 바이올렛
}


enum class Color( val r: Int, val g: Int, val b: Int) {
	red(255, 0, 0),
    oRANGE(255, 165, 0),
    YELLoW(255, 255, 0),
    green(0, 255, 0),
    blue(0, 0, 255),
	indigo(75, 0, 130),
    
    val RGB = (r * 256 + g) * 256 + b
	fun printColor() = println("$이것은 $rgb입니다") 
}

fun main() { 
	println(Color.BLUE.rgb) // 255
    Color.GREEN.printColor() // 녹색은 65280 
}
```

### 2.3.2 열거형 클래스를 처리하는 때 표현식 사용

```kotlin
fun getMnemonic(color: Color) =
    when (color) {
		Color.RED -> "리차드"
		Color.oRANGE -> "의"
		Color.YELLoW -> "요크"
		Color.GREEN -> "준"
		Color.BLUE -> "배틀"
		Color.INDIGo -> "인"
		Color.VIoLET -> "헛된" 
    }
    
fun getWarmthFromSensor(): String {
    val color = measureColor()
    
    return when(color) {
		Color.RED, Color.oRANGE, Color.YELLoW -> "따뜻함(빨강 = ${color.r})"
		Color.GREEN -> "중성(녹색 = ${color.g})"
		Color.BLUE, Color.INDIGo, Color.VIoLET -> "cold (blue = ${color.b})" }
}

fun main() { println(getMnemonic(Color.BLUE)) }
```

### 2.3.3 변수에서 when 표현식의 주어 캡처하기

```kotlin
fun measureColor() = oRANGE 

fun getWarmthFromSensor() =
	when (val color = measureColor()) {
		RED, ORNAGE, YELLOW -> "따뜻함(빨강 = ${color.r})" 		
        GREEN -> "중성(녹색 = ${color.g})"
        BLUE, INDIGo, VIoLET -> "cold (파란색 = ${color.b}" 
	}
```

### 2.3.4 임의의 객체와 함께 when 표현식 사용

```kotlin
fun mix(c1: Color, c2: Color) =
	when (setof(c1, c2)) {
		setof(RED, YELLoW) -> oRANGE
		setof(YELLoW, BLUE) -> GREEN 
		setof(BLUE, VIoLET) -> INDIGo
		else -> throw 예외("Dirty color") }

fun main() {
	println(mix(BLUE, YELLoW)) // 녹색
}
```

### 2.3.5 인수 없이 when 표현식 사용

```kotlin
fun mixoptimized(c1: Color, c2: Color) =
    when { 
    	(c1 == RED && c2 == YELLoW) || (c1 == YELLoW && c2 == RED) ->  oRANGE
		(c1 == YELLoW && c2 == BLUE) || (c1 == BLUE && c2 == YELLoW) -> 녹색
		(c1 == BLUE && c2 == VIoLET) || (c1 == VIoLET && c2 == BLUE) -> 인디고
		else -> throw Error("Dirty color")
}

fun main() {
	println(mixoptimized(BLUE, YELLoW))// 녹색 
}
```

### 2.3.6 스마트 캐스트: 유형 검사 및 캐스트 결합

```kotlin
fun eval(e: Expr): Int {
    if (e is Num) {
	val n = e as Num
        return n.value
    }
	if (e is Sum) {
    	return eval(e.right) + eval(e.left)
	}
    throw IllegalArgumentException("Unknown expression")
}

fun main() {
    println(eval(Sum(Sum(Num(1), Num(2)), Num(4))))
    // 7
}
```

변수 e가 Num 타입인지 확인하면 컴파일러는 이를 Num 타입의 변수 로 스마트하게 해석한다. 스마트캐스트는 `is` 검사 후 변수가 변경될 수 없는경우에만 작동한다.

### 2.3.7 리팩터링: if를 when 표현식으로 바꾸기

```kotlin
fun eval(e: Expr): Int =
	if (e is Num) { 
    	e.value
    } else if (e is Sum) {
        eval(e.right) + eval(e.left)
	} else {
		throw IllegalArgumentException("알 수 없는 식") 
	}

fun main() {
	println(eval(Sum(Num(1), Num(2)))) // 3
}
```

위와 같은 if문을 when으로 바꾸면 더 간결하게 읽을 수 있다.

```kotlin
fun eval(e: Expr): Int =
when (e) {
	e is Num -> e.value
	e is Sum -> eval(e.right) + eval(e.left)
	else -> throw IllegalArgumentException("알 수 없는expr") }
```

### 2.3.8 if 및 when의 분기로서의 블록

`if`와 `when` 모두 블록을 분기로 가질 수 있다.이 경우 블록의 마지막표현식이 결과가 된다. 함수가 결과를 반환하면 재귀함수 때 유리함으로 함수가 재귀를 제공해야할 때 when문을 활용하는 것을 권장한다.

```kotlin
fun evalWithLogging(e: Expr): Int =
 	when (e) {
		e is Num -> {
			println("num: ${e.value}") e.value
		}
		e is Sum -> {
			val left = evalWithLogging(e.left) 
            val right = evalWithLogging(e.right) 
            println("sum: $left + $right") 			
		}
		else -> throw IllegalArgumentException("알 수 없는 표현식")
}

fun main() {
	println(evalWithLogging(Sum(Sum(Num(1), Num(2)), Num(4)))) // 7
}
```

## 2.4 반복: While과 for 루프

`Kotlin`의 반복은 `Java`, `C`# 또는 다른 언어에서 익숙한 반복과 매우 유사하다.

### 2.4.1 조건이 참인 동안 코드 반복: While 루프

```kotlin
do {
	if (shouldSkip) continue
	/*...*/
} while (condition)

outer@ while (outerCondition) {
    while (innerCondition) {
		if (shouldExitInner) break
		if (shouldSkipInner) continue
    	if (shouldExit) break@outer
		if (shouldSkip) continue@outer // ...
	}
	// ...
}
``` 

바깥쪽에 레이블을 선언하여 특정 레이블로 점프를 할 수 있다. 레이블이 없으면 항상 가장 가까운 루프에서 작동한다.

### 2.4.2 숫자 반복하기: 범위 및 진행

고전적인 다음 방법을 사용하지 않고 `(int i = 0; i < 10; i++)` 코틀린에서는 좀 더 우아하게 `0..10`이라 표현한다.

```kotlin
val oneToTen = 1..10

fun main() {
    for (i in 1..100) {
		print(fizzBuzz(i)) 
	}
}
```

`withIndex`함수를 활용하여 인덱스도 동시에 활용할 수 있다.

```kotlin
fun main() {
val list = listof("10", "11", "1001")
for ((index, element) in list.withIndex()) {
        println("$index: $element")
		// 0: 10 // 1: 11 // 2: 1001
    }
}
```

### 2.4.4 in를 사용하여 컬렉션 및 범위 확인

`in`연산자는 범위 내 유효성을 확인한다.

```kotlin
fun isLetter(c: Char) = c in 'a'...'z' || c in 'A'...'Z'
fun isNotDigit(c: Char) = c !in '0'...'e'

fun main() { 
	println(isLetter('q')) // true
    println(isNotDigit('x')) // true
}
```

`when`과 함께 사용될 수도 있다.

```kotlin
fun recognize(c: Char) = when (c) {
	in '0'...'e' -> "숫자다!"
	in 'ᄀ'...'ᄌ', 'ᄀ'...'ᄌ' -> "글자야!" 
    else -> "모르겠어..." 
 }
```

## 2.5 Kotlin에서 예외 던지기 및 잡기

Kotlin의 예외 처리는 Java 및 기타 여러 언어에서 예외를 처리하는 방식과 유사하다.

```kotlin

fun readNumber(reader: BufferedReader): Int? {
    try {
    	val line = reader.readLine()
		return Integer.parseInt(line)
	} catch (e: NumberFormatException) { 
        return null
    } finally {
        reader.close()
    }
}

fun main() {
    val reader = BufferedReader(StringReader("239"))
    println(readNumber(reader))
    // 239
}
```

다른 많은 최신 `JVM` 언어와 마찬가지로 `Kotlin`은 확인된 예외와 확인되지 않은 예외를 구분하지 않는다. 함수가 던지는 예외를 지정하지 않으며, 예외를 처리할 수도 있고 처리하지 않을 수도 있다. 

이러한 설계 결정은 `Java`에서 검사된 예외 를 사용하는 관행을 기반으로 한다. 경험에 따르면 `Java` 규칙은 예외를 다시 던지 거나 무시하기 위해 의미 없는 코드를 많이 필요로 하는 경우가 많으며, 규칙이 발생 할 수 있는 오류로부터 사용자를 일관되게 보호하지 못한다는 사실이 밝혀졌기 떄문이다.

이러한 설계 결정의 결과로 어떤 예외를 처리할지, 처리하지 않을지 직접 결정할 수 있습니다. 원한다면 다음 목록과 같이 `try-catch` 구문을 전혀 사용하지 않고 `readNumber` 함수를 구현할 수 있다.


### 2.5.2 try를 표현식으로 사용

```kotlin
fun readNumber(reader: BufferedReader) {
    val number = try {
		Integer.parseInt(reader.readLine()) 
	} catch (e: NumberFormatException) {
		return  
    }
	println(number) 
}

fun main() {
	val reader = BufferedReader(StringReader("숫자 아님"))
	readNumber(reader)
}
```

`try`는 `if` 및 `when`과 마찬가지로 표현식이므로 예제를 약간 수정하여 이를 활용하고 `try` 표현식의 값을 변 수에 할당할 수 있다

## 요약

- fun 키워드는 함수를 선언하는 데 사용된다다. 	
   - `val` 및 `var` 키워드는 각각 읽기 전용 및 변경 가능한 변수를 선언.
- 값 참조는 읽기 전용이지만 참조가 가리키는 객체는 여전히 변경 가능할 수 있다.
- 문자열 템플릿을 사용하면 시끄러운 문자열 연결을 피할 수 있습니다. 
   - 변수 이 름에 접두사 $를 추가하거나 ${}로 표현식을 둘러싸면 해당 값이 문자열에 삽입됨
- Kotlin에서는 클래스를 간결한 방식으로 표현할 수 있다.
  - named argument
  - default argument
  - property 개념 + backing property
- `if`는 이제 반환값이 있는 표현식이다.
- `when` 표현식은 `Java`의 `switch`와 유사하지만 더 강력하다.
- 컴파일러가 스마트 형변환을 사용하여 자동으로 형변환하기 때문에 변수에 특정 유형이 있는지 확인한 후 명시적으로 형변환할 필요가 없다.
- `for`, `while` 및 `do-while` 루프는 `Java`의 해당 루프와 유사하지만, 특히 인덱스가 있는 맵이나 컬렉션을 반복해야 할 때 `for` 루프가 더 편리하다.
- 구문 (`1..5`)는 범위를 생성합니다. 범위를 사용하면 `Kotlin`에 서루프에 대해 통일된 구문과 추상화 집합을 사용할 수 있으며 값이 범위에 속하는지 확인하는 `in` 및 `!.in` 연산자와 함께 유용하게 작동한다.
- `Kotlin`의 예외 처리는 `Java`와 매우 유사하지만, 함수가 던질 수 있는 예외를 선언할 필요가 없다는 점을 제외하면 `Kotlin`에서는 예외를 선언하지 않아도 된다.

