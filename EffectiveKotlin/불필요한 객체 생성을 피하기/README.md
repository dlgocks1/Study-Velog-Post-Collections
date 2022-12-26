# 효율성에 대한 관점

오늘날의 코드는 `효율성`을 관대하게 바라본다. 그이유는 메모리가 너무 저렴해졌고, 개발자는 비싸졌기 때문이다.

> **무어의 법칙**
> 마이크로칩 기술의 발전 속도에 관한 일종의 법칙으로 마이크로칩에 저장할 수 있는 데이터 분량이 18-24개월 마다 두 배씩 증가한다는 법칙이다

마이크로 칩은 고작 9년 사이에 용량이 128MB에서 128GB로 1000배나 올랐다!
![](https://velog.velcdn.com/images/cksgodl/post/8ef23e51-bd2d-4f77-a9dd-357ded2f7aa3/image.png)

---

하지만 어떤 애플리케이션이 수백 만 대의 장치에서 실행된다면 배터리 사용을 조금만 최적화해도 작은 마을에 공급할 수 있을만큼의 에너지를 절약할 수 있을 것이다.

가독성과 성능 사이에는 트레이드 오프가 발생하며, 개발자는 무엇이 더 중요한지 스스로 답할 수 있어야 한다.

# 불필요햔 객체 생성을 피하라

객체의 생성은 언제나 비용이 들어간다. 따라서 불필요한 객체 생성을 비팧는 것은 최적화의 관점에서 필요하다.

JVM에서는 하나의 가상 머신에서 동일한 문자열을 처리하는 코드가 여러개 있다면 기존의 문자열을 재사용한다.

```
val str1 = "해찬이가 노래한다 홍홍홍"
val str2 = "해찬이가 노래한다 홍홍홍"

println(str1 == str2) // true
println(str1 === str2) // true
```

`Integer`와 `Long`처럼 박스화한 기본 자료형도 작은 경우에는 재사용된다(기본적으로 Int는 -128~127 범위 내의 숫자는 캐쉬된다.

```
val j1: Int? = 100
val j2: Int? = 100

println(j1 == j2) // true
println(j1 === j2) // true
```

참고로 `nullable` 타입은 `int`자료형 대신 `Integer` 자료형을 사용하게 강제된다. `Int`를 사용하면, 일반적으로 기본 자료형 `int`로 컴파일 된다.

> 추가) 상수는 언제 추출하여야 하는가?

```
const val USER_LENGTH = 5
```

1. 값이 변경되지 않는 다는 것을 미리 공지할 때 (또는 코드를 변경해야 할 때 일괄적으로 해당 코드를 바꾸기 위해)

2. 바뀌지 말아야할 값을 명시적으로 선언하여 실수로 변경하지 않도록 방지할 때

3. 변수는 런타임시 필요할 때 선언되지만, 상수는 초기 1회 컴파일시 생성되고 더이상 선언하지 않아도 된다. (`Int`형은 -128~127 사이의 값만 캐쉬한다.)

## 객체 생성 비용은 항상 클까?

어떤 객체를 랩(wrap)하면, 크게 세 가지 비용이 발생한다.

- 64비트 JDK에서는 객체는 8바이트의 `배수`만큼 공간을 차지한다. 앞부분 12바이트는 헤더로서 반드시 있어야 하므로, 최소 크기는 16바이트이다. (32비트 JVM에서는 8바이트) 추가적으로 객체에 대한 레퍼런스도 공간을 차지한다. 64비트 플랫폼의 32G(-Xmx32G)는 8바이트이다. 정수처럼 작은 것들을 많이 사용하면, 그 비용의 차이가 더 커진다. 기본 자료형 `int`는 4바이트지만, 오늘날 널리 사용되고 있는 64비트 JDK의 랩되어 있는 `Integer`은 16바이트이다. 추가로 이에 대한 레퍼런스로 인해 8바이트가 더 필요하다.

- 요소가 캡슐화되어 있다면, 접근에 추가적인 함수 호출이 필요하다.

- 객체는 생성되어야 한다. 객체는 생성되고, 메모리 영역에 할당되고, 이에 대한 레퍼런스를 만드는 작업이 필요하다.

객체를 제거함으로써 이런 세 가지 비용을 모두 피할 수 있다. 특히 객체를 재사용하면 첫 번째와 세 번째에 설명한 비용을 제거할 수 있다. 어떠한 방식으로 불필요한 객체를 제거해야 할까?

## 객체 선언

매 순간 객체를 선언하지 않고, 객체를 재사용하는 간단한 방법은 싱글톤객체를 사용하는 것이다.

#### 링크드 리스트 예제를 살펴보자

```
sealed class LinkedList<T>

class Node<T>(
    val head: T,
    val tail: LinkedList<T>
) : LinkedList<T>()

class Empty<T> : LinkedList<T>()

val list1 = Node(1, Node(2, Node(3, Empty())))
val list2 = Node("A", Node(5, Empty()))
```

이러한 링크드리스트의 문제점을 뽑으라면, 리스트를 만들 때마다 Empty() 인스턴트를 만드는 것이다. 이 Empty()객체를 한번 선언하고 재사용하면 어떨까? 하지만 제네릭 타입이 일치하지 않아서 문제가 될 수 있다. 이 때는 `Nothing`리스트를 만들어서 사용하면 된다. `Nothing`은 모든 타입의 서브타입이다. 따라서 `LinkedList<Nothing>`은 리스트가 `convariant(out 한정자)`라면 모든 `LinkedList`의 서브타입이 된다. 리스트는 `immutable`이고, 이 타입은 out 위치에서만 사용되므로, 현재 상황에서는 타입 아규먼트를 `covariant`로 만드는 것은 의미 있는 일이다.

개선된 코드는 다음과 같다.

```
sealed class LinkedList<out T>

class Node<T>(
    val head: T,
    val tail: LinkedList<T>
) : LinkedList<T>()

object Empty : LinkedList<Nothing>()

fun main() {
    val list1 = Node(1, Node(2, Node(3, Empty)))
    val list2 = Node("A", Node(5, Empty))
}
```

이러한 방식은 `immutable sealed 클래스`를 정의할 때 자주 사용된다. 만약 `mutable`객체에 사용하면 공유 상태 관리와 관련된 버그를 검출하기 어려울 수 있다.

## 캐쉬를 활용하는 팩토리 함수

객체는 생성자를 사용해서 만들지만, 팩토리 메서드를 사용해서 만드는 경우도 있다.

> 팩토리 함수는 캐시를 가질수 있다.

그래서 팩토리 함수는 항상 같은 객체를 리턴하게 만들 수 있다.실제로 `stdlib`의 `emptyList`는 이를 활용해 구현이 되어 있다.

```
fun <T> emptyList(): List<T> = EmptyList
```

[우테코 프리코스 3주차](https://velog.io/@cksgodl/%EC%9A%B0%ED%85%8C%EC%BD%94-%EC%95%88%EB%93%9C%EB%A1%9C%EC%9D%B4%EB%93%9C-3%EC%A3%BC%EC%B0%A8-%ED%86%BA%EC%95%84%EB%B3%B4%EA%B8%B0)에서도 로또를 생성할 때 로또번호를 객체로 만들어 이를 캐싱할 수 있었다.

```
class LottoNumber(private val number: Int) {

    companion object {
        private val CACHED_LOTTO_NUMBER = List(MAX_LOTTO_NUM) { idx ->
            LottoNumber(idx + 1)
        }

        fun valueOf(number: Int): LottoNumber {
            validationNumber(number)
            return CACHED_LOTTO_NUMBER[number - 1]
        }
    }
}
```

이와 연관된 개념으로 `경량 패턴`이라는 개념이 있다.

> 경량 패턴이란?
> 한개의 고유 상태를 다른 객체들에서 공유하게 만들어 메모리 사용량을 줄이는 것

![](https://velog.velcdn.com/images/cksgodl/post/4ddf34ce-0820-43bf-988d-29f03d2d2536/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/aeac92a6-a3a7-4e43-ae63-9151e20dd940/image.png)

1~45까지의 로또번호라는 객체를 생성하고 이를 다른 로또에게 공유해 메모리 사용량을 줄일 수 있다. 이를 위해 팩토리 생성자가 필요하며 싱글톤을 이용해 초기에 모든 객체를 메모리에 넣어야 하기 때문에 초기 컴파일은 느릴 수 있다. 하지만 이렇게 생성된 객체를 재사용하면 GC에 의한 메모리 단편화현상을 방지할 수 있다.

연관 키워드 : `객체 풀`, `오브젝트 풀`, `커넥션 풀` 등 등

---

형인자(parameterized) 팩토리 메서드도 캐싱을 활용할 수 있다. 위에서 로또 번호를 저장한것과 같이 객체를 다음과 같이 map에 저장해 둘 수 있을 것이다.

```
private val connections = mutableMapOf<String, Connection>()

fun getConnection(host: String) = connections.getOrPut(host) { createConnection(host) }
```

모든 순수 함수는 캐싱을 활용할 수 있다. 이를 메모이제이션이라고 부른다.

> 메모이제이션은 주어진 입력값에 대한 결과를 저장함으로써 같은 입력값에 대해 함수가 한 번만 실행되는 것을 보장한다(보통 딕셔너리에 저장한다).
> 이는 동적계획법의 핵심이 되는 기술로 알고리즘, 코딩테스트에서 유용하게 사용된다.

다음 예는 피보나치 수를 동적계획법을 활용하여 구하는 함수이다.

```
private val FIB_CAHCE = mutableMapOf<Int, BigInteger>()

fub fib(n: Int): BigInteger = FIB_CAHCE.getOrPut(n) {
	if ( n<=1 ) BigInteger.ONE else fib(n-1) + fib(n-2)
}
```

하지만 이러한 방식도 문제가 있다. 더 많은 메모리를 사용하게 된다는 것이다.

메모리 문제로 충돌이 생기면 가비지 컬렉터가 자동으로 메모리를 해제해 준다. 메모리가 필요할 때 자동으로 메모리를 해제해 주는 `SoftReference`를 사용하면 더 좋다.

- WeakReference란?
  가비지 컬렉터가 값을 정리(clean)하는 것을 막지 않는다. 다른 레퍼런스가 이를 사용하지 않으면 곧바로 제거된다.

- SoftReference란?
  가비지 컬렉터가 값을 정리할 수도 있고, 정리하지 않을 수도 있다. 일반적인 JVM의 경우 메모리가 부족할 경우에만 정리한다. 따라서 캐시를 만들 때는 SoftReference를 사용하자.

캐시는 메모리와 성능의 트레이드 오프가 발생함으로, 캐시를 잘 설계하는 것은 쉽지 않다. 여러 상황을 잘 고려해서 현명하게 사용하자.

## 무거운 객체를 외부 스코프로 내보내기

성능 개선을 위한 유용한 트릭으로, 무거운 객체를 외부 스코프로 보내는 방법이 있다. 컬렉션 처리에서 이루어지는 무거운 연산은 컬렉션 처리 함수 내부에서 외부로 빼는 것 이좋다.

```
fun <T : Comparable<T>> Iterable<T>.countMax(): Int {
    return count { it == this.maxOrNull() }
}
```

```
fun <T : Comparable<T>> Iterable<T>.countMax(): Int {
    val max = this.maxOrNull()
    return count { it == max }
}
```

두 함수의 차이를 알겠는가? 처음 `max`값을 찾아 두고, 이를 활용해 수를 센다. 리시버로 바로 `max`를 호출하는 형태가 보임으로 가독성이 향상되고, `max`값을 한번만 호출하기 때문에 성능이 좋다.

또한 다음 패스워드를 체크하는 정규식을 보자

```
fun String.isValidPassword(): Boolean {
    return this.matches("^(?=.*[A-Za-z])(?=.*\\d)(?=.*[@\$!%*#?&])[A-Za-z\\d@\$!%*#?&]{8,}\$".toRegex())
}
```

이 함수의 문제는 함수를 호출할 때마다 Regex 객체를 계속해서 새로 만든다는 것이다. 정규 표현식을 톱레밸로 보내면 이런 문제는 사라진다.

```
private val IS_VALID_PASSWORD_REGEX = "^(?=.*[A-Za-z])(?=.*\\d)(?=.*[@\$!%*#?&])[A-Za-z\\d@\$!%*#?&]{8,}\$".toRegex()

fun String.isValidPassword(): Boolean {
    return this.matches(IS_VALID_PASSWORD_REGEX)
}
```

한 파일에 다른 함수와 함께 있을 때, 해당 함수를 사용하지 않는다면 정규 표현식이 만들어지는 것 자체가 낭비이다. 이러한 경웬는 `지연 초기화`를 활용하자.

```
private val IS_VALID_PASSWORD_REGEX by lazy {
    "^(?=.*[A-Za-z])(?=.*\\d)(?=.*[@\$!%*#?&])[A-Za-z\\d@\$!%*#?&]{8,}\$".toRegex()
}
```

## 지연 초기화

무거운 클래스를 만들 때는 지연되게 만드는 것이 좋다. 예를들어 A 클래스에 B, C, D라는 무거운 인스턴트가 필요하다고 가정해 보자. 클래스를 생성할 때 이를 모두 생성한다면, A 객체를 생성하는 과정이 무거워질 것이다.

```
class A{
    val b = B()
    val c = C()
    val d = D()
}
```

내부에 있는 인스턴스들을 지연 초기화하면 A라는 객체를 생성하는 과정을 가볍게 만들 수 있다.

```
class A {
    val b by lazy { B() }
    val c by lazy { C() }
    val d by lazy { D() }
}

fun main() {
    val a = A() // b, c, d 모두 생성되지 않음
    a.b.print()
    a.c.print()
    a.d.print()
}
```

실행결과

```
B was Created
Im B
C was Created
Im C
D was Created
Im D
```

하지만 이러한 지연 초기화도 단점을 가진다.

> 무거운 객체를 가졌지만, 메서드의 호출은 빨라야 하는 경우가 있을 수 있다.

A가 HTTP호출에 응답하는 백엔드 어플리케이션의 컨트롤러라고 생각해보자. 백엔드 어플리케이션은 전체적인 실행 시간은 중요하지 않은데, 이렇게 지연되게 만들면, 첫 번째 호출 때 응답 시간이 굉장히 길어질 수 있다.
또한 이러한 지연 초기화는 성능 테스트를 복잡하게 만든다.

## 기본 자료형 사용하기

JVM은 숫자와 문자 등의 기본적인 요소를 나타내기 위한 특별한 기본 내장 자료형을 가지고 있다. 이를 `기본 자료형(primitives)`라고 한다. 코틀린/JVM 컴파일러는 내부적으로 최대한 이러한 기본 자료형을 사용한다. 다만 다음과 같은 두 가지 상황에는 기본 자료형을 랩(wrap)한 자료형이 사용된다.

1. nullable한 타입을 연산할 때(기본 자료형은 null일 수 없다.)
2. 타입을 제네릭으로 사용할 때

```
Kotlin.Int == java.int
Kotlin.Int? == Java.Integer
Kotlin.List<Int> == Java<Integer>
```

랩한 자료형 대신 기본 자료형을 사용하게 코드를 최적화 해야 한다. 이런 코드의 최적화는 숫자에 대한 작업이 여러 번 반복되어야(큰 컬렉션을 처리할 때) 의미가 있다.

라이브러리의 성능이 굉장히 중요한 부분에서만 이를 적용하자.

## 정리

객체를 생성하는 것은 비용과 시간이 든다. 캐싱을 하면 시간을 줄일 수 있지만 비용이 늘어나고, 하지 않으면 시간이 늘어나지만 비용이 줄어든다. 주어진 상황에 맞추어 캐싱을 잘 설계하자

객체를 캐싱하는 것은 성능을 향상시키는 것 외에도 가독성을 향상 시켜주는 장점도 있다. 예를 들어 `무거운 객체를 외부 스코프로 보내기`는 성능도 향상시키고, 객체에 이름을 붙여 함수 내부에서 사용하므로 가독성이 올라간다.
