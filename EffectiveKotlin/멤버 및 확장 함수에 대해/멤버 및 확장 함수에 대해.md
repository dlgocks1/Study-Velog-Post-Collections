# API의 필수적이지 않는 부분을 확장함수로 추출하라

클래스의 메서드를 정의할 때는 메서드를 멤버로 정의할 것인지, 확장 함수로 정의할 것인지 결정해야 한다.

```
class Workshop(/* .. */) {
	// ...

    fun makeEvent(date: DateTime): Event == //..

    val permalink
    	get() = "/workshop/$name"
}

// 확장 함수
fun Workshop.makeEvent(date: DateTime): Event = //...

val Workshop.permalink
	get() = "/workshop/$name"
```

두 가지 방법은 거의 비슷하고, 호출하는 방법도 비슷하고, 리플렉션으로 레퍼런싱하는 방법도 비슷하다.

또한 두 가지 방식 중 어떤 것이 우월하다고 할 수는 없다. 장단점을 모두 갖고있으니 상황에 맞게 사용해야 한다.

멤버와 확장의 가장 큰 차이점은 확장은 따로 가져와서 사용해야 한다는 것이다. 그래서 일반적으로 확장 다른 패키지에 위치한다. 확장은 우리가 직접 멤버를 추가할 수 없는 경우,

> 즉 데이터와 행위를 분리하도록 설계된 프로젝트에서 사용된다.

확장은 같은 타입에 같은 이름으로 여러 개를 만들 수도 있다. 따라 여러 라이브러리에서 여러 메서드를 받을 수있고, 충돌이 발생하지 않는다. 하지만, 같은 이름으로 다른 동작을 하는 멤버함수가 혼돈을 야기할 수 있다.

확장은 가상`(virtual)`이 아니라는 것이다. 즉 파생 클래스에서 오버라이드할 수 없다. 확장 함수는 컴파일 시점에 정적으로 선택된다. 확장 함수는 가상 멤버 함수와 다르게 동작한다. 상속을 목적으로 설계된 요소는 확장 함수로 만들면 안된다.

```
open class C
class D : C()

fun C.foo() = "c"
fun D.foo() = "d"

fun main() {
    val d = D()
    println(d.foo()) // d
    val c: C = d
    println(c.foo()) // c

    println(D().foo()) // d
    println((D() as C).foo()) // c
}
```

> 이러한 차이는 확장 함수가 `첫 번째 아규먼트로 리시버가 들어가는 일반 함수`로 컴파일되기 때문에 발생되는 결과이다.

```
fun foo(`this$receiver`: C) = "c"
fun foo(`this$receiver`: D) = "d"

fun main() {
    val d = D()
    println(foo(d))
    val c: C = d
    println(foo(c))

    println(foo(D())) // d
    println(foo((D() as C))) // c
}
```

추가로 확장 함수는 클래스가 아닌 타입에 정의하는 것이다. 그래서 nullable 또는 구체적인 제네릭 타입에도 확장 함수를 정의할 수 있다.

```
public fun Iterable<Int>sum(): Int { /*...*/ }
```

## 정리

멤버와 확장 함수의 차이를 비교하면 다음과 같다.

1. 확장 함수는 읽어 들여야 한다.
2. 확장 함수는 virtual이 아니다. (첫번째 리시버로 들어가게됨)
3. 멤버는 높은 우선 순위를 가진다. (이름이 같으면 멤버함수)
4. 확장 함수는 클래스 위가 아니라 타입 위에 만들어진다.
5. 확장 함수는 클래스 레퍼런스에 나오지 않는다.

확장은 더 많은 자유와 유연성을 주지만, 이는 상속, 어노테이션처리를 지원하지 않고 클래스 내부에 없으므로 혼동을 줄 수 있다.

> API의 필수적인 부분은 멤버로 두는 것이 좋지만, 필수적이지 않은 부분은 확장 함수로 만드는 것이 여러모로 좋다.

# 멤버 확장 함수의 사용을 피하라

어떤 클래스에 대한 확장 함수를 정의할 때, 이를 멤버로 추가하는 것은 좋지 않다. 확장함수는 첫 번째 아규먼트로 리시버를 받는 단순한 일반 함수로 컴파일된다.

예를들어 다음함수는 컴파일되면

```
fun String.isPhoneNUmber(): Boolean = length == 7 && all { it.isDigit() }
```

다음과 같이 변하게 된다.

```
fun isPhoneNUmber(`receiver$this`: String): Boolean =
    `receiver$this`.length == 7 && `receiver$this`.all { it.isDigit() }
```

이렇게 단순하게 변환되는 것이므로, 확장 함수를 클래스 멤버로 정의할 수도 있고, 인터페이스 내부에 정의할 수도 있다.

```
interface PhoneBook {
    fun String.isPhonumber(): Boolean // 인터페이스 내부에 정의한 확장 함수
}

class Fizz : PhoneBook {
    override fun String.isPhonumber(): Boolean =
        length == 7 && all { it.isDigit() }

}
```

이런 코드가 가능하지만, DSL을 만들 때를 제외하면 이를 사용하지 않는 것이 좋다. 특히 가시성 제한을 위해 확장 함수를 멤버로 정의하는 것은 굉장히 좋지 않다.

```
class PhoneBook {
    fun String.isPhonumber(): Boolean =
        length == 7 && all { it.isDigit() }
}

fun main() {
    PhoneBook().apply { "1234123".isPhonumber() } // PhoneBook 클래스내에서만 함수에 접근 가능
}
```

확장 함수의 가시성을 제한하고 싶다면, 멤버로 만들지 말고 가시성 한정자를 붙여주자

```
private fun String.isPhoneNUmber(): Boolean = length == 7 && all { it.isDigit() }
```

또한 암묵적 접근을 할 때, 두 리시버 중에 어떤 리시버가 선택될지 혼동된다.

```
class A {
    val a = 10
}

class B {
    val a = 20
    val b = 30
    fun A.test() = a + b
}

B().apply {
	println(A().test()) // 40
}
```

또한 확장 함수가 외부에 있는 다른 클래스를 리시버로 받을 때, 해당 함수가 어떤 동작을 하는지 명확하지 않다.

```
class A {
	// ...
}

class B {

    // ...
    fun A.update() = //.. 무슨일을 할까?
}
```

## 정리

멤버 확장 함수를 사용하는 것이 의미가 있는 경우에는 사용해도 괜찮다. 하지만 일반적으로는 그 단점을 인지하고, 사용하지 않는 것이 좋다. 가시성을 제한하려면 한정자를 붙이자.
