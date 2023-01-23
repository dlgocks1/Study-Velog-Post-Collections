컬렉션에 공부하기전

### 컬렉션(Collection)과 배열(Arrays)의 차이란?

[Difference between List and Array types in Kotlin - stackoverflow](https://stackoverflow.com/questions/36262305/difference-between-list-and-array-types-in-kotlin) (코틀린에서 리스트와 어레이 타입의 차이점은 무엇인가요??)

- `Array<T>`는 고정 사이즈 메모리를 참조하며 데이터를 저장하는 객체이다.(JVM에서 `Java array`를 나타냄)
  `List<T>` 와 `MutableList<T>`는 `ArrayList<T>`와 `LinkedList<T>`가 상속받는 인터페이스 중 하나이다.

```
public class ArrayList<E> extends AbstractList<E>
        implements List<E>, RandomAccess, Cloneable, java.io.Serializable
```

- `Array<T>`는 `mutable`하며 `List<T>`는 `immutable`하다. 읽기 전용 콜랙션이며 수정하려면 `MutableList<T>`를 사용해야 한다.

```
val a = arrayOf(1, 2, 3)
a[0] = a[1] // OK

val l = listOf(1, 2, 3)
l[0] = l[1] // doesn't compile

val m = mutableListOf(1, 2, 3)
m[0] = m[1] // OK
```

- `Array<T>`는 크기가 고정되어 있으므로, 크기를 늘리거나 축소할 수 없다. `List<T>`의 경우 사이즈를 늘릴 수 있다.

```
val a = arrayOf(1, 2, 3)
println(a.size) // will always be 3 for this array

val l = mutableListOf(1, 2, 3)
l.add(4)
println(l.size) // 4
```

- `Array<T>`는 T에 대해 `invariant`하다 (`Array<Int>`는 `Array<Number>`가 될 수 없다.) 그러나 `List<T>`는 T에 대해 `covariant`하다.

```
val a: Array<Number> = Array<Int>(0) { 0 } // won't compile
val l: List<Number> = listOf(1, 2, 3) // OK
```

- `Array`는 `IntArray`, `DoubleArray`, `CharArray`등의 원시타입에 최적화 되어 있다. (각각의 어레이는 `int[]`, `double[]`, `char[]`으로 매핑된다.)
  `List`는 원시 타입에 대해 최적화를 제공하지 않지만, 일부 라이브러리에서 최적화를 제공한다.

> 라이브러리와 같은 성능이 중요한 파트의 소스가 아니면 `List`를 사용하는 것이 좋다.

---

컬렉션은 프로그래밍에서 굉장히 중요한 개념 중 하나이다. 안드로이드의 `RecyclerView`, `LazyRow` 등과 같은 뷰에서 컬렉션은 필수불가결한 요소이다. 이러한 컬렉션을 효율적으로 사용하는 방법을 알아보자.

대부분의 현대적인 프로그래밍 언어에는 컬렉션 리터널이 따로 제공된다.

```
// 파이썬
primes = [2, 3, 5, 7, 13]
// 스위프트
let primes = [2, 3, 5, 7, 13]
```

코틀린 역시 강력한 컬렉션 처리를 제공한다. 대표적인 예로는 `map`, `filter`, `all`, `none`등과 같은 `Collection API`와 `Sequence`를 예로 들 수 있겠다.

이러한 최적화 도구를 잘 활용하지 않으면, 어플리케이션 성능에 문제가 일어날 수 있다. 컬렉션 최적화를 공부하는 것은 그렇게 어렵지는 않다. 몇 가지 규칙을 기억하고, 상황에 맞춰 생각하면 누구나 효과적으로 최적화할 수 있다.

> 그 규칙과 상황을 지금부터 알아보자.

# 규칙 1 : 하나 이상의 처리 단계를 가진 경우에는 시퀀스를 사용하라

`Iterable`과 `Sequence`의 차이가 무엇일까?

```
public interface Sequence<out T> {
    public operator fun iterator(): Iterator<T>
}

public interface Iterable<out T> {
    public operator fun iterator(): Iterator<T>
}
```

`Iterable`과 `Sequence`는 완전히 다른 목적으로 설계되어서, 완전히 다른 형태로 동작한다.
무엇보다 `Sequnce`는 지연(lazy)처리된다. 따라서 시퀀스 처리 함수들을 사용하면, 데코레이터 패턴으로 꾸며진 새로운 시퀀스가 리턴된다. 최종적인 계산은 `toList` 또는 `count`등의 최종 연산이 이루어질 때 수행된다.
`Iterable`은 처리 함수를 사용할 때마다 연산이 이루어져 `List`가 만들어 진다.

---

> 데코레이터 패턴에 대해 간단히 알아보기

데코레이터 패턴(Decorator Pattenr)은 주어진 상황 및 용도에 따라 어떤 객체에 책임(기능)을 동적으로 추가하는 패턴이다.

```
val result = sequenceOf(1, 2, 3, 4, 5)
    .filter { it % 2 == 1 } // 데코레이터를 추가
    .map { it + 1 } // 데코레이터 추가
    .toList() // 최종 연산 수행

println(result)
```

---

정리하자면 컬렉션 처리 연산은 호출할 때 연산이 이루어진다. 반면, 시퀀스 처리는 최종 연산이 이루어지기 전까지는 각 단계에서 연산이 이러나지 않는다. 따라서 어떤 연산 처리도 하지 않고, 기존의 시퀀스에 대한 데코레이터의 연산만 설치한다. 최종 필터링 처리는 `toList`등과 같은 최종 연산을 할 때 이루어진다.

```
val seq = sequenceOf(1, 2, 3)
val filtered = seq.filter { println("f$it"); it % 2 == 1 }
println(filtered) // kotlin.sequences.FilteringSequence@62043840

val asList = filtered.toList() // f1, f2, f3
println(asList) // [1, 3]

val list = listOf(1, 2, 3)
val listFiltered = list.filter { println("f$it"); it % 2 == 1 } // f1, f2, f3
println(listFiltered) // [1, 3]
```

`Seqeunce`의 `filtered`는 시퀀스 객체를 의미하며 리스트를 나타내지 않는다.(최종 연산이 이루어지기 전까지 설치만 함)
`Iterable`은 각각의 연산을 수행할 때마다 리스트 결과값을 반환한다.

---

## 이런 시퀀스의 지연 처리의 장점은 다음과 같다.

1. 자연스러운 처리 순서를 유지한다.
2. 최소한만 연산한다.
3. 무한 시퀀스 형태로 사용할 수 있다.
4. 각각의 단계에서 컬렉션을 만들어 내지 않는다.

### 순서의 중요성

`Iterable`처리와 `Sequnce` 처리는 연산의 순서가 달라지면, 다른 결과가 나타난다.

시퀀스는 요소하나하나에 지정한 연산을 한꺼번에 적용한다. 이를 전문적으로 `element-by-element order` 또는 `lazy-order`이라고 한다.

이터러블은 요소 전체를 대상으로 설치된 연산을 차근차근 하나씩 적용해 나간다. 이를 전문적으로 `step-by-step order`또는 `eager order`이라고 부른다.

```
sequenceOf(1, 2, 3)
    .filter { print("F$it, "); it % 2 == 1 }
    .map { print("M$it, "); it * 2 }
    .forEach { print("E$it, ") }
// F1, M1, E2, F2, F3, M3, E6

listOf(1, 2, 3)
    .filter { print("F$it, "); it % 2 == 1 }
    .map { print("M$it, "); it * 2 }
    .forEach { print("E$it, ") }
// F1, F2, F3, M1, M3, E2, E6,
```

> `Sequnce`는 요소 하나하나에 지정한 연산을 한꺼번에 적용한다.
> `Iterable`은 요소 전체를 대상으로 연산을 차근차근 수행한다.

## 최소 연산

컬렉션에 어떤 처리를 적용하고, 앞의 요소 10개만 필요한 상황은 굉장히 자주 접할 수 있는 상황이다. `이터러블`의 처리는 기본적으로 중간 연산이라는 개념이 없으므로, 원하는 처리를 컬렉션 전체에 적용한 뒤, 앞의 요소 10개를 사용해야한다. 하지만 시퀀스는 중간 연산이라는 개념을 갖고 있으므로, **앞의 요소 10개만 원하는 처리를 할 수 있다.**

![](https://velog.velcdn.com/images/cksgodl/post/737880b2-e224-4f5a-b812-1032b87c3022/image.png)

간단한 예를 살펴보자.

```
(1..10).asSequence()
    .filter { print("F$it, "); it % 2 == 1 }
    .map { print("M$it, "); it * 2 }
    .find { it > 5 }
// F1, M1, F2, F3, M3

(1..10)
    .filter { print("F$it, "); it % 2 == 1 }
    .map { print("M$it, "); it * 2 }
    .find { it > 5 }
// F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, M1, M3, M5, M7, M9,
```

이러한 이유로 중간 처리 단계를 모든 요소에 적용할 필요가 없는 경우에는 시퀀스를 사용하는 것이 좋다.

현재 코드에서 `find`처럼 처리를 적용하고 싶은 요소를 선택하는 연산으로는 `first`, `take`, `any`, `all`, `none`, `indexOf`등이 있다.

## 무한 시퀀스

시퀀스는 실제 최종 연산이 일어나기 전까지는 컬렉션에 어떠한 처리도 하지 않는다. 따라서 무한 시퀀스를 만들고 필요한 값을 추출하는 것도 가능하다.

`generateSequence` 또는 `sequence`를 사용해 시퀀스를 만들 수 있다.

```
generateSequence(1) { it + 1 } // 첫번 째 요소와 그 다음요소의 계산방법을 정의
    .map { it * 2 }
    .take(10)
    .forEach { print("$it, ") } // 2, 4, 6, 8, 10, 12, 14, 16, 18, 20,
```

두 번째로 `sequence`는 `suspend` 함수로 요소들을 지정한다. 시퀀스 빌더는 중단 함수내부에서 `yield`로 값을 하나씩 만들어 낸다.

> 이때 시퀀셜 코루틴이 생성되며, 쓰레드를 변경하지 않고, 단순하게 함수를 중간에 중단하는 기능만을 제공한다.

```
val fibonacci = sequence<Int> {
    yield(1) // 1 방출
    var current = 1
    var prev = 1
    while (true) {
        yield(current) // current 방출
        val temp = prev
        prev = current
        current += temp
    }
}
println(fibonacci.take(10).toList()) // [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
```

`find`,`any`,`first`,`all`,`take`와 같은 값의 활용 갯수를 지정하지 않으면 무한하게 반복한다.

```
fibonaaci.toList() // 무한 반복
```

실제로 무한 반복에 빠지는 경우가 많음으로 종결 연산으로 `first`, `take`정도만 사용하는 것이 좋다.

## 각각의 단계에서 컬렉션을 만들어 내지 않음

표준 컬렉션 처리 함수는 각각의 단계에서 새로운 컬렉션을 만들어 낸다. 일반적으로 대부분 `List`이다. 각각의 단계에서 만들어진 결과를 활용하거나,

_저장할 수 있다는 것은 컬렉션의 장점이지만, 각각의 단계에서 결과가 만들어지면서 공간을 차지하는 비용이 든다는 것은 큰 단점이다._

```
val numbers = listOf(1, 2, 3, 4, 5, 6)
numbers.filter { it % 3 == 0 } // 여기서 컬렉션 1개
    .map { it * 2 } // 여기서 컬렉션 1개
    .sum() // 총 2개의 컬렉션이 만들어짐

numbers.asSequence()
    .filter { it % 3 == 0 }
    .map { it * 2 }
    .sum() // 컬렉션이 만들어지지 않음
```

크거나 무거운 컬렉션을 처리할 때는 큰 비용이 들어간다. 만약 크기가 `1GB`인 컬렉션을 처리한다고 해보자.

```
File("1GBCollection.csv").readLines() // 1개
	.drop(1) // descriptions 컬럼 제거
    .mapNotNull { it.split(",").getOrNull(6) } // 1개
    .filter { /* */ } // 1개
    .count()
    .let(::println)
```

컬렉션이 총 3개가 만들어직 있음으로 약 `3GB`이내의 메모리를 소비할 것이다. 이를 `Sequence`로 구현한다면 비용, 성능면에서 이득을 볼 수 있을 것이다.

```
File("1GBCollection.csv").useLines {
	.drop(1) // descriptions 컬럼 제거
    .mapNotNull { it.split(",").getOrNull(6) }
    .filter { /* */ }
    .count()
    .let(::println)
}
```

`useLines`는 시퀀스의 형태로 파일을 사용할 수 있게해준다.

> 컬렉션의 파일이 클 수록, 처리 단계가 많아질수록 시퀀스와 이터러블의 차이가 커진다.

## 시퀀스가 빠르지 않은 경우도 있다.

#### 컬렉션 전체를 기반으로 처리해야 하는 연산은 시퀀스를 사용해도 빨라지지 않는다.

예를 들면 `stdlib`의 `sorted`함수가 있다. 이는 `Sequence`를 `List`로 변환한 뒤에, 자바 `stdlib`의 `sort`를 사용해 처리한다. 문제는 이러한 변환 처리로 인해서, 시퀀스가 컬렉션처리보다 느려진다는 것이다.

_무한 시퀀스에서 `sorted`를 사용하면 무한 시퀀스에 빠진다.
_

`sorted`는 `Sequence`보다 `Collection`이 더 빠른 희귀한 예이다. 다른 처리는 모두 `Sequence`가 빠르므로, 여러 처리가 결합된 경우에는 시퀀스를 사용하자.

## 자바 스트림의 경우

자바 8부터는 컬렉션 처리를 위해 스트림 기능이 추가되었다. 코틀린의 시퀀스와 비슷한 형태로 동작한다.

```
products.asSequence()
	.filter { it.bought }
    .map { it.price }
    .average()

products.stream()
	.filter { it.bought }
    .mapToDouble { it.price }
    .average()
    .orElse(0.0)
```

자바8의 스트림도 `lazy`하게 작동하며, 마지막 처리 단계에서 연산이 일어난다. 다만 자바의 스트림과 코틀린의 시퀀스는 다음과 같은 세 가지 큰 차이점이 있다.

1. 코틀린의 시퀀스가 더 많은 처리 함수를 가지고 있으며(확장 함수로 정의되어 있기에), 더 사용하기 쉽다.

2. 자바 스틀미은 별렬 함수를 사용해서 병렬 모드로 실행할 수 있다. 멀티 코어 환경에서 굉장히 큰 성능 향상을 가져온다.(자바 내에서 쓰레드풀과 관련된 문제가 있음으로 주의)

3. 코틀린의 시퀀스는 코틀린/JVM, 코틀린/JS, 코틀린/네이티브 등의 일반적인 모듈에서 모두 사용가능하다. 하지만 자바 스트림은 코틀린/JVM에서만 동작하며, JVM이 8버전 이상일 때만 동작한다.

병렬 모드를 사용하지 않는다면, 자바 스트림과 코틀린 시퀀스 중 어떤 것이 더 효율적이라고 단정하긴 어렵다.

> 정말 성능적 이득을 볼려고한다면 자바의 스트림을 사용하고, 이외의 일반적인 경우에는 코틀린의 시퀀스를 사용하자.(사용하기 쉽고 가독성이 좋다.)

# 정리

컬렉션과 시퀀스는 같은 처리 메서드를 지원하며, 사용하는 형태가 거의 비슷하다. 일반적으로 데이터를 컬렉션에 저장하므로, 시퀀스 처리를 하려면 시퀀스로 변환하는 과정이 필요하다.

최종적으로 컬렉션 결과를 원하므로, 시퀀스를 다시 컬렉션으로 변환하는 과정도 필요하다. 이것이 시퀀스 처리의 단점이라고 할 수 있다.

하지만 시퀀스는 `lazy`하게 처리되므로 다음과 같은 장점이 있다.

1. 자연스러운 처리 순서를 유지한다.
2. 최소한의 연산만 수행한다.
3. 무한 시퀀스 형태로 사용 가능하다.
4. 각각의 단계에서 컬렉션을 만들어 내지 않는다.

> 무거운 객체나 규모가 큰 컬렉션을 여러 단계에 걸쳐서 처리할 때 시퀀스를 사용하자. 상황에 따라서 시퀀스 처리를 활용하면 성능 향상을 기대할 수 있다.

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

- 톱 레벨 함수
- 클래스의 멤버 함수
- 함수 내부의 지역 함수

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
