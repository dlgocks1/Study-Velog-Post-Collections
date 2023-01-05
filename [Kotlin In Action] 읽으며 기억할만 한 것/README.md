> Kotlin In Action은 2017년도에 만들어진 책으로 내용이 오래되었고 친절하지 않는다. 수많은 내용이 있지만 나에게 기억이 남으면 좋을 내용들을 정리해 보았다.

# 1. 코틀린이란?

- 타입 추론을 지원하는 정적 타입 지정언어이다. 소스코드의 정확성과 성능을 보장하며, 소스코드를 간결하게 유지한다.

- 객체지향과 함수형 프로그래밍 스타일을 모두 지원한다.

- 실용적이며, 안전하고, 간결하며, 상호운용성이 좋다. `NullPointerException`과 같은 흔히 발생하는 오류를 방지하며, 읽기 쉽고 간결한 코드를 지원하면서 자바와 아무런 제약 없이 통합될 수 있다.

# 2. 코틀린 기초

- `val`, `var`은 각각 읽기 전용 변수와 변경 가능한 변수를 선언할 때 사용한다.

- 문자열 템플릿을 활용하자.

- 코틀린의 `when`은 자바의 `switch`보다 간결하고 강력하다.

- 한번 변수의 타입을 검사하면 이후 캐스팅이 필요가 없다.(스마트캐스팅)

- `1..5`와 같은 식은 범위를 만들어낸다. 범위에 들어있는지 검사하기 위해 `in`이나 `!in`을 활용한다.

- 코틀린은 프로퍼티를 언어 기본 기능으로 제공하며, 게터와 세터를 자동으로 구현한다.
  또한 커스텀 접근자를 수정할 수도 있다.

# 3. 함수 정의와 호출

- 이름있는 아규먼트를 활용하자

- 디폴트 파라미터 값을 활용하자

- 코틀린은 자신만의 컬렉션을 제공하지 않는다.

```
println(set.javaclass) // class java.util.Hashset

println(list.javaclass) // class java.util.ArrayList

println(map.javaclass) // class java.util.HashMap

println(MutableList(1) { 0 }.javaClass) // class java.util.ArrayList

println(Array(1) { 0 }.javaClass) // class [Ljava.lang.Integer;
```

모두 자바 컬렉션으로 이루어져 있으며 이는 자신만의 컬렉션을 제공하지 않는다는 뜻이다

하지만 `last()`, `first()`, `filter`등과 같은 컬렉션 API를 제공한다. 그 이유는 확장함수이다.

## 확장 함수

자바 컬렉션에 대한 확장함수를 선언하여 코틀린만의 컬렉션 선언없이도 여러 API를 제공한다.

```
// 확장함수의 예
fun String.lastChar(): Char = this.get(this.length - 1)
```

확장함수는 멤버 메소드인 것 처럼 호출하지만, 클래스 밖에 선언된 함수이다. 확장 함수를 만들기 위해서는 확장할 클래스의 이름을 덧붙이기만 하면된다.

- String -> `수신 객체 타입`
- this -> `수신 객체`

`String`클래스를 직접 작성하지 않고, 소스코드를 보유하지도 않았지만 원하는 메소드를 해당 클래스에 추가할 수 있다!

> 확장함수를 남발하여 이름이 겹치지 않게 조심하자.
> 이름을 바꿔 임포트하거나, 전체 이름을 사용할 수 있지만 이는 좋은 방법이 아니다.

```
public fun <T> List<T>.last(): T { // 확장함수로 리스트에 API를 덧붙이고 있다.
    if (isEmpty())
        throw NoSuchElementException("List is empty.")
    return this[lastIndex]
}
```

### 확장함수는 오버라이드 불가능

확장함수는 오버라이드가 불가능하다. 이것이 무슨뜻이냐면

```
open class View {
	open fun click = println("Im View!")
}

class Button: View() {
	overrid fun click() = println("Im Button!")
}
```

다음과 같은 클래스가 있을 때

```
View().click() // Im View!
Button().click() // Im Button!

val view: View = Button()
view.click() // Im Button!
```

함수가 오버라이딩되는 것은 당연하다.

하지만 확장함수는 클래스의 일부가 아니다. 클래스 밖에 선언되는 확장함수의 특성상 이런 오버라이드가 허용되지 않는다. 수신 객체로 지정한 변수의 정적 타입에 의해 어떤 확장함수가 호추로딜지 결정된다. (동적 타입에 확장함수가 의존하지 않음)

```
fun View.showOff() = println("Im a View!")
fun Button.showOff() = println("im a Button!")

val view: View = Button()
view.click() // Im View!
```

---

## 최상위 함수

자바에서는 모든 함수를 클래스의 메소드로 작성해야 한다. 하지만 이로 인해 중복된 일을 수행하는 클래스내 함수가 겹칠 수 있고, 많이 사용되지 않는 API를 위해 크기를 늘리는 일이 있을 수도 있다.

> 코틀린은 이런 무의미한 클래스가 필요없다. 함수를 최상위 수준에 위치시키면 이 함수를 언제 어디서나 임포트하여 사용할 수 있기 때문이다.

```
fun joinToString() { /* .. */ }
```

코틀린은 JVM기반으로 돌아가는데 어떻게 이게 가능할까? 디컴파일해보자.

```
// In Join.kt
fun joinToString() {
    println("Hello!")
}

// Decompile
public final class JoinKt {
   public static final void joinToString() {
      String var0 = "Hello!";
      System.out.println(var0);
   }
```

최상위 함수를 디컴파일할 때 해당 소스가 있는 파일이름을 기반으로 새로운 클래스를 정의한다. 코틀린의 모든 최상위 함수는 이 클래스의 정적인 메소드가 된다. 즉 임포트하여 사용할 수 있다는 것

```
JoinKt.joinToString() // 사용가능
```

---

## 최상위 프로퍼티

코틀린에서는 프로퍼티도 파일의 최상위 수준에 놓을 수 있다. 또 디컴파일 해보자.

```
// In Join.kt
private val imTopProperty = "Hello!"

// Decompile
public final class JoinKt {
   private static final String imTopProperty;

   static {
      imTopProperty = "Hello!";
   }
}
```

최상위 함수와 동일하게 `JoinKt`클래스의 변수로 사용되는 것을 볼 수 있다. 또한 이런 프로퍼티는 `static`으로 정적필드에 저장되며, `const val`한정자를 붙여

`private static final String imTopProperty = "Hello!";`

public static final 필드로 컴파일하게 만들 수 있다.
